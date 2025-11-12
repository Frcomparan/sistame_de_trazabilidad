from django.contrib import admin
from .models import (
    EventType, 
    Event, 
    Attachment, 
    Variable,
    IrrigationEvent,
    FertilizationEvent,
    PhytosanitaryEvent,
    MaintenanceEvent,
    MonitoringEvent,
    OutbreakEvent,
    ClimateEvent,
    HarvestEvent,
    PostHarvestEvent,
    LaborCostEvent,
)


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información General', {
            'fields': ('name', 'category', 'description')
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


# Admin base para Event (solo lectura, para consultas)
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
        ('Observaciones', {
            'fields': ('observations',)
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

    def has_add_permission(self, request):
        """No permitir crear eventos desde el admin base."""
        return False


# Admins específicos para cada tipo de evento
@admin.register(IrrigationEvent)
class IrrigationEventAdmin(admin.ModelAdmin):
    list_display = ('field', 'campaign', 'metodo', 'duracion_minutos', 'timestamp', 'created_by')
    list_filter = ('metodo', 'fuente_agua', 'timestamp', 'field', 'campaign')
    search_fields = ('field__name', 'observations')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ['field', 'campaign', 'created_by']
    date_hierarchy = 'timestamp'
    inlines = [AttachmentInline]
    fieldsets = (
        ('Información General', {
            'fields': ('event_type', 'field', 'campaign', 'timestamp')
        }),
        ('Datos de Riego', {
            'fields': (
                'metodo', 'duracion_minutos', 'fuente_agua',
                'volumen_m3', 'presion_bar', 'ce_uScm', 'ph'
            )
        }),
        ('Observaciones', {
            'fields': ('observations',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FertilizationEvent)
class FertilizationEventAdmin(admin.ModelAdmin):
    list_display = ('field', 'campaign', 'producto', 'metodo_aplicacion', 'dosis', 'timestamp')
    list_filter = ('metodo_aplicacion', 'timestamp', 'field', 'campaign')
    search_fields = ('producto', 'field__name', 'observations')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ['field', 'campaign', 'created_by']
    date_hierarchy = 'timestamp'
    inlines = [AttachmentInline]
    fieldsets = (
        ('Información General', {
            'fields': ('event_type', 'field', 'campaign', 'timestamp')
        }),
        ('Datos de Fertilización', {
            'fields': (
                'producto', 'metodo_aplicacion', 'dosis', 'unidad_dosis',
                'n_porcentaje', 'p_porcentaje', 'k_porcentaje', 'volumen_caldo_l'
            )
        }),
        ('Observaciones', {
            'fields': ('observations',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PhytosanitaryEvent)
class PhytosanitaryEventAdmin(admin.ModelAdmin):
    list_display = ('field', 'campaign', 'producto', 'tipo_producto', 'objetivo', 'timestamp')
    list_filter = ('tipo_producto', 'metodo_aplicacion', 'timestamp', 'field', 'campaign')
    search_fields = ('producto', 'objetivo', 'field__name', 'observations')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ['field', 'campaign', 'created_by']
    date_hierarchy = 'timestamp'
    inlines = [AttachmentInline]
    fieldsets = (
        ('Información General', {
            'fields': ('event_type', 'field', 'campaign', 'timestamp')
        }),
        ('Datos del Producto', {
            'fields': (
                'producto', 'ingrediente_activo', 'tipo_producto', 'objetivo',
                'lote_producto'
            )
        }),
        ('Aplicación', {
            'fields': (
                'metodo_aplicacion', 'dosis', 'unidad_dosis', 'volumen_caldo_l',
                'presion_bar', 'intervalo_seguridad_dias', 'responsable_aplicacion'
            )
        }),
        ('Resultados', {
            'fields': ('eficacia_observada', 'fitotoxicidad')
        }),
        ('Observaciones', {
            'fields': ('observations',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MaintenanceEvent)
class MaintenanceEventAdmin(admin.ModelAdmin):
    list_display = ('field', 'campaign', 'actividad', 'horas_hombre', 'timestamp')
    list_filter = ('actividad', 'timestamp', 'field', 'campaign')
    search_fields = ('actividad', 'field__name', 'observations')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ['field', 'campaign', 'created_by']
    date_hierarchy = 'timestamp'
    inlines = [AttachmentInline]
    fieldsets = (
        ('Información General', {
            'fields': ('event_type', 'field', 'campaign', 'timestamp')
        }),
        ('Datos de la Labor', {
            'fields': (
                'actividad', 'herramienta_equipo', 'numero_jornales',
                'horas_hombre', 'objetivo', 'porcentaje_completado',
                'herramientas_desinfectadas'
            )
        }),
        ('Observaciones', {
            'fields': ('observations',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MonitoringEvent)
class MonitoringEventAdmin(admin.ModelAdmin):
    list_display = ('field', 'campaign', 'plaga_enfermedad', 'incidencia', 'timestamp')
    list_filter = ('metodo_muestreo', 'incidencia', 'timestamp', 'field', 'campaign')
    search_fields = ('plaga_enfermedad', 'field__name', 'observations')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ['field', 'campaign', 'created_by']
    date_hierarchy = 'timestamp'
    inlines = [AttachmentInline]
    fieldsets = (
        ('Información General', {
            'fields': ('event_type', 'field', 'campaign', 'timestamp')
        }),
        ('Datos de Monitoreo', {
            'fields': (
                'plaga_enfermedad', 'metodo_muestreo', 'incidencia', 'severidad',
                'ubicacion_campo', 'numero_muestras', 'accion_recomendada'
            )
        }),
        ('Observaciones', {
            'fields': ('observations',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OutbreakEvent)
class OutbreakEventAdmin(admin.ModelAdmin):
    list_display = ('field', 'campaign', 'tipo_problema', 'severidad', 'timestamp')
    list_filter = ('severidad', 'metodo_deteccion', 'requiere_tratamiento', 'timestamp', 'field', 'campaign')
    search_fields = ('tipo_problema', 'field__name', 'observations')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ['field', 'campaign', 'created_by']
    date_hierarchy = 'timestamp'
    inlines = [AttachmentInline]
    fieldsets = (
        ('Información General', {
            'fields': ('event_type', 'field', 'campaign', 'timestamp')
        }),
        ('Datos del Brote', {
            'fields': (
                'tipo_problema', 'severidad', 'metodo_deteccion',
                'area_afectada_ha', 'porcentaje_afectacion', 'requiere_tratamiento'
            )
        }),
        ('Acción', {
            'fields': ('accion_inmediata',)
        }),
        ('Observaciones', {
            'fields': ('observations',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ClimateEvent)
class ClimateEventAdmin(admin.ModelAdmin):
    list_display = ('field', 'campaign', 'temperatura_max', 'temperatura_min', 'timestamp')
    list_filter = ('viento', 'timestamp', 'field', 'campaign')
    search_fields = ('field__name', 'observations')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ['field', 'campaign', 'created_by']
    date_hierarchy = 'timestamp'
    inlines = [AttachmentInline]
    fieldsets = (
        ('Información General', {
            'fields': ('event_type', 'field', 'campaign', 'timestamp')
        }),
        ('Condiciones Climáticas', {
            'fields': (
                'temperatura_max', 'temperatura_min', 'humedad_relativa',
                'precipitacion_mm', 'velocidad_viento_ms', 'viento',
                'radiacion_solar_wm2'
            )
        }),
        ('Observaciones', {
            'fields': ('observations',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(HarvestEvent)
class HarvestEventAdmin(admin.ModelAdmin):
    list_display = ('field', 'campaign', 'volumen_kg', 'rendimiento_kg_ha', 'calidad', 'timestamp')
    list_filter = ('calidad', 'timestamp', 'field', 'campaign')
    search_fields = ('variedad', 'field__name', 'observations')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ['field', 'campaign', 'created_by']
    date_hierarchy = 'timestamp'
    inlines = [AttachmentInline]
    fieldsets = (
        ('Información General', {
            'fields': ('event_type', 'field', 'campaign', 'timestamp')
        }),
        ('Datos de Cosecha', {
            'fields': (
                'variedad', 'volumen_kg', 'rendimiento_kg_ha', 'calidad',
                'numero_trabajadores', 'horas_trabajo', 'fecha_inicio', 'fecha_fin'
            )
        }),
        ('Observaciones', {
            'fields': ('observations',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PostHarvestEvent)
class PostHarvestEventAdmin(admin.ModelAdmin):
    list_display = ('field', 'campaign', 'producto', 'cantidad_kg', 'temperatura', 'timestamp')
    list_filter = ('tipo_almacenamiento', 'timestamp', 'field', 'campaign')
    search_fields = ('producto', 'field__name', 'observations')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ['field', 'campaign', 'created_by']
    date_hierarchy = 'timestamp'
    inlines = [AttachmentInline]
    fieldsets = (
        ('Información General', {
            'fields': ('event_type', 'field', 'campaign', 'timestamp')
        }),
        ('Datos de Almacenamiento', {
            'fields': (
                'producto', 'cantidad_kg', 'temperatura', 'humedad',
                'tipo_almacenamiento', 'fecha_ingreso', 'fecha_salida_prevista'
            )
        }),
        ('Condiciones', {
            'fields': ('condiciones_observadas',)
        }),
        ('Observaciones', {
            'fields': ('observations',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LaborCostEvent)
class LaborCostEventAdmin(admin.ModelAdmin):
    list_display = ('field', 'campaign', 'actividad', 'numero_trabajadores', 'costo_total', 'timestamp')
    list_filter = ('actividad', 'timestamp', 'field', 'campaign')
    search_fields = ('actividad', 'field__name', 'observations')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ['field', 'campaign', 'created_by']
    date_hierarchy = 'timestamp'
    inlines = [AttachmentInline]
    fieldsets = (
        ('Información General', {
            'fields': ('event_type', 'field', 'campaign', 'timestamp')
        }),
        ('Datos de Mano de Obra', {
            'fields': (
                'actividad', 'numero_trabajadores', 'horas_trabajo',
                'costo_hora', 'costo_total'
            ),
            'description': 'Nota: Si proporciona horas_trabajo y costo_hora, el costo_total se calculará automáticamente.'
        }),
        ('Observaciones', {
            'fields': ('observations',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at'),
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
