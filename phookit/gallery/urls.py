
from django.conf.urls import patterns, url

import views


urlpatterns = patterns('',
    url(r'^gallery/$', views.index, name='gallery-index'),
    url(r'^gallery/(?P<tags>[0-9A-Za-z\-,]+)/$', views.tags, name='gallery-tags'),
    url(r'^gallery/i/(?P<image_slug>[0-9A-Za-z\-]+)/(?P<tags>[0-9A-Za-z\-,]*)$', views.image, name='gallery-image'),
    url(r'^gallery/i/(?P<image_slug>[0-9A-Za-z\-]+)(?:/(?P<tags>[0-9A-Za-z\-,])*)$', views.image, name='gallery-image'),
)

