from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    SAFE_METHODS,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.generate_pdf import generate_pdf
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import Subscription, User
from .methods import post_or_delete_method
from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .serializers import (
    FavoriteRecipeSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeListSerializer,
    ShoppingCartSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UsersSerializer,
)


class TagModelViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = None


class IngredientModelViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    pagination_class = None
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filterset_class = IngredientFilter


class UsersModelViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticatedOrReadOnly, )

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        is_subscribed = Subscription.objects.filter(
            user=user, author=author).exists()

        if request.method == 'POST':
            if is_subscribed:
                return Response({'Вы уже подписаны на этого автора'},
                                status=status.HTTP_400_BAD_REQUEST)
            if author == user:
                return Response({'Нельзя подписаться на самого себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscriptionSerializer(author,
                                                context={'request': request})
            Subscription.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not is_subscribed:
            return Response({'У вас нет подписки на этого автора'},
                            status=status.HTTP_400_BAD_REQUEST)
        Subscription.objects.filter(user=user, author=author).delete()
        return Response(
            {'Вы отписались от этого автора'}, status=status.HTTP_200_OK
        )

    @action(methods=['GET'], detail=False,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeModelViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = CustomPagination
    pagination_class.page_size = 6
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateSerializer

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        response = post_or_delete_method(
            ShoppingCart, ShoppingCartSerializer, request, **kwargs)
        return response

    @action(
        detail=False,
        methods=['POST', 'DELETE'],
        url_path=r'(?P<pk>[\d]+)/favorite',
        url_name='favorite',
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, **kwargs):
        response = post_or_delete_method(
            Favorite, FavoriteRecipeSerializer, request, **kwargs)
        return response

    @action(methods=['GET'],
            detail=False,)
    def download_shopping_cart(self, request):
        """Скачавание PDF файла со списком покупок"""
        user = request.user
        queryset = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=user
        )
        queryset_sort = queryset.values('ingredient__name',
                                        'ingredient__measurement_unit',
                                        ).annotate(
            quantity=Sum('amount')).order_by()
        return generate_pdf(queryset_sort)
