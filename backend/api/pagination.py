from foodgram.constants import PAGE_SIZE
from rest_framework.pagination import PageNumberPagination


class PageSizePagination(PageNumberPagination):
    """Пагинатор с ограничением вывода."""
    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
