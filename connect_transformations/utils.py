from decimal import Decimal

from dateutil.parser import parse as _to_datetime
from fastapi.responses import JSONResponse

from connect_transformations.exceptions import BaseTransformationException


def is_input_column_nullable(input_columns, column):
    for input_column in input_columns:
        if input_column['name'] == column:
            return input_column['nullable']
    raise BaseTransformationException(f'The column {column} does not exists.')


def _to_decimal(value, precision=None):
    value = value.replace(',', '.') if isinstance(value, str) else value
    return Decimal(
        value,
    ).quantize(
        Decimal(f'.{"1".zfill(int(precision))}'),
    ) if precision else Decimal(value)


def _to_boolean(value):
    if isinstance(value, bool):
        return value
    value = value.lower() if isinstance(value, str) else value
    if value in ['true', '1', 'y', 'yes']:
        return True
    elif value in ['false', '0', 'n', 'no']:
        return False


_cast_mapping = {
    'string': str,
    'integer': int,
    'decimal': _to_decimal,
    'boolean': _to_boolean,
    'datetime': _to_datetime,
}


def cast_value_to_type(value, type, additional_parameters=None):
    if additional_parameters is None:
        additional_parameters = {}
    cast_fn = _cast_mapping[type]
    return cast_fn(value, **additional_parameters) if value is not None else None


def check_mapping(settings, columns, multiple=False):
    available_columns = [c['name'] for c in columns['input']]
    if multiple:
        input_columns = [item['input_column'] for item in settings['map_by']]
    else:
        input_columns = [settings['map_by']['input_column']]

    for col in input_columns:
        if col not in available_columns:
            return JSONResponse(
                status_code=400,
                content={
                    'error': (
                        'The settings contains invalid input column that '
                        'does not exist on columns.input'
                    ),
                },
            )

    for mapping in settings['mapping']:
        if (
            not isinstance(mapping, dict)
            or 'from' not in mapping
            or not mapping['from']
            or 'to' not in mapping
            or not mapping['to']
        ):
            return JSONResponse(
                status_code=400,
                content={
                    'error': (
                        'Each element of the settings `mapping` must contain '
                        '`from` and `to` fields in it.'
                    ),
                },
            )


def does_not_contain_required_keys(data, required_keys):
    for key in required_keys:
        if key not in data or data[key] is None:
            return True
    return False


def has_invalid_basic_structure(data, data_type=dict):
    return (
        does_not_contain_required_keys(data, ['settings', 'columns'])
        or not isinstance(data['settings'], data_type)
        or does_not_contain_required_keys(data['columns'], ['input'])
    )


def build_error_response(message):
    return JSONResponse(status_code=400, content={'error': message})


def deep_convert_type(original, type_to_convert, converter):
    if isinstance(original, type_to_convert):
        return converter(original)
    elif isinstance(original, dict):
        return {k: deep_convert_type(v, type_to_convert, converter) for k, v in original.items()}
    elif isinstance(original, list):
        return [deep_convert_type(v, type_to_convert, converter) for v in original]
    return original


def deep_itemgetter(obj, attr_name):
    value = obj
    for attr in attr_name.split('.'):
        try:
            value = value[attr]
        except KeyError:
            return
    return value
