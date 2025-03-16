from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.constants import (
    MAX_LENGTH_TAG,
    MAX_LENGTH_INGREDIENT,
    MAX_LENGTH_MEASUREMENT_UNIT,
    MAX_LENGTH_RECIPES,
    MAX_LENGTH_SLUG
)


User = get_user_model()

# Create your models here.


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Тег',
        max_length=MAX_LENGTH_TAG,
        unique=True
    )
    slug = models.SlugField(
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


class Recipes(models.Model):
    author = models.ForeignKey(
        verbose_name='Автор',
        to=User,
        on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH_RECIPES,
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='media/recipes/'
    )
    text = models.TextField()
    ingredients = models.ManyToManyField(
        to=Ingredients,
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(to=Tag)
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('id',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("get-link", kwargs={"pk": self.pk})


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to=Recipes,
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
