from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from api.filters import RecipeFilterSet, NameSearchFilter
from api.serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipesGETSerializer,
    RecipeShortSerializer,
    RecipesSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class CustomPaginator(PageNumberPagination):
    """Настройки пагинатора"""

    page_size = 6
    page_size_query_param = "limit"


class TagViewSet(
    generics.ListAPIView, generics.RetrieveAPIView, viewsets.GenericViewSet
):
    """Получение списка и одиночного тега"""

    serializer_class = TagSerializer
    permission_classes = [
        permissions.AllowAny,
    ]
    queryset = Tag.objects.all()


class IngredientViewSet(
    generics.ListAPIView, generics.RetrieveAPIView, viewsets.GenericViewSet
):
    """Получение списка и одиночного ингридиента"""

    serializer_class = IngredientSerializer
    permission_classes = [
        permissions.AllowAny,
    ]
    filter_backends = (
        DjangoFilterBackend,
        NameSearchFilter,
    )
    search_fields = ("^name",)
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    """CRDU для модели Recipe"""

    serializer_class = RecipesSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
    ]
    queryset = Recipe.objects.all()
    pagination_class = CustomPaginator
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("created",)
    filterset_class = RecipeFilterSet
    filterset_fields = (
        "author",
        "tags",
        "is_favorited",
        "is_in_shopping_cart",
    )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipesGETSerializer

        return super().get_serializer_class()

    def perform_create(self, serializer):
        """Добавление пользователя совершившего запрос"""
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="favorite",
        permission_classes=[
            permissions.IsAuthenticated,
        ],
    )
    def favorite(self, request, pk):
        """Добавление рецептов в избранное"""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            serializer = FavoriteSerializer(
                data={"user": request.user.pk, "recipe": recipe.pk}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(RecipeShortSerializer(instance=recipe).data)

        instance = get_object_or_404(
            Favorite, recipe=recipe, user=request.user
        )
        deleted = instance.delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="shopping_cart",
        permission_classes=[
            permissions.IsAuthenticated,
        ],
    )
    def shopping_cart(self, request, pk):
        """Добавление в список покупок"""
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            serializer = ShoppingCartSerializer(
                data={"user": request.user.pk, "recipe": recipe.pk}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(RecipeShortSerializer(instance=recipe).data)

        instance = get_object_or_404(
            ShoppingCart, recipe=recipe, user=request.user
        )
        deleted = instance.delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["GET"],
        url_path="download_shopping_cart",
        permission_classes=[
            permissions.IsAuthenticated,
        ],
    )
    def download_shopping_cart(self, request):
        """Сгенерировать и отдать список покупок"""
        recipes_qs = Recipe.objects.filter(
            cart__user=request.user
        ).prefetch_related("ingredients")
        shopping_dict = {}
        for recipe in recipes_qs:
            for ingredient in recipe.ingredients.all():
                current_dict_key = (
                    f"{ingredient.name}({ingredient.measurement_unit})"
                )
                if current_dict_key not in shopping_dict.keys():
                    shopping_dict[
                        current_dict_key
                    ] = ingredient.ingredient_recipe.get(recipe=recipe).amount
                else:
                    shopping_dict[
                        current_dict_key
                    ] += ingredient.ingredient_recipe.get(recipe=recipe).amount
        content = "\n".join(
            [f"{key} - {value}" for key, value in shopping_dict.items()]
        )
        response = HttpResponse(content, content_type="text/plain")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="Список_покупок.txt"'
        return response
