import base64

from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, serializers
from rest_framework.authtoken.models import Token

from api.validators import UsernameValidator
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import Follow, User


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя."""

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
        """Подписан ли на пользователя"""
        user = self.context.get("request").user
        if user.is_authenticated:
            return user.follower.filter(author=obj).exists()

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

        return User.objects.create_user(**validated_data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов"""

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )
        read_only_fields = (
            "name",
            "color",
            "slug",
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингридиентов"""

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )
        read_only_fields = (
            "name",
            "measurement_unit",
        )


class Base64ImageField(serializers.ImageField):
    """Поле сериализатора Base64 кодировка изображения"""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер промежуточной таблицы рецепта и ингридиентов"""

    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class RecipesGETSerializer(serializers.ModelSerializer):
    """GET Сериалайзер рецептов"""

    image = Base64ImageField(required=True, use_url=False)
    ingredients = IngredientRecipeSerializer(
        many=True, source="recipe_ingredient.all"
    )
    author = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = (
            "id",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_is_in_shopping_cart(self, obj):
        """Находится ли в списке покупок"""
        user = self.context.get("request").user
        if user.is_authenticated:
            return user.cart.exists()
        return False

    def get_is_favorited(self, obj):
        """Находится ли в списке избранного"""
        user = self.context.get("request").user
        if user.is_authenticated:
            return user.favorite.exists()
        return False

    def get_author(self, obj):
        """Передача контекста в сериализатор профиля"""
        return ProfileSerializer(
            instance=obj.author, read_only=True, context=self.context
        ).data


class RecipesSerializer(serializers.ModelSerializer):
    """Сериалайзер рецептов"""

    image = Base64ImageField(required=True)
    ingredients = IngredientRecipeSerializer(
        many=True, source="recipe_ingredient.all"
    )
    author = ProfileSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def validate_ingredients(self, value):
        """Валидация тегов"""
        for val in value:
            if not Ingredient.objects.filter(
                pk=val.get("ingredient").get("id")
            ).exists():
                raise serializers.ValidationError(
                    "Передан несуществующий ингредиент!"
                )

        return value

    def ingredient_recipe_bulk_create(self, recipe, ingredients):
        """Метод множественного создания связи ингрииентов с рецептом"""
        IngredientRecipe.objects.bulk_create(
            [
                IngredientRecipe(
                    recipe=recipe,
                    ingredient=get_object_or_404(
                        Ingredient, pk=elem.get("ingredient").get("id")
                    ),
                    amount=elem.get("amount"),
                )
                for elem in ingredients.get("all")
            ]
        )

    def create(self, validated_data):
        """Создание нового рецепта"""
        ingredients = validated_data.pop("recipe_ingredient")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.ingredient_recipe_bulk_create(
            recipe=recipe, ingredients=ingredients
        )
        return recipe

    def update(self, instance, validated_data):
        """Обновление существующего рецепта"""
        ingredients = validated_data.pop("recipe_ingredient")
        tags = validated_data.pop("tags")

        instance.image = validated_data.get("image", instance.image)
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        instance.recipe_ingredient.all().delete()
        instance.tags.set(tags)
        instance.save()
        self.ingredient_recipe_bulk_create(
            recipe=instance, ingredients=ingredients
        )
        return instance

    def to_representation(self, instance):
        """Представление объекта после создания/изменения"""
        representation = RecipesGETSerializer(
            instance=instance, context=self.context
        )
        return representation.data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Короткий сериалайзер рецепта"""

    image = Base64ImageField(read_only=True)

    class Meta:
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("id", "name", "image", "cooking_time")
        model = Recipe


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериалайзер избранного"""

    class Meta:
        fields = (
            "id",
            "user",
            "recipe",
        )
        write_only_fields = (
            "user",
            "recipe",
        )
        model = Favorite
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=("user", "recipe"),
                message="Вы уже добавили этот рецепт",
            ),
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериалайзер списка покупок"""

    class Meta:
        fields = (
            "id",
            "user",
            "recipe",
        )
        write_only_fields = (
            "user",
            "recipe",
        )
        model = ShoppingCart
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=("user", "recipe"),
                message="Вы уже добавили этот рецепт",
            ),
        ]


class ProfileGetSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя с рецептами доступен только на чтение"""

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = RecipeShortSerializer(read_only=True, many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        read_only_fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        model = User

    def get_recipes_count(self, obj):
        """Кол-во рецептов пользователя"""
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        """Подписан ли на пользователя"""
        user = self.context["request"].user
        if user.is_authenticated:
            return user.follower.filter(author=obj).exists()

        return False


class ObtainTokenSerializer(serializers.ModelSerializer):
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


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериалайзер подписок"""

    class Meta:
        fields = (
            "id",
            "user",
            "author",
        )
        write_only_fields = (
            "user",
            "author",
        )
        model = Follow
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=("user", "author"),
                message="Вы уже подписанны на этого пользователя",
            ),
        ]

    def validate(self, data):
        """Валидация само-подписки"""
        if data["user"] == data["author"]:
            raise serializers.ValidationError(
                "Нельзя подписаться на самого себя!"
            )

        return data
