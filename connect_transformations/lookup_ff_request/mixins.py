# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from typing import Dict

from connect.client import AsyncConnectClient
from connect.eaas.core.decorators import router, transformation
from connect.eaas.core.inject.asynchronous import get_installation_client
from connect.eaas.core.responses import RowTransformationResponse
from fastapi import Depends

from connect_transformations.constants import SEPARATOR
from connect_transformations.lookup_ff_request.exceptions import FFRequestLookupError
from connect_transformations.lookup_ff_request.models import Configuration, SubscriptionParameter
from connect_transformations.lookup_ff_request.utils import (
    FF_REQ_COMMON_FILTERS,
    FF_REQ_SELECT,
    filter_requests_with_changes,
    validate_lookup_ff_request,
)
from connect_transformations.models import Error, ValidationResult
from connect_transformations.utils import deep_itemgetter, is_input_column_nullable


class LookupFFRequestTransformationMixin:
    @transformation(
        name='Lookup CloudBlue FF request data',
        description=(
            'This transformation function allows you to get the CloudBlue'
            ' FF request data by the subscription ID or parameter value and sets'
            ' item by ID or MPN.'
        ),
        edit_dialog_ui='/static/transformations/lookup_ff_request.html',
    )
    async def lookup_ff_request(
        self,
        row: Dict,
    ):
        output_columns = self.settings.get('output_config')
        value = row[self.settings['parameter_column']]
        item_id = row.get(self.settings['item_column'])

        if is_input_column_nullable(
            self.transformation_request['transformation']['columns']['input'],
            self.settings['parameter_column'],
        ) and not value:
            return RowTransformationResponse.skip()

        lookup = {}
        if self.settings.get('asset_type'):
            lookup[f'asset.{self.settings["asset_type"]}'] = row[self.settings['asset_column']]

        lookup['asset.params.name'] = self.settings['parameter']['name']
        lookup['asset.params.value'] = value

        try:
            request = await self.get_request(lookup)
        except Exception as e:
            return RowTransformationResponse.fail(output=str(e))

        if not request:
            return RowTransformationResponse.skip()

        return RowTransformationResponse.done(
            self.extract_row_from_request(request, output_columns, item_id),
        )

    def extract_row_from_request(self, request, output_columns, item_id):
        row = {}

        item_attrs = []

        for col_name, col_config in output_columns.items():
            value = None
            attr = col_config['attribute']
            if attr == 'asset.parameter.value':
                param_name = col_config['parameter_name']
                for param_data in request['asset']['params']:
                    if param_data['name'] == param_name:
                        value = param_data['value']
                        break
            elif attr.startswith('asset.items.'):
                item_attr = attr.split('.')[-1]
                item_attrs.append((col_name, item_attr))
                value = ''
            else:
                value = deep_itemgetter(request, attr)

            row[col_name] = value

        if item_attrs:
            self.extract_item_attrs_from_request(item_attrs, row, request, item_id)

        return row

    def extract_item_attrs_from_request(self, item_attrs, row, request, item_id_value):
        item_id = self.settings['item']['id']
        for item in request['asset']['items']:
            if item_id == 'all' or item.get(item_id) == item_id_value:
                for col_name, item_attr in item_attrs:
                    item_value = str(item.get(item_attr, ''))
                    row[col_name] += f'{SEPARATOR}{item_value}' if row[col_name] else item_value

    async def get_request(self, lookup):
        k = ''
        for key, value in lookup.items():
            k = k + f'{key}-{value}'
        try:
            return self.cache_get(k)
        except KeyError:
            pass

        result = await self.retrieve_ff_requests(lookup)

        await self.acache_put(k, result)
        return result

    async def retrieve_ff_requests(self, lookup):
        batch_context = self.transformation_request['batch']['context']
        period_end = batch_context.get('period', {}).get('end')
        additional_filters = {}
        if period_end:
            additional_filters['updated__lt'] = period_end

        ff_reqs = self.installation_client.requests.filter(
            **FF_REQ_COMMON_FILTERS,
            **lookup,
            **additional_filters,
        ).select(
            *FF_REQ_SELECT,
        ).order_by('-updated')

        result = None

        async for item in filter_requests_with_changes(ff_reqs):
            if result is None:
                result = item
            elif self.settings.get('action_if_multiple') == 'leave_empty':
                return
            elif self.settings.get('action_if_multiple') == 'use_most_actual':
                return result
            else:
                raise FFRequestLookupError(f'Many results found for the filter {lookup}')

        if result:
            return result

        if self.settings.get('action_if_not_found') == 'fail':
            raise FFRequestLookupError(f'No result found for the filter {lookup}')

    @property
    def settings(self):
        return self.transformation_request['transformation']['settings']


class LookupFFRequestWebAppMixin:

    @router.post(
        '/lookup_ff_request/validate',
        summary='Validate lookup FF request settings',
        response_model=ValidationResult,
        responses={
            400: {'model': Error},
        },
    )
    def validate_lookup_ff_request_settings(
        self,
        data: Configuration,
    ):
        return validate_lookup_ff_request(data)

    @router.get(
        '/lookup_ff_request/parameters',
        summary='Return available parameters names',
    )
    async def get_ff_parameters(
        self,
        product_id: str,
        client: AsyncConnectClient = Depends(get_installation_client),
    ):
        return [
            SubscriptionParameter(
                id=parameter['id'],
                name=parameter['name'],
            )
            async for parameter in client.products[product_id].parameters.all()
        ]
