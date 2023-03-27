# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
class BaseTransformationException(Exception):
    """BaseException for transformation exceptions"""


class SubscriptionLookup(BaseTransformationException):
    """Exception that happens when the subscription lookup fails"""


class CurrencyConversion(BaseTransformationException):
    """Exception that happens when the conversion call fails"""


class SplitColumn(BaseTransformationException):
    """Exception that happens when the split column call fails"""
