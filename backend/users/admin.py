from django.contrib import admin

from users.models import Follow, User


class UserAdmin(admin.ModelAdmin):
    """
    Админ-модель для модели User.
    """

    list_display = (
        "id",
        "username",
        "email",
    )
    search_fields = ("username", "email")
    list_filter = ("username", "email")
    empty_value_display = "-пусто-"


class FollowAdmin(admin.ModelAdmin):
    """
    Админ-модель для модели Follow.
    """

    list_display = (
        "id",
        "user",
        "author",
    )
    search_fields = ("user", "author")
    list_filter = ("user", "author")
    empty_value_display = "-пусто-"


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
