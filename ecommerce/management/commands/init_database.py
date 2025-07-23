"""
Comando de Django para inicializar la base de datos con datos de ejemplo
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from ecommerce.models import Cliente, Producto, Pedido, DetallePedido
from ecommerce.integration_service import ClienteIntegrationService, PedidoIntegrationService
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Inicializa la base de datos con datos de ejemplo para el sistema híbrido'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Elimina todos los datos existentes antes de crear los nuevos',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Iniciando inicialización de la base de datos...')
        )

        if options['clear']:
            self.stdout.write('Eliminando datos existentes...')
            self._clear_database()

        try:
            with transaction.atomic():
                self._create_sample_data()
                self.stdout.write(
                    self.style.SUCCESS('Base de datos inicializada exitosamente!')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al inicializar la base de datos: {e}')
            )
            logger.error(f'Error en init_database: {e}')
            raise

    def _clear_database(self):
        """Elimina todos los datos existentes"""
        DetallePedido.objects.all().delete()
        Pedido.objects.all().delete()
        Producto.objects.all().delete()
        Cliente.objects.all().delete()
        self.stdout.write('Datos existentes eliminados.')

    def _create_sample_data(self):
        """Crea datos de ejemplo"""
        self.stdout.write('Creando clientes de ejemplo...')
        clientes = self._create_clientes()
        
        self.stdout.write('Creando productos de ejemplo...')
        productos = self._create_productos()
        
        self.stdout.write('Creando pedidos de ejemplo...')
        self._create_pedidos(clientes, productos)
        
        self.stdout.write('Agregando comentarios y preferencias...')
        self._create_mongodb_data(clientes)

    def _create_clientes(self):
        """Crea clientes de ejemplo"""
        clientes_data = [
            {
                'nombre': 'Juan Pérez',
                'email': 'juan.perez@email.com',
                'telefono': '+57 300 123 4567',
                'preferencias': {
                    'idioma': 'ES',
                    'metodo_pago': 'Tarjeta de crédito',
                    'notificaciones': True
                }
            },
            {
                'nombre': 'María García',
                'email': 'maria.garcia@email.com',
                'telefono': '+57 310 987 6543',
                'preferencias': {
                    'idioma': 'ES',
                    'metodo_pago': 'Transferencia bancaria',
                    'notificaciones': False
                }
            },
            {
                'nombre': 'Carlos Rodríguez',
                'email': 'carlos.rodriguez@email.com',
                'telefono': '+57 315 555 1234',
                'preferencias': {
                    'idioma': 'EN',
                    'metodo_pago': 'PayPal',
                    'notificaciones': True
                }
            },
            {
                'nombre': 'Ana López',
                'email': 'ana.lopez@email.com',
                'telefono': '+57 320 777 8888',
                'preferencias': {
                    'idioma': 'ES',
                    'metodo_pago': 'Efectivo',
                    'notificaciones': True
                }
            },
            {
                'nombre': 'Luis Martínez',
                'email': 'luis.martinez@email.com',
                'telefono': '+57 305 444 9999',
                'preferencias': {
                    'idioma': 'ES',
                    'metodo_pago': 'Tarjeta de débito',
                    'notificaciones': False
                }
            }
        ]

        clientes = []
        for cliente_data in clientes_data:
            cliente_completo = ClienteIntegrationService.crear_cliente_completo(
                nombre=cliente_data['nombre'],
                email=cliente_data['email'],
                telefono=cliente_data['telefono'],
                preferencias=cliente_data['preferencias']
            )
            if cliente_completo:
                clientes.append(cliente_completo)
                self.stdout.write(f'  - Cliente creado: {cliente_data["nombre"]}')

        return clientes

    def _create_productos(self):
        """Crea productos de ejemplo"""
        productos_data = [
            {
                'nombre': 'Laptop HP Pavilion',
                'precio': Decimal('899.99'),
                'descripcion': 'Laptop de 15.6 pulgadas con procesador Intel i5, 8GB RAM, 256GB SSD',
                'stock': 15
            },
            {
                'nombre': 'Smartphone Samsung Galaxy',
                'precio': Decimal('599.99'),
                'descripcion': 'Smartphone Android con pantalla de 6.1 pulgadas, 128GB almacenamiento',
                'stock': 25
            },
            {
                'nombre': 'Auriculares Bluetooth Sony',
                'precio': Decimal('89.99'),
                'descripcion': 'Auriculares inalámbricos con cancelación de ruido activa',
                'stock': 50
            },
            {
                'nombre': 'Tablet Apple iPad',
                'precio': Decimal('399.99'),
                'descripcion': 'Tablet de 10.2 pulgadas con procesador A13 Bionic, 64GB',
                'stock': 20
            },
            {
                'nombre': 'Monitor LG 24"',
                'precio': Decimal('199.99'),
                'descripcion': 'Monitor LED de 24 pulgadas con resolución Full HD',
                'stock': 30
            },
            {
                'nombre': 'Teclado Mecánico Logitech',
                'precio': Decimal('129.99'),
                'descripcion': 'Teclado mecánico con switches Cherry MX Brown',
                'stock': 40
            },
            {
                'nombre': 'Mouse Gaming Razer',
                'precio': Decimal('79.99'),
                'descripcion': 'Mouse gaming con sensor óptico de 16,000 DPI',
                'stock': 35
            },
            {
                'nombre': 'Cámara Web Logitech C920',
                'precio': Decimal('69.99'),
                'descripcion': 'Cámara web HD 1080p con micrófono integrado',
                'stock': 45
            }
        ]

        productos = []
        for producto_data in productos_data:
            producto = Producto.objects.create(**producto_data)
            productos.append(producto)
            self.stdout.write(f'  - Producto creado: {producto_data["nombre"]}')

        return productos

    def _create_pedidos(self, clientes, productos):
        """Crea pedidos de ejemplo"""
        pedidos_data = [
            {
                'cliente_id': 1,
                'productos': [
                    {'id_producto': 1, 'cantidad': 1},
                    {'id_producto': 3, 'cantidad': 2}
                ],
                'direccion_envio': 'Calle 123 #45-67, Bogotá, Colombia',
                'metodo_pago': 'Tarjeta de crédito'
            },
            {
                'cliente_id': 2,
                'productos': [
                    {'id_producto': 2, 'cantidad': 1},
                    {'id_producto': 4, 'cantidad': 1}
                ],
                'direccion_envio': 'Avenida 78 #90-12, Medellín, Colombia',
                'metodo_pago': 'Transferencia bancaria'
            },
            {
                'cliente_id': 3,
                'productos': [
                    {'id_producto': 5, 'cantidad': 2},
                    {'id_producto': 6, 'cantidad': 1},
                    {'id_producto': 7, 'cantidad': 1}
                ],
                'direccion_envio': 'Carrera 15 #23-45, Cali, Colombia',
                'metodo_pago': 'PayPal'
            },
            {
                'cliente_id': 4,
                'productos': [
                    {'id_producto': 8, 'cantidad': 1}
                ],
                'direccion_envio': 'Calle 56 #78-90, Barranquilla, Colombia',
                'metodo_pago': 'Efectivo'
            },
            {
                'cliente_id': 5,
                'productos': [
                    {'id_producto': 1, 'cantidad': 1},
                    {'id_producto': 5, 'cantidad': 1},
                    {'id_producto': 8, 'cantidad': 1}
                ],
                'direccion_envio': 'Avenida 34 #56-78, Cartagena, Colombia',
                'metodo_pago': 'Tarjeta de débito'
            }
        ]

        for pedido_data in pedidos_data:
            pedido_completo = PedidoIntegrationService.crear_pedido_completo(
                id_cliente=pedido_data['cliente_id'],
                productos=pedido_data['productos'],
                direccion_envio=pedido_data['direccion_envio'],
                metodo_pago=pedido_data['metodo_pago']
            )
            if pedido_completo:
                self.stdout.write(f'  - Pedido creado: #{pedido_completo["id_pedido"]}')

    def _create_mongodb_data(self, clientes):
        """Crea datos adicionales en MongoDB"""
        comentarios_data = [
            {
                'cliente_id': 1,
                'comentarios': [
                    'Excelente servicio de entrega, muy rápido',
                    'Los productos llegaron en perfecto estado',
                    'Me gustaría ver más opciones de pago'
                ]
            },
            {
                'cliente_id': 2,
                'comentarios': [
                    'Buena calidad de productos',
                    'El envío fue un poco lento pero llegó bien'
                ]
            },
            {
                'cliente_id': 3,
                'comentarios': [
                    'Muy satisfecho con mi compra',
                    'Recomendaría esta tienda a mis amigos',
                    'Excelente atención al cliente'
                ]
            },
            {
                'cliente_id': 4,
                'comentarios': [
                    'Productos de buena calidad',
                    'Precios competitivos'
                ]
            },
            {
                'cliente_id': 5,
                'comentarios': [
                    'Entrega rápida y eficiente',
                    'Me gustaría más variedad de productos'
                ]
            }
        ]

        from ecommerce.mongodb_services import cliente_info_service

        for comentario_data in comentarios_data:
            for comentario in comentario_data['comentarios']:
                cliente_info_service.agregar_comentario(
                    comentario_data['cliente_id'], 
                    comentario
                )
            self.stdout.write(f'  - Comentarios agregados para cliente {comentario_data["cliente_id"]}') 