from django.contrib import admin
from .models import Badge, Category, Notification, Subforum, Thread, Post,Report,Like,Dislike,UserBadge

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    

class SubforumAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'description')
    list_filter = ('category',)
    search_fields = ('title', 'category__name')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'subforum', 'author', 'created_at', 'updated_at')
    list_filter = ('subforum', 'author', 'created_at')
    search_fields = ('title', 'author__username', 'subforum__title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Informations de base', {
            'fields': ('title', 'subforum', 'author', 'slug', 'content', 'image','tags', 'likes')
        }),
        ('Statistiques', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'description': 'Informations sur les vues et les dates.'
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'view_count')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('content','author', 'thread', 'created_at')
    list_filter = ('author', 'thread', 'created_at')
    search_fields = ('author__username', 'thread__title', 'content')
    fieldsets = (
        ('Informations de base', {
            'fields': ('author', 'thread', 'content','likes')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'description': 'Dates de création et de mise à jour.'
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'awarded_at')
    list_filter = ('user', 'badge', 'awarded_at')
    search_fields = ('user__username', 'badge__name')
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'badge')
        }),
        ('Date', {
            'fields': ('awarded_at',),
            'description': 'Date d\'attribution du badge.'
        }),
    )
    readonly_fields = ('awarded_at',) 

class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name','icon',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'link', 'created_at', 'is_read')
    list_filter = ('user', 'is_read', 'created_at')
    search_fields = ('user__username', 'message')
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'message', 'is_read')
        }),
        ('Date', {
            'fields': ('created_at',),
            'description': 'Date de création de la notification.'
        }),
    )
    readonly_fields = ('created_at',)
    


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reported_by', 'report_type', 'reported_user', 'thread', 'post', 'created_at')
    list_filter = ('report_type', 'created_at')
    search_fields = ('reported_by__username', 'report_reason', 'reported_user__username')
    fieldsets = (
        ('Informations de base', {
            'fields': ('reported_by', 'report_type', 'report_reason', 'created_at')
        }),
        ('Contenu signalé', {
            'fields': ('thread', 'post', 'reported_user'),
            'description': 'Contenu ou utilisateur signalé.'
        }),
    )
    readonly_fields = ('created_at',) 
    
admin.site.register(Category, CategoryAdmin)
admin.site.register(Subforum, SubforumAdmin)





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