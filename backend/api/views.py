from hashlib import md5

from rest_framework import viewsets, views, status, mixins
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings

from .pagination import TagPagination, IngredientPagination
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
    RecipeFavoritesSerializer,
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


class RecipeFavoritesViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = RecipeFavorites.objects.all()
    serializer_class = RecipeFavoritesSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post', 'delete']

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get('pk')
        user = self.request.user
        recipe = get_object_or_404(Recipes, id=recipe_id)
        favorite = RecipeFavorites.objects.select_related(
            'recipe', 'user'
        ).filter(recipe__id=recipe_id, user__id=user.id).first()
        if favorite is not None:
            raise ValidationError('Такой рецепт уже добавлен в избранное.')
        serializer.save(recipe=recipe, user=user)

    def perform_destroy(self, instance):
        user = self.request.user
        if user != instance.user:
            raise PermissionDenied('Удалять из избранного может только автор.')
        instance.delete()
