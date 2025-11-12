from rest_framework import generics, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
import pytz
from django.http import JsonResponse
from .models import Event, EventType, Attachment
from apps.catalogs.models import Field, Campaign
from .forms import get_event_form, EVENT_FORM_MAP
from .event_models import get_event_model, EVENT_TYPE_MODEL_MAP
from .serializers import (
    EventSerializer, 
    EventListSerializer, 
    EventTypeSerializer,
    EventCreateSerializer,
    get_event_serializer,
)


# ========== API Views ==========


@extend_schema(
    summary="Listar Eventos",
    description="""
    Obtiene una lista de todos los eventos de trazabilidad registrados en el sistema.
    
    Los eventos representan actividades que ocurren durante el ciclo de cultivo como:
    - Aplicaciones fitosanitarias
    - Riegos y fertilizaciones
    - Cosechas
    - Podas y labores culturales
    - Monitoreo de plagas y enfermedades
    
    **Casos de uso:**
    - Consultar historial de actividades por campo o campaña
    - Auditar trazabilidad de productos
    - Generar reportes de actividades
    - Análisis de prácticas agrícolas
    """,
    tags=['Eventos de Trazabilidad'],
    parameters=[
        OpenApiParameter(
            name='event_type',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.QUERY,
            description='Filtrar por tipo de evento (UUID)',
            required=False,
        ),
        OpenApiParameter(
            name='date_from',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description='Fecha inicial para filtrar eventos (formato: YYYY-MM-DD)',
            required=False,
        ),
        OpenApiParameter(
            name='date_to',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description='Fecha final para filtrar eventos (formato: YYYY-MM-DD)',
            required=False,
        ),
    ],
    responses={
        200: EventListSerializer(many=True),
    },
    examples=[
        OpenApiExample(
            'Eventos registrados',
            summary='Lista de eventos',
            description='Ejemplo de respuesta con eventos de trazabilidad',
            value=[
                {
                    'id': '550e8400-e29b-41d4-a716-446655440010',
                    'event_type': '550e8400-e29b-41d4-a716-446655440020',
                    'event_type_name': 'Riego',
                    'field': '550e8400-e29b-41d4-a716-446655440000',
                    'field_name': 'Parcela Norte',
                    'timestamp': '2024-10-27T10:30:00Z',
                    'observations': 'Riego por goteo - 2 horas'
                }
            ],
            response_only=True,
        ),
    ],
)
class EventListView(generics.ListAPIView):
    """
    API endpoint para listar eventos de trazabilidad.
    
    Permite filtrar por tipo de evento y rango de fechas mediante query parameters.
    """
    serializer_class = EventListSerializer
    
    def get_queryset(self):
        queryset = Event.objects.all().select_related('event_type').order_by('-timestamp')
        
        # Filtrar por tipo de evento
        event_type = self.request.query_params.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type_id=event_type)
        
        # Filtrar por rango de fechas
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        
        return queryset


@extend_schema(
    summary="Listar Tipos de Eventos",
    description="""
    Obtiene una lista de todos los tipos de eventos disponibles en el sistema.
    
    Los tipos de eventos definen las categorías de actividades que pueden registrarse:
    - Riego
    - Fertilización
    - Aplicación fitosanitaria
    - Cosecha
    - Poda
    - Monitoreo
    - Otros
    
    **Casos de uso:**
    - Consultar tipos disponibles para crear nuevos eventos
    - Validar esquemas JSON de datos de eventos
    - Obtener categorías para filtros en reportes
    """,
    tags=['Eventos de Trazabilidad'],
    parameters=[
        OpenApiParameter(
            name='category',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filtrar por categoría de evento',
            required=False,
        ),
        OpenApiParameter(
            name='is_active',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description='Filtrar por estado: true (activos) o false (inactivos)',
            required=False,
        ),
    ],
    responses={
        200: EventTypeSerializer(many=True),
    },
)
class EventTypeListView(generics.ListAPIView):
    """
    API endpoint para listar tipos de eventos.
    
    Permite filtrar por categoría y estado mediante query parameters.
    """
    serializer_class = EventTypeSerializer
    
    def get_queryset(self):
        queryset = EventType.objects.all().order_by('name')
        
        category = self.request.query_params.get('category')
        is_active = self.request.query_params.get('is_active')
        
        if category:
            queryset = queryset.filter(category__icontains=category)
        
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        return queryset


@extend_schema(
    summary="Crear Evento",
    description="""
    Crea un nuevo evento de trazabilidad.
    
    El tipo de evento determina qué campos específicos se requieren.
    
    **Casos de uso:**
    - Registrar aplicación fitosanitaria
    - Registrar riego o fertilización
    - Registrar cosecha
    - Registrar cualquier actividad definida en los tipos de eventos
    
    **Validación:**
    - El tipo de evento debe estar activo
    - El campo debe existir y estar activo
    - Los campos requeridos dependen del tipo de evento seleccionado
    - La campaña (opcional) debe pertenecer al campo
    """,
    tags=['Eventos de Trazabilidad'],
    request=EventCreateSerializer,
    responses={
        201: EventSerializer,
        400: OpenApiResponse(description="Datos inválidos o campos requeridos faltantes"),
    },
)
class EventCreateView(generics.CreateAPIView):
    """
    API endpoint para crear eventos de trazabilidad.
    
    Crea un evento usando el modelo específico según el tipo de evento.
    """
    serializer_class = EventCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Obtener el tipo de evento y determinar el modelo específico
        event_type = serializer.validated_data['event_type']
        model_class = get_event_model(event_type.name)
        serializer_class = get_event_serializer(event_type.name)
        
        # Si hay un serializer específico, usarlo
        if serializer_class != EventSerializer:
            specific_serializer = serializer_class(data=request.data)
            specific_serializer.is_valid(raise_exception=True)
            event = specific_serializer.save(
                event_type=event_type,
                created_by=request.user if request.user.is_authenticated else None
            )
            response_serializer = serializer_class(event)
        else:
            # Fallback al serializer base
            event = serializer.save(created_by=request.user if request.user.is_authenticated else None)
            response_serializer = EventSerializer(event)
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


# ========== Template Views ==========

@login_required
def event_list_view(request):
    """Vista de lista de eventos."""
    events_list = Event.objects.all().select_related(
        'event_type', 'field', 'campaign', 'created_by'
    ).order_by('-timestamp')
    
    # Filtros
    event_type_id = request.GET.get('event_type')
    field_id = request.GET.get('field')
    campaign_id = request.GET.get('campaign')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if event_type_id:
        events_list = events_list.filter(event_type_id=event_type_id)
    if field_id:
        events_list = events_list.filter(field_id=field_id)
    if campaign_id:
        events_list = events_list.filter(campaign_id=campaign_id)
    if date_from:
        events_list = events_list.filter(timestamp__gte=date_from)
    if date_to:
        events_list = events_list.filter(timestamp__lte=date_to)
    
    # Paginación
    paginator = Paginator(events_list, 20)
    page_number = request.GET.get('page')
    events = paginator.get_page(page_number)
    
    # Datos para filtros
    event_types = EventType.objects.filter(is_active=True).order_by('category', 'name')
    fields = Field.objects.filter(is_active=True).order_by('name')
    campaigns = Campaign.objects.filter(is_active=True).order_by('-start_date')
    
    context = {
        'events': events,
        'event_types': event_types,
        'fields': fields,
        'campaigns': campaigns,
        'selected_event_type': event_type_id,
        'selected_field': field_id,
        'selected_campaign': campaign_id,
        'date_from': date_from,
        'date_to': date_to,
        'total_count': Event.objects.count(),
    }
    return render(request, 'events/event_list.html', context)


@login_required
def event_create_view(request):
    """Vista para crear un nuevo evento."""
    event_type_id = request.GET.get('event_type') or request.POST.get('event_type')
    event_type = None
    form = None
    
    if event_type_id:
        event_type = get_object_or_404(EventType, pk=event_type_id, is_active=True)
        FormClass = get_event_form(event_type.name)
        
        if not FormClass:
            messages.error(request, f'No se encontró formulario para el tipo de evento: {event_type.name}')
            return redirect('event_list')
        
        if request.method == 'POST':
            form = FormClass(request.POST)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        event = form.save(commit=False)
                        event.event_type = event_type
                        event.created_by = request.user
                        event.full_clean()  # Ejecutar validaciones del modelo
                        event.save()
                        
                        messages.success(request, f'Evento "{event_type.name}" registrado exitosamente.')
                        return redirect('event_list')
                except Exception as e:
                    messages.error(request, f'Error al crear evento: {str(e)}')
        else:
            form = FormClass(initial={'event_type': event_type})
    else:
        # Si no hay event_type seleccionado, mostrar selector
        if request.method == 'POST':
            messages.error(request, 'Debe seleccionar un tipo de evento.')
    
    # GET request o error - mostrar formulario o selector
    event_types = EventType.objects.filter(is_active=True).order_by('category', 'name')
    fields = Field.objects.filter(is_active=True).order_by('name')
    campaigns = Campaign.objects.filter(is_active=True).order_by('-start_date')
    
    context = {
        'event_types': event_types,
        'fields': fields,
        'campaigns': campaigns,
        'event_type': event_type,
        'form': form,
        'action': 'Crear'
    }
    return render(request, 'events/event_form.html', context)


@login_required
def event_detail_view(request, pk):
    """Vista de detalle de un evento."""
    # Intentar obtener el evento específico primero
    event = None
    for model_class in EVENT_TYPE_MODEL_MAP.values():
        try:
            event = model_class.objects.select_related('event_type', 'field', 'campaign', 'created_by').get(pk=pk)
            break
        except model_class.DoesNotExist:
            continue
    
    # Si no se encontró en modelos específicos, buscar en Event base
    if event is None:
        event = get_object_or_404(
            Event.objects.select_related('event_type', 'field', 'campaign', 'created_by'),
            pk=pk
        )
    
    context = {
        'event': event,
    }
    return render(request, 'events/event_detail.html', context)


@login_required
def get_event_type_info(request, pk):
    """API auxiliar para obtener información de un tipo de evento."""
    event_type = get_object_or_404(EventType, pk=pk)
    
    # Obtener el modelo específico asociado
    model_class = get_event_model(event_type.name)
    form_class = get_event_form(event_type.name)
    
    return JsonResponse({
        'id': event_type.id,
        'name': event_type.name,
        'category': event_type.category,
        'description': event_type.description,
        'icon': event_type.icon,
        'color': event_type.color,
        'model_name': model_class.__name__ if model_class else 'Event',
        'has_form': form_class is not None,
    })


# ========== Event Type CRUD Views ==========


@login_required
def event_type_list_view(request):
    """Vista para listar tipos de eventos."""
    event_types = EventType.objects.all().order_by('category', 'name')
    
    # Contar eventos por tipo
    for et in event_types:
        et.event_count = et.events.count()
    
    context = {
        'event_types': event_types,
        'total_count': EventType.objects.count(),
        'active_count': EventType.objects.filter(is_active=True).count(),
    }
    return render(request, 'events/event_type_list.html', context)


@login_required
def event_type_create_view(request):
    """Vista para crear un nuevo tipo de evento (deshabilitada - tipos son fijos)."""
    messages.warning(request, 'Los tipos de eventos son predefinidos y no se pueden crear nuevos.')
    return redirect('event_type_list')


@login_required
def event_type_edit_view(request, pk):
    """Vista para editar metadata de un tipo de evento (solo icon, color, description, is_active)."""
    event_type = get_object_or_404(EventType, pk=pk)
    
    if request.method == 'POST':
        try:
            # Solo permitir editar metadata, no name ni category (son fijos)
            event_type.description = request.POST.get('description', '')
            event_type.icon = request.POST.get('icon', '')
            event_type.color = request.POST.get('color', '#6c757d')
            event_type.is_active = request.POST.get('is_active') == 'on'
            event_type.save()
            
            messages.success(request, f'Metadata del tipo de evento "{event_type.name}" actualizado exitosamente.')
            return redirect('event_type_list')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar tipo de evento: {str(e)}')
    
    context = {
        'action': 'Editar',
        'event_type': event_type,
        'categories': EventType.CATEGORIES,
    }
    return render(request, 'events/event_type_form.html', context)


@login_required
def event_type_delete_view(request, pk):
    """Vista para eliminar un tipo de evento."""
    event_type = get_object_or_404(EventType, pk=pk)
    
    # Verificar si hay eventos asociados
    event_count = event_type.events.count()
    
    if request.method == 'POST':
        if event_count > 0:
            messages.error(
                request, 
                f'No se puede eliminar "{event_type.name}" porque tiene {event_count} evento(s) registrado(s).'
            )
        else:
            name = event_type.name
            event_type.delete()
            messages.success(request, f'Tipo de evento "{name}" eliminado exitosamente.')
            return redirect('event_type_list')
    
    context = {
        'event_type': event_type,
        'event_count': event_count,
    }
    return render(request, 'events/event_type_confirm_delete.html', context)


