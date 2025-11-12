"""
API Client para conectarse al backend en AWS
==============================================
Cliente HTTP que consume los endpoints de analytics del backend FastAPI.
"""

import requests
from typing import List, Dict, Optional, Any
from datetime import datetime
import streamlit as st


class AnalyticsAPI:
    """Cliente para consumir los endpoints de analytics del backend."""
    
    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        """
        Inicializa el cliente API.
        
        Args:
            base_url: URL base del API (ej: http://3.19.208.242:8000/v1)
            auth_token: Token de autenticación opcional
        """
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.session = requests.Session()
        
        if auth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {auth_token}'
            })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """
        Realiza una petición GET al API.
        
        Args:
            endpoint: Ruta del endpoint (ej: /analytics/bq/1_1)
            params: Parámetros de query
            
        Returns:
            Respuesta JSON del API
            
        Raises:
            Exception: Si hay error en la petición
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise Exception("⏱️ Timeout: El servidor tardó demasiado en responder")
        except requests.exceptions.ConnectionError:
            raise Exception("🔌 Error de conexión: No se pudo conectar al servidor")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("🔒 No autorizado: Token de autenticación inválido")
            elif e.response.status_code == 404:
                raise Exception("❌ Endpoint no encontrado")
            elif e.response.status_code == 500:
                raise Exception("🔥 Error interno del servidor")
            else:
                raise Exception(f"❌ Error HTTP {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise Exception(f"❌ Error inesperado: {str(e)}")
    
    def _format_datetime(self, dt: datetime) -> str:
        """Formatea datetime a ISO 8601 para el API."""
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # ========================================================================
    # BQ 1.x - Listings & Escrow Analytics
    # ========================================================================
    
    def get_listings_per_day_by_category(
        self, 
        start: datetime, 
        end: datetime
    ) -> List[Dict]:
        """
        BQ 1.1: Listings creados por día y categoría.
        
        Returns:
            Lista de dicts con keys: day, category_id, count
        """
        params = {
            'start': self._format_datetime(start),
            'end': self._format_datetime(end)
        }
        return self._make_request('/analytics/bq/1_1', params)
    
    def get_escrow_cancel_rate(
        self, 
        start: datetime, 
        end: datetime
    ) -> List[Dict]:
        """
        BQ 1.2: Tasa de cancelación de escrow por step.
        
        Returns:
            Lista de dicts con keys: step, total, cancelled, pct_cancelled
        """
        params = {
            'start': self._format_datetime(start),
            'end': self._format_datetime(end)
        }
        return self._make_request('/analytics/bq/1_2', params)
    
    # ========================================================================
    # BQ 2.x - User Behavior Analytics
    # ========================================================================
    
    def get_events_per_type_by_day(
        self, 
        start: datetime, 
        end: datetime
    ) -> List[Dict]:
        """
        BQ 2.1: Eventos por tipo por día.
        
        Returns:
            Lista de dicts con keys: day, event_type, count
        """
        params = {
            'start': self._format_datetime(start),
            'end': self._format_datetime(end)
        }
        return self._make_request('/analytics/bq/2_1', params)
    
    def get_clicks_by_button_by_day(
        self, 
        start: datetime, 
        end: datetime
    ) -> List[Dict]:
        """
        BQ 2.2: Clicks por botón por día.
        
        Returns:
            Lista de dicts con keys: day, button, count
        """
        params = {
            'start': self._format_datetime(start),
            'end': self._format_datetime(end)
        }
        return self._make_request('/analytics/bq/2_2', params)
    
    def get_time_by_screen(
        self, 
        start: datetime, 
        end: datetime,
        max_idle_sec: int = 300
    ) -> List[Dict]:
        """
        BQ 2.4: Tiempo invertido por pantalla.
        
        Args:
            max_idle_sec: Máximo tiempo de idle en segundos (default: 300)
        
        Returns:
            Lista de dicts con keys: screen, total_seconds, views, avg_seconds
        """
        params = {
            'start': self._format_datetime(start),
            'end': self._format_datetime(end),
            'max_idle_sec': max_idle_sec
        }
        return self._make_request('/analytics/bq/2_4', params)
    
    # ========================================================================
    # BQ 3.x - User Engagement Metrics
    # ========================================================================
    
    def get_daily_active_users(
        self, 
        start: datetime, 
        end: datetime
    ) -> List[Dict]:
        """
        BQ 3.1: Daily Active Users (DAU).
        
        Returns:
            Lista de dicts con keys: day, dau
        """
        params = {
            'start': self._format_datetime(start),
            'end': self._format_datetime(end)
        }
        return self._make_request('/analytics/bq/3_1', params)
    
    def get_sessions_by_day(
        self, 
        start: datetime, 
        end: datetime
    ) -> List[Dict]:
        """
        BQ 3.2: Sesiones por día.
        
        Returns:
            Lista de dicts con keys: day, sessions
        """
        params = {
            'start': self._format_datetime(start),
            'end': self._format_datetime(end)
        }
        return self._make_request('/analytics/bq/3_2', params)
    
    # ========================================================================
    # BQ 4.x - Revenue & Orders Analytics
    # ========================================================================
    
    def get_orders_by_status_by_day(
        self, 
        start: datetime, 
        end: datetime
    ) -> List[Dict]:
        """
        BQ 4.1: Órdenes por estado por día.
        
        Returns:
            Lista de dicts con keys: day, status, count
        """
        params = {
            'start': self._format_datetime(start),
            'end': self._format_datetime(end)
        }
        return self._make_request('/analytics/bq/4_1', params)
    
    def get_gmv_by_day(
        self, 
        start: datetime, 
        end: datetime
    ) -> List[Dict]:
        """
        BQ 4.2: Gross Merchandise Value (GMV) por día.
        
        Returns:
            Lista de dicts con keys: day, gmv_cents, orders_paid
        """
        params = {
            'start': self._format_datetime(start),
            'end': self._format_datetime(end)
        }
        return self._make_request('/analytics/bq/4_2', params)
    
    # ========================================================================
    # BQ 5.x - Feature Usage Analytics
    # ========================================================================
    
    def get_quick_view_by_category(
        self, 
        start: datetime, 
        end: datetime
    ) -> List[Dict]:
        """
        BQ 5.1: Uso de quick view por categoría por día.
        
        Returns:
            Lista de dicts con keys: day, category_id, count
        """
        params = {
            'start': self._format_datetime(start),
            'end': self._format_datetime(end)
        }
        return self._make_request('/analytics/bq/5_1', params)
    
    # ========================================================================
    # Catalogs
    # ========================================================================
    
    def get_categories(self) -> List[Dict]:
        """
        Obtiene el catálogo de categorías.
        
        Returns:
            Lista de dicts con keys: id, name, ...
        """
        return self._make_request('/categories')


# ============================================================================
# Cache singleton para reutilizar la instancia del cliente
# ============================================================================

@st.cache_resource
def get_api_client(base_url: str, auth_token: Optional[str] = None) -> AnalyticsAPI:
    """
    Obtiene una instancia singleton del cliente API con cache.
    
    Args:
        base_url: URL base del API
        auth_token: Token de autenticación opcional
        
    Returns:
        Instancia de AnalyticsAPI
    """
    return AnalyticsAPI(base_url, auth_token)
