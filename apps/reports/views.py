from rest_framework import views, response, status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime
import csv

from apps.catalogs.models import Field, Campaign
from apps.events.models import EventType
from .generators import PDFReportGenerator, CSVExporter, ExcelExporter


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


