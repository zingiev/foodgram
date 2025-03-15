from django.db import models
from django.contrib.auth.models import AbstractUser

from core.constants import MAX_LENGTH_EMAIL

# Create your models here.
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
        upload_to='users/avatar/',
        blank=True, null=True
    )
    
    class Meta:
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
        unique_together = ('user', 'author')
