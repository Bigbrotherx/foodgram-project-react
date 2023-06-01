from rest_framework import viewsets, generics
from rest_framework import permissions
from .serializers import (
    TagSerializer,
    RecipesGETSerializer,
    RecipesSerializer,
    IngredientSerializer,
)
from recipes.models import Tag, Recipe, Ingredient


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
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    """CRDU для модели Recipe"""

    serializer_class = RecipesSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipesGETSerializer

        return super().get_serializer_class()

    def perform_create(self, serializer):
        """Добавление пользователя совершившего запрос"""
        serializer.save(author=self.request.user)
