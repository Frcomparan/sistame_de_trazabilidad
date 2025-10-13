### 1. Visión General y Características del Sistema

El proyecto consiste en el desarrollo de una **Plataforma Web de Trazabilidad Agrícola** para un centro de cultivo de limón. El sistema permitirá registrar, monitorear y consultar todas las actividades y variables relevantes a lo largo del ciclo de producción, desde la preparación del terreno hasta la post-cosecha.

**Características Principales:**

* **Trazabilidad Completa:** Permitirá seguir el historial de cada lote o parcela, consultando todos los eventos aplicados (riegos, fertilizaciones, cosechas, etc.).
* **Gestión Dinámica de Eventos:** El núcleo del sistema será un módulo que permita a los administradores **crear, modificar y definir nuevos tipos de eventos** de seguimiento, sin necesidad de alterar el código fuente. Esto asegura que el sistema pueda adaptarse a futuras necesidades de registro.
* **Interfaz Visual Intuitiva:** Un panel de control (dashboard) web facilitará a los usuarios (administradores, ingenieros agrónomos, personal de campo) el registro de datos y la visualización de reportes, gráficos e historiales.
* **API RESTful:** Expondrá los datos de forma segura para que puedan ser consumidos por otros servicios, como sistemas de análisis de datos, aplicaciones móviles o dispositivos IoT.
* **Orientado a Datos:** Centralizará la información para facilitar la toma de decisiones, la optimización de recursos y el cumplimiento de normativas.

---

### 2. Requerimientos Funcionales (RF)

Los requerimientos funcionales describen lo que el sistema **debe hacer**.

* **RF-01: Gestión de Usuarios y Roles:**
    * El sistema debe permitir el registro de usuarios.
    * Deben existir al menos tres roles: **Administrador** (control total), **Gestor de Campo** (registra y consulta eventos), y **Consultor** (solo lectura).
* **RF-02: Gestión de Activos Agrícolas:**
    * [cite_start]El sistema debe permitir registrar y gestionar las unidades productivas: **Lotes** o **Parcelas**[cite: 18, 31, 43]. Se debe poder registrar su nombre, tamaño y ubicación.
* **RF-03: Gestión de Tipos de Eventos (Dinámico):**
    * Un Administrador debe poder **crear un nuevo tipo de evento** (ej. "Análisis de Suelo").
    * Para cada tipo de evento, el Administrador debe poder **definir los campos de datos** a registrar (ej. para "Análisis de Suelo", podría añadir campos como "pH", "Materia Orgánica (%)", "Fósforo (ppm)").
    * Los campos deben tener tipos de datos definidos (texto, número, fecha, selección, etc.).
* **RF-04: Registro de Instancias de Eventos:**
    * Un Gestor de Campo debe poder seleccionar un Lote/Parcela y registrar una nueva instancia de un evento existente (ej. registrar una "Aplicación de Riego" para el "Lote 3").
    * Al registrar el evento, el sistema debe presentar el formulario con los campos definidos dinámicamente en el RF-03.
* **RF-05: Consulta y Visualización de Trazabilidad:**
    * Cualquier usuario debe poder seleccionar un Lote/Parcela y ver una **línea de tiempo cronológica** de todos los eventos registrados.
    * El sistema debe permitir filtrar los eventos por tipo y por rango de fechas.
* **RF-06: API de Consulta:**
    * El sistema debe proveer una API RESTful segura.
    * La API debe tener *endpoints* (puntos de acceso) para consultar lotes, tipos de eventos y los eventos registrados en un lote específico.
    * El acceso a la API debe estar protegido por un sistema de tokens o claves.

---

### 3. Requerimientos No Funcionales (RNF)

Los requerimientos no funcionales describen **cómo** el sistema debe operar.

* **RNF-01: Usabilidad:** La interfaz web debe ser clara, intuitiva y fácil de usar para personal con distintos niveles de habilidad tecnológica.
* **RNF-02: Seguridad:** El acceso al sistema debe ser mediante autenticación (usuario y contraseña). Los datos sensibles deben estar protegidos y la API debe implementar mecanismos de autorización.
* **RNF-03: Extensibilidad:** La arquitectura debe soportar la adición de nuevos tipos de eventos y campos de datos sin requerir modificaciones en el núcleo del sistema (cubierto por el diseño dinámico).
* **RNF-04: Rendimiento:** Las consultas de trazabilidad y las respuestas de la API deben ejecutarse en un tiempo razonable (ej. < 2 segundos) bajo una carga de trabajo normal.
* **RNF-05: Compatibilidad:** El sistema web debe ser compatible con los principales navegadores web modernos (Chrome, Firefox, Safari, Edge).

---

### 4. Arquitectura y Diseño de Clases

Para lograr la flexibilidad de eventos dinámicos, se propone una arquitectura basada en un modelo de "Entidad-Atributo-Valor" (EAV), pero estructurado de forma relacional.

A continuación, se presenta un diagrama de clases básico que representa esta idea. Las clases principales serían:

* **Lote (Plot):** Representa una parcela o lote de cultivo.
* **TipoEvento (EventType):** Define una categoría de evento, como "Riego" o "Cosecha". Contiene el nombre del tipo de evento.
* **DefinicionCampo (FieldDefinition):** Define un campo de datos para un `TipoEvento`. Por ejemplo, para el `TipoEvento` "Riego", una `DefinicionCampo` sería "Duración del riego" con el tipo de dato "Número" y la unidad "horas".
* **Evento (Event):** Representa una instancia real de un `TipoEvento` que ocurrió en un `Lote` en una fecha específica.
* **DatoEvento (EventData):** Almacena el valor concreto para una `DefinicionCampo` en un `Evento` específico. Por ejemplo, si el `Evento` #101 es un riego, este objeto guardaría el valor "2.5" para el campo "Duración del riego".


Este diseño desacopla la definición de los eventos de los datos, permitiendo que un administrador defina nuevos `TipoEvento` y sus `DefinicionCampo` a través de la interfaz, y el sistema los renderizará y almacenará sin cambios en el código.

---

### 5. Diseño de la Base de Datos (Esquema ER)

El diagrama de clases se traduce directamente en el siguiente esquema de base de datos relacional.

* **Tabla `Lotes`**:
    * `id` (PK)
    * `nombre`
    * `superficie_ha`
* **Tabla `TiposEvento`**:
    * `id` (PK)
    * [cite_start]`nombre` (ej. "Aplicación de fungicida / insecticida / herbicida" [cite: 41])
    * `descripcion`
* **Tabla `DefinicionesCampo`**:
    * `id` (PK)
    * `tipo_evento_id` (FK a `TiposEvento`)
    * [cite_start]`nombre_campo` (ej. "Producto (nombre comercial + ingrediente activo)" [cite: 44])
    * `tipo_dato` (ej. TEXT, INTEGER, DECIMAL, DATE)
    * [cite_start]`unidad` (ej. "kg/ha", "$L/ha$" [cite: 35])
* **Tabla `Eventos`**:
    * `id` (PK)
    * `lote_id` (FK a `Lotes`)
    * `tipo_evento_id` (FK a `TiposEvento`)
    * `fecha_evento`
    * `usuario_responsable_id` (FK a la tabla de Usuarios)
* **Tabla `DatosEvento`**:
    * `id` (PK)
    * `evento_id` (FK a `Eventos`)
    * `definicion_campo_id` (FK a `DefinicionesCampo`)
    * `valor` (un campo de texto flexible para almacenar el valor, que se interpretará según el `tipo_dato` de la definición)


---

### 6. Estructura de la API RESTful

La API podría seguir los principios REST y tener los siguientes *endpoints* básicos:

* `GET /api/lotes/`: Devuelve una lista de todos los lotes.
* `GET /api/lotes/{id}/`: Devuelve los detalles de un lote específico.
* `GET /api/lotes/{id}/eventos/`: Devuelve todos los eventos registrados para un lote, permitiendo filtros por fecha (ej. `?fecha_inicio=2025-01-01&fecha_fin=2025-01-31`).
* `GET /api/tipos-evento/`: Devuelve todos los tipos de evento configurables.
* `POST /api/eventos/`: Endpoint para registrar un nuevo evento. El cuerpo de la solicitud (en JSON) contendría el `lote_id`, `tipo_evento_id`, la fecha y un objeto o lista con los valores de los campos correspondientes.

---

### 7. Próximos Pasos Recomendados

1.  **Validar y Refinar Requerimientos:** Discute esta propuesta con los interesados (personal del centro de cultivo) para ajustar los detalles.
2.  **Diseñar Mockups/Wireframes:** Crea bocetos de las pantallas principales (login, dashboard, formulario de registro de eventos, vista de trazabilidad) para definir la experiencia de usuario.
3.  **Configurar el Entorno de Desarrollo:** Iniciar el proyecto en Django, configurar la base de datos y crear las aplicaciones iniciales (ej. `usuarios`, `finca`, `eventos`).
4.  **Desarrollo Iterativo:** Comienza implementando el núcleo del sistema (la gestión dinámica de eventos) y luego construye las demás funcionalidades a su alrededor.