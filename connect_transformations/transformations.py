# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import asyncio

from cachetools import LRUCache
from connect.eaas.core.decorators import transformation
from connect.eaas.core.extension import TransformationsApplicationBase

from connect_transformations.exceptions import SubscriptionLookup


class StandardTransformationsApplication(TransformationsApplicationBase):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self._cache = LRUCache(128)
        self._cache_lock = asyncio.Lock()

    @transformation(
        name='Copy Column(s)',
        description='The transformation function that copy content from one column to another',
        edit_dialog_ui='/static/transformations/copy.html',
    )
    def copy_columns(
        self,
        row: dict,
    ):
        trfn_settings = (
            self.transformation_request['transformation']['settings']
        )
        result = {}

        for setting in trfn_settings:
            result[setting['to']] = row[setting['from']]

        return result

    async def retrieve_subscription(self, key, value):
        result = None

        k = f'{key}-{value}'
        try:
            result = self._cache[k]
        except KeyError:
            pass

        if not result:
            query = {key: value}
            results = await self.installation_client('subscriptions').assets.filter(**query).count()
            if results == 0:
                raise SubscriptionLookup(f'No result found for the filter {query}')
            elif results > 1:
                raise SubscriptionLookup(f'Many results found for the filter {query}')
            else:
                result = await self.installation_client(
                    'subscriptions',
                ).assets.filter(
                    **query,
                ).first()
                async with self._cache_lock:
                    self._cache[k] = result

        return result

    @transformation(
        name='Lookup subscription data',
        description=(
            'The transformation function that retreive the subscription data from one column'
            'specifying the id, the external id or a parameter value'
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
        subscription = await self.retrieve_subscription(lookup_type, row[from_column])

        return {
            f'{prefix}.product.id': subscription['product']['id'],
            f'{prefix}.product.name': subscription['product']['name'],
            f'{prefix}.marketplace.id': subscription['marketplace']['id'],
            f'{prefix}.marketplace.name': subscription['marketplace']['name'],
            f'{prefix}.vendor.id': subscription['connection']['vendor']['id'],
            f'{prefix}.vendor.name': subscription['connection']['vendor']['name'],
            f'{prefix}.subscription.id': subscription['id'],
            f'{prefix}.subscription.external_id': subscription['external_id'],
        }
