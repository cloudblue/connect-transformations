from connect_transformations.exceptions import BaseTransformationException


class BillingRequestLookupError(BaseTransformationException):
    """Exception that happens when the billing request lookup fails"""
