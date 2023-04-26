# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest

from connect_transformations.webapp import TransformationsWebApplication


def test_validate_split_column(test_client_factory):
    data = {
        'settings': {
            'from': 'column',
            'regex': {
                'pattern': '(?P<first_name>\\w+) (?P<last_name>\\w+)',
                'groups': {1: 'First Name', 2: 'last name'},
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
                'groups': [],
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
                'groups': {'1': 'First Name', '2': 'last name'},
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


def test_validate_split_column_invalid_regex(test_client_factory):
    data = {
        'settings': {
            'from': 'column',
            'regex': {
                'pattern': '(?P<first name>\\w+) (?P<last name>\\w+)',
                'groups': {'1': 'First Name', '2': 'last name'},
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


def test_validate_split_column_invalid_group_amount(test_client_factory):
    data = {
        'settings': {
            'from': 'column',
            'regex': {
                'pattern': r'(\w+) (?P<first_name>\w+) (?P<last_name>\w+)',
                'groups': {'1': 'First Name', '2': 'last name'},
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
            'The settings `groups` contains a different number of elements that are defined in the '
            r'regular expression (\w+) (?P<first_name>\w+) (?P<last_name>\w+)'
        ),
    }


def test_groups(
    test_client_factory,
):
    client = test_client_factory(TransformationsWebApplication)
    response = client.post(
        '/api/split_column/extract_groups',
        json={'pattern': '(?P<first_name>\\w+) (?P<last_name>\\w+) (\\w+)'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'groups': {
            '1': {'name': 'first_name', 'type': 'string'},
            '2': {'name': 'last_name', 'type': 'string'},
            '3': {'name': 'group_3', 'type': 'string'},
        },
    }


def test_groups_merge(
    test_client_factory,
):
    client = test_client_factory(TransformationsWebApplication)
    response = client.post(
        '/api/split_column/extract_groups',
        json={
            'pattern': '(?P<first_name>\\w+)',
        },
    )
    assert response.status_code == 200
    data = response.json()
    groups = data.get('groups')
    groups['1']['name'] = 'Is First Name'
    groups['1']['type'] = 'boolean'

    response = client.post(
        '/api/split_column/extract_groups',
        json={
            'pattern': r'(\w+) (?P<first_name>\\w+) (?P<last_name>\\w+)',
            'groups': groups,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'groups': {
            '1': {'name': 'Is First Name', 'type': 'boolean'},
            '2': {'name': 'first_name', 'type': 'string'},
            '3': {'name': 'last_name', 'type': 'string'},
        },
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
        'error': 'The `groups` key must be a valid dict',
    }


def test_groups_invalid_data(
    test_client_factory,
):
    client = test_client_factory(TransformationsWebApplication)
    response = client.post(
        '/api/split_column/extract_groups',
        json={},
    )

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
