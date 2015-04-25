from django.db import models
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.fields import FileField, RichTextField
from mezzanine.core.models import SiteRelated
from mezzanine.utils.models import upload_to
from phookit.address.models import Address

class SitewideContent(SiteRelated):
    '''
    A page representing the format of the home page
    '''
    image = FileField(verbose_name=_("Image"),
                    upload_to=upload_to("homepage.image", "homepage"),
                            format="Image", max_length=255, null=True, blank=True)
    other_title = models.CharField(max_length=64, default="Other Title")
    other_sub_title = models.CharField(max_length=64, default="Other Sub Title")
    description = RichTextField()
    address = models.OneToOneField(Address)

    class Meta:
        verbose_name = _("Sitewide Content")
        verbose_name_plural = _("Sitewide Content")


