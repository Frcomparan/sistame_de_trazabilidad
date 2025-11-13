from rest_framework import views, response, status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime
import csv
import io

from apps.catalogs.models import Field, Campaign
from apps.events.models import EventType
from .generators import PDFReportGenerator, CSVExporter, ExcelExporter
from .serializers import (
    FieldTraceabilityReportSerializer,
    CampaignTraceabilityReportSerializer,
    ReportMetadataSerializer
)


@extend_schema(
    summary="Health Check",
    description="""
    Endpoint de verificación de estado del servicio (health check).
    
    Este endpoint permite verificar que el servicio API está funcionando correctamente
    y puede responder a peticiones.
    
    **Casos de uso:**
    - Monitoreo de disponibilidad del servicio
    - Validación en sistemas de balanceo de carga
    - Pruebas de conectividad
    - Verificación de despliegues
    
    **Respuesta:**
    - Status 200: El servicio está operativo
    - Incluye información básica del estado del sistema
    """,
    tags=['Sistema - Reportes'],
    responses={
        200: OpenApiResponse(
            description="Servicio operativo",
            response={
                'type': 'object',
                'properties': {
                    'status': {
                        'type': 'string',
                        'example': 'ok',
                        'description': 'Estado del servicio'
                    },
                    'service': {
                        'type': 'string',
                        'example': 'Sistema de Trazabilidad Agrícola',
                        'description': 'Nombre del servicio'
                    },
                    'version': {
                        'type': 'string',
                        'example': '1.0.0',
                        'description': 'Versión de la API'
                    }
                }
            }
        ),
    },
)
class HealthCheckView(views.APIView):
    """
    API endpoint para verificación de estado del servicio.
    
    Retorna un JSON simple indicando que el servicio está operativo.
    """
    
    def get(self, request):
        """
        Verifica el estado del servicio.
        
        Returns:
            Response: JSON con el estado del servicio
        """
        return response.Response({
            'status': 'ok',
            'service': 'Sistema de Trazabilidad Agrícola',
            'version': '1.0.0',
        }, status=status.HTTP_200_OK)


# ==================== VISTAS WEB ====================

@login_required
@require_http_methods(["GET"])
def reports_dashboard_view(request):
    """
    Dashboard principal de reportes.
    """
    context = {
        'page_title': 'Sistema de Reportes',
        'fields': Field.objects.filter(is_active=True).order_by('name'),
        'campaigns': Campaign.objects.all().order_by('-start_date'),
        'event_types': EventType.objects.all().order_by('name'),
    }
    return render(request, 'reports/dashboard.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def traceability_report_view(request):
    """
    Vista para generar reporte de trazabilidad.
    GET: Muestra formulario
    POST: Genera el reporte en el formato solicitado
    """
    if request.method == 'GET':
        context = {
            'page_title': 'Reporte de Trazabilidad',
            'fields': Field.objects.filter(is_active=True).order_by('name'),
            'campaigns': Campaign.objects.all().order_by('-start_date'),
            'event_types': EventType.objects.all().order_by('name'),
        }
        return render(request, 'reports/traceability_form.html', context)
    
    # POST - Generar reporte
    field_id = request.POST.get('field_id')
    date_from = request.POST.get('date_from')
    date_to = request.POST.get('date_to')
    campaign_id = request.POST.get('campaign_id')
    export_format = request.POST.get('format', 'pdf')
    event_types = request.POST.getlist('event_types')
    
    # Validar campo requerido
    if not field_id:
        context = {
            'page_title': 'Reporte de Trazabilidad',
            'fields': Field.objects.filter(is_active=True).order_by('name'),
            'campaigns': Campaign.objects.all().order_by('-start_date'),
            'event_types': EventType.objects.all().order_by('name'),
            'error': 'Debe seleccionar un lote'
        }
        return render(request, 'reports/traceability_form.html', context)
    
    # Convertir fechas y preparar parámetros
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    # No convertir IDs a int, son UUIDs (strings)
    campaign_id_val = campaign_id if campaign_id else None
    event_types_list = event_types if event_types else None
    
    try:
        if export_format == 'pdf':
            # Generar PDF
            generator = PDFReportGenerator()
            pdf_buffer = generator.generate_traceability_report(
                field_id=field_id,
                date_from=date_from_obj,
                date_to=date_to_obj,
                campaign_id=campaign_id_val,
                event_types=event_types_list
            )
            
            field = Field.objects.get(id=field_id)
            filename = f"trazabilidad_{field.code}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            response = FileResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        elif export_format == 'csv':
            # Generar CSV
            exporter = CSVExporter()
            data = exporter.export_events(
                field_id=field_id,
                date_from=date_from_obj,
                date_to=date_to_obj,
                event_types=event_types_list
            )
            
            field = Field.objects.get(id=field_id)
            filename = f"eventos_{field.code}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response.write('\ufeff')  # BOM para Excel
            
            writer = csv.DictWriter(response, fieldnames=data[0].keys() if data else [])
            writer.writeheader()
            writer.writerows(data)
            
            return response
            
        elif export_format == 'excel':
            # Generar Excel
            exporter = ExcelExporter()
            excel_buffer = exporter.export_events(
                field_id=field_id,
                date_from=date_from_obj,
                date_to=date_to_obj,
                event_types=event_types_list
            )
            
            field = Field.objects.get(id=field_id)
            filename = f"eventos_{field.code}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            response = FileResponse(
                excel_buffer,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    
    except Exception as e:
        context = {
            'page_title': 'Reporte de Trazabilidad',
            'fields': Field.objects.filter(is_active=True).order_by('name'),
            'campaigns': Campaign.objects.all().order_by('-start_date'),
            'event_types': EventType.objects.all().order_by('name'),
            'error': f'Error al generar el reporte: {str(e)}'
        }
        return render(request, 'reports/traceability_form.html', context)


@login_required
@require_http_methods(["GET"])
def export_events_view(request):
    """
    Vista para exportar eventos masivamente.
    """
    export_format = request.GET.get('format', 'csv')
    field_id = request.GET.get('field_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Convertir parámetros (IDs son UUIDs, no convertir a int)
    field_id_val = field_id if field_id else None
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    
    try:
        if export_format == 'csv':
            exporter = CSVExporter()
            data = exporter.export_events(
                field_id=field_id_val,
                date_from=date_from_obj,
                date_to=date_to_obj
            )
            
            filename = f"eventos_export_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response.write('\ufeff')  # BOM para Excel
            
            if data:
                writer = csv.DictWriter(response, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            return response
            
        elif export_format == 'excel':
            exporter = ExcelExporter()
            excel_buffer = exporter.export_events(
                field_id=field_id_val,
                date_from=date_from_obj,
                date_to=date_to_obj
            )
            
            filename = f"eventos_export_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            response = FileResponse(
                excel_buffer,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
    except Exception as e:
        return HttpResponse(f'Error al exportar datos: {str(e)}', status=500)


@login_required
@require_http_methods(["GET", "POST"])
def campaign_traceability_report_view(request):
    """
    Vista para generar reporte de trazabilidad por campaña.
    GET: Muestra formulario
    POST: Genera el reporte en el formato solicitado
    """
    if request.method == 'GET':
        context = {
            'page_title': 'Reporte de Trazabilidad por Campaña',
            'fields': Field.objects.filter(is_active=True).order_by('name'),
            'campaigns': Campaign.objects.all().order_by('-start_date'),
            'event_types': EventType.objects.all().order_by('name'),
        }
        return render(request, 'reports/campaign_traceability_form.html', context)
    
    # POST - Generar reporte
    campaign_id = request.POST.get('campaign_id')
    field_ids = request.POST.getlist('field_ids')  # Múltiples lotes opcionales
    event_types = request.POST.getlist('event_types')
    export_format = request.POST.get('format', 'pdf')
    
    # Validar campaña requerida
    if not campaign_id:
        context = {
            'page_title': 'Reporte de Trazabilidad por Campaña',
            'fields': Field.objects.filter(is_active=True).order_by('name'),
            'campaigns': Campaign.objects.all().order_by('-start_date'),
            'event_types': EventType.objects.all().order_by('name'),
            'error': 'Debe seleccionar una campaña'
        }
        return render(request, 'reports/campaign_traceability_form.html', context)
    
    # Preparar parámetros
    field_ids_list = field_ids if field_ids else None
    event_types_list = event_types if event_types else None
    
    try:
        if export_format == 'pdf':
            # Generar PDF
            generator = PDFReportGenerator()
            pdf_buffer = generator.generate_campaign_traceability_report(
                campaign_id=campaign_id,
                field_ids=field_ids_list,
                event_types=event_types_list
            )
            
            campaign = Campaign.objects.get(id=campaign_id)
            filename = f"trazabilidad_campana_{campaign.name.replace(' ', '_')}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            response = FileResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        elif export_format == 'csv':
            # Generar CSV
            exporter = CSVExporter()
            data = exporter.export_campaign_events(
                campaign_id=campaign_id,
                field_ids=field_ids_list,
                event_types=event_types_list
            )
            
            campaign = Campaign.objects.get(id=campaign_id)
            filename = f"eventos_campana_{campaign.name.replace(' ', '_')}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response.write('\ufeff')  # BOM para Excel
            
            writer = csv.DictWriter(response, fieldnames=data[0].keys() if data else [])
            writer.writeheader()
            writer.writerows(data)
            
            return response
            
        elif export_format == 'excel':
            # Generar Excel
            exporter = ExcelExporter()
            excel_buffer = exporter.export_campaign_events(
                campaign_id=campaign_id,
                field_ids=field_ids_list,
                event_types=event_types_list
            )
            
            campaign = Campaign.objects.get(id=campaign_id)
            filename = f"eventos_campana_{campaign.name.replace(' ', '_')}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            response = FileResponse(
                excel_buffer,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    
    except Exception as e:
        context = {
            'page_title': 'Reporte de Trazabilidad por Campaña',
            'fields': Field.objects.filter(is_active=True).order_by('name'),
            'campaigns': Campaign.objects.all().order_by('-start_date'),
            'event_types': EventType.objects.all().order_by('name'),
            'error': f'Error al generar el reporte: {str(e)}'
        }
        return render(request, 'reports/campaign_traceability_form.html', context)


# ==================== VISTAS API ====================

@extend_schema(
    summary="Listar tipos de reportes disponibles",
    description="""
    Obtiene información sobre los tipos de reportes disponibles en el sistema.
    
    Este endpoint proporciona metadatos sobre cada tipo de reporte:
    - Tipo y descripción del reporte
    - Formatos de exportación disponibles
    - Endpoint correspondiente para generar el reporte
    
    **Reportes disponibles:**
    1. **Trazabilidad por Lote**: Reporte completo de un lote específico
    2. **Trazabilidad por Campaña**: Reporte consolidado de una campaña
    
    **Formatos soportados:**
    - PDF: Documento profesional para impresión/presentación
    - Excel: Hojas de cálculo con datos y análisis
    - CSV: Datos tabulares para análisis externo
    """,
    tags=['Reportes API'],
    responses={
        200: OpenApiResponse(
            response=ReportMetadataSerializer(many=True),
            description="Lista de reportes disponibles"
        ),
    },
)
class ReportTypesListView(views.APIView):
    """
    Lista los tipos de reportes disponibles con sus metadatos.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Retorna información sobre los reportes disponibles.
        """
        reports = [
            {
                'report_type': 'field_traceability',
                'description': 'Reporte de trazabilidad completo de un lote específico con historial de eventos',
                'formats': ['pdf', 'excel', 'csv'],
                'endpoint': '/api/v1/reports/field-traceability/'
            },
            {
                'report_type': 'campaign_traceability',
                'description': 'Reporte consolidado de todos los eventos de una campaña agrícola',
                'formats': ['pdf', 'excel', 'csv'],
                'endpoint': '/api/v1/reports/campaign-traceability/'
            }
        ]
        
        serializer = ReportMetadataSerializer(reports, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Generar reporte de trazabilidad por lote",
    description="""
    Genera un reporte de trazabilidad completo para un lote específico.
    
    El reporte incluye:
    - Información general del lote (ubicación, superficie, cultivo)
    - Resumen estadístico de eventos registrados
    - Línea de tiempo completa de actividades
    - Detalles de cada evento (tipo, fecha, responsable, observaciones)
    - Distribución de eventos por tipo
    - Lista de archivos adjuntos
    
    **Filtros opcionales:**
    - Rango de fechas (date_from, date_to)
    - Campaña específica (campaign_id)
    - Tipos de eventos (event_types)
    
    **Formatos de salida:**
    - **PDF**: Documento profesional con diseño formal
    - **Excel**: Múltiples hojas con datos, estadísticas y gráficos
    - **CSV**: Datos tabulares simples para importación
    
    **Nota:** La respuesta será un archivo binario del formato seleccionado.
    """,
    tags=['Reportes API'],
    request=FieldTraceabilityReportSerializer,
    responses={
        200: OpenApiResponse(
            description="Archivo del reporte en el formato solicitado",
            response=OpenApiTypes.BINARY
        ),
        400: OpenApiResponse(
            description="Parámetros inválidos",
            response={
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'El campo field_id es requerido'}
                }
            }
        ),
        404: OpenApiResponse(
            description="Lote no encontrado",
            response={
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'El lote especificado no existe'}
                }
            }
        ),
    },
    examples=[
        OpenApiExample(
            'Reporte PDF básico',
            value={
                'field_id': '123e4567-e89b-12d3-a456-426614174000',
                'format': 'pdf'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Reporte Excel con filtros',
            value={
                'field_id': '123e4567-e89b-12d3-a456-426614174000',
                'date_from': '2024-01-01',
                'date_to': '2024-12-31',
                'campaign_id': '987e6543-e21b-43d3-a456-426614174999',
                'event_types': [
                    '111e1111-e11b-11d3-a456-426614174111',
                    '222e2222-e22b-22d3-a456-426614174222'
                ],
                'format': 'excel'
            },
            request_only=True,
        ),
    ],
)
class FieldTraceabilityReportView(views.APIView):
    """
    Genera reportes de trazabilidad por lote.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Genera y retorna el reporte en el formato especificado.
        """
        serializer = FieldTraceabilityReportSerializer(data=request.data)
        
        if not serializer.is_valid():
            return response.Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = serializer.validated_data
        field_id = str(data['field_id'])
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        campaign_id = str(data['campaign_id']) if data.get('campaign_id') else None
        event_types = [str(et) for et in data.get('event_types', [])] if data.get('event_types') else None
        export_format = data.get('format', 'pdf')
        
        # Verificar que el lote existe
        field = get_object_or_404(Field, id=field_id)
        
        try:
            if export_format == 'pdf':
                generator = PDFReportGenerator()
                pdf_buffer = generator.generate_traceability_report(
                    field_id=field_id,
                    date_from=date_from,
                    date_to=date_to,
                    campaign_id=campaign_id,
                    event_types=event_types
                )
                
                filename = f"trazabilidad_{field.code}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
                response_obj = FileResponse(pdf_buffer, content_type='application/pdf')
                response_obj['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response_obj
                
            elif export_format == 'csv':
                exporter = CSVExporter()
                data = exporter.export_events(
                    field_id=field_id,
                    date_from=date_from,
                    date_to=date_to,
                    event_types=event_types
                )
                
                filename = f"eventos_{field.code}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
                
                response_obj = HttpResponse(content_type='text/csv; charset=utf-8')
                response_obj['Content-Disposition'] = f'attachment; filename="{filename}"'
                response_obj.write('\ufeff')  # BOM para Excel
                
                if data:
                    writer = csv.DictWriter(response_obj, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                
                return response_obj
                
            elif export_format == 'excel':
                exporter = ExcelExporter()
                excel_buffer = exporter.export_events(
                    field_id=field_id,
                    date_from=date_from,
                    date_to=date_to,
                    event_types=event_types
                )
                
                filename = f"eventos_{field.code}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                
                response_obj = FileResponse(
                    excel_buffer,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response_obj['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response_obj
                
        except Exception as e:
            return response.Response(
                {'error': f'Error al generar el reporte: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    summary="Generar reporte de trazabilidad por campaña",
    description="""
    Genera un reporte consolidado de trazabilidad para una campaña completa.
    
    El reporte incluye:
    - Información general de la campaña (nombre, fechas, estado)
    - Estadísticas consolidadas de todos los lotes
    - Resumen de eventos por tipo de actividad
    - Detalle de eventos por cada lote
    - Comparativas entre lotes
    - Distribución temporal de actividades
    - Totales de insumos utilizados
    
    **Filtros opcionales:**
    - Lotes específicos (field_ids) - si está vacío incluye todos los lotes de la campaña
    - Tipos de eventos (event_types) - si está vacío incluye todos los tipos
    
    **Formatos de salida:**
    - **PDF**: Reporte formal con gráficos y tablas
    - **Excel**: Múltiples hojas con análisis detallado
    - **CSV**: Datos consolidados en formato tabular
    
    **Nota:** La respuesta será un archivo binario del formato seleccionado.
    """,
    tags=['Reportes API'],
    request=CampaignTraceabilityReportSerializer,
    responses={
        200: OpenApiResponse(
            description="Archivo del reporte en el formato solicitado",
            response=OpenApiTypes.BINARY
        ),
        400: OpenApiResponse(
            description="Parámetros inválidos",
            response={
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'El campo campaign_id es requerido'}
                }
            }
        ),
        404: OpenApiResponse(
            description="Campaña no encontrada",
            response={
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'La campaña especificada no existe'}
                }
            }
        ),
    },
    examples=[
        OpenApiExample(
            'Reporte PDF de campaña completa',
            value={
                'campaign_id': '789e4567-e89b-12d3-a456-426614174789',
                'format': 'pdf'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Reporte Excel filtrado',
            value={
                'campaign_id': '789e4567-e89b-12d3-a456-426614174789',
                'field_ids': [
                    '123e4567-e89b-12d3-a456-426614174000',
                    '456e7890-e89b-12d3-a456-426614174456'
                ],
                'event_types': [
                    '111e1111-e11b-11d3-a456-426614174111'
                ],
                'format': 'excel'
            },
            request_only=True,
        ),
    ],
)
class CampaignTraceabilityReportView(views.APIView):
    """
    Genera reportes de trazabilidad por campaña.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Genera y retorna el reporte de campaña en el formato especificado.
        """
        serializer = CampaignTraceabilityReportSerializer(data=request.data)
        
        if not serializer.is_valid():
            return response.Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = serializer.validated_data
        campaign_id = str(data['campaign_id'])
        field_ids = [str(fid) for fid in data.get('field_ids', [])] if data.get('field_ids') else None
        event_types = [str(et) for et in data.get('event_types', [])] if data.get('event_types') else None
        export_format = data.get('format', 'pdf')
        
        # Verificar que la campaña existe
        campaign = get_object_or_404(Campaign, id=campaign_id)
        
        try:
            if export_format == 'pdf':
                generator = PDFReportGenerator()
                pdf_buffer = generator.generate_campaign_traceability_report(
                    campaign_id=campaign_id,
                    field_ids=field_ids,
                    event_types=event_types
                )
                
                filename = f"trazabilidad_campana_{campaign.name.replace(' ', '_')}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
                response_obj = FileResponse(pdf_buffer, content_type='application/pdf')
                response_obj['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response_obj
                
            elif export_format == 'csv':
                exporter = CSVExporter()
                data = exporter.export_campaign_events(
                    campaign_id=campaign_id,
                    field_ids=field_ids,
                    event_types=event_types
                )
                
                filename = f"eventos_campana_{campaign.name.replace(' ', '_')}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
                
                response_obj = HttpResponse(content_type='text/csv; charset=utf-8')
                response_obj['Content-Disposition'] = f'attachment; filename="{filename}"'
                response_obj.write('\ufeff')  # BOM para Excel
                
                if data:
                    writer = csv.DictWriter(response_obj, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                
                return response_obj
                
            elif export_format == 'excel':
                exporter = ExcelExporter()
                excel_buffer = exporter.export_campaign_events(
                    campaign_id=campaign_id,
                    field_ids=field_ids,
                    event_types=event_types
                )
                
                filename = f"eventos_campana_{campaign.name.replace(' ', '_')}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                
                response_obj = FileResponse(
                    excel_buffer,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response_obj['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response_obj
                
        except Exception as e:
            return response.Response(
                {'error': f'Error al generar el reporte: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
