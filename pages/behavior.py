"""
Página de Comportamiento de Usuario (BQ 2.x)
=============================================
Visualización de métricas de comportamiento de usuario.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from services.api_client import get_api_client
from components.filters import date_range_filter
from components.metrics import metric_row, format_number
from components.charts import line_chart, bar_chart, horizontal_bar_chart, stacked_bar_chart
from utils.config import API_BASE_URL


def render_behavior_page():
    """Renderiza la página de Comportamiento de Usuario."""
    
    st.title("👥 Comportamiento de Usuario")
    st.markdown("Análisis de eventos, clicks y tiempo en pantallas.")
    
    # Filtro de fechas
    start_date, end_date = date_range_filter(key="behavior", default_days=30)
    
    # Obtener cliente API
    api = get_api_client(API_BASE_URL)
    
    # Contenedor para loading
    with st.spinner("Cargando datos de comportamiento..."):
        try:
            # BQ 2.1 - Eventos por tipo
            events_data = api.get_events_per_type_by_day(start_date, end_date)
            df_events = pd.DataFrame(events_data)
            
            # BQ 2.2 - Clicks por botón
            clicks_data = api.get_clicks_by_button_by_day(start_date, end_date)
            df_clicks = pd.DataFrame(clicks_data)
            
            # BQ 2.4 - Tiempo por pantalla
            time_data = api.get_time_by_screen(start_date, end_date)
            df_time = pd.DataFrame(time_data)
            
            # Debug info
            st.sidebar.markdown("### 🔍 Debug Info")
            st.sidebar.text(f"Eventos: {len(df_events)} filas")
            st.sidebar.text(f"Clicks: {len(df_clicks)} filas")
            st.sidebar.text(f"Tiempo: {len(df_time)} filas")
            
        except Exception as e:
            st.error(f"❌ Error al cargar datos: {str(e)}")
            st.info("💡 Posibles causas:\n- Backend no está respondiendo\n- No hay datos para este período\n- Error de autenticación")
            return
    
    # ========================================================================
    # Sección: Eventos
    # ========================================================================
    
    st.markdown("## 📊 Eventos de Usuario")
    
    if not df_events.empty:
        # KPIs de eventos
        total_events = df_events['count'].sum()
        unique_event_types = df_events['event_type'].nunique()
        avg_events_per_day = df_events.groupby('day')['count'].sum().mean()
        
        metrics = [
            {
                "label": "🎯 Total Eventos",
                "value": format_number(total_events),
                "help": "Total de eventos registrados"
            },
            {
                "label": "📂 Tipos de Eventos",
                "value": format_number(unique_event_types),
                "help": "Tipos únicos de eventos"
            },
            {
                "label": "📈 Promedio Diario",
                "value": format_number(int(avg_events_per_day)),
                "help": "Eventos promedio por día"
            }
        ]
        
        metric_row(metrics)
        
        st.markdown("---")
        
        # Gráfico de tendencia
        st.markdown("### 📈 Eventos por Día")
        
        df_events_by_day = df_events.groupby('day')['count'].sum().reset_index()
        
        fig_events_trend = line_chart(
            df_events_by_day,
            x='day',
            y='count',
            title='Total de Eventos por Día',
            height=400
        )
        st.plotly_chart(fig_events_trend, use_container_width=True)
        
        # Gráfico por tipo de evento
        st.markdown("### 📂 Distribución por Tipo de Evento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de barras apiladas por día
            fig_stacked = stacked_bar_chart(
                df_events,
                x='day',
                y='count',
                color='event_type',
                title='Eventos por Tipo (apilados)',
                height=400
            )
            st.plotly_chart(fig_stacked, use_container_width=True)
        
        with col2:
            # Top eventos
            df_events_agg = df_events.groupby('event_type')['count'].sum().reset_index()
            df_events_agg = df_events_agg.sort_values('count', ascending=False).head(10)
            
            fig_top_events = horizontal_bar_chart(
                df_events_agg,
                x='count',
                y='event_type',
                title='Top 10 Tipos de Eventos',
                height=400
            )
            st.plotly_chart(fig_top_events, use_container_width=True)
        
        # Tabla detallada
        with st.expander("📊 Ver datos detallados de eventos"):
            st.dataframe(
                df_events.rename(columns={
                    'day': 'Día',
                    'event_type': 'Tipo de Evento',
                    'count': 'Cantidad'
                }),
                use_container_width=True
            )
    
    else:
        st.info("No hay datos de eventos para el período seleccionado.")
    
    st.markdown("---")
    
    # ========================================================================
    # Sección: Clicks (usando eventos existentes como proxy)
    # ========================================================================
    
    st.markdown("## 🖱️ Análisis de Interacciones")
    
    # Si no hay datos de BQ 2.2, usar eventos relacionados con clicks
    if df_clicks.empty and not df_events.empty:
        st.info("💡 Usando eventos de interacción como proxy para clicks")
        
        # Filtrar eventos que representan interacciones de usuario
        interaction_events = df_events[df_events['event_type'].isin([
            'search.filter.used',
            'category.clicked',
            'listing.viewed',
            'listing.created',
            'auth.login.success'
        ])].copy()
        
        if not interaction_events.empty:
            df_clicks = interaction_events.rename(columns={'event_type': 'button'})
    
    if not df_clicks.empty:
        # KPIs de clicks
        total_clicks = df_clicks['count'].sum()
        unique_buttons = df_clicks['button'].nunique()
        avg_clicks_per_day = df_clicks.groupby('day')['count'].sum().mean()
        
        metrics = [
            {
                "label": "🖱️ Total Clicks",
                "value": format_number(total_clicks),
                "help": "Total de clicks registrados"
            },
            {
                "label": "🔘 Botones Únicos",
                "value": format_number(unique_buttons),
                "help": "Botones únicos clickeados"
            },
            {
                "label": "📊 Promedio Diario",
                "value": format_number(int(avg_clicks_per_day)),
                "help": "Clicks promedio por día"
            }
        ]
        
        metric_row(metrics)
        
        st.markdown("---")
        
        # Top botones clickeados
        st.markdown("### 🔝 Botones Más Clickeados")
        
        df_clicks_agg = df_clicks.groupby('button')['count'].sum().reset_index()
        df_clicks_agg = df_clicks_agg.sort_values('count', ascending=False).head(15)
        
        fig_top_buttons = horizontal_bar_chart(
            df_clicks_agg,
            x='count',
            y='button',
            title='Top 15 Botones por Clicks',
            height=500
        )
        st.plotly_chart(fig_top_buttons, use_container_width=True)
        
        # Tabla detallada
        with st.expander("📊 Ver datos detallados de clicks"):
            st.dataframe(
                df_clicks.rename(columns={
                    'day': 'Día',
                    'button': 'Botón',
                    'count': 'Clicks'
                }),
                use_container_width=True
            )
    
    else:
        st.warning("📭 No hay datos de interacciones de usuario para el período seleccionado.")
        
        if not df_events.empty:
            st.info("""
            ℹ️ **Nota:** Hay eventos generales pero ninguno clasificado como interacción de usuario.
            
            Eventos de interacción reconocidos:
            - `search.filter.used` - Usuario usó filtros
            - `category.clicked` - Usuario clickeó categoría
            - `listing.viewed` - Usuario vio un listing
            - `listing.created` - Usuario creó un listing
            - `auth.login.success` - Usuario hizo login
            """)
        else:
            st.error("❌ No hay ningún evento registrado en este período.")
    
    st.markdown("---")
    
    # ========================================================================
    # Sección: Tiempo en Pantallas
    # ========================================================================
    
    st.markdown("## ⏱️ Tiempo en Pantallas")
    
    if not df_time.empty:
        # KPIs de tiempo
        total_time_seconds = df_time['total_seconds'].sum()
        total_time_minutes = total_time_seconds / 60
        total_time_hours = total_time_minutes / 60
        total_views = df_time['views'].sum()
        avg_time_per_view = total_time_seconds / total_views if total_views > 0 else 0
        
        metrics = [
            {
                "label": "⏱️ Tiempo Total",
                "value": f"{total_time_hours:.1f}h",
                "help": f"{total_time_minutes:.0f} minutos totales"
            },
            {
                "label": "👁️ Vistas Totales",
                "value": format_number(total_views),
                "help": "Total de vistas de pantallas"
            },
            {
                "label": "⏰ Tiempo Promedio",
                "value": f"{avg_time_per_view:.0f}s",
                "help": "Tiempo promedio por vista de pantalla"
            }
        ]
        
        metric_row(metrics)
        
        st.markdown("---")
        
        # Pantallas con más tiempo
        st.markdown("### 🏆 Pantallas con Más Engagement")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Por tiempo total
            df_time_sorted = df_time.sort_values('total_seconds', ascending=False).head(10)
            df_time_sorted['total_minutes'] = df_time_sorted['total_seconds'] / 60
            
            fig_time_total = horizontal_bar_chart(
                df_time_sorted,
                x='total_minutes',
                y='screen',
                title='Top 10 Pantallas por Tiempo Total (minutos)',
                height=400
            )
            st.plotly_chart(fig_time_total, use_container_width=True)
        
        with col2:
            # Por tiempo promedio
            df_avg_sorted = df_time.sort_values('avg_seconds', ascending=False).head(10)
            
            fig_time_avg = horizontal_bar_chart(
                df_avg_sorted,
                x='avg_seconds',
                y='screen',
                title='Top 10 Pantallas por Tiempo Promedio (segundos)',
                height=400
            )
            st.plotly_chart(fig_time_avg, use_container_width=True)
        
        # Tabla detallada
        st.markdown("### 📊 Resumen de Pantallas")
        
        df_time_display = df_time.copy()
        df_time_display['avg_minutes'] = (df_time_display['avg_seconds'] / 60).round(2)
        df_time_display['total_minutes'] = (df_time_display['total_seconds'] / 60).round(2)
        
        st.dataframe(
            df_time_display[['screen', 'views', 'total_minutes', 'avg_minutes']].rename(columns={
                'screen': 'Pantalla',
                'views': 'Vistas',
                'total_minutes': 'Tiempo Total (min)',
                'avg_minutes': 'Tiempo Promedio (min)'
            }).sort_values('Tiempo Total (min)', ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        # Insights
        st.markdown("### 💡 Insights")
        
        # Pantalla con más engagement
        top_screen = df_time.loc[df_time['total_seconds'].idxmax()]
        longest_screen = df_time.loc[df_time['avg_seconds'].idxmax()]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **📱 Pantalla Más Vista:**
            
            **{top_screen['screen']}**
            - {format_number(top_screen['views'])} vistas
            - {top_screen['total_seconds']/60:.1f} minutos totales
            """)
        
        with col2:
            st.info(f"""
            **⏰ Mayor Tiempo Promedio:**
            
            **{longest_screen['screen']}**
            - {longest_screen['avg_seconds']:.0f} segundos promedio
            - {format_number(longest_screen['views'])} vistas
            """)
    
    else:
        st.info("📭 No hay datos de tiempo en pantallas para el período seleccionado.")
        st.markdown("""
        **¿Por qué no hay datos?**
        
        Los datos de tiempo en pantallas se generan cuando:
        - Los usuarios navegan entre pantallas usando `telemetry.trackScreenView()`
        - La app registra eventos de tipo `screen.view`
        
        **Para generar datos:**
        1. Asegúrate de que la app móvil llame `trackScreenView()` en cada pantalla
        2. Los usuarios deben navegar por la app
        3. Se calcula el tiempo entre vistas consecutivas de pantallas
        """)


if __name__ == "__main__":
    render_behavior_page()
