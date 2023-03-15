# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
class BaseTransformationException(Exception):
    """BaseException for transformation exceptions"""


class SubscriptionLookup(BaseException):
    """Exception that happens when the subscription lookup fails"""
