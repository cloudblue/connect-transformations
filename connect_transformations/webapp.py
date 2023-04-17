# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from connect.eaas.core.decorators import router, web_app
from connect.eaas.core.extension import WebApplicationBase

from connect_transformations.copy_columns.mixins import CopyColumnWebAppMixin
from connect_transformations.currency_conversion.mixins import CurrencyConversionWebAppMixin
from connect_transformations.filter_row.mixins import FilterRowWebAppMixin
from connect_transformations.formula.mixins import FormulaWebAppMixin
from connect_transformations.lookup_subscription.mixins import LookupSubscriptionWebAppMixin
from connect_transformations.split_column.mixins import SplitColumnWebAppMixin


@web_app(router)
class TransformationsWebApplication(
    WebApplicationBase,
    CopyColumnWebAppMixin,
    CurrencyConversionWebAppMixin,
    FilterRowWebAppMixin,
    FormulaWebAppMixin,
    LookupSubscriptionWebAppMixin,
    SplitColumnWebAppMixin,
):
    pass
