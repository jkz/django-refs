# Django Refs
## Reference internal and external resources by uuid

The Reference model has 4 fields:
`uuid` the uuid that maps
`namespace` usually the name of a Django app with models, but could as well be an adapter for an external api
`model` usually a django-style model name, but could also be an external resource name
`uid` the unique identifier of the model or resource

