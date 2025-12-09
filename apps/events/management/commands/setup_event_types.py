"""
Comando de Django para crear o actualizar los tipos de eventos base del sistema.

Uso:
    python manage.py setup_event_types
    python manage.py setup_event_types --update  # Actualiza tipos existentes
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.events.models import EventType


class Command(BaseCommand):
    help = 'Crea los tipos de eventos base del sistema de trazabilidad agrícola'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Actualiza los tipos de eventos existentes con nuevos datos',
        )

    def handle(self, *args, **options):
        update_existing = options['update']
        
        event_types_data = [
            {
                'name': 'Aplicación de Riego',
                'description': 'Registro de aplicación de riego en cultivos de limón',
                'category': 'irrigation',
                'icon': 'droplet-fill',
                'color': '#0dcaf0',
            },
            {
                'name': 'Aplicación de Fertilizante',
                'description': 'Registro de fertilización al suelo o foliar',
                'category': 'fertilization',
                'icon': 'moisture',
                'color': '#198754',
            },
            {
                'name': 'Aplicación Fitosanitaria',
                'description': 'Aplicación de fungicidas, insecticidas, herbicidas o acaricidas',
                'category': 'phytosanitary',
                'icon': 'bug-fill',
                'color': '#dc3545',
            },
            {
                'name': 'Labores de Cultivo',
                'description': 'Actividades de mantenimiento y cuidado del cultivo',
                'category': 'maintenance',
                'icon': 'tools',
                'color': '#6f42c1',
            },
            {
                'name': 'Monitoreo de Plagas',
                'description': 'Registro de monitoreo y detección temprana de plagas y enfermedades',
                'category': 'monitoring',
                'icon': 'eye-fill',
                'color': '#fd7e14',
            },
            {
                'name': 'Brote de Plaga/Enfermedad',
                'description': 'Registro de brotes severos que requieren atención inmediata',
                'category': 'monitoring',
                'icon': 'exclamation-triangle-fill',
                'color': '#dc3545',
            },
            {
                'name': 'Condiciones Climáticas',
                'description': 'Registro de variables climáticas observadas o medidas',
                'category': 'monitoring',
                'icon': 'cloud-sun-fill',
                'color': '#20c997',
            },
            {
                'name': 'Cosecha',
                'description': 'Registro de actividades de cosecha de limones',
                'category': 'harvest',
                'icon': 'basket-fill',
                'color': '#ffc107',
            },
            {
                'name': 'Almacenamiento Poscosecha',
                'description': 'Control de almacenamiento y conservación del producto',
                'category': 'postharvest',
                'icon': 'box-seam-fill',
                'color': '#795548',
            },
            {
                'name': 'Mano de Obra y Costos',
                'description': 'Registro de recursos humanos y costos asociados a actividades',
                'category': 'other',
                'icon': 'people-fill',
                'color': '#6c757d',
            },
        ]
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        with transaction.atomic():
            for event_data in event_types_data:
                event_type, created = EventType.objects.get_or_create(
                    name=event_data['name'],
                    defaults=event_data
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Creado: {event_data["name"]}')
                    )
                elif update_existing:
                    # Actualizar campos excepto name
                    for key, value in event_data.items():
                        if key != 'name':
                            setattr(event_type, key, value)
                    event_type.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'↻ Actualizado: {event_data["name"]}')
                    )
                else:
                    skipped_count += 1
                    self.stdout.write(
                        self.style.NOTICE(f'○ Omitido: {event_data["name"]} (ya existe)')
                    )
        
        # Resumen
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('RESUMEN DE LA OPERACIÓN')
        self.stdout.write('=' * 60)
        self.stdout.write(f'Tipos de eventos creados:      {created_count}')
        self.stdout.write(f'Tipos de eventos actualizados: {updated_count}')
        self.stdout.write(f'Tipos de eventos omitidos:      {skipped_count}')
        self.stdout.write('=' * 60)
        
        if created_count > 0 or updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Sistema configurado correctamente con {created_count + updated_count} tipos de eventos.'
                )
            )
