# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import asyncio

import httpx
from cachetools import LRUCache
from connect.eaas.core.extension import TransformationsApplicationBase

from connect_transformations.copy_columns.mixins import CopyColumnTransformationMixin
from connect_transformations.currency_conversion.mixins import CurrencyConverterTransformationMixin
from connect_transformations.lookup_subscription.mixins import LookupSubscriptionTransformationMixin
from connect_transformations.manual_transformation.mixins import ManualTransformationMixin
from connect_transformations.split_column.mixins import SplitColumnTransformationMixin


class StandardTransformationsApplication(
    TransformationsApplicationBase,
    ManualTransformationMixin,
    CopyColumnTransformationMixin,
    CurrencyConverterTransformationMixin,
    LookupSubscriptionTransformationMixin,
    SplitColumnTransformationMixin,
):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = LRUCache(128)
        self._cache_lock = asyncio.Lock()
        self._ssl_context = httpx.create_ssl_context()
