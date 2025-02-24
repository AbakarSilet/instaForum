from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin
from admin_interface.models import Theme

admin.site.site_header = 'InstaForum Admin'
admin.site.site_title = 'InstaForum Admin Portal'
admin.site.index_title = 'Bienvenue sur le portail d\'administration InstaForum'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username','first_name', 'last_name', 'is_staff', 'is_active']
    search_fields = ['email', 'first_name', 'last_name','username']


admin.site.unregister(User)
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    filter_horizontal = ('groups', 'user_permissions',)