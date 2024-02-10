from django.contrib import admin

from .models import (
    FavoriteRecipe,
    Ingredient,
    IngredientCount,
    Recipe,
    RecipeTag,
    ShoppingList,
    Tag,
)


class IngredientCountInline(admin.TabularInline):
    """
    Встроенный инлайн-объект администрирования ингредиентов в рецепте.
    Позволяет управлять связями между ингредиентами и рецептами в админ-панели.
    """

    model = IngredientCount


class RecipeTagInLine(admin.TabularInline):
    """
    Встроенный инлайн-объект администрирования тегов для рецепта.
    Позволяет управлять связями между тегами и рецептами в админ-панели.
    """

    model = RecipeTag


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели Ingredient.
    Определяет набор атрибутов, отображаемых в списке админ-панели,
    а также фильтр и поиск.
    """

    list_display = ("id", "name", "measurement_unit")
    list_display_links = ("name",)
    search_fields = ("name",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели Recipe.
    Определяет набор атрибутов, отображаемых в списке админ-панели,
    а также фильтры, поиск и встроенные инлайн-объекты для управления
    ингредиентами и тегами.
    """

    list_display = ("name", "author", "favorite_recipe")
    list_display_links = ("name", "author")
    list_filter = ("tags",)
    inlines = [IngredientCountInline, RecipeTagInLine]
    search_fields = ("name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("author").prefetch_related(
            "ingredients", "tags")

    @admin.display(
        description="Общее число добавлений этого рецепта в избранное")
    def favorite_recipe(self, obj: Recipe):
        return obj.favorite.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели Tag.
    Определяет набор атрибутов, отображаемых в списке админ-панели,
    а также фильтры и поиск.
    """

    list_display = ("id", "name", "slug")
    list_display_links = ("name",)
    search_fields = ("name", "slug",)


@admin.register(FavoriteRecipe)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели FavoriteRecipe.
    Определяет набор атрибутов, отображаемых в списке админ-панели.
    """

    list_display = ("id", "user", "recipe")
    list_display_links = ("user",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user", "recipe")


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели ShoppingList.
    Определяет набор атрибутов, отображаемых в списке админ-панели.
    """

    list_display = ("id", "user", "recipe")
    list_display_links = ("user",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user", "recipe")
