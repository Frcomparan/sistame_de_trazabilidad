"""
Serializers for Reports API.
"""
from rest_framework import serializers


class FieldTraceabilityReportSerializer(serializers.Serializer):
    """Serializer para parámetros del reporte de trazabilidad por lote."""
    
    field_id = serializers.UUIDField(
        required=True,
        help_text="ID del lote para el cual generar el reporte"
    )
    date_from = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="Fecha de inicio del período (opcional, formato: YYYY-MM-DD)"
    )
    date_to = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="Fecha de fin del período (opcional, formato: YYYY-MM-DD)"
    )
    campaign_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="ID de la campaña para filtrar (opcional)"
    )
    event_types = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
        help_text="Lista de IDs de tipos de eventos a incluir (opcional)"
    )
    format = serializers.ChoiceField(
        choices=['pdf', 'excel', 'csv'],
        default='pdf',
        help_text="Formato de exportación: pdf, excel o csv"
    )


class CampaignTraceabilityReportSerializer(serializers.Serializer):
    """Serializer para parámetros del reporte de trazabilidad por campaña."""
    
    campaign_id = serializers.UUIDField(
        required=True,
        help_text="ID de la campaña para la cual generar el reporte"
    )
    field_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
        help_text="Lista de IDs de lotes específicos a incluir (opcional, vacío = todos)"
    )
    event_types = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
        help_text="Lista de IDs de tipos de eventos a incluir (opcional, vacío = todos)"
    )
    format = serializers.ChoiceField(
        choices=['pdf', 'excel', 'csv'],
        default='pdf',
        help_text="Formato de exportación: pdf, excel o csv"
    )


class ReportMetadataSerializer(serializers.Serializer):
    """Serializer para metadatos de reportes disponibles."""
    
    report_type = serializers.CharField(help_text="Tipo de reporte")
    description = serializers.CharField(help_text="Descripción del reporte")
    formats = serializers.ListField(
        child=serializers.CharField(),
        help_text="Formatos disponibles"
    )
    endpoint = serializers.CharField(help_text="Endpoint de la API")
