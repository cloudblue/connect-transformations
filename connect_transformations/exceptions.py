# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
class BaseTransformationException(Exception):
    """BaseException for transformation exceptions"""


class SubscriptionLookupError(BaseTransformationException):
    """Exception that happens when the subscription lookup fails"""


class CurrencyConversionError(BaseTransformationException):
    """Exception that happens when the conversion call fails"""


class SplitColumnError(BaseTransformationException):
    """Exception that happens when the split column call fails"""
