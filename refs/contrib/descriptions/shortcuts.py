from .models import Description
from django.conf import settings

def get(obj, lang=settings.LANGUAGE_CODE):
    return Description.objects.get(obj=obj, lang=lang)

def edit(obj, lang, head=None, body=None):
    desc, created = Description.objects.get_or_create(obj=obj, lang=lang)
    if head is not None:
      desc.head = head
    if body is not None:
      desc.body = body
    desc.save()
    return desc

def delete(obj, lang=None):
    params = {'obj': obj}
    if lang:
        params['lang'] = lang
    models.Description.objects.filter(**params).delete()
