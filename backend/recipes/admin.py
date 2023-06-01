from django.contrib import admin

from .models import Recipe, Ingredient, Tag, IngredientRecipe


class IngredientInline(admin.TabularInline):
    """
    Инлайн для отображения ManyToMany поля ingredients в админ-модели Recipes.
    """

    model = IngredientRecipe
    extra = 1


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
    )
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "-пусто-"


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


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
