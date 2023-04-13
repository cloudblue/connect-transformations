# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import re

import jq
from connect.eaas.core.decorators import router, transformation

from connect_transformations.formula.utils import extract_input, strip_column_name, validate_formula


class FormulaTransformationMixin:

    @transformation(
        name='Formula',
        description=(
            'Use this transformation to perform data manipulation '
            'using columns manipulation formula.'
        ),
        edit_dialog_ui='/static/transformations/formula.html',
    )
    def formula(
        self,
        row: dict,
    ):

        trfn_settings = self.transformation_request['transformation']['settings']
        input_columns = self.transformation_request['transformation']['columns']['input']
        columns_types = {column['name']: column.get('type') for column in input_columns}

        row_stripped = {}
        for column in row:
            if columns_types[column] == 'datetime':
                row_stripped[strip_column_name(column)] = str(row[column])
            else:
                row_stripped[strip_column_name(column)] = row[column]

        result = {}
        for expression in trfn_settings['expressions']:
            columns = re.findall(r'\.\(.*?\)', expression['formula'])
            formula_to_compile = expression['formula']
            for column in columns:
                formula_to_compile = formula_to_compile.replace(
                    column,
                    f'.{strip_column_name(column[2:-1])}',
                )

            result[expression['to']] = jq.compile(formula_to_compile).input(row_stripped).first()

        return result


class FormulaWebAppMixin:

    @router.post(
        '/validate/formula',
        summary='Validate formula settings',
    )
    def validate_formula_settings(
        self,
        data: dict,
    ):
        return validate_formula(data)

    @router.post(
        '/formula/extract_input',
        summary='Extract input columns',
    )
    def extract_formula_input(
        self,
        data: dict,
    ):
        return extract_input(data)
