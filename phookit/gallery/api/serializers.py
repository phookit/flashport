
from django.conf import settings
from django.core.urlresolvers import reverse
from rest_framework import serializers
from rest_framework import pagination
#from rest_framework.reverse import reverse
from mezzanine.core.templatetags.mezzanine_tags import thumbnail

from phookit.gallery.models import Image, Tag


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'title', 'slug', 'main_tag', 'priority', )



class ImageSerializer(serializers.ModelSerializer):

    url = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ('id', 'title', 'url', 'slug', 'description', 'public_filename', 'filename', 'thumbnail', 'publish_date', 'tag', 'other_tags',)

    def get_url(self, obj):
        return reverse('gallery-image', args=[obj.slug])

    def get_thumbnail(self, obj):
        return settings.MEDIA_URL + thumbnail(obj.filename, 420, 260, 95, .5, .5, True, '#25286b');
