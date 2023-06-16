from connect_transformations.exceptions import BaseTransformationException


class CurrencyConversionError(BaseTransformationException):
    """Exception that happens when the conversion call fails"""
