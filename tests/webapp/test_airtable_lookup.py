# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#

from connect_transformations.webapp import TransformationsWebApplication


def test_get_bases(test_client_factory, httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://api.airtable.com/v0/meta/bases',
        json={
            'bases': [
                {'id': '1', 'name': 'First base', 'permissionLevel': 'create'},
                {'id': '2', 'name': 'Second base', 'permissionLevel': 'create'},
            ],
        },
    )

    client = test_client_factory(TransformationsWebApplication)
    response = client.get('/api/airtable_lookup/bases?api_key=token')

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert {'id': '1', 'name': 'First base'} in data
    assert {'id': '2', 'name': 'Second base'} in data


def test_get_bases_airtable_api_error(test_client_factory, httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://api.airtable.com/v0/meta/bases',
        status_code=400,
    )

    client = test_client_factory(TransformationsWebApplication)
    response = client.get('/api/airtable_lookup/bases?api_key=token')

    assert response.status_code == 400
    data = response.json()
    assert data['error'] == 'Error calling `meta/bases`'


def test_get_tables(test_client_factory, httpx_mock):
    columns_1 = [
        {'type': 'number', 'options': {'precision': 0}, 'id': 'f1_1', 'name': 'id'},
        {'type': 'number', 'options': {'precision': 2}, 'id': 'f1_2', 'name': 'price'},
        {'type': 'multilineText', 'id': 'f1_3', 'name': 'sub_id'},
        {'type': 'singleLineText', 'id': 'f1_4', 'name': 'delivered'},
        {
            'type': 'dateTime',
            'options': {
                'dateFormat': {'name': 'iso', 'format': 'YYYY-MM-DD'},
                'timeFormat': {'name': '24hour', 'format': 'HH:mm'},
                'timeZone': 'client',
            },
            'id': 'f1_5',
            'name': 'purchase_time',
        },
    ]
    columns_2 = [
        {'type': 'singleLineText', 'id': 'f2_1', 'name': 'id'},
        {'type': 'singleLineText', 'id': 'f2_2', 'name': 'name'},
    ]

    httpx_mock.add_response(
        method='GET',
        url='https://api.airtable.com/v0/meta/bases/base_id/tables',
        json={
            'tables': [
                {
                    'id': '1',
                    'name': 'Data',
                    'primaryFieldId': 'some_key_1',
                    'fields': columns_1,
                    'views': [{'id': 'view_id', 'name': 'Grid view', 'type': 'grid'}]},
                {
                    'id': '2',
                    'name': 'Customers',
                    'primaryFieldId': 'some_key_2',
                    'fields': columns_2,
                    'views': [{'id': 'view_id', 'name': 'Grid view', 'type': 'grid'}],
                },
            ],
        },
    )

    client = test_client_factory(TransformationsWebApplication)
    response = client.get('/api/airtable_lookup/tables?api_key=token&base_id=base_id')

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert {
        'id': '1',
        'name': 'Data',
        'columns': columns_1,
    } in data
    assert {
        'id': '2',
        'name': 'Customers',
        'columns': columns_2,
    } in data


def test_get_tables_airtable_api_error(test_client_factory, httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://api.airtable.com/v0/meta/bases/base_id/tables',
        status_code=500,
    )

    client = test_client_factory(TransformationsWebApplication)
    response = client.get('/api/airtable_lookup/tables?api_key=token&base_id=base_id')

    assert response.status_code == 400
    data = response.json()
    assert data['error'] == 'Error calling `meta/bases/base_id/tables`'


def test_validate_airtable_lookup(test_client_factory):
    data = {
        'settings': {
            'api_key': 'token',
            'base_id': 'base_id',
            'table_id': 'table_id',
            'map_by': {
                'input_column': 'id',
                'airtable_column': 'customer_id',
            },
            'mapping': [
                {
                    'from': 'sub_id',
                    'to': 'Subscription',
                },
                {
                    'from': 'purchase_time',
                    'to': 'Purchase time',
                },
            ],
        },
        'columns': {
            'input': [
                {'name': 'id'},
            ],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/airtable_lookup', json=data)

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'overview': (
            'Match column "id" with AirTable field "customer_id" '
            'and populate 2 columns with the matching data.'
        ),
    }


def test_validate_airtable_lookup_invalid_data(test_client_factory):
    data = {
        'settings': {
            'api_key': 'token',
            'base_id': 'base_id',
            'table_id': 'table_id',
            'map_by': {
                'input_column': 'id',
                'airtable_column': 'customer_id',
            },
            'mapping': [
                {
                    'from': 'sub_id',
                    'to': 'Subscription',
                },
                {
                    'from': 'purchase_time',
                    'to': 'Purchase time',
                },
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/airtable_lookup', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data['error'] == 'Invalid input data'


def test_validate_airtable_lookup_invalid_settings(test_client_factory):
    data = {
        'settings': {
            'base_id': 'base_id',
            'table_id': 'table_id',
            'map_by': {
                'input_column': 'id',
                'airtable_column': 'customer_id',
            },
            'mapping': [
                {
                    'from': 'sub_id',
                    'to': 'Subscription',
                },
                {
                    'from': 'purchase_time',
                    'to': 'Purchase time',
                },
            ],
        },
        'columns': {
            'input': [{'name': 'id'}],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/airtable_lookup', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data['error'] == (
        'The settings must contain `api_key`, `base_id`, `table_id` '
        'fields, dictionary `map_by` and list `mapping` fields.'
    )


def test_validate_airtable_lookup_invalid_map_by(test_client_factory):
    data = {
        'settings': {
            'api_key': 'token',
            'base_id': 'base_id',
            'table_id': 'table_id',
            'map_by': {
                'from': 'id',
                'to': 'customer_id',
            },
            'mapping': [
                {
                    'from': 'sub_id',
                    'to': 'Subscription',
                },
                {
                    'from': 'purchase_time',
                    'to': 'Purchase time',
                },
            ],
        },
        'columns': {
            'input': [{'name': 'id'}],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/airtable_lookup', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data['error'] == (
        'The settings field `map_by` must contain '
        '`input_column` and `airtable_column` fields in it.'
    )


def test_validate_airtable_lookup_invalid_mapping(test_client_factory):
    data = {
        'settings': {
            'api_key': 'token',
            'base_id': 'base_id',
            'table_id': 'table_id',
            'map_by': {
                'input_column': 'id',
                'airtable_column': 'customer_id',
            },
            'mapping': [
                {
                    'input_column': 'sub_id',
                    'output_column': 'Subscription',
                },
            ],
        },
        'columns': {
            'input': [{'name': 'id'}],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/airtable_lookup', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data['error'] == (
        'Each element of the settings `mapping` must contain '
        '`from` and `to` fields in it.'
    )


def test_validate_airtable_lookup_not_existed_input_column(test_client_factory):
    data = {
        'settings': {
            'api_key': 'token',
            'base_id': 'base_id',
            'table_id': 'table_id',
            'map_by': {
                'input_column': 'idd',
                'airtable_column': 'customer_id',
            },
            'mapping': [
                {
                    'input_column': 'sub_id',
                    'output_column': 'Subscription',
                },
            ],
        },
        'columns': {
            'input': [{'name': 'id'}],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/airtable_lookup', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data['error'] == (
        'The settings contains invalid input column that '
        'does not exist on columns.input'
    )
