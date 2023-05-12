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
        'https://api.exchangerate.host/vat_rates',
        json={
            'success': True,
            'rates': {
                'FR': {
                    'country_name': 'France',
                    'standard_rate': 20,
                    'reduced_rates': [5.5, 10],
                    'super_reduced_rates': [2.1],
                    'parking_rates': [],
                },
                'ES': {
                    'country_name': 'Spain',
                    'standard_rate': 21,
                    'reduced_rates': [10],
                    'super_reduced_rates': [4],
                    'parking_rates': [],
                },
            },
        },
    )
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
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
            'Country': 'FR',
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
        'https://api.exchangerate.host/vat_rates',
        status=500,
    )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
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
        'https://api.exchangerate.host/vat_rates'
    ) in response.output


def test_var_rate_first_unexpected_response(mocker, responses):
    responses.add(
        'GET',
        'https://api.exchangerate.host/vat_rates',
        json={
            'success': False,
            'result': None,
        },
    )
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
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
        'Unexpected response calling '
        'https://api.exchangerate.host/vat_rates'
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
