# Referencias

[← Volver al índice](../README.md) | [← Glosario](./glosario.md)

## 1. Documentos del Proyecto

### 1.1 Documentos Fuente

| Documento | Descripción | Ubicación |
|-----------|-------------|-----------|
| **propuesta_chat.md** | Propuesta inicial generada por agente IA (ChatGPT) | `/propuesta_chat.md` |
| **propuesta_gemini.md** | Propuesta inicial generada por Gemini | `/propuesta_gemini.md` |
| **Sistema_IoT_Monitoreo_de_Variables.pdf** | Documento de referencia con eventos y variables base | Adjunto |

### 1.2 Documentos de Diseño

Toda la documentación del proyecto se encuentra en el directorio `/docs/`:

- [01_vision_alcance.md](./01_vision_alcance.md)
- [02_requerimientos.md](./02_requerimientos.md)
- [03_arquitectura.md](./03_arquitectura.md)
- [04_modelo_dominio.md](./04_modelo_dominio.md)
- [05_base_datos.md](./05_base_datos.md)
- [06_api_rest.md](./06_api_rest.md)
- [07_eventos_dinamicos.md](./07_eventos_dinamicos.md)
- [08_cronograma.md](./08_cronograma.md)
- [09_riesgos.md](./09_riesgos.md)
- [10_pruebas.md](./10_pruebas.md)
- [glosario.md](./glosario.md)

## 2. Tecnologías y Frameworks

### 2.1 Backend

| Tecnología | Versión | Documentación Oficial | Propósito |
|------------|---------|----------------------|-----------|
| **Python** | 3.11+ | https://docs.python.org/3/ | Lenguaje principal |
| **Django** | 5.0 | https://docs.djangoproject.com/en/5.0/ | Framework web |
| **Django REST Framework** | 3.14+ | https://www.django-rest-framework.org/ | API REST |
| **PostgreSQL** | 15+ | https://www.postgresql.org/docs/15/ | Base de datos |
| **psycopg2** | 2.9+ | https://www.psycopg.org/docs/ | Adaptador PostgreSQL |

### 2.2 Librerías Python

| Librería | Versión | Documentación | Propósito |
|----------|---------|---------------|-----------|
| **jsonschema** | 4.x | https://python-jsonschema.readthedocs.io/ | Validación JSON Schema |
| **djangorestframework-simplejwt** | 5.3+ | https://django-rest-framework-simplejwt.readthedocs.io/ | Autenticación JWT |
| **drf-spectacular** | 0.27+ | https://drf-spectacular.readthedocs.io/ | Documentación OpenAPI |
| **django-cors-headers** | 4.x | https://github.com/adamchainz/django-cors-headers | Control CORS |
| **django-filter** | 23.x | https://django-filter.readthedocs.io/ | Filtros avanzados |
| **Pillow** | 10.x | https://pillow.readthedocs.io/ | Procesamiento imágenes |
| **openpyxl** | 3.x | https://openpyxl.readthedocs.io/ | Exportación Excel |

### 2.3 Testing

| Herramienta | Versión | Documentación | Propósito |
|-------------|---------|---------------|-----------|
| **pytest** | 7.x | https://docs.pytest.org/ | Framework de testing |
| **pytest-django** | 4.x | https://pytest-django.readthedocs.io/ | Pytest + Django |
| **pytest-cov** | 4.x | https://pytest-cov.readthedocs.io/ | Cobertura de código |
| **factory-boy** | 3.x | https://factoryboy.readthedocs.io/ | Fixtures de datos |
| **Locust** | 2.x | https://docs.locust.io/ | Pruebas de carga |
| **Playwright** | 1.x | https://playwright.dev/python/ | Pruebas E2E |

### 2.4 Frontend

| Tecnología | Versión | Documentación | Propósito |
|------------|---------|---------------|-----------|
| **HTMX** | 1.9+ | https://htmx.org/docs/ | Interactividad HTML |
| **Alpine.js** | 3.x | https://alpinejs.dev/ | JavaScript reactivo |
| **Bootstrap** | 5.3 | https://getbootstrap.com/docs/5.3/ | Framework CSS |
| **Chart.js** | 4.x | https://www.chartjs.org/docs/ | Gráficos |

### 2.5 Infraestructura

| Herramienta | Versión | Documentación | Propósito |
|-------------|---------|---------------|-----------|
| **Gunicorn** | 21.x | https://docs.gunicorn.org/ | Servidor WSGI |
| **Nginx** | 1.24+ | https://nginx.org/en/docs/ | Proxy inverso |
| **PostgreSQL + PostGIS** | 15 + 3.3 | https://postgis.net/docs/ | Base de datos geoespacial |

## 3. Estándares y Especificaciones

### 3.1 JSON Schema

- **JSON Schema Draft-07**: https://json-schema.org/draft-07/json-schema-release-notes.html
- **Understanding JSON Schema**: https://json-schema.org/understanding-json-schema/

### 3.2 APIs REST

- **REST API Best Practices**: https://restfulapi.net/
- **OpenAPI 3.0 Specification**: https://swagger.io/specification/
- **HTTP Status Codes**: https://httpstatuses.com/

### 3.3 Seguridad

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **OWASP REST Security Cheat Sheet**: https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html
- **Django Security**: https://docs.djangoproject.com/en/5.0/topics/security/

### 3.4 Bases de Datos

- **PostgreSQL JSON Functions**: https://www.postgresql.org/docs/15/functions-json.html
- **GIN Indexes**: https://www.postgresql.org/docs/15/gin-intro.html
- **Table Partitioning**: https://www.postgresql.org/docs/15/ddl-partitioning.html

## 4. Metodologías y Buenas Prácticas

### 4.1 Desarrollo

- **PEP 8 - Style Guide for Python Code**: https://peps.python.org/pep-0008/
- **Django Coding Style**: https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/
- **The Twelve-Factor App**: https://12factor.net/
- **Semantic Versioning**: https://semver.org/

### 4.2 Testing

- **Test-Driven Development (TDD)**: http://testdriven.io/
- **Testing Best Practices**: https://docs.pytest.org/en/stable/goodpractices.html
- **Django Testing**: https://docs.djangoproject.com/en/5.0/topics/testing/

### 4.3 Git

- **Conventional Commits**: https://www.conventionalcommits.org/
- **Git Flow**: https://nvie.com/posts/a-successful-git-branching-model/
- **Semantic Commit Messages**: https://gist.github.com/joshbuchea/6f47e86d2510bce28f8e7f42ae84c716

## 5. Libros y Artículos

### 5.1 Django y Python

1. **"Two Scoops of Django"** - Daniel Roy Greenfeld & Audrey Roy Greenfeld  
   *Best practices para Django*  
   https://www.feldroy.com/books/two-scoops-of-django-3-x

2. **"Django for APIs"** - William S. Vincent  
   *Construcción de APIs web con Django REST Framework*  
   https://djangoforapis.com/

3. **"Fluent Python"** - Luciano Ramalho  
   *Python idiomático y avanzado*  
   https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/

### 5.2 Arquitectura de Software

4. **"Clean Architecture"** - Robert C. Martin  
   *Principios de diseño de software*  
   https://www.oreilly.com/library/view/clean-architecture-a/9780134494272/

5. **"Domain-Driven Design"** - Eric Evans  
   *Modelado de dominios complejos*  
   https://www.domainlanguage.com/ddd/

### 5.3 Bases de Datos

6. **"PostgreSQL: Up and Running"** - Regina Obe & Leo Hsu  
   *Guía práctica de PostgreSQL*  
   https://www.oreilly.com/library/view/postgresql-up-and/9781491963417/

7. **"High Performance PostgreSQL"** - Ibrar Ahmed, et al.  
   *Optimización y tuning*  
   https://www.packtpub.com/product/postgresql-13-cookbook/9781838648138

## 6. Tutoriales y Recursos de Aprendizaje

### 6.1 Django

- **Official Django Tutorial**: https://docs.djangoproject.com/en/5.0/intro/tutorial01/
- **Django Girls Tutorial**: https://tutorial.djangogirls.org/
- **Real Python - Django Tutorials**: https://realpython.com/tutorials/django/

### 6.2 Django REST Framework

- **DRF Official Tutorial**: https://www.django-rest-framework.org/tutorial/quickstart/
- **Building APIs with Django and DRF**: https://testdriven.io/blog/drf-views-part-1/

### 6.3 PostgreSQL y JSONB

- **PostgreSQL JSONB Tutorial**: https://www.postgresql.org/docs/current/datatype-json.html
- **Indexing JSONB columns**: https://www.postgresql.org/docs/current/datatype-json.html#JSON-INDEXING

### 6.4 Testing

- **Pytest Documentation**: https://docs.pytest.org/en/stable/contents.html
- **Django Testing Tutorial**: https://docs.djangoproject.com/en/5.0/topics/testing/tutorial/

## 7. Herramientas de Desarrollo

### 7.1 IDEs y Editores

- **Visual Studio Code**: https://code.visualstudio.com/
- **PyCharm**: https://www.jetbrains.com/pycharm/
- **Vim with Python**: https://realpython.com/vim-and-python-a-match-made-in-heaven/

### 7.2 Extensiones VS Code

- **Python** (Microsoft): https://marketplace.visualstudio.com/items?itemName=ms-python.python
- **Django** (Baptiste Darthenay): https://marketplace.visualstudio.com/items?itemName=batisteo.vscode-django
- **PostgreSQL** (Chris Kolkman): https://marketplace.visualstudio.com/items?itemName=ckolkman.vscode-postgres

### 7.3 Herramientas de Análisis

- **Bandit** (seguridad): https://bandit.readthedocs.io/
- **Safety** (vulnerabilidades): https://pyup.io/safety/
- **Pylint**: https://pylint.pycqa.org/
- **Flake8**: https://flake8.pycqa.org/

## 8. Comunidad y Soporte

### 8.1 Foros y Discusión

- **Django Forum**: https://forum.djangoproject.com/
- **Stack Overflow - Django**: https://stackoverflow.com/questions/tagged/django
- **Reddit - r/django**: https://www.reddit.com/r/django/
- **Django Discord**: https://discord.gg/xcRH6mN4fa

### 8.2 Listas de Correo

- **Django Users**: https://groups.google.com/g/django-users
- **Django Developers**: https://groups.google.com/g/django-developers

## 9. Trazabilidad Agrícola y Normativas

### 9.1 Estándares de Certificación

- **GlobalGAP**: https://www.globalgap.org/
- **Certificación Orgánica (USDA)**: https://www.ams.usda.gov/about-ams/programs-offices/national-organic-program
- **SENASICA (México)**: https://www.gob.mx/senasica

### 9.2 IoT Agrícola

- **MQTT Protocol**: https://mqtt.org/
- **LoRaWAN for Agriculture**: https://lora-alliance.org/
- **Agricultural Sensors Guide**: https://www.agritech.tnau.ac.in/

### 9.3 Índices de Vegetación

- **NDVI Explanation**: https://earthobservatory.nasa.gov/features/MeasuringVegetation/measuring_vegetation_2.php
- **NDRE in Precision Agriculture**: https://www.sensefly.com/education/tutorials/ndre-ndvi-drones-crop-health/

## 10. Buenas Prácticas de Proyecto

### 10.1 Documentación

- **Write the Docs**: https://www.writethedocs.org/
- **Markdown Guide**: https://www.markdownguide.org/
- **README Best Practices**: https://github.com/matiassingers/awesome-readme

### 10.2 Control de Versiones

- **Pro Git Book**: https://git-scm.com/book/en/v2
- **Git Best Practices**: https://sethrobertson.github.io/GitBestPractices/

### 10.3 CI/CD

- **GitHub Actions**: https://docs.github.com/en/actions
- **GitLab CI/CD**: https://docs.gitlab.com/ee/ci/
- **Docker for Django**: https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/

## 11. Licencias

### 11.1 Open Source

- **MIT License**: https://opensource.org/licenses/MIT
- **Apache License 2.0**: https://opensource.org/licenses/Apache-2.0
- **GNU GPL v3**: https://www.gnu.org/licenses/gpl-3.0.en.html

### 11.2 Creative Commons (Documentación)

- **CC BY 4.0**: https://creativecommons.org/licenses/by/4.0/

---

## 12. Contacto y Contribución

### Repositorio del Proyecto

```
git clone https://github.com/tu-usuario/trazabilidad-agricola.git
```

### Autor

**Proyecto de Maestría en Ingeniería de Software**  
Fecha: Octubre 2025

### Contribuciones

Este proyecto es académico. Para consultas o sugerencias, abrir un issue en el repositorio.

---

**Última actualización**: Octubre 2025

[← Volver al índice](../README.md)
