from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard_view(request):
    """Vista del dashboard principal después del login."""
    return render(request, 'dashboard.html')
