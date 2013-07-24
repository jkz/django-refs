"""
Cast object arguments to desired types. Common converted types would be
Model instances, Ref instances, strings, ContentType.
"""

from functools import wraps

def to_str(func):
    @wraps(func)
    def funk(obj):
        res = func(obj)
        if isinstance(res, (int, long)):
            res = str(res)
        return res
    return funk


@to_str
def uid(obj):
    if hasattr(obj, 'uid'):
        return obj.uid
    if hasattr(obj, 'pk'):
        return obj.pk
    return obj


def lower(func):
    @wraps(func)
    def funk(obj):
        res = func(obj)
        try:
            return res.lower()
        except AttributeError:
            return res
    return funk



@lower
def model(obj):
    if isinstance(obj, basestring):
        return obj
    if hasattr(obj, 'model'):
        return obj.model
    if hasattr(obj, '_meta') and hasattr(obj._meta, 'model'):
        return obj._meta.model
    if hasattr(obj, '__name__'):
        return obj.__name__
    if hasattr(obj, '__class__') and hasattr(obj.__class__, '__name__'):
        return obj.__class__.__name__
    return obj

@lower
def namespace(obj):
    if isinstance(obj, basestring):
        return obj
    if hasattr(obj, 'namespace'):
        return obj.namespace
    if hasattr(obj, 'app_label'):
        return obj.app_label
    if hasattr(obj, '_meta'):
        return obj._meta.app_label
    if hasattr(obj, '_meta') and hasattr(obj._meta, 'app_label'):
        return obj._meta.app_label
    if hasattr(obj, '__module__'):
        return obj.__module__
    if hasattr(obj, '__class__') and hasattr(obj.__class__, '__module__'):
        return obj.__class__.__module__
    return obj

def uuid(obj):
    if isinstance(obj, (int, long, basestring)):
        return obj
    if hasattr(obj, 'uuid'):
        return obj.uuid
    return obj
