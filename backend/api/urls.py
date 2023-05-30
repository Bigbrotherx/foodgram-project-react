from django.urls import path, include
from rest_framework import routers

from users.views import SingUpViewSet, ObtainTokenView

app_name = "api"

router_v1 = routers.DefaultRouter()
router_v1.register(r"users", SingUpViewSet, basename="users")


urlpatterns = [
    path("", include(router_v1.urls)),
    path("auth/token/login/", ObtainTokenView.as_view(), name="login"),
]
