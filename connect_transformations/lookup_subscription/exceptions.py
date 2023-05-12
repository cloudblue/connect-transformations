from connect_transformations.exceptions import BaseTransformationException


class SubscriptionLookupError(BaseTransformationException):
    """Exception that happens when the subscription lookup fails"""
