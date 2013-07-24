import django.db.models as m
from utils.models import QuerySetModel, RequestQuerySet, QuerySetManager

import refs


class Poll(QuerySetModel):
    app = refs.RefField('polls')
    subject = m.TextField()
    content = m.TextField()


class Option(QuerySetModel):
    poll = m.ForeignKey(Poll, related_name='options')
    text = m.TextField()
    index = m.IntegerField(default=0)

    class Meta:
        ordering = ['poll', 'index']
        unique_together = [('poll', 'index')]

    def choose(self, user):
        try:
            vote = self.poll.votes.get(user=user)
        except Vote.DoesNotExist:
            return self.votes.create(poll=self.poll, user=user)
        vote.option = self
        vote.save()
        return vote

    def count(self):
        return self.votes.count()


class Vote(QuerySetModel):
    poll = m.ForeignKey(Poll, related_name='votes')
    option = m.ForeignKey(Option, related_name='votes')
    user = refs.RefField()


