from django.contrib import admin
from .models import Resource

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'user', 'date_added')
    list_filter = ('resource_type', 'date_added')
    search_fields = ('title', 'description', 'link')

# ou simplement
# admin.site.register(Resource, ResourceAdmin)
