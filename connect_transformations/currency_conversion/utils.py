# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from decimal import Decimal

import requests

from connect_transformations.currency_conversion.exceptions import CurrencyConversionError
from connect_transformations.utils import (
    build_error_response,
    does_not_contain_required_keys,
    has_invalid_basic_structure,
)


def validate_currency_conversion(data):
    data = data.dict(by_alias=True)

    if has_invalid_basic_structure(data, data_type=(list, dict)):
        return build_error_response('Invalid input data')

    trf_settings = data['settings']
    if not isinstance(trf_settings, list):
        trf_settings = [trf_settings]

    input_columns = data['columns']['input']
    available_input_columns = {c['id']: c for c in input_columns}

    overview = ''

    for row in trf_settings:
        if (
            does_not_contain_required_keys(
                row,
                ['from', 'to'],
            ) or does_not_contain_required_keys(
                row['from'],
                ['column', 'currency'],
            ) or does_not_contain_required_keys(
                row['to'],
                ['column', 'currency'],
            )
        ):
            return build_error_response(
                'The settings must have `from` with the `column` and the `currency`, and '
                '`to` with the `column` and `currency` fields',
            )

        if row['from']['currency'] == row['to']['currency']:
            return build_error_response(
                'The settings must have different currencies for `from` and `to`',
            )

        if row['from']['column'] not in available_input_columns:
            return build_error_response(
                'The settings contains an invalid `from` column name'
                f' "{row["from"]["column"]}" that does not exist on '
                'columns.input',
            )

        if overview:
            overview += '\n'

        overview += 'From: {src} ({src_curr})\nTo: {dst} ({dst_curr})\n'.format(
            src=available_input_columns[row['from']['column']]['name'],
            src_curr=row['from']['currency'],
            dst=row['to']['column'],
            dst_curr=row['to']['currency'],
        )

    return {
        'overview': overview,
    }


def load_currency_rate(currency_from, currency_to):
    try:
        url = 'https://api.exchangerate.host/latest'
        params = {
            'symbols': currency_to,
            'base': currency_from,
        }

        response = requests.get(
            url,
            params=params,
        )
        response.raise_for_status()
        data = response.json()

        if not data['success']:
            raise CurrencyConversionError(
                f'Unexpected response calling {url}'
                f' with params {params}',
            )

        return Decimal(data['rates'][currency_to])
    except requests.RequestException as exc:
        raise CurrencyConversionError(
            f'An error occurred while requesting {url} with '
            f'params {params}: {exc}',
        )
