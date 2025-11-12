# Analytics Dashboard

Dashboard web para visualización de métricas de negocio (Business Queries) del backend marketplace.

## 📋 Descripción

Este dashboard consume los endpoints de analytics del backend FastAPI desplegado en AWS y presenta visualizaciones interactivas de las siguientes métricas:

### 📦 BQ 1.x - Listings & Escrow
- Listings creados por día y categoría
- Tasa de cancelación de escrow por step

### 👥 BQ 2.x - Comportamiento de Usuario
- Eventos por tipo por día
- Clicks por botón
- Tiempo invertido por pantalla

### 🔥 BQ 3.x - Engagement
- Daily Active Users (DAU)
- Sesiones por día

### 💰 BQ 4.x - Revenue & Órdenes
- Órdenes por estado
- GMV (Gross Merchandise Value) por día

### ⚡ BQ 5.x - Features
- Uso de quick view por categoría

## 🚀 Instalación

### Prerrequisitos

- Python 3.8+
- pip

### Pasos

1. **Clonar el repositorio** (o navegar a la carpeta):

```bash
cd analytics-dashboard
```

2. **Crear entorno virtual** (recomendado):

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**:

```bash
python -m pip install streamlit plotly pandas requests python-dotenv pytz
```

4. **Configurar variables de entorno**:

Edita el archivo `.env` con la URL de tu backend:

```env
API_BASE_URL=http://3.19.208.242:8000/v1
```

## 🎯 Uso

### Ejecutar el dashboard

**Opción 1: Doble click en `run.bat`** (más fácil)

**Opción 2: Línea de comandos**
```bash
python -m streamlit run dashboard.py
```

El dashboard se abrirá automáticamente en tu navegador en `http://localhost:8501`.

### Navegación

Usa el menú lateral para navegar entre las diferentes secciones:

- **🏠 Inicio**: Vista general y bienvenida
- **📦 Listings & Escrow**: Métricas de listings y escrow
- **👥 Comportamiento**: Analytics de comportamiento de usuario
- **🔥 Engagement**: DAU y sesiones
- **💰 Revenue**: GMV y órdenes
- **⚡ Features**: Uso de features específicas

### Filtros

Cada página incluye filtros de fecha con presets comunes:
- Últimos 7 días
- Últimos 30 días
- Últimos 90 días
- Este mes
- Mes anterior
- Personalizado

## 📁 Estructura del Proyecto

```
analytics-dashboard/
├── dashboard.py              # Punto de entrada principal
├── requirements.txt          # Dependencias Python
├── .env                      # Variables de entorno
├── README.md                # Este archivo
├── components/              # Componentes reutilizables
│   ├── charts.py           # Gráficos (Plotly)
│   ├── filters.py          # Filtros de fecha, categoría, etc.
│   └── metrics.py          # Tarjetas de métricas y KPIs
├── pages/                   # Páginas del dashboard
│   ├── revenue.py          # BQ 4.x - Revenue
│   └── engagement.py       # BQ 3.x - Engagement
├── services/               # Servicios externos
│   └── api_client.py      # Cliente HTTP para el backend
└── utils/                  # Utilidades
    └── config.py          # Configuración centralizada
```

## 🔧 Configuración Avanzada

### Cambiar URL del Backend

Edita `.env`:

```env
API_BASE_URL=http://tu-servidor:8000/v1
```

### Autenticación

Si el backend requiere autenticación, agrega el token en `.env`:

```env
AUTH_TOKEN=tu_token_jwt_aqui
```

### Personalizar Colores

Edita `utils/config.py`:

```python
COLORS = {
    "primary": "#3b82f6",
    "success": "#10b981",
    # ...
}
```

## 🐛 Troubleshooting

### Error de conexión

```
🔌 Error de conexión: No se pudo conectar al servidor
```

**Solución**: Verifica que:
1. El backend esté corriendo
2. La URL en `.env` sea correcta
3. Tu firewall permita la conexión

### No hay datos

```
⚠️ No hay datos disponibles para el período seleccionado
```

**Solución**: 
1. Verifica que haya datos en el backend para ese rango de fechas
2. Prueba con un rango de fechas más amplio
3. Verifica que los usuarios de la app móvil estén generando eventos

## 📊 Tecnologías

- **Streamlit**: Framework web para Python
- **Plotly**: Gráficos interactivos
- **Pandas**: Manipulación de datos
- **Requests**: Cliente HTTP
- **Python-dotenv**: Manejo de variables de entorno

## 🚀 Despliegue

### Streamlit Cloud (Gratuito)

1. Sube el código a GitHub
2. Visita [streamlit.io/cloud](https://streamlit.io/cloud)
3. Conecta tu repo y despliega
4. Configura las variables de entorno en los settings

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t analytics-dashboard .
docker run -p 8501:8501 analytics-dashboard
```

## 📝 Licencia

Este proyecto es parte del curso de Desarrollo de Aplicaciones Móviles.

## 👥 Autores

Team 26 - ISIS3510-202520
