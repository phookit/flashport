
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# use a default page query param if it hasnt been set in settings
_page_query_param = 'page'
if hasattr(settings, 'PAGE_QUERY_PARAM'):
    _page_query_param = settings.PAGE_QUERY_PARAM

def paginate(objs, request, **kwargs):
    paginator = Paginator(objs, settings.PAGINATE_BY)
    # get the page query param, normally defaults to 'page' or
    # whatever value settings.PAGE_QUERY_PARAM is.
    page = request.GET.get(kwargs.get('page_query_param', _page_query_param))
    try:
        objs = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        objs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        objs = paginator.page(paginator.num_pages)
    return objs
