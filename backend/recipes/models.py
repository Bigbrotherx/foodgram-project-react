from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель тега для рецепта"""

    name = models.CharField("Имя тега", max_length=200)
    color = models.CharField("Цветовой HEX код", max_length=7)
    slug = models.SlugField("Уникальный слаг", unique=True, max_length=200)

    class Meta:
        verbose_name = "тег"
        verbose_name_plural = "теги"
        ordering = ("name",)

    def __str__(self) -> str:
        """Строковое представление модели"""
        return f"{self.name} - {self.slug}"


class Ingredient(models.Model):
    """Модель ингридиента"""

    name = models.CharField("Название ингридиента", max_length=200)
    measurement_unit = models.CharField("Единица измерения", max_length=200)

    class Meta:
        verbose_name = "ингридиент"
        verbose_name_plural = "ингридиенты"
        ordering = ("name",)

    def __str__(self) -> str:
        """Строковое представление модели"""
        return f"{self.name} - {self.measurement_unit}"


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
        upload_to="media/recipes/",
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
        ordering = ("-created",)

    def __str__(self) -> str:
        """Строковое представление модели"""
        return f"Рецепт {self.name} пользователя {self.author}"


class IngredientRecipe(models.Model):
    """Промежуточная модель связи ингридентов и рецептов"""

    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.PROTECT, related_name="ingredient_recipe"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="recipe_ingredient"
    )
    amount = models.PositiveSmallIntegerField("Колличество")

    class Meta:
        verbose_name = "ингредиент в рецепте"
        verbose_name_plural = "ингридиенты в рецепте"
        ordering = ("-recipe__created",)

    def __str__(self) -> str:
        """Строковое представление модели"""
        return (
            f"В {self.recipe.name} использовано "
            f"{self.recipe.recipe_ingredient.count()} ингредиентов"
        )


class ShoppingCart(models.Model):
    """Список покупок"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cart"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="cart"
    )

    class Meta:
        verbose_name = "список покупок"
        verbose_name_plural = "списки покупок"
        ordering = ("-recipe__created",)
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_recipe_cart"
            )
        ]

    def __str__(self) -> str:
        """Строковое представление модели"""
        return f"Корзина пользователя {self.user}"


class Favorite(models.Model):
    """Избранные рецепты"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorite"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorite"
    )

    class Meta:
        verbose_name = "избранный рецепт"
        verbose_name_plural = "избранные рецепты"
        ordering = ("-recipe__created",)
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_recipe_favorite"
            )
        ]

    def __str__(self) -> str:
        """Строковое представление модели"""
        return f"Список избранного пользователя {self.user}"
