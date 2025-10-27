from django.contrib import admin
from .models import Field, Campaign, Station


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'surface_ha', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Información General', {
            'fields': ('name', 'code', 'surface_ha')
        }),
        ('Detalles', {
            'fields': ('notes', 'is_active')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'season', 'variety', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'season', 'start_date')
    search_fields = ('name', 'season', 'variety')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_date'
    fieldsets = (
        ('Información General', {
            'fields': ('name', 'season', 'variety')
        }),
        ('Fechas', {
            'fields': ('start_date', 'end_date')
        }),
        ('Detalles', {
            'fields': ('notes', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'field', 'station_type', 'is_operational', 'installed_at')
    list_filter = ('station_type', 'is_operational', 'field')
    search_fields = ('name', 'field__name')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['field']
    fieldsets = (
        ('Información General', {
            'fields': ('name', 'field', 'station_type')
        }),
        ('Estado', {
            'fields': ('is_operational', 'installed_at')
        }),
        ('Detalles', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
