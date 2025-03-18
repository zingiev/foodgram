from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import Subscription
from .serializers import CustomUserSerialier, UserSubscribeSerializer


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerialier
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post']
    permission_classes = [AllowAny]

    def get_queryset(self):
        return self.queryset


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
