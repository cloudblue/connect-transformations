# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import asyncio

import httpx
import pytest
from connect.eaas.core.enums import ResultType

from connect_transformations.exceptions import BaseTransformationException
from connect_transformations.transformations import StandardTransformationsApplication


@pytest.mark.asyncio
async def test_vat_rate_first(mocker, httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://api.exchangerate.host/vat_rates',
        json={
            'success': True,
            'rates': {
                'FR': {
                    'country_name': 'France',
                    'standard_rate': 20,
                    'reduced_rates': [5.5, 10],
                    'super_reduced_rates': [2.1],
                    'parking_rates': [],
                },
                'ES': {
                    'country_name': 'Spain',
                    'standard_rate': 21,
                    'reduced_rates': [10],
                    'super_reduced_rates': [4],
                    'parking_rates': [],
                },
            },
        },
    )
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'Country',
                'to': 'VAT',
                'action_if_not_found': 'leave_empty',
            },
            'columns': {
                'input': [{'name': 'Country', 'nullable': False}],
            },
        },
    }

    response = await app.get_vat_rate(
        {
            'Country': 'ES',
        },
    )
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'VAT': 21,
    }

    response = await app.get_vat_rate(
        {
            'Country': 'FR',
        },
    )
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'VAT': 20,
    }


@pytest.mark.asyncio
async def test_var_rate_first_with_multitask(mocker, httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://api.exchangerate.host/vat_rates',
        json={
            'success': True,
            'rates': {
                'ES': {
                    'country_name': 'Spain',
                    'standard_rate': 21,
                    'reduced_rates': [10],
                    'super_reduced_rates': [4],
                    'parking_rates': [],
                },
            },
        },
    )
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'Country',
                'to': 'VAT',
                'action_if_not_found': 'leave_empty',
            },
            'columns': {
                'input': [{'name': 'Country', 'nullable': False}],
            },
        },
    }

    tasks = []
    for _ in range(10):
        task = asyncio.create_task(
            app.get_vat_rate(
                {
                    'Country': 'ES',
                },
            ),
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    for result in results:
        assert result.status == ResultType.SUCCESS
        assert result.transformed_row == {
            'VAT': 21,
        }
    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.asyncio
async def test_var_rate(mocker):
    mocked_client = mocker.patch(
        'connect_transformations.vat_rate.mixins.httpx.Client',
    )
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.current_vat_rate = {
        'FR': 20,
        'France': 20,
        'ES': 21,
        'Spain': 21,
    }
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'Country',
                'to': 'VAT',
                'action_if_not_found': 'leave_empty',
            },
            'columns': {
                'input': [{'name': 'Country', 'nullable': False}],
            },
        },
    }

    response = await app.get_vat_rate(
        {
            'Country': 'ES',
        },
    )
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'VAT': 21,
    }
    assert mocked_client.call_count == 0


@pytest.mark.asyncio
async def test_var_rate_first_http_error(mocker):
    mocker.patch(
        'connect_transformations.vat_rate.mixins.httpx.Client',
        side_effect=httpx.RequestError('error'),
    )
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'Country',
                'to': 'VAT',
                'action_if_not_found': 'leave_empty',
            },
            'columns': {
                'input': [{'name': 'Country', 'nullable': False}],
            },
        },
    }

    response = await app.get_vat_rate({'Country': 'ES'})
    assert response.status == ResultType.FAIL
    assert (
        'An error occurred while requesting '
        'https://api.exchangerate.host/vat_rates: error'
    ) in response.output


@pytest.mark.asyncio
async def test_var_rate_first_unexpected_response(mocker, httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://api.exchangerate.host/vat_rates',
        json={
            'success': False,
            'result': None,
        },
    )
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'Country',
                'to': 'VAT',
                'action_if_not_found': 'leave_empty',
            },
            'columns': {
                'input': [{'name': 'Country', 'nullable': False}],
            },
        },
    }

    response = await app.get_vat_rate({'Country': 'ES'})
    assert response.status == ResultType.FAIL
    assert (
        'Unexpected response calling '
        'https://api.exchangerate.host/vat_rates'
    ) in response.output


@pytest.mark.asyncio
async def test_var_rate_first_400_response(mocker, httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://api.exchangerate.host/vat_rates',
        status_code=400,
        json={},
    )
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'Country',
                'to': 'VAT',
                'action_if_not_found': 'leave_empty',
            },
            'columns': {
                'input': [{'name': 'Country', 'nullable': False}],
            },
        },
    }

    response = await app.get_vat_rate({'Country': 'ES'})
    assert response.status == ResultType.FAIL
    assert (
        'Unexpected response calling '
        'https://api.exchangerate.host/vat_rates'
    ) in response.output


@pytest.mark.asyncio
async def test_var_rate_null_value(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'Country',
                'to': 'VAT',
                'action_if_not_found': 'leave_empty',
            },
            'columns': {
                'input': [{'name': 'Country', 'nullable': False}],
            },
        },
    }

    response = await app.get_vat_rate(
        {
            'Country': None,
        },
    )
    assert response.status == ResultType.SKIP


@pytest.mark.asyncio
async def test_vat_rate_no_input_column_found(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.current_vat_rate = {
        'FR': 20,
        'France': 20,
        'ES': 21,
        'Spain': 21,
    }
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'Country',
                'to': 'VAT',
                'action_if_not_found': 'leave_empty',
            },
            'columns': {
                'input': [{'name': 'Other', 'nullable': False}],
            },
        },
    }

    with pytest.raises(BaseTransformationException) as e:
        await app.get_vat_rate(
            {
                'Country': None,
            },
        )
        assert str(e.value) == 'The column Country does not exists.'


@pytest.mark.asyncio
async def test_vat_rate_country_not_found(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.current_vat_rate = {}
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'Country',
                'to': 'VAT',
                'action_if_not_found': 'fail',
            },
            'columns': {
                'input': [{'name': 'Country', 'nullable': False}],
            },
        },
    }

    response = await app.get_vat_rate(
        {
            'Country': 'AN',
        },
    )
    assert response.status == ResultType.FAIL
    assert response.output == 'Country AN not found'
