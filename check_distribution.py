"""
Script para verificar la distribución de eventos entre campañas.
Ejecutar: docker-compose exec web python check_distribution.py
"""

from apps.events.models import Event
from apps.catalogs.models import Campaign, Field

print('=' * 70)
print('📊 ESTADÍSTICAS DE DISTRIBUCIÓN DE EVENTOS')
print('=' * 70)

print(f'\n📈 TOTALES:')
print(f'   • Eventos: {Event.objects.count()}')
print(f'   • Campos: {Field.objects.count()}')
print(f'   • Campañas: {Campaign.objects.count()}')

print(f'\n📅 EVENTOS POR CAMPAÑA:')
for c in Campaign.objects.all().order_by('start_date'):
    count = Event.objects.filter(campaign=c).count()
    status = '🟢 Activa' if c.is_active else '⚪ Finalizada'
    print(f'   {status} {c.name}')
    print(f'      Periodo: {c.start_date} a {c.end_date or "presente"}')
    print(f'      Eventos: {count}')
    
    if count > 0:
        first = Event.objects.filter(campaign=c).order_by('timestamp').first()
        last = Event.objects.filter(campaign=c).order_by('timestamp').last()
        print(f'      Rango real: {first.timestamp.strftime("%d/%m/%Y")} - {last.timestamp.strftime("%d/%m/%Y")}')
    print()

print(f'📍 EVENTOS POR CAMPO:')
for f in Field.objects.all():
    count = Event.objects.filter(field=f).count()
    print(f'   • {f.name} ({f.code}): {count} eventos')

print('\n' + '=' * 70)
print('✅ Verificación completa')
print('=' * 70)
