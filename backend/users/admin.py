from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Subscription


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Настройка интерфейса администрирования пользователей
    в панели администратора Django.
    """

    list_display = ("id", "username", "first_name",
                    "last_name", "email", "password",)
    list_display_links = ("username",)
    search_fields = ("username", "first_name",
                     "last_name", "email",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Настройка интерфейса администрирования подписок
    в панели администратора Django.
    """

    list_display = ("user", "following")
    list_filter = ("user", "following")
    list_display_links = ("user",)
    search_fields = ("user", )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user", "following")
