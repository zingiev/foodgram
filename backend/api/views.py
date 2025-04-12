from core.constants import URL_PATH_DOWNLOAD_SHOPPING_CART
from core.shopping_list import generate_shopping_list
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Favorite, Ingredients, Recipe, ShoppingCart, Tag
from rest_framework import status, views, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import IngredientsSearchFilter, RecipeFilter
from .mixins import ListRetrieveViewSet, ShoppingFavoriteViewSet
from .pagination import IngredientPagination, TagPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeGetSerializer,
                          ShoppingCartSerializer, TagSerializer)


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']
    permission_classes = [AllowAny]
    pagination_class = TagPagination


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get']
    permission_classes = [AllowAny]
    pagination_class = IngredientPagination
    filter_backends = (IngredientsSearchFilter,)
    search_fields = ('^name', 'name')


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [
        IsAuthorOrReadOnly,
        IsAuthenticatedOrReadOnly
    ]
    http_method_names = ['get', 'post', 'delete', 'patch']
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeGetSerializer

    @action(methods=['GET'],
            detail=False,
            url_path=URL_PATH_DOWNLOAD_SHOPPING_CART,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(
            user=user).select_related('recipe')
        shopping_list = generate_shopping_list(shopping_cart)
        response = HttpResponse(shopping_list,
                                content_type="text/plain; charset=utf-8")
        response['Content-Disposition'] = 'attachment; \
            filename="shopping_list.txt"'
        return response


class FavoriteViewSet(ShoppingFavoriteViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]


class ShoppingCartViewSet(ShoppingFavoriteViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = [IsAuthenticated]


class ShortLinkView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        short_link = f'{settings.SITE_URL}/s/{recipe.short_url}'
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)


class RedirectShortLinkView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request, short_url):
        recipe = get_object_or_404(Recipe, short_url=short_url)
        return redirect(f'{settings.SITE_URL}/recipes/{recipe.id}')
