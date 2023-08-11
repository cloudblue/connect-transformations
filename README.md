# Welcome to the CloudBlue Connect Standard Transformations Extension!

*Connect Standard Transformations Library* is an extension of the CloudBlue Connect platform that provides customers with the ability to transform a stream of data by applying different transformations to it. This extension makes it easier for users to manage and manipulate data by providing pre-built transformations that can be easily configured and executed.

## Available transformations:

The current release provides the following transformations:

* `Manual transformation`: This transformation function allows you to perform manual operations that cannot be automated using other transformations.
* `Copy columns`: This transformation function allows you to copy input column values to an output column.
* `Split columns`: This transformation function allows you to divide values of one column into separate columns, using regular expressions.
* `Lookup CloudBlue subscription data`: This transformation function allows you to get the Cloudblue subscription data by the subscription ID or parameter value.
* `Lookup CloudBlue product item`: This transformation function allows you to get the CloudBlue product item data by the product item ID or MPN.
* `Convert currency`: This transformation function allows you to convert currency rates, using the https://exchangerate.host API.
* `Formula`: This transformation function allows you to perform mathematical and logical operations on columns and context variables using the jq programming language.
* `Delete rows by condition`: This transformation function allows you to delete rows that contain or do not contain a specific value(s).
* `Lookup data from AirTable`: This transformation function allows you to populate data from AirTable by matching input column values with AirTable ones.
* `Lookup data from Excel file attached to stream`: This transformation function allows you to populate data from the attached Excel file by matching input column values with the attached table values.
* `Get standard VAT Rate for EU Country`: This transformation function is performed, using the latest rates from the https://exchangerate.host API. The input value must be either a two-letter country code defined in the ISO 3166-1 alpha-2 standard or country name. For example, ES or Spain.

Overall, Connect Standard Transformations Library is a valuable extension of the CloudBlue Connect platform that provides users with a powerful set of tools for managing and manipulating data. By providing pre-built transformations that can be easily configured and executed, Connect Standard Transformations Library streamlines the data transformation process and makes it easier for users to work with their data.

## License

**CloudBlue Connect Standard Transformations Extension** is licensed under the *Apache Software License 2.0* license.
