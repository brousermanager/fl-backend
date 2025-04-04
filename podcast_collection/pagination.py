from rest_framework.pagination import PageNumberPagination


class PodcastCollectionPagination(PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = "page_size"
    max_page_size = 100
