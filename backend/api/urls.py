from django.urls import path, include
from rest_framework import routers

from .users.views import UserViewSet, APIGetTokenVeiw, LogoutView
from .views import (
    TagViewSet,
    RecipeViewSet,
    IngredientViewSet,
    RecipeShortLinkView
)

app_name = 'api'

v1_router = routers.DefaultRouter()
v1_router.register('users', UserViewSet, basename='users')
v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')
v1_router.register('recipes', RecipeViewSet, basename='recipes')

auth_urlpatterns = [
    path('token/login/', APIGetTokenVeiw.as_view(), name='auth_token'),
    path('token/logout/', LogoutView.as_view(), name='auth_logout'),
]

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include(auth_urlpatterns)),
    path(
        'recipes/<int:id>/get-link/',
        RecipeShortLinkView.as_view(),
        name='get_link'
    )
]
