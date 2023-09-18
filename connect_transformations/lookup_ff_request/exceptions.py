from connect_transformations.exceptions import BaseTransformationException


class FFRequestLookupError(BaseTransformationException):
    """Exception that happens when the FF request lookup fails"""
