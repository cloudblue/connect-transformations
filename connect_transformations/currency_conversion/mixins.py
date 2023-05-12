# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from decimal import Decimal
from typing import List

import httpx
import requests
from connect.eaas.core.decorators import router, transformation
from connect.eaas.core.responses import RowTransformationResponse

from connect_transformations.currency_conversion.exceptions import CurrencyConversionError
from connect_transformations.currency_conversion.models import Configuration, Currency
from connect_transformations.currency_conversion.utils import validate_currency_conversion
from connect_transformations.models import Error, ValidationResult
from connect_transformations.utils import is_input_column_nullable


class CurrencyConverterTransformationMixin:

    def preload_currency_conversion_rates(self, currency_from, currency_to):
        with self.lock():
            if hasattr(self, 'currency_conversion_rates'):
                return

            self.currency_conversion_rates = {}

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
                self.currency_conversion_rates[currency_to] = Decimal(data['rates'][currency_to])
            except requests.RequestException as exc:
                raise CurrencyConversionError(
                    f'An error occurred while requesting {url} with '
                    f'params {params}: {exc}',
                )

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
        trfn_settings = self.transformation_request['transformation']['settings']
        value = row[trfn_settings['from']['column']]
        currency = trfn_settings['from']['currency']
        currency_to = trfn_settings['to']['currency']

        try:
            self.preload_currency_conversion_rates(
                currency,
                currency_to,
            )
        except Exception as e:
            return RowTransformationResponse.fail(output=str(e))

        if is_input_column_nullable(
            self.transformation_request['transformation']['columns']['input'],
            trfn_settings['from']['column'],
        ) and not value:
            return RowTransformationResponse.skip()

        return RowTransformationResponse.done({
            trfn_settings['to']['column']: (
                Decimal(value) * self.currency_conversion_rates[currency_to]
            ).quantize(
                Decimal('.00001'),
            ),
        })


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
