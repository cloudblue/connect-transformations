# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from connect.eaas.core.decorators import router, transformation
from connect.eaas.core.responses import RowTransformationResponse

from connect_transformations.filter_row.utils import validate_filter_row


class FilterRowTransformationMixin:

    @transformation(
        name='Filter row by condition',
        description=(
            'This transformation function allows you to filter by equality of a given input column'
            ' with a given string value. If it matches the row is kept, if not it is marked to be '
            'deleted.'
        ),
        edit_dialog_ui='/static/transformations/filter_row.html',
    )
    def filter_row(
        self,
        row: dict,
    ):
        trfn_settings = (
            self.transformation_request['transformation']['settings']
        )
        if trfn_settings['value'] == row[trfn_settings['from']]:
            return RowTransformationResponse.done({trfn_settings['from']: None})
        return RowTransformationResponse.delete()


class FilterRowWebAppMixin:

    @router.post(
        '/validate/filter_row',
        summary='Validate filter row by condition settings',
    )
    def validate_filter_row_settings(
        self,
        data: dict,
    ):
        return validate_filter_row(data)
