# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from connect.eaas.core.enums import ResultType

from connect_transformations.transformations import StandardTransformationsApplication


def test_copy_columns_old_version(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': [
                {'from': 'ColumnA', 'to': 'NewColC'},
                {'from': 'ColumnB', 'to': 'NewColD'},
            ],
        },
    }

    response = app.copy_columns(
        {
            'ColumnA': 'ContentColumnA',
            'ColumnB': 'ContentColumnB',
        },
    )

    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'NewColC': 'ContentColumnA',
        'NewColD': 'ContentColumnB',
    }
    assert response.transformed_row_styles == {}


def test_copy_columns(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': [
                {'from': 'ColumnA', 'to': 'NewColC'},
                {'from': 'ColumnB', 'to': 'NewColD'},
            ],
        },
    }

    response = app.copy_columns(
        {
            'ColumnA': 'ContentColumnA',
            'ColumnB': 'ContentColumnB',
        },
        row_styles={
            'ColumnA': 'StyleA',
            'ColumnB': 'StyleB',
        },
    )

    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'NewColC': 'ContentColumnA',
        'NewColD': 'ContentColumnB',
    }
    assert response.transformed_row_styles == {
        'NewColC': 'StyleA',
        'NewColD': 'StyleB',
    }
