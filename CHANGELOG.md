# Changelog

## v1.3.7 2021-05-20

* Update dependencies

## v1.3.6 2021-05-20

* Update dependencies

## v1.3.5 2020-02-28

* Rework schema reference logic, to improve handling of nested structures.

## v1.3.4 2020-02-27

* Resolve issue with drf-spectacular's use of "oneOf" to handle null enums.

## v1.3.3 2020-02-25

* Replace Python 3.8+ functools.cache_property with the Django builtin version to ensure Python 3.6 comp.

## v1.3.2 2020-02-20

* Hotfix regression due to pk resolution logic

## v1.3.1 2020-02-20

* Hotfix regression due to pk resolution logic

## v1.3.0 2020-02-20

* Added validators for the "format" keyword, handling the following format values generated by DRF and DRF derived libraries: "uuid", "base64", "email", "uri", "url", "ipv4", "ipv6" and "time"
  validator
* Added support for dynamic <pk> url parameters (DRF feature) in schemas
* Added an option to pass a map of custom url parameters and values
* Fixed handling of byte format to test for base64 string instead of bytes
* Refactored error messages to be more concise and precise


## v1.2.0 2020-02-14

* Added validation of writeOnly keys
* Updated openAPI keyword (anyOf, oneOf, allOf) logic
* Resolve minor issues with error formatting (unable to handle bytes)

## v1.1.0 2020-02-12

* Fixed allOf deep object merging
* Fixed handling of non-string path parameters
* Fixed error messages
* Fixed handling of 0 as a float format value

## v1.0.0 2020-02-07

* Now supports `anyOf`
* Adds `additionalProperties` support
* Adds validation for remaining OpenAPI features, including
    * `format`
    * `enum`
    * `pattern`
    * `multipleOf`
    * `uniqueItems`
    * `minLength` and `maxLength`
    * `minProperties` and `maxProperties`
    * `minimum`, `maximum`, `exclusiveMinimum`, and `exclusiveMaximum`

## v0.1.0 2020-01-26

* Package refactored and renamed from `django-swagger-tester` to `drf-openapi-tester`
* Adds `inflection` for case checking
* Adds `prance` for schema validation
* Adds enum validation
* Adds format validation
* Adds support for `oneOf` and `allOf`
