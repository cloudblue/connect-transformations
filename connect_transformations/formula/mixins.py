# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from typing import Dict, List

import jq
from connect.eaas.core.decorators import router, transformation
from connect.eaas.core.responses import RowTransformationResponse

from connect_transformations.formula.models import Configuration
from connect_transformations.formula.utils import DROP_REGEX, extract_input, validate_formula
from connect_transformations.models import Error, StreamsColumn, ValidationResult
from connect_transformations.utils import cast_value_to_type


class FormulaTransformationMixin:

    def precompile_jq_expressions(self):
        with self.lock():
            if hasattr(self, 'jq_expressions'):
                return

            self.jq_expressions = {}

            trfn_settings = self.transformation_request['transformation']['settings']
            for expression in trfn_settings['expressions']:
                formula = expression['formula']
                if DROP_REGEX.findall(formula):
                    formula = f'def drop_row: "#INSTRUCTION/DELETE_ROW"; {formula}'
                self.jq_expressions[expression['to']] = jq.compile(formula)

    @transformation(
        name='Formula',
        description=(
            'Use this transformation to perform data manipulation '
            'using columns manipulation formula. Also it is possible '
            'to use reserved function drop_row to delete row.'
            '(see https://stedolan.github.io/jq/manual/)'
        ),
        edit_dialog_ui='/static/transformations/formula.html',
    )
    def formula(
        self,
        row: Dict,
    ):

        try:
            self.precompile_jq_expressions()
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
                    parameters['additional_parameters'] = {'precision': expression.get('precision')}
                result[expression['to']] = cast_value_to_type(**parameters)
            except StopIteration:
                result[expression['to']] = None
            except Exception as e:
                self.logger.exception('Something went wrong!')
                if not expression.get('ignore_errors'):
                    return RowTransformationResponse.fail(output=str(e))
                else:
                    result[expression['to']] = None

        return RowTransformationResponse.done(result)


class FormulaWebAppMixin:

    @router.post(
        '/formula/validate',
        summary='Validate formula settings',
        response_model=ValidationResult,
        responses={
            400: {'model': Error},
        },
    )
    def validate_formula_settings(
        self,
        data: Configuration,
    ):
        return validate_formula(data)

    @router.post(
        '/formula/extract_input',
        summary='Extract input columns',
        response_model=List[StreamsColumn],
        responses={
            400: {'model': Error},
        },
    )
    def extract_formula_input(
        self,
        data: Dict,
    ):
        return extract_input(data)
