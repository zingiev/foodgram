from hashlib import md5

from rest_framework import viewsets, views, status, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from .filters import RecipeFilter

from .pagination import TagPagination, IngredientPagination
from .mixins import ShoppingFavoriteViewSet
from recipes.models import (
    Tag,
    Recipe,
    Ingredients,
    ShortLink,
    Favorite,
    ShoppingCart
)
from .serializers import (
    TagSerializer,
    RecipeSerializer,
    IngredientSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer
)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']
    permission_classes = [AllowAny]
    pagination_class = TagPagination


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get']
    permission_classes = [AllowAny]
    pagination_class = IngredientPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name', 'name')


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get', 'post', 'delete', 'patch']
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author', 'tags')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        user = self.request.user
        author = serializer.instance.author
        if user != author:
            raise PermissionDenied('Обновлять этот рецепт может только автор.')
        serializer.save()


class ShortLinkView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):
        recipe = Recipe.objects.filter(id=id).first()
        if not recipe:
            return Response(
                {'detail': 'Страница не найдена.'},
                status=status.HTTP_404_NOT_FOUND
            )
        unique_string = f'recipe-{recipe.id}'
        short_hash = md5(unique_string.encode()).hexdigest()[:6]
        short_code = ShortLink.objects.get_or_create(
            recipe=recipe, short_code=short_hash
        )[0].short_code
        short_link = f'{settings.SITE_URL}/s/{short_code}'
        return Response({'short-link': short_link})


class ShortLinkView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request, short_code):
        short_link = get_object_or_404(ShortLink, short_code=short_code)
        return redirect(f'{settings.SITE_URL}/api/recipes/{short_link.recipe.id}')


class FavoriteViewSet(ShoppingFavoriteViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]


class ShoppingCartViewSet(ShoppingFavoriteViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = [IsAuthenticated]
