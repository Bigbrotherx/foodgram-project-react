from django.shortcuts import get_object_or_404
from rest_framework import generics, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.serializers import (
    ChangePasswordSerializer,
    MyObtainTokenSerializer,
    ProfileGetSerializer,
    ProfileSerializer,
    SubscriptionSerializer,
)
from users.models import Follow, User


class ObtainTokenView(views.APIView):
    """Генерирет Acceess_token при получении email и password"""

    serializer_class = MyObtainTokenSerializer
    permission_classes = [
        AllowAny,
    ]

    def post(self, request):
        """Обработка post запроса на получение токена."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"auth_token": serializer.validated_data.get("auth_token")},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteTokenView(views.APIView):
    """Генерирет Acceess_token при получении email и password"""

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        """Обработка post запроса на удаление токена."""
        token = request.auth
        if token:
            token.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(
    generics.ListCreateAPIView,
    generics.RetrieveAPIView,
    viewsets.GenericViewSet,
):
    """Вьюсет профиля пользователя"""

    serializer_class = ProfileSerializer
    permission_classes = [
        AllowAny,
    ]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        """Получение всех пользователей"""
        return User.objects.all()

    @action(
        detail=False,
        methods=["GET"],
        url_path="me",
        permission_classes=[
            IsAuthenticated,
        ],
        pagination_class=LimitOffsetPagination,
    )
    def me(self, request):
        """Профайл текущего пользователя."""

        return Response(
            self.serializer_class(
                self.request.user, context={"request": request}
            ).data
        )

    @action(
        detail=False,
        methods=["POST"],
        url_path="set_password",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def set_password(self, request):
        """Обработка post запроса на изменение пароля"""
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="subscribe",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def subscribe(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        if request.method == "POST":
            serializer = SubscriptionSerializer(
                data={"user": request.user.pk, "author": author.pk}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                ProfileGetSerializer(
                    context={"request": request}, instance=author
                ).data
            )

        instance = get_object_or_404(Follow, author=author, user=request.user)
        deleted = instance.delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["GET"],
        url_path="subscriptions",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def subscriptions(self, request):
        """Получить все подписки пользователя"""
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProfileGetSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        return Response(
            ProfileGetSerializer(
                queryset,
                many=True,
                context={"request": request},
            ).data
        )
