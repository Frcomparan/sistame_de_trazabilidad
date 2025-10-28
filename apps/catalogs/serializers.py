"""
Serializers para la API de Catálogos.
Incluye serialización de Campos (Fields), Campañas (Campaigns) y Estaciones (Stations).
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Field, Campaign, Station


class FieldSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Field (Campo/Parcela).
    
    Los campos representan las parcelas físicas donde se realiza el cultivo de limón.
    Cada campo tiene una ubicación, superficie y puede estar asociado a múltiples campañas.
    """
    
    # Campos calculados/adicionales
    status_display = serializers.SerializerMethodField(
        help_text="Estado del campo en formato legible"
    )
    
    class Meta:
        model = Field
        fields = [
            'id',
            'code',
            'name',
            'surface_ha',
            'notes',
            'is_active',
            'status_display',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status_display']
    
    @extend_schema_field(serializers.CharField)
    def get_status_display(self, obj):
        """Retorna el estado del campo en formato legible."""
        return "Activo" if obj.is_active else "Inactivo"


class FieldListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listado de campos.
    Incluye solo los campos esenciales para optimizar la respuesta.
    """
    
    class Meta:
        model = Field
        fields = ['id', 'code', 'name', 'surface_ha', 'is_active']


class FieldCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y actualizar campos.
    Incluye validaciones específicas para la creación/actualización.
    """
    
    class Meta:
        model = Field
        fields = ['code', 'name', 'surface_ha', 'notes', 'is_active']
    
    def validate_code(self, value):
        """Valida que el código sea único."""
        instance = self.instance
        if Field.objects.filter(code=value).exclude(
            pk=instance.pk if instance else None
        ).exists():
            raise serializers.ValidationError(
                "Ya existe un campo con este código."
            )
        return value
    
    def validate_surface_ha(self, value):
        """Valida que la superficie sea un valor positivo."""
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "La superficie debe ser un valor positivo."
            )
        return value


class CampaignSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Campaign (Campaña de cultivo).
    
    Las campañas representan ciclos productivos o temporadas de cultivo de limón.
    Cada campaña define la variedad cultivada, período de tiempo y está asociada a eventos.
    """
    
    # Campos calculados/adicionales
    status_display = serializers.SerializerMethodField(
        help_text="Estado de la campaña en formato legible"
    )
    duration_days = serializers.SerializerMethodField(
        help_text="Duración de la campaña en días (si tiene fecha de fin)"
    )
    
    class Meta:
        model = Campaign
        fields = [
            'id',
            'name',
            'season',
            'variety',
            'start_date',
            'end_date',
            'notes',
            'is_active',
            'status_display',
            'duration_days',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status_display', 'duration_days']
    
    @extend_schema_field(serializers.CharField)
    def get_status_display(self, obj):
        """Retorna el estado de la campaña en formato legible."""
        return "Activa" if obj.is_active else "Inactiva"
    
    @extend_schema_field(serializers.IntegerField)
    def get_duration_days(self, obj):
        """Calcula la duración de la campaña en días."""
        if obj.end_date:
            return (obj.end_date - obj.start_date).days
        return None


class CampaignListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listado de campañas.
    Incluye solo los campos esenciales para optimizar la respuesta.
    """
    
    class Meta:
        model = Campaign
        fields = ['id', 'name', 'season', 'variety', 'start_date', 'end_date', 'is_active']


class CampaignCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y actualizar campañas.
    Incluye validaciones específicas para la creación/actualización.
    """
    
    class Meta:
        model = Campaign
        fields = ['name', 'season', 'variety', 'start_date', 'end_date', 'notes', 'is_active']
    
    def validate(self, data):
        """Valida que la fecha de fin sea posterior a la fecha de inicio."""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({
                'end_date': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })
        
        return data


class StationSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Station (Estación de monitoreo).
    
    Las estaciones representan dispositivos IoT o puntos de monitoreo en los campos.
    Recopilan datos ambientales y de cultivo para trazabilidad.
    """
    
    # Campos calculados/adicionales
    status_display = serializers.SerializerMethodField(
        help_text="Estado de la estación en formato legible"
    )
    
    class Meta:
        model = Station
        fields = [
            'id',
            'code',
            'name',
            'location',
            'notes',
            'is_active',
            'status_display',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status_display']
    
    @extend_schema_field(serializers.CharField)
    def get_status_display(self, obj):
        """Retorna el estado de la estación en formato legible."""
        return "Activa" if obj.is_active else "Inactiva"
