from connect_transformations.exceptions import BaseTransformationException


class AttachmentError(BaseTransformationException):
    """Exception that happens when the attachment lookup api call fails"""
