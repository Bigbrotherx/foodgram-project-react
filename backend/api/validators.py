from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from rest_framework import serializers
from rest_framework.validators import ValidationError

from users.models import User


class UsernameValidator(UnicodeUsernameValidator):
    def __call__(self, value) -> None:
        if value == "me":
            raise ValidationError(f"Недопустимое имя: {value}")
        return super().__call__(value)


def check_unique_email_and_name(data):
    queryset = User.objects.filter(
        models.Q(email=data.get("email", ""))
        | models.Q(username=data.get("username"))
    )
    if queryset.exists():
        raise serializers.ValidationError(
            "Имя и email должны быть уникальными!"
        )
