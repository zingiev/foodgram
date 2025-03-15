from django.urls import path, include
from rest_framework import routers

from .users.views import UserViewSet, APIGetTokenVeiw, LogoutView
from .views import TagViewSet

app_name = 'api'

v1_router = routers.DefaultRouter()
v1_router.register('users', UserViewSet, basename='users')
v1_router.register('tags', TagViewSet, basename='tags')

auth_urlpatterns = [
    path('token/login/', APIGetTokenVeiw.as_view(), name='auth_token'),
    path('token/logout/', LogoutView.as_view(), name='auth_logout'),
]

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include(auth_urlpatterns))
]
