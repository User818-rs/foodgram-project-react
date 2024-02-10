from django.core.exceptions import ValidationError

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    IngredientCount,
    Recipe,
    ShoppingList,
    Tag,
)
from users.models import CustomUser, Subscription


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели CustomUser дополнительными полями и методом."""

    password = serializers.CharField(write_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ("email", "id", "username", "first_name", "last_name",
                  "is_subscribed", "password")

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=user, following=obj.id).exists()


class AuthorSubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Subscription, отображающей подписку
    автора и следующих за ним пользователей.
    """

    class Meta:
        model = Subscription
        fields = ("user", "following")


class IngredientCountSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели IngredientCount, представляющей количество
    ингредиентов в рецепте.
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source="ingredients.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredients.measurement_unit"
    )

    class Meta:
        model = IngredientCount
        fields = ["id", "name", "amount", "measurement_unit"]


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient, представляющей ингредиент."""

    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit"]


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag, представляющей тег."""

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class RecipeViewingSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Recipe, представляющей рецепт
    с дополнительными полями.
    """

    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id", "tags", "author", "ingredients", "is_favorited",
            "is_in_shopping_cart", "name", "image", "text", "cooking_time")

    def get_ingredients(self, obj):
        ingredients = IngredientCount.objects.filter(recipe=obj)
        return IngredientCountSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(user=user, recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return ShoppingList.objects.filter(user=user, recipe=obj.id).exists()


class ReducedRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Recipe, представляющей рецепт
    с сокращенными полями.
    """

    class Meta:
        model = Recipe
        fields = "id", "name", "image", "cooking_time"
        read_only_fields = ["id", "name", "image", "cooking_time"]


class SubscribeRecipesSerializer(CustomUserSerializer):
    """
    Сериализатор для модели CustomUser с дополнительными
    полями о подписках на рецепты.
    """

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta(CustomUser.Meta):
        model = CustomUser
        fields = ["email", "id", "username", "first_name", "last_name",
                  "is_subscribed", "recipes", "recipes_count"]

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes_limit = request.GET.get("recipes_limit")
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
                if recipes_limit <= 0:
                    raise ValidationError(
                        "recipes_limit должно быть положительным целым числом."
                    )
            except ValueError:
                raise ValidationError(
                    "recipes_limit должно быть целым числом.")
            recipes = Recipe.objects.filter(
                author=obj).order_by("id")[:recipes_limit]
        else:
            recipes = Recipe.objects.filter(author=obj)
        serializer = ReducedRecipeSerializer(recipes, many=True)
        return serializer.data


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientCountSerializer(
        many=True, source="ingredient_count_ingredients")
    IngredientCountSerializer
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            "id", "author", "ingredients", "tags",
            "image", "name", "text", "cooking_time"]

    def add_tags_and_ingredients(self, tags, ingredients_data, recipe):
        recipe.tags.set(tags)
        for ingredient in ingredients_data:
            IngredientCount.objects.create(
                ingredients_id=ingredient.get("id").id,
                amount=ingredient.get("amount"),
                recipe=recipe)
        return recipe

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredient_count_ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        return self.add_tags_and_ingredients(tags, ingredients_data, recipe)

    def update(self, instance, validated_data):
        IngredientCount.objects.filter(recipe=instance).delete()
        ingredients_data = validated_data.pop("ingredient_count_ingredients")
        tags = validated_data.pop("tags")
        instance.tags.clear()
        self.add_tags_and_ingredients(tags, ingredients_data, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get("request")
        return RecipeViewingSerializer(
            instance,
            context={"request": request}).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ShoppingList,
    представляющей список рецептов в корзине.
    """

    class Meta:
        model = ShoppingList
        fields = ["user", "recipe"]

    def to_representation(self, instance):
        request = self.context.get("request")
        return ReducedRecipeSerializer(
            instance.recipe,
            context={"request": request}).data


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели FavoriteRecipes,
    представляющей список любимых рецептов.
    """

    class Meta:
        model = FavoriteRecipe
        fields = ["user", "recipe"]

    def to_representation(self, instance):
        request = self.context.get("request")
        return ReducedRecipeSerializer(
            instance.recipe,
            context={"request": request}).data
