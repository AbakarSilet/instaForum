from django.contrib import admin
from .models import NewsSource, NewsArticle, SavedArticle

class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')
    search_fields = ('name',)

class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'published_at', 'is_active')
    list_filter = ('source', 'published_at', 'is_active')
    search_fields = ('title', 'description')
    date_hierarchy = 'published_at'
    ordering = ['-published_at']

class SavedArticleAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__username', 'article__title')
    date_hierarchy = 'saved_at'

admin.site.register(NewsSource, NewsSourceAdmin)
admin.site.register(NewsArticle, NewsArticleAdmin)
admin.site.register(SavedArticle, SavedArticleAdmin)
