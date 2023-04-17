# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from connect.client import AsyncConnectClient
from connect.eaas.core.decorators import router, transformation
from connect.eaas.core.inject.asynchronous import get_installation_client
from connect.eaas.core.responses import RowTransformationResponse
from fastapi import Depends

from connect_transformations.constants import SUBSCRIPTION_LOOKUP
from connect_transformations.lookup_subscription.utils import (
    retrieve_subscription,
    validate_lookup_subscription,
)
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
        row: dict,
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
            subscription = await retrieve_subscription(
                self.installation_client,
                self._cache,
                self._cache_lock,
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


class LookupSubscriptionWebAppMixin:

    @router.post(
        '/validate/lookup_subscription',
        summary='Validate lookup subscription settings',
    )
    def validate_lookup_subscription_settings(
        self,
        data: dict,
    ):
        return validate_lookup_subscription(data)

    @router.get(
        '/lookup_subscription/criteria',
        summary='Return the subscription criteria options',
    )
    def get_subscription_criteria(
        self,
    ):
        return SUBSCRIPTION_LOOKUP

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
            {parameter['id']: parameter['name']}
            async for parameter in client.products[product_id].parameters.all()
        ]
