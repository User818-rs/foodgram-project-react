from django.contrib import admin

from .models import CustomUser, Subscription


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    """
    Настройка интерфейса администрирования пользователей
    в панели администратора Django.
    """
    list_display = ('id', 'username', 'first_name',
                    'last_name', 'email', 'password',)
    list_filter = ['email', 'username']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Настройка интерфейса администрирования подписок
    в панели администратора Django.
    """
    list_display = ('user', 'following')
    list_filter = ['user', 'following']
