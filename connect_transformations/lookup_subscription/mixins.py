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

from connect_transformations.lookup_subscription.exceptions import SubscriptionLookupError
from connect_transformations.lookup_subscription.models import Configuration, SubscriptionParameter
from connect_transformations.lookup_subscription.utils import validate_lookup_subscription
from connect_transformations.models import Error, ValidationResult
from connect_transformations.utils import is_input_column_nullable


class LookupSubscriptionTransformationMixin:

    @transformation(
        name='Lookup CloudBlue Subscription Data',
        description=(
            'This transformation function allows to search for the corresponding CloudBlue '
            'Subscription data.'
        ),
        edit_dialog_ui='/static/transformations/lookup_subscription.html',
    )
    async def lookup_subscription(
        self,
        row: Dict,
    ):
        trfn_settings = (
            self.transformation_request['transformation']['settings']
        )
        lookup_type = trfn_settings['lookup_type']
        from_column = trfn_settings['from']
        prefix = trfn_settings['prefix']
        parameter = trfn_settings.get('parameter', {}).get('name', None)
        value = row[from_column]
        leave_empty = trfn_settings['action_if_not_found'] == 'leave_empty'

        if is_input_column_nullable(
            self.transformation_request['transformation']['columns']['input'],
            from_column,
        ) and not value:
            return RowTransformationResponse.skip()

        if lookup_type == 'params__value':
            lookup = {
                'params.id': parameter,
                'params.value': value,
            }
        else:
            lookup = {lookup_type: value}

        subscription = None

        try:
            subscription = await self.retrieve_subscription(
                lookup,
                leave_empty,
            )
        except Exception as e:
            return RowTransformationResponse.fail(output=str(e))

        return RowTransformationResponse.done({
            f'{prefix}.product.id': subscription['product']['id'],
            f'{prefix}.product.name': subscription['product']['name'],
            f'{prefix}.marketplace.id': subscription['marketplace']['id'],
            f'{prefix}.marketplace.name': subscription['marketplace']['name'],
            f'{prefix}.vendor.id': subscription['connection']['vendor']['id'],
            f'{prefix}.vendor.name': subscription['connection']['vendor']['name'],
            f'{prefix}.subscription.id': subscription['id'],
            f'{prefix}.subscription.external_id': subscription['external_id'],
        }) if subscription else RowTransformationResponse.skip()

    async def retrieve_subscription(self, lookup, leave_empty):
        k = ''
        for key, value in lookup.items():
            k = k + f'{key}-{value}'
        try:
            return self.cache_get(k)
        except KeyError:
            pass

        results = await self.installation_client('subscriptions').assets.filter(**lookup).count()
        if results == 0:
            if leave_empty:
                return
            raise SubscriptionLookupError(f'No result found for the filter {lookup}')
        elif results > 1:
            raise SubscriptionLookupError(f'Many results found for the filter {lookup}')
        else:
            result = await self.installation_client(
                'subscriptions',
            ).assets.filter(
                **lookup,
            ).first()
            await self.acache_put(k, result)
            return result


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
    )
    async def get_parameters(
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
