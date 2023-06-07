from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    """Кастомный класс модели User"""

    REQUIRED_FIELDS = ["email", "first_name", "last_name", "password"]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["email", "username"],
                name="unique_pair",
            ),
        ]
        ordering = ["username"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return f"Пользователь {self.username}"

    def clean(self) -> None:
        if self.username == "me":
            raise ValidationError(f"Недопустимое имя: {self.username}")
        return super().clean()


class Follow(models.Model):
    """Модель подписки на авторов"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="подписчик",
        help_text="Пользоваетль, который подписывается на автора",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="автор",
        help_text="Автор, на которого подписываются",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_following",
            )
        ]
        verbose_name = "подписка"
        verbose_name_plural = "подписки"
        ordering = ("-author__id",)

    def __str__(self) -> str:
        """Стринг метод"""

        return (
            self.user.get_username() + " follow: " + self.author.get_username()
        )
