import pdb
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from recipes.models import Ingredient, Recipe, ShoppingList, Tag, IngredientCount, FavRecipes
from rest_framework.decorators import action
from djoser.serializers import UserCreateSerializer, UserSerializer

from rest_framework import permissions, serializers
from users.models import CustomUser, Subscription
from rest_framework.serializers import ModelSerializer


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'password')

    # def create(self, validated_data):
    #     user = CustomUser(
    #         email=validated_data['email'],
    #         username=validated_data['username'],
    #         first_name=validated_data['first_name'],
    #         last_name=validated_data['last_name'],
    #     )
        
    #     user.set_password(validated_data['password'])
    #     user.save()
    #     return user
    
    def get_is_subscribed(self, obj):
        
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, following=obj.id).exists()
    

class AuthorSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('user', 'following')



class IngredientCountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )
    class Meta:
        model = IngredientCount
        fields = ['id', 'name', 'amount', 'measurement_unit']
        # fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    # amount = IngredientCountSerializer(many=True)
    class Meta:
        model = Ingredient
        # fields = ['id', 'name', 'measurement_unit', 'amount']
        fields = ['id', 'name', 'measurement_unit']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    "sdfsdf"
    ingredients = serializers.SerializerMethodField()
    # ingredients = IngredientCountSerializer(many=True)
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    image = serializers.CharField(style={'base64': True})
    name = serializers.CharField(required=False, allow_blank=True)
    text = serializers.CharField(required=False, allow_blank=True)
    cooking_time = serializers.FloatField(required=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients','is_favorited','is_in_shopping_cart', 'name',  'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        # ingredients = IngredientCountSerializer.objects.filter(recipe=obj)
        ingredients = IngredientCount.objects.filter(recipe=obj)
        # pdb.set_trace()
        return IngredientCountSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return FavRecipes.objects.filter(user=user, recipe=obj.id).exists()
    
    def get_is_in_shopping_cart(self, obj):
        
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingList.objects.filter(user=user, recipe=obj.id).exists()
      
class ReducedRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = ['__all__']

class SubscribeRecipesSerializer(CustomUserSerializer):
    recipes = ReducedRecipeSerializer(read_only=True, many=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(CustomUser.Meta):
        model = CustomUser
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count']

    def get_recipes_count(self, obj):
        return obj.recipes.count()
