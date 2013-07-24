# imports .ref (circular dependency)
from .models import Ref


class Proxy(object):
    """
    A proxy instance behaves like the object it's proxying, but provides a Ref
    interface as well.
    """
    #TODO write all necessary magic
    def __init__(self, obj):
        #TODO cache these attributes
        if isinstance(obj, Proxy):
            self._obj = obj._obj
            self._ref = obj._ref
        elif isinstance(obj, Ref):
            self._obj = obj.deref()
            self._ref = obj
        else:
            from . import ref
            self._obj = obj
            self._ref = ref(obj)

    @property
    def pk(self):
        """
        Return the pk of the object.
        The pk of the reference should always be referenced as 'uuid'
        """
        return self._obj.pk

    def save(self, *args, **kwargs):
        """Save both object and reference"""
        self._obj.save(*args, **kwargs)
        self._ref.save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Delete the object and kill the reference"""
        self._obj.delete(*args, **kwargs)
        self._ref.kill()

    def __getattr__(self, name):
        """
        Getattrs to the Proxy are deferred to the referent first,
        so they behave like referent-type objects to agnostic code.
        """
        try:
            return getattr(self._obj, name)
        except AttributeError as e:
            try:
                return getattr(self._ref, name)
            except AttributeError:
                raise e


    def __setattr__(self, name, value):
        """
        Call setattr on both the object and the reference.
        Propagate Attribute errors if they occur on both.
        """
        is_success = True
        if name in ('_obj', '_ref'):
            self.__dict__[name] = value
            return
        try:
            setattr(self._ref, name, value)
        except AttributeError:
            is_success = False
        try:
            setattr(self._obj, name, value)
        except AttributeError:
            if not is_success:
                raise

    def __unicode__(self):
        return unicode(self._obj)

