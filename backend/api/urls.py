from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientModelViewSet,
    RecipeModelViewSet,
    TagModelViewSet,
    UsersModelViewSet,
)

router = DefaultRouter()
router.register(r'users', UsersModelViewSet, basename='users')
router.register(r'tags', TagModelViewSet, basename='tags')
router.register(r'recipes', RecipeModelViewSet, basename='recipes')
router.register(r'ingredients', IngredientModelViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls.authtoken'))
]
