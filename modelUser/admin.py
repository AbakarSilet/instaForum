from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'is_suspended', 'groups']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    readonly_fields = ['last_login', 'suspension_date']  # Supprimez 'date_joined'
    fieldsets = (
        ('Informations de base', {
            'fields': ('email', 'username', 'first_name', 'last_name', 'profile_image')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_suspended', 'groups', 'user_permissions'),
            'description': 'Gestion des permissions et des groupes.'
        }),
        ('Dates importantes', {
            'fields': ('last_login', 'suspension_date'),  # Supprimez 'date_joined'
            'description': 'Dates de connexion et de suspension.'
        }),
    )
    filter_horizontal = ('groups', 'user_permissions',)
    actions = ['suspend_users', 'activate_users']