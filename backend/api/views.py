from rest_framework import viewsets

from recipes.models import Tag
from .pagination import TagPagination
from .serializers import TagSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']
    pagination_class = TagPagination
