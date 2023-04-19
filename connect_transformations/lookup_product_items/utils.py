# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from connect.client.exceptions import ClientError
from connect.eaas.core.responses import RowTransformationResponse
from fastapi.responses import JSONResponse

from connect_transformations.constants import PRODUCT_ITEM_LOOKUP
from connect_transformations.exceptions import ProductLookupError


async def retrieve_product(client, cache, cache_lock, product_id, leave_empty):
    cached_product = cache.get(product_id)
    if cached_product:
        return cached_product

    try:
        product = await client.products[product_id].get()
    except ClientError:
        if leave_empty:
            return
        raise ProductLookupError('Product not found')
    async with cache_lock:
        cache[product_id] = product
    return product


async def _get_product_item_by_id(client, product, lookup_value):
    try:
        return await client.products[product['id']].items[lookup_value].get()
    except ClientError:
        return None


async def _get_product_item_by_filter(client, product, lookup_value):
    filter_expression = f"eq(mpn,{lookup_value})"
    count = await client.products[product['id']].items.filter(filter_expression).count()

    if count == 0:
        return None
    elif count > 1:
        raise ProductLookupError(f'Multiple results found for the filter: {lookup_value}')

    return await client.products[product['id']].items.filter(filter_expression).first()


async def retrieve_product_item(
        client, cache, cache_lock, product, lookup_type, lookup_value, leave_empty,
):
    cache_key = f'{lookup_type}-{lookup_value}'
    cached_product_item = cache.get(cache_key)

    if cached_product_item:
        return cached_product_item

    if lookup_type not in PRODUCT_ITEM_LOOKUP:
        raise ProductLookupError('Unknown lookup type')

    product_item = None
    if lookup_type == 'id':
        product_item = await _get_product_item_by_id(client, product, lookup_value)
    else:
        product_item = await _get_product_item_by_filter(client, product, lookup_value)

    if product_item is None and not leave_empty:
        raise ProductLookupError('Product not found')

    if product_item is not None:
        product_item['product'] = product
        async with cache_lock:
            cache[cache_key] = product_item

    return product_item


def _validate_required_keys(data, required_keys):
    for key in required_keys:
        if key not in data or not data[key]:
            return False
    return True


def _validate_required_product_keys(data, product_id, product_column):
    if (product_id not in data) and (product_column not in data):
        return False
    if (not data[product_id]) and (not data[product_column]):
        return False
    return True


def _build_error_response(message):
    return JSONResponse(status_code=400, content={'error': message})


def _build_overview(settings):
    overview = f'Criteria = "{PRODUCT_ITEM_LOOKUP[settings["lookup_type"]]}"\n'
    if settings.get('product_id', '') != '':
        overview += f'In product = "{settings["product_id"]}"\n'
    if settings.get('product_column', '') != '':
        overview += 'With row-specific product IDs \n'
    overview += f'Prefix = "{settings["prefix"]}"\n'
    overview += f'If not found = {settings["action_if_not_found"].replace("_", " ").title()}\n'
    return overview


def validate_lookup_product_item(data):
    """
    Validate the input data for the lookup product item process.
    """
    if not _validate_required_keys(
        data, ['settings', 'columns'],
    ) or not _validate_required_keys(
        data['columns'], ['input'],
    ):
        return _build_error_response('Invalid input data')

    required_settings_keys = ['lookup_type', 'from', 'prefix', 'action_if_not_found']
    if not _validate_required_keys(data['settings'], required_settings_keys):
        return _build_error_response(
            'The settings must have `lookup_type`, `from`, `prefix` '
            'and `action_if_not_found` fields',
        )

    if not _validate_required_product_keys(data['settings'], 'product_id', 'product_column'):
        return _build_error_response(
            'No product associated with this data stream. Please either enter '
            'a Product ID, which will be applied to all product item lookups, '
            'or select a Product column containing the row-specific product IDs.',
        )

    settings = data['settings']
    if settings['lookup_type'] not in PRODUCT_ITEM_LOOKUP:
        return _build_error_response(
            f'The settings `lookup_type` allowed values {list(PRODUCT_ITEM_LOOKUP.keys())}',
        )

    values = ['leave_empty', 'fail']
    if settings['action_if_not_found'] not in values:
        return _build_error_response(
            f'The settings `action_if_not_found` allowed values {values}',
        )

    input_columns = data['columns']['input']
    available_input_columns = [c['name'] for c in input_columns]
    column_name = settings['from']
    if column_name not in available_input_columns:
        return _build_error_response(
            f'The settings `from` contains an invalid column name {column_name} '
            'that does not exist on columns.input',
        )

    if len(settings['prefix']) > 10:
        return _build_error_response('The settings `prefix` max length is 10')

    return {'overview': _build_overview(settings)}


def extract_settings(trfn_settings, row):
    product_id = trfn_settings['product_id']
    if product_id == '':
        product_column = trfn_settings['product_column']
        product_id = row[product_column]
    from_column = trfn_settings['from']
    leave_empty = trfn_settings['action_if_not_found'] == 'leave_empty'
    return product_id, from_column, leave_empty


def generate_transformation_response(trfn_settings, product_item):
    if not product_item:
        return RowTransformationResponse.skip()

    prefix = trfn_settings['prefix']
    output_data = {
        f'{prefix}.product.id': product_item['product']['id'],
        f'{prefix}.product.name': product_item['product']['name'],
        f'{prefix}.item.id': product_item['id'],
        f'{prefix}.item.name': product_item['name'],
        f'{prefix}.item.unit': product_item['unit']['name'],
        f'{prefix}.item.period': product_item['period'],
        f'{prefix}.item.mpn': product_item['mpn'],
    }

    return RowTransformationResponse.done(output_data)
