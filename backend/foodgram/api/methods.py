from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from rest_framework import status
from rest_framework.response import Response
from users.models import User


def post_or_delete_method(cart_or_favortie_model,
                          cart_or_favortie_serializer,
                          request,
                          **kwargs):
    recipe = get_object_or_404(Recipe, id=kwargs['pk'])
    user = get_object_or_404(User, id=request.user.id)
    recipe_is_in_shopping_cart_or_favorite = (
        cart_or_favortie_model.objects.filter(
            user=user.id,
            recipe=recipe
        ))

    if request.method == 'POST':
        if not recipe_is_in_shopping_cart_or_favorite.exists():
            serializer = cart_or_favortie_serializer(
                data={'user': user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Рецепт уже добавлен'},
                            status=status.HTTP_400_BAD_REQUEST)
    else:
        if recipe_is_in_shopping_cart_or_favorite.exists():
            recipe_is_in_shopping_cart_or_favorite.delete()
            return Response(status=status.HTTP_200_OK)
