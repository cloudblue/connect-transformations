# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest
from connect.eaas.core.enums import ResultType

from connect_transformations.exceptions import BaseTransformationException
from connect_transformations.transformations import StandardTransformationsApplication


def test_vat_rate_first(mocker, responses):
    responses.add(
        'GET',
        'https://api.apilayer.com/tax_data/rate_list',
        json={
            'data': [
                {
                    'country_code': 'AU',
                    'country_name': 'Australia',
                    'eu': False,
                    'other_rates': [],
                    'standard_rate': {
                        'class': 'standard',
                        'description': '',
                        'rate': 0.1,
                        'types': None,
                    },
                    'success': True,
                },
                {
                    'country_code': 'ES',
                    'country_name': 'Spain',
                    'eu': True,
                    'other_rates': [],
                    'standard_rate': {
                        'class': 'standard',
                        'description': '',
                        'rate': 0.21,
                        'types': None,
                    },
                    'success': True,
                },
                {
                    'country_code': 'AT',
                    'country_name': 'Austria',
                    'eu': True,
                    'other_rates': [
                        {
                            'class': 'reduced',
                            'rate': 0.13,
                        },
                        {
                            'class': 'zero',
                            'rate': 0,
                        },
                    ],
                    'standard_rate': {
                        'class': 'standard',
                        'description': '',
                        'rate': 0.2,
                        'types': None,
                    },
                    'success': True,
                },
            ],
        },
    )
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, {'EXCHANGE_API_KEY': 'ApiKey'})
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'Country',
                'to': 'VAT',
                'action_if_not_found': 'leave_empty',
            },
            'columns': {
                'input': [{'name': 'Country', 'nullable': False}],
            },
        },
    }

    response = app.get_vat_rate(
        {
            'Country': 'ES',
        },
    )
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'VAT': 21,
    }

    response = app.get_vat_rate(
        {
            'Country': 'Austria',
        },
    )
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'VAT': 20,
    }


def test_var_rate(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.eu_vat_rates = {
        'FR': 20,
        'France': 20,
        'ES': 21,
        'Spain': 21,
    }
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'Country',
                'to': 'VAT',
                'action_if_not_found': 'leave_empty',
            },
            'columns': {
                'input': [{'name': 'Country', 'nullable': False}],
            },
        },
    }

    response = app.get_vat_rate(
        {
            'Country': 'ES',
        },
    )
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'VAT': 21,
    }


def test_var_rate_first_http_error(mocker, responses):
    responses.add(
        'GET',
        'https://api.apilayer.com/tax_data/rate_list',
        status=500,
    )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, {'EXCHANGE_API_KEY': 'ApiKey'})
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'Country',
                'to': 'VAT',
                'action_if_not_found': 'leave_empty',
            },
            'columns': {
                'input': [{'name': 'Country', 'nullable': False}],
            },
        },
    }

    response = app.get_vat_rate({'Country': 'ES'})
    assert response.status == ResultType.FAIL
    assert (
        'An error occurred while requesting '
        'https://api.apilayer.com/tax_data/rate_list'
    ) in response.output


def test_var_rate_null_value(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.eu_vat_rates = {'a': 3}
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'Country',
                'to': 'VAT',
                'action_if_not_found': 'leave_empty',
            },
            'columns': {
                'input': [{'name': 'Country', 'nullable': False}],
            },
        },
    }

    response = app.get_vat_rate(
        {
            'Country': None,
        },
    )
    assert response.status == ResultType.SKIP


def test_vat_rate_no_input_column_found(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.eu_vat_rates = {
        'FR': 20,
        'France': 20,
        'ES': 21,
        'Spain': 21,
    }
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'Country',
                'to': 'VAT',
                'action_if_not_found': 'leave_empty',
            },
            'columns': {
                'input': [{'name': 'Other', 'nullable': False}],
            },
        },
    }

    with pytest.raises(BaseTransformationException) as e:
        app.get_vat_rate(
            {
                'Country': None,
            },
        )
        assert str(e.value) == 'The column Country does not exists.'


def test_vat_rate_country_not_found(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.eu_vat_rates = {}
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'Country',
                'to': 'VAT',
                'action_if_not_found': 'fail',
            },
            'columns': {
                'input': [{'name': 'Country', 'nullable': False}],
            },
        },
    }

    response = app.get_vat_rate(
        {
            'Country': 'AN',
        },
    )
    assert response.status == ResultType.FAIL
    assert response.output == 'Country AN not found'
