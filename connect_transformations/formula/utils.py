# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import re

import jq
from fastapi.responses import JSONResponse

from connect_transformations.utils import (
    _cast_mapping,
    build_error_response,
    does_not_contain_required_keys,
    has_invalid_basic_structure,
)


JQ_FIELDS_REGEX = re.compile(r'(\.([a-z_][a-z0-9_]*))|(\."(.+?)")|(\.\["(.+?)"\])', re.I)
DROP_REGEX = re.compile(r'(?<![."])drop_row(?![."])', re.I)


def validate_formula(data):  # noqa: CCR001
    data = data.dict(by_alias=True)

    if (
        has_invalid_basic_structure(data)
        or does_not_contain_required_keys(data['columns'], ['output'])
    ):
        print('error')
        return build_error_response('Invalid input data')

    if (
        does_not_contain_required_keys(data['settings'], ['expressions'])
        or not isinstance(data['settings']['expressions'], list)
    ):
        return build_error_response(
            'The settings must have `expressions` field which contains list of formulas.',
        )

    for expression in data['settings']['expressions']:
        if (
            does_not_contain_required_keys(
                expression,
                ['to', 'formula', 'type', 'ignore_errors'],
            ) or not isinstance(expression['to'], str)
            or not isinstance(expression['formula'], str)
            or expression['type'] not in _cast_mapping.keys()
            or not isinstance(expression['ignore_errors'], bool)
        ):
            return build_error_response(
                'Each expression must have not empty `to`, `formula`, `type` '
                'and `ignore_errors` fields.',
            )

    output_columns = []
    available_columns = {col['name']: col['id'] for col in data['columns']['input']}

    for expression in data['settings']['expressions']:
        if expression['to'] in output_columns:
            return build_error_response('Each `output column` must be unique.')

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
                return build_error_response(f'Column `{expression["to"]}` already exists.')

        columns = [
            r[1] or r[3] or r[5]
            for r in JQ_FIELDS_REGEX.findall(expression['formula'])
        ]

        for column in columns:
            if column not in available_columns:
                return build_error_response(
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
            return build_error_response(
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
