from django import template
from django.utils.http import urlquote as quote
from django.conf import settings

register = template.Library()


@register.filter(is_safe=True)
def google_nav_url(event):
        location = quote(event.mappable_location)
        return "https://{}/maps?daddr={}".format(settings.GEOCODERS_GOOGLE_MAPS_DOMAIN, location)

@register.tag
def google_static_map(parser, token):
        try:
                tag_name, event, width, height, zoom = token.split_contents()
        except ValueError:
                raise template.TemplateSyntaxError('google_static_map requires an event, width, height and zoom level')
        return GoogleStaticMapNode(event, width, height, zoom)

class GoogleStaticMapNode (template.Node):
        def __init__(self, e, w, h, z):
                self.event = template.Variable(e)
                self.width = w
                self.height = h
                self.zoom = z
        def render(self, context):
                event = self.event.resolve(context)
                width = self.width
                height = self.height
                zoom = self.zoom
                marker = quote('{:.6},{:.6}'.format(event.lat, event.lon))
                if settings.GEOCODERS_HIDPI_STATIC_MAPS:
                        scale = 2
                else:
                        scale = 1
                return "<img src='http://maps.googleapis.com/maps/api/staticmap?size={width}x{height}&scale={scale}&format=png&markers={marker}&sensor=false&zoom={zoom}' width='{width}' height='{height}' />".format(**locals())
