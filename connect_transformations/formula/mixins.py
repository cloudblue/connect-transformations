# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import re

import jq
from connect.eaas.core.decorators import router, transformation
from connect.eaas.core.responses import RowTransformationResponse

from connect_transformations.formula.utils import extract_input, validate_formula
from connect_transformations.utils import cast_value_to_type


class FormulaTransformationMixin:

    @transformation(
        name='Formula',
        description=(
            'Use this transformation to perform data manipulation '
            'using columns manipulation formula. '
            '(see https://stedolan.github.io/jq/manual/)'
        ),
        edit_dialog_ui='/static/transformations/formula.html',
    )
    def formula(
        self,
        row: dict,
    ):

        try:
            self.precompile_jq_expression()
        except Exception as e:
            return RowTransformationResponse.fail(output=str(e))

        trfn_settings = self.transformation_request['transformation']['settings']
        input_columns = self.transformation_request['transformation']['columns']['input']
        columns_types = {column['name']: column.get('type') for column in input_columns}

        for column in row:
            if columns_types[column] == 'datetime':
                row[column] = str(row[column])

        result = {}
        for expression in trfn_settings['expressions']:
            try:
                value = self.jq_expressions[expression['to']].input(row).first()
                column_type = expression.get('type', 'string')
                parameters = {'value': value, 'type': column_type}
                if column_type == 'decimal':
                    parameters['additional_parameters'] = {'precision': expression['precision']}
                result[expression['to']] = cast_value_to_type(**parameters)
            except Exception as e:
                return RowTransformationResponse.fail(output=str(e))

        return RowTransformationResponse.done(result)

    def precompile_jq_expression(self):
        with self._sync_lock:
            if hasattr(self, 'jq_expressions'):
                return
            self.jq_expressions = {}
            trfn_settings = self.transformation_request['transformation']['settings']
            for expression in trfn_settings['expressions']:
                columns = re.findall(r'\.\([^\"\)]*\)', expression['formula'])
                formula_to_compile = expression['formula']

                for column in columns:
                    formula_to_compile = formula_to_compile.replace(
                        column,
                        f'."{column[2:-1]}"',
                    )

                self.jq_expressions[expression['to']] = jq.compile(formula_to_compile)


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
