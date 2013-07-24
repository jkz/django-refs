from django.conf.urls.defaults import patterns, url

from . import resources as r

urlpatterns = patterns('',
    url(r'^polls/?$', r.Poll()),
    url(r'^polls/(?P<poll>[^/]+)/?$', r.Poll()),

    url(r'^polls/(?P<poll>[^/]+)/options/?$', r.Option()),
    url(r'^polls/(?P<poll>[^/]+)/options/(?P<index>[^/]+)/?$', r.Option()),

    url(r'^polls/(?P<poll>[^/]+)/votes/$', r.Vote()),
    url(r'^polls/(?P<poll>[^/]+)/votes/(?P<index>[^/]+)/?$', r.Vote()),
)

