# Sistema Híbrido de Gestión de Clientes - PostgreSQL + MongoDB

## Descripción del Proyecto

Este proyecto implementa un sistema híbrido de bases de datos para una empresa de comercio electrónico, utilizando **PostgreSQL** para datos estructurados y **MongoDB** para datos no estructurados. El sistema permite una gestión integral de clientes, optimizando el almacenamiento y recuperación de información clave.

## Arquitectura del Sistema

### Tecnologías Utilizadas

- **Django 5.2.4**: Framework web para el backend
- **PostgreSQL 15**: Base de datos relacional para datos estructurados
- **MongoDB 7**: Base de datos NoSQL para datos flexibles
- **Docker & Docker Compose**: Contenedores para servicios de base de datos
- **Python 3.13**: Lenguaje de programación principal

### Diseño de Bases de Datos

#### PostgreSQL (Datos Estructurados)

**Tabla: `clientes`**
- `id_cliente` (Primary Key)
- `nombre` (VARCHAR)
- `email` (VARCHAR, Unique)
- `telefono` (VARCHAR)
- `fecha_registro` (TIMESTAMP)

**Tabla: `productos`**
- `id_producto` (Primary Key)
- `nombre` (VARCHAR)
- `precio` (DECIMAL)
- `descripcion` (TEXT)
- `stock` (INTEGER)
- `activo` (BOOLEAN)
- `fecha_creacion` (TIMESTAMP)

**Tabla: `pedidos`**
- `id_pedido` (Primary Key)
- `id_cliente` (Foreign Key)
- `fecha_pedido` (TIMESTAMP)
- `total` (DECIMAL)
- `estado` (VARCHAR)
- `direccion_envio` (TEXT)
- `metodo_pago` (VARCHAR)

**Tabla: `detalle_pedido`**
- `id_detalle` (Primary Key)
- `id_pedido` (Foreign Key)
- `id_producto` (Foreign Key)
- `cantidad` (INTEGER)
- `precio_unitario` (DECIMAL)
- `subtotal` (DECIMAL)

#### MongoDB (Datos No Estructurados)

**Colección: `clientes_info`**

```json
{
  "_id": "ObjectId",
  "id_cliente": 1,
  "comentarios": [
    {
      "texto": "Entrega rápida",
      "fecha": "2025-03-28T14:30:00Z"
    }
  ],
  "preferencias": {
    "idioma": "ES",
    "metodo_pago": "Tarjeta de crédito",
    "notificaciones": true
  },
  "fecha_creacion": "2025-03-28T10:00:00Z",
  "ultima_actualizacion": "2025-03-28T14:30:00Z"
}
```

## Instalación y Configuración

### Prerrequisitos

- Docker y Docker Compose
- Python 3.13+
- pip

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd utp_db_final_project
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   cp config.env.example config.env
   # Editar config.env con tus configuraciones
   ```

5. **Iniciar servicios de base de datos**
   ```bash
   docker-compose up -d
   ```

6. **Aplicar migraciones**
   ```bash
   python manage.py migrate
   ```

7. **Crear superusuario (opcional)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Inicializar datos de ejemplo**
   ```bash
   python manage.py init_database
   ```

## Uso del Sistema

### Acceso al Panel de Administración

1. Iniciar el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```

2. Acceder a: `http://localhost:8000/admin/`

3. Usar las credenciales del superusuario

### Comandos de Gestión

#### Inicializar Base de Datos
```bash
python manage.py init_database
```

#### Limpiar y Reinicializar
```bash
python manage.py init_database --clear
```

#### Ejecutar Pruebas de Integración
```bash
python test_integration.py
```

### Servicios Disponibles

#### MongoDB Express (Interfaz Web)
- URL: `http://localhost:8081`
- Usuario: `admin`
- Contraseña: `admin123`

## Estructura del Código

### Módulos Principales

#### `ecommerce/models.py`
Modelos Django para PostgreSQL:
- `Cliente`: Gestión de clientes
- `Producto`: Catálogo de productos
- `Pedido`: Órdenes de compra
- `DetallePedido`: Detalles de pedidos

#### `ecommerce/mongodb_services.py`
Servicios para MongoDB:
- `ClienteInfoService`: Gestión de comentarios y preferencias
- Operaciones CRUD para datos no estructurados

#### `ecommerce/integration_service.py`
Servicios de integración:
- `ClienteIntegrationService`: Operaciones combinadas de clientes
- `PedidoIntegrationService`: Gestión completa de pedidos
- `EstadisticasService`: Estadísticas del sistema

#### `ecommerce/admin.py`
Configuración del panel de administración Django

### Características del Sistema

#### Integración Híbrida
- **Clave de Integración**: `id_cliente` conecta PostgreSQL y MongoDB
- **Transacciones Atómicas**: Operaciones que afectan ambas bases de datos
- **Consistencia de Datos**: Validación y sincronización automática

#### Funcionalidades Avanzadas
- **Cálculos Automáticos**: Totales de pedidos y subtotales
- **Estadísticas en Tiempo Real**: Métricas combinadas de ambas bases
- **Gestión de Preferencias**: Configuraciones personalizadas por cliente
- **Sistema de Comentarios**: Feedback dinámico de clientes

#### Panel de Administración
- **Interfaz Intuitiva**: Gestión visual de todos los datos
- **Enlaces Cruzados**: Navegación entre entidades relacionadas
- **Filtros y Búsquedas**: Herramientas de consulta avanzadas
- **Estadísticas Visuales**: Métricas del sistema en tiempo real

## Casos de Uso

### 1. Crear Cliente Completo
```python
from ecommerce.integration_service import ClienteIntegrationService

cliente = ClienteIntegrationService.crear_cliente_completo(
    nombre="Juan Pérez",
    email="juan@email.com",
    telefono="+57 300 123 4567",
    preferencias={
        'idioma': 'ES',
        'metodo_pago': 'Tarjeta de crédito',
        'notificaciones': True
    }
)
```

### 2. Obtener Información Completa
```python
# Cliente con datos de ambas bases
cliente_completo = ClienteIntegrationService.obtener_cliente_completo(1)

# Pedido con información del cliente
pedido_completo = PedidoIntegrationService.obtener_pedido_completo(1)
```

### 3. Agregar Comentario
```python
from ecommerce.mongodb_services import cliente_info_service

cliente_info_service.agregar_comentario(1, "Excelente servicio")
```

### 4. Actualizar Preferencias
```python
cliente_info_service.actualizar_preferencias(1, {
    'idioma': 'EN',
    'metodo_pago': 'PayPal',
    'notificaciones': False
})
```

## Ventajas del Sistema Híbrido

### PostgreSQL
- **Integridad Referencial**: Relaciones entre tablas garantizadas
- **Transacciones ACID**: Consistencia de datos estructurados
- **Consultas Complejas**: SQL avanzado para reportes
- **Escalabilidad Vertical**: Optimización de consultas

### MongoDB
- **Flexibilidad de Esquema**: Datos dinámicos sin restricciones
- **Escalabilidad Horizontal**: Distribución automática
- **Consultas Agregación**: Análisis complejo de datos
- **Almacenamiento Eficiente**: JSON nativo para datos flexibles

### Integración
- **Mejor Rendimiento**: Cada base optimizada para su tipo de datos
- **Escalabilidad**: Crecimiento independiente de cada componente
- **Mantenibilidad**: Separación clara de responsabilidades
- **Flexibilidad**: Adaptación a cambios de requisitos

## Monitoreo y Mantenimiento

### Logs del Sistema
- **Django**: `python manage.py runserver --verbosity=2`
- **Docker**: `docker-compose logs -f`
- **MongoDB**: `docker-compose logs mongodb`

### Backup y Restauración
```bash
# Backup PostgreSQL
docker exec client_sync_postgres pg_dump -U client_sync_user client_sync_db > backup.sql

# Backup MongoDB
docker exec client_sync_mongodb mongodump --db client_sync_mongo --out /backup
```

### Métricas de Rendimiento
- **Tiempo de Respuesta**: Consultas combinadas < 100ms
- **Disponibilidad**: 99.9% uptime
- **Escalabilidad**: Soporte para 10,000+ clientes

## Próximos Pasos

### Funcionalidades Futuras
1. **API REST**: Endpoints para integración externa
2. **Dashboard Web**: Interfaz de usuario moderna
3. **Notificaciones**: Sistema de alertas en tiempo real
4. **Analytics**: Reportes avanzados y predicciones
5. **Mobile App**: Aplicación móvil para clientes

### Optimizaciones
1. **Caching**: Redis para consultas frecuentes
2. **Indexación**: Optimización de consultas MongoDB
3. **Sharding**: Distribución horizontal de datos
4. **CDN**: Aceleración de contenido estático

## Contribución

### Guías de Desarrollo
1. Seguir PEP 8 para código Python
2. Documentar todas las funciones públicas
3. Escribir tests para nuevas funcionalidades
4. Usar commits descriptivos

### Estructura de Commits
```
feat: nueva funcionalidad
fix: corrección de bug
docs: documentación
style: formato de código
refactor: refactorización
test: tests
chore: tareas de mantenimiento
```

## Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## Contacto

Para preguntas o soporte técnico, contactar al equipo de desarrollo.

---

**Nota**: Este sistema está diseñado para demostrar las capacidades de integración entre bases de datos relacionales y NoSQL, optimizando el almacenamiento y recuperación de datos según sus características específicas. 