"""
Página de Listings & Escrow (BQ 1.x)
=====================================
Visualización de métricas de listings y escrow.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from services.api_client import get_api_client
from components.filters import date_range_filter
from components.metrics import metric_row, format_number, format_percentage
from components.charts import line_chart, bar_chart, pie_chart, horizontal_bar_chart
from utils.config import API_BASE_URL


def render_listings_page():
    """Renderiza la página de Listings & Escrow."""
    
    st.title("📦 Listings & Escrow Analytics")
    st.markdown("Métricas de creación de listings y cancelación de escrow.")
    
    # Filtro de fechas
    start_date, end_date = date_range_filter(key="listings", default_days=30)
    
    # Obtener cliente API
    api = get_api_client(API_BASE_URL)
    
    # Contenedor para loading
    with st.spinner("Cargando datos de listings..."):
        try:
            # BQ 1.1 - Listings por día y categoría
            listings_data = api.get_listings_per_day_by_category(start_date, end_date)
            df_listings = pd.DataFrame(listings_data)
            
            # BQ 1.2 - Tasa de cancelación de escrow
            escrow_data = api.get_escrow_cancel_rate(start_date, end_date)
            df_escrow = pd.DataFrame(escrow_data)
            
        except Exception as e:
            st.error(f"Error al cargar datos: {str(e)}")
            return
    
    # ========================================================================
    # Sección: Listings
    # ========================================================================
    
    st.markdown("## 📦 Listings Creados")
    
    if not df_listings.empty:
        # KPIs de listings
        total_listings = df_listings['count'].sum()
        unique_categories = df_listings['category_id'].nunique()
        avg_per_day = df_listings.groupby('day')['count'].sum().mean()
        
        metrics = [
            {
                "label": "📦 Total Listings",
                "value": format_number(total_listings),
                "help": "Listings creados en el período"
            },
            {
                "label": "📁 Categorías Activas",
                "value": format_number(unique_categories),
                "help": "Categorías con al menos un listing"
            },
            {
                "label": "📊 Promedio Diario",
                "value": format_number(int(avg_per_day)),
                "help": "Listings promedio por día"
            }
        ]
        
        metric_row(metrics)
        
        st.markdown("---")
        
        # Gráfico de tendencia temporal
        st.markdown("### 📈 Tendencia de Creación")
        
        df_listings_by_day = df_listings.groupby('day')['count'].sum().reset_index()
        
        fig_trend = line_chart(
            df_listings_by_day,
            x='day',
            y='count',
            title='Listings Creados por Día',
            height=400
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Gráfico por categoría
        st.markdown("### 📁 Distribución por Categoría")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de pastel
            df_by_category = df_listings.groupby('category_id')['count'].sum().reset_index()
            df_by_category['category_id'] = df_by_category['category_id'].fillna('Sin categoría')
            
            fig_pie = pie_chart(
                df_by_category,
                names='category_id',
                values='count',
                title='Listings por Categoría',
                height=400
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Gráfico de barras horizontales
            fig_bar = horizontal_bar_chart(
                df_by_category.head(10),
                x='count',
                y='category_id',
                title='Top 10 Categorías',
                height=400
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Tabla detallada
        with st.expander("📊 Ver datos detallados de listings"):
            st.dataframe(
                df_listings.rename(columns={
                    'day': 'Día',
                    'category_id': 'Categoría',
                    'count': 'Cantidad'
                }),
                use_container_width=True
            )
    
    else:
        st.info("No hay datos de listings para el período seleccionado.")
    
    st.markdown("---")
    
    # ========================================================================
    # Sección: Escrow
    # ========================================================================
    
    st.markdown("## 🔒 Análisis de Escrow")
    
    if not df_escrow.empty:
        # KPIs de escrow
        total_escrows = df_escrow['total'].sum()
        total_cancelled = df_escrow['cancelled'].sum()
        overall_cancel_rate = (total_cancelled / total_escrows * 100) if total_escrows > 0 else 0
        
        metrics = [
            {
                "label": "🔒 Total Escrows",
                "value": format_number(total_escrows),
                "help": "Total de transacciones escrow"
            },
            {
                "label": "❌ Cancelados",
                "value": format_number(total_cancelled),
                "help": "Escrows cancelados"
            },
            {
                "label": "📉 Tasa de Cancelación",
                "value": f"{overall_cancel_rate:.1f}%",
                "help": "Porcentaje de escrows cancelados"
            }
        ]
        
        metric_row(metrics)
        
        st.markdown("---")
        
        # Gráfico de tasa de cancelación por step
        st.markdown("### 🚦 Tasa de Cancelación por Step")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            fig_cancel = bar_chart(
                df_escrow,
                x='step',
                y='pct_cancelled',
                title='% de Cancelación por Step del Proceso',
                height=400
            )
            st.plotly_chart(fig_cancel, use_container_width=True)
        
        with col2:
            st.markdown("#### 🎯 Análisis de Friction Points")
            
            # Identificar el step con mayor cancelación
            worst_step = df_escrow.loc[df_escrow['pct_cancelled'].idxmax()]
            best_step = df_escrow.loc[df_escrow['pct_cancelled'].idxmin()]
            
            st.error(f"""
            **⚠️ Mayor Cancelación:**
            - **Step:** {worst_step['step']}
            - **Tasa:** {worst_step['pct_cancelled']:.1f}%
            - **Cantidad:** {worst_step['cancelled']}/{worst_step['total']}
            """)
            
            st.success(f"""
            **✅ Menor Cancelación:**
            - **Step:** {best_step['step']}
            - **Tasa:** {best_step['pct_cancelled']:.1f}%
            - **Cantidad:** {best_step['cancelled']}/{best_step['total']}
            """)
        
        # Tabla detallada
        st.markdown("### 📊 Detalle por Step")
        
        df_escrow_display = df_escrow.copy()
        df_escrow_display['pct_cancelled'] = df_escrow_display['pct_cancelled'].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(
            df_escrow_display.rename(columns={
                'step': 'Step',
                'total': 'Total',
                'cancelled': 'Cancelados',
                'pct_cancelled': '% Cancelación'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Insights
        st.markdown("### 💡 Recomendaciones")
        
        high_cancel_steps = df_escrow[df_escrow['pct_cancelled'] > 20]
        
        if not high_cancel_steps.empty:
            st.warning(f"""
            **⚠️ Atención requerida:**
            
            Los siguientes steps tienen tasas de cancelación superiores al 20%:
            {', '.join(high_cancel_steps['step'].tolist())}
            
            **Acciones sugeridas:**
            - Revisar la experiencia de usuario en estos steps
            - Simplificar el proceso si es posible
            - Agregar tooltips o ayuda contextual
            - Investigar razones comunes de cancelación
            """)
        else:
            st.success("""
            **✅ Buen desempeño:**
            
            Ningún step tiene una tasa de cancelación preocupante (>20%).
            El flujo de escrow funciona correctamente.
            """)
    
    else:
        st.info("No hay datos de escrow para el período seleccionado.")


if __name__ == "__main__":
    render_listings_page()
