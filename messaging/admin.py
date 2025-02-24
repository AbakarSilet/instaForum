from django.contrib import admin
from .models import Message, SharedLink, UserBlock

class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'content')

class SharedLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'url', 'link_type', 'title')
    list_filter = ('link_type',)
    search_fields = ('url', 'title')

class UserBlockAdmin(admin.ModelAdmin):
    list_display = ('id', 'blocker', 'blocked', 'created_at')
    search_fields = ('blocker__username', 'blocked__username')

admin.site.register(Message, MessageAdmin)
admin.site.register(SharedLink, SharedLinkAdmin)
admin.site.register(UserBlock, UserBlockAdmin)



