# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from decimal import Decimal
from functools import cached_property
from typing import List

import httpx
from connect.eaas.core.decorators import router, transformation
from connect.eaas.core.responses import RowTransformationResponse

from connect_transformations.currency_conversion.models import Configuration, Currency
from connect_transformations.currency_conversion.utils import (
    load_currency_rate,
    validate_currency_conversion,
)
from connect_transformations.models import Error, ValidationResult
from connect_transformations.utils import is_input_column_nullable


class CurrencyConverterTransformationMixin:

    def get_currency_rate(self, currency_from, currency_to):
        if not hasattr(self, '_currency_rates'):
            self._currency_rates = {}

        key = (currency_from, currency_to)

        if key not in self._currency_rates:
            with self.lock():
                if key not in self._currency_rates:
                    self._currency_rates[key] = load_currency_rate(currency_from, currency_to)

        return self._currency_rates[key]

    @cached_property
    def input_columns(self):
        input_columns = self.transformation_request['transformation']['columns']['input']
        return {c['id']: c for c in input_columns}

    @transformation(
        name='Convert Currency',
        description=(
            'This transformation function allows you to make rate convertions using the '
            'https://exchangerate.host API.'
        ),
        edit_dialog_ui='/static/transformations/currency_conversion.html',
    )
    def currency_conversion(
        self,
        row,
    ):
        return_values = {}

        for conv_settings in self.transformation_request['transformation']['settings']:
            col_name = self.input_columns[conv_settings['from']['column']]['name']
            value = row[col_name]
            currency_from = conv_settings['from']['currency']
            currency_to = conv_settings['to']['currency']

            if (not value) and is_input_column_nullable(
                self.transformation_request['transformation']['columns']['input'],
                col_name,
            ):
                return RowTransformationResponse.skip()

            try:
                return_values[conv_settings['to']['column']] = (
                    Decimal(value) * self.get_currency_rate(currency_from, currency_to)
                ).quantize(
                    Decimal('.00001'),
                )
            except Exception as e:
                return RowTransformationResponse.fail(output=str(e))
        return RowTransformationResponse.done(return_values)


class CurrencyConversionWebAppMixin:

    @router.post(
        '/currency_conversion/validate',
        summary='Validate currency conversion settings',
        response_model=ValidationResult,
        responses={
            400: {'model': Error},
        },
    )
    def validate_currency_conversion_settings(
        self,
        data: Configuration,
    ):
        return validate_currency_conversion(data)

    @router.get(
        '/currency_conversion/currencies',
        summary='List available exchange rates',
        response_model=List[Currency],
        responses={
            400: {'model': Error},
        },
    )
    async def get_available_currencies(self):
        try:
            url = 'https://api.exchangerate.host/symbols'
            async with httpx.AsyncClient(
                transport=httpx.AsyncHTTPTransport(retries=3),
            ) as client:
                response = await client.get(url)
            data = response.json()
            if response.status_code != 200 or not data['success']:
                return []
            currencies = []
            for key in data['symbols'].keys():
                element = data['symbols'][key]
                currencies.append(
                    Currency(
                        code=element['code'],
                        description=element['description'],
                    ),
                )
            return currencies
        except Exception:
            return []
