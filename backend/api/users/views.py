from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action

from core.constants import URL_PATH_AVATAR
from users.models import Subscription
from .serializers import (
    CustomUserSerialier,
    UserSubscribeSerializer,
    UserAvatarSerializer
)


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerialier
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [AllowAny]

    def get_queryset(self):
        return self.queryset

    @action(methods=['put', 'delete'], detail=False,
            url_path=URL_PATH_AVATAR)
    def avatar(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if request.method == 'DELETE':
            user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = UserAvatarSerializer(
            user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserSubscribeViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = UserSubscribeSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @staticmethod
    def get_subscribe(request, kwargs):
        author_id = kwargs.get('author_id')
        author = get_object_or_404(User, pk=author_id)
        subscribe = Subscription.objects.filter(
            author=author, user=request.user)
        return (author, subscribe)

    def create(self, request, **kwargs):
        author, subscribe = self.get_subscribe(request, kwargs)
        if not subscribe.exists() and author != request.user:
            subscribe.create(author=author, user=request.user)
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        author, subscribe = self.get_subscribe(request, kwargs)
        if subscribe.exists():
            subscribe.delete()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
