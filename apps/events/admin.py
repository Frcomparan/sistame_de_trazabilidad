from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'field', 'created_at')
    list_filter = ('event_type',)
    search_fields = ('event_type',)
