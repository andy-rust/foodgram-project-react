from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    '''Отображаем модель юзеров
    фильтрация по email и username
    '''
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
