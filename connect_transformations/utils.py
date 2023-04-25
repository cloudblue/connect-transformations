from decimal import Decimal

from dateutil.parser import parse as _to_datetime
from fastapi.responses import JSONResponse

from connect_transformations.exceptions import BaseTransformationException


def is_input_column_nullable(input_columns, column):
    for input_column in input_columns:
        if input_column['name'] == column:
            return input_column['nullable']
    raise BaseTransformationException(f'The column {column} does not exists.')


def _to_decimal(value, precision=2):
    value = value.replace(',', '.') if isinstance(value, str) else value
    return Decimal(
        value,
    ).quantize(
        Decimal(f'.{"1".zfill(int(precision))}'),
    )


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


def check_mapping(settings, columns):
    available_columns = [c['name'] for c in columns['input']]
    if settings['map_by']['input_column'] not in available_columns:
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
                or 'to' not in mapping
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
