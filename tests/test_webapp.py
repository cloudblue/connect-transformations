# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest
from connect.client.testing import get_httpx_mocker

from connect_transformations.constants import SUBSCRIPTION_LOOKUP
from connect_transformations.webapp import TransformationsWebApplication


def test_validate_copy_columns(test_client_factory):
    data = {
        'settings': [
            {
                'from': 'columnInput1',
                'to': 'newColumn1',
            },
            {
                'from': 'columnInput2',
                'to': 'newColumn2',
            },
        ],
        'columns': {
            'input': [
                {'name': 'columnInput1'},
                {'name': 'columnInput2'},
            ],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)

    response = client.post('/api/validate/copy_columns', json=data)
    assert response.status_code == 200

    data = response.json()
    assert data == {
        'overview': 'columnInput1  -->  newColumn1\ncolumnInput2  -->  newColumn2\n',
    }


@pytest.mark.parametrize(
    'data',
    (
        {},
        {'settings': {}},
        {'settings': []},
        {'settings': [], 'columns': {}},
    ),
)
def test_validate_copy_columns_missing_settings_or_invalid(test_client_factory, data):

    client = test_client_factory(TransformationsWebApplication)

    response = client.post('/api/validate/copy_columns', json=data)
    assert response.status_code == 400
    assert response.json() == {'error': 'Invalid input data'}


def test_validate_copy_columns_invalid_settings(test_client_factory):
    data = {'settings': [{'x': 'y'}], 'columns': {'input': []}}

    client = test_client_factory(TransformationsWebApplication)

    response = client.post('/api/validate/copy_columns', json=data)
    assert response.status_code == 400
    assert response.json() == {'error': 'Invalid settings format'}


def test_validate_copy_columns_invalid_from(test_client_factory):
    data = {'settings': [{'from': 'Hola', 'to': 'Hola2'}], 'columns': {'input': [{'name': 'Gola'}]}}

    client = test_client_factory(TransformationsWebApplication)

    response = client.post('/api/validate/copy_columns', json=data)
    assert response.status_code == 400
    assert response.json() == {'error': 'The input column Hola does not exists'}


@pytest.mark.parametrize(
    'data',
    (
        {
            'settings': [
                {'from': 'A', 'to': 'C'},
                {'from': 'B', 'to': 'C'},
            ],
            'columns': {
                'input': [
                    {'name': 'A'},
                    {'name': 'B'},
                ],
            },
        },
        {
            'settings': [
                {'from': 'A', 'to': 'C'},
            ],
            'columns': {
                'input': [
                    {'name': 'A'},
                    {'name': 'C'},
                ],
            },
        },
    ),
)
def test_validate_copy_columns_not_unique_name(test_client_factory, data):
    client = test_client_factory(TransformationsWebApplication)

    response = client.post('/api/validate/copy_columns', json=data)
    assert response.status_code == 400
    assert response.json() == {
        'error': 'Invalid column name C. The to field should be unique',
    }


def test_validate_lookup_subscription(test_client_factory):
    data = {
        'settings': {
            'lookup_type': 'id',
            'from': 'column',
            'prefix': 'PREFIX',
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/lookup_subscription', json=data)

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'overview': 'Criteria = "id"\nInput Column = "column"\nPrefix = "PREFIX"\n',
    }


@pytest.mark.parametrize(
    'data',
    (
        {},
        {'settings': []},
        {'settings': [], 'columns': {}},
    ),
)
def test_validate_lookup_subscription_settings_or_invalid(test_client_factory, data):
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/lookup_subscription', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'Invalid input data',
    }


@pytest.mark.parametrize(
    'settings',
    (
        {},
        {'from': 'x'},
        {'from': 'x', 'prefix': ''},
        {'lookup_type': 'x', 'prefix': ''},
    ),
)
def test_validate_lookup_subscription_invalid_format(test_client_factory, settings):
    data = {'settings': settings, 'columns': {'input': []}}
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/lookup_subscription', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'The settings must have `lookup_type`, `from` and `prefix` fields',
    }


@pytest.mark.parametrize(
    'lookup_type',
    (
        'invalidtype',
        '',
    ),
)
def test_validate_lookup_subscription_invalid_lookup_type(test_client_factory, lookup_type):
    data = {
        'settings': {
            'lookup_type': lookup_type,
            'from': 'column',
            'prefix': 'PREFIX',
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/lookup_subscription', json=data)

    assert response.status_code == 400
    data = response.json()
    values = SUBSCRIPTION_LOOKUP.keys()
    assert data == {
        'error': f'The settings `lookup_type` allowed values {values}',
    }


@pytest.mark.parametrize(
    'lookup_type',
    (
        'invalidtype',
        '',
    ),
)
def test_validate_lookup_subscription_invalid_column(test_client_factory, lookup_type):
    data = {
        'settings': {
            'lookup_type': 'id',
            'from': 'column',
            'prefix': 'PREFIX',
        },
        'columns': {
            'input': [
                {'name': 'otherColumn'},
            ],
            'output': [],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/lookup_subscription', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings `from` contains an invalid column name column that does not exist'
            ' on columns.input'
        ),
    }


def test_validate_lookup_subscription_invalid_prefix(test_client_factory):
    data = {
        'settings': {
            'lookup_type': 'id',
            'from': 'column',
            'prefix': '12345678901',
        },
        'columns': {
            'input': [{'name': 'column'}],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/lookup_subscription', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'The settings `prefix` max length is 10',
    }


def test_get_subscription_criteria(test_client_factory):
    data = {
        'settings': {
            'lookup_type': 'id',
            'from': 'column',
            'prefix': 'PREFIX',
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.get('/api/lookup_subscription/criteria')

    assert response.status_code == 200
    data = response.json()
    assert data == SUBSCRIPTION_LOOKUP


def test_validate_currency_conversion(test_client_factory):
    data = {
        'settings': {
            'from': {'column': 'column', 'currency': 'USD'},
            'to': {'column': 'result', 'currency': 'EUR'},
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/currency_conversion', json=data)

    assert response.status_code == 200
    data = response.json()

    assert data == {
        'overview': (
            'From Currency = USD\n'
            'To Currency = EUR\n'
        ),
    }


@pytest.mark.parametrize(
    'data',
    (
        {},
        {'settings': []},
        {'settings': {}},
        {'settings': {}, 'columns': {}},
    ),
)
def test_validate_currency_conversion_settings_or_invalid(test_client_factory, data):
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/currency_conversion', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'Invalid input data',
    }


@pytest.mark.parametrize(
    'settings',
    (
        {'from': {'column': 'x'}},
        {'from': {'column': 'x', 'currency': ''}},
        {'from': {'column': 'x', 'currency': ''}, 'to': {'column': 'y'}},
        {'from': {'column': 'x', 'currency': ''}, 'to': {'currency': 'y'}},
    ),
)
def test_validate_currency_conversion_invalid_format(test_client_factory, settings):
    data = {'settings': settings, 'columns': {'input': []}}
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/currency_conversion', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings must have `from` with the `column` and the `currency`, and '
            '`to` with the `column` and `currency` fields'
        ),
    }


def test_validate_currency_conversion_invalid_column(test_client_factory):
    data = {
        'settings': {
            'from': {'column': 'column', 'currency': 'USD'},
            'to': {'column': 'columnB', 'currency': 'EUR'},
        },
        'columns': {
            'input': [
                {'name': 'otherColumn'},
            ],
            'output': [],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/currency_conversion', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings contains an invalid `from` column name "column" that does not exist on'
            ' columns.input'
        ),
    }


def test_get_available_rates(
    test_client_factory,
):
    httpx_mock = get_httpx_mocker()
    httpx_mock.add_response(
        method='GET',
        url='https://api.exchangerate.host/symbols',
        json={
            'symbols': {
                'EUR': {'code': 'EUR', 'description': 'Euro'},
                'USD': {'code': 'USD', 'description': "United States Dollar's"},
            },
            'success': True,
        },
    )
    client = test_client_factory(TransformationsWebApplication)
    response = client.get('/api/currency_conversion/currencies')

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'EUR': 'Euro',
        'USD': "United States Dollar's",
    }


def test_get_available_rates_invalid_response(
    test_client_factory,
):
    httpx_mock = get_httpx_mocker()
    httpx_mock.add_response(
        method='GET',
        url='https://api.exchangerate.host/symbols',
        json={
            'symbols': {},
            'success': False,
        },
    )
    client = test_client_factory(TransformationsWebApplication)
    response = client.get('/api/currency_conversion/currencies')

    assert response.status_code == 200
    data = response.json()
    assert data == {}


def test_get_available_rates_invalid_status_code(
    test_client_factory,
):
    httpx_mock = get_httpx_mocker()
    httpx_mock.add_response(
        method='GET',
        url='https://api.exchangerate.host/symbols',
        status_code=400,
    )
    client = test_client_factory(TransformationsWebApplication)
    response = client.get('/api/currency_conversion/currencies')

    assert response.status_code == 200
    data = response.json()
    assert data == {}


def test_get_available_rates_code_exception(
    test_client_factory,
    mocker,
):
    mocker.patch(
        'connect_transformations.currency_conversion.mixins.httpx.AsyncClient',
        side_effect=Exception(),
    )

    client = test_client_factory(TransformationsWebApplication)
    response = client.get('/api/currency_conversion/currencies')

    assert response.status_code == 200
    data = response.json()
    assert data == {}


def test_validate_split_column(test_client_factory):
    data = {
        'settings': {
            'from': 'column',
            'regex': {
                'pattern': '(?P<first_name>\\w+) (?P<last_name>\\w+)',
                'groups': [{'first_name': 'First Name'}, {'last_name': 'Last Name'}],
            },
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/split_column', json=data)
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data == {
        'overview': "Regexp = '(?P<first_name>\\w+) (?P<last_name>\\w+)'",
    }


@pytest.mark.parametrize(
    'data',
    (
        {},
        {'settings': []},
        {'settings': {}},
        {'settings': {}, 'columns': {}},
    ),
)
def test_validate_split_column_settings_or_invalid(test_client_factory, data):
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/split_column', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'Invalid input data',
    }


@pytest.mark.parametrize(
    'settings',
    (
        {'from': 'column'},
        {'from': 'column', 'regex': {'pattern': '(?P<first_name>\\w+) (?P<last_name>\\w+)'}},
        {
            'from': 'column',
            'regex': {
                'pattern': '(?P<first_name>\\w+) (?P<last_name>\\w+)',
                'groups': {},
            },
        },
    ),
)
def test_validate_split_column_invalid_format(test_client_factory, settings):
    data = {'settings': settings, 'columns': {'input': []}}
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/split_column', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings must have `from` and `regex` with `pattern` and `groups` '
            'fields'
        ),
    }


def test_validate_split_column_invalid_column(test_client_factory):
    data = {
        'settings': {
            'from': 'column',
            'regex': {
                'pattern': '(?P<first_name>\\w+) (?P<last_name>\\w+)',
                'groups': [{'first_name': 'First Name'}, {'last_name': 'Last Name'}],
            },
        },
        'columns': {
            'input': [
                {'name': 'otherColumn'},
            ],
            'output': [],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/split_column', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings contains an invalid `from` column name "column" that does not exist on'
            ' columns.input'
        ),
    }


def test_validate_split_column_invalid_to_field(test_client_factory):
    data = {
        'settings': {
            'from': 'column',
            'regex': {
                'pattern': '(?P<first_name>\\w+) (?P<last_name>\\w+)',
                'groups': [{'first_name': 'First Name'}, {'name': 'Name'}],
            },
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/split_column', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings `groups` contains a group name <name> that does not exists '
            'on `pattern` regular expression (?P<first_name>\\w+) (?P<last_name>\\w+)'
        ),
    }


def test_validate_split_column_invalid_regex(test_client_factory):
    data = {
        'settings': {
            'from': 'column',
            'regex': {
                'pattern': '(?P<first name>\\w+) (?P<last name>\\w+)',
                'groups': [{'first name': 'First Name'}, {'last name': 'Last Name'}],
            },
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/split_column', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings contains an invalid `regex` regular expression '
            '(?P<first name>\\w+) (?P<last name>\\w+)'
        ),
    }


def test_groups(
    test_client_factory,
):
    client = test_client_factory(TransformationsWebApplication)
    response = client.post(
        '/api/split_column/extract_groups',
        json={'pattern': '(?P<first_name>\\w+) (?P<last_name>\\w+)'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'groups': [{'first_name': 'first_name'}, {'last_name': 'last_name'}],
    }


def test_groups_merge(
    test_client_factory,
):
    client = test_client_factory(TransformationsWebApplication)
    response = client.post(
        '/api/split_column/extract_groups',
        json={
            'pattern': '(?P<first_name>\\w+) (?P<last_name>\\w+)',
            'groups': [{'first_name': 'First Name'}],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'groups': [{'first_name': 'First Name'}, {'last_name': 'last_name'}],
    }


def test_groups_merge_invalid_groups(
    test_client_factory,
):
    client = test_client_factory(TransformationsWebApplication)
    response = client.post(
        '/api/split_column/extract_groups',
        json={
            'pattern': '(?P<first_name>\\w+) (?P<last_name>\\w+)',
            'groups': 'hello',
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'The `groups` key must be a valid list',
    }


def test_groups_invalid_data(
    test_client_factory,
):
    client = test_client_factory(TransformationsWebApplication)
    response = client.post(
        '/api/split_column/extract_groups',
        json={},
    )

    print(response.json())
    assert response.status_code == 400
    assert response.json() == {
        'error': 'The body does not contain `pattern` key',
    }


def test_groups_invalid_pattern(
    test_client_factory,
):
    client = test_client_factory(TransformationsWebApplication)
    response = client.post(
        '/api/split_column/extract_groups',
        json={'pattern': '(?P<first name>\\w+) (?P<last name>\\w+)'},
    )

    assert response.status_code == 400
    assert response.json() == {
        'error': 'Invalid regular expression',
    }


def test_validate_formula(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': [
                {
                    'to': 'Price with Tax',
                    'formula': '.(Price without Tax) + .(Tax)',
                },
                {
                    'to': 'Tax value',
                    'formula': '.(Tax) / .(Price without Tax)',
                },
            ],
        },
        'columns': {
            'input': [
                {'name': 'Price without Tax', 'nullable': False},
                {'name': 'Tax', 'nullable': False},
            ],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/formula', json=data)

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'overview': (
            "Output column = Price with Tax, Formula = .(Price without Tax) + .(Tax)\n"
            "Output column = Tax value, Formula = .(Tax) / .(Price without Tax)\n"
        ),
    }


def test_validate_formula_invalid_input(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': [
                {
                    'to': 'Price with Tax',
                    'formula': '.(Price without Tax) + .(Tax)',
                },
            ],
        },
        'columns': {},
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/formula', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'Invalid input data.',
    }


def test_validate_formula_invalid_expression_field(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': {
                'to': 'Price with Tax',
                'formula': '.(Price without Tax) + .(Tax)',
            },
        },
        'columns': {
            'input': [
                {'name': 'Price without Tax', 'nullable': False},
                {'name': 'Tax', 'nullable': False},
            ],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/formula', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'The settings must have `expressions` field which contains list of formulas.',
    }


def test_validate_formula_invalid_expression(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': [
                {'formula': '.(Price without Tax) + .(Tax)'},
            ],
        },
        'columns': {
            'input': [
                {'name': 'Price without Tax', 'nullable': False},
                {'name': 'Tax', 'nullable': False},
            ],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/formula', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'Each expression must have `to` and `formula` fields.',
    }


def test_validate_formula_unique_error(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': [
                {
                    'to': 'Price',
                    'formula': '.(Price) + .(Tax)',
                },
            ],
        },
        'columns': {
            'input': [
                {'name': 'Price', 'nullable': False},
                {'name': 'Tax', 'nullable': False},
            ],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/formula', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'Each `output column` must be unique.',
    }


def test_validate_formula_non_existing_column(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': [
                {
                    'to': 'Price with Tax',
                    'formula': '.(Price) + .(Tax)',
                },
            ],
        },
        'columns': {
            'input': [
                {'name': 'Price without Tax', 'nullable': False},
                {'name': 'Tax', 'nullable': False},
            ],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/formula', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'Settings contains formula `.(Price) + .(Tax)` '
            'with column that does not exist on columns.input.'
        ),
    }


def test_validate_formula_invalid_formula(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': [
                {
                    'to': 'Price with Tax',
                    'formula': '.Price with Tax + .(Tax)',
                },
            ],
        },
        'columns': {
            'input': [
                {'name': 'Price without Tax', 'nullable': False},
                {'name': 'Tax', 'nullable': False},
            ],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/formula', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'Settings contains invalid formula `.Price with Tax + .(Tax)`.',
    }
