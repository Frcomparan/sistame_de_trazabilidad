"""
Serializers para la API de Eventos.
Incluye serialización de Eventos y Tipos de Eventos.
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import (
    Event, 
    EventType, 
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
from .event_models import EVENT_TYPE_MODEL_MAP


class EventTypeSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo EventType (Tipo de Evento).
    
    Los tipos de evento definen las categorías de actividades que pueden registrarse
    en el sistema de trazabilidad (riego, fertilización, cosecha, etc.).
    """
    
    class Meta:
        model = EventType
        fields = [
            'id',
            'name',
            'category',
            'description',
            'is_active',
            'icon',
            'color',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EventSerializer(serializers.ModelSerializer):
    """
    Serializer base para el modelo Event (Evento de trazabilidad).
    
    Los eventos representan actividades o registros que ocurren durante el ciclo
    de cultivo, como aplicaciones fitosanitarias, riegos, cosechas, etc.
    """
    
    # Campos relacionados expandidos
    event_type_detail = EventTypeSerializer(source='event_type', read_only=True)
    
    # Campos calculados
    event_type_name = serializers.CharField(
        source='event_type.name',
        read_only=True,
        help_text="Nombre del tipo de evento"
    )
    field_name = serializers.CharField(
        source='field.name',
        read_only=True,
        help_text="Nombre del campo"
    )
    campaign_name = serializers.CharField(
        source='campaign.name',
        read_only=True,
        help_text="Nombre de la campaña",
        allow_null=True
    )
    
    class Meta:
        model = Event
        fields = [
            'id',
            'event_type',
            'event_type_name',
            'event_type_detail',
            'field',
            'field_name',
            'campaign',
            'campaign_name',
            'timestamp',
            'observations',
            'created_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'event_type_name',
            'event_type_detail',
            'field_name',
            'campaign_name'
        ]


# Serializers específicos para cada tipo de evento
class IrrigationEventSerializer(EventSerializer):
    """Serializer para eventos de riego."""
    
    class Meta(EventSerializer.Meta):
        model = IrrigationEvent
        fields = EventSerializer.Meta.fields + [
            'metodo',
            'duracion_minutos',
            'fuente_agua',
            'volumen_m3',
            'presion_bar',
            'ce_uScm',
            'ph',
        ]


class FertilizationEventSerializer(EventSerializer):
    """Serializer para eventos de fertilización."""
    
    class Meta(EventSerializer.Meta):
        model = FertilizationEvent
        fields = EventSerializer.Meta.fields + [
            'producto',
            'metodo_aplicacion',
            'dosis',
            'unidad_dosis',
            'n_porcentaje',
            'p_porcentaje',
            'k_porcentaje',
            'volumen_caldo_l',
        ]


class PhytosanitaryEventSerializer(EventSerializer):
    """Serializer para eventos fitosanitarios."""
    
    class Meta(EventSerializer.Meta):
        model = PhytosanitaryEvent
        fields = EventSerializer.Meta.fields + [
            'producto',
            'ingrediente_activo',
            'tipo_producto',
            'objetivo',
            'metodo_aplicacion',
            'dosis',
            'unidad_dosis',
            'lote_producto',
            'volumen_caldo_l',
            'presion_bar',
            'intervalo_seguridad_dias',
            'responsable_aplicacion',
            'eficacia_observada',
            'fitotoxicidad',
        ]


class MaintenanceEventSerializer(EventSerializer):
    """Serializer para eventos de labores."""
    
    class Meta(EventSerializer.Meta):
        model = MaintenanceEvent
        fields = EventSerializer.Meta.fields + [
            'actividad',
            'herramienta_equipo',
            'numero_jornales',
            'horas_hombre',
            'objetivo',
            'porcentaje_completado',
            'herramientas_desinfectadas',
        ]


class MonitoringEventSerializer(EventSerializer):
    """Serializer para eventos de monitoreo."""
    
    class Meta(EventSerializer.Meta):
        model = MonitoringEvent
        fields = EventSerializer.Meta.fields + [
            'plaga_enfermedad',
            'metodo_muestreo',
            'incidencia',
            'severidad',
            'ubicacion_campo',
            'numero_muestras',
            'accion_recomendada',
        ]


class OutbreakEventSerializer(EventSerializer):
    """Serializer para eventos de brote."""
    
    class Meta(EventSerializer.Meta):
        model = OutbreakEvent
        fields = EventSerializer.Meta.fields + [
            'tipo_problema',
            'severidad',
            'metodo_deteccion',
            'area_afectada_ha',
            'porcentaje_afectacion',
            'accion_inmediata',
            'requiere_tratamiento',
        ]


class ClimateEventSerializer(EventSerializer):
    """Serializer para eventos climáticos."""
    
    class Meta(EventSerializer.Meta):
        model = ClimateEvent
        fields = EventSerializer.Meta.fields + [
            'temperatura_max',
            'temperatura_min',
            'humedad_relativa',
            'precipitacion_mm',
            'velocidad_viento_ms',
            'viento',
            'radiacion_solar_wm2',
        ]


class HarvestEventSerializer(EventSerializer):
    """Serializer para eventos de cosecha."""
    
    class Meta(EventSerializer.Meta):
        model = HarvestEvent
        fields = EventSerializer.Meta.fields + [
            'variedad',
            'volumen_kg',
            'rendimiento_kg_ha',
            'calidad',
            'numero_trabajadores',
            'horas_trabajo',
            'fecha_inicio',
            'fecha_fin',
        ]


class PostHarvestEventSerializer(EventSerializer):
    """Serializer para eventos poscosecha."""
    
    class Meta(EventSerializer.Meta):
        model = PostHarvestEvent
        fields = EventSerializer.Meta.fields + [
            'producto',
            'cantidad_kg',
            'temperatura',
            'humedad',
            'tipo_almacenamiento',
            'fecha_ingreso',
            'fecha_salida_prevista',
            'condiciones_observadas',
        ]


class LaborCostEventSerializer(EventSerializer):
    """Serializer para eventos de mano de obra."""
    
    class Meta(EventSerializer.Meta):
        model = LaborCostEvent
        fields = EventSerializer.Meta.fields + [
            'actividad',
            'numero_trabajadores',
            'horas_trabajo',
            'costo_hora',
            'costo_total',
        ]


# Mapeo de tipos de eventos a sus serializers
EVENT_SERIALIZER_MAP = {
    'Aplicación de Riego': IrrigationEventSerializer,
    'Aplicación de Fertilizante': FertilizationEventSerializer,
    'Aplicación Fitosanitaria': PhytosanitaryEventSerializer,
    'Labores de Cultivo': MaintenanceEventSerializer,
    'Monitoreo de Plagas': MonitoringEventSerializer,
    'Brote de Plaga/Enfermedad': OutbreakEventSerializer,
    'Condiciones Climáticas': ClimateEventSerializer,
    'Cosecha': HarvestEventSerializer,
    'Almacenamiento Poscosecha': PostHarvestEventSerializer,
    'Mano de Obra y Costos': LaborCostEventSerializer,
}


def get_event_serializer(event_type_name):
    """
    Obtiene el serializer apropiado para un tipo de evento.
    
    Args:
        event_type_name: Nombre del tipo de evento
        
    Returns:
        Clase del serializer o EventSerializer base si no se encuentra
    """
    return EVENT_SERIALIZER_MAP.get(event_type_name, EventSerializer)


class EventListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listado de eventos.
    Incluye solo los campos esenciales para optimizar la respuesta.
    """
    
    event_type_name = serializers.CharField(source='event_type.name', read_only=True)
    field_name = serializers.CharField(source='field.name', read_only=True)
    
    class Meta:
        model = Event
        fields = ['id', 'event_type', 'event_type_name', 'field', 'field_name', 'timestamp', 'observations']


class EventCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear eventos.
    Usa el serializer específico según el tipo de evento.
    """
    
    def to_internal_value(self, data):
        """Determina qué serializer usar basado en event_type."""
        event_type_id = data.get('event_type')
        
        if event_type_id:
            try:
                from .models import EventType
                event_type = EventType.objects.get(pk=event_type_id)
                serializer_class = get_event_serializer(event_type.name)
                
                # Si hay un serializer específico, usarlo
                if serializer_class != EventSerializer:
                    serializer = serializer_class(data=data)
                    serializer.is_valid(raise_exception=True)
                    return serializer.validated_data
            except EventType.DoesNotExist:
                pass
        
        # Fallback al serializer base
        return super().to_internal_value(data)
    
    class Meta:
        model = Event
        fields = ['event_type', 'field', 'campaign', 'timestamp', 'observations']
    
    def validate(self, data):
        """Valida que el tipo de evento esté activo."""
        event_type = data.get('event_type')
        
        if event_type and not event_type.is_active:
            raise serializers.ValidationError({
                'event_type': 'No se pueden crear eventos de un tipo inactivo.'
            })
        
        return data
