from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework import exceptions, serializers

from .models import User
from .validators import UsernameValidator


class MyObtainTokenSerializer(serializers.ModelSerializer):
    """Сериализатор получения токена для зарегистрированного пользователя."""

    class Meta:
        model = User
        fields = ("password", "email")

    def validate(self, data):
        """Валидатор для 'email' и 'password'."""
        user = get_object_or_404(User, email=data.get("email", None))
        authenticate_kwargs = {
            "username": user.username,
            "password": data.get("password", None),
        }
        user = authenticate(**authenticate_kwargs)
        if user is None:
            raise exceptions.ValidationError("Неверный email или пароль!")
        token, created = Token.objects.get_or_create(user=user)
        return {
            "auth_token": str(token),
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
        if User.objects.filter(
            email=data.get("email"), username=data.get("username")
        ).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует!"
            )

        return data

    def create(self, validated_data):
        """Создание и установка пароля пользователя"""
        user = User.objects.create_user(**validated_data)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Сериалайзер смены пароля"""

    new_password = serializers.CharField(max_length=128, required=True)
    current_password = serializers.CharField(max_length=128, required=True)

    def validate_current_password(self, value):
        """Проверка валидности текущего пароля"""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Неверный пароль!")
        return value

    def create(self, validated_data):
        """Смена пароля"""
        user = self.context["request"].user
        new_password = validated_data["new_password"]
        user.set_password(new_password)
        user.save()
        return user
