import os
from django.conf import settings
from django import template
from django.templatetags.static import StaticNode
from django.contrib.staticfiles.storage import staticfiles_storage

register = template.Library()

try:
    settings.STATIC_VERSION
except:        
    raise Exception("You need settings.STATIC_VERSION")


class StaticFilesNode(StaticNode):

    def url(self, context):
        path = self.path.resolve(context)
        return staticfiles_storage.url(os.path.join(settings.STATIC_VERSION, path))


@register.tag('staticv')
def do_staticv(parser, token):
    """
    A copy of the django static but with a version number taken
    from settings.
    """
    return StaticFilesNode.handle_token(parser, token)
