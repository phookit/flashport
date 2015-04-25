from django.conf.urls import patterns, include, url
import views as api_views

urlpatterns = patterns('',
    url(r'^tags/$', api_views.TagList.as_view(), name='tag-list'),
    url(r'^tags/(?P<slug>[0-9a-zA-z\-]+)/$', api_views.TagDetail.as_view(), name='tag-detail'),
    url(r'^images/$', api_views.ImageList.as_view(), name='image-list'),
    url(r'^images/(?P<slug>[0-9a-zA-z\-]+)/$', api_views.ImageDetail.as_view(), name='image-detail'),
    url(r'^images/t/(?P<slugs>[0-9a-zA-z\-,]+)/$', api_views.ImageByTagList.as_view(), name='image-by-tag-list'),
)

