# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import re

import jq
from fastapi.responses import JSONResponse


def error_response(error):
    return JSONResponse(
        status_code=400,
        content={
            'error': error,
        },
    )


def strip_column_name(value):
    return ''.join([c for c in value if c.isalnum()])


def validate_formula(data):  # noqa: CCR001
    if (
        'settings' not in data
        or not isinstance(data['settings'], dict)
        or 'columns' not in data
        or 'input' not in data['columns']
    ):
        return error_response('Invalid input data.')

    if (
        'expressions' not in data['settings']
        or not isinstance(data['settings']['expressions'], list)
    ):
        return error_response(
            'The settings must have `expressions` field which contains list of formulas.',
        )

    for expression in data['settings']['expressions']:
        if (
            'to' not in expression
            or not isinstance(expression['to'], str)
            or 'formula' not in expression
            or not isinstance(expression['formula'], str)
        ):
            return error_response('Each expression must have `to` and `formula` fields.')

    input_columns = data['columns']['input']
    available_input_columns = [c['name'] for c in input_columns]
    output_columns = []
    for expression in data['settings']['expressions']:
        if (
            expression['to'] in available_input_columns
            or expression['to'] in output_columns
        ):
            return error_response('Each `output column` must be unique.')

        columns = re.findall(r'\.\(.*?\)', expression['formula'])
        formula_to_compile = expression['formula']
        for column in columns:
            if column[2:-1] not in available_input_columns:
                return error_response(
                    (
                        f'Settings contains formula `{expression["formula"]}` '
                        'with column that does not exist on columns.input.'
                    ),
                )
            formula_to_compile = formula_to_compile.replace(
                column,
                f'.{strip_column_name(column[2:-1])}',
            )

        try:
            jq.compile(formula_to_compile)
        except ValueError:
            return error_response(
                f'Settings contains invalid formula `{expression["formula"]}`.',
            )

        output_columns.append(expression['to'])

    overview = ''
    for expression in data['settings']['expressions']:
        overview += f'Output column = {expression["to"]}, Formula = {expression["formula"]}\n'
    return {
        'overview': overview,
    }
