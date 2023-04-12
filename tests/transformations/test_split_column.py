# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest

from connect_transformations.transformations import StandardTransformationsApplication


@pytest.mark.asyncio
async def test_split_column(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'column',
                'regex': {
                    'pattern': r'(\w+) (?P<first_name>\w+) (?P<last_name>\w+)',
                    'groups': {
                        '1': 'group_1',
                        '2': 'First Name',
                        '3': 'Last Name',
                    },
                },
            },
        },
    }
    assert await app.split_column({
        'column': 'X Name Surname',
    }) == {
        'group_1': 'X',
        'First Name': 'Name',
        'Last Name': 'Surname',
    }


@pytest.mark.asyncio
async def test_split_column_not_match_regex(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'column',
                'regex': {
                    'pattern': '(\\w+) (?P<first_name>\\w+) (?P<last_name>\\w+)',
                    'groups': {
                        '1': 'group_1',
                        '2': 'First Name',
                        '3': 'Last Name',
                    },
                },
            },
        },
    }
    assert await app.split_column({
        'column': 'Name Surname',
    }) == {
        'First Name': None,
        'Last Name': None,
        'group_1': None,
    }


@pytest.mark.asyncio
async def test_split_column_match_partially(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'column',
                'regex': {
                    'pattern': '(?P<first_name>\\w+) (?P<last_name>\\w+)',
                    'groups': {
                        '1': 'First Name',
                        '2': 'Last Name',
                    },
                },
            },
        },
    }
    assert await app.split_column({
        'column': 'Name Surname Othername',
    }) == {
        'First Name': 'Name',
        'Last Name': 'Surname',
    }


@pytest.mark.asyncio
async def test_split_column_match_optional(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'column',
                'regex': {
                    'pattern': '(?P<first_name>\\w+) (?:(?P<last_name>\\w+))?',
                    'groups': {
                        '1': 'First Name',
                        '2': 'Last Name',
                    },
                },
            },
        },
    }
    assert await app.split_column({
        'column': 'Name ',
    }) == {
        'First Name': 'Name',
        'Last Name': None,
    }
