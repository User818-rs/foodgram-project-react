from django_filters import rest_framework

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(rest_framework.FilterSet):
    """Фильтр для поиска ингредиентов по имени."""

    name = rest_framework.CharFilter(lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ["name"]


class RecipeFilter(rest_framework.FilterSet):
    """
    Фильтр для поиска рецептов с возможностью фильтрации по автору, тегам,
    избранным и добавленным в корзину.
    """

    author = rest_framework.CharFilter()
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        queryset=Tag.objects.all(),
        label="Tags",
        to_field_name="slug",
    )
    is_favorited = rest_framework.BooleanFilter(method="get_is_favorited")
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method="get_is_in_shopping_cart")

    class Meta:
        model = Recipe
        fields = ("tags", "author", "is_favorited", "is_in_shopping_cart")

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(
                favorite__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(
                shopping_list_recipe__user=self.request.user)
        return queryset
