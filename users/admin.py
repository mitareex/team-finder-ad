from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'name', 'surname', 'phone', 'is_staff', 'is_active')

    ordering = ('email',)

    list_filter = ('is_staff', 'is_active')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональные данные', {'fields': (
            'name',
            'surname',
            'phone',
            'avatar',
            'about',
            'github_url'
        )}),
        ('Права доступа', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions'
        )}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('collapse',),
            'fields': ('email', 'name', 'surname', 'phone', 'password'),
        }),
    )

    search_fields = ('email', 'name', 'surname')
