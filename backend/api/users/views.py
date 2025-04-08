from core.constants import URL_PATH_AVATAR, URL_PATH_ME
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription

from .serializers import (CustomUserSerialier, UserAvatarSerializer,
                          UserSubscribeSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerialier
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [AllowAny]

    def get_queryset(self):
        return self.queryset

    @action(methods=['get'], detail=False, url_path=URL_PATH_ME)
    def me(self, request, *args, **kwargs):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "Вы не авторизованы"}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

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
        if not request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserSubscribeViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = UserSubscribeSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']
    pagination_class = LimitOffsetPagination

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
        if request.user == author:
            return Response({'errors': 'Нельзя подписаться на себя'}, status=400)
        if subscribe:
            return Response({'errors': 'Уже подписан'}, status=400)

        subscription = Subscription.objects.create(author=author, user=request.user)
        serializer = self.get_serializer(
            subscription, context=self.get_serializer_context()
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        # author, subscribe = self.get_subscribe(request, kwargs)
        # if not subscribe.exists() and author != request.user:
        #     author = subscribe.create(author=author, user=request.user)
        #     serializer = self.get_serializer(
        #         subscribe, context=self.get_serializer_context()
        #     )
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        author, subscribe = self.get_subscribe(request, kwargs)
        if subscribe.exists():
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
