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
from connect.eaas.core.inject.common import get_config
from connect.eaas.core.responses import RowTransformationResponse
from fastapi import Depends

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
                    self._currency_rates[key] = load_currency_rate(
                        currency_from,
                        currency_to,
                        self.config.get('EXCHANGE_API_KEY'),
                    )

        return self._currency_rates[key]

    @cached_property
    def input_columns(self):
        input_columns = self.transformation_request['transformation']['columns']['input']
        return {c['id']: c for c in input_columns}

    @transformation(
        name='Convert currency',
        description=(
            'This transformation function allows you to convert currency rates, using the '
            '[Open Exchange Rates API](https://openexchangerates.org).'
        ),
        edit_dialog_ui='/static/transformations/currency_conversion.html',
    )
    def currency_conversion(
        self,
        row,
    ):
        return_values = {}
        settings = self.transformation_request['transformation']['settings']
        if not isinstance(settings, (tuple, list)):
            settings = [settings]

        for conv_settings in settings:
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
    async def get_available_currencies(
        self,
        config: dict = Depends(get_config),
    ):
        try:
            url = 'https://openexchangerates.org/api/currencies.json'
            async with httpx.AsyncClient(
                transport=httpx.AsyncHTTPTransport(retries=3),
            ) as client:
                response = await client.get(
                    url,
                    params={'app_id': config['EXCHANGE_API_KEY']},
                )
            data = response.json()
            if response.status_code != 200:
                return []
            currencies = []
            for key in data:
                currencies.append(
                    Currency(
                        code=key,
                        description=data[key],
                    ),
                )
            return currencies
        except Exception:
            return []
