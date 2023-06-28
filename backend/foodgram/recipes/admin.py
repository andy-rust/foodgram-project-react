from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author',
    )
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit'
    )
    list_filter = ('name',)


admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)
admin.site.register(Ingredient)
admin.site.register(IngredientInRecipe)
