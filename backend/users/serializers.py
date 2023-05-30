from django.contrib.auth import authenticate
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, validators, serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .validators import UsernameValidator


class MyObtainTokenSerializer(serializers.ModelSerializer):
    """Сериализатор получения токена для зарегистрированного пользователя."""

    class Meta:
        model = User
        fields = ("password", "email")

    def validate(self, data):
        """Валидатор для 'email' и 'password'."""
        user = get_object_or_404(User, email=data["email"])
        authenticate_kwargs = {
            "username": user.username,
            "password": data["password"],
        }
        user = authenticate(**authenticate_kwargs)
        if user is None:
            raise exceptions.ValidationError("Неверный email или пароль!")
        refresh = RefreshToken.for_user(user)
        return {
            "auth_token": str(refresh.access_token),
        }


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
            "is_subscribed",
        )
        read_only_fields = ("id", "is_subscribed")
        extra_kwargs = {
            "username": {
                "validators": [
                    UsernameValidator(),
                ],
            },
            "password": {
                "write_only": True,
            },
        }
        model = User

    def get_is_subscribed(self, obj):
        """Проверка есть ли подписка"""
        return False

    def validate(self, data):
        """Проверка уникальности username и email"""
        if User.objects.filter(email="email", username="username").exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже сужествует!"
            )
        return data

    def create(self, validated_data):
        """Если пользователь уже создан взять существующего."""
        return User.objects.get_or_create(**validated_data)
