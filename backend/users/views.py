from rest_framework import views, status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import User
from .serializers import MyObtainTokenSerializer, ProfileSerializer


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
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


class SingUpViewSet(generics.ListCreateAPIView, viewsets.GenericViewSet):
    """Регистрация пользователя"""

    serializer_class = ProfileSerializer
    permission_classes = [
        AllowAny,
    ]
    queryset = User.objects.all()

    @action(
        detail=False,
        methods=["GET"],
        url_path="me",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def me(self, request):
        """Профайл текущего пользователя."""

        return Response(ProfileSerializer(self.request.user).data)
