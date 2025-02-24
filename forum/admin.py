from django.contrib import admin
from .models import Badge, Category, Notification, Subforum, Thread, Post,Report,Like,Dislike,UserBadge

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    

class SubforumAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'description')
    list_filter = ('category',)
    search_fields = ('title', 'category__name')

class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'subforum', 'author', 'created_at', 'updated_at', 'view_count')
    list_filter = ('id','subforum', 'author')
    search_fields = ('title', 'author__username', 'subforum__title')
    prepopulated_fields = {'slug': ('title',)}

class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'thread', 'updated_at')
    list_filter = ('author', 'thread')
    search_fields = ('author__username', 'thread__title', 'content')

class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'thread')

class DislikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'thread')

class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user',)

class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name',)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user','message')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Subforum, SubforumAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Dislike, DislikeAdmin)
admin.site.register(UserBadge, UserBadgeAdmin)
admin.site.register(Badge, BadgeAdmin)
admin.site.register(Notification, NotificationAdmin)





"""from django.contrib import admin
from django.contrib.auth.models import Group, Permission

# Créer les groupes
admin_group, created = Group.objects.get_or_create(name='Administrateurs')
mod_group, created = Group.objects.get_or_create(name='Modérateurs')

# Attribuer des permissions aux groupes
admin_permissions = [
    'add_category',
    'change_category',
    'delete_category',
    'add_subforum',
    'change_subforum',
    'delete_subforum',
    'add_thread',
    'change_thread',
    'delete_thread',
    'add_post',
    'change_post',
    'delete_post',
]

mod_permissions = [
    'change_subforum',
    'add_thread',
    'change_thread',
    'delete_thread',
    'add_post',
    'change_post',
    'delete_post',
]

for perm in admin_permissions:
    admin_group.permissions.add(Permission.objects.get(codename=perm))

for perm in mod_permissions:
    mod_group.permissions.add(Permission.objects.get(codename=perm))


from django.contrib import admin
from django.contrib.auth.models import Group, Permission

# Créer les groupes
admin_group, created = Group.objects.get_or_create(name='Administrateurs')

# Attribuer des permissions aux groupes
admin_permissions = [
    'add_subforum',
    'change_subforum',
    'delete_subforum',
    'delete_thread',
    'move_thread',
]

for perm in admin_permissions:
    admin_group.permissions.add(Permission.objects.get(codename=perm))

"""