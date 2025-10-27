# Sistema de Trazabilidad Agrícola - Cultivo de Limón

## 📋 Descripción del Proyecto

Sistema web de trazabilidad para la gestión integral del cultivo de limón, desde las labores de campo hasta la poscosecha. Desarrollado en Python con Django, permite registrar, auditar y consultar eventos agronómicos, variables ambientales y operativas a través de una interfaz web y API REST.

> **Enfoque MVP**: Este sistema está diseñado como un MVP (Minimum Viable Product), priorizando la simplicidad y la implementación rápida. Se minimiza la lógica compleja excepto el sistema de eventos dinámicos. El despliegue se realiza mediante Docker para facilitar la instalación y configuración.

## 🎯 Características Principales

- **Trazabilidad completa** del ciclo de cultivo por lote/parcela
- **Eventos dinámicos**: Creación y configuración de nuevos tipos de eventos sin modificar código
- **Interfaz web intuitiva** para captura y consulta de información
- **API REST** para integración con otros sistemas y dispositivos IoT
- **Gestión de variables ambientales** (temperatura, humedad, precipitación, NDVI/NDRE)
- **Sistema de auditoría** completo
- **Reportes y KPIs** configurables

## 📚 Documentación

### Documentos Principales

1. **[Visión y Alcance](./docs/01_vision_alcance.md)** - Objetivos, alcance y propuesta de valor
2. **[Análisis de Requerimientos](./docs/02_requerimientos.md)** - Requerimientos funcionales y no funcionales
3. **[Arquitectura del Sistema](./docs/03_arquitectura.md)** - Diseño de alto nivel y decisiones arquitectónicas
4. **[Modelo de Dominio](./docs/04_modelo_dominio.md)** - Clases, entidades y relaciones
5. **[Diseño de Base de Datos](./docs/05_base_datos.md)** - Esquema de datos y modelo relacional
6. **[Especificación de API](./docs/06_api_rest.md)** - Endpoints, autenticación y ejemplos
7. **[Sistema de Eventos Dinámicos](./docs/07_eventos_dinamicos.md)** - Diseño del núcleo flexible del sistema
8. **[Plan de Desarrollo](./docs/08_cronograma.md)** - Cronograma de 16 semanas
9. **[Gestión de Riesgos](./docs/09_riesgos.md)** - Identificación y mitigación de riesgos
10. **[Plan de Pruebas](./docs/10_pruebas.md)** - Estrategia de testing y calidad

### Documentos de Referencia

- **[Glosario de Términos](./docs/glosario.md)** - Definiciones y terminología agrícola
- **[Referencias](./docs/referencias.md)** - Documentos fuente y bibliografía

## 🛠️ Stack Tecnológico

- **Backend**: Python 3.11+, Django 5.x, Django REST Framework
- **Base de Datos**: PostgreSQL 15+ (con soporte JSONB)
- **Despliegue**: Docker + Docker Compose
- **Autenticación**: JWT para API, Session para Web
- **Testing**: pytest, pytest-django
- **Documentación API**: OpenAPI/Swagger
- **Control de Versiones**: Git

## 👥 Actores del Sistema

- **Administrador**: Gestión de catálogos, permisos y tipos de evento
- **Técnico de Campo**: Captura de eventos y variables
- **Supervisor/Calidad**: Auditoría y consulta de reportes
- **Sistemas Externos**: Consumo/envío de datos vía API

## 📊 Eventos Base del Sistema

El sistema incluye soporte predefinido para los siguientes eventos de trazabilidad:

1. **Riego**: Métodos, duración, volumen, CE, pH
2. **Fertilización**: Productos, dosis, métodos de aplicación
3. **Fitosanitarios**: Control de plagas y enfermedades
4. **Labores Culturales**: Poda, deshierbe, aclareo
5. **Monitoreo**: Plagas, enfermedades, malezas
6. **Variables Climáticas**: Temperatura, humedad, precipitación
7. **Cosecha**: Rendimiento, calidad, personal
8. **Poscosecha**: Almacenamiento, procesamiento
9. **Mano de Obra y Costos**: Registro económico

> **Nota**: El sistema permite crear eventos adicionales de forma dinámica según necesidades específicas.

## 📈 Variables Monitoreadas

### Variables de Suelo
- Humedad del suelo (%)
- Temperatura del suelo (°C)
- Conductividad eléctrica (µS/cm)
- pH

### Variables Climáticas
- Temperatura ambiente (°C)
- Humedad relativa (%)
- Precipitación (mm)
- Velocidad del viento (m/s)

### Índices de Vegetación
- NDVI (Normalized Difference Vegetation Index)
- NDRE (Normalized Difference Red Edge)

## 🚀 Estado del Proyecto

**Fase Actual**: Documentación y Diseño Inicial

### Hitos Completados
- ✅ Análisis de requerimientos
- ✅ Definición de arquitectura
- ✅ Diseño de base de datos

### Próximos Hitos
- ⏳ Setup inicial del proyecto Django
- ⏳ Implementación de modelos base
- ⏳ Desarrollo del sistema de eventos dinámicos

## 📅 Cronograma

El proyecto está planificado para **16 semanas** de desarrollo. Ver [Cronograma Detallado](./docs/08_cronograma.md).

## 📝 Licencia

Este proyecto es desarrollado como parte de un proyecto de Maestría en Ingeniería de Software.

## 📧 Contacto

Para más información sobre el proyecto, consulta la documentación en el directorio `/docs`.

---

**Última actualización**: Octubre 2025  
**Versión de la documentación**: 1.0
