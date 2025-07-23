#!/usr/bin/env python
"""
Script de prueba para verificar la integración entre PostgreSQL y MongoDB
"""

import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'client_sync.settings')
django.setup()

from ecommerce.models import Cliente, Producto, Pedido, DetallePedido
from ecommerce.integration_service import ClienteIntegrationService, PedidoIntegrationService, EstadisticasService
from ecommerce.mongodb_services import cliente_info_service


def test_postgresql_data():
    """Prueba los datos en PostgreSQL"""
    print("=" * 60)
    print("PRUEBA DE DATOS EN POSTGRESQL")
    print("=" * 60)
    
    # Contar registros
    total_clientes = Cliente.objects.count()
    total_productos = Producto.objects.count()
    total_pedidos = Pedido.objects.count()
    total_detalles = DetallePedido.objects.count()
    
    print(f"Total de clientes: {total_clientes}")
    print(f"Total de productos: {total_productos}")
    print(f"Total de pedidos: {total_pedidos}")
    print(f"Total de detalles de pedido: {total_detalles}")
    
    # Mostrar algunos clientes
    print("\nClientes registrados:")
    for cliente in Cliente.objects.all()[:3]:
        print(f"  - {cliente.nombre} ({cliente.email}) - Total gastado: ${cliente.total_gastado:,.2f}")
    
    # Mostrar algunos productos
    print("\nProductos disponibles:")
    for producto in Producto.objects.all()[:3]:
        print(f"  - {producto.nombre} - ${producto.precio:,.2f} - Stock: {producto.stock}")
    
    # Mostrar algunos pedidos
    print("\nPedidos realizados:")
    for pedido in Pedido.objects.select_related('id_cliente').all()[:3]:
        print(f"  - Pedido #{pedido.id_pedido} - {pedido.id_cliente.nombre} - ${pedido.total:,.2f}")


def test_mongodb_data():
    """Prueba los datos en MongoDB"""
    print("\n" + "=" * 60)
    print("PRUEBA DE DATOS EN MONGODB")
    print("=" * 60)
    
    # Obtener estadísticas de MongoDB
    stats = cliente_info_service.obtener_estadisticas()
    print(f"Total de clientes con información en MongoDB: {stats['total_clientes']}")
    print(f"Total de comentarios: {stats['total_comentarios']}")
    print(f"Promedio de comentarios por cliente: {stats['promedio_comentarios']:.2f}")
    
    # Mostrar información de algunos clientes
    print("\nInformación de clientes en MongoDB:")
    for cliente in Cliente.objects.all()[:3]:
        info_mongo = cliente_info_service.obtener_info_completa(cliente.id_cliente)
        if info_mongo:
            comentarios = info_mongo.get('comentarios', [])
            preferencias = info_mongo.get('preferencias', {})
            print(f"  - Cliente {cliente.id_cliente} ({cliente.nombre}):")
            print(f"    Preferencias: {preferencias}")
            print(f"    Comentarios: {len(comentarios)} comentarios")
            if comentarios:
                print(f"    Último comentario: {comentarios[-1]['texto'][:50]}...")


def test_integration():
    """Prueba la integración entre ambas bases de datos"""
    print("\n" + "=" * 60)
    print("PRUEBA DE INTEGRACIÓN")
    print("=" * 60)
    
    # Obtener cliente completo
    cliente_completo = ClienteIntegrationService.obtener_cliente_completo(1)
    if cliente_completo:
        print("Cliente completo (PostgreSQL + MongoDB):")
        print(f"  ID: {cliente_completo['id_cliente']}")
        print(f"  Nombre: {cliente_completo['nombre']}")
        print(f"  Email: {cliente_completo['email']}")
        print(f"  Total pedidos: {cliente_completo['total_pedidos']}")
        print(f"  Total gastado: ${cliente_completo['total_gastado']:,.2f}")
        print(f"  Preferencias: {cliente_completo['preferencias']}")
        print(f"  Comentarios: {len(cliente_completo['comentarios'])} comentarios")
    
    # Obtener pedido completo
    pedido_completo = PedidoIntegrationService.obtener_pedido_completo(1)
    if pedido_completo:
        print("\nPedido completo:")
        print(f"  ID: {pedido_completo['id_pedido']}")
        print(f"  Cliente: {pedido_completo['cliente']['nombre']}")
        print(f"  Total: ${pedido_completo['total']:,.2f}")
        print(f"  Estado: {pedido_completo['estado']}")
        print(f"  Detalles: {len(pedido_completo['detalles'])} productos")
        for detalle in pedido_completo['detalles']:
            print(f"    - {detalle['producto']['nombre']} x{detalle['cantidad']} = ${detalle['subtotal']:,.2f}")


def test_statistics():
    """Prueba las estadísticas del sistema"""
    print("\n" + "=" * 60)
    print("ESTADÍSTICAS DEL SISTEMA")
    print("=" * 60)
    
    stats = EstadisticasService.obtener_estadisticas_generales()
    
    print("Estadísticas de PostgreSQL:")
    pg_stats = stats.get('postgresql', {})
    print(f"  Total clientes: {pg_stats.get('total_clientes', 0)}")
    print(f"  Total pedidos: {pg_stats.get('total_pedidos', 0)}")
    print(f"  Total productos: {pg_stats.get('total_productos', 0)}")
    print(f"  Total ventas: ${pg_stats.get('total_ventas', 0):,.2f}")
    print(f"  Promedio venta: ${pg_stats.get('promedio_venta', 0):,.2f}")
    
    print("\nEstadísticas de MongoDB:")
    mongo_stats = stats.get('mongodb', {})
    print(f"  Total clientes con info: {mongo_stats.get('total_clientes', 0)}")
    print(f"  Total comentarios: {mongo_stats.get('total_comentarios', 0)}")
    print(f"  Promedio comentarios: {mongo_stats.get('promedio_comentarios', 0):.2f}")
    
    print("\nEstadísticas de Integración:")
    int_stats = stats.get('integracion', {})
    print(f"  Clientes con info completa: {int_stats.get('clientes_con_info_completa', 0)}")
    print(f"  Porcentaje cobertura: {int_stats.get('porcentaje_cobertura', 0):.1f}%")


def test_new_operations():
    """Prueba operaciones adicionales"""
    print("\n" + "=" * 60)
    print("PRUEBA DE OPERACIONES ADICIONALES")
    print("=" * 60)
    
    # Agregar un nuevo comentario
    print("Agregando nuevo comentario para cliente 1...")
    success = cliente_info_service.agregar_comentario(1, "Este es un comentario de prueba agregado dinámicamente")
    print(f"Comentario agregado: {'Sí' if success else 'No'}")
    
    # Actualizar preferencias
    print("Actualizando preferencias para cliente 2...")
    nuevas_preferencias = {
        'idioma': 'EN',
        'metodo_pago': 'PayPal',
        'notificaciones': True
    }
    success = cliente_info_service.actualizar_preferencias(2, nuevas_preferencias)
    print(f"Preferencias actualizadas: {'Sí' if success else 'No'}")
    
    # Verificar cambios
    cliente_actualizado = ClienteIntegrationService.obtener_cliente_completo(2)
    if cliente_actualizado:
        print(f"Preferencias actualizadas: {cliente_actualizado['preferencias']}")


def main():
    """Función principal"""
    print("INICIANDO PRUEBAS DEL SISTEMA HÍBRIDO POSTGRESQL + MONGODB")
    print("=" * 80)
    
    try:
        test_postgresql_data()
        test_mongodb_data()
        test_integration()
        test_statistics()
        test_new_operations()
        
        print("\n" + "=" * 80)
        print("TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nError durante las pruebas: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 