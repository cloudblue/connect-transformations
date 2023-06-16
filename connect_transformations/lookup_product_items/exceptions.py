from connect_transformations.exceptions import BaseTransformationException


class ProductLookupError(BaseTransformationException):
    """Exception that happens when the subscription lookup fails"""
