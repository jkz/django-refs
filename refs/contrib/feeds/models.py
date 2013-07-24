import django.db.models as m

import refs

from utils.decorators import created_receiver
from utils.fields import TimestampField
from utils.functions import getattr_recursive
from utils.models import QuerySetModel, RequestQuerySet

class Line(m.Model):
    app = refs.RefField('storyline')

class Feed(m.Model):
    line = m.ForeignKey(Line, null=True, related_name='feeds')
    app = refs.RefField('storyfeeds_as_app')
    user = refs.RefField('storyfeeds_as_user')

    def feeds_user(self, user):
        print 'feeds user %s == %s -> %s' % (self, user, refs.equals(self.user, user))
        return refs.equals(self.user, user)

    def fire(self, obj):
        return self.stories.get_or_create(obj=obj)

    def listen(self, model, attr):
        #XXX Does not support nested attributes!
        @created_receiver(model, dispatch_uid='%s.%s' % (model.__name__, attr))
        def feed_listener(instance, **kwargs):
            if self.feeds_user(getattr_recursive(instance, attr)):
                self.fire(instance)

class Story(QuerySetModel):
    feed = m.ForeignKey(Feed, related_name='stories')
    obj = refs.RefField('stories')
    timestamp = TimestampField()

    class Meta:
        ordering = ['-timestamp']

    class QuerySet(RequestQuerySet): pass

