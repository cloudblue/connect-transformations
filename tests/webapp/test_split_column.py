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
