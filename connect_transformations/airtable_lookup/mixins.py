# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from connect.eaas.core.decorators import router, transformation
from connect.eaas.core.responses import RowTransformationResponse
from fastapi.responses import JSONResponse

from connect_transformations.airtable_lookup.utils import (
    get_airtable_data,
    validate_airtable_lookup,
)
from connect_transformations.exceptions import AirTableError
from connect_transformations.utils import is_input_column_nullable


class AirTableLookupTransformationMixin:

    @transformation(
        name='Airtable lookup',
        description=(
            'Use this transformation to populate data from AirTable by '
            'matching column from input table with column in AirTable table.'
        ),
        edit_dialog_ui='/static/transformations/airtable_lookup.html',
    )
    async def airtable_lookup(
            self,
            row: dict,
    ):
        trfn_settings = self.transformation_request['transformation']['settings']
        map_by = trfn_settings['map_by']
        input_column = self.transformation_request['transformation']['columns']['input']

        if is_input_column_nullable(
            input_column,
            map_by['input_column'],
        ) and not row[map_by['input_column']]:
            return RowTransformationResponse.skip()

        records = None
        try:
            params = {
                'filterByFormula': f'{map_by["airtable_column"]}={row[map_by["input_column"]]}',
                'maxRecords': 2,
            }
            records = await get_airtable_data(
                api_url=f'{trfn_settings["base_id"]}/{trfn_settings["table_id"]}',
                token=trfn_settings['api_key'],
                params=params,
            )
        except AirTableError as e:
            return RowTransformationResponse.fail(output=str(e))

        if (
            not records
            or 'records' not in records
            or len(records['records']) != 1
        ):
            return RowTransformationResponse.skip()

        try:
            record = records['records'][0]['fields']
            return RowTransformationResponse.done({
                mapping['to']: record[mapping['from']]
                for mapping in trfn_settings['mapping']
            })
        except Exception as e:
            return RowTransformationResponse.fail(output=f'Error extracting data: {e}')


class AirTableLookupWebAppMixin:

    @router.get(
        '/airtable_lookup/bases',
        summary='Get list of bases by given token',
    )
    async def get_bases(
        self,
        api_key: str,
    ):
        try:
            bases = await get_airtable_data('meta/bases', api_key, params={})
            return [
                {'id': base['id'], 'name': base['name']}
                for base in bases['bases']
            ]

        except AirTableError as e:
            return JSONResponse(
                status_code=400,
                content={'error': f'{e}'},
            )

    @router.get(
        '/airtable_lookup/tables',
        summary='Get list of tables with its columns by given base and token',
    )
    async def get_tables(
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
                {
                    'id': table['id'],
                    'name': table['name'],
                    'columns': table['fields'],
                }
                for table in tables['tables']
            ]

        except AirTableError as e:
            return JSONResponse(
                status_code=400,
                content={'error': f'{e}'},
            )

    @router.post(
        '/validate/airtable_lookup',
        summary='Validate airtable lookup settings',
    )
    def validate_airtable_lookup_settings(
        self,
        data: dict,
    ):
        return validate_airtable_lookup(data)
