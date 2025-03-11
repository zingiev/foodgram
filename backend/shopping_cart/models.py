from django.db import models
from django.contrib.auth import get_user_model

from recipes.models import Recipes


User = get_user_model()

# Create your models here.
class ShoppingCart(models.Model):
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to=Recipes,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.recipe
