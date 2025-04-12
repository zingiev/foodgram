from core.decodeimage import Base64ImageField
from django.contrib.auth import get_user_model
from recipes.models import (Favorite, Ingredients, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault
from rest_framework.validators import UniqueTogetherValidator

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user.subscriptions.filter(author=obj).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


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

    def validate_amount(self, value):
        if value < 1:
            raise ValidationError(
                {'amount': 'Количество не может быть меншья одного'}
            )
        return value


class RecipeGetSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    tags = TagSerializer(many=True)
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
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.favorites.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.shopping_carts.filter(user=user).exists()
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipeingredient_set'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError('Не указаны теги')
        existing_tag_ids = set(Tag.objects.values_list('id', flat=True))
        tag_ids = []
        for tag in tags:
            if int(tag.id) not in existing_tag_ids:
                raise serializers.ValidationError(
                    f'Тег с id={tag.id} не существует')
            if tag.id in tag_ids:
                raise serializers.ValidationError(
                    'Теги не должны повторяться')
            tag_ids.append(tag.id)
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError('Ингредиенты не добавлены')
        ingredient_ids = []
        for ingredient in ingredients:
            ingredient_id = ingredient['ingredient']['id']
            amount = ingredient.get('amount')
            if int(amount) < 1:
                raise serializers.ValidationError(
                    'Количество должно быть >= 1')
            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться')
            ingredient_ids.append(ingredient_id)
        return ingredients

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredients_to_create = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient']['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(ingredients_to_create)

    def create(self, validated_data):
        user = self.context.get('request').user
        ingredients = validated_data.pop('recipeingredient_set', None)
        tags = validated_data.pop('tags', None)
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipeingredient_set', None)
        tags = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)
        if not tags:
            raise ValidationError({'tags': 'Не указаны теги'})
        if not ingredients:
            raise ValidationError({'ingredients': 'Ингредиенты не добавлены'})
        instance.tags.set(tags)
        instance.recipeingredient_set.all().delete()
        self.create_ingredients(instance, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeGetSerializer(
            instance, context={'request': request}).data


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
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('name', 'recipe'),
                message='Рецепт уже добавлен в избранное.'
            )
        ]


class ShoppingCartSerializer(RecipeMinifiedSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'name', 'image', 'cooking_time')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('name', 'recipe'),
                message='Рецепт уже добавлен в корзину.'
            )
        ]


class ShortLinkSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='recipe-detail', lookup_field='id'
    )

    class Meta:
        model = Recipe
        fields = ('url',)
