# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import requests
from connect.eaas.core.decorators import router, transformation
from connect.eaas.core.responses import RowTransformationResponse

from connect_transformations.models import Error, ValidationResult
from connect_transformations.utils import is_input_column_nullable
from connect_transformations.vat_rate.exceptions import VATRateError
from connect_transformations.vat_rate.models import Configuration
from connect_transformations.vat_rate.utils import validate_vat_rate


class VATRateForEUCountryTransformationMixin:

    def preload_eu_vat_rates(self):
        with self.lock():
            if hasattr(self, 'eu_vat_rates'):
                return

            self.eu_vat_rates = {}

            try:
                url = 'https://api.exchangerate.host/vat_rates'
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                if not data['success']:
                    raise VATRateError(
                        f'Unexpected response calling {url}',
                    )
                for key, rate in data['rates'].items():
                    value = rate['standard_rate']
                    self.eu_vat_rates[key] = value
                    self.eu_vat_rates[rate['country_name']] = value
            except requests.RequestException as exc:
                raise VATRateError(
                    f'An error occurred while requesting {url}: {exc}',
                )

    @transformation(
        name='Get standard VAT rate for EU country',
        description=(
            'This transformation function is performed, using the latest'
            ' rates from the [Exchange rates API](https://exchangerate.host). '
            'The input value must be either a two-letter country code defined'
            ' in the ISO 3166-1 alpha-2 standard or country name. '
            'For example, ES or Spain.'
        ),
        edit_dialog_ui='/static/transformations/vat_rate.html',
    )
    def get_vat_rate(
        self,
        row,
    ):
        trfn_settings = self.transformation_request['transformation']['settings']
        country = row[trfn_settings['from']]
        column_to = trfn_settings['to']
        leave_empty = trfn_settings['action_if_not_found'] == 'leave_empty'

        try:
            self.preload_eu_vat_rates()
        except Exception as e:
            return RowTransformationResponse.fail(output=str(e))

        if (
            is_input_column_nullable(
                self.transformation_request['transformation']['columns']['input'],
                trfn_settings['from'],
            ) and not country
            or country not in self.eu_vat_rates
            and leave_empty
        ):
            return RowTransformationResponse.skip()

        if country not in self.eu_vat_rates and not leave_empty:
            return RowTransformationResponse.fail(
                output=f'Country {country} not found',
            )

        return RowTransformationResponse.done({
            column_to: self.eu_vat_rates[country],
        })


class VATRateForEUCountryWebAppMixin:

    @router.post(
        '/vat_rate/validate',
        summary='Validate VAT rate settings',
        response_model=ValidationResult,
        responses={
            400: {'model': Error},
        },
    )
    def validate_get_vat_rate_settings(
        self,
        data: Configuration,
    ):
        return validate_vat_rate(data)
