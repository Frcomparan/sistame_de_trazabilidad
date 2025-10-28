"""
Serializers para la API de Eventos.
Incluye serialización de Eventos y Tipos de Eventos.
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Event, EventType


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
            'schema',
            'version',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EventSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Event (Evento de trazabilidad).
    
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
            'payload',
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
    
    def validate_payload(self, value):
        """Valida que el campo payload sea un diccionario JSON válido."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "El campo 'payload' debe ser un objeto JSON válido."
            )
        return value


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
    Incluye validaciones específicas para la creación.
    """
    
    class Meta:
        model = Event
        fields = ['event_type', 'field', 'campaign', 'timestamp', 'payload', 'observations']
    
    def validate(self, data):
        """Valida que el tipo de evento esté activo."""
        event_type = data.get('event_type')
        
        if event_type and not event_type.is_active:
            raise serializers.ValidationError({
                'event_type': 'No se pueden crear eventos de un tipo inactivo.'
            })
        
        return data
