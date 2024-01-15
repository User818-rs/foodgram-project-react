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

    def get_favorite(self, queryset, name, item_value):
        if self.request.user.is_authenticated and item_value:
            queryset = queryset.filter(in_favorite__user=self.request.user)
        return queryset

    def get_shopping(self, queryset, name, item_value):
        if self.request.user.is_authenticated and item_value:
            queryset = queryset.filter(shopping_cart__user=self.request.user)
        return queryset
