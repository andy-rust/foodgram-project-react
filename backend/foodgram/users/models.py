from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import USERNAME_VALIDATOR


class User(AbstractUser):
    '''Кастомная модель юзера
    Поля email, username, first_name, last_name, password обязательны,
    '''
    USER = 'user'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, 'user'),
        (ADMIN, 'admin'),
    ]

    email = models.EmailField(
        'email',
        max_length=254,
        unique=True,
        blank=False
    )
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        blank=False,
        validators=[USERNAME_VALIDATOR]
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True,
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
        blank=False
    )
    role = models.CharField(
        'Роль пользователя',
        max_length=50,
        choices=ROLE_CHOICES,
        default=USER,
        blank=True
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_together',
            )
        ]

    def __str__(self):
        return self.username


class Subscription(models.Model):
    '''Модель подписок'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follow',
        verbose_name='На кого подписываются'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription',
            )
        ]

    def __str__(self):
        return str(self.id)
