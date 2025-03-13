from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api.validators import username_by_path_me, username_by_pattern
from users.models import Subscription


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'avatar', 'is_subscribed'
        )

    def validate_username(self, username):
        # Проверяем, что имя пользователя не равно "me"
        username_by_path_me(username)

        # Проверка валидности username по паттерну
        username_by_pattern(username)
        return username

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Subscription.objects.filter(
            author=request.user, user=obj).exists()


class GetTokenSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'password')

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = get_object_or_404(User, email=email)
        if user.email != email and user.check_password(password):
            raise serializers.ValidationError(
                {'error': 'Неверный email или пароль'}
            )
        return data
