"""
Servicio para gestionar preferencias de usuario.
"""
from typing import Dict, Optional, List
from datetime import datetime
import json
from src.config import settings
from supabase import create_client
from src.monitoring.logger import Logger
from src.monitoring.metrics import preferences_metrics

logger = Logger(__name__)

class PreferencesService:
    """Servicio para gestionar preferencias de usuario."""
    
    def __init__(self):
        """Inicializar servicio de preferencias."""
        self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.default_preferences = {
            "viewer": {
                "theme": "system",
                "fontSize": 16,
                "zoom": 1.0,
                "showMinimap": True,
                "showLineNumbers": True,
                "wordWrap": True
            },
            "thumbnails": {
                "viewMode": "grid",
                "size": "medium",
                "showLabels": True
            },
            "annotations": {
                "defaultColor": "#FFD700",
                "defaultType": "highlight",
                "autoShow": True
            },
            "collaboration": {
                "showCursors": True,
                "showPresence": True,
                "notificationsEnabled": True
            },
            "keyboard": {
                "shortcuts": {
                    "save": "mod+s",
                    "find": "mod+f",
                    "zoom_in": "mod+plus",
                    "zoom_out": "mod+minus"
                },
                "enabledFeatures": [
                    "shortcuts",
                    "gestures",
                    "touch"
                ]
            },
            "sync": {
                "frequency": 30000,  # 30 segundos
                "autoSave": True,
                "offlineMode": "conservative"
            }
        }
        
    async def get_preferences(self, user_id: str) -> Dict:
        """Obtener preferencias de un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Preferencias del usuario
        """
        try:
            with preferences_metrics.measure_latency("get_preferences"):
                # Obtener de Supabase
                result = self.supabase.table('user_preferences') \
                    .select('preferences') \
                    .eq('user_id', user_id) \
                    .single() \
                    .execute()
                
                if result.data:
                    return result.data['preferences']
                
                # Si no existe, crear con valores por defecto
                await self.set_preferences(user_id, self.default_preferences)
                return self.default_preferences
                
        except Exception as e:
            logger.error(f"Error getting preferences: {str(e)}")
            raise

    async def set_preferences(self, user_id: str, preferences: Dict) -> Dict:
        """Establecer preferencias de usuario.
        
        Args:
            user_id: ID del usuario
            preferences: Nuevas preferencias
            
        Returns:
            Preferencias actualizadas
        """
        try:
            with preferences_metrics.measure_latency("set_preferences"):
                # Validar preferencias
                validated = self._validate_preferences(preferences)
                
                # Guardar en Supabase
                result = self.supabase.table('user_preferences') \
                    .upsert({
                        'user_id': user_id,
                        'preferences': validated,
                        'updated_at': datetime.utcnow().isoformat()
                    }) \
                    .execute()
                
                return result.data[0]['preferences']
                
        except Exception as e:
            logger.error(f"Error setting preferences: {str(e)}")
            raise

    async def sync_preferences(
        self,
        user_id: str,
        request: Dict,
        device_id: str
    ) -> Dict:
        """Sincronizar preferencias con resolución de conflictos.
        
        Args:
            user_id: ID del usuario
            request: Request de sincronización
            device_id: ID del dispositivo
            
        Returns:
            Resultado de sincronización
        """
        try:
            with preferences_metrics.measure_latency("sync_preferences"):
                # Obtener preferencias actuales
                current = await self.get_preferences(user_id)
                
                # Detectar conflictos
                conflicts = self._detect_conflicts(
                    current,
                    request['preferences'],
                    request['lastSyncTimestamp']
                )
                
                if not conflicts:
                    # Sin conflictos, actualizar directamente
                    merged = self._merge_preferences(
                        current,
                        request['preferences']
                    )
                    await self.set_preferences(user_id, merged)
                    
                    return {
                        'preferences': merged,
                        'conflicts': [],
                        'syncTimestamp': datetime.utcnow().isoformat()
                    }
                
                # Resolver conflictos
                resolved = await self._resolve_conflicts(
                    current,
                    request['preferences'],
                    conflicts
                )
                
                return {
                    'preferences': resolved['preferences'],
                    'conflicts': resolved['conflicts'],
                    'syncTimestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error syncing preferences: {str(e)}")
            raise

    def _validate_preferences(self, preferences: Dict) -> Dict:
        """Validar y sanitizar preferencias."""
        validated = {}
        
        # Viewer
        viewer = preferences.get('viewer', {})
        validated['viewer'] = {
            'theme': self._validate_enum(
                viewer.get('theme'),
                ['light', 'dark', 'system'],
                'system'
            ),
            'fontSize': self._validate_range(
                viewer.get('fontSize'), 12, 24, 16
            ),
            'zoom': self._validate_range(
                viewer.get('zoom'), 0.5, 2.0, 1.0
            ),
            'showMinimap': bool(viewer.get('showMinimap', True)),
            'showLineNumbers': bool(viewer.get('showLineNumbers', True)),
            'wordWrap': bool(viewer.get('wordWrap', True))
        }
        
        # Thumbnails
        thumbnails = preferences.get('thumbnails', {})
        validated['thumbnails'] = {
            'viewMode': self._validate_enum(
                thumbnails.get('viewMode'),
                ['grid', 'list'],
                'grid'
            ),
            'size': self._validate_enum(
                thumbnails.get('size'),
                ['small', 'medium', 'large'],
                'medium'
            ),
            'showLabels': bool(thumbnails.get('showLabels', True))
        }
        
        # Annotations
        annotations = preferences.get('annotations', {})
        validated['annotations'] = {
            'defaultColor': self._validate_color(
                annotations.get('defaultColor'),
                '#FFD700'
            ),
            'defaultType': self._validate_enum(
                annotations.get('defaultType'),
                ['highlight', 'comment', 'drawing'],
                'highlight'
            ),
            'autoShow': bool(annotations.get('autoShow', True))
        }
        
        # Collaboration
        collab = preferences.get('collaboration', {})
        validated['collaboration'] = {
            'showCursors': bool(collab.get('showCursors', True)),
            'showPresence': bool(collab.get('showPresence', True)),
            'notificationsEnabled': bool(collab.get('notificationsEnabled', True))
        }
        
        # Keyboard
        keyboard = preferences.get('keyboard', {})
        validated['keyboard'] = {
            'shortcuts': self._validate_shortcuts(
                keyboard.get('shortcuts', {})
            ),
            'enabledFeatures': self._validate_features(
                keyboard.get('enabledFeatures', [])
            )
        }
        
        # Sync
        sync = preferences.get('sync', {})
        validated['sync'] = {
            'frequency': self._validate_range(
                sync.get('frequency'),
                5000,  # min 5s
                300000,  # max 5min
                30000
            ),
            'autoSave': bool(sync.get('autoSave', True)),
            'offlineMode': self._validate_enum(
                sync.get('offlineMode'),
                ['aggressive', 'conservative'],
                'conservative'
            )
        }
        
        return validated

    def _detect_conflicts(
        self,
        current: Dict,
        new: Dict,
        last_sync: str
    ) -> List[Dict]:
        """Detectar conflictos entre versiones de preferencias."""
        conflicts = []
        
        def compare_paths(current_val, new_val, path=[]):
            if isinstance(current_val, dict):
                for key in set(current_val.keys()) | set(new_val.keys()):
                    if key in current_val and key in new_val:
                        compare_paths(
                            current_val[key],
                            new_val[key],
                            path + [key]
                        )
            elif current_val != new_val:
                conflicts.append({
                    'path': path,
                    'serverValue': current_val,
                    'clientValue': new_val
                })
        
        compare_paths(current, new)
        return conflicts

    async def _resolve_conflicts(
        self,
        current: Dict,
        new: Dict,
        conflicts: List[Dict]
    ) -> Dict:
        """Resolver conflictos de preferencias."""
        resolved = current.copy()
        resolved_conflicts = []
        
        for conflict in conflicts:
            path = conflict['path']
            resolution = self._get_conflict_resolution(path)
            
            if resolution == 'server':
                # Mantener valor del servidor
                resolved_conflicts.append({
                    **conflict,
                    'resolution': 'server'
                })
            
            elif resolution == 'client':
                # Usar valor del cliente
                current_dict = resolved
                for key in path[:-1]:
                    current_dict = current_dict[key]
                current_dict[path[-1]] = conflict['clientValue']
                
                resolved_conflicts.append({
                    **conflict,
                    'resolution': 'client'
                })
            
            elif resolution == 'merge':
                # Intentar combinar valores
                merged = self._merge_values(
                    conflict['serverValue'],
                    conflict['clientValue']
                )
                
                current_dict = resolved
                for key in path[:-1]:
                    current_dict = current_dict[key]
                current_dict[path[-1]] = merged
                
                resolved_conflicts.append({
                    **conflict,
                    'resolution': 'merged',
                    'mergedValue': merged
                })
        
        return {
            'preferences': resolved,
            'conflicts': resolved_conflicts
        }

    def _get_conflict_resolution(self, path: List[str]) -> str:
        """Determinar estrategia de resolución para un path."""
        path_str = '.'.join(path)
        
        # Estrategias específicas por path
        if path_str.startswith('viewer'):
            return 'client'  # Preferencias de visualización son personales
        elif path_str.startswith('collaboration'):
            return 'server'  # Configuración de colaboración es global
        elif path_str.startswith('keyboard.shortcuts'):
            return 'merge'   # Combinar atajos personalizados
        
        return 'server'  # Por defecto, el servidor gana

    def _merge_values(self, server_value: any, client_value: any) -> any:
        """Combinar valores en conflicto."""
        if isinstance(server_value, dict) and isinstance(client_value, dict):
            return {**server_value, **client_value}
        elif isinstance(server_value, list) and isinstance(client_value, list):
            return list(set(server_value + client_value))
        
        return server_value  # Si no se puede combinar, usar valor del servidor

    # Funciones auxiliares de validación
    def _validate_enum(self, value: str, valid: List[str], default: str) -> str:
        return value if value in valid else default

    def _validate_range(
        self,
        value: float,
        min_val: float,
        max_val: float,
        default: float
    ) -> float:
        try:
            val = float(value)
            return max(min(val, max_val), min_val)
        except:
            return default

    def _validate_color(self, color: str, default: str) -> str:
        import re
        if re.match(r'^#[0-9A-Fa-f]{6}$', str(color)):
            return color
        return default

    def _validate_shortcuts(self, shortcuts: Dict) -> Dict:
        valid_mods = ['mod', 'shift', 'alt']
        valid_keys = set('abcdefghijklmnopqrstuvwxyz0123456789+-')
        
        validated = {}
        for action, combo in shortcuts.items():
            parts = combo.lower().split('+')
            if all(p in valid_mods or set(p) <= valid_keys for p in parts):
                validated[action] = combo
        
        return validated

    def _validate_features(self, features: List[str]) -> List[str]:
        valid_features = {'shortcuts', 'gestures', 'touch'}
        return list(set(features) & valid_features)
