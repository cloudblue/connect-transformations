# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from typing import Dict

from connect.eaas.core.decorators import router, transformation
from connect.eaas.core.responses import RowTransformationResponse

from connect_transformations.copy_columns.models import Configuration
from connect_transformations.copy_columns.utils import validate_copy_columns
from connect_transformations.models import Error, ValidationResult


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
        row: Dict,
        row_styles: Dict = None,
    ):
        trfn_settings = (
            self.transformation_request['transformation']['settings']
        )
        result = {}
        result_styles = {}

        for setting in trfn_settings:
            result[setting['to']] = row[setting['from']]
            if row_styles:
                result_styles[setting['to']] = row_styles[setting['from']]

        return RowTransformationResponse.done(result, result_styles)


class CopyColumnWebAppMixin:

    @router.post(
        '/copy_columns/validate',
        summary='Validate copy columns settings',
        response_model=ValidationResult,
        responses={
            400: {'model': Error},
        },
    )
    def validate_copy_columns_settings(
        self,
        data: Configuration,
    ):
        return validate_copy_columns(data)
