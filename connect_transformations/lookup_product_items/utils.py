# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from connect.eaas.core.responses import RowTransformationResponse

from connect_transformations.utils import (
    build_error_response,
    does_not_contain_required_keys,
    has_invalid_basic_structure,
)


PRODUCT_ITEM_LOOKUP = {
    'mpn': 'CloudBlue Item MPN',
    'id': 'CloudBlue Item ID',
}


def _validate_required_product_keys(data, product_id, product_column):
    if (product_id not in data) and (product_column not in data):
        return False
    if (not data[product_id]) and (not data[product_column]):
        return False
    return True


def _build_overview(settings):
    overview = f'Criteria = "{PRODUCT_ITEM_LOOKUP[settings["lookup_type"]]}"\n'
    if settings.get('product_lookup_mode', '') == 'id':
        overview += f'In product = "{settings["product_id"]}"\n'
    if settings.get('product_lookup_mode', '') == 'column':
        overview += 'With row-specific product IDs \n'
    overview += f'Prefix = "{settings["prefix"]}"\n'
    overview += f'If not found = {settings["action_if_not_found"].replace("_", " ").title()}\n'
    return overview


def validate_lookup_product_item(data):
    """
    Validate the input data for the lookup product item process.
    """
    data = data.dict(by_alias=True)

    if has_invalid_basic_structure(data):
        return build_error_response('Invalid input data')

    required_settings_keys = ['lookup_type', 'from', 'prefix', 'action_if_not_found']
    if does_not_contain_required_keys(data['settings'], required_settings_keys):
        return build_error_response(
            'The settings must have `lookup_type`, `from`, `prefix` '
            'and `action_if_not_found` fields',
        )

    if not _validate_required_product_keys(data['settings'], 'product_id', 'product_column'):
        return build_error_response(
            'No product associated with this data stream. Please either enter '
            'a Product ID, which will be applied to all product item lookups, '
            'or select a Product column containing the row-specific product IDs.',
        )

    settings = data['settings']
    if settings['lookup_type'] not in PRODUCT_ITEM_LOOKUP:
        return build_error_response(
            f'The settings `lookup_type` allowed values {list(PRODUCT_ITEM_LOOKUP.keys())}',
        )

    values = ['leave_empty', 'fail']
    if settings['action_if_not_found'] not in values:
        return build_error_response(
            f'The settings `action_if_not_found` allowed values {values}',
        )

    input_columns = data['columns']['input']
    available_input_columns = [c['name'] for c in input_columns]
    column_name = settings['from']
    if column_name not in available_input_columns:
        return build_error_response(
            f'The settings `from` contains an invalid column name {column_name} '
            'that does not exist on columns.input',
        )

    if len(settings['prefix']) > 10:
        return build_error_response('The settings `prefix` max length is 10')

    return {'overview': _build_overview(settings)}


def extract_settings(trfn_settings, row):
    product_lookup_mode = trfn_settings.get('product_lookup_mode', 'id')
    product_id = trfn_settings['product_id']
    if product_lookup_mode == 'column':
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
        f'{prefix}.item.commitment': product_item.get('commitment', {}).get('count'),
    }

    return RowTransformationResponse.done(output_data)
