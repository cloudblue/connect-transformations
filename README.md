# Welcome to the CloudBlue Connect Standard Transformations Extension!

*Connect Standard Transformations Library* is an extension of the CloudBlue Connect platform that provides customers with the ability to transform a stream of data by applying different transformations to it. This extension makes it easier for users to manage and manipulate data by providing pre-built transformations that can be easily configured and executed.

## Available transformations:

The current release provides the following transformations:

* `Manual transformation`: The manual transformation is a special kind of transformation that allow to describe the steps that must be done on the input file to produce the transformed output file. The file must be transformed both by hands or by an external system.
* `Copy Column(s)`: This transformation allows you to copy values from Input to Output columns, which might be handy if you’d like to change column name in the output data or for some other reason create a copy of values in a table.
* `Split Column`: This transformation function allows you to copy values from Input to Output columns, which might be handy if you’d like to change column name in the output data for for some other reason create a copy of values in table.
* `Lookup CloudBlue Subscription data`: This transformation function allows to search for the corresponding CloudBlue Subscription data.
* `Convert Currency`: This transformation function converts a given column value with a given currency to another.
* `Formula`: Use this transformation to perform data manipulation using columns manipulation formula.
* `Filter Rows`: This transformation function allows you to filter by equality of a given input column with a given string value. If it matches the row is kept, if not it is marked to be deleted.

Overall, Connect Standard Transformations Library is a valuable extension of the CloudBlue Connect platform that provides users with a powerful set of tools for managing and manipulating data. By providing pre-built transformations that can be easily configured and executed, Connect Standard Transformations Library streamlines the data transformation process and makes it easier for users to work with their data.

## License

**CloudBlue Connect Standard Transformations Extension** is licensed under the *Apache Software License 2.0* license.
