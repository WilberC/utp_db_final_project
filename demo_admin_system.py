#!/usr/bin/env python3
"""
Script de demostración del Sistema de Administración Centralizada
E-commerce Híbrido PostgreSQL + MongoDB

Este script muestra cómo usar el sistema de administración para:
1. Crear clientes con datos en PostgreSQL y MongoDB
2. Gestionar productos y pedidos
3. Usar las funcionalidades integradas del admin
"""

import os
import sys
import django
from datetime import datetime
from django.db.models import Sum, Count

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'client_sync.settings')
django.setup()

from ecommerce.models import Cliente, Producto, Pedido, DetallePedido
from ecommerce.mongodb_services import ClienteInfoService
from ecommerce.integration_service import ClienteIntegrationService, PedidoIntegrationService


def print_header(title):
    """Imprime un encabezado formateado"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_section(title):
    """Imprime una sección formateada"""
    print(f"\n--- {title} ---")


def demo_crear_cliente_completo():
    """Demuestra la creación de un cliente completo"""
    print_section("Creando Cliente Completo (PostgreSQL + MongoDB)")
    
    # Crear cliente usando el servicio de integración
    cliente_data = ClienteIntegrationService.crear_cliente_completo(
        nombre="María González",
        email="maria.gonzalez@email.com",
        telefono="+34 612 345 678",
        preferencias={
            'idioma': 'ES',
            'metodo_pago': 'PayPal',
            'notificaciones': True
        }
    )
    
    if cliente_data:
        print(f"✅ Cliente creado exitosamente:")
        print(f"   ID: {cliente_data['id_cliente']}")
        print(f"   Nombre: {cliente_data['nombre']}")
        print(f"   Email: {cliente_data['email']}")
        print(f"   Preferencias: {cliente_data['preferencias']}")
        return cliente_data['id_cliente']
    else:
        print("❌ Error al crear cliente")
        return None


def demo_agregar_comentarios(cliente_id):
    """Demuestra cómo agregar comentarios a un cliente"""
    print_section("Agregando Comentarios al Cliente")
    
    service = ClienteInfoService()
    comentarios = [
        "Cliente muy satisfecho con el servicio",
        "Realizó su primera compra exitosamente",
        "Interesado en productos de tecnología"
    ]
    
    for comentario in comentarios:
        if service.agregar_comentario(cliente_id, comentario):
            print(f"✅ Comentario agregado: {comentario}")
        else:
            print(f"❌ Error al agregar comentario: {comentario}")


def demo_crear_productos():
    """Demuestra la creación de productos"""
    print_section("Creando Productos")
    
    productos_data = [
        {
            'nombre': 'Laptop Gaming Pro',
            'precio': 1299.99,
            'descripcion': 'Laptop de alto rendimiento para gaming',
            'stock': 15
        },
        {
            'nombre': 'Smartphone Galaxy S23',
            'precio': 899.99,
            'descripcion': 'Smartphone de última generación',
            'stock': 25
        },
        {
            'nombre': 'Auriculares Bluetooth Premium',
            'precio': 199.99,
            'descripcion': 'Auriculares inalámbricos de alta calidad',
            'stock': 50
        }
    ]
    
    productos_creados = []
    for data in productos_data:
        producto = Producto.objects.create(**data)
        productos_creados.append(producto)
        print(f"✅ Producto creado: {producto.nombre} - ${producto.precio}")
    
    return productos_creados


def demo_crear_pedido_completo(cliente_id, productos):
    """Demuestra la creación de un pedido completo"""
    print_section("Creando Pedido Completo")
    
    # Crear pedido usando el servicio de integración
    productos_pedido = [
        {
            'id_producto': productos[0].id_producto,
            'cantidad': 1
        },
        {
            'id_producto': productos[2].id_producto,
            'cantidad': 2
        }
    ]
    
    pedido_data = PedidoIntegrationService.crear_pedido_completo(
        id_cliente=cliente_id,
        productos=productos_pedido,
        direccion_envio="Calle Mayor 123, Madrid, España",
        metodo_pago="PayPal"
    )
    
    if pedido_data:
        print(f"✅ Pedido creado exitosamente:")
        print(f"   ID: {pedido_data['id_pedido']}")
        print(f"   Cliente: {pedido_data['cliente']['nombre']}")
        print(f"   Total: ${pedido_data['total']}")
        print(f"   Productos: {len(pedido_data['detalles'])}")
        return pedido_data['id_pedido']
    else:
        print("❌ Error al crear pedido")
        return None


def demo_consultas_integradas():
    """Demuestra consultas que integran ambas bases de datos"""
    print_section("Consultas Integradas (PostgreSQL + MongoDB)")
    
    # Obtener todos los clientes con información completa
    clientes_completos = ClienteIntegrationService.obtener_todos_clientes_completos()
    
    print(f"📊 Total de clientes con datos completos: {len(clientes_completos)}")
    
    for cliente in clientes_completos:
        print(f"\n👤 Cliente: {cliente['nombre']}")
        print(f"   📧 Email: {cliente['email']}")
        print(f"   🛒 Total pedidos: {cliente['total_pedidos']}")
        print(f"   💰 Total gastado: ${cliente['total_gastado']}")
        print(f"   💬 Comentarios: {len(cliente['comentarios'])}")
        print(f"   ⚙️ Preferencias: {cliente['preferencias']}")


def demo_estadisticas():
    """Demuestra las estadísticas del sistema"""
    print_section("Estadísticas del Sistema")
    
    # Estadísticas básicas
    total_clientes = Cliente.objects.count()
    total_productos = Producto.objects.count()
    total_pedidos = Pedido.objects.count()
    
    print(f"📈 Estadísticas Generales:")
    print(f"   👥 Total Clientes: {total_clientes}")
    print(f"   📦 Total Productos: {total_productos}")
    print(f"   🛒 Total Pedidos: {total_pedidos}")
    
    # Productos más vendidos
    productos_mas_vendidos = DetallePedido.objects.values(
        'id_producto__nombre'
    ).annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')[:3]
    
    print(f"\n🏆 Productos Más Vendidos:")
    for producto in productos_mas_vendidos:
        print(f"   📦 {producto['id_producto__nombre']}: {producto['total_vendido']} unidades")
    
    # Clientes más activos
    clientes_mas_activos = Cliente.objects.annotate(
        num_pedidos=Count('pedidos')
    ).order_by('-num_pedidos')[:3]
    
    print(f"\n👑 Clientes Más Activos:")
    for cliente in clientes_mas_activos:
        print(f"   👤 {cliente.nombre}: {cliente.num_pedidos} pedidos")


def demo_admin_features():
    """Demuestra las características del admin"""
    print_section("Características del Django Admin")
    
    print("🎛️ Funcionalidades Disponibles en el Admin:")
    print("   ✅ Dashboard personalizado con estadísticas")
    print("   ✅ Gestión integrada de PostgreSQL y MongoDB")
    print("   ✅ Acciones masivas para múltiples registros")
    print("   ✅ Vistas personalizadas para comentarios y preferencias")
    print("   ✅ Exportación de datos en formato JSON")
    print("   ✅ Enlaces cruzados entre entidades relacionadas")
    print("   ✅ Filtros y búsquedas avanzadas")
    print("   ✅ Validación automática de datos")
    
    print(f"\n🌐 Para acceder al admin:")
    print(f"   URL: http://localhost:8000/admin/")
    print(f"   Usuario: Tu superusuario existente")


def main():
    """Función principal de demostración"""
    print_header("DEMOSTRACIÓN DEL SISTEMA DE ADMINISTRACIÓN CENTRALIZADA")
    print("E-commerce Híbrido PostgreSQL + MongoDB")
    
    try:
        # 1. Crear cliente completo
        cliente_id = demo_crear_cliente_completo()
        
        if cliente_id:
            # 2. Agregar comentarios
            demo_agregar_comentarios(cliente_id)
            
            # 3. Crear productos
            productos = demo_crear_productos()
            
            # 4. Crear pedido
            if productos:
                demo_crear_pedido_completo(cliente_id, productos)
            
            # 5. Mostrar consultas integradas
            demo_consultas_integradas()
            
            # 6. Mostrar estadísticas
            demo_estadisticas()
            
            # 7. Mostrar características del admin
            demo_admin_features()
        
        print_header("DEMOSTRACIÓN COMPLETADA")
        print("🎉 El sistema está listo para usar!")
        print("📖 Revisa README_ADMIN_SISTEMA.md para más detalles")
        
    except Exception as e:
        print(f"❌ Error durante la demostración: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 