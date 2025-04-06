from api.validators import username_by_path_me, username_by_pattern
from core.decodeimage import Base64ImageField
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Recipe
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from users.models import Subscription

User = get_user_model()


def is_subscribed(request, obj):
    if isinstance(obj, Subscription):
        obj = obj.author
    if not request or not request.user.is_authenticated:
        return False
    return Subscription.objects.filter(
        author=obj, user=request.user).exists()


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
        return is_subscribed(request, obj)


class RecipeMinifiedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSubscribeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='author.email', read_only=True)
    id = serializers.IntegerField(source='author.id', read_only=True)
    username = serializers.CharField(source='author.username', read_only=True)
    first_name = serializers.CharField(
        source='author.first_name', read_only=True)
    last_name = serializers.CharField(
        source='author.last_name', read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.ImageField(source='author.avatar', read_only=True)

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return is_subscribed(request, obj)

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)
        return RecipeMinifiedSerializer(
            recipes, many=True, context=self.context).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class UserAvatarSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=CurrentUserDefault())
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('user', 'avatar')
