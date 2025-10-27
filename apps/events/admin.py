from django.contrib import admin
from .models import EventType, Event, Attachment, Variable


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'version', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información General', {
            'fields': ('name', 'category', 'description')
        }),
        ('Esquema', {
            'fields': ('schema', 'version')
        }),
        ('Presentación', {
            'fields': ('icon', 'color', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    readonly_fields = ('file_size', 'mime_type', 'uploaded_by', 'uploaded_at')
    fields = ('file', 'file_name', 'file_size', 'mime_type', 'uploaded_at')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'field', 'campaign', 'timestamp', 'created_by', 'created_at')
    list_filter = ('event_type', 'field', 'campaign', 'timestamp', 'created_at')
    search_fields = ('event_type__name', 'field__name', 'observations')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ['field', 'campaign', 'created_by']
    date_hierarchy = 'timestamp'
    inlines = [AttachmentInline]
    fieldsets = (
        ('Información General', {
            'fields': ('event_type', 'field', 'campaign', 'timestamp')
        }),
        ('Datos', {
            'fields': ('payload', 'observations')
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('ID', {
            'fields': ('id',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'event', 'file_size', 'mime_type', 'uploaded_by', 'uploaded_at')
    list_filter = ('mime_type', 'uploaded_at')
    search_fields = ('file_name', 'event__event_type__name')
    readonly_fields = ('file_size', 'mime_type', 'uploaded_at')
    autocomplete_fields = ['event', 'uploaded_by']


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    list_display = ('variable_type', 'value', 'unit', 'station', 'field', 'timestamp', 'source')
    list_filter = ('variable_type', 'source', 'station', 'field', 'timestamp')
    search_fields = ('variable_type',)
    readonly_fields = ('created_at',)
    autocomplete_fields = ['station', 'field']
    date_hierarchy = 'timestamp'
    fieldsets = (
        ('Medición', {
            'fields': ('variable_type', 'value', 'unit', 'timestamp')
        }),
        ('Ubicación', {
            'fields': ('station', 'field')
        }),
        ('Fuente', {
            'fields': ('source', 'metadata')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
