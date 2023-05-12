from connect_transformations.exceptions import BaseTransformationException


class AirTableError(BaseTransformationException):
    """Exception that happens when the airtable api call fails"""
