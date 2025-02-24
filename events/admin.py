from django.contrib import admin
from .models import Event, Attendee

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'organizer', 'image')

admin.site.register(Event, EventAdmin)
admin.site.register(Attendee)
