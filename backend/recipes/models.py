from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    """Модель тега для рецепта"""

    name = models.CharField("Имя тега", max_length=200)
    color = models.CharField("Цветовой HEX код", max_length=7)
    slug = models.SlugField("Уникальный слаг", unique=True, max_length=200)


class Ingredient(models.Model):
    """Модель ингридиента"""

    name = models.CharField("Название ингридиента", max_length=200)
    measurement_unit = models.CharField("Единица измерения", max_length=200)


class Recipe(models.Model):
    """Модель рецепта"""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="автор рецепта",
    )
    name = models.CharField("Название рецепта", max_length=200)
    image = models.ImageField(
        "Картинка",
        upload_to="recipes/",
        blank=True,
        help_text="Добавьте изображение к рецепту",
    )
    text = models.TextField("Описание рецепта")
    ingredients = models.ManyToManyField(
        Ingredient, through="IngredientRecipe"
    )
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField("Время приготовления в минутах")
    created = models.DateTimeField("дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "рецепт"
        verbose_name_plural = "рецепты"


class IngredientRecipe(models.Model):
    """Промежуточная модель связи ингридентов и рецептов"""

    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.PROTECT, related_name="ingredient_recipe"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="recipe_ingredient"
    )
    amount = models.PositiveSmallIntegerField("Колличество")
