import datetime
import re
import os
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.db import models
from mezzanine.core.templatetags.mezzanine_tags import thumbnail

#from PIL import Image as PILImage

from phookit.core.models import Ownable, Slugged

class Tag(Slugged):
    '''
    Defines a tag which is essentially an album
    '''

    ''' Priority for ordering tags in menus '''
    priority = models.IntegerField(default=0)
    ''' Main tag or not '''
    main_tag = models.NullBooleanField(blank=True, null=True)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ("priority",)

    def __str__(self):
        return self.title


class Image(Ownable, Slugged):
    other_tags = models.ManyToManyField("Tag", 
                                  verbose_name=_("Tags"),
                                  blank=True, 
                                  related_name="other_tags")
    tag = models.ForeignKey(Tag, related_name='images')
    description = models.CharField(max_length=512, blank=True, null=True)
    filename = models.FileField(upload_to='galleryimages')
    _public_filename = models.CharField(max_length=512, blank=True, null=True)
    publish_date = models.DateTimeField(_("Published Date"),
        help_text=_("Date the image was published"),
        auto_now_add=True)

    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")
        ordering = ("-publish_date",)

    @property
    def public_filename(self):
        if not self._public_filename:
            self._public_filename = thumbnail(self.filename, settings.GALLERY_IMAGE_PUBLIC_WIDTH, settings.GALLERY_IMAGE_PUBLIC_HEIGHT)
            if self._public_filename:
                self._public_filename = "%s%s" % (settings.MEDIA_URL, self._public_filename)
            self.save()
        return self._public_filename    

    def __str__(self):
        return self.title
