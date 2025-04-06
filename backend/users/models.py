from core.constants import MAX_LENGTH_EMAIL
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
        help_text='Обязательно поле. Введите корректный адрес электронно '
                  'почты.'
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='avatars/',
        blank=True, null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.email


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='followers'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        ordering = ('id',)
        unique_together = ('user', 'author')
