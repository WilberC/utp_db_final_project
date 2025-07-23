from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import Cliente, Producto, Pedido, DetallePedido
from .mongodb_services import ClienteInfoService
from .integration_service import ClienteIntegrationService, PedidoIntegrationService, EstadisticasService


class ComentarioInline(admin.TabularInline):
    """Inline para mostrar comentarios de MongoDB"""
    model = None  # No es un modelo real, solo para la interfaz
    extra = 0
    readonly_fields = ['texto', 'fecha']
    fields = ['texto', 'fecha']
    template = 'admin/ecommerce/cliente/comentarios_inline.html'
    
    def has_add_permission(self, request, obj=None):
        return True
    
    def has_delete_permission(self, request, obj=None):
        return True


class ClienteAdmin(admin.ModelAdmin):
    list_display = [
        'id_cliente', 'nombre', 'email', 'telefono', 'fecha_registro', 
        'total_pedidos', 'total_gastado', 'estado_mongo', 'acciones_rapidas'
    ]
    list_filter = ['fecha_registro', 'activo']
    search_fields = ['nombre', 'email', 'telefono']
    readonly_fields = [
        'id_cliente', 'fecha_registro', 'total_pedidos', 'total_gastado',
        'comentarios_display', 'preferencias_display'
    ]
    ordering = ['-fecha_registro']
    actions = ['sincronizar_mongodb', 'exportar_datos_completos', 'limpiar_comentarios']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'email', 'telefono')
        }),
        ('Información de MongoDB', {
            'fields': ('comentarios_display', 'preferencias_display'),
            'classes': ('collapse',)
        }),
        ('Estadísticas', {
            'fields': ('total_pedidos', 'total_gastado'),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('id_cliente', 'fecha_registro'),
            'classes': ('collapse',)
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:cliente_id>/agregar_comentario/',
                self.admin_site.admin_view(self.agregar_comentario_view),
                name='ecommerce_cliente_agregar_comentario',
            ),
            path(
                '<int:cliente_id>/actualizar_preferencias/',
                self.admin_site.admin_view(self.actualizar_preferencias_view),
                name='ecommerce_cliente_actualizar_preferencias',
            ),
        ]
        return custom_urls + urls
    
    def estado_mongo(self, obj):
        """Indica si el cliente tiene datos en MongoDB"""
        try:
            info = ClienteInfoService().obtener_info_completa(obj.id_cliente)
            if info:
                return format_html(
                    '<span style="color: green;">✓ Sincronizado</span>'
                )
            else:
                return format_html(
                    '<span style="color: orange;">⚠ Sin datos</span>'
                )
        except:
            return format_html(
                '<span style="color: red;">✗ Error</span>'
            )
    estado_mongo.short_description = 'Estado MongoDB'
    
    def acciones_rapidas(self, obj):
        """Botones de acciones rápidas"""
        return format_html(
            '<a href="{}" class="button">Comentario</a> '
            '<a href="{}" class="button">Preferencias</a>',
            reverse('admin:ecommerce_cliente_agregar_comentario', args=[obj.id_cliente]),
            reverse('admin:ecommerce_cliente_actualizar_preferencias', args=[obj.id_cliente])
        )
    acciones_rapidas.short_description = 'Acciones'
    
    def comentarios_display(self, obj):
        """Muestra comentarios de MongoDB"""
        try:
            info = ClienteInfoService().obtener_info_completa(obj.id_cliente)
            if info and info.get('comentarios'):
                comentarios_html = []
                for comentario in info['comentarios'][-5:]:  # Últimos 5 comentarios
                    fecha = comentario.get('fecha', 'Sin fecha')
                    if isinstance(fecha, datetime):
                        fecha = fecha.strftime('%d/%m/%Y %H:%M')
                    comentarios_html.append(
                        f'<div style="border-left: 3px solid #007cba; padding-left: 10px; margin: 5px 0;">'
                        f'<strong>{fecha}</strong><br>{comentario.get("texto", "")}'
                        f'</div>'
                    )
                return mark_safe(''.join(comentarios_html))
            else:
                return '<em>Sin comentarios</em>'
        except Exception as e:
            return f'<span style="color: red;">Error: {str(e)}</span>'
    comentarios_display.short_description = 'Comentarios'
    
    def preferencias_display(self, obj):
        """Muestra preferencias de MongoDB"""
        try:
            info = ClienteInfoService().obtener_info_completa(obj.id_cliente)
            if info and info.get('preferencias'):
                prefs = info['preferencias']
                return format_html(
                    '<strong>Idioma:</strong> {}<br>'
                    '<strong>Método de pago:</strong> {}<br>'
                    '<strong>Notificaciones:</strong> {}',
                    prefs.get('idioma', 'No especificado'),
                    prefs.get('metodo_pago', 'No especificado'),
                    'Sí' if prefs.get('notificaciones') else 'No'
                )
            else:
                return '<em>Sin preferencias configuradas</em>'
        except Exception as e:
            return f'<span style="color: red;">Error: {str(e)}</span>'
    preferencias_display.short_description = 'Preferencias'
    
    def total_pedidos(self, obj):
        return obj.total_pedidos
    total_pedidos.short_description = 'Total Pedidos'
    
    def total_gastado(self, obj):
        return f"${obj.total_gastado:,.2f}"
    total_gastado.short_description = 'Total Gastado'
    
    def agregar_comentario_view(self, request, cliente_id):
        """Vista para agregar comentarios"""
        if request.method == 'POST':
            texto = request.POST.get('texto')
            if texto:
                service = ClienteInfoService()
                if service.agregar_comentario(cliente_id, texto):
                    messages.success(request, 'Comentario agregado exitosamente.')
                else:
                    messages.error(request, 'Error al agregar comentario.')
            return redirect('admin:ecommerce_cliente_change', cliente_id)
        
        cliente = Cliente.objects.get(id_cliente=cliente_id)
        context = {
            'title': f'Agregar Comentario - {cliente.nombre}',
            'cliente': cliente,
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'admin/ecommerce/cliente/agregar_comentario.html', context)
    
    def actualizar_preferencias_view(self, request, cliente_id):
        """Vista para actualizar preferencias"""
        if request.method == 'POST':
            preferencias = {
                'idioma': request.POST.get('idioma', 'ES'),
                'metodo_pago': request.POST.get('metodo_pago', 'Tarjeta de crédito'),
                'notificaciones': request.POST.get('notificaciones') == 'on'
            }
            service = ClienteInfoService()
            if service.actualizar_preferencias(cliente_id, preferencias):
                messages.success(request, 'Preferencias actualizadas exitosamente.')
            else:
                messages.error(request, 'Error al actualizar preferencias.')
            return redirect('admin:ecommerce_cliente_change', cliente_id)
        
        cliente = Cliente.objects.get(id_cliente=cliente_id)
        service = ClienteInfoService()
        info = service.obtener_info_completa(cliente_id)
        preferencias = info.get('preferencias', {}) if info else {}
        
        context = {
            'title': f'Actualizar Preferencias - {cliente.nombre}',
            'cliente': cliente,
            'preferencias': preferencias,
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'admin/ecommerce/cliente/actualizar_preferencias.html', context)
    
    def sincronizar_mongodb(self, request, queryset):
        """Acción para sincronizar datos con MongoDB"""
        service = ClienteInfoService()
        sincronizados = 0
        for cliente in queryset:
            if service.crear_documento_cliente(cliente.id_cliente):
                sincronizados += 1
        
        messages.success(
            request, 
            f'{sincronizados} de {queryset.count()} clientes sincronizados con MongoDB.'
        )
    sincronizar_mongodb.short_description = "Sincronizar con MongoDB"
    
    def exportar_datos_completos(self, request, queryset):
        """Acción para exportar datos completos"""
        datos_completos = []
        for cliente in queryset:
            datos = ClienteIntegrationService.obtener_cliente_completo(cliente.id_cliente)
            if datos:
                datos_completos.append(datos)
        
        response = JsonResponse(datos_completos, safe=False)
        response['Content-Disposition'] = f'attachment; filename="clientes_completos_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
        return response
    exportar_datos_completos.short_description = "Exportar datos completos"
    
    def limpiar_comentarios(self, request, queryset):
        """Acción para limpiar comentarios antiguos"""
        service = ClienteInfoService()
        limpiados = 0
        for cliente in queryset:
            info = service.obtener_info_completa(cliente.id_cliente)
            if info and info.get('comentarios'):
                # Mantener solo los últimos 10 comentarios
                comentarios = info['comentarios'][-10:]
                service.actualizar_preferencias(cliente.id_cliente, info.get('preferencias', {}))
                limpiados += 1
        
        messages.success(
            request, 
            f'Comentarios limpiados para {limpiados} clientes.'
        )
    limpiar_comentarios.short_description = "Limpiar comentarios antiguos"


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    readonly_fields = ['subtotal']
    fields = ['id_producto', 'cantidad', 'precio_unitario', 'subtotal']


class PedidoAdmin(admin.ModelAdmin):
    list_display = [
        'id_pedido', 'cliente_link', 'fecha_pedido', 'total', 
        'estado', 'metodo_pago', 'productos_count'
    ]
    list_filter = ['estado', 'fecha_pedido', 'metodo_pago']
    search_fields = ['id_cliente__nombre', 'id_cliente__email']
    readonly_fields = ['id_pedido', 'fecha_pedido', 'total']
    ordering = ['-fecha_pedido']
    inlines = [DetallePedidoInline]
    actions = ['marcar_entregado', 'marcar_enviado', 'exportar_pedido_completo']
    
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('id_cliente',)
        }),
        ('Información del Pedido', {
            'fields': ('estado', 'direccion_envio', 'metodo_pago')
        }),
        ('Información del Sistema', {
            'fields': ('id_pedido', 'fecha_pedido', 'total'),
            'classes': ('collapse',)
        }),
    )
    
    def cliente_link(self, obj):
        if obj.id_cliente:
            url = reverse('admin:ecommerce_cliente_change', args=[obj.id_cliente.id_cliente])
            return format_html('<a href="{}">{}</a>', url, obj.id_cliente.nombre)
        return "-"
    cliente_link.short_description = 'Cliente'
    cliente_link.admin_order_field = 'id_cliente__nombre'
    
    def productos_count(self, obj):
        return obj.detalles.count()
    productos_count.short_description = 'Productos'
    
    def total(self, obj):
        return f"${obj.total:,.2f}"
    total.short_description = 'Total'
    
    def marcar_entregado(self, request, queryset):
        """Acción para marcar pedidos como entregados"""
        actualizados = queryset.update(estado='entregado')
        messages.success(request, f'{actualizados} pedidos marcados como entregados.')
    marcar_entregado.short_description = "Marcar como entregado"
    
    def marcar_enviado(self, request, queryset):
        """Acción para marcar pedidos como enviados"""
        actualizados = queryset.update(estado='enviado')
        messages.success(request, f'{actualizados} pedidos marcados como enviados.')
    marcar_enviado.short_description = "Marcar como enviado"
    
    def exportar_pedido_completo(self, request, queryset):
        """Acción para exportar pedidos completos"""
        datos_completos = []
        for pedido in queryset:
            datos = PedidoIntegrationService.obtener_pedido_completo(pedido.id_pedido)
            if datos:
                datos_completos.append(datos)
        
        response = JsonResponse(datos_completos, safe=False)
        response['Content-Disposition'] = f'attachment; filename="pedidos_completos_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
        return response
    exportar_pedido_completo.short_description = "Exportar pedidos completos"


class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        'id_producto', 'nombre', 'precio', 'stock', 'activo', 
        'fecha_creacion', 'ventas_count'
    ]
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['id_producto', 'fecha_creacion']
    ordering = ['nombre']
    actions = ['activar_productos', 'desactivar_productos', 'ajustar_stock']
    
    fieldsets = (
        ('Información del Producto', {
            'fields': ('nombre', 'descripcion', 'precio', 'stock')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Información del Sistema', {
            'fields': ('id_producto', 'fecha_creacion'),
            'classes': ('collapse',)
        }),
    )
    
    def precio(self, obj):
        return f"${obj.precio:,.2f}"
    precio.short_description = 'Precio'
    
    def ventas_count(self, obj):
        return obj.detallepedido_set.count()
    ventas_count.short_description = 'Ventas'
    
    def activar_productos(self, request, queryset):
        """Acción para activar productos"""
        actualizados = queryset.update(activo=True)
        messages.success(request, f'{actualizados} productos activados.')
    activar_productos.short_description = "Activar productos"
    
    def desactivar_productos(self, request, queryset):
        """Acción para desactivar productos"""
        actualizados = queryset.update(activo=False)
        messages.success(request, f'{actualizados} productos desactivados.')
    desactivar_productos.short_description = "Desactivar productos"
    
    def ajustar_stock(self, request, queryset):
        """Acción para ajustar stock"""
        # Esta es una acción de ejemplo, se puede implementar una vista personalizada
        messages.info(request, 'Función de ajuste de stock en desarrollo.')
    ajustar_stock.short_description = "Ajustar stock"


class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = [
        'id_detalle', 'pedido_link', 'producto_link', 'cantidad', 
        'precio_unitario', 'subtotal'
    ]
    list_filter = ['id_pedido__fecha_pedido']
    search_fields = ['id_pedido__id_cliente__nombre', 'id_producto__nombre']
    readonly_fields = ['id_detalle', 'subtotal']
    ordering = ['-id_pedido__fecha_pedido']
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('id_pedido',)
        }),
        ('Información del Producto', {
            'fields': ('id_producto', 'cantidad', 'precio_unitario')
        }),
        ('Información del Sistema', {
            'fields': ('id_detalle', 'subtotal'),
            'classes': ('collapse',)
        }),
    )
    
    def pedido_link(self, obj):
        if obj.id_pedido:
            url = reverse('admin:ecommerce_pedido_change', args=[obj.id_pedido.id_pedido])
            return format_html('<a href="{}">Pedido #{}</a>', url, obj.id_pedido.id_pedido)
        return "-"
    pedido_link.short_description = 'Pedido'
    pedido_link.admin_order_field = 'id_pedido__id_pedido'
    
    def producto_link(self, obj):
        if obj.id_producto:
            url = reverse('admin:ecommerce_producto_change', args=[obj.id_producto.id_producto])
            return format_html('<a href="{}">{}</a>', url, obj.id_producto.nombre)
        return "-"
    producto_link.short_description = 'Producto'
    producto_link.admin_order_field = 'id_producto__nombre'
    
    def precio_unitario(self, obj):
        return f"${obj.precio_unitario:,.2f}"
    precio_unitario.short_description = 'Precio Unitario'
    
    def subtotal(self, obj):
        return f"${obj.subtotal:,.2f}"
    subtotal.short_description = 'Subtotal'


# Configuración del sitio de administración
admin.site.site_header = "🏪 Sistema Híbrido E-commerce"
admin.site.site_title = "Sistema Híbrido PostgreSQL + MongoDB"
admin.site.index_title = "Panel de Administración Centralizada"

# Personalización del índice del admin
class CustomAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        """Vista personalizada del índice con estadísticas"""
        extra_context = extra_context or {}
        
        # Estadísticas generales
        stats = EstadisticasService.obtener_estadisticas_generales()
        
        # Estadísticas adicionales
        total_clientes = Cliente.objects.count()
        total_productos = Producto.objects.count()
        total_pedidos = Pedido.objects.count()
        pedidos_hoy = Pedido.objects.filter(
            fecha_pedido__date=timezone.now().date()
        ).count()
        
        # Productos más vendidos
        productos_mas_vendidos = DetallePedido.objects.values(
            'id_producto__nombre'
        ).annotate(
            total_vendido=Sum('cantidad')
        ).order_by('-total_vendido')[:5]
        
        # Clientes más activos
        clientes_mas_activos = Cliente.objects.annotate(
            num_pedidos=Count('pedidos')
        ).order_by('-num_pedidos')[:5]
        
        extra_context.update({
            'total_clientes': total_clientes,
            'total_productos': total_productos,
            'total_pedidos': total_pedidos,
            'pedidos_hoy': pedidos_hoy,
            'productos_mas_vendidos': productos_mas_vendidos,
            'clientes_mas_activos': clientes_mas_activos,
            'stats': stats,
        })
        
        return super().index(request, extra_context)

# Crear instancia del sitio admin personalizado
custom_admin_site = CustomAdminSite()

# Registrar los modelos en el sitio personalizado
custom_admin_site.register(Cliente, ClienteAdmin)
custom_admin_site.register(Producto, ProductoAdmin)
custom_admin_site.register(Pedido, PedidoAdmin)
custom_admin_site.register(DetallePedido, DetallePedidoAdmin)

# Reemplazar el sitio admin por defecto
admin.site = custom_admin_site
