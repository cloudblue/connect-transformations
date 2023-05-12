# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from connect.eaas.core.enums import ResultType
from responses import matchers

from connect_transformations.transformations import StandardTransformationsApplication


def test_airtable_lookup(mocker, responses):
    responses.add(
        'GET',
        'https://api.airtable.com/v0/base_id/table_id',
        json={
            'records': [
                {
                    'id': 'some_id',
                    'createdTime': '2023-01-01T00:0:00.000Z',
                    'fields': {
                        'customer_id': '1',
                        'first name': 'First Name',
                        'last name': 'Last Name',
                    },
                },
            ],
            'offset': 'second_page_offset',
        },
    )

    params = {'offset': 'second_page_offset'}

    responses.add(
        'GET',
        'https://api.airtable.com/v0/base_id/table_id',
        match=[matchers.query_param_matcher(params)],
        json={
            'records': [
                {
                    'id': 'some_id',
                    'createdTime': '2023-01-01T00:0:00.000Z',
                    'fields': {
                        'customer_id': '2',
                        'first name': 'First Name 2',
                        'last name': 'Last Name 2',
                    },
                },
            ],
        },
    )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
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
                        'from': 'first name',
                        'to': 'Customer first name',
                    },
                    {
                        'from': 'last name',
                        'to': 'Customer last name',
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'id', 'nullable': False},
                ],
            },
        },
    }

    response = app.airtable_lookup({'id': '1'})
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'Customer first name': 'First Name',
        'Customer last name': 'Last Name',
    }


def test_airtable_lookup_skip_nullable(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.airtable_data = {'a': 'b'}
    app.transformation_request = {
        'transformation': {
            'settings': {
                'api_key': 'token',
                'base_id': 'base_id',
                'table_id': 'table_id',
                'map_by': {
                    'input_column': 'purchase_id',
                    'airtable_column': 'id',
                },
                'mapping': [
                    {
                        'from': 'created',
                        'to': 'Purchase date',
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'purchase_id', 'nullable': True},
                ],
            },
        },
    }

    response = app.airtable_lookup({'purchase_id': None})
    assert response.status == ResultType.SKIP


def test_airtable_lookup_no_matching_value(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.airtable_data = {'a': 'b'}
    app.transformation_request = {
        'transformation': {
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
                        'from': 'first_name',
                        'to': 'Customer first name',
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'id', 'nullable': False},
                ],
            },
        },
    }

    response = app.airtable_lookup({'id': 1})
    assert response.status == ResultType.SKIP


def test_airtable_lookup_airtable_api_error(mocker, responses):
    responses.add(
        'GET',
        'https://api.airtable.com/v0/base_id/table_id',
        status=400,
    )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
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
                        'from': 'first_name',
                        'to': 'First name',
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'id', 'nullable': False},
                ],
            },
        },
    }

    response = app.airtable_lookup({'id': 1})
    assert response.status == ResultType.FAIL
    assert '400 Client Error' in response.output
