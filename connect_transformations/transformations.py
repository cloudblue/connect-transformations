# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import asyncio
import threading
from collections import defaultdict

from cachetools import LRUCache
from connect.eaas.core.extension import TransformationsApplicationBase

from connect_transformations.airtable_lookup.mixins import AirTableLookupTransformationMixin
from connect_transformations.attachment_lookup.mixins import AttachmentLookupTransformationMixin
from connect_transformations.copy_columns.mixins import CopyColumnTransformationMixin
from connect_transformations.currency_conversion.mixins import CurrencyConverterTransformationMixin
from connect_transformations.filter_row.mixins import FilterRowTransformationMixin
from connect_transformations.formula.mixins import FormulaTransformationMixin
from connect_transformations.lookup_subscription.mixins import LookupSubscriptionTransformationMixin
from connect_transformations.manual_transformation.mixins import ManualTransformationMixin
from connect_transformations.split_column.mixins import SplitColumnTransformationMixin


class StandardTransformationsApplication(
    TransformationsApplicationBase,
    ManualTransformationMixin,
    AirTableLookupTransformationMixin,
    AttachmentLookupTransformationMixin,
    CopyColumnTransformationMixin,
    CurrencyConverterTransformationMixin,
    FilterRowTransformationMixin,
    FormulaTransformationMixin,
    LookupSubscriptionTransformationMixin,
    SplitColumnTransformationMixin,
):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = LRUCache(128)
        self._cache_lock = asyncio.Lock()
        self._current_exchange_rate_lock = asyncio.Lock()
        self._sync_lock = threading.Lock()
        self.current_exchange_rate = None
        self._attachments = defaultdict(dict)
        self._attachment_lock = asyncio.Lock()
