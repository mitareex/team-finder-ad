from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .constants import PROJECTS_PER_PAGE


def paginate_queryset(request, queryset):
    paginator = Paginator(queryset, PROJECTS_PER_PAGE)
    page_number = request.GET.get('page')

    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)
