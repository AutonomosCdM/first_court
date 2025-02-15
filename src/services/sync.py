"""
Servicio de sincronización offline.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from src.config import settings
from src.monitoring.logger import Logger
from src.monitoring.metrics import sync_metrics

logger = Logger(__name__)

class SyncService:
    """Servicio para gestionar sincronización offline."""
    
    def __init__(self):
        """Inicializar servicio de sincronización."""
        self.priorities = {
            'CRITICAL': {
                'types': ['document', 'annotations'],
                'maxAge': 0,  # Inmediato
                'retryInterval': 1000,  # 1s
                'maxRetries': 5
            },
            'HIGH': {
                'types': ['thumbnails', 'preferences'],
                'maxAge': 5 * 60 * 1000,  # 5min
                'retryInterval': 5000,  # 5s
                'maxRetries': 3
            },
            'NORMAL': {
                'types': ['history', 'comments'],
                'maxAge': 30 * 60 * 1000,  # 30min
                'retryInterval': 30000,  # 30s
                'maxRetries': 2
            }
        }
        
        self.conflict_resolution = {
            'document': 'LAST_WRITE_WINS',
            'annotations': 'MERGE',
            'preferences': 'SERVER_WINS'
        }
        
    async def sync(
        self,
        operations: List[Dict],
        last_sync: str,
        device_id: str
    ) -> Dict:
        """Sincronizar operaciones pendientes.
        
        Args:
            operations: Lista de operaciones pendientes
            last_sync: Timestamp de última sincronización
            device_id: ID del dispositivo
            
        Returns:
            Resultado de sincronización
        """
        try:
            with sync_metrics.measure_latency("sync_operations"):
                # 1. Validar y ordenar operaciones por prioridad
                validated_ops = self._validate_operations(operations)
                sorted_ops = self._sort_by_priority(validated_ops)
                
                # 2. Procesar operaciones
                results = []
                conflicts = []
                
                for op in sorted_ops:
                    try:
                        # Verificar si la operación está dentro del tiempo máximo
                        if not self._is_operation_valid(op):
                            conflicts.append(self._create_conflict(
                                op,
                                None,
                                'EXPIRED',
                                None
                            ))
                            continue
                        
                        # Procesar operación
                        result = await self._process_operation(op)
                        
                        if result.get('conflict'):
                            conflicts.append(result['conflict'])
                        else:
                            results.append(result)
                            
                    except Exception as e:
                        logger.error(f"Error processing operation: {str(e)}")
                        conflicts.append(self._create_conflict(
                            op,
                            None,
                            'ERROR',
                            str(e)
                        ))
                
                return {
                    'success': len(conflicts) == 0,
                    'results': results,
                    'conflicts': conflicts,
                    'syncTimestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error in sync: {str(e)}")
            raise

    async def _process_operation(self, operation: Dict) -> Dict:
        """Procesar una operación individual."""
        try:
            # Obtener estado actual del servidor
            server_state = await self._get_server_state(
                operation['type'],
                operation.get('id')
            )
            
            # Verificar conflictos
            if self._has_conflict(operation, server_state):
                # Resolver según estrategia
                resolution = self._resolve_conflict(
                    operation,
                    server_state
                )
                
                if resolution['action'] == 'abort':
                    return {
                        'conflict': self._create_conflict(
                            operation,
                            server_state,
                            'CONFLICT',
                            None
                        )
                    }
                
                # Usar estado resuelto
                operation['data'] = resolution['data']
            
            # Ejecutar operación
            result = await self._execute_operation(operation)
            
            return {
                'operation': operation,
                'status': 'success',
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Error processing operation: {str(e)}")
            raise

    def _validate_operations(self, operations: List[Dict]) -> List[Dict]:
        """Validar operaciones pendientes."""
        validated = []
        
        for op in operations:
            # Validar campos requeridos
            if not all(k in op for k in [
                'type',
                'action',
                'data',
                'timestamp',
                'deviceId',
                'priority'
            ]):
                logger.warning(f"Invalid operation format: {op}")
                continue
                
            # Validar tipo
            valid_types = sum(
                [p['types'] for p in self.priorities.values()],
                []
            )
            if op['type'] not in valid_types:
                logger.warning(f"Invalid operation type: {op['type']}")
                continue
                
            # Validar acción
            if op['action'] not in ['create', 'update', 'delete']:
                logger.warning(f"Invalid operation action: {op['action']}")
                continue
                
            # Validar prioridad
            if op['priority'] not in self.priorities:
                logger.warning(f"Invalid operation priority: {op['priority']}")
                continue
                
            validated.append(op)
            
        return validated

    def _sort_by_priority(self, operations: List[Dict]) -> List[Dict]:
        """Ordenar operaciones por prioridad."""
        priority_order = {
            'CRITICAL': 0,
            'HIGH': 1,
            'NORMAL': 2
        }
        
        return sorted(
            operations,
            key=lambda x: (
                priority_order[x['priority']],
                x['timestamp']
            )
        )

    def _is_operation_valid(self, operation: Dict) -> bool:
        """Verificar si una operación está dentro del tiempo máximo."""
        priority = self.priorities[operation['priority']]
        
        if priority['maxAge'] == 0:
            return True
            
        op_time = datetime.fromisoformat(operation['timestamp'])
        max_age = timedelta(milliseconds=priority['maxAge'])
        
        return datetime.utcnow() - op_time <= max_age

    async def _get_server_state(
        self,
        type: str,
        id: Optional[str]
    ) -> Optional[Dict]:
        """Obtener estado actual del servidor."""
        if type == 'document':
            # TODO: Obtener estado del documento
            pass
        elif type == 'annotations':
            # TODO: Obtener estado de anotaciones
            pass
        elif type == 'preferences':
            # TODO: Obtener preferencias
            pass
        
        return None

    def _has_conflict(
        self,
        operation: Dict,
        server_state: Optional[Dict]
    ) -> bool:
        """Verificar si hay conflicto con el estado del servidor."""
        if not server_state:
            return False
            
        if operation['type'] == 'document':
            return self._check_document_conflict(operation, server_state)
        elif operation['type'] == 'annotations':
            return self._check_annotation_conflict(operation, server_state)
            
        return False

    def _resolve_conflict(
        self,
        operation: Dict,
        server_state: Dict
    ) -> Dict:
        """Resolver conflicto según estrategia configurada."""
        strategy = self.conflict_resolution[operation['type']]
        
        if strategy == 'LAST_WRITE_WINS':
            # Comparar timestamps
            op_time = datetime.fromisoformat(operation['timestamp'])
            server_time = datetime.fromisoformat(server_state['timestamp'])
            
            if op_time > server_time:
                return {
                    'action': 'continue',
                    'data': operation['data']
                }
            else:
                return {
                    'action': 'abort',
                    'data': None
                }
                
        elif strategy == 'MERGE':
            # Intentar combinar cambios
            merged = self._merge_states(
                operation['data'],
                server_state['data']
            )
            
            return {
                'action': 'continue',
                'data': merged
            }
            
        else:  # SERVER_WINS
            return {
                'action': 'abort',
                'data': None
            }

    async def _execute_operation(self, operation: Dict) -> Dict:
        """Ejecutar operación en el servidor."""
        if operation['type'] == 'document':
            # TODO: Ejecutar operación de documento
            pass
        elif operation['type'] == 'annotations':
            # TODO: Ejecutar operación de anotaciones
            pass
        elif operation['type'] == 'preferences':
            # TODO: Ejecutar operación de preferencias
            pass
            
        return {}

    def _create_conflict(
        self,
        operation: Dict,
        server_state: Optional[Dict],
        reason: str,
        details: Optional[str]
    ) -> Dict:
        """Crear objeto de conflicto."""
        return {
            'operation': operation,
            'serverState': server_state,
            'reason': reason,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }

    def _merge_states(self, client_state: Dict, server_state: Dict) -> Dict:
        """Combinar estados en conflicto."""
        if isinstance(client_state, dict) and isinstance(server_state, dict):
            merged = server_state.copy()
            
            for key, value in client_state.items():
                if key in merged:
                    merged[key] = self._merge_states(value, merged[key])
                else:
                    merged[key] = value
                    
            return merged
            
        elif isinstance(client_state, list) and isinstance(server_state, list):
            # Para listas, usar conjunto para eliminar duplicados
            return list(set(client_state + server_state))
            
        # Para valores simples, mantener el más reciente (cliente)
        return client_state
