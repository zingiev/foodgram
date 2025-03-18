from hashlib import md5

from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings

from .pagination import TagPagination, IngredientPagination
from core.constants import URL_PATH_FAVORITE
from recipes.models import (
    Tag,
    Recipes,
    Ingredients,
    ShortLink,
    RecipeFavorites
)
from .serializers import (
    TagSerializer,
    RecipeSerializer,
    IngredientSerializer,
    RecipeFavoriteSerializer,
)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']
    permission_classes = (AllowAny,)
    pagination_class = TagPagination


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get']
    permission_classes = (AllowAny,)
    pagination_class = IngredientPagination


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)
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

    # @action(methods=['post'], detail=True, url_path=URL_PATH_FAVORITE)
    # def add_to_favorite(self, request, pk):
    #     recipe = get_object_or_404(Recipes, pk=pk)
    #     favorite, created = RecipeFavorites.objects.get_or_create(
    #         user=request.user,
    #         recipe=recipe
    #     )
    #     if created:
    #         return Response(
    #             'Рецепт добавлен в избранное',
    #             status=status.HTTP_200_OK
    #         )
    #     return Response(
    #         'Рецепт уже в избранном',
    #         status=status.HTTP_400_BAD_REQUEST
    #     )

    # @action(methods=['delete'], detail=True, url_path=URL_PATH_FAVORITE)
    # def delete_from_favorite(self, request, pk):
    #     recipe = get_object_or_404(Recipes, pk=pk)
    #     favorite = RecipeFavorites.objects.filter(
    #         user=request.user,
    #         recipe=recipe
    #     )
    #     if favorite.exists():
    #         favorite.delete()
    #         return Response(
    #             'Рецепт удален из избранного',
    #             status=status.HTTP_204_NO_CONTENT
    #         )
    #     return Response(
    #         'Рецепт не найден в избранном',
    #         status=status.HTTP_404_NOT_FOUND
    #     )


class RecipeShortLinkView(views.APIView):
    def get(self, request, id):
        recipe = Recipes.objects.filter(id=id).first()
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


class RedirectRecipeShortLinkView(views.APIView):
    def get(self, request, short_code):
        short_link = get_object_or_404(ShortLink, short_code=short_code)
        return redirect(f'{settings.SITE_URL}/api/recipes/{short_link.recipe.id}')


class RecipeFavoriteViewSet(viewsets.ModelViewSet):
    queryset = RecipeFavorites.objects.select_related('recipe')
    serializer_class = RecipeFavoriteSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'delete']

    def create(self, *args, **kwargs):
        recipe_id = kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipes, pk=recipe_id)
        favorite, created = RecipeFavorites.objects.get_or_create(
            user=self.request.user,
            recipe=recipe
        )
        if created:
            return Response(
                'Рецепт добавлен в избранное',
                status=status.HTTP_201_CREATED
            )
        return Response(
            'Рецепт уже в избранном',
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, *args, **kwargs):
        recipe_id = kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipes, pk=recipe_id)
        favorite = RecipeFavorites.objects.filter(
            user=self.request.user,
            recipe=recipe
        )
        if favorite.exists():
            favorite.delete()
            return Response(
                'Рецепт успешно удален из избранного',
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            'Рецепт не найден в избранном',
            status=status.HTTP_400_BAD_REQUEST
        )
