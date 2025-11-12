"""
Página de Revenue & Órdenes (BQ 4.x)
=====================================
Visualización de métricas de revenue y órdenes.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from services.api_client import get_api_client
from components.filters import date_range_filter
from components.metrics import metric_row, format_currency, format_number, calculate_growth
from components.charts import line_chart, pie_chart, stacked_bar_chart
from utils.config import API_BASE_URL


def render_revenue_page():
    """Renderiza la página de Revenue & Órdenes."""
    
    st.title("💰 Revenue & Órdenes")
    st.markdown("Métricas de GMV (Gross Merchandise Value) y órdenes por estado.")
    
    # Filtro de fechas
    start_date, end_date = date_range_filter(key="revenue", default_days=30)
    
    # Obtener cliente API
    api = get_api_client(API_BASE_URL)
    
    # Contenedor para loading
    with st.spinner("Cargando datos de revenue..."):
        try:
            # BQ 4.2 - GMV por día
            gmv_data = api.get_gmv_by_day(start_date, end_date)
            df_gmv = pd.DataFrame(gmv_data)
            
            # BQ 4.1 - Órdenes por estado
            orders_data = api.get_orders_by_status_by_day(start_date, end_date)
            df_orders = pd.DataFrame(orders_data)
            
        except Exception as e:
            st.error(f"Error al cargar datos: {str(e)}")
            return
    
    # ========================================================================
    # KPIs Principales
    # ========================================================================
    
    if not df_gmv.empty:
        total_revenue_cents = df_gmv['gmv_cents'].sum()
        total_orders = df_gmv['orders_paid'].sum()
        avg_order_value = total_revenue_cents / total_orders if total_orders > 0 else 0
        
        # Calcular métricas del período anterior para comparación
        days_diff = (end_date - start_date).days
        prev_start = start_date - timedelta(days=days_diff)
        prev_end = start_date - timedelta(days=1)
        
        try:
            prev_gmv_data = api.get_gmv_by_day(prev_start, prev_end)
            df_prev_gmv = pd.DataFrame(prev_gmv_data)
            
            if not df_prev_gmv.empty:
                prev_revenue = df_prev_gmv['gmv_cents'].sum()
                prev_orders = df_prev_gmv['orders_paid'].sum()
                
                revenue_growth = calculate_growth(total_revenue_cents, prev_revenue)
                orders_growth = calculate_growth(total_orders, prev_orders)
            else:
                revenue_growth = None
                orders_growth = None
        except:
            revenue_growth = None
            orders_growth = None
        
        # Mostrar KPIs
        metrics = [
            {
                "label": "💵 Revenue Total",
                "value": format_currency(total_revenue_cents),
                "delta": f"{revenue_growth*100:+.1f}%" if revenue_growth else None,
                "help": "Suma de GMV de órdenes pagadas"
            },
            {
                "label": "📦 Órdenes Pagadas",
                "value": format_number(total_orders),
                "delta": f"{orders_growth*100:+.1f}%" if orders_growth else None,
                "help": "Total de órdenes con pago completado"
            },
            {
                "label": "🎯 Ticket Promedio",
                "value": format_currency(int(avg_order_value)),
                "help": "Revenue total / órdenes pagadas"
            }
        ]
        
        metric_row(metrics)
        
        st.markdown("---")
        
        # ====================================================================
        # Gráfico de Revenue Diario
        # ====================================================================
        
        st.markdown("### 📈 Revenue Diario")
        
        if not df_gmv.empty:
            # Convertir centavos a dólares
            df_gmv['revenue_usd'] = df_gmv['gmv_cents'] / 100
            
            fig_revenue = line_chart(
                df_gmv,
                x='day',
                y='revenue_usd',
                title='GMV por Día (USD)',
                height=400
            )
            st.plotly_chart(fig_revenue, use_container_width=True)
            
            # Tabla de datos
            with st.expander("📊 Ver datos detallados"):
                st.dataframe(
                    df_gmv[['day', 'revenue_usd', 'orders_paid']].rename(columns={
                        'day': 'Día',
                        'revenue_usd': 'Revenue (USD)',
                        'orders_paid': 'Órdenes Pagadas'
                    }),
                    use_container_width=True
                )
        else:
            st.info("No hay datos de revenue para el período seleccionado.")
        
        st.markdown("---")
        
        # ====================================================================
        # Órdenes por Estado
        # ====================================================================
        
        st.markdown("### 📊 Órdenes por Estado")
        
        if not df_orders.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de pastel con totales agregados
                df_orders_agg = df_orders.groupby('status')['count'].sum().reset_index()
                
                fig_pie = pie_chart(
                    df_orders_agg,
                    names='status',
                    values='count',
                    title='Distribución de Órdenes por Estado',
                    height=400
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Tabla resumen
                st.markdown("#### Resumen por Estado")
                df_summary = df_orders_agg.copy()
                total = df_summary['count'].sum()
                df_summary['percentage'] = (df_summary['count'] / total * 100).round(1)
                
                st.dataframe(
                    df_summary.rename(columns={
                        'status': 'Estado',
                        'count': 'Cantidad',
                        'percentage': '% del Total'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            
            # Gráfico de barras apiladas por día
            st.markdown("#### 📅 Evolución de Órdenes por Estado")
            
            fig_stacked = stacked_bar_chart(
                df_orders,
                x='day',
                y='count',
                color='status',
                title='Órdenes por Día (apiladas por estado)',
                height=400
            )
            st.plotly_chart(fig_stacked, use_container_width=True)
            
        else:
            st.info("No hay datos de órdenes para el período seleccionado.")
    
    else:
        st.warning("⚠️ No hay datos disponibles para el período seleccionado.")


if __name__ == "__main__":
    render_revenue_page()
