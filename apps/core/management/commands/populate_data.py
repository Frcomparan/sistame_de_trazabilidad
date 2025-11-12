"""
Comando para poblar la base de datos con datos de prueba realistas.

Este comando crea:
- 5 campos/parcelas
- 3 campañas/temporadas
- Múltiples eventos de cada tipo distribuidos a lo largo de un año
- Datos coherentes y realistas para cultivo de limón

Uso:
    python manage.py populate_data
    python manage.py populate_data --clear  # Borra datos existentes primero
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random

from apps.catalogs.models import Field, Campaign
from apps.events.models import (
    EventType, Event, IrrigationEvent, FertilizationEvent,
    PhytosanitaryEvent, MaintenanceEvent, MonitoringEvent,
    OutbreakEvent, ClimateEvent, HarvestEvent, PostHarvestEvent,
    LaborCostEvent
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de prueba realistas para cultivo de limón'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Elimina todos los eventos y campañas existentes antes de poblar',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Iniciando población de datos de prueba...'))

        if options['clear']:
            self.clear_data()

        # Obtener o crear usuario admin
        self.user = self.get_or_create_admin()

        # Crear campos
        self.fields = self.create_fields()

        # Crear campañas
        self.campaigns = self.create_campaigns()

        # Crear eventos a lo largo del año
        self.create_events_timeline()

        self.stdout.write(self.style.SUCCESS('✅ ¡Población de datos completada exitosamente!'))
        self.print_summary()

    def clear_data(self):
        """Elimina datos existentes."""
        self.stdout.write(self.style.WARNING('🗑️  Eliminando datos existentes...'))
        
        Event.objects.all().delete()
        Campaign.objects.all().delete()
        Field.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('   ✓ Datos eliminados'))

    def get_or_create_admin(self):
        """Obtiene o crea usuario admin."""
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@trazabilidad.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS('   ✓ Usuario admin creado'))
        else:
            self.stdout.write(self.style.SUCCESS('   ✓ Usuario admin encontrado'))
        return user

    def create_fields(self):
        """Crea campos/parcelas."""
        self.stdout.write('📍 Creando campos/parcelas...')
        
        fields_data = [
            {
                'name': 'Campo Norte',
                'code': 'NORTE-01',
                'surface_ha': Decimal('2.5000'),
                'notes': 'Campo principal con sistema de riego por goteo. Variedad Limón Persa.'
            },
            {
                'name': 'Campo Sur',
                'code': 'SUR-01',
                'surface_ha': Decimal('3.2000'),
                'notes': 'Campo con árboles jóvenes (3 años). Riego por microaspersión.'
            },
            {
                'name': 'Campo Este',
                'code': 'ESTE-01',
                'surface_ha': Decimal('1.8000'),
                'notes': 'Campo experimental con manejo orgánico.'
            },
            {
                'name': 'Campo Oeste',
                'code': 'OESTE-01',
                'surface_ha': Decimal('4.0000'),
                'notes': 'Campo de mayor producción. Árboles de 8 años.'
            },
            {
                'name': 'Campo Central',
                'code': 'CENTRAL-01',
                'surface_ha': Decimal('2.0000'),
                'notes': 'Campo con sistema de fertirrigación automatizado.'
            },
        ]

        fields = []
        for data in fields_data:
            field, created = Field.objects.get_or_create(
                code=data['code'],
                defaults=data
            )
            fields.append(field)
            symbol = '✓' if created else '↻'
            self.stdout.write(f'   {symbol} {field.name} ({field.surface_ha} ha)')

        return fields

    def create_campaigns(self):
        """Crea campañas/temporadas."""
        self.stdout.write('📅 Creando campañas/temporadas...')
        
        # Año actual
        now = timezone.now()
        current_year = now.year
        
        campaigns_data = [
            {
                'name': f'Primavera {current_year - 1}',
                'season': 'Primavera',
                'variety': 'Limón Persa',
                'start_date': datetime(current_year - 1, 3, 1).date(),
                'end_date': datetime(current_year - 1, 8, 31).date(),
                'notes': 'Campaña de primavera-verano con buena producción.',
                'is_active': False,
            },
            {
                'name': f'Otoño {current_year - 1}',
                'season': 'Otoño',
                'variety': 'Limón Mexicano',
                'start_date': datetime(current_year - 1, 9, 1).date(),
                'end_date': datetime(current_year, 2, 28).date(),
                'notes': 'Campaña de otoño-invierno.',
                'is_active': False,
            },
            {
                'name': f'Primavera {current_year}',
                'season': 'Primavera',
                'variety': 'Limón Persa',
                'start_date': datetime(current_year, 3, 1).date(),
                'end_date': None,  # Campaña activa
                'notes': 'Campaña actual en curso.',
                'is_active': True,
            },
        ]

        campaigns = []
        for data in campaigns_data:
            campaign, created = Campaign.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            campaigns.append(campaign)
            symbol = '✓' if created else '↻'
            status = '(Activa)' if campaign.is_active else ''
            self.stdout.write(f'   {symbol} {campaign.name} {status}')

        return campaigns

    def create_events_timeline(self):
        """Crea eventos distribuidos a lo largo del año para TODAS las campañas."""
        self.stdout.write('📊 Creando eventos temporales...')
        
        # Contadores globales
        counts = {
            'irrigation': 0,
            'fertilization': 0,
            'phytosanitary': 0,
            'maintenance': 0,
            'monitoring': 0,
            'outbreak': 0,
            'climate': 0,
            'harvest': 0,
            'postharvest': 0,
            'labor': 0,
        }
        
        # Crear eventos para cada campaña
        campaign_configs = [
            {
                'campaign': self.campaigns[0],  # Primavera 2024
                'start_date': timezone.make_aware(datetime(2024, 3, 1)),
                'months': 6,  # Marzo-Agosto 2024
                'name': 'Primavera 2024'
            },
            {
                'campaign': self.campaigns[1],  # Otoño 2024
                'start_date': timezone.make_aware(datetime(2024, 9, 1)),
                'months': 6,  # Septiembre 2024 - Febrero 2025
                'name': 'Otoño 2024'
            },
            {
                'campaign': self.campaigns[2],  # Primavera 2025 (Activa)
                'start_date': timezone.make_aware(datetime(2025, 3, 1)),
                'months': 9,  # Marzo-Noviembre 2025
                'name': 'Primavera 2025'
            },
        ]
        
        for config in campaign_configs:
            campaign = config['campaign']
            start_date = config['start_date']
            months = config['months']
            campaign_name = config['name']
            
            self.stdout.write(f'\n   📅 Creando eventos para {campaign_name}...')
            campaign_counts = {key: 0 for key in counts.keys()}
            
            # Crear eventos mes por mes
            for month_offset in range(months):
                month_start = start_date + timedelta(days=30 * month_offset)
                
                for field in self.fields:
                    # Eventos de riego (2-3 por mes por campo)
                    for _ in range(random.randint(2, 3)):
                        self.create_irrigation_event(field, campaign, month_start)
                        counts['irrigation'] += 1
                        campaign_counts['irrigation'] += 1
                    
                    # Eventos de fertilización (1-2 por mes)
                    for _ in range(random.randint(1, 2)):
                        self.create_fertilization_event(field, campaign, month_start)
                        counts['fertilization'] += 1
                        campaign_counts['fertilization'] += 1
                    
                    # Eventos fitosanitarios (1-2 por mes)
                    for _ in range(random.randint(1, 2)):
                        self.create_phytosanitary_event(field, campaign, month_start)
                        counts['phytosanitary'] += 1
                        campaign_counts['phytosanitary'] += 1
                    
                    # Labores de cultivo (1 por mes)
                    self.create_maintenance_event(field, campaign, month_start)
                    counts['maintenance'] += 1
                    campaign_counts['maintenance'] += 1
                    
                    # Monitoreo (2 por mes)
                    for _ in range(2):
                        self.create_monitoring_event(field, campaign, month_start)
                        counts['monitoring'] += 1
                        campaign_counts['monitoring'] += 1
                    
                    # Eventos climáticos (3-4 por mes)
                    for _ in range(random.randint(3, 4)):
                        self.create_climate_event(field, campaign, month_start)
                        counts['climate'] += 1
                        campaign_counts['climate'] += 1
                    
                    # Brotes (ocasionales, 20% de probabilidad)
                    if random.random() < 0.2:
                        self.create_outbreak_event(field, campaign, month_start)
                        counts['outbreak'] += 1
                        campaign_counts['outbreak'] += 1
                    
                    # Cosecha (solo en ciertos meses según la campaña)
                    # Primavera: meses 4,5,6 (julio-sept)
                    # Otoño: meses 3,4,5 (dic-feb)
                    harvest_months = [3, 4, 5] if 'Otoño' in campaign_name else [4, 5, 6]
                    if month_offset in harvest_months:
                        self.create_harvest_event(field, campaign, month_start)
                        counts['harvest'] += 1
                        campaign_counts['harvest'] += 1
                        
                        # Poscosecha después de cada cosecha
                        self.create_postharvest_event(field, campaign, month_start)
                        counts['postharvest'] += 1
                        campaign_counts['postharvest'] += 1
                    
                    # Costos de mano de obra (1 por mes)
                    self.create_labor_cost_event(field, campaign, month_start)
                    counts['labor'] += 1
                    campaign_counts['labor'] += 1
            
            # Resumen de la campaña
            total_campaign = sum(campaign_counts.values())
            self.stdout.write(f'      ✓ {total_campaign} eventos creados para {campaign_name}')
        
        # Imprimir resumen global
        self.stdout.write('\n   📊 Total de eventos creados por tipo:')
        for event_type, count in counts.items():
            self.stdout.write(f'      • {event_type.capitalize()}: {count}')

    def create_irrigation_event(self, field, campaign, base_date):
        """Crea evento de riego."""
        event_type = EventType.objects.get(name='Aplicación de Riego')
        
        days_offset = random.randint(0, 28)
        event_date = base_date + timedelta(days=days_offset, hours=random.randint(6, 9))
        
        methods = ['Goteo', 'Microaspersión', 'Aspersión']
        sources = ['Pozo', 'Río', 'Presa']
        
        IrrigationEvent.objects.create(
            event_type=event_type,
            field=field,
            campaign=campaign,
            timestamp=event_date,
            metodo=random.choice(methods),
            duracion_minutos=random.randint(60, 180),
            volumen_m3=Decimal(str(round(random.uniform(20, 80), 2))),
            fuente_agua=random.choice(sources),
            ce_uScm=Decimal(str(random.randint(400, 1200))),
            ph=Decimal(str(round(random.uniform(6.0, 7.5), 1))),
            observations=f'Riego programado. Condiciones normales.',
            created_by=self.user
        )

    def create_fertilization_event(self, field, campaign, base_date):
        """Crea evento de fertilización."""
        event_type = EventType.objects.get(name='Aplicación de Fertilizante')
        
        days_offset = random.randint(0, 28)
        event_date = base_date + timedelta(days=days_offset, hours=random.randint(7, 10))
        
        fertilizers = [
            ('NPK 15-15-15', 'kg/ha', 150),
            ('Urea 46%', 'kg/ha', 100),
            ('Nitrato de Potasio', 'kg/ha', 80),
            ('Fosfato Diamónico', 'kg/ha', 120),
            ('Sulfato de Magnesio', 'kg/ha', 50),
        ]
        
        fertilizer = random.choice(fertilizers)
        
        FertilizationEvent.objects.create(
            event_type=event_type,
            field=field,
            campaign=campaign,
            timestamp=event_date,
            producto=fertilizer[0],
            dosis=Decimal(str(random.randint(50, fertilizer[2]))),
            unidad_dosis=fertilizer[1],
            metodo_aplicacion=random.choice(['Fertirriego', 'Foliar', 'Edáfica']),
            observations=f'Aplicación {fertilizer[0]}. Según programa nutricional.',
            created_by=self.user
        )

    def create_phytosanitary_event(self, field, campaign, base_date):
        """Crea evento fitosanitario."""
        event_type = EventType.objects.get(name='Aplicación Fitosanitaria')
        
        days_offset = random.randint(0, 28)
        event_date = base_date + timedelta(days=days_offset, hours=random.randint(6, 8))
        
        products = [
            ('Mancozeb 80%', 'Fungicida', 'Antracnosis', 2.5, 14),
            ('Cobre Oxicloruro', 'Fungicida', 'Gomosis', 3.0, 7),
            ('Azufre 80%', 'Fungicida', 'Ácaro rojo', 4.0, 0),
            ('Aceite Mineral', 'Insecticida', 'Cochinilla', 2.0, 3),
            ('Bacillus thuringiensis', 'Insecticida', 'Minador', 1.5, 0),
        ]
        
        product = random.choice(products)
        
        PhytosanitaryEvent.objects.create(
            event_type=event_type,
            field=field,
            campaign=campaign,
            timestamp=event_date,
            producto=product[0],
            ingrediente_activo=product[0].split()[0],
            tipo_producto=product[1],
            objetivo=product[2],
            dosis=Decimal(str(product[3])),
            unidad_dosis='L/ha' if 'Aceite' in product[0] else 'kg/ha',
            metodo_aplicacion='Mochila motorizada',
            intervalo_seguridad_dias=product[4],
            observations=f'Aplicación preventiva de {product[0]} contra {product[2]}.',
            created_by=self.user
        )

    def create_maintenance_event(self, field, campaign, base_date):
        """Crea evento de labores de cultivo."""
        event_type = EventType.objects.get(name='Labores de Cultivo')
        
        days_offset = random.randint(0, 28)
        event_date = base_date + timedelta(days=days_offset, hours=random.randint(7, 11))
        
        activities = [
            ('Poda', 'Tijeras de podar, escalera', 32),
            ('Deshierbe', 'Azadón, desbrozadora', 16),
            ('Aclareo de frutos', 'Tijeras de podar', 24),
            ('Limpieza de canales', 'Herramienta básica', 8),
            ('Desbrote', 'Tijeras de podar', 12),
        ]
        
        activity = random.choice(activities)
        workers = random.randint(2, 6)
        
        MaintenanceEvent.objects.create(
            event_type=event_type,
            field=field,
            campaign=campaign,
            timestamp=event_date,
            actividad=activity[0],
            herramienta_equipo=activity[1],
            horas_hombre=Decimal(str(activity[2])),
            numero_jornales=workers,
            observations=f'{activity[0]} realizada por {workers} trabajadores.',
            created_by=self.user
        )

    def create_monitoring_event(self, field, campaign, base_date):
        """Crea evento de monitoreo."""
        event_type = EventType.objects.get(name='Monitoreo de Plagas')
        
        days_offset = random.randint(0, 28)
        event_date = base_date + timedelta(days=days_offset, hours=random.randint(8, 12))
        
        pests = [
            'Minador de la hoja',
            'Araña roja',
            'Pulgón',
            'Trips',
            'Antracnosis',
            'Gomosis',
        ]
        
        severities = ['Baja', 'Media', 'Alta']
        
        MonitoringEvent.objects.create(
            event_type=event_type,
            field=field,
            campaign=campaign,
            timestamp=event_date,
            plaga_enfermedad=random.choice(pests),
            metodo_muestreo='Visual directa',
            incidencia=random.choice(severities),
            severidad=random.choice(severities),
            observations=f'Monitoreo de rutina. Se detectaron síntomas.',
            created_by=self.user
        )

    def create_outbreak_event(self, field, campaign, base_date):
        """Crea evento de brote."""
        event_type = EventType.objects.get(name='Brote de Plaga/Enfermedad')
        
        days_offset = random.randint(0, 28)
        event_date = base_date + timedelta(days=days_offset, hours=random.randint(8, 14))
        
        outbreaks = [
            ('Brote de Minador', 1.2),
            ('Brote de Araña Roja', 0.8),
            ('Brote de Antracnosis', 1.5),
            ('Brote de Trips', 0.6),
        ]
        
        outbreak = random.choice(outbreaks)
        
        OutbreakEvent.objects.create(
            event_type=event_type,
            field=field,
            campaign=campaign,
            timestamp=event_date,
            tipo_problema=outbreak[0],
            severidad=random.choice(['Media', 'Alta']),
            metodo_deteccion='Monitoreo rutinario',
            area_afectada_ha=Decimal(str(outbreak[1])),
            accion_inmediata='Aplicación fitosanitaria inmediata programada',
            observations=f'{outbreak[0]} detectado. Requiere tratamiento.',
            created_by=self.user
        )

    def create_climate_event(self, field, campaign, base_date):
        """Crea evento climático."""
        event_type = EventType.objects.get(name='Condiciones Climáticas')
        
        days_offset = random.randint(0, 28)
        event_date = base_date + timedelta(days=days_offset, hours=random.randint(12, 18))
        
        ClimateEvent.objects.create(
            event_type=event_type,
            field=field,
            campaign=campaign,
            timestamp=event_date,
            temperatura_max=Decimal(str(round(random.uniform(28, 38), 1))),
            temperatura_min=Decimal(str(round(random.uniform(15, 22), 1))),
            humedad_relativa=Decimal(str(random.randint(45, 85))),
            precipitacion_mm=Decimal(str(round(random.uniform(0, 25), 1))) if random.random() < 0.3 else Decimal('0'),
            velocidad_viento_ms=Decimal(str(round(random.uniform(1, 10), 1))),
            observations='Registro automático estación meteorológica',
            created_by=self.user
        )

    def create_harvest_event(self, field, campaign, base_date):
        """Crea evento de cosecha."""
        event_type = EventType.objects.get(name='Cosecha')
        
        days_offset = random.randint(0, 28)
        event_date = base_date + timedelta(days=days_offset, hours=random.randint(6, 10))
        
        varieties = ['Limón Persa', 'Limón Mexicano']
        
        volume = random.randint(1000, 3000)
        surface = float(field.surface_ha)
        yield_per_ha = int(volume / surface)
        
        HarvestEvent.objects.create(
            event_type=event_type,
            field=field,
            campaign=campaign,
            timestamp=event_date,
            variedad=random.choice(varieties),
            volumen_kg=Decimal(str(volume)),
            rendimiento_kg_ha=Decimal(str(yield_per_ha)),
            calidad=random.choice(['exportacion', 'primera', 'segunda', 'tercera']),
            numero_trabajadores=random.randint(8, 15),
            horas_trabajo=Decimal(str(random.randint(6, 10))),
            observations=f'Cosecha de {volume} kg. Rendimiento: {yield_per_ha} kg/ha.',
            created_by=self.user
        )

    def create_postharvest_event(self, field, campaign, base_date):
        """Crea evento de poscosecha."""
        event_type = EventType.objects.get(name='Almacenamiento Poscosecha')
        
        days_offset = random.randint(0, 3)  # Pocos días después de la cosecha
        event_date = base_date + timedelta(days=days_offset, hours=random.randint(10, 14))
        
        PostHarvestEvent.objects.create(
            event_type=event_type,
            field=field,
            campaign=campaign,
            timestamp=event_date,
            producto='Limón Persa calibre 150',
            cantidad_kg=Decimal(str(random.randint(800, 2500))),
            temperatura=Decimal(str(round(random.uniform(10, 14), 1))),
            humedad=Decimal(str(random.randint(85, 95))),
            tipo_almacenamiento=random.choice(['Cámara frigorífica', 'Almacén techado']),
            condiciones_observadas='Producto en buenas condiciones',
            observations='Almacenamiento controlado según estándares.',
            created_by=self.user
        )

    def create_labor_cost_event(self, field, campaign, base_date):
        """Crea evento de costos de mano de obra."""
        event_type = EventType.objects.get(name='Mano de Obra y Costos')
        
        days_offset = random.randint(0, 28)
        event_date = base_date + timedelta(days=days_offset, hours=random.randint(16, 18))
        
        workers = random.randint(3, 8)
        hours = Decimal(str(random.randint(30, 50)))
        cost_per_hour = Decimal(str(round(random.uniform(20, 30), 2)))
        total = workers * hours * cost_per_hour
        
        LaborCostEvent.objects.create(
            event_type=event_type,
            field=field,
            campaign=campaign,
            timestamp=event_date,
            actividad='Cosecha',
            numero_trabajadores=workers,
            horas_trabajo=hours,
            costo_hora=cost_per_hour,
            costo_total=Decimal(str(round(total, 2))),
            observations=f'Costo laboral mensual: {workers} trabajadores × {hours}h × ${cost_per_hour}/h',
            created_by=self.user
        )

    def print_summary(self):
        """Imprime resumen de datos creados."""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 RESUMEN DE DATOS CREADOS'))
        self.stdout.write('='*60)
        
        self.stdout.write(f'\n📍 Campos: {Field.objects.count()}')
        for field in Field.objects.all():
            self.stdout.write(f'   • {field.name} ({field.code}) - {field.surface_ha} ha')
        
        self.stdout.write(f'\n📅 Campañas: {Campaign.objects.count()}')
        for campaign in Campaign.objects.all():
            status = '✓ Activa' if campaign.is_active else '  Finalizada'
            event_count = Event.objects.filter(campaign=campaign).count()
            self.stdout.write(f'   {status} {campaign.name} ({campaign.season}) - {event_count} eventos')
        
        self.stdout.write(f'\n📊 Total de Eventos: {Event.objects.count()}')
        
        # Contar eventos por tipo
        for event_type in EventType.objects.all():
            count = Event.objects.filter(event_type=event_type).count()
            if count > 0:
                self.stdout.write(f'   • {event_type.name}: {count}')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ Sistema listo para probar reportes!'))
        self.stdout.write('='*60)
        self.stdout.write('\n💡 Sugerencias:')
        self.stdout.write('   • Accede a http://localhost:8000/reportes/')
        self.stdout.write('   • Genera un reporte PDF del "Campo Norte"')
        self.stdout.write('   • Prueba filtrar por diferentes campañas:')
        self.stdout.write('     - Primavera 2024 (datos históricos)')
        self.stdout.write('     - Otoño 2024 (datos históricos)')
        self.stdout.write('     - Primavera 2025 (campaña activa)')
        self.stdout.write('   • Prueba exportar a Excel y CSV')
        self.stdout.write('')
