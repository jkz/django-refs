import django.db.models as m
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType

from utils.models import QuerySetManager

from . import fields as f


class DanglingReferenceException(Exception):
    pass

class ReferenceManager(QuerySetManager):
    def get_query_set(self):
        return super(ReferenceManager, self).get_query_set() \
                .filter(is_dangling=False)

class DanglingReferenceManager(QuerySetManager):
    """
    A dangling reference references an object that does no longer exist. The
    reference is kept for meta purposes, but no longer considered valid data.
    """
    def get_query_set(self):
        return super(DanglerManager, self).get_query_set() \
                .filter(is_dangling=True)

class Ref(m.Model):
    """
    A generic reference to any database model object. It is built for maximum
    flexibility, by casting arguments magically.
    """
    uuid = f.UUIDField(primary_key=True)
    namespace = f.NamespaceField()
    model = f.ModelField()
    uid = f.UIDField(null=True)
    is_dangling = m.BooleanField(default=False)

    objects = ReferenceManager()
    danglers = DanglingReferenceManager()
    all_objects = QuerySetManager()

    class Meta:
        unique_together = [('namespace', 'model', 'uid')]

    def __unicode__(self):
        return '{}::{}_{}({})'.format(self.pk, self.namespace, self.model, self.uid)

    def danglify(self):
        """
        Flag a reference that lost its referent.
        """
        self.is_dangling = True
        self.save()

    @property
    def content_type(self):
        """Return the content type of the referenced object"""
        return ContentType.objects.get_by_natural_key(self.namespace, self.model)

    @property
    def model_class(self):
        cls = self.content_type.model_class()
        return cls

    def deref(self):
        """
        Return the orignal referenced object. If it does not exist, danglify
        the reference.
        """
        try:
            return self.content_type.get_object_for_this_type(pk=self.uid)
        except self.model_class.DoesNotExist:
            self.danglify()
            raise DanglingReferenceException

    def proxy(self):
        from . import proxy as p
        return p(self)


    class QuerySet(QuerySet):
        def create_ref(self, obj):
            return self.create(namespace=obj, model=obj, uid=obj)

        def get_ref(self, obj):
            return self.get(namespace=obj, model=obj, uid=obj)

        def get_or_create_ref(self, obj):
            try:
                return self.get_ref(obj), False
            except Ref.DoesNotExist:
                return self.create_ref(obj), True

        def with_content_type(self, content_type):
            return self.filter(namespace=content_type, model=content_type)

