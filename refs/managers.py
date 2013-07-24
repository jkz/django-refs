from django.db.models.query import QuerySet

from utils.models import MapFilterMixin, QuerySetManager

from . import casts

class RelManager(QuerySetManager):
    pass

class RelQuerySet(QuerySet, MapFilterMixin):
    """
    A manager with filters for models with Ref fields.
    Sample usage to find all users connected with a twitter account:

    class User:
        account = RefField()

    User.objects.with_namespace(account='twitter').with_model(account='user')
    """
    def with_namespace(self, **kwargs):
        return self.map_filter('%s__namespace', casts.namespace, **kwargs)
    def with_model(self, **kwargs):
        return self.map_filter('%s__model', casts.model, **kwargs)
    def with_uid(self, **kwargs):
        return self.map_filter('%s__uid', casts.uid, **kwargs)
