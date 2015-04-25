import re
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Slugged(models.Model):
    title = models.CharField(max_length=64)
    slug = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        """
        if not self.slug:
            self.slug = self.generate_slug()
        super(Slugged, self).save(*args, **kwargs)

    def generate_slug(self):
        s = self.get_slug()
        qs = self.__class__.objects.all()
        i = 1
        while True:
            try:
                qs.get(**{'slug': s})
            except ObjectDoesNotExist:
                break
            if i > 1:
                s = s.rsplit("-", 1)[0]
            s = "%s-%s" % (s, i)    
            i += 1
        return s     

    def get_slug(self):
        return re.sub('[^0-9a-z]+', '-', self.title.lower())



class Ownable(models.Model):
    """
    """
    user = models.ForeignKey(User, verbose_name=_("Owner"),
                   related_name="%(class)ss", 
                   blank=True, null=True) # allow user to be set from request

    class Meta:
        abstract = True

    def is_editable(self, request):
        return request.user.is_superuser or request.user.id == self.user_id

