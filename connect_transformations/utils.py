def is_input_column_nullable(input_columns, column):
    for input_column in input_columns:
        if input_column['name'] == column:
            return input_column['nullable']
    return True
