from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import Field, Campaign, Station
from .serializers import (
    FieldSerializer,
    FieldListSerializer,
    FieldCreateUpdateSerializer,
    CampaignSerializer,
    CampaignListSerializer,
    CampaignCreateUpdateSerializer,
    StationSerializer,
)


# ========== API Views ==========

@extend_schema(
    summary="Listar Campos",
    description="""
    Obtiene una lista de todos los campos (parcelas) registrados en el sistema.
    
    Los campos representan las parcelas físicas donde se realiza el cultivo de limón.
    Cada campo tiene una ubicación, superficie definida y puede estar asociado a múltiples campañas.
    
    **Casos de uso:**
    - Consultar todos los campos disponibles para asignar a campañas
    - Obtener información de superficie total cultivada
    - Filtrar campos por estado (activo/inactivo)
    """,
    tags=['Catálogos - Campos'],
    parameters=[
        OpenApiParameter(
            name='is_active',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description='Filtrar por estado: true (activos) o false (inactivos)',
            required=False,
        ),
    ],
    responses={
        200: FieldListSerializer(many=True),
    },
    examples=[
        OpenApiExample(
            'Campos activos',
            summary='Lista de campos activos',
            description='Ejemplo de respuesta con campos activos',
            value=[
                {
                    'id': '550e8400-e29b-41d4-a716-446655440000',
                    'code': 'FIELD-001',
                    'name': 'Parcela Norte',
                    'surface_ha': 2.50,
                    'is_active': True
                }
            ],
            response_only=True,
        ),
    ],
)
class FieldListView(generics.ListAPIView):
    """
    API endpoint para listar campos/parcelas.
    
    Permite filtrar por estado (activo/inactivo) mediante query parameters.
    """
    serializer_class = FieldListSerializer
    
    def get_queryset(self):
        queryset = Field.objects.all().order_by('-created_at')
        is_active = self.request.query_params.get('is_active')
        
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        return queryset


@extend_schema(
    summary="Listar Campañas",
    description="""
    Obtiene una lista de todas las campañas (ciclos productivos) registradas en el sistema.
    
    Las campañas representan ciclos productivos o temporadas de cultivo de limón en un campo específico.
    Cada campaña define la variedad cultivada, el período de tiempo y permite asociar eventos de trazabilidad.
    
    **Casos de uso:**
    - Consultar campañas disponibles para registro de eventos
    - Obtener información de ciclos productivos por temporada
    - Filtrar campañas activas o finalizadas
    """,
    tags=['Catálogos - Campañas'],
    parameters=[
        OpenApiParameter(
            name='is_active',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description='Filtrar por estado: true (activas) o false (inactivas)',
            required=False,
        ),
        OpenApiParameter(
            name='season',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filtrar por temporada (ej: "Verano 2024")',
            required=False,
        ),
    ],
    responses={
        200: CampaignListSerializer(many=True),
    },
    examples=[
        OpenApiExample(
            'Campañas activas',
            summary='Lista de campañas activas',
            description='Ejemplo de respuesta con campañas en curso',
            value=[
                {
                    'id': '550e8400-e29b-41d4-a716-446655440001',
                    'name': 'Campaña Verano 2024',
                    'season': 'Verano 2024',
                    'variety': 'Eureka',
                    'start_date': '2024-01-15',
                    'end_date': None,
                    'is_active': True
                }
            ],
            response_only=True,
        ),
    ],
)
class CampaignListView(generics.ListAPIView):
    """
    API endpoint para listar campañas de cultivo.
    
    Permite filtrar por estado y temporada mediante query parameters.
    """
    serializer_class = CampaignListSerializer
    
    def get_queryset(self):
        queryset = Campaign.objects.all().order_by('-start_date')
        is_active = self.request.query_params.get('is_active')
        season = self.request.query_params.get('season')
        
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        if season:
            queryset = queryset.filter(season__icontains=season)
        
        return queryset


# ========== Sensores / IoT API Views ==========

from django.http import JsonResponse
from .sensors import get_thingspeak_service


@extend_schema(
    summary="Obtener Datos de Sensores",
    description="""
    Obtiene datos históricos de sensores IoT desde la plataforma ThingSpeak.
    
    Este endpoint permite consultar mediciones de temperatura y humedad de sensores
    conectados al sistema de trazabilidad. Los datos se pueden filtrar por rango de fechas
    y número de registros.
    
    **Parámetros de filtrado:**
    - `results`: Número de registros a obtener (por defecto 20, máximo 8000)
    - `start_date`: Fecha de inicio en formato ISO (YYYY-MM-DDTHH:MM:SS)
    - `end_date`: Fecha de fin en formato ISO (YYYY-MM-DDTHH:MM:SS)
    
    **Casos de uso:**
    - Consultar últimas lecturas de sensores
    - Obtener histórico de temperatura y humedad
    - Filtrar datos por rango de fechas específico
    - Integrar con sistemas externos de monitoreo
    """,
    tags=['Sensores IoT'],
    parameters=[
        OpenApiParameter(
            name='results',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Número de registros a obtener (por defecto 20, máximo 8000)',
            required=False,
            default=20,
        ),
        OpenApiParameter(
            name='start_date',
            type=OpenApiTypes.DATETIME,
            location=OpenApiParameter.QUERY,
            description='Fecha de inicio en formato ISO (YYYY-MM-DDTHH:MM:SS)',
            required=False,
        ),
        OpenApiParameter(
            name='end_date',
            type=OpenApiTypes.DATETIME,
            location=OpenApiParameter.QUERY,
            description='Fecha de fin en formato ISO (YYYY-MM-DDTHH:MM:SS)',
            required=False,
        ),
    ],
    responses={
        200: OpenApiTypes.OBJECT,
        500: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            'Respuesta exitosa',
            summary='Datos de sensores con temperatura y humedad',
            description='Ejemplo de respuesta con datos históricos de sensores',
            value={
                'success': True,
                'data': {
                    'channel_id': 3142831,
                    'channel_name': 'Trazabilidad',
                    'description': 'Obtención de datos de sensores de temperatura, humedad relativa.',
                    'field_names': {
                        'field1': 'Temperature',
                        'field2': 'Humidity'
                    },
                    'feeds': [
                        {
                            'timestamp': '2025-11-15T18:04:38Z',
                            'entry_id': 305,
                            'temperature': 28.0,
                            'humidity': 68.0
                        },
                        {
                            'timestamp': '2025-11-15T18:06:38Z',
                            'entry_id': 306,
                            'temperature': 28.0,
                            'humidity': 67.0
                        }
                    ]
                }
            },
            response_only=True,
        ),
        OpenApiExample(
            'Filtrado por últimos 50 registros',
            summary='Solicitud con parámetro results',
            description='Ejemplo de solicitud para obtener los últimos 50 registros',
            value={'results': 50},
            request_only=True,
        ),
        OpenApiExample(
            'Filtrado por rango de fechas',
            summary='Solicitud con rango de fechas',
            description='Ejemplo de solicitud con filtro de fechas',
            value={
                'start_date': '2025-11-15T00:00:00',
                'end_date': '2025-11-15T23:59:59',
                'results': 8000
            },
            request_only=True,
        ),
    ],
)
class SensorDataAPIView(APIView):
    """
    API endpoint para obtener datos de sensores IoT.
    
    Permite consultar mediciones de temperatura y humedad con filtros opcionales.
    """
    
    def get(self, request):
        """Obtiene datos históricos de sensores con filtros opcionales."""
        try:
            service = get_thingspeak_service()
            
            # Obtener parámetros de la petición
            results = int(request.GET.get('results', 20))
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            
            # Validar results
            if results < 1:
                return Response({
                    'success': False,
                    'error': 'El parámetro results debe ser mayor a 0'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if results > 8000:
                return Response({
                    'success': False,
                    'error': 'El parámetro results no puede ser mayor a 8000'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener datos históricos con filtros opcionales
            data = service.get_formatted_historical_data(
                results=results,
                start_date=start_date,
                end_date=end_date
            )
            
            if data:
                return Response({
                    'success': True,
                    'data': data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'No se pudieron obtener datos de los sensores'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except ValueError as e:
            return Response({
                'success': False,
                'error': f'Parámetro inválido: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Obtener Información del Canal de Sensores",
    description="""
    Obtiene información general del canal de sensores IoT.
    
    Este endpoint proporciona metadatos del canal ThingSpeak incluyendo:
    - ID del canal
    - Nombre del canal
    - Descripción
    - Campos disponibles (temperatura, humedad, etc.)
    - Fecha de creación y última actualización
    - Último entry_id registrado
    
    **Casos de uso:**
    - Obtener configuración del canal antes de consultar datos
    - Verificar disponibilidad de campos de sensores
    - Validar conectividad con ThingSpeak
    """,
    tags=['Sensores IoT'],
    responses={
        200: OpenApiTypes.OBJECT,
        500: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            'Información del canal',
            summary='Metadatos del canal de sensores',
            description='Ejemplo de respuesta con información del canal ThingSpeak',
            value={
                'success': True,
                'data': {
                    'channel': {
                        'id': 3142831,
                        'name': 'Trazabilidad',
                        'description': 'Obtención de datos de sensores de temperatura, humedad relativa.',
                        'latitude': '0.0',
                        'longitude': '0.0',
                        'field1': 'Temperature',
                        'field2': 'Humidity',
                        'created_at': '2025-11-01T18:37:44Z',
                        'updated_at': '2025-11-15T14:21:09Z',
                        'last_entry_id': 306
                    }
                }
            },
            response_only=True,
        ),
    ],
)
class SensorChannelInfoAPIView(APIView):
    """
    API endpoint para obtener información del canal de sensores.
    
    Proporciona metadatos del canal ThingSpeak.
    """
    
    def get(self, request):
        """Obtiene información general del canal de sensores."""
        try:
            service = get_thingspeak_service()
            
            # Obtener información del canal (1 registro para tener acceso a channel info)
            raw_data = service.get_latest_feeds(results=1)
            
            if raw_data and 'channel' in raw_data:
                return Response({
                    'success': True,
                    'data': {
                        'channel': raw_data['channel']
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'No se pudo obtener información del canal'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========== Template Views ==========

@login_required
def field_list_view(request):
    """Vista de lista de campos/parcelas."""
    fields_list = Field.objects.all().order_by('-created_at')
    
    # Búsqueda
    search = request.GET.get('search', '')
    if search:
        fields_list = fields_list.filter(
            name__icontains=search
        ) | fields_list.filter(
            code__icontains=search
        )
    
    # Filtro por estado
    status = request.GET.get('status', '')
    if status == 'active':
        fields_list = fields_list.filter(is_active=True)
    elif status == 'inactive':
        fields_list = fields_list.filter(is_active=False)
    
    # Paginación
    paginator = Paginator(fields_list, 10)
    page_number = request.GET.get('page')
    fields = paginator.get_page(page_number)
    
    context = {
        'fields': fields,
        'search': search,
        'status': status,
        'total_count': Field.objects.count(),
        'active_count': Field.objects.filter(is_active=True).count(),
    }
    return render(request, 'catalogs/field_list.html', context)


@login_required
def field_create_view(request):
    """Vista para crear un nuevo campo."""
    if request.method == 'POST':
        try:
            field = Field.objects.create(
                name=request.POST.get('name'),
                code=request.POST.get('code'),
                surface_ha=request.POST.get('surface_ha') or None,
                notes=request.POST.get('notes', ''),
                is_active=request.POST.get('is_active') == 'on'
            )
            messages.success(request, f'Campo "{field.name}" creado exitosamente.')
            return redirect('field_list')
        except Exception as e:
            messages.error(request, f'Error al crear campo: {str(e)}')
    
    return render(request, 'catalogs/field_form.html', {'action': 'Crear'})


@login_required
def field_edit_view(request, pk):
    """Vista para editar un campo existente."""
    field = get_object_or_404(Field, pk=pk)
    
    if request.method == 'POST':
        try:
            field.name = request.POST.get('name')
            field.code = request.POST.get('code')
            field.surface_ha = request.POST.get('surface_ha') or None
            field.notes = request.POST.get('notes', '')
            field.is_active = request.POST.get('is_active') == 'on'
            field.save()
            messages.success(request, f'Campo "{field.name}" actualizado exitosamente.')
            return redirect('field_list')
        except Exception as e:
            messages.error(request, f'Error al actualizar campo: {str(e)}')
    
    return render(request, 'catalogs/field_form.html', {
        'field': field,
        'action': 'Editar'
    })


@login_required
def field_delete_view(request, pk):
    """Vista para eliminar un campo."""
    field = get_object_or_404(Field, pk=pk)
    
    if request.method == 'POST':
        name = field.name
        field.delete()
        messages.success(request, f'Campo "{name}" eliminado exitosamente.')
        return redirect('field_list')
    
    return render(request, 'catalogs/field_confirm_delete.html', {'field': field})


@login_required
def campaign_list_view(request):
    """Vista de lista de campañas."""
    campaigns_list = Campaign.objects.all().order_by('-start_date')
    
    # Búsqueda
    search = request.GET.get('search', '')
    if search:
        campaigns_list = campaigns_list.filter(
            name__icontains=search
        ) | campaigns_list.filter(
            season__icontains=search
        ) | campaigns_list.filter(
            variety__icontains=search
        )
    
    # Filtro por estado
    status = request.GET.get('status', '')
    if status == 'active':
        campaigns_list = campaigns_list.filter(is_active=True)
    elif status == 'inactive':
        campaigns_list = campaigns_list.filter(is_active=False)
    
    # Paginación
    paginator = Paginator(campaigns_list, 10)
    page_number = request.GET.get('page')
    campaigns = paginator.get_page(page_number)
    
    context = {
        'campaigns': campaigns,
        'search': search,
        'status': status,
        'total_count': Campaign.objects.count(),
        'active_count': Campaign.objects.filter(is_active=True).count(),
    }
    return render(request, 'catalogs/campaign_list.html', context)


@login_required
def campaign_create_view(request):
    """Vista para crear una nueva campaña."""
    if request.method == 'POST':
        try:
            campaign = Campaign.objects.create(
                name=request.POST.get('name'),
                season=request.POST.get('season', ''),
                variety=request.POST.get('variety', ''),
                start_date=request.POST.get('start_date'),
                end_date=request.POST.get('end_date') or None,
                notes=request.POST.get('notes', ''),
                is_active=request.POST.get('is_active') == 'on'
            )
            messages.success(request, f'Campaña "{campaign.name}" creada exitosamente.')
            return redirect('campaign_list')
        except Exception as e:
            messages.error(request, f'Error al crear campaña: {str(e)}')
    
    return render(request, 'catalogs/campaign_form.html', {'action': 'Crear'})


@login_required
def campaign_edit_view(request, pk):
    """Vista para editar una campaña existente."""
    campaign = get_object_or_404(Campaign, pk=pk)
    
    if request.method == 'POST':
        try:
            campaign.name = request.POST.get('name')
            campaign.season = request.POST.get('season', '')
            campaign.variety = request.POST.get('variety', '')
            campaign.start_date = request.POST.get('start_date')
            campaign.end_date = request.POST.get('end_date') or None
            campaign.notes = request.POST.get('notes', '')
            campaign.is_active = request.POST.get('is_active') == 'on'
            campaign.save()
            messages.success(request, f'Campaña "{campaign.name}" actualizada exitosamente.')
            return redirect('campaign_list')
        except Exception as e:
            messages.error(request, f'Error al actualizar campaña: {str(e)}')
    
    return render(request, 'catalogs/campaign_form.html', {
        'campaign': campaign,
        'action': 'Editar'
    })


@login_required
def campaign_delete_view(request, pk):
    """Vista para eliminar una campaña."""
    campaign = get_object_or_404(Campaign, pk=pk)
    
    if request.method == 'POST':
        name = campaign.name
        campaign.delete()
        messages.success(request, f'Campaña "{name}" eliminada exitosamente.')
        return redirect('campaign_list')
    
    return render(request, 'catalogs/campaign_confirm_delete.html', {'campaign': campaign})


# ========== Sensores / IoT Views ==========

from django.http import JsonResponse
from .sensors import get_thingspeak_service


@login_required
def sensors_dashboard_view(request):
    """Vista del dashboard de sensores en tiempo real."""
    # Obtener estaciones disponibles
    stations = Station.objects.filter(is_operational=True).select_related('field')
    
    context = {
        'stations': stations,
    }
    return render(request, 'catalogs/sensors_dashboard.html', context)


@login_required
def sensors_data_api(request):
    """API para obtener datos de sensores en tiempo real."""
    try:
        service = get_thingspeak_service()
        
        # Obtener parámetros de la petición
        results = int(request.GET.get('results', 20))
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Obtener datos históricos con filtros opcionales
        data = service.get_formatted_historical_data(
            results=results,
            start_date=start_date,
            end_date=end_date
        )
        
        if data:
            return JsonResponse({
                'success': True,
                'data': data
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'No se pudieron obtener datos del sensor'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
