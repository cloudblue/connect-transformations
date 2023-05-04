# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import httpx
from connect.eaas.core.decorators import router, transformation
from connect.eaas.core.responses import RowTransformationResponse

from connect_transformations.exceptions import VATRateError
from connect_transformations.utils import is_input_column_nullable
from connect_transformations.vat_rate.utils import validate_vat_rate


class VATRateForEUCountryTransformationMixin:

    def _process_rates(self, rates):
        result = {}
        for key, rate in rates.items():
            value = rate['standard_rate']
            result[key] = value
            result[rate['country_name']] = value
        return result

    async def _generate_vat_rate(self):
        if not self.current_vat_rate:
            async with self._current_vat_rate_lock:
                if not self.current_vat_rate:
                    try:
                        url = 'https://api.exchangerate.host/vat_rates'
                        with httpx.Client(
                            transport=httpx.HTTPTransport(retries=3),
                        ) as client:
                            response = client.get(url)
                            data = response.json()
                            if response.status_code != 200 or not data['success']:
                                raise VATRateError(
                                    f'Unexpected response calling {url}',
                                )
                            self.current_vat_rate = self._process_rates(data['rates'])
                    except httpx.RequestError as exc:
                        raise VATRateError(
                            f'An error occurred while requesting {url}: {exc}',
                        )

    @transformation(
        name='Get standard VAT Rate for EU Country',
        description=(
            'Lates rates from the https://exchangerate.host API will be used to perform this '
            'transformation. The input content should be either ISO 3166 alpha-2 code or country '
            'name in english. For instance ES or Spain.'
        ),
        edit_dialog_ui='/static/transformations/vat_rate.html',
    )
    async def get_vat_rate(
        self,
        row,
    ):
        trfn_settings = self.transformation_request['transformation']['settings']
        country = row[trfn_settings['from']]
        column_to = trfn_settings['to']
        leave_empty = trfn_settings['action_if_not_found'] == 'leave_empty'

        try:
            await self._generate_vat_rate()
        except Exception as e:
            return RowTransformationResponse.fail(output=str(e))

        if (
            is_input_column_nullable(
                self.transformation_request['transformation']['columns']['input'],
                trfn_settings['from'],
            ) and not country
            or country not in self.current_vat_rate
            and leave_empty
        ):
            return RowTransformationResponse.skip()

        if country not in self.current_vat_rate and not leave_empty:
            return RowTransformationResponse.fail(
                output=f'Country {country} not found',
            )

        return RowTransformationResponse.done({
            column_to: self.current_vat_rate[country],
        })


class VATRateForEUCountryWebAppMixin:

    @router.post(
        '/validate/vat_rate',
        summary='Validate VAT rate settings',
    )
    def validate_get_vat_rate_settings(
        self,
        data: dict,
    ):
        return validate_vat_rate(data)
