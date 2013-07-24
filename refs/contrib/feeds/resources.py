from restlib.resources import Resource

from preserialize.serialize import serialize

from . import models as m

class Stories(Resource):
    def get(self, request):
        if request.is_parent_mode:
            #TODO: bind feeds to a line properly
            '''
            lines = m.Line.objects.filter(app=request.client)
            stories = m.Story.objects.filter(feed__line__in=lines)
            '''
            stories = m.Story.objects.all()
        else:
            feeds = m.Feed.objects.filter(app=request.client)
            stories = m.Story.objects.filter(feed__in=feeds)
        return serialize(stories.request(request))


class Story(Resource):
    def get(self, request, uid):
        return serialize(m.Story.objects.get(pk=uid))

class Feeds(Resource):
    def get(self, request):
        return serialize(m.Feed.objects.filter(app=request.client))

class Storyline(Resource):
    pass
