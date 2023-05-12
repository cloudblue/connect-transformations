from connect_transformations.exceptions import BaseTransformationException


class VATRateError(BaseTransformationException):
    """Exception that happens when the VAT rate call fails"""
