# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import time
from typing import Dict, List

import requests
from connect.eaas.core.decorators import router, transformation
from connect.eaas.core.responses import RowTransformationResponse
from fastapi.responses import JSONResponse

from connect_transformations.airtable_lookup.exceptions import AirTableError
from connect_transformations.airtable_lookup.models import (
    AirTableBase,
    AirTableColumn,
    AirTableTable,
    Configuration,
)
from connect_transformations.airtable_lookup.utils import (
    get_airtable_data,
    validate_airtable_lookup,
)
from connect_transformations.models import Error, ValidationResult
from connect_transformations.utils import is_input_column_nullable


class AirTableLookupTransformationMixin:

    def preload_lookup_data_for_airtable(self, trfn_settings):  # noqa: CCR001
        with self.lock():
            if hasattr(self, 'airtable_data'):
                return

            self.airtable_data = {}

            page_count = 0
            params = {}
            mapped_columns = [mapping['from'] for mapping in trfn_settings['mapping']]
            lookup_column = trfn_settings['map_by']['airtable_column']
            while True:
                response = requests.get(
                    'https://api.airtable.com/v0/'
                    f'{trfn_settings["base_id"]}/{trfn_settings["table_id"]}',
                    headers={
                        'Authorization': f'Bearer {trfn_settings["api_key"]}',
                    },
                    params=params,
                )
                response.raise_for_status()
                data = response.json()

                for record in data.get('records', []):
                    lookup_value = None
                    looked_up_data = {}
                    for field_name, field_value in record['fields'].items():
                        if field_name == lookup_column:
                            lookup_value = field_value
                            continue
                        if field_name in mapped_columns:
                            looked_up_data[field_name] = field_value
                    self.airtable_data[lookup_value] = looked_up_data

                if 'offset' not in data:
                    break
                params['offset'] = data['offset']
                if page_count % 5 == 0:
                    time.sleep(1)
                page_count += 1

    @transformation(
        name='Lookup data from AirTable',
        description=(
            'This transformation function allows you to populate data from'
            ' AirTable by matching input column values with AirTable ones.'
        ),
        edit_dialog_ui='/static/transformations/airtable_lookup.html',
    )
    def airtable_lookup(
            self,
            row: Dict,
    ):
        trfn_settings = self.transformation_request['transformation']['settings']

        try:
            self.preload_lookup_data_for_airtable(trfn_settings)
        except Exception as e:
            return RowTransformationResponse.fail(output=str(e))

        map_by = trfn_settings['map_by']
        input_column = self.transformation_request['transformation']['columns']['input']

        if is_input_column_nullable(
            input_column,
            map_by['input_column'],
        ) and not row[map_by['input_column']]:
            return RowTransformationResponse.skip()

        record = self.airtable_data.get(row[map_by['input_column']])
        if not record:
            return RowTransformationResponse.skip()

        return RowTransformationResponse.done({
            mapping['to']: record[mapping['from']]
            for mapping in trfn_settings['mapping']
        })


class AirTableLookupWebAppMixin:

    @router.get(
        '/airtable_lookup/bases',
        summary='Get list of AirTable bases.',
        response_model=List[AirTableBase],
        responses={
            400: {'model': Error},
        },
    )
    async def get_airtable_bases(
        self,
        api_key: str,
    ):
        try:
            bases = await get_airtable_data('meta/bases', api_key, params={})
            return [
                AirTableBase(id=base['id'], name=base['name'])
                for base in bases['bases']
            ]

        except AirTableError as e:
            return JSONResponse(status_code=400, content={'error': str(e)})

    @router.get(
        '/airtable_lookup/tables',
        summary='Get list of AirTable tables within a given base.',
        response_model=List[AirTableTable],
        responses={
            400: {'model': Error},
        },
    )
    async def get_airtable_tables(
        self,
        api_key: str,
        base_id: str,
    ):
        try:
            tables = await get_airtable_data(
                f'meta/bases/{base_id}/tables',
                api_key,
            )
            return [
                AirTableTable(
                    id=table['id'],
                    name=table['name'],
                    columns=[
                        AirTableColumn(
                            id=col['id'],
                            name=col['name'],
                            type=col['type'],
                        )
                        for col in table['fields']
                    ],
                )
                for table in tables['tables']
            ]

        except AirTableError as e:
            return JSONResponse(
                status_code=400,
                content={'error': str(e)},
            )

    @router.post(
        '/airtable_lookup/validate',
        summary='Validate airtable lookup settings',
        response_model=ValidationResult,
        responses={
            400: {'model': Error},
        },
    )
    def validate_airtable_lookup_settings(
        self,
        data: Configuration,
    ):
        return validate_airtable_lookup(data)
