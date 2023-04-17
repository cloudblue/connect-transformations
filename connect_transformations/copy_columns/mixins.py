# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from connect.eaas.core.decorators import router, transformation
from connect.eaas.core.responses import RowTransformationResponse

from connect_transformations.copy_columns.utils import validate_copy_columns


class CopyColumnTransformationMixin:

    @transformation(
        name='Copy Column(s)',
        description=(
            'This transformation function allows you to copy values from Input to Output columns, '
            'which might be handy if you\'d like to change column name in the output data or '
            'create a copy of values in a table.'
        ),
        edit_dialog_ui='/static/transformations/copy.html',
    )
    def copy_columns(
        self,
        row: dict,
    ):
        trfn_settings = (
            self.transformation_request['transformation']['settings']
        )
        result = {}

        for setting in trfn_settings:
            result[setting['to']] = row[setting['from']]

        return RowTransformationResponse.done(result)


class CopyColumnWebAppMixin:

    @router.post(
        '/validate/copy_columns',
        summary='Validate copy columns settings',
    )
    def validate_copy_columns_settings(
        self,
        data: dict,
    ):
        return validate_copy_columns(data)
