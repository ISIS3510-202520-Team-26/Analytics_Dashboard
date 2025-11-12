"""
Configuración del Dashboard
============================
Variables de configuración centralizadas.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# URL del backend en AWS
API_BASE_URL = os.getenv(
    "API_BASE_URL", 
    "http://3.19.208.242:8000/v1"
)

# Token de autenticación (opcional)
AUTH_TOKEN = os.getenv("AUTH_TOKEN", None)

# Configuración de página
PAGE_TITLE = "Analytics Dashboard"
PAGE_ICON = "📊"
LAYOUT = "wide"

# Colores del tema
COLORS = {
    "primary": "#3b82f6",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "purple": "#8b5cf6"
}

# Configuración de gráficos
CHART_HEIGHT_DEFAULT = 400
CHART_HEIGHT_SMALL = 300
CHART_HEIGHT_LARGE = 500

# Días por defecto para filtros
DEFAULT_DAYS = 30

# Configuración de cache (en segundos)
CACHE_TTL = 300  # 5 minutos
