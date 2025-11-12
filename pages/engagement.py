"""
Página de Engagement (BQ 3.x)
==============================
Visualización de métricas de engagement de usuarios.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from services.api_client import get_api_client
from components.filters import date_range_filter
from components.metrics import metric_row, format_number, calculate_growth
from components.charts import line_chart, area_chart
from utils.config import API_BASE_URL


def render_engagement_page():
    """Renderiza la página de Engagement."""
    
    st.title("🔥 Métricas de Engagement")
    st.markdown("Daily Active Users (DAU) y sesiones de usuario.")
    
    # Filtro de fechas
    start_date, end_date = date_range_filter(key="engagement", default_days=30)
    
    # Obtener cliente API
    api = get_api_client(API_BASE_URL)
    
    # Contenedor para loading
    with st.spinner("Cargando datos de engagement..."):
        try:
            # BQ 3.1 - DAU
            dau_data = api.get_daily_active_users(start_date, end_date)
            df_dau = pd.DataFrame(dau_data)
            
            # BQ 3.2 - Sesiones
            sessions_data = api.get_sessions_by_day(start_date, end_date)
            df_sessions = pd.DataFrame(sessions_data)
            
        except Exception as e:
            st.error(f"Error al cargar datos: {str(e)}")
            return
    
    # ========================================================================
    # KPIs Principales
    # ========================================================================
    
    if not df_dau.empty and not df_sessions.empty:
        # Métricas del período actual
        total_dau = df_dau['dau'].sum()
        avg_dau = df_dau['dau'].mean()
        total_sessions = df_sessions['sessions'].sum()
        sessions_per_user = total_sessions / total_dau if total_dau > 0 else 0
        
        # Calcular período anterior
        days_diff = (end_date - start_date).days
        prev_start = start_date - timedelta(days=days_diff)
        prev_end = start_date - timedelta(days=1)
        
        try:
            prev_dau_data = api.get_daily_active_users(prev_start, prev_end)
            df_prev_dau = pd.DataFrame(prev_dau_data)
            
            if not df_prev_dau.empty:
                prev_avg_dau = df_prev_dau['dau'].mean()
                dau_growth = calculate_growth(avg_dau, prev_avg_dau)
            else:
                dau_growth = None
        except:
            dau_growth = None
        
        # Mostrar KPIs
        metrics = [
            {
                "label": "👥 DAU Promedio",
                "value": format_number(int(avg_dau)),
                "delta": f"{dau_growth*100:+.1f}%" if dau_growth else None,
                "help": "Daily Active Users promedio del período"
            },
            {
                "label": "📱 Sesiones Totales",
                "value": format_number(total_sessions),
                "help": "Total de sesiones únicas"
            },
            {
                "label": "🔄 Sesiones/Usuario",
                "value": f"{sessions_per_user:.2f}",
                "help": "Promedio de sesiones por usuario activo"
            }
        ]
        
        metric_row(metrics)
        
        st.markdown("---")
        
        # ====================================================================
        # Gráfico de DAU
        # ====================================================================
        
        st.markdown("### 📈 Daily Active Users (DAU)")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_dau = area_chart(
                df_dau,
                x='day',
                y='dau',
                title='Usuarios Activos por Día',
                height=400
            )
            st.plotly_chart(fig_dau, use_container_width=True)
        
        with col2:
            st.markdown("#### 📊 Estadísticas")
            st.metric("DAU Máximo", format_number(int(df_dau['dau'].max())))
            st.metric("DAU Mínimo", format_number(int(df_dau['dau'].min())))
            st.metric("DAU Promedio", format_number(int(df_dau['dau'].mean())))
            st.metric("Desv. Estándar", format_number(int(df_dau['dau'].std())))
        
        # Tabla de datos
        with st.expander("📊 Ver datos detallados de DAU"):
            st.dataframe(
                df_dau.rename(columns={
                    'day': 'Día',
                    'dau': 'DAU'
                }),
                use_container_width=True
            )
        
        st.markdown("---")
        
        # ====================================================================
        # Gráfico de Sesiones
        # ====================================================================
        
        st.markdown("### 📱 Sesiones por Día")
        
        # Merge DAU y Sesiones para calcular sesiones por usuario
        df_merged = pd.merge(df_dau, df_sessions, on='day', how='inner')
        df_merged['sessions_per_user'] = df_merged['sessions'] / df_merged['dau']
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_sessions = line_chart(
                df_sessions,
                x='day',
                y='sessions',
                title='Sesiones Totales por Día',
                height=350
            )
            st.plotly_chart(fig_sessions, use_container_width=True)
        
        with col2:
            fig_sessions_per_user = line_chart(
                df_merged,
                x='day',
                y='sessions_per_user',
                title='Sesiones por Usuario por Día',
                height=350
            )
            st.plotly_chart(fig_sessions_per_user, use_container_width=True)
        
        # Tabla de datos combinada
        with st.expander("📊 Ver datos detallados de sesiones"):
            st.dataframe(
                df_merged[['day', 'dau', 'sessions', 'sessions_per_user']].rename(columns={
                    'day': 'Día',
                    'dau': 'DAU',
                    'sessions': 'Sesiones',
                    'sessions_per_user': 'Sesiones/Usuario'
                }),
                use_container_width=True
            )
        
        st.markdown("---")
        
        # ====================================================================
        # Insights
        # ====================================================================
        
        st.markdown("### 💡 Insights")
        
        # Calcular tendencia
        if len(df_dau) >= 7:
            recent_dau = df_dau.tail(7)['dau'].mean()
            older_dau = df_dau.head(7)['dau'].mean()
            trend = "📈 al alza" if recent_dau > older_dau else "📉 a la baja"
        else:
            trend = "sin datos suficientes"
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **Tendencia de DAU:** {trend}
            
            El DAU promedio es de **{format_number(int(avg_dau))}** usuarios activos por día.
            """)
        
        with col2:
            engagement_level = "🔥 Alto" if sessions_per_user >= 2 else "📊 Moderado" if sessions_per_user >= 1.5 else "⚠️ Bajo"
            st.info(f"""
            **Nivel de Engagement:** {engagement_level}
            
            Los usuarios abren la app en promedio **{sessions_per_user:.2f}** veces por día.
            """)
    
    else:
        st.warning("⚠️ No hay datos disponibles para el período seleccionado.")


if __name__ == "__main__":
    render_engagement_page()
