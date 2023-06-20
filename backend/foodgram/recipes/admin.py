from django.contrib import admin

from .models import Favorite, Ingredient, ShoppingCart, Tag

admin.site.register(Tag)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)
admin.site.register(Ingredient)
