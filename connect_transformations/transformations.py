# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import asyncio
import threading

from cachetools import LRUCache
from connect.eaas.core.extension import TransformationsApplicationBase

from connect_transformations.airtable_lookup.mixins import AirTableLookupTransformationMixin
from connect_transformations.attachment_lookup.mixins import AttachmentLookupTransformationMixin
from connect_transformations.copy_columns.mixins import CopyColumnTransformationMixin
from connect_transformations.currency_conversion.mixins import CurrencyConverterTransformationMixin
from connect_transformations.filter_row.mixins import FilterRowTransformationMixin
from connect_transformations.formula.mixins import FormulaTransformationMixin
from connect_transformations.lookup_billing_request.mixins import (
    LookupBillingRequestTransformationMixin,
)
from connect_transformations.lookup_ff_request.mixins import LookupFFRequestTransformationMixin
from connect_transformations.lookup_product_items.mixins import (
    LookupProductItemsTransformationMixin,
)
from connect_transformations.lookup_subscription.mixins import LookupSubscriptionTransformationMixin
from connect_transformations.manual_transformation.mixins import ManualTransformationMixin
from connect_transformations.split_column.mixins import SplitColumnTransformationMixin
from connect_transformations.vat_rate.mixins import VATRateForEUCountryTransformationMixin


class StandardTransformationsApplication(
    TransformationsApplicationBase,
    ManualTransformationMixin,
    AirTableLookupTransformationMixin,
    AttachmentLookupTransformationMixin,
    CopyColumnTransformationMixin,
    CurrencyConverterTransformationMixin,
    FilterRowTransformationMixin,
    FormulaTransformationMixin,
    LookupBillingRequestTransformationMixin,
    LookupFFRequestTransformationMixin,
    LookupSubscriptionTransformationMixin,
    SplitColumnTransformationMixin,
    LookupProductItemsTransformationMixin,
    VATRateForEUCountryTransformationMixin,
):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = LRUCache(128)
        self._sync_lock = threading.Lock()
        self._async_lock = asyncio.Lock()

    def lock(self):
        return self._sync_lock

    def alock(self):
        return self._async_lock

    def cache_put(self, key, val):
        with self.lock():
            self._cache[key] = val

    async def acache_put(self, key, val):
        async with self.alock():
            self._cache[key] = val

    def cache_get(self, key):
        return self._cache[key]
