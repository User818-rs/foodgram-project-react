from django.contrib.auth.models import AbstractUser
from django.db import models

from api.validators import validate_me, validate_symbols_in_fields


class CustomUser(AbstractUser):
    """Модель пользователя"""
    email = models.EmailField(
        verbose_name="Адрес электронной почты",
        max_length=254,
        unique=True
    )
    username = models.CharField(
        verbose_name="Уникальный юзернейм",
        max_length=150,
        unique=True,
        validators=[validate_symbols_in_fields, validate_me]
    )

    first_name = models.CharField(
        verbose_name="Имя",
        max_length=150
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=150
    )
    password = models.CharField(
        verbose_name="Пароль",
        max_length=150
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username", "first_name", "last_name")

    class Meta:
        ordering = ["id"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username[:15]


class Subscription(models.Model):
    """Модель для подписки"""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )

    following = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Подписант",
    )

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(fields=("user", "following"),
                                    name="unique_list")]

    def __str__(self):
        return (f"Подписчик {self.user.username[:15]}"
                f"автора- {self.following.username}")
