from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied

from recipes.models import Tag, Recipes, Ingredients
from .pagination import TagPagination, IngredientPagination
from .serializers import (
    TagSerializer,
    RecipeSerializer,
    IngredientSerializer
)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']
    pagination_class = TagPagination
    

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get']
    pagination_class = IngredientPagination


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ['get', 'post', 'delete', 'patch']
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        user = self.request.user
        author = serializer.instance.author
        if user != author:
            raise PermissionDenied('Обновлять этот рецепт может только автор.')
        serializer.save()
