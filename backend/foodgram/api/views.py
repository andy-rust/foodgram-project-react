from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.generate_pdf import generate_pdf
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    SAFE_METHODS,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import Subscription, User

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
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    search_fields = ('^name',)


class UsersModelViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    pagination_class = PageNumberPagination
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

        if request.method == 'DELETE':
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
    filter_backends = (DjangoFilterBackend, )
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = PageNumberPagination
    pagination_class.page_size = 6
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        user = self.request.user

        queryset = Recipe.objects.all()
        if self.request.query_params.getlist('tags'):
            list = self.request.query_params.getlist('tags')
            queryset = queryset.filter(tags__slug__in=list).distinct()
        if self.request.query_params.get('is_favorited') == '1':
            queryset = queryset.filter(favorites=user)
        if self.request.query_params.get('is_in_shopping_cart') == '1':
            queryset = queryset.filter(shoppings=user)
        return queryset

    def get_serializer_class(self):
        if self.action in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateSerializer

    def post_delete(self, pk, serializer_class):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        recipe_model = serializer_class.Meta.model.objects.filter(
            user=user, recipe=recipe
        )
        # recipe_model = Recipe.objects.filter(user=user, recipe=recipe)

        if self.request.method == 'POST':
            serializer = serializer_class(
                data={'user': user.id, 'recipe': recipe.id},
                context={'request': self.request}
            )
            serializer.is_valid()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not recipe_model.exists():
                return Response(
                    {'Такого рецепта не существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe_model.delete()
            return Response(status=status.HTTP_200_OK)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = get_object_or_404(User, id=request.user.id)
        recipe_is_in_shopping_cart = ShoppingCart.objects.filter(
            user=user.id,
            recipe=recipe
        )
        if request.method == 'POST' and (
            not recipe_is_in_shopping_cart.exists()
        ):
            serializer = ShoppingCartSerializer(
                data={'user': user.id, 'recipe': recipe.id}
            )
            serializer.is_valid()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE' and recipe_is_in_shopping_cart.exists():
            recipe_is_in_shopping_cart.delete()
            return Response(status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['POST', 'DELETE'],
        url_path=r'(?P<id>[\d]+)/favorite',
        url_name='favorite',
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['id'])
        user = get_object_or_404(User, id=request.user.id)
        recipe_is_favorited = Favorite.objects.filter(
            user=user.id,
            recipe=recipe
        )

        if request.method == 'POST':
            if not recipe_is_favorited.exists():
                serializer = FavoriteRecipeSerializer(
                    data={'user': user.id, 'recipe': recipe.id}
                )
                serializer.is_valid()
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': 'Данный рецепт уже в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE' and recipe_is_favorited.exists():
            recipe_is_favorited.delete()
            return Response(status=status.HTTP_200_OK)

    @action(methods=['GET'],
            detail=False,)
    def download_shopping_cart(self, request):
        """Скачавание PDF файла со списком покупок"""
        user = request.user
        qweryset = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=user
        )
        qweryset_sort = qweryset.values('ingredient__name',
                                        'ingredient__measurement_unit',
                                        ).annotate(
            quantity=Sum('amount')).order_by()
        return generate_pdf(qweryset_sort)
