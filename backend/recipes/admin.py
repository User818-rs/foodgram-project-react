from django.contrib import admin

from users.models import CustomUser

from .models import FavRecipes, IngredientCount, Ingredient, Recipe, ShoppingList, Tag


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    """Класс настройки раздела пользователей."""

    # list_display = (
    #     *
    # )
    # empty_value_display = 'значение отсутствует'
    # list_editable = ('role',)
    # list_filter = ('username',)
    # search_fields = ('username', 'role')


admin.site.register(IngredientCount, UserAdmin)
admin.site.register(ShoppingList, UserAdmin)
admin.site.register(FavRecipes, UserAdmin)
admin.site.register(Recipe, UserAdmin)
admin.site.register(Tag, UserAdmin)
admin.site.register(Ingredient, UserAdmin)
