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


def validate_formula(data):  # noqa: CCR001
    if (
        'settings' not in data
        or not isinstance(data['settings'], dict)
        or 'columns' not in data
        or 'input' not in data['columns']
        or 'output' not in data['columns']
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
            or not expression['to']
            or not isinstance(expression['to'], str)
            or not expression['formula']
            or 'formula' not in expression
            or not isinstance(expression['formula'], str)
        ):
            return error_response(
                'Each expression must have not empty `to` and `formula` fields.',
            )

    output_columns = []
    available_columns = {col['name']: col['id'] for col in data['columns']['input']}

    for expression in data['settings']['expressions']:
        if expression['to'] in output_columns:
            return error_response('Each `output column` must be unique.')

        if expression['to'] in available_columns:
            output_column = list(filter(
                lambda col: col['name'] == expression['to'],
                data['columns']['output'],
            ))
            if (
                len(output_column) != 1
                or not output_column[0].get('id')
                or output_column[0]['id'] != available_columns[expression['to']]
            ):
                return error_response(f'Column `{expression["to"]}` already exists.')

        formula_to_compile = str(expression['formula'])

        columns = re.findall(r'\.[a-zA-Z]\w*', expression['formula'])
        for column in columns:
            if column[1:] not in available_columns:
                return error_response(
                    (
                        f'Settings contains formula `{expression["formula"]}` '
                        'with column that does not exist on columns.input.'
                    ),
                )

        columns = re.findall(r'\."[\w (),]+"', expression['formula'])
        for column in columns:
            if column[2:-1] not in available_columns:
                return error_response(
                    (
                        f'Settings contains formula `{expression["formula"]}` '
                        'with column that does not exist on columns.input.'
                    ),
                )

        columns = re.findall(r'\.\([a-zA-Z][^\(]*?\)', expression['formula'])
        for column in columns:
            if column[2:-1] not in available_columns:
                return error_response(
                    (
                        f'Settings contains formula `{expression["formula"]}` '
                        'with column that does not exist on columns.input.'
                    ),
                )
            formula_to_compile = formula_to_compile.replace(
                column,
                f'."{(column[2:-1])}"',
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
        overview += f'{expression["to"]} = {expression["formula"]}\n'

    return {'overview': overview}


def extract_input(data):
    if 'expressions' not in data or not isinstance(data['expressions'], list):
        return JSONResponse(
            status_code=400,
            content={
                'error': 'The body does not contain `expressions` list',
            },
        )
    if 'columns' not in data or not isinstance(data['columns'], list):
        return JSONResponse(
            status_code=400,
            content={
                'error': 'The body does not contain `columns` list',
            },
        )

    input_columns = set()
    for expression in data['expressions']:
        columns = re.findall(r'\.[a-zA-Z]\w*', expression['formula'])
        input_columns.update([column[1:] for column in columns])

        columns = re.findall(r'\."[\w ]+"', expression['formula'])
        input_columns.update([column[2:-1] for column in columns])

        columns = re.findall(r'\.\([a-zA-Z][^\(]*?\)', expression['formula'])
        input_columns.update([column[2:-1] for column in columns])

    return [column for column in data['columns'] if column['name'] in input_columns]
