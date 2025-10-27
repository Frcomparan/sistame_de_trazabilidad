from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from rest_framework import generics, serializers
from .models import Field, Campaign, Station


# ========== API Views ==========

class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = '__all__'


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'


class FieldListView(generics.ListAPIView):
    queryset = Field.objects.filter(is_active=True)
    serializer_class = FieldSerializer


class CampaignListView(generics.ListAPIView):
    queryset = Campaign.objects.filter(is_active=True)
    serializer_class = CampaignSerializer


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
