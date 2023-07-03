from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'password',
        'email',
        'first_name',
        'last_name',
        'role',
    )
    list_filter = ('username', 'email')


admin.site.register(User)
admin.site.register(Subscription)
