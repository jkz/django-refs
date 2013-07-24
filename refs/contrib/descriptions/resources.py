from restlib.resources import Resource
from preserialize.serialize import serialize

from . import models
from . import shortcuts

class Description(Resource):
    def get(self, request, obj, lang=settings.LANGUAGE_CODE):
        return serialize(shortctus.description(obj, lang))

    def post(self, request, obj, lang-settings.LANGUAGE_CODE):
        return serialize(describe(obj, lang, request.POST.get('head', None),
            request.POST.get('body', None)))

    def delete(self, request, obj, lang=None):
      params = {'obj': obj}
        if lang:
            params['lang'] = lang
      models.Description.objects.filter(**params).delete()
      return ''
