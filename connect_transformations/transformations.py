from connect.eaas.core.decorators import transformation
from connect.eaas.core.extension import TransformationsApplicationBase


class StandardTransformationsApplication(TransformationsApplicationBase):

    @transformation(
        name='Copy row transformation',
        description='The transformation function that copy content from one column to another',
        edit_dialog_ui='/static/transformations/copy.html',
    )
    def transform_1_copy_row(
        self,
        row: dict,
    ):
        trfn_settings = (
            self.transformation_request['transformation']['settings']
        )
        result = {}

        for setting in trfn_settings:
            result[setting['to']] = row[setting['from']]

        return result
