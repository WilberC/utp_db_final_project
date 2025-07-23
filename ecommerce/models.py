from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Cliente(models.Model):
    """
    Modelo para la tabla 'clientes' en PostgreSQL
    Almacena información estructurada de los clientes
    """
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200, verbose_name="Nombre completo")
    email = models.EmailField(unique=True, verbose_name="Correo electrónico")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    
    class Meta:
        db_table = 'clientes'
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"{self.nombre} ({self.email})"
    
    @property
    def total_pedidos(self):
        """Retorna el total de pedidos del cliente"""
        return self.pedidos.count()
    
    @property
    def total_gastado(self):
        """Retorna el total gastado por el cliente"""
        return self.pedidos.aggregate(
            total=models.Sum('total')
        )['total'] or Decimal('0.00')


class Producto(models.Model):
    """
    Modelo para la tabla 'productos' en PostgreSQL
    Almacena información de productos
    """
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200, verbose_name="Nombre del producto")
    precio = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Precio"
    )
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock disponible")
    activo = models.BooleanField(default=True, verbose_name="Producto activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    
    class Meta:
        db_table = 'productos'
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio}"


class Pedido(models.Model):
    """
    Modelo para la tabla 'pedidos' en PostgreSQL
    Almacena información de pedidos
    """
    ESTADOS_PEDIDO = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('en_proceso', 'En Proceso'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    id_pedido = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE, 
        related_name='pedidos',
        verbose_name="Cliente"
    )
    fecha_pedido = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del pedido")
    total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Total del pedido"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_PEDIDO,
        default='pendiente',
        verbose_name="Estado del pedido"
    )
    direccion_envio = models.TextField(verbose_name="Dirección de envío")
    metodo_pago = models.CharField(max_length=50, verbose_name="Método de pago")
    
    class Meta:
        db_table = 'pedidos'
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_pedido']
    
    def __str__(self):
        return f"Pedido #{self.id_pedido} - {self.id_cliente.nombre}"
    
    def calcular_total(self):
        """Calcula el total del pedido basado en los detalles"""
        total = self.detalles.aggregate(
            total=models.Sum('subtotal')
        )['total'] or Decimal('0.00')
        self.total = total
        self.save()
        return total


class DetallePedido(models.Model):
    """
    Modelo para la tabla 'detalle_pedido' en PostgreSQL
    Almacena los detalles de cada pedido
    """
    id_detalle = models.AutoField(primary_key=True)
    id_pedido = models.ForeignKey(
        Pedido, 
        on_delete=models.CASCADE, 
        related_name='detalles',
        verbose_name="Pedido"
    )
    id_producto = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE,
        verbose_name="Producto"
    )
    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Cantidad"
    )
    precio_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Precio unitario"
    )
    subtotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Subtotal"
    )
    
    class Meta:
        db_table = 'detalle_pedido'
        verbose_name = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedidos"
        unique_together = ['id_pedido', 'id_producto']
    
    def __str__(self):
        return f"{self.cantidad}x {self.id_producto.nombre} - ${self.subtotal}"
    
    def save(self, *args, **kwargs):
        """Calcula automáticamente el subtotal antes de guardar"""
        if not self.precio_unitario:
            self.precio_unitario = self.id_producto.precio
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)
        
        # Recalcula el total del pedido
        self.id_pedido.calcular_total()
