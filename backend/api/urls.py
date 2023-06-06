from django.urls import include, path
from rest_framework import routers

from users.views import DeleteTokenView, ObtainTokenView, UsersViewSet

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

app_name = "api"

router_v1 = routers.DefaultRouter()
router_v1.register(r"users", UsersViewSet, basename="users")
router_v1.register(r"tags", TagViewSet, basename="tags")
router_v1.register(r"ingredients", IngredientViewSet, basename="ingredient")
router_v1.register(r"recipes", RecipeViewSet, basename="recipes")


urlpatterns = [
    path("", include(router_v1.urls)),
    path("auth/token/login/", ObtainTokenView.as_view(), name="login"),
    path("auth/token/logout/", DeleteTokenView.as_view(), name="logout"),
]
