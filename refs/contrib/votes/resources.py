from restlib.resources import Resource

from preserialize.serialize import serialize

import credits

from . import models as m


class Poll(Resource):
    def get(self, request, poll_pk):
        poll = m.Poll.objects.get(pk=poll_pk)
        data = serialize(poll, fields=['subject', 'content'])
        data['options'] = {}
        data['total'] = 0
        for option in poll.options.all():
            o = serialize(option, fields=['text', 'index', 'count'])
            data['options'][unicode(option.index)] = o
            data['count'] += o['count']
        if request.user.is_authenticated():
            try:
                data['vote'] = q.votes.get(user=request.user).option.index
            except m.Vote.DoesNotExist:
                data['vote'] = None
        return data

    def post(self, request):
        m.Poll.objects.create(**request.data)
        return {}

    def put(self, request, poll_pk):
        m.Poll(pk=poll_pk, **request.data).save()
        return {}

    def delete(self, request, poll_pk):
        # Fails silently
        m.Poll.objects.filter(pk=poll_pk).delete()
        return {}


class Option(Resource):
    def get(self, request, poll_pk, option_idx=None):
        if option_idx is None:
            options = m.Option.objects.filter(poll_pk=poll_pk)
        else:
            options = m.Option.objects.get(poll_pk=poll_pk, index=option_idx)
        return serialize(options, fields=['text', 'index', 'count', 'poll'],
                related={'poll': ['subject', 'content']})

    def post(self, request, poll_pk):
        poll = m.Poll.objects.get(pk=poll_pk)
        poll.options.create(**request.data)
        return {}

    def put(self, request, poll_pk, option_idx):
        poll = m.Poll.objects.get(pk=poll_pk)
        option, created = poll.objects.get_or_create(index=option_idx)
        poll.options.update(**request.data)
        return {}

    def delete(self, request, poll_pk, option_idx):
        # Fails silently
        m.Option.objects.filter(poll__pk=poll_pk, index=option_idx).delete()
        return {}


class Vote(Resource):
    def put(self, request, poll_pk, option_idx):
        option = m.Option.objects.get(poll__pk=poll_pk, index=option_idx)
        option.choose(request.user)
        return {}

    def delete(self, request, poll_pk):
        vote = m.Vote.objects.get(poll_id=poll, user=request.user)
        vote.delete()
        return {}

