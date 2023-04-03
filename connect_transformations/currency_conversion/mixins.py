# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import httpx
from connect.eaas.core.decorators import router, transformation

from connect_transformations.currency_conversion.utils import validate_currency_conversion
from connect_transformations.exceptions import CurrencyConversion
from connect_transformations.utils import is_input_column_nullable


class CurrencyConverterTransformationMixin:

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

        if is_input_column_nullable(
            self.transformation_request['transformation']['columns']['input'],
            trfn_settings['from']['column'],
        ) and not value:
            return {trfn_settings['to']['column']: None}

        try:
            params = {
                'from': currency,
                'to': currency_to,
                'amount': value,
            }
            async with httpx.AsyncClient(
                verify=self._ssl_context,
                transport=httpx.AsyncHTTPTransport(retries=3),
            ) as client:
                response = await client.get(
                    'https://api.exchangerate.host/convert',
                    params=params,
                )
                data = response.json()
                if response.status_code != 200 or not data['success']:
                    raise CurrencyConversion(
                        'Unexpected response calling https://api.exchangerate.host/convert'
                        f' with params {params}',
                    )
        except httpx.RequestError as exc:
            raise CurrencyConversion(
                'An error occurred while requesting https://api.exchangerate.host/convert with '
                f'params {params}: {exc}',
            )
        return {trfn_settings['to']['column']: data['result']}


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
