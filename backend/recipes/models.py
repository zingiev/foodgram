from core.constants import (MAX_LENGTH_INGREDIENT, MAX_LENGTH_MEASUREMENT_UNIT,
                            MAX_LENGTH_RECIPES, MAX_LENGTH_SHORT_URL,
                            MAX_LENGTH_SLUG, MAX_LENGTH_TAG)
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint
from shortuuid import ShortUUID

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Тег',
        max_length=MAX_LENGTH_TAG,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=MAX_LENGTH_SLUG,
        unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(
        verbose_name='Ингредиент',
        max_length=MAX_LENGTH_INGREDIENT
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_LENGTH_MEASUREMENT_UNIT
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        verbose_name='Автор',
        to=User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH_RECIPES,
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/'
    )
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        verbose_name='Ингредиенты',
        to=Ingredients,
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(verbose_name='Теги', to=Tag)
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True)
    short_url = models.CharField(
        max_length=MAX_LENGTH_SHORT_URL,
        unique=True, blank=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('pub_date',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.short_url:
            self.short_url = ShortUUID().random(length=6).lower()
        super().save(*args, **kwargs)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to=Recipe,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        verbose_name='Ингредиент',
        to=Ingredients,
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        verbose_name='Сумма'
    )

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецептов'

    def __str__(self):
        return self.ingredient.name


class Favorite(models.Model):
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to=Recipe,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('id',)
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite')
        ]

    def __str__(self):
        return self.recipe.name


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to=Recipe,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ('id',)
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart')
        ]

    def __str__(self):
        return self.recipe.name
