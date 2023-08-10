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
            'This transformation function allows you to perform manual'
            ' operations that cannot be automated using other transformations.'
        ),
        edit_dialog_ui='/static/transformations/manual.html',
    )
    @manual_transformation()
    def manual_transformation(
        self,
        row: Dict,
    ):  # pragma: no cover
        pass
