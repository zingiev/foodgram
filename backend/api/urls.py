from django.urls import path, include
from rest_framework import routers

from .views import (
    TagViewSet,
    RecipeViewSet,
    IngredientViewSet,
    RecipeShortLinkView,
    RecipeFavoriteViewSet
)
from .users.views import CustomUserViewSet


app_name = 'api'

v1_router = routers.DefaultRouter()
v1_router.register('users', CustomUserViewSet, basename='name')
v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')
v1_router.register('recipes', RecipeViewSet, basename='recipes')
v1_router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    RecipeFavoriteViewSet,
    basename='recipe_favorite'
)



urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'recipes/<int:id>/get-link/',
        RecipeShortLinkView.as_view(),
        name='get_link'
    )
]
