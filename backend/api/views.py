import pdb
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.views import APIView
from api.pagination import PageSizePagination
from api.serializers import CustomUserSerializer, AuthorSubscriptionSerializer, IngredientSerializer, SubscribeRecipesSerializer,   TagSerializer, RecipeSerializer
from recipes.models import Ingredient, Tag, Recipe
from rest_framework.decorators import action
from users.models import CustomUser, Subscription
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from djoser.views import UserViewSet

class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = AllowAny
    serializer_class = CustomUserSerializer
    pagination_class = PageSizePagination

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
        pagination_class=PageSizePagination)
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(CustomUser, id=id)
        if request.method == 'POST':
            if user == author:
                return Response(
                    'Нельзя подписываться на самого себя ',
                    status=status.HTTP_400_BAD_REQUEST)
            if Subscription.objects.filter(user=user, following=author).exists():
                return Response(
                    'Нельзя подписаться два раза на одного пользователя',
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = AuthorSubscriptionSerializer(
                data={'user': user.id, 'following': author.id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # pdb.set_trace()
            serializer = SubscribeRecipesSerializer(
                author,
                context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = Subscription.objects.filter(user=user, following=author)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Возвращает пользователей, на которых подписан текущий пользователь"""
        user = request.user
        queryset = CustomUser.objects.filter(username=user)
        # pdb.set_trace()
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeRecipesSerializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageSizePagination

    def perform_create(self, serializer):
        pdb.set_trace()
        serializer.save(author=self.request.user) 
    # @action(methods=['get'], detail=False)
    # def get_ingredients(self, request,pk):
    #     post = get_object_or_404(Recipe, id=pk)
    #     serializer = self.get_serializer(post, many=True)
    #     return Response(serializer.data)


class PasswordChangeView(APIView):

    def patch(self, request):
        user = request.user
        serializer = PasswordSerializer(
            instance=user, data=request.data
        )
        # if serializer.is_valid(raise_exception=True):
        #     serializer.save()
        #     return Response(status=status.HTTP_204_NO_CONTENT)
        pdb.set_trace()
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)