# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from connect.eaas.core.decorators import router, web_app
from connect.eaas.core.extension import WebApplicationBase

from connect_transformations.airtable_lookup.mixins import AirTableLookupWebAppMixin
from connect_transformations.attachment_lookup.mixins import AttachmentLookupWebAppMixin
from connect_transformations.copy_columns.mixins import CopyColumnWebAppMixin
from connect_transformations.currency_conversion.mixins import CurrencyConversionWebAppMixin
from connect_transformations.filter_row.mixins import FilterRowWebAppMixin
from connect_transformations.formula.mixins import FormulaWebAppMixin
from connect_transformations.handlers import CustomExceptionHandlers
from connect_transformations.lookup_billing_request.mixins import LookupBillingRequestWebAppMixin
from connect_transformations.lookup_ff_request.mixins import LookupFFRequestWebAppMixin
from connect_transformations.lookup_product_items.mixins import LookupProductItemsWebAppMixin
from connect_transformations.lookup_subscription.mixins import LookupSubscriptionWebAppMixin
from connect_transformations.split_column.mixins import SplitColumnWebAppMixin
from connect_transformations.vat_rate.mixins import VATRateForEUCountryWebAppMixin


@web_app(router)
class TransformationsWebApplication(
    WebApplicationBase,
    CustomExceptionHandlers,
    AirTableLookupWebAppMixin,
    AttachmentLookupWebAppMixin,
    CopyColumnWebAppMixin,
    CurrencyConversionWebAppMixin,
    FilterRowWebAppMixin,
    FormulaWebAppMixin,
    LookupBillingRequestWebAppMixin,
    LookupFFRequestWebAppMixin,
    LookupSubscriptionWebAppMixin,
    SplitColumnWebAppMixin,
    LookupProductItemsWebAppMixin,
    VATRateForEUCountryWebAppMixin,
):
    pass
