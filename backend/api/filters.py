from django_filters import (
    TypedChoiceFilter,
    FilterSet,
    NumberFilter,
    ModelMultipleChoiceFilter,
)
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


BOOLEAN_CHOICES = (
    ("0", False),
    ("1", True),
)


class RecipeFilterSet(FilterSet):
    """Фильтр рецептов API"""

    is_favorited = TypedChoiceFilter(
        field_name="is_favorited",
        method="get_is_favorited",
        choices=BOOLEAN_CHOICES,
    )
    is_in_shopping_cart = TypedChoiceFilter(
        field_name="is_in_shopping_cart",
        method="get_is_in_shopping_cart",
        choices=BOOLEAN_CHOICES,
    )
    author = NumberFilter(field_name="author")

    tags = ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = (
            "is_favorited",
            "is_in_shopping_cart",
            "author",
            "tags",
        )

    def get_is_favorited(self, queryset, field_name, value):
        """Поиск рецептов добавленных в избранное"""
        if value:
            user = self.request.user
            if user.is_authenticated:
                queryset = queryset.filter(favorite__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, field_name, value):
        """Поиск рецептов добавленных в список поупок"""
        if value:
            user = self.request.user
            if user.is_authenticated:
                queryset = queryset.filter(cart__user=user)
        return queryset


class NameSearchFilter(SearchFilter):
    """Поисковый фильтр по ключевому слову 'name'"""

    search_param = "name"
