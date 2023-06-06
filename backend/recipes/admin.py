from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


class IngredientInline(admin.TabularInline):
    """
    Инлайн для отображения ManyToMany поля ingredients в админ-модели Recipes.
    """

    model = IngredientRecipe
    extra = 1
    verbose_name_plural = "Ингридиенты использованные в рецепте"


class RecipeAdmin(admin.ModelAdmin):
    """
    Админ-модель для модели Category.
    """

    inlines = [
        IngredientInline,
    ]
    list_display = (
        "id",
        "author",
        "name",
        "image",
        "text",
        "cooking_time",
        "added_to_favorite_times",
    )
    filter_horizontal = ("tags",)
    search_fields = ("name", "author", "tags")
    list_filter = ("name", "author", "tags")
    empty_value_display = "-пусто-"

    def added_to_favorite_times(self, obj):
        """Общее число раз рецепт добавлен в избраное"""
        return obj.favorite.all().count()

    added_to_favorite_times.short_description = (
        "Рецепт добавлен в избранное раз"
    )


class TagAdmin(admin.ModelAdmin):
    """
    Админ-модель для модели Tag.
    """

    list_display = ("id", "name", "color", "slug")
    search_fields = ("name", "color", "slug")
    list_filter = ("name", "color", "slug")
    empty_value_display = "-пусто-"


class IngredientAdmin(admin.ModelAdmin):
    """
    Админ-модель для модели Ingredient
    """

    list_display = ("id", "name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("name", "measurement_unit")
    empty_value_display = "-пусто-"


class FavoriteAdmin(admin.ModelAdmin):
    """
    Админ-модель для модели Faivorite
    """

    list_display = ("id", "user", "recipe")
    search_fields = ("user", "recipe")
    list_filter = ("user", "recipe")
    empty_value_display = "-пусто-"


class CartAdmin(admin.ModelAdmin):
    """
    Админ-модель для модели Cart
    """

    list_display = ("id", "user", "recipe")
    search_fields = ("user", "recipe")
    list_filter = ("user", "recipe")
    empty_value_display = "-пусто-"


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ShoppingCart, CartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
