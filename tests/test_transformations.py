# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from connect_transformations.transformations import StandardTransformationsApplication


def test_transform_1_copy_row(mocker):
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
    assert app.transform_1_copy_row(
        {
            'ColumnA': 'ContentColumnA',
            'ColumnB': 'ContentColumnB',
        },
    ) == {
        'NewColC': 'ContentColumnA',
        'NewColD': 'ContentColumnB',
    }
