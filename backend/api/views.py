from hashlib import md5
from collections import defaultdict

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, views, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated

from .filters import RecipeFilter
from .pagination import TagPagination, IngredientPagination
from .mixins import ShoppingFavoriteViewSet
from core.constants import URL_PATH_DOWNLOAD_SHOPPING_CART
from recipes.models import (
    Tag,
    Recipe,
    Ingredients,
    Favorite,
    ShoppingCart,
    RecipeIngredient
)
from .serializers import (
    TagSerializer,
    RecipeSerializer,
    IngredientSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
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
    filterset_class = RecipeFilter

    @action(methods=['GET'],
            detail=False,
            url_path=URL_PATH_DOWNLOAD_SHOPPING_CART)
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(
            user=user).select_related('recipe')
        ingredients_dict = defaultdict(lambda: {'amount': 0, 'unit': ''})

        for cart_item in shopping_cart:
            recipe = cart_item.recipe
            recipe_ingredients = RecipeIngredient.objects.filter(
                recipe=recipe).select_related('ingredient')
            for recipe_ingredient in recipe_ingredients:
                ingredient = recipe_ingredient.ingredient
                key = ingredient.name
                ingredients_dict[key]['amount'] += recipe_ingredient.amount
                ingredients_dict[key]['unit'] = ingredient.measurement_unit

        shopping_list = "\n".join(
            f"{name} ({data['unit']}) — {data['amount']}"
            for name, data in ingredients_dict.items()
        )

        response = HttpResponse(shopping_list,
                                content_type="text/plain; charset=utf-8")
        response['Content-Disposition'] = 'attachment; \
            filename="shopping_list.txt"'
        return response

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        user = self.request.user
        author = serializer.instance.author
        if user != author:
            raise PermissionDenied('Обновлять этот рецепт может только автор.')
        serializer.save()


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
        short_link = f'{settings.BACKEND_URL}/s/{recipe.short_url}'
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)


class RedirectShortLinkView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request, short_url):
        recipe = get_object_or_404(Recipe, short_url=short_url)
        return redirect(f'{settings.FRONTEND_URL}/recipes/{recipe.id}')
