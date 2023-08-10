# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from typing import Dict, List

from connect.eaas.core.decorators import router, transformation
from connect.eaas.core.responses import RowTransformationResponse

from connect_transformations.formula.models import Configuration
from connect_transformations.formula.utils import (
    DROP_REGEX,
    clear_formula,
    compile_formula,
    extract_input,
    validate_formula,
)
from connect_transformations.models import Error, StreamsColumn, ValidationResult
from connect_transformations.utils import cast_value_to_type


class FormulaTransformationMixin:

    def precompile(self, row: Dict):
        with self.lock():
            if hasattr(self, 'jq_expressions'):
                return

            self.jq_expressions = {}

            trfn_settings = self.transformation_request['transformation']['settings']
            for expression in trfn_settings['expressions']:
                formula = expression['formula']
                if DROP_REGEX.findall(formula):
                    formula = f'def drop_row: "#INSTRUCTION/DELETE_ROW"; {formula}'
                clean_formula = clear_formula(formula)
                self.jq_expressions[expression['to']] = compile_formula(
                    clean_formula,
                    stream=self.transformation_request['stream'],
                    batch=self.transformation_request['batch'],
                )

            self.column_converters = []

            input_columns = self.transformation_request['transformation']['columns']['input']
            columns_types = {column['name']: column.get('type') for column in input_columns}
            for col_name in row:
                if columns_types.get(col_name) == 'datetime':
                    self.column_converters.append((col_name, str))

    @transformation(
        name='Formula',
        description=(
            'This transformation function allows you to perform'
            ' mathematical and logical operations on columns and'
            ' context variables using the jq programming language.'
        ),
        edit_dialog_ui='/static/transformations/formula.html',
    )
    def formula(
        self,
        row: Dict,
    ):
        try:
            self.precompile(row)
        except Exception as e:
            return RowTransformationResponse.fail(output=str(e))

        trfn_settings = self.transformation_request['transformation']['settings']

        for col_name, converter in self.column_converters:
            row[col_name] = converter(row[col_name])

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
