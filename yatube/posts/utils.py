from django.core.paginator import Paginator

NUMBER_OF_ENTRIES = 10


def numbers_of_page(request, posts):
    paginator = Paginator(posts, NUMBER_OF_ENTRIES)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
