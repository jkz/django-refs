from django.conf.urls.defaults import patterns, url

from . import resources as r

urlpatterns = patterns('',
    url(r'^stories/$', r.Stories),
    url(r'^feeds/$', r.Feeds),
    url(r'^storyline/$', r.Storyline),
)

