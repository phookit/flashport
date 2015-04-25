from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Image, Tag
from phookit.core.paginator import paginate


def _get_album_tags(images):
    result = []
    for i in images:
        for t in i.other_tags.all():
            if t not in result:
                result.append(t)
    return result


def index(request):
    images = paginate(Image.objects.all(), request)
    tags = Tag.objects.all()

    context = {
        'images': images,
        'tags': tags,
        'album_tags': _get_album_tags(images)
    }
    #    'in_tags': '',
    return render(request, 'gallery/index.html', context)
    
    
def tags(request, tags):
    tag_objs = Tag.objects.all()
    images = Image.objects.all()

    t = tags.split(',')
    for c in t:
        images = images.filter(Q(tag__slug=c) | Q(other_tags__slug=c))
    # paginate results    
    images = paginate(images, request)

    context = {
        'images': images,
        'in_tags': tags,
        'tags': tag_objs,
        'album_tags': _get_album_tags(images)
    }
    return render(request, 'gallery/index.html', context)
    
    
def image(request, image_slug, tags=None):
    image = get_object_or_404(Image, slug=image_slug)
    tag_objs = Tag.objects.all()
    images = Image.objects.all()
    if tags:
        t = tags.split(',')
        for c in t:
            images = images.filter(Q(tag__slug=c) | Q(other_tags__slug=c))
        # paginate results    
        images = paginate(images, request)

    context = {
        'image': image,
        'images': images,
        'in_tags': tags,
        'tags': tag_objs,
        'album_tags': _get_album_tags(images)
    }
    return render(request, 'gallery/image.html', context)


