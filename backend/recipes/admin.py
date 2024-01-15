from django.contrib import admin

from .models import (
    FavRecipes,
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
    list_filter = ["name"]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели Recipe.
    Определяет набор атрибутов, отображаемых в списке админ-панели,
    а также фильтры, поиск и встроенные инлайн-объекты для управления
    ингредиентами и тегами.
    """
    list_display = ("name", "author", "fav_recipes")
    list_filter = ("author", "name", "tags")
    inlines = [IngredientCountInline, RecipeTagInLine]

    @admin.display(
        description="Общее число добавлений этого рецепта в избранное")
    def fav_recipes(self, obj: Recipe):
        return obj.fav_recipes.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели Tag.
    Определяет набор атрибутов, отображаемых в списке админ-панели,
    а также фильтры и поиск.
    """
    list_display = ("id", "name", "slug")


@admin.register(FavRecipes)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели FavRecipes.
    Определяет набор атрибутов, отображаемых в списке админ-панели.
    """
    list_display = ("id", "user", "recipe")


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели ShoppingList.
    Определяет набор атрибутов, отображаемых в списке админ-панели.
    """
    list_display = ("id", "user", "recipe")
