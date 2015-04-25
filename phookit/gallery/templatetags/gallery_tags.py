from django import template

register = template.Library()

@register.filter
def join_image_tag_slugs(image, other_tag):
    return image.tag.slug + "," + other_tag.slug


#@register.filter
#def get_image_tag_slugs(image, in_tags):
#    if in_tags:
#        return in_tags
#    return image.tag.slug
