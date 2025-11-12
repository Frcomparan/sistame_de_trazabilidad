"""
Management command para verificar la distribución de eventos.
"""

from django.core.management.base import BaseCommand
from apps.events.models import Event
from apps.catalogs.models import Campaign, Field


class Command(BaseCommand):
    help = 'Muestra estadísticas de distribución de eventos entre campañas'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.SUCCESS('📊 ESTADÍSTICAS DE DISTRIBUCIÓN DE EVENTOS'))
        self.stdout.write('=' * 70)

        self.stdout.write(f'\n📈 TOTALES:')
        self.stdout.write(f'   • Eventos: {Event.objects.count()}')
        self.stdout.write(f'   • Campos: {Field.objects.count()}')
        self.stdout.write(f'   • Campañas: {Campaign.objects.count()}')

        self.stdout.write(f'\n📅 EVENTOS POR CAMPAÑA:')
        for c in Campaign.objects.all().order_by('start_date'):
            count = Event.objects.filter(campaign=c).count()
            status = '🟢 Activa' if c.is_active else '⚪ Finalizada'
            self.stdout.write(f'\n   {status} {c.name}')
            self.stdout.write(f'      Periodo: {c.start_date} a {c.end_date or "presente"}')
            self.stdout.write(f'      Eventos: {count}')
            
            if count > 0:
                first = Event.objects.filter(campaign=c).order_by('timestamp').first()
                last = Event.objects.filter(campaign=c).order_by('timestamp').last()
                self.stdout.write(f'      Rango real: {first.timestamp.strftime("%d/%m/%Y")} - {last.timestamp.strftime("%d/%m/%Y")}')

        self.stdout.write(f'\n📍 EVENTOS POR CAMPO:')
        for f in Field.objects.all():
            count = Event.objects.filter(field=f).count()
            self.stdout.write(f'   • {f.name} ({f.code}): {count} eventos')

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('✅ Verificación completa'))
        self.stdout.write('=' * 70)
