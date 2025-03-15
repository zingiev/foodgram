from django.db import models
from django.contrib.auth import get_user_model

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
    
    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Ингредиент',
        max_length=MAX_LENGTH_INGREDIENT
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_LENGTH_MEASUREMENT_UNIT
    )
    
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
    ingredient = models.ManyToManyField(
        to=Ingredient,
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(to=Tag)
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления'
    )
    
    def __str__(self):
        return self.name
    

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to=Recipes,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        verbose_name='Ингредиент',
        to=Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        verbose_name='Сумма'
    )
