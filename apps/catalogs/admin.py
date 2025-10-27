from django.contrib import admin
from .models import Field


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'surface_ha', 'is_active', 'created_at')
    search_fields = ('name', 'code')
    list_filter = ('is_active',)
