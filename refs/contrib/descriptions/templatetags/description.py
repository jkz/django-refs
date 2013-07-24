from django import template
register = template.Library()

from .. import shortcuts

@register.tag
def do_upper(parser, token):
    nodelist = parser.parse(('enddescription',))
    parser.delete_first_token()
    tag_name, arg = token.contents.split(None, 1)

    return UpperNode(nodelist)

class DescriptionNode(template.Node):
    def __init__(self, nodelist, obj, lang=None):
        self.nodelist = nodelist
        self.description = shortcuts.get(
                obj=template.Variable(obj),
                lang=lang and
                template.Variable(lang)

    def render(self, context):
        return self.nodel
        output = self.nodelist.render(context)
        return output.upper()
