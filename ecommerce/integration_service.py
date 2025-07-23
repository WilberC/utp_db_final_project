"""
Servicio de integración entre PostgreSQL y MongoDB
Combina datos estructurados y no estructurados para ofrecer una vista completa
"""

from typing import Dict, List, Optional, Any
from django.db import transaction, models
from .models import Cliente, Pedido, Producto, DetallePedido
from .mongodb_services import cliente_info_service
import logging

logger = logging.getLogger(__name__)


class ClienteIntegrationService:
    """
    Servicio para integrar datos de clientes entre PostgreSQL y MongoDB
    """
    
    @staticmethod
    def crear_cliente_completo(
        nombre: str,
        email: str,
        telefono: str,
        preferencias: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Crea un cliente completo con datos en PostgreSQL y MongoDB
        
        Args:
            nombre: Nombre del cliente
            email: Email del cliente
            telefono: Teléfono del cliente
            preferencias: Preferencias iniciales (opcional)
            
        Returns:
            Dict: Información completa del cliente o None si hay error
        """
        try:
            with transaction.atomic():
                # Crear cliente en PostgreSQL
                cliente = Cliente.objects.create(
                    nombre=nombre,
                    email=email,
                    telefono=telefono
                )
                
                # Crear documento en MongoDB
                if preferencias:
                    cliente_info_service.actualizar_preferencias(
                        cliente.id_cliente, 
                        preferencias
                    )
                else:
                    cliente_info_service.crear_documento_cliente(cliente.id_cliente)
                
                # Obtener información completa
                return ClienteIntegrationService.obtener_cliente_completo(cliente.id_cliente)
                
        except Exception as e:
            logger.error(f"Error al crear cliente completo: {e}")
            return None
    
    @staticmethod
    def obtener_cliente_completo(id_cliente: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene información completa de un cliente desde ambas bases de datos
        
        Args:
            id_cliente: ID del cliente
            
        Returns:
            Dict: Información completa del cliente o None si no existe
        """
        try:
            # Obtener datos de PostgreSQL
            cliente = Cliente.objects.filter(id_cliente=id_cliente).first()
            if not cliente:
                return None
            
            # Obtener datos de MongoDB
            info_mongo = cliente_info_service.obtener_info_completa(id_cliente)
            
            # Combinar información
            cliente_data = {
                "id_cliente": cliente.id_cliente,
                "nombre": cliente.nombre,
                "email": cliente.email,
                "telefono": cliente.telefono,
                "fecha_registro": cliente.fecha_registro,
                "total_pedidos": cliente.total_pedidos,
                "total_gastado": float(cliente.total_gastado),
                "comentarios": info_mongo.get("comentarios", []) if info_mongo else [],
                "preferencias": info_mongo.get("preferencias", {}) if info_mongo else {},
                "ultima_actualizacion_mongo": info_mongo.get("ultima_actualizacion") if info_mongo else None
            }
            
            return cliente_data
            
        except Exception as e:
            logger.error(f"Error al obtener cliente completo {id_cliente}: {e}")
            return None
    
    @staticmethod
    def obtener_todos_clientes_completos() -> List[Dict[str, Any]]:
        """
        Obtiene información completa de todos los clientes
        
        Returns:
            List[Dict]: Lista con información completa de todos los clientes
        """
        try:
            clientes = Cliente.objects.all()
            clientes_completos = []
            
            for cliente in clientes:
                cliente_completo = ClienteIntegrationService.obtener_cliente_completo(cliente.id_cliente)
                if cliente_completo:
                    clientes_completos.append(cliente_completo)
            
            return clientes_completos
            
        except Exception as e:
            logger.error(f"Error al obtener todos los clientes completos: {e}")
            return []
    
    @staticmethod
    def actualizar_cliente_completo(
        id_cliente: int,
        datos_postgres: Optional[Dict[str, Any]] = None,
        comentario: Optional[str] = None,
        preferencias: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Actualiza información del cliente en ambas bases de datos
        
        Args:
            id_cliente: ID del cliente
            datos_postgres: Datos a actualizar en PostgreSQL
            comentario: Comentario a agregar en MongoDB
            preferencias: Preferencias a actualizar en MongoDB
            
        Returns:
            bool: True si se actualizó exitosamente, False en caso contrario
        """
        try:
            with transaction.atomic():
                # Actualizar datos en PostgreSQL
                if datos_postgres:
                    Cliente.objects.filter(id_cliente=id_cliente).update(**datos_postgres)
                
                # Actualizar datos en MongoDB
                if comentario:
                    cliente_info_service.agregar_comentario(id_cliente, comentario)
                
                if preferencias:
                    cliente_info_service.actualizar_preferencias(id_cliente, preferencias)
                
                return True
                
        except Exception as e:
            logger.error(f"Error al actualizar cliente completo {id_cliente}: {e}")
            return False
    
    @staticmethod
    def eliminar_cliente_completo(id_cliente: int) -> bool:
        """
        Elimina un cliente de ambas bases de datos
        
        Args:
            id_cliente: ID del cliente
            
        Returns:
            bool: True si se eliminó exitosamente, False en caso contrario
        """
        try:
            with transaction.atomic():
                # Eliminar de MongoDB primero
                cliente_info_service.eliminar_cliente(id_cliente)
                
                # Eliminar de PostgreSQL
                cliente = Cliente.objects.filter(id_cliente=id_cliente).first()
                if cliente:
                    cliente.delete()
                
                return True
                
        except Exception as e:
            logger.error(f"Error al eliminar cliente completo {id_cliente}: {e}")
            return False


class PedidoIntegrationService:
    """
    Servicio para integrar datos de pedidos con información de clientes
    """
    
    @staticmethod
    def crear_pedido_completo(
        id_cliente: int,
        productos: List[Dict[str, Any]],
        direccion_envio: str,
        metodo_pago: str
    ) -> Optional[Dict[str, Any]]:
        """
        Crea un pedido completo con todos sus detalles
        
        Args:
            id_cliente: ID del cliente
            productos: Lista de productos con cantidad
            direccion_envio: Dirección de envío
            metodo_pago: Método de pago
            
        Returns:
            Dict: Información completa del pedido o None si hay error
        """
        try:
            with transaction.atomic():
                # Crear pedido
                pedido = Pedido.objects.create(
                    id_cliente_id=id_cliente,
                    direccion_envio=direccion_envio,
                    metodo_pago=metodo_pago
                )
                
                # Crear detalles del pedido
                for producto_data in productos:
                    producto = Producto.objects.get(id_producto=producto_data['id_producto'])
                    DetallePedido.objects.create(
                        id_pedido=pedido,
                        id_producto=producto,
                        cantidad=producto_data['cantidad']
                    )
                
                # Recalcular total
                pedido.calcular_total()
                
                # Actualizar preferencias de método de pago en MongoDB
                cliente_info_service.actualizar_preferencias(
                    id_cliente,
                    {"metodo_pago": metodo_pago}
                )
                
                return PedidoIntegrationService.obtener_pedido_completo(pedido.id_pedido)
                
        except Exception as e:
            logger.error(f"Error al crear pedido completo: {e}")
            return None
    
    @staticmethod
    def obtener_pedido_completo(id_pedido: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene información completa de un pedido
        
        Args:
            id_pedido: ID del pedido
            
        Returns:
            Dict: Información completa del pedido o None si no existe
        """
        try:
            pedido = Pedido.objects.select_related('id_cliente').prefetch_related('detalles__id_producto').get(id_pedido=id_pedido)
            
            # Obtener información del cliente desde MongoDB
            info_cliente = cliente_info_service.obtener_info_completa(pedido.id_cliente.id_cliente)
            
            pedido_data = {
                "id_pedido": pedido.id_pedido,
                "cliente": {
                    "id_cliente": pedido.id_cliente.id_cliente,
                    "nombre": pedido.id_cliente.nombre,
                    "email": pedido.id_cliente.email,
                    "preferencias": info_cliente.get("preferencias", {}) if info_cliente else {}
                },
                "fecha_pedido": pedido.fecha_pedido,
                "total": float(pedido.total),
                "estado": pedido.estado,
                "direccion_envio": pedido.direccion_envio,
                "metodo_pago": pedido.metodo_pago,
                "detalles": [
                    {
                        "id_detalle": detalle.id_detalle,
                        "producto": {
                            "id_producto": detalle.id_producto.id_producto,
                            "nombre": detalle.id_producto.nombre,
                            "precio": float(detalle.id_producto.precio)
                        },
                        "cantidad": detalle.cantidad,
                        "precio_unitario": float(detalle.precio_unitario),
                        "subtotal": float(detalle.subtotal)
                    }
                    for detalle in pedido.detalles.all()
                ]
            }
            
            return pedido_data
            
        except Pedido.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error al obtener pedido completo {id_pedido}: {e}")
            return None
    
    @staticmethod
    def obtener_pedidos_cliente(id_cliente: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los pedidos de un cliente con información completa
        
        Args:
            id_cliente: ID del cliente
            
        Returns:
            List[Dict]: Lista de pedidos completos del cliente
        """
        try:
            pedidos = Pedido.objects.filter(id_cliente_id=id_cliente).order_by('-fecha_pedido')
            pedidos_completos = []
            
            for pedido in pedidos:
                pedido_completo = PedidoIntegrationService.obtener_pedido_completo(pedido.id_pedido)
                if pedido_completo:
                    pedidos_completos.append(pedido_completo)
            
            return pedidos_completos
            
        except Exception as e:
            logger.error(f"Error al obtener pedidos del cliente {id_cliente}: {e}")
            return []


class EstadisticasService:
    """
    Servicio para obtener estadísticas combinadas de ambas bases de datos
    """
    
    @staticmethod
    def obtener_estadisticas_generales() -> Dict[str, Any]:
        """
        Obtiene estadísticas generales del sistema
        
        Returns:
            Dict: Estadísticas generales
        """
        try:
            # Estadísticas de PostgreSQL
            total_clientes = Cliente.objects.count()
            total_pedidos = Pedido.objects.count()
            total_productos = Producto.objects.count()
            total_ventas = Pedido.objects.aggregate(
                total=models.Sum('total')
            )['total'] or 0
            
            # Estadísticas de MongoDB
            stats_mongo = cliente_info_service.obtener_estadisticas()
            
            return {
                "postgresql": {
                    "total_clientes": total_clientes,
                    "total_pedidos": total_pedidos,
                    "total_productos": total_productos,
                    "total_ventas": float(total_ventas),
                    "promedio_venta": float(total_ventas / total_pedidos) if total_pedidos > 0 else 0
                },
                "mongodb": stats_mongo,
                "integracion": {
                    "clientes_con_info_completa": stats_mongo["total_clientes"],
                    "porcentaje_cobertura": (stats_mongo["total_clientes"] / total_clientes * 100) if total_clientes > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas generales: {e}")
            return {} 