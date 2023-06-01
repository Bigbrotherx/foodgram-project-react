import base64

from rest_framework import exceptions, serializers
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

from recipes.models import Tag, Recipe, Ingredient, IngredientRecipe
from users.serializers import ProfileSerializer


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

    image = Base64ImageField(required=True)
    ingredients = IngredientRecipeSerializer(
        many=True, source="recipe_ingredient.all"
    )
    author = ProfileSerializer(read_only=True)
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
        return False

    def get_is_favorited(self, obj):
        """Находится ли в списке избранного"""
        return False


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

    def create(self, validated_data):
        """Создание нового рецепта"""
        ingredients = validated_data.pop("recipe_ingredient")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for elem in ingredients.get("all"):
            ingredient = get_object_or_404(
                Ingredient, pk=elem.get("ingredient").get("id")
            )
            IngredientRecipe.objects.create(
                recipe=recipe, ingredient=ingredient, amount=elem.get("amount")
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
        IngredientRecipe.objects.filter(recipe=instance).delete()
        instance.tags.set(tags)
        instance.save()
        for elem in ingredients.get("all"):
            ingredient = get_object_or_404(
                Ingredient, pk=elem.get("ingredient").get("id")
            )
            IngredientRecipe.objects.create(
                recipe=instance,
                ingredient=ingredient,
                amount=elem.get("amount"),
            )
        return instance

    def to_representation(self, instance):
        """Представление объекта после создания/изменения"""
        representation = RecipesGETSerializer(instance=instance)
        return representation.data
