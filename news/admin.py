from django.contrib import admin
from .models import NewsSource, NewsArticle

class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')
    search_fields = ('name',)

class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'published_at', 'is_active')
    list_filter = ('source', 'published_at', 'is_active')
    search_fields = ('title', 'description')
    date_hierarchy = 'published_at'
    ordering = ['-published_at']


admin.site.register(NewsSource, NewsSourceAdmin)
admin.site.register(NewsArticle, NewsArticleAdmin)

