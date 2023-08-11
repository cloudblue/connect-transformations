# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from typing import Dict

import jq
from connect.eaas.core.decorators import router, transformation
from connect.eaas.core.responses import RowTransformationResponse

from connect_transformations.filter_row.models import Configuration
from connect_transformations.filter_row.utils import validate_filter_row
from connect_transformations.models import Error, ValidationResult


class FilterRowTransformationMixin:

    def precompile_filter_expression(self):
        with self.lock():
            if hasattr(self, 'filter_row_expression'):
                return

            trfn_settings = self.transformation_request['transformation']['settings']
            comparison = "==" if trfn_settings["match_condition"] else "!="
            operation = 'or' if trfn_settings["match_condition"] else 'and'
            column = trfn_settings["from"]
            filter_expression = f'."{column}" {comparison} "{trfn_settings["value"]}"'

            for condition in trfn_settings['additional_values']:
                filter_expression += (
                    f' {operation} ."{column}" {comparison} "{condition["value"]}"'
                )
            self.filter_row_expression = jq.compile(filter_expression)

    @transformation(
        name='Delete rows by condition',
        description=(
            'This transformation function allows you to delete'
            ' rows that contain or do not contain a specific value(s).'
        ),
        edit_dialog_ui='/static/transformations/filter_row.html',
    )
    def filter_row(
        self,
        row: Dict,
    ):
        trfn_settings = (
            self.transformation_request['transformation']['settings']
        )
        if trfn_settings.get('additional_values'):
            self.precompile_filter_expression()

            if self.filter_row_expression.input(row).first():
                return RowTransformationResponse.done({trfn_settings['from']: None})

        elif (
            trfn_settings.get('match_condition', True)
            and trfn_settings['value'] == row[trfn_settings['from']]
            or not trfn_settings.get('match_condition', True)
            and trfn_settings['value'] != row[trfn_settings['from']]
        ):
            return RowTransformationResponse.done({trfn_settings['from']: None})

        return RowTransformationResponse.delete()


class FilterRowWebAppMixin:

    @router.post(
        '/filter_row/validate',
        summary='Validate filter row by condition settings',
        response_model=ValidationResult,
        responses={
            400: {'model': Error},
        },
    )
    def validate_filter_row_settings(
        self,
        data: Configuration,
    ):
        return validate_filter_row(data)
