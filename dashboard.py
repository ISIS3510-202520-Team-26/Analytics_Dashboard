"""
Analytics Dashboard - Página Principal
=========================================
Dashboard para visualización de métricas de negocio (BQ).
Este es el punto de entrada principal de la aplicación.
"""

import streamlit as st
from datetime import datetime, timedelta
from utils.auth import get_or_create_token, is_authenticated, clear_token
from utils.config import API_BASE_URL

# Configuración de la página
st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Dashboard de Analytics para Marketplace"
    }
)

# ============================================================================
# AUTENTICACIÓN AUTOMÁTICA
# ============================================================================
# Intentar obtener o crear token automáticamente al cargar el dashboard
token = get_or_create_token(API_BASE_URL)

# Estilos personalizados
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    h1 {
        color: #1f2937;
        padding-bottom: 1rem;
    }
    h2 {
        color: #374151;
        padding-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar para navegación
st.sidebar.title("📊 Analytics Dashboard")

# Mostrar estado de autenticación
if is_authenticated():
    st.sidebar.success(f"✅ Autenticado como: {st.session_state.get('auth_email', 'Usuario')}")
    if st.sidebar.button("🚪 Cerrar Sesión"):
        clear_token()
        st.rerun()
else:
    st.sidebar.error("❌ No autenticado")
    st.error("No se pudo autenticar. Verifica la conexión con el backend.")
    st.stop()

st.sidebar.markdown("---")

# Navegación
page = st.sidebar.radio(
    "Navegación",
    [
        "🏠 Inicio",
        "🎯 UX Tuning (Flutter)",
        "📦 Listings & Escrow (BQ 1.x)",
        "👥 Comportamiento de Usuario (BQ 2.x)",
        "🔥 Engagement (BQ 3.x)",
        "💰 Revenue & Órdenes (BQ 4.x)",
        "🔄 Conversion Funnel (BQ 4.3)",
        "⚡ Features (BQ 5.x)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Backend:** AWS\n\n"
    "**API:** `http://3.19.208.242:8000/v1`"
)

# Página de inicio
if page == "🏠 Inicio":
    st.title("📊 Analytics Dashboard")
    st.markdown("### Bienvenido al Dashboard de Analytics")
    
    st.markdown("""
    Este dashboard te permite visualizar métricas clave del negocio agrupadas en 6 categorías:
    
    #### 🎯 **UX Tuning (Flutter)**
    - Análisis de búsquedas vs filtros (auto-open logic)
    - Categorías más usadas (recommendations)
    - Prioridad de CTAs basada en eventos
    - Métricas específicas para `UxTuningService`
    
    #### 📦 **BQ 1.x - Listings & Escrow**
    - Listings creados por día y categoría
    - Tasa de cancelación de escrow por step
    
    #### 👥 **BQ 2.x - Comportamiento de Usuario**
    - Eventos por tipo por día
    - Clicks por botón
    - Tiempo invertido por pantalla
    
    #### 🔥 **BQ 3.x - Engagement**
    - Daily Active Users (DAU)
    - Sesiones por día
    
    #### 💰 **BQ 4.x - Revenue & Órdenes**
    - Órdenes por estado
    - GMV (Gross Merchandise Value) por día
    
    #### 🔄 **BQ 4.3 - Conversion Funnel (NUEVO)**
    - Análisis del funnel de conversión de órdenes
    - Tasas de conversión entre estados
    - Identificación de cuellos de botella
    - Análisis temporal de conversiones
    
    #### ⚡ **BQ 5.x - Features**
    - Uso de quick view por categoría
    """)
    
    # Métricas rápidas de ejemplo
    st.markdown("---")
    st.markdown("### 📈 Vista Rápida")
    
    # Cargar datos reales para la vista rápida
    from services.api_client import get_api_client
    from datetime import datetime, timedelta
    
    api = get_api_client(API_BASE_URL, token)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    try:
        # Obtener DAU
        dau_data = api.get_daily_active_users(start_date, end_date)
        total_dau = sum(d['dau'] for d in dau_data) if dau_data else 0
        
        # Obtener eventos
        events_data = api.get_events_per_type_by_day(start_date, end_date)
        total_events = sum(e['count'] for e in events_data) if events_data else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="👥 DAU (Últimos 7 días)",
                value=f"{total_dau:,}",
                help="Total de usuarios activos únicos"
            )
        
        with col2:
            st.metric(
                label="📊 Eventos Totales",
                value=f"{total_events:,}",
                help="Total de eventos registrados"
            )
        
        with col3:
            unique_types = len(set(e['event_type'] for e in events_data if e.get('event_type')))
            st.metric(
                label="🎯 Tipos de Eventos",
                value=f"{unique_types}",
                help="Tipos únicos de eventos"
            )
        
        with col4:
            avg_events_per_user = (total_events / total_dau) if total_dau > 0 else 0
            st.metric(
                label="⚡ Eventos/Usuario",
                value=f"{avg_events_per_user:.1f}",
                help="Promedio de eventos por usuario"
            )
    
    except Exception as e:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Estado", value="—", delta="Error al cargar")
    
    st.markdown("---")
    
    # Estado de disponibilidad de datos
    st.markdown("### 🔍 Estado de Datos Disponibles")
    
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Verificar disponibilidad de cada BQ
        status_col1, status_col2 = st.columns(2)
        
        with status_col1:
            st.markdown("#### ✅ Datos Disponibles")
            
            # BQ 3.1 - DAU
            dau_data = api.get_daily_active_users(start_date, end_date)
            if dau_data:
                st.success(f"✓ **BQ 3.1** - DAU: {len(dau_data)} días")
            
            # BQ 2.1 - Eventos
            events_data = api.get_events_per_type_by_day(start_date, end_date)
            if events_data:
                st.success(f"✓ **BQ 2.1** - Eventos: {sum(e['count'] for e in events_data):,} eventos")
            
            # BQ 3.2 - Sesiones
            sessions_data = api.get_sessions_by_day(start_date, end_date)
            if sessions_data:
                st.success(f"✓ **BQ 3.2** - Sesiones: {sum(s['sessions'] for s in sessions_data):,} sesiones")
        
        with status_col2:
            st.markdown("#### ⚠️ Datos Faltantes")
            
            # BQ 2.2 - Clicks
            clicks_data = api.get_clicks_by_button_by_day(start_date, end_date)
            if not clicks_data:
                st.warning("⚠ **BQ 2.2** - Clicks: No hay eventos `category.clicked`")
            
            # BQ 2.4 - Tiempo en pantallas
            time_data = api.get_time_by_screen(start_date, end_date)
            if not time_data:
                st.warning("⚠ **BQ 2.4** - Tiempo: No hay eventos `screen.view`")
            
            st.info("""
            💡 **Tip:** Para generar estos datos, la app móvil debe llamar:
            - `trackClick()` para clicks
            - `trackScreenView()` para tiempo en pantallas
            """)
    
    except Exception as e:
        st.error(f"Error verificando disponibilidad: {str(e)}")
    
    st.markdown("---")
    st.info("👈 Selecciona una categoría en el menú lateral para comenzar")

elif page == "🎯 UX Tuning (Flutter)":
    from pages.ux_tuning import render_ux_tuning_page
    render_ux_tuning_page()

elif page == "📦 Listings & Escrow (BQ 1.x)":
    from pages.listings import render_listings_page
    render_listings_page()

elif page == "👥 Comportamiento de Usuario (BQ 2.x)":
    from pages.behavior import render_behavior_page
    render_behavior_page()

elif page == "🔥 Engagement (BQ 3.x)":
    from pages.engagement import render_engagement_page
    render_engagement_page()

elif page == "💰 Revenue & Órdenes (BQ 4.x)":
    from pages.revenue import render_revenue_page
    render_revenue_page()

elif page == "🔄 Conversion Funnel (BQ 4.3)":
    from pages.conversion_funnel import render_conversion_funnel_page
    render_conversion_funnel_page()

elif page == "⚡ Features (BQ 5.x)":
    from pages.features import render_features_page
    render_features_page()

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("v1.0.0 | Noviembre 2025")
