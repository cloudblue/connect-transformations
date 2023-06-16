# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from typing import Dict

from connect.eaas.core.decorators import manual_transformation, transformation


class ManualTransformationMixin:

    @transformation(
        name='Manual transformation',
        description=(
            'The manual transformation is a special kind of transformation that allow to describe'
            ' the steps that must be done on the input file to produce the transformed output file.'
            ' The file must be transformed both by hands or by an external system.'
        ),
        edit_dialog_ui='/static/transformations/manual.html',
    )
    @manual_transformation()
    def manual_transformation(
        self,
        row: Dict,
    ):  # pragma: no cover
        pass
