from django.conf.urls.defaults import patterns, url

from . import views as v

urlpatterns = patterns('',
    url(r'^(?P<obj>[^/]+)/edit/',                 v.edit),
    url(r'^(?P<obj>[^/]+)/edit/(?P<lang>[^/]+)/', v.edit),

    url(r'^(?P<obj>[^/]+)/',                      v.resource),
    url(r'^(?P<obj>[^/]+)/(?P<lang>[^/]+)/',      v.resource),
)

