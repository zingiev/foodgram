from django.contrib.auth import get_user_model
from djoser.serializers import (
    UserCreateSerializer,
    UserSerializer
)
from rest_framework import serializers

from api.validators import username_by_path_me, username_by_pattern
from users.models import Subscription
from core.decodeimage import Base64ImageField


User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')

    def validate_username(self, username):
        username_by_path_me(username)
        username_by_pattern(username)
        return username


class CustomUserSerialier(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Subscription.objects.filter(
            author=request.user, user=obj).exists()
