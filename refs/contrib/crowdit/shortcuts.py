from django.contrib.contenttypes.models import ContentType

from . import models

def rule(*args, **params):
    return models.Rule.objects.populate(*args, **params)

def rule_curry(**kwargs):
    """
    An easy way to specify default parameters for rules configuration.
    """
    def func(*args, **params):
        copy = kwargs.copy()
        copy.update(params)
        return rule(*args, **copy)
    return func

def listen(*args, **kwargs):
    return models.Hook.objects.listen(*args, **kwargs)
