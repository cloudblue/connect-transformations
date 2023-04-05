from connect_transformations.exceptions import BaseTransformationException


def is_input_column_nullable(input_columns, column):
    for input_column in input_columns:
        if input_column['name'] == column:
            return input_column['nullable']
    raise BaseTransformationException(f'The column {column} does not exists.')
