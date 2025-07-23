from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Cliente, Producto, Pedido, DetallePedido


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['id_cliente', 'nombre', 'email', 'telefono', 'fecha_registro', 'total_pedidos', 'total_gastado']
    list_filter = ['fecha_registro']
    search_fields = ['nombre', 'email', 'telefono']
    readonly_fields = ['id_cliente', 'fecha_registro', 'total_pedidos', 'total_gastado']
    ordering = ['-fecha_registro']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'email', 'telefono')
        }),
        ('Información del Sistema', {
            'fields': ('id_cliente', 'fecha_registro'),
            'classes': ('collapse',)
        }),
        ('Estadísticas', {
            'fields': ('total_pedidos', 'total_gastado'),
            'classes': ('collapse',)
        }),
    )
    
    def total_pedidos(self, obj):
        return obj.total_pedidos
    total_pedidos.short_description = 'Total Pedidos'
    
    def total_gastado(self, obj):
        return f"${obj.total_gastado:,.2f}"
    total_gastado.short_description = 'Total Gastado'


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    readonly_fields = ['subtotal']
    fields = ['id_producto', 'cantidad', 'precio_unitario', 'subtotal']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id_pedido', 'cliente_link', 'fecha_pedido', 'total', 'estado', 'metodo_pago']
    list_filter = ['estado', 'fecha_pedido', 'metodo_pago']
    search_fields = ['id_cliente__nombre', 'id_cliente__email']
    readonly_fields = ['id_pedido', 'fecha_pedido', 'total']
    ordering = ['-fecha_pedido']
    inlines = [DetallePedidoInline]
    
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
    
    def total(self, obj):
        return f"${obj.total:,.2f}"
    total.short_description = 'Total'


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['id_producto', 'nombre', 'precio', 'stock', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['id_producto', 'fecha_creacion']
    ordering = ['nombre']
    
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


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ['id_detalle', 'pedido_link', 'producto_link', 'cantidad', 'precio_unitario', 'subtotal']
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
admin.site.site_header = "Administración del Sistema Híbrido"
admin.site.site_title = "Sistema Híbrido PostgreSQL + MongoDB"
admin.site.index_title = "Panel de Administración"
