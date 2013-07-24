from django.conf.urls.defaults import patterns, url

from . import resources as r

urlpatterns = patterns('django.views.generic.simple',
    (r'^$', 'direct_to_template', {'template': 'crowdit/crowdit.html'}),
)

urlpatterns += patterns('',
    url(r'^rules/$',                            r.Rules),
    url(r'^rules/(?P<uid>[^/]+)/$',             r.Rule),

    url(r'^hooks/$',                            r.Hooks),
    url(r'^hooks/(?P<uid>[^/]+)/$',             r.Hook),

    url(r'^rerulers/$',                          r.Rerulers),
    #url(r'^rerulers/(?P<namespace>[^/]+)?$',     r.Rerulers),
    url(r'^rerulers/(?P<uid>[^/]+)/$',           r.Rerulers),

    url(r'^boostables/?$',                      r.Boostables),
    #url(r'^boostables/(?P<namespace>[^/]+)/?$', r.Boostables),
    url(r'^boostables/(?P<uid>[^/]+)/$',        r.Boostable),
    url(r'^boostables/(?P<uid>[^/]+)/power/$',  r.Power),

    url(r'^triggers/$',                         r.Triggers),
    url(r'^triggers/(?P<uid>[^/]+)/$',          r.Trigger),
)

