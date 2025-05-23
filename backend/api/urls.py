from django.urls import include, path
from rest_framework import routers

from .users.views import CustomUserViewSet, UserSubscribeViewSet
from .views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                    ShoppingCartViewSet, ShortLinkView, TagViewSet)

app_name = 'api'

v1_router = routers.DefaultRouter()
v1_router.register('users/subscriptions',
                   UserSubscribeViewSet, basename='user_subscriptions')
v1_router.register('users', CustomUserViewSet, basename='name')
v1_router.register(r'users/(?P<author_id>\d+)/subscribe',
                   UserSubscribeViewSet, basename='user_subscribe')

v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')

v1_router.register('recipes', RecipeViewSet, basename='recipe')

v1_router.register(r'recipes/(?P<recipe_id>\d+)/favorite',
                   FavoriteViewSet, basename='recipe_favorite')

v1_router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
                   ShoppingCartViewSet, basename='recipe_shopping_cart')


urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/<int:recipe_id>/get-link/',
         ShortLinkView.as_view(), name='get_link')
]
