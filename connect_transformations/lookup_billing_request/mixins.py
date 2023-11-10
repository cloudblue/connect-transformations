# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from typing import Dict

from connect.client import AsyncConnectClient, ClientError
from connect.eaas.core.decorators import router, transformation
from connect.eaas.core.inject.asynchronous import get_installation_client
from connect.eaas.core.responses import RowTransformationResponse
from fastapi import Depends

from connect_transformations.constants import SEPARATOR
from connect_transformations.lookup_billing_request.exceptions import BillingRequestLookupError
from connect_transformations.lookup_billing_request.models import (
    Configuration,
    SubscriptionParameter,
)
from connect_transformations.lookup_billing_request.utils import validate_lookup_billing_request
from connect_transformations.models import Error, ValidationResult
from connect_transformations.utils import deep_itemgetter, is_input_column_nullable


class LookupBillingRequestTransformationMixin:
    @transformation(
        name='Lookup CloudBlue Billing request data',
        description=(
            'This transformation function allows you to get the CloudBlue billing'
            ' request data by the subscription ID or parameter value and sets'
            ' item by ID or MPN.'
        ),
        edit_dialog_ui='/static/transformations/lookup_billing_request.html',
    )
    async def lookup_billing_request(
        self,
        row: Dict,
    ):
        output_columns = self.billing_settings.get('output_config')
        value = row[self.billing_settings['parameter_column']]
        item_id = row.get(self.billing_settings['item_column'])

        if is_input_column_nullable(
            self.transformation_request['transformation']['columns']['input'],
            self.billing_settings['parameter_column'],
        ) and not value:
            return RowTransformationResponse.skip()

        lookup = {}
        if self.billing_settings.get('asset_type'):
            lookup[f'asset.{self.billing_settings["asset_type"]}'] = row[
                self.billing_settings['asset_column']
            ]

        lookup['asset.params.name'] = self.billing_settings['parameter']['name']
        lookup['asset.params.value'] = value

        try:
            request = await self.get_billing_request(lookup)
        except Exception as e:
            return RowTransformationResponse.fail(output=str(e))

        if not request:
            return RowTransformationResponse.skip()

        return RowTransformationResponse.done(
            await self.extract_row_from_billing(request, output_columns, item_id),
        )

    async def extract_row_from_billing(self, request, output_columns, item_id):
        row = {}

        item_attrs = []
        asset = None

        for col_name, col_config in output_columns.items():
            value = None
            attr = col_config['attribute']
            if attr == 'asset.parameter.value':
                param_name = col_config['parameter_name']
                for param_data in request['asset']['params']:
                    if param_data['name'] == param_name:
                        value = param_data['value']
                        break
            elif attr.startswith('items.'):
                if attr == 'items.old_quantity':
                    asset = await self.get_asset(request)
                item_attr = attr.split('.')[-1]
                item_attrs.append((col_name, item_attr))
                value = ''
            else:
                value = deep_itemgetter(request, attr)

            row[col_name] = value

        if item_attrs:
            self.extract_item_attrs_from_billing(item_attrs, row, request, item_id, asset)

        return row

    def extract_item_attrs_from_billing(  # noqa: CCR001
        self,
        item_attrs,
        row,
        request,
        item_id_value,
        asset,
    ):
        item_id = self.billing_settings['item']['id']
        for item in request['items']:
            if item_id == 'all' or item.get(item_id) == item_id_value:
                for col_name, item_attr in item_attrs:
                    if item_attr == 'old_quantity' and asset:
                        items = [x for x in asset.get('items') if x['id'] == item['id']]
                        asset_item = items[0] if item else {}
                        item_value = str(asset_item.get(item_attr, ''))
                    else:
                        item_value = str(item.get(item_attr, ''))
                    row[col_name] += f'{SEPARATOR}{item_value}' if row[col_name] else item_value

    async def get_billing_request(self, lookup):
        k = 'billing-'
        for key, value in lookup.items():
            k = k + f'{key}-{value}'
        try:
            return self.cache_get(k)
        except KeyError:
            pass

        result = await self.retrieve_billing_requests(lookup)

        await self.acache_put(k, result)
        return result

    async def retrieve_billing_requests(self, lookup):
        batch_context = self.transformation_request['batch']['context']
        period_end = batch_context.get('period', {}).get('end')
        additional_filters = {}
        if period_end:
            additional_filters['events.created.at__lt'] = period_end

        requests = self.installation_client('subscriptions').requests.filter(
            **lookup,
            **additional_filters,
        ).order_by('-events.created.at')
        requests = [r async for r in requests]

        result = None

        for item in requests:
            if result is None:
                result = item
            elif self.billing_settings.get('action_if_multiple') == 'leave_empty':
                return
            elif self.billing_settings.get('action_if_multiple') == 'use_most_actual':
                return result
            else:
                raise BillingRequestLookupError(f'Many results found for the filter {lookup}')

        if result:
            return result

        if self.billing_settings.get('action_if_not_found') == 'fail':
            raise BillingRequestLookupError(f'No result found for the filter {lookup}')

    async def get_asset(self, billing_request):
        k = 'billing-asset-'
        k += f'{billing_request["asset"]["id"]}-{billing_request["events"]["created"]["at"]}'
        try:
            return self.cache_get(k)
        except KeyError:
            pass

        result = await self.retrieve_asset_from_ff(billing_request)

        await self.acache_put(k, result)
        return result

    async def retrieve_asset_from_ff(self, billing_request):
        try:
            request = await self.installation_client.requests.filter(
                asset__id=billing_request['asset']['id'],
                status='approved',
                updated__lt=billing_request['events']['created']['at'],
            ).select(
                '-activation_key',
                '-template',
            ).order_by('-updated').first()
        except ClientError:
            return None

        if request:
            return request['asset']

    @property
    def billing_settings(self):
        return self.transformation_request['transformation']['settings']


class LookupBillingRequestWebAppMixin:

    @router.post(
        '/lookup_billing_request/validate',
        summary='Validate lookup billing request settings',
        response_model=ValidationResult,
        responses={
            400: {'model': Error},
        },
    )
    def validate_lookup_billing_request_settings(
        self,
        data: Configuration,
    ):
        return validate_lookup_billing_request(data)

    @router.get(
        '/lookup_billing_request/parameters',
        summary='Return available parameters names',
    )
    async def get_billing_parameters(
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
