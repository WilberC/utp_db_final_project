# 🏪 Sistema de Administración Centralizada - E-commerce Híbrido

## 📋 Descripción General

Este sistema proporciona una **interfaz centralizada** para gestionar datos tanto de **PostgreSQL** (datos estructurados) como de **MongoDB** (datos dinámicos) a través del **Django Admin**. La aplicación sirve como punto único de administración para todo el sistema híbrido.

## 🎯 Características Principales

### ✅ Interfaz Centralizada
- **Panel de administración unificado** que integra PostgreSQL y MongoDB
- **Dashboard personalizado** con estadísticas en tiempo real
- **Navegación intuitiva** entre diferentes módulos
- **Acciones masivas** para gestionar múltiples registros

### 🔗 Integración de Sistemas
- **Conexión automática** a PostgreSQL para datos estructurados
- **Conexión automática** a MongoDB para datos dinámicos
- **Sincronización bidireccional** entre ambas bases de datos
- **Campo `id_cliente`** como llave de integración

### 🛠️ Funciones y Operaciones

#### 📊 Gestión de Clientes
- **Vista completa** de información del cliente (PostgreSQL + MongoDB)
- **Comentarios dinámicos** almacenados en MongoDB
- **Preferencias personalizadas** (idioma, método de pago, notificaciones)
- **Estadísticas automáticas** (total de pedidos, monto gastado)
- **Acciones rápidas** para agregar comentarios y actualizar preferencias

#### 📦 Gestión de Productos
- **Control de inventario** con stock en tiempo real
- **Estados activo/inactivo** para productos
- **Estadísticas de ventas** por producto
- **Acciones masivas** para activar/desactivar productos

#### 🛒 Gestión de Pedidos
- **Seguimiento de estados** (pendiente, confirmado, en proceso, enviado, entregado)
- **Cálculo automático** de totales
- **Gestión de detalles** de pedidos
- **Acciones masivas** para cambiar estados

#### 📈 Reportes y Estadísticas
- **Dashboard principal** con métricas clave
- **Productos más vendidos**
- **Clientes más activos**
- **Pedidos del día**
- **Exportación de datos** en formato JSON

## 🚀 Cómo Acceder al Sistema

### 1. Iniciar el Servidor
```bash
# Activar entorno virtual
source venv/bin/activate

# Iniciar servidor de desarrollo
python manage.py runserver 0.0.0.0:8000
```

### 2. Acceder al Admin
- **URL**: `http://localhost:8000/admin/`
- **Usuario**: Tu superusuario existente
- **Contraseña**: Tu contraseña de superusuario

## 📱 Interfaz de Usuario

### 🏠 Dashboard Principal
El dashboard muestra:
- **Tarjetas de estadísticas** con métricas clave
- **Productos más vendidos** (top 5)
- **Clientes más activos** (top 5)
- **Acciones rápidas** para crear nuevos registros

### 👥 Gestión de Clientes
**Lista de Clientes:**
- ID, Nombre, Email, Teléfono
- Estado de sincronización con MongoDB
- Total de pedidos y monto gastado
- Botones de acciones rápidas

**Vista Detallada de Cliente:**
- Información básica (PostgreSQL)
- Comentarios dinámicos (MongoDB)
- Preferencias personalizadas (MongoDB)
- Estadísticas automáticas

**Acciones Disponibles:**
- ✅ **Sincronizar con MongoDB**: Crea documentos en MongoDB para clientes seleccionados
- 📤 **Exportar datos completos**: Exporta información combinada de PostgreSQL y MongoDB
- 🧹 **Limpiar comentarios**: Mantiene solo los últimos 10 comentarios

### 📦 Gestión de Productos
**Lista de Productos:**
- ID, Nombre, Precio, Stock
- Estado activo/inactivo
- Contador de ventas
- Fecha de creación

**Acciones Disponibles:**
- ✅ **Activar productos**: Marca productos como activos
- ❌ **Desactivar productos**: Marca productos como inactivos
- 📊 **Ajustar stock**: Función para ajustar inventario

### 🛒 Gestión de Pedidos
**Lista de Pedidos:**
- ID, Cliente, Fecha, Total
- Estado del pedido
- Método de pago
- Número de productos

**Acciones Disponibles:**
- 📦 **Marcar como enviado**: Cambia estado a "enviado"
- ✅ **Marcar como entregado**: Cambia estado a "entregado"
- 📤 **Exportar pedidos completos**: Exporta información detallada

## 🔧 Funcionalidades Avanzadas

### 🔄 Sincronización Automática
- **Creación automática** de documentos MongoDB al crear clientes
- **Actualización bidireccional** de datos
- **Validación de integridad** entre bases de datos

### 📊 Reportes Integrados
- **Estadísticas combinadas** de PostgreSQL y MongoDB
- **Métricas en tiempo real**
- **Exportación de datos** en múltiples formatos

### 🛡️ Seguridad y Mantenimiento
- **Control de acceso** basado en permisos de Django
- **Validación de datos** en ambas bases de datos
- **Logging automático** de operaciones
- **Respaldos integrados** del sistema

## 📁 Estructura de Archivos

```
ecommerce/
├── admin.py                    # Configuración principal del admin
├── models.py                   # Modelos de PostgreSQL
├── mongodb_services.py         # Servicios para MongoDB
├── integration_service.py      # Servicio de integración
├── templates/
│   └── admin/
│       ├── index.html          # Dashboard personalizado
│       └── ecommerce/
│           └── cliente/
│               ├── agregar_comentario.html
│               └── actualizar_preferencias.html
```

## 🎨 Personalización del Admin

### 🎯 Características Implementadas
- **Header personalizado** con emoji y branding
- **Dashboard con estadísticas** en tiempo real
- **Vistas personalizadas** para comentarios y preferencias
- **Acciones masivas** para operaciones comunes
- **Enlaces cruzados** entre entidades relacionadas

### 🔧 Cómo Personalizar
1. **Modificar `admin.py`** para cambiar la configuración
2. **Editar plantillas** en `templates/admin/`
3. **Agregar acciones** personalizadas en las clases Admin
4. **Personalizar estilos** CSS en las plantillas

## 🚀 Beneficios del Sistema

### ✅ Usabilidad
- **Interfaz intuitiva** para usuarios no técnicos
- **Navegación clara** entre diferentes módulos
- **Acciones rápidas** para operaciones comunes
- **Feedback visual** del estado del sistema

### ⚡ Eficiencia Operativa
- **Gestión centralizada** de ambas bases de datos
- **Operaciones masivas** para múltiples registros
- **Cálculos automáticos** de totales y estadísticas
- **Exportación rápida** de datos

### 📈 Escalabilidad
- **Arquitectura modular** fácil de extender
- **Servicios reutilizables** para MongoDB y PostgreSQL
- **Plantillas personalizables** para diferentes necesidades
- **API preparada** para futuras integraciones

## 🔍 Troubleshooting

### Problemas Comunes
1. **Error de conexión a MongoDB**: Verificar configuración en `config.env`
2. **Error de migración**: Ejecutar `python manage.py migrate`
3. **Plantillas no encontradas**: Verificar estructura de directorios
4. **Permisos de admin**: Verificar que el usuario sea superusuario

### Logs y Debugging
- **Logs de Django**: Revisar salida del servidor
- **Logs de MongoDB**: Verificar conexión en `mongodb_services.py`
- **Logs de PostgreSQL**: Verificar configuración de base de datos

## 📞 Soporte

Para problemas o preguntas sobre el sistema de administración:
1. Revisar este README
2. Verificar logs del servidor
3. Consultar la documentación de Django Admin
4. Revisar la configuración en `config.env`

---

**🎉 ¡El sistema está listo para usar!** Accede a `http://localhost:8000/admin/` para comenzar a gestionar tu e-commerce híbrido. 