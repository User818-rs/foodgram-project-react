from django_filters import (
    BooleanFilter,
    CharFilter,
    FilterSet,
    ModelMultipleChoiceFilter,
)
from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    """
    Фильтр для поиска ингредиентов по имени.
    """
    name = CharFilter(lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ["name"]


class IngredientFilter(FilterSet):
    """
    Фильтр для поиска ингредиентов по имени.
    """
    name = CharFilter(lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ["name"]


class RecipeFilter(FilterSet):
    """
    Фильтр для поиска рецептов с возможностью фильтрации по автору, тегам,
    избранным и добавленным в корзину.
    """
    author = CharFilter()
    tags = ModelMultipleChoiceFilter(
        field_name="tags__slug",
        queryset=Tag.objects.all(),
        label="Tags",
        to_field_name="slug"
    )
    is_favorited = BooleanFilter(method="get_is_favorited")
    is_in_shopping_cart = BooleanFilter(method="get_is_in_shopping_cart")

    class Meta:
        model = Recipe
        fields = ("tags", "author", "is_favorited", "is_in_shopping_cart")

    def get_is_favorited(self, queryset, name, value):
        return queryset.filter(fav_recipes__user=self.request.user)

    def get_is_in_shopping_cart(self, queryset, name, value):
        return queryset.filter(shopping_list__user=self.request.user)
