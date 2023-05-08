# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from connect.eaas.core.enums import ResultType
from connect.eaas.core.responses import RowTransformationResponse

from connect_transformations.transformations import StandardTransformationsApplication


def test_filter_row_old_settings(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'ColumnA',
                'value': 'matchvalue',
            },
        },
    }

    response = app.filter_row(
        {
            'ColumnA': 'matchvalue',
        },
    )
    assert isinstance(response, RowTransformationResponse)
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {'ColumnA': None}

    response = app.filter_row(
        {
            'ColumnA': 'some_value',
        },
    )
    assert isinstance(response, RowTransformationResponse)
    assert response.status == ResultType.DELETE
    assert response.transformed_row is None


def test_filter_row_new_settings(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'ColumnA',
                'value': 'matchvalue',
                'match_condition': True,
                'additional_values': [],
            },
        },
    }

    response = app.filter_row(
        {
            'ColumnA': 'matchvalue',
        },
    )

    assert isinstance(response, RowTransformationResponse)
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {'ColumnA': None}


def test_filter_row_new_settings_complex(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'ColumnA',
                'value': 'some_value',
                'match_condition': False,
                'additional_values': [{
                    'operation': 'and',
                    'value': 'another_value',
                }],
            },
        },
    }

    response = app.filter_row({'ColumnA': 'matchvalue'})
    assert isinstance(response, RowTransformationResponse)
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {'ColumnA': None}

    response = app.filter_row({'ColumnA': 'some_value'})
    assert isinstance(response, RowTransformationResponse)
    assert response.status == ResultType.DELETE
    assert response.transformed_row is None
