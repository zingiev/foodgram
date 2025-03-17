from django.urls import path, include
from rest_framework import routers

from .users.views import CustomUserViewSet


app_name = 'api'

v1_router = routers.DefaultRouter()
v1_router.register('users', CustomUserViewSet, basename='name')


urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
