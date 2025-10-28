from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from rest_framework import generics, status
from rest_framework.response import Response
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
