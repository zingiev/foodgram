from core.decodeimage import Base64ImageField
from django.contrib.auth import get_user_model
from recipes.models import (Favorite, Ingredients, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from users.models import Subscription

from .validators import slug_by_pattern

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Subscription.objects.filter(
            author=request.user, user=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')

    def validate_slug(self, value):
        slug_by_pattern(value)
        return value


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(),
        source='ingredient.id'
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipeingredient_set'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorite_set.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.shoppingcart_set.filter(user=request.user).exists()
        return False

    def validate(self, data):
        request = self.context.get('request')
        tags = request.data.get('tags')
        ingredients = request.data.get('ingredients')
        cooking_time = data.get('cooking_time')

        if not tags:
            raise serializers.ValidationError({'tags': 'Не указаны теги'})
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты не добавлены'})
        if cooking_time is not None and int(cooking_time) < 1:
            raise serializers.ValidationError(
                {'cooking_time': 'Время приготовления указано неверно'}
            )

        # Проверка тегов
        existing_tag_ids = set(Tag.objects.values_list('id', flat=True))
        tag_ids = []
        for tag_id in tags:
            if int(tag_id) not in existing_tag_ids:
                raise serializers.ValidationError(
                    {'tags': f'Тег с id={tag_id} не существует'})
            if tag_id in tag_ids:
                raise serializers.ValidationError(
                    {'tags': 'Теги не должны повторяться'})
            tag_ids.append(tag_id)

        # Проверка ингредиентов
        ingredient_ids = []
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount')
            if int(amount) < 1:
                raise serializers.ValidationError(
                    {'ingredients': 'Количество должно быть >= 1'})
            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError(
                    {'ingredients': 'Ингредиенты не должны повторяться'})
            ingredient_ids.append(ingredient_id)

        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('recipeingredient_set')
        tags = self.context['request'].data.get('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['ingredient']['id'],
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipeingredient_set', None)
        tags = self.context['request'].data.get('tags')

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)

        if tags:
            instance.tags.set(tags)

        if ingredients:
            instance.recipeingredient_set.all().delete()
            for ingredient in ingredients:
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient['ingredient']['id'],
                    amount=ingredient['amount']
                )
        instance.save()
        return instance


class RecipeMinifiedSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=CurrentUserDefault())
    name = serializers.ReadOnlyField(source='recipe.name')
    id = serializers.ReadOnlyField(source='recipe.id')
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')


class FavoriteSerializer(RecipeMinifiedSerializer):
    class Meta:
        model = Favorite
        fields = ('id', 'user', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(RecipeMinifiedSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'name', 'image', 'cooking_time')


class ShortLinkSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='recipe-detail', lookup_field='id'
    )

    class Meta:
        model = Recipe
        fields = ('url',)
