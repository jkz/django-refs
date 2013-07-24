from django.conf import settings
from restlib.resources import Resource

from preserialize.serialize import serialize

import credits

from . import models as m

class Rules(Resource):
    def get(self, request, namespace=None):
        params = {}
        if namespace:
            params['app'] = request.app.clients[namespace]
        else:
            params['app__in'] = request.app.clients.values_list('child__pk', flat=True)
        return serialize(m.Rule.objects.request(request, **params))


class Rule(Resource):
    def get(self, request, uid):
        return serialize(m.Rule.objects.get(pk=uid))


class Rerulers(Resource):
    def get(self, request, namespace=None):
        params = {}
        if namespace:
            params['rule__app__namespace'] = namespace
        return serialize(m.Hook.rerulers.request(request, **params))

class Boostables(Resource):
    def get(self, request, namespace=None):
        params = {}
        if namespace:
            params['rule__app__namespace'] = namespace
        hooks = m.Hook.boostables.request(request, **params)
        result = []
        for hook in hooks:
            data = serialize(hook)
            data['power'] = credits.have(hook, settings.CURRENCY)
            result.append(data)
        return result

class Boostable(Resource):
    def get(self, request, uid):
        hook = m.Hook.boostables.get(pk=uid)
        data = serialize(hook)
        data['power'] = credits.have(hook, settings.CURRENCY)
        return data


class Power(Resource):
    def get(self, request, uid):
        hook = m.Hook.boostables.get(pk=uid)
        return credits.have(hook, settings.CURRENCY)

    def post(self, request, uid):
        hook = m.Hook.boostables.get(pk=uid)
        hook.boost(request.user, request.POST.get('amount'))
        return {}


class Hooks(Resource):
    def get(self, request, namespace=None):
        params = {}
        if namespace:
            params['user'] = request.user.accounts[namespace]
        else:
            params['user__in'] = request.user.accounts.values_list('child__pk', flat=True)
        return serialize(m.Hook.objects.request(request, **params))

class Hook(Resource):
    def get(self, request, uid):
        return m.Hook.objects.get(pk=uid)

    def post(self, request, uid):
        m.Hook.objects.get(pk=uid).boost(request.user, request.POST.get('amount'))
        return {}


class Triggers(Resource):
    def get(self, request, namespace=None):
        params = {}
        if namespace:
            params['user'] = request.user.accounts[namespace]
        else:
            params['user__in'] = request.user.accounts.values_list('child__pk', flat=True)
        return serialize(m.Trigger.objects.request(request, **params))


class Trigger(Resource):
    def get(self, request, uid):
        return m.Trigger.objects.get(pk=uid)

