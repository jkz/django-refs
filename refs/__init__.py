from .models import Ref
from .proxies import Proxy
from .fields import RefField, OneToOneRef, NamespaceField, ModelField, UIDField
from .casts import namespace, model, uid
from .managers import RelManager, RelQuerySet

# Overloaded transform functions.

def ref(obj=None, **kwargs):
    # 'namespace', 'model', 'uid' kwargs
    if not obj:
        if kwargs:
            return Ref.objects.get(**kwargs)
        return None
    # Proxy object
    if isinstance(obj, Proxy):
        return obj._ref
    # Ref object
    if isinstance(obj, Ref):
        return obj
    # UUID
    try:
        return Ref.objects.get(pk=obj)
    except TypeError:
        pass
    except Ref.DoesNotExist:
        pass
    # Model object
    return Ref.objects.get_or_create_ref(obj)[0]

def uuid(obj=None, **kwargs):
    if isinstance(obj, (int, long, basestring)):
        return obj
    return getattr(ref(obj, **kwargs), 'uuid', None)

def deref(obj=None, **kwargs):
    if isinstance(obj, (Ref, Proxy)):
        return obj.deref()
    if isinstance(obj, (int, long, basestring)):
        return ref(obj).deref()
    return obj

def proxy(obj=None, **kwargs):
    if isinstance(obj, Proxy):
        return obj
    return Proxy(ref(obj, **kwargs))

def equals(obj1, obj2):
    return ref(obj1) == ref(obj2)
