# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from typing import Dict, List

from connect.client import AsyncConnectClient, ClientError
from connect.eaas.core.decorators import router, transformation
from connect.eaas.core.inject.asynchronous import get_installation_client
from connect.eaas.core.responses import RowTransformationResponse
from fastapi import Depends

from connect_transformations.constants import MAX_API_CALL_CONNECTION_ERROR_RETRIES, SEPARATOR
from connect_transformations.lookup_subscription.exceptions import SubscriptionLookupError
from connect_transformations.lookup_subscription.models import Configuration, SubscriptionParameter
from connect_transformations.lookup_subscription.utils import validate_lookup_subscription
from connect_transformations.models import Error, ValidationResult
from connect_transformations.utils import deep_itemgetter, is_input_column_nullable


SUBSCRIPTIONS_ACTIVE_STATUSES = ('active', 'terminating')


class LookupSubscriptionTransformationMixin:

    @transformation(
        name='Lookup CloudBlue subscription data',
        description=(
            'This transformation function allows you to get the CloudBlue'
            ' subscription data by the subscription ID or parameter value.'
        ),
        edit_dialog_ui='/static/transformations/lookup_subscription.html',
    )
    async def lookup_subscription(
        self,
        row: Dict,
    ):
        lookup_type = self.settings['lookup_type']
        from_column = self.settings['from']
        prefix = self.settings.get('prefix', '')
        parameter = self.settings.get('parameter', {}).get('name', None)
        output_columns = self.settings.get('output_config')
        value = row[from_column]

        if is_input_column_nullable(
            self.transformation_request['transformation']['columns']['input'],
            from_column,
        ) and not value:
            return RowTransformationResponse.skip()

        if lookup_type == 'params__value':
            lookup = {
                'params.name': parameter,
                'params.value': value,
            }
        else:
            lookup = {lookup_type: value}

        try:
            subscription = await self.get_subscription(lookup)
        except Exception as e:
            return RowTransformationResponse.fail(output=str(e))

        if not subscription:
            return RowTransformationResponse.skip()

        # backward compatibility
        if not output_columns:
            return RowTransformationResponse.done({
                f'{prefix}.product.id': subscription['product']['id'],
                f'{prefix}.product.name': subscription['product']['name'],
                f'{prefix}.marketplace.id': subscription['marketplace']['id'],
                f'{prefix}.marketplace.name': subscription['marketplace']['name'],
                f'{prefix}.vendor.id': subscription['connection']['vendor']['id'],
                f'{prefix}.vendor.name': subscription['connection']['vendor']['name'],
                f'{prefix}.subscription.id': subscription['id'],
                f'{prefix}.subscription.external_id': subscription['external_id'],
                f'{prefix}.subscription.status': subscription['status'],
            })

        return RowTransformationResponse.done(
            self.extract_row_from_subscription(subscription, output_columns),
        )

    def extract_row_from_subscription(self, subscription, output_columns):
        row = {}

        item_attrs = []

        for col_name, col_config in output_columns.items():
            value = None
            attr = col_config['attribute']
            if attr == 'parameter.value':
                param_name = col_config['parameter_name']
                for param_data in subscription['params']:
                    if param_data['name'] == param_name:
                        value = param_data['value']
                        break
            elif attr.startswith('items.'):
                item_attr = attr.split('.')[-1]
                item_attrs.append((col_name, item_attr))
                value = ''
            else:
                value = deep_itemgetter(subscription, attr)

            row[col_name] = value

        if item_attrs:
            self.extract_item_attrs_from_subscription(item_attrs, row, subscription)

        return row

    @staticmethod
    def extract_item_attrs_from_subscription(item_attrs, row, subscription):
        for item in subscription['items']:
            if (
                item.get('item_type') == 'reservation'
                and item.get('quantity') == 0
            ):
                continue

            for col_name, item_attr in item_attrs:
                item_value = str(item.get(item_attr, ''))
                row[col_name] += f'{SEPARATOR}{item_value}' if row[col_name] else item_value

    async def get_subscription(self, lookup):
        k = ''
        for key, value in lookup.items():
            k = k + f'{key}-{value}'
        try:
            return self.cache_get(k)
        except KeyError:
            pass

        for attempts_left in range(MAX_API_CALL_CONNECTION_ERROR_RETRIES, -1, -1):
            try:
                result = await self.retrieve_subscription(lookup)
                break
            except ClientError:
                if not attempts_left:
                    raise
                continue

        await self.acache_put(k, result)
        return result

    async def retrieve_subscription(self, lookup):
        subscriptions = self.installation_client('subscriptions').assets.filter(
            status__in=(
                'active', 'terminating', 'suspended',
                'terminated', 'terminated',
            ),
        ).filter(**lookup).order_by('-events.created.at')

        result = None

        async for item in subscriptions:
            if result is None:
                result = item
            elif self.settings.get('action_if_multiple') == 'leave_empty':
                return
            elif self.settings.get('action_if_multiple') == 'use_most_actual':
                result = self.select_actual_subscription(result, item)
            else:
                raise SubscriptionLookupError(f'Many results found for the filter {lookup}')

        if result:
            return result

        if self.settings.get('action_if_not_found') == 'fail':
            raise SubscriptionLookupError(f'No result found for the filter {lookup}')

    @staticmethod
    def select_actual_subscription(*subscriptions):
        result = None
        for item in subscriptions:
            if result is None or item['status'] in SUBSCRIPTIONS_ACTIVE_STATUSES:
                result = item
        return result

    @property
    def settings(self):
        return self.transformation_request['transformation']['settings']


class LookupSubscriptionWebAppMixin:

    @router.post(
        '/lookup_subscription/validate',
        summary='Validate lookup subscription settings',
        response_model=ValidationResult,
        responses={
            400: {'model': Error},
        },
    )
    def validate_lookup_subscription_settings(
        self,
        data: Configuration,
    ):
        return validate_lookup_subscription(data)

    @router.get(
        '/lookup_subscription/parameters',
        summary='Return the subscription available parameters names',
        response_model=List[SubscriptionParameter],
        responses={
            400: {'model': Error},
        },
    )
    async def get_subscription_parameters(
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
