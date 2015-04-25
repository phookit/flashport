from django.contrib import admin
from mezzanine.core.admin import SingletonAdmin
from models import SitewideContent


admin.site.register(SitewideContent, SingletonAdmin)

