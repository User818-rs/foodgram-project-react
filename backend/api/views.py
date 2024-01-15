from api.filters import IngredientFilter, RecipeFilter
from api.pagination import PageSizePagination
from api.serializers import (
    AuthorSubscriptionSerializer,
    CreateRecipeSerializer,
    CustomUserSerializer,
    FavRecipesSerializer,
    IngredientSerializer,
    RecipeViewingSerializer,
    ShoppingCartSerializer,
    SubscribeRecipesSerializer,
    TagSerializer,
)
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import FavRecipes, Ingredient, Recipe, ShoppingList, Tag
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import CustomUser, Subscription

from .permissions import IsOwnerOrAdminOrReadOnly

# import pdb


class CustomUserViewSet(UserViewSet):
    """
    CustomUserViewSet - это класс представления для работы
    с пользователями в приложении.Он наследуется от UserViewSet и
    предоставляет дополнительные функции и возможности.
    """
    queryset = CustomUser.objects.all()
    permissions_classes = (AllowAny,)
    serializer_class = CustomUserSerializer
    pagination_class = PageSizePagination
    filterset_class = RecipeFilter

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated],
        pagination_class=PageSizePagination)
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(CustomUser, id=id)
        if request.method == "POST":
            if user == author:
                return Response(
                    "Нельзя подписываться на самого себя ",
                    status=status.HTTP_400_BAD_REQUEST)
            if Subscription.objects.filter(
                    user=user, following=author).exists():
                return Response(
                    "Нельзя подписаться два раза на одного пользователя",
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = AuthorSubscriptionSerializer(
                data={"user": user.id, "following": author.id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # pdb.set_trace()
            serializer = SubscribeRecipesSerializer(
                author,
                context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = Subscription.objects.filter(user=user, following=author)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = CustomUser.objects.filter(
            following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscribeRecipesSerializer(
            page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ModelViewSet):
    """
    IngredientViewSet - это класс представления для работы
    с ингредиентами в приложении.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ModelViewSet):
    """
    TagViewSet - это класс представления для работы с тегами в приложении.
    Он наследуется от viewsets.ModelViewSet и предоставляет полный набор
    функций для работы с тегами.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """
    RecipeViewSet - это класс представления для работы с рецептами
    в приложении.Он наследуется от viewsets.ModelViewSet и предоставляет
    полный набор функций для работы с рецептами.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeViewingSerializer
    pagination_class = PageSizePagination
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == "POST" or self.request.method == "PATCH":
            return CreateRecipeSerializer
        return RecipeViewingSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    @action(methods=["POST", "DELETE"], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        recipe = self.get_object()
        if request.method == "POST":
            new_cart_item, created = ShoppingList.objects.get_or_create(
                user=request.user, recipe=recipe)
            if not created:
                return Response(
                    {"Ошибка добавления рецепт уже есть в списке покупок"},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = ShoppingCartSerializer(new_cart_item,
                                                context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            cart_item = get_object_or_404(ShoppingList, user=request.user,
                                          recipe=recipe)
            cart_item.delete()
            return Response(
                {"Рецепт успешно удален из списка покупок."},
                status=status.HTTP_204_NO_CONTENT)

    @action(methods=["POST", "DELETE"], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        recipe = self.get_object()
        if request.method == "POST":
            if FavRecipes.objects.filter(user=request.user,
                                         recipe=recipe).exists():
                return Response(
                    "Нельзя добавить один и тот же рецепт два раза",
                    status=status.HTTP_400_BAD_REQUEST)
            favorite = FavRecipes.objects.create(
                user=request.user, recipe=recipe)
            serializer = FavRecipesSerializer(
                favorite,
                context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            old_fav = get_object_or_404(FavRecipes,
                                        user=request.user,
                                        recipe=recipe)
            old_fav.delete()
            return Response("Рецепт успешно удален из избранного",
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["GET"],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingList.objects.filter(user=request.user).all()
        shopping_list = {}
        for item in shopping_cart:
            for recipe_ingredient in item.recipe.ingredient_count.all():
                name = recipe_ingredient.ingredients.name
                measuring_unit = recipe_ingredient.ingredients.measurement_unit
                amount = recipe_ingredient.amount
                if name not in shopping_list:
                    shopping_list[name] = {
                        "name": name,
                        "measurement_unit": measuring_unit,
                        "amount": amount
                    }
                else:
                    shopping_list[name]["amount"] += amount
        content = (
            [f"{item['name']} - ({item['measurement_unit']}) "
             f"- {item['amount']}\n"for item in shopping_list.values()]
        )
        filename = f"{request.user.username}_shop_list.txt"
        response = HttpResponse(content, content_type="text/plain")
        response["Content-Disposition"] = (
            "attachment; filename={0}".format(filename)
        )
        return response
