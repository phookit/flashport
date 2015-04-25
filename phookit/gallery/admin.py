from django.contrib import admin
from phookit.core.admin import OwnableAdmin
from models import Image, Tag


class ImageAdmin(OwnableAdmin):
    def save_form(self, request, form, change):
        # save the logged in user as owner if it was not selected in the admin page
        OwnableAdmin.save_form(self, request, form, change)
        return super(ImageAdmin, self).save_form(request, form, change)



admin.site.register(Image, ImageAdmin)
admin.site.register(Tag)

