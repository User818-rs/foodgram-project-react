from rest_framework.pagination import PageNumberPagination


class PageSizePagination(PageNumberPagination):
    """Пагинатор с ограничением вывода"""
    page_size = 6
    page_size_query_param = 'limit'
