# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import re

import jq
from fastapi.responses import JSONResponse

from connect_transformations.utils import _cast_mapping


JQ_FIELDS_REGEX = re.compile(r'(\.([a-z_][a-z0-9_]*))|(\."(.+?)")|(\.\["(.+?)"\])', re.I)
DROP_REGEX = re.compile(r'(?<![."])drop_row(?![."])', re.I)


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
            or 'type' not in expression
            or expression['type'] not in _cast_mapping.keys()
            or 'ignore_errors' not in expression
            or not isinstance(expression['ignore_errors'], bool)
        ):
            return error_response(
                'Each expression must have not empty `to`, `formula`, `type` '
                'and `ignore_errors` fields.',
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

        columns = [
            r[1] or r[3] or r[5]
            for r in JQ_FIELDS_REGEX.findall(expression['formula'])
        ]

        for column in columns:
            if column not in available_columns:
                return error_response(
                    (
                        f'Settings contains formula `{expression["formula"]}` '
                        'with column that does not exist on columns.input.'
                    ),
                )

        try:
            formula = expression['formula']
            if DROP_REGEX.findall(formula):
                formula = f'def drop_row: "#DROP_ROW"; {formula}'
            jq.compile(formula)
        except ValueError as e:
            return error_response(
                f'Settings contains invalid formula `{expression["formula"]}: {str(e)}`.',
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
        input_columns.update([
            r[1] or r[3] or r[5]
            for r in JQ_FIELDS_REGEX.findall(expression['formula'])
        ])
    return [column for column in data['columns'] if column['name'] in input_columns]
