# Django Refs
## Reference internal and external resources by uuid

The Reference model has 4 fields:

- `uuid` the new identifier for the resource
- `namespace` usually the name of a Django app with models, but could be an adapter for an external api
- `model` usually a Django style model name, but could also be an external resource name
- `uid` the original identifier of the model or resource

