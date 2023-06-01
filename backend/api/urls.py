from django.urls import path, include
from rest_framework import routers

from users.views import SingUpViewSet, ObtainTokenView, DeleteTokenView
from .views import TagViewSet, RecipeViewSet, IngredientViewSet

app_name = "api"

router_v1 = routers.DefaultRouter()
router_v1.register(r"users", SingUpViewSet, basename="users")
router_v1.register(r"tags", TagViewSet, basename="tags")
router_v1.register(r"ingredients", IngredientViewSet, basename="ingredient")
router_v1.register(r"recipes", RecipeViewSet, basename="recipes")


urlpatterns = [
    path("", include(router_v1.urls)),
    path("auth/token/login/", ObtainTokenView.as_view(), name="login"),
    path("auth/token/logout/", DeleteTokenView.as_view(), name="logout"),
]
