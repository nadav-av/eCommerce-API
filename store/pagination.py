from rest_framework.pagination import PageNumberPagination

class PaginationWrapper(PageNumberPagination):
    page_size = 10