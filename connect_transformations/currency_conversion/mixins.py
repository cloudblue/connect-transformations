# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from decimal import Decimal

import httpx
from connect.eaas.core.decorators import router, transformation

from connect_transformations.currency_conversion.utils import validate_currency_conversion
from connect_transformations.exceptions import CurrencyConversionError
from connect_transformations.utils import is_input_column_nullable


class CurrencyConverterTransformationMixin:

    async def _generate_current_exchange_rate(self, currency_from, currency_to):
        if not self.current_exchange_rate:
            async with self._current_exchange_rate_lock:
                if not self.current_exchange_rate:
                    try:
                        url = 'https://api.exchangerate.host/latest'
                        params = {
                            'symbols': currency_to,
                            'base': currency_from,
                        }
                        with httpx.Client(
                            transport=httpx.HTTPTransport(retries=3),
                        ) as client:
                            response = client.get(
                                url,
                                params=params,
                            )
                            data = response.json()
                            if response.status_code != 200 or not data['success']:
                                raise CurrencyConversionError(
                                    f'Unexpected response calling {url}'
                                    f' with params {params}',
                                )
                            self.current_exchange_rate = Decimal(data['rates'][currency_to])
                    except httpx.RequestError as exc:
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
    async def currency_conversion(
        self,
        row,
    ):
        trfn_settings = self.transformation_request['transformation']['settings']
        value = row[trfn_settings['from']['column']]
        currency = trfn_settings['from']['currency']
        currency_to = trfn_settings['to']['currency']

        await self._generate_current_exchange_rate(
            currency,
            currency_to,
        )

        if is_input_column_nullable(
            self.transformation_request['transformation']['columns']['input'],
            trfn_settings['from']['column'],
        ) and not value:
            return {trfn_settings['to']['column']: None}

        return {
            trfn_settings['to']['column']: (
                Decimal(value) * self.current_exchange_rate
            ).quantize(
                Decimal('.00001'),
            ),
        }


class CurrencyConversionWebAppMixin:

    @router.post(
        '/validate/currency_conversion',
        summary='Validate currency conversion settings',
    )
    def validate_currency_conversion_settings(
        self,
        data: dict,
    ):
        return validate_currency_conversion(data)

    @router.get(
        '/currency_conversion/currencies',
        summary='List available exchange rates',
        response_model=dict,
    )
    async def get_available_rates(self):
        try:
            url = 'https://api.exchangerate.host/symbols'
            async with httpx.AsyncClient(
                transport=httpx.AsyncHTTPTransport(retries=3),
            ) as client:
                response = await client.get(url)
            data = response.json()
            if response.status_code != 200 or not data['success']:
                return {}
            currencies = {}
            for key in data['symbols'].keys():
                element = data['symbols'][key]
                currencies[element['code']] = element['description']
            return currencies
        except Exception:
            return {}
