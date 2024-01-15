# import pdb
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (
    FavRecipes,
    Ingredient,
    IngredientCount,
    Recipe,
    ShoppingList,
    Tag,
)
from rest_framework import serializers
from users.models import CustomUser, Subscription


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели CustomUser с дополнительными полями и методом.
    """
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
    id = serializers.ReadOnlyField(source="ingredients.id")
    name = serializers.ReadOnlyField(source="ingredients.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredients.measurement_unit"
    )

    class Meta:
        model = IngredientCount
        fields = ["id", "name", "amount", "measurement_unit"]


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredient, представляющей ингредиент.
    """
    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit"]


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Tag, представляющей тег.
    """
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
    name = serializers.CharField(required=False, allow_blank=True)
    text = serializers.CharField(required=False, allow_blank=True)
    cooking_time = serializers.FloatField(required=False)
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
        return FavRecipes.objects.filter(user=user, recipe=obj.id).exists()

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
        read_only_fields = ["__all__"]


class SubscribeRecipesSerializer(CustomUserSerializer):
    """
    Сериализатор для модели CustomUser с дополнительными
    полями о подписках на рецепты.
    """
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(CustomUser.Meta):
        model = CustomUser
        fields = ["email", "id", "username", "first_name", "last_name",
                  "is_subscribed", "recipes", "recipes_count"]

    def get_recipes_count(self, obj):
        return obj.recipes.count()

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


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Вспомогательный сериализатор для создания рецепта
    """
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ("id", "amount")


class CreateRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания рецепта
    """
    author = CustomUserSerializer(read_only=True)
    ingredients = CreateRecipeIngredientSerializer(
        many=True, source="Ingredient_Count")
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()

    def create(self, validated_data):
        ingredients_data = validated_data.pop("Ingredient_Count")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        Ingredient_Count = []
        for ingredient in ingredients_data:
            id = ingredient.get("id")
            amount = ingredient.get("amount")
            ingredient_instance, created = Ingredient.objects.get_or_create(
                id=id)
            Ingredient_Count.append(IngredientCount(
                recipe=recipe,
                ingredients=ingredient_instance,
                amount=amount))
        IngredientCount.objects.bulk_create(Ingredient_Count)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.setdefault("name", instance.name)
        instance.image = validated_data.setdefault("image", instance.image)
        instance.text = validated_data.setdefault("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time)
        tags_data = validated_data.pop("tags")
        ingredients_data = validated_data.pop("Ingredient_Count")
        new_ingredient = []
        for item in ingredients_data:
            amount = item.get("amount")
            ingredient = get_object_or_404(Ingredient, id=item.get("id"))
            new_ingredient.append(
                ingredient)
        new_tags = []
        for item in tags_data:
            tags = get_object_or_404(Tag, id=item.id)
            new_tags.append(tags)
        instance.tags.set(new_tags)
        instance.ingredients.set(
            new_ingredient,
            through_defaults={"amount": amount})
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get("request")
        return RecipeViewingSerializer(
            instance,
            context={"request": request}).data

    class Meta:
        model = Recipe
        fields = [
            "id", "author", "ingredients", "tags",
            "image", "name", "text", "cooking_time"]


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


class FavRecipesSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели FavRecipes, представляющей список любимых рецептов.
    """

    class Meta:
        model = FavRecipes
        fields = ["user", "recipe"]

    def to_representation(self, instance):
        request = self.context.get("request")
        return ReducedRecipeSerializer(
            instance.recipe,
            context={"request": request}).data
