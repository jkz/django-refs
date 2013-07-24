from django.shortcuts import render_to_response

from utils.decorators import renders_to, to_json

from . import shortcuts

@renders_to('descriptions/edit.html')
def edit(request, obj, lang=settings.LANGUAGE_CODE):
    if request.method == 'POST':
        return shortcuts.edit(obj, lang,
                request.POST.get('head', None),
                request.POST.get('body', None))
    elif request.method =='GET':
        return {'description': shortcuts.get(obj, lang)}


@to_json
def resource(request, obj, lang=None):
    if request.method == 'DELETE':
        shortcuts.delete(obj, lang)
        return {}
    elif request.method in ('POST', 'PUT'):
        return shortcuts.edit(obj, lang,
                request.POST.get('head', None),
                request.POST.get('body', None)).to_json()
    elif request.method == 'GET':
        return shortcuts.get(obj, lang).to_json()


