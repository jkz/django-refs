import django.db.models as m

import uuids

from . import casts

#imports .models.Ref
#imports .ref
#imports .proxy

from utils.fields import CastToTextField

class NamespaceField(CastToTextField):
    def __init__(self, **kwargs):
        super(NamespaceField, self).__init__(casts.namespace, **kwargs)

class ModelField(CastToTextField):
    def __init__(self, **kwargs):
        super(ModelField, self).__init__(casts.model, **kwargs)

class UIDField(CastToTextField):
    def __init__(self, **kwargs):
        super(UIDField, self).__init__(casts.uid, **kwargs)

class UUIDField(uuids.UUIDField):
    def get_prep_value(self, value):
        from .models import Ref
        if not value:
            return
        value = casts.uuid(value)
        try:
            # This relies on the uuid field being a BigInteger
            return int(value)
        except ValueError:
            return Ref.objects.ensure_ref(value).uuid

class RefField(m.ForeignKey):
    """
    A foreign key to a Ref object, automatically casting its passed value
    """
    #__metaclass__ = m.SubfieldBase

    def __init__(self, related_name='ref_set', **kwargs):
        from .models import Ref
        super(RefField, self).__init__(Ref, related_name=related_name,
                **kwargs)

    def get_prep_value(self, value):
        from . import ref
        ret = ref(value),
        print 'PREP', value, ret
        return ret
        return ref(value)

    #XXX Might use these in the future
    def _to_python(self, value):
        from . import proxy
        print 'M2O TO_PYTHON', value
        return proxy(value)

class OneToOneRef(m.OneToOneField):
    #__metaclass__ = m.SubfieldBase

    def __init__(self, related_name='ref_set', **kwargs):
        from .models import Ref
        super(OneToOneRef, self).__init__(Ref, related_name=related_name,
                **kwargs)
    def get_prep_value(self, value):
        from . import ref
        ret = ref(value),
        print 'PREP', value, ret
        return ret
        return ref(value)

    #XXX Might use these in the future
    def _to_python(self, value):
        print 'O2O TO_PYTHON', value
        from . import proxy
        return proxy(value)


# MONEY PATCH!!
# We desire to change the assignment behaviour for reference fields, because
# the need to accept non-Ref values. Unfortunately this behaviour should be
# changed at the call to (Reverse)SingleRelatedObjectDescriptor.__set__,
# which is not accessible through the related field superclasses. Therefore,
# we monkeypatch the method here:
def reference_setter(func):
    def __set__(self, instance, value):
        from .models import Ref
        from . import ref
        if hasattr(self, 'field'):
            if (issubclass(self.field.related.parent_model, Ref)
            or (isinstance(self.field, UUIDField)
            and not isinstance(value, (int, basestring)))):
                value = ref(value)
        return func(self, instance, value)
    return __set__


def reference_getter(func):
    def __get__(self, instance, instance_type=None):
        from .models import Ref
        try:
            return func(self, instance, instance_type)
        except Ref.DoesNotExist:
            #XXX Dangerous stuff, not sure if ok
            print 'refs.fields.REMOVING'
            setattr(instance, self.field.attname, None)
            return None
    return __get__
from django.db.models.fields.related import (
    SingleRelatedObjectDescriptor as SROD,
    ReverseSingleRelatedObjectDescriptor as RSROD)
#            _.ForeignRelatedObjectsDescriptor,
#            _.ManyRelatedObjectsDescriptor,
#            _.ReverseManyRelatedObjectsDescriptor
for cls in SROD, RSROD:
    cls.__set__ = reference_setter(cls.__set__)
    cls.__get__ = reference_getter(cls.__get__)



# MORE MONKEYS!
# We need change UUIDField _pk_trace behaviour. It takes any value stored in
# the model (e.g. in uuid_id) and calculates its pk. We don't want the
# default pk, we want the pk of its Ref. We patch it here
from django.db.models.fields.related import RelatedField
def pk_tracer(func):
    def _pk_trace(self, value, prep_func, lookup_type, **kwargs):
        from . import ref
        if isinstance(self, (RefField, OneToOneRef)):
            value = ref(value)
        return func(self, value, prep_func, lookup_type, **kwargs)
    return _pk_trace
RelatedField._pk_trace = pk_tracer(RelatedField._pk_trace)
