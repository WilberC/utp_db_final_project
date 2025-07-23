"""
Servicios para manejar datos no estructurados en MongoDB
Incluye operaciones para comentarios y preferencias de clientes
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from client_sync.mongodb import get_mongodb_collection
import logging

logger = logging.getLogger(__name__)


class ClienteInfoService:
    """
    Servicio para manejar información no estructurada de clientes en MongoDB
    """
    
    def __init__(self):
        self.collection = get_mongodb_collection('clientes_info')
    
    def crear_documento_cliente(self, id_cliente: int) -> bool:
        """
        Crea un documento inicial para un cliente en MongoDB
        
        Args:
            id_cliente: ID del cliente en PostgreSQL
            
        Returns:
            bool: True si se creó exitosamente, False en caso contrario
        """
        try:
            documento = {
                "id_cliente": id_cliente,
                "comentarios": [],
                "preferencias": {
                    "idioma": "ES",
                    "metodo_pago": "Tarjeta de crédito",
                    "notificaciones": True
                },
                "fecha_creacion": datetime.utcnow(),
                "ultima_actualizacion": datetime.utcnow()
            }
            
            result = self.collection.insert_one(documento)
            logger.info(f"Documento creado para cliente {id_cliente} con ID: {result.inserted_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error al crear documento para cliente {id_cliente}: {e}")
            return False
    
    def agregar_comentario(self, id_cliente: int, texto: str) -> bool:
        """
        Agrega un comentario al cliente
        
        Args:
            id_cliente: ID del cliente en PostgreSQL
            texto: Texto del comentario
            
        Returns:
            bool: True si se agregó exitosamente, False en caso contrario
        """
        try:
            comentario = {
                "texto": texto,
                "fecha": datetime.utcnow()
            }
            
            result = self.collection.update_one(
                {"id_cliente": id_cliente},
                {
                    "$push": {"comentarios": comentario},
                    "$set": {"ultima_actualizacion": datetime.utcnow()}
                }
            )
            
            if result.matched_count == 0:
                # Si no existe el documento, lo creamos
                return self.crear_documento_cliente(id_cliente)
            
            logger.info(f"Comentario agregado para cliente {id_cliente}")
            return True
            
        except Exception as e:
            logger.error(f"Error al agregar comentario para cliente {id_cliente}: {e}")
            return False
    
    def obtener_comentarios(self, id_cliente: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los comentarios de un cliente
        
        Args:
            id_cliente: ID del cliente en PostgreSQL
            
        Returns:
            List[Dict]: Lista de comentarios
        """
        try:
            documento = self.collection.find_one({"id_cliente": id_cliente})
            if documento:
                return documento.get("comentarios", [])
            return []
            
        except Exception as e:
            logger.error(f"Error al obtener comentarios para cliente {id_cliente}: {e}")
            return []
    
    def actualizar_preferencias(self, id_cliente: int, preferencias: Dict[str, Any]) -> bool:
        """
        Actualiza las preferencias de un cliente
        
        Args:
            id_cliente: ID del cliente en PostgreSQL
            preferencias: Diccionario con las nuevas preferencias
            
        Returns:
            bool: True si se actualizó exitosamente, False en caso contrario
        """
        try:
            # Validar estructura de preferencias
            preferencias_validas = {
                "idioma": preferencias.get("idioma", "ES"),
                "metodo_pago": preferencias.get("metodo_pago", "Tarjeta de crédito"),
                "notificaciones": preferencias.get("notificaciones", True)
            }
            
            result = self.collection.update_one(
                {"id_cliente": id_cliente},
                {
                    "$set": {
                        "preferencias": preferencias_validas,
                        "ultima_actualizacion": datetime.utcnow()
                    }
                }
            )
            
            if result.matched_count == 0:
                # Si no existe el documento, lo creamos
                return self.crear_documento_cliente(id_cliente)
            
            logger.info(f"Preferencias actualizadas para cliente {id_cliente}")
            return True
            
        except Exception as e:
            logger.error(f"Error al actualizar preferencias para cliente {id_cliente}: {e}")
            return False
    
    def obtener_preferencias(self, id_cliente: int) -> Dict[str, Any]:
        """
        Obtiene las preferencias de un cliente
        
        Args:
            id_cliente: ID del cliente en PostgreSQL
            
        Returns:
            Dict: Preferencias del cliente
        """
        try:
            documento = self.collection.find_one({"id_cliente": id_cliente})
            if documento:
                return documento.get("preferencias", {})
            return {}
            
        except Exception as e:
            logger.error(f"Error al obtener preferencias para cliente {id_cliente}: {e}")
            return {}
    
    def obtener_info_completa(self, id_cliente: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene toda la información no estructurada de un cliente
        
        Args:
            id_cliente: ID del cliente en PostgreSQL
            
        Returns:
            Dict: Información completa del cliente o None si no existe
        """
        try:
            documento = self.collection.find_one({"id_cliente": id_cliente})
            return documento
            
        except Exception as e:
            logger.error(f"Error al obtener información completa para cliente {id_cliente}: {e}")
            return None
    
    def eliminar_cliente(self, id_cliente: int) -> bool:
        """
        Elimina toda la información no estructurada de un cliente
        
        Args:
            id_cliente: ID del cliente en PostgreSQL
            
        Returns:
            bool: True si se eliminó exitosamente, False en caso contrario
        """
        try:
            result = self.collection.delete_one({"id_cliente": id_cliente})
            if result.deleted_count > 0:
                logger.info(f"Información eliminada para cliente {id_cliente}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error al eliminar información para cliente {id_cliente}: {e}")
            return False
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de la colección
        
        Returns:
            Dict: Estadísticas de la colección
        """
        try:
            total_clientes = self.collection.count_documents({})
            total_comentarios = self.collection.aggregate([
                {"$unwind": "$comentarios"},
                {"$count": "total"}
            ]).next().get("total", 0) if total_clientes > 0 else 0
            
            return {
                "total_clientes": total_clientes,
                "total_comentarios": total_comentarios,
                "promedio_comentarios": total_comentarios / total_clientes if total_clientes > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            return {
                "total_clientes": 0,
                "total_comentarios": 0,
                "promedio_comentarios": 0
            }


# Instancia global del servicio
cliente_info_service = ClienteInfoService() 