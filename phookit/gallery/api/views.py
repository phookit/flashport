from django.conf import settings
from django.db.models import Q
from rest_framework import generics
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import pagination

from rest_framework.views import APIView
from rest_framework.response import Response

from serializers import TagSerializer, ImageSerializer
from phookit.gallery.models import Image, Tag


class ImageResultsSetPagination(pagination.PageNumberPagination):
    page_size = settings.PAGINATE_BY
    page_size_query_param = 'count'
    max_page_size = 1000

# TODO: Move into permissions.py
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the owner of the snippet.
        ### return obj.owner == request.user
        return obj.is_editable(request)

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            print "SAFE"
            return True
        # Write permissions are only allowed to admins
        print "IS ADMIN?"
        return request.user.is_staff


class TagList(generics.ListCreateAPIView):
    '''
    Only admins can create new tags
    '''
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAdminOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'

class TagDetail(generics.RetrieveUpdateDestroyAPIView):
    '''
    '''
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'



class ImageList(generics.ListCreateAPIView):
    '''
    '''
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    lookup_field = 'slug'
    pagination_class = ImageResultsSetPagination


    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ImageByTagList(generics.ListAPIView):
    '''
    Given a comma separated list of tags return all images with all those tags.
    e.g. For a tattoo website you may want to retrieve all images that are tagged
    as tribal and chest to get all tribal tattoos on chests. `slugs` should be 
    "tribal,chest"
    '''
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ImageSerializer
    pagination_class = ImageResultsSetPagination

    def get_queryset(self):
        slugs = self.kwargs.get('slugs').split(',')
        images = Image.objects.all()
        # if a tag is 'latest' just ignore it 
        for ts in slugs:
            if ts != 'latest':
                images = images.filter(Q(tag__slug=ts) | Q(other_tags__slug=ts))
        return images


class ImageDetail(generics.RetrieveUpdateDestroyAPIView):
    '''
    '''
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    lookup_field = 'slug'

