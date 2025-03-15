from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class TagPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return Response(data)
    