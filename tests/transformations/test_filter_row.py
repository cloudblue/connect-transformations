# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from connect.eaas.core.enums import ResultType
from connect.eaas.core.responses import RowTransformationResponse

from connect_transformations.transformations import StandardTransformationsApplication


def test_filter_row(mocker):
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


def test_filter_row_delete(mocker):
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
            'ColumnA': 'othermatchvalue',
        },
    )

    assert isinstance(response, RowTransformationResponse)
    assert response.status == ResultType.DELETE
    assert response.transformed_row is None
