"""
Página de Conversion Funnel (BQ 4.3)
=====================================
Análisis del funnel de conversión de órdenes desde creación hasta completado.
Business Question Tipo 4 - Complejidad Alta con SQL Avanzado
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from services.api_client import get_api_client
from components.filters import date_range_filter
from components.metrics import metric_row, format_number, format_currency, calculate_growth
from components.charts import line_chart, pie_chart, horizontal_bar_chart
from utils.config import API_BASE_URL
import plotly.graph_objects as go


def render_conversion_funnel_page():
    """Renderiza la página de Conversion Funnel."""
    
    st.title("🔄 Funnel de Conversión de Órdenes")
    st.markdown("""
    **Business Question 4.3** - Análisis avanzado del funnel de conversión de órdenes.
    Identifica cuellos de botella y tasas de conversión entre cada estado del proceso de compra.
    """)
    
    # Filtro de fechas
    start_date, end_date = date_range_filter(key="conversion_funnel", default_days=30)
    
    # Obtener cliente API
    api = get_api_client(API_BASE_URL)
    
    # Contenedor para loading
    with st.spinner("Cargando datos del funnel de conversión..."):
        try:
            # BQ 4.3 - Conversion Funnel
            funnel_data = api.get_conversion_funnel(start_date, end_date)
            df_funnel = pd.DataFrame(funnel_data)
            
            # BQ 4.1 - Órdenes por estado (para análisis temporal)
            orders_data = api.get_orders_by_status_by_day(start_date, end_date)
            df_orders = pd.DataFrame(orders_data)
            
        except Exception as e:
            st.error(f"Error al cargar datos: {str(e)}")
            st.info("💡 Esta función requiere el endpoint BQ 4.3 en el backend.")
            return
    
    # ========================================================================
    # KPIs Principales del Funnel
    # ========================================================================
    
    if not df_funnel.empty:
        # Calcular métricas clave
        total_created = df_funnel[df_funnel['status'] == 'created']['count'].sum()
        total_paid = df_funnel[df_funnel['status'] == 'paid']['count'].sum()
        total_shipped = df_funnel[df_funnel['status'] == 'shipped']['count'].sum()
        total_completed = df_funnel[df_funnel['status'] == 'completed']['count'].sum()
        total_cancelled = df_funnel[df_funnel['status'] == 'cancelled']['count'].sum()
        
        # Tasas de conversión
        conversion_to_paid = (total_paid / total_created * 100) if total_created > 0 else 0
        conversion_to_shipped = (total_shipped / total_paid * 100) if total_paid > 0 else 0
        conversion_to_completed = (total_completed / total_shipped * 100) if total_shipped > 0 else 0
        overall_conversion = (total_completed / total_created * 100) if total_created > 0 else 0
        cancellation_rate = (total_cancelled / total_created * 100) if total_created > 0 else 0
        
        # Mostrar KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🎯 Conversión Total",
                f"{overall_conversion:.1f}%",
                help="Porcentaje de órdenes creadas que llegan a completado"
            )
        
        with col2:
            st.metric(
                "💳 Creadas → Pagadas",
                f"{conversion_to_paid:.1f}%",
                help="Tasa de conversión de creadas a pagadas"
            )
        
        with col3:
            st.metric(
                "📦 Pagadas → Enviadas",
                f"{conversion_to_shipped:.1f}%",
                help="Tasa de conversión de pagadas a enviadas"
            )
        
        with col4:
            st.metric(
                "❌ Tasa de Cancelación",
                f"{cancellation_rate:.1f}%",
                delta=None,
                delta_color="inverse",
                help="Porcentaje de órdenes canceladas"
            )
        
        st.markdown("---")
        
        # ====================================================================
        # Gráfico de Funnel Visual
        # ====================================================================
        
        st.markdown("### 📊 Visualización del Funnel de Conversión")
        
        # Preparar datos para el funnel
        funnel_stages = []
        funnel_values = []
        funnel_colors = []
        
        stages_config = [
            ('created', '🆕 Creadas', total_created, '#3b82f6'),
            ('paid', '💳 Pagadas', total_paid, '#10b981'),
            ('shipped', '📦 Enviadas', total_shipped, '#f59e0b'),
            ('completed', '✅ Completadas', total_completed, '#8b5cf6'),
        ]
        
        for status, label, count, color in stages_config:
            if count > 0:
                funnel_stages.append(label)
                funnel_values.append(count)
                funnel_colors.append(color)
        
        # Crear gráfico de funnel
        fig_funnel = go.Figure(go.Funnel(
            y=funnel_stages,
            x=funnel_values,
            textposition="inside",
            textinfo="value+percent initial+percent previous",
            marker=dict(color=funnel_colors),
            connector=dict(line=dict(color="gray", width=2))
        ))
        
        fig_funnel.update_layout(
            title="Funnel de Conversión de Órdenes",
            height=450,
            showlegend=False
        )
        
        st.plotly_chart(fig_funnel, use_container_width=True)
        
        # ====================================================================
        # Métricas detalladas por etapa
        # ====================================================================
        
        st.markdown("### 📈 Análisis Detallado por Etapa")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Tasas de Conversión")
            
            metrics_data = {
                "Etapa": [
                    "Creadas → Pagadas",
                    "Pagadas → Enviadas", 
                    "Enviadas → Completadas",
                    "🎯 Conversión Total"
                ],
                "Tasa": [
                    f"{conversion_to_paid:.1f}%",
                    f"{conversion_to_shipped:.1f}%",
                    f"{conversion_to_completed:.1f}%",
                    f"{overall_conversion:.1f}%"
                ],
                "Drop-off": [
                    f"{100 - conversion_to_paid:.1f}%",
                    f"{100 - conversion_to_shipped:.1f}%",
                    f"{100 - conversion_to_completed:.1f}%",
                    f"{100 - overall_conversion:.1f}%"
                ]
            }
            
            df_metrics = pd.DataFrame(metrics_data)
            st.dataframe(df_metrics, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("#### 📊 Volumen por Estado")
            
            volume_data = {
                "Estado": ["Creadas", "Pagadas", "Enviadas", "Completadas", "Canceladas"],
                "Cantidad": [total_created, total_paid, total_shipped, total_completed, total_cancelled],
                "% del Total": [
                    f"{(total_created/total_created*100):.1f}%" if total_created > 0 else "0%",
                    f"{(total_paid/total_created*100):.1f}%" if total_created > 0 else "0%",
                    f"{(total_shipped/total_created*100):.1f}%" if total_created > 0 else "0%",
                    f"{(total_completed/total_created*100):.1f}%" if total_created > 0 else "0%",
                    f"{(total_cancelled/total_created*100):.1f}%" if total_created > 0 else "0%"
                ]
            }
            
            df_volume = pd.DataFrame(volume_data)
            st.dataframe(df_volume, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # ====================================================================
        # Análisis Temporal de Conversiones
        # ====================================================================
        
        st.markdown("### 📅 Tendencia de Conversión en el Tiempo")
        
        if not df_orders.empty:
            # Calcular conversión diaria
            df_daily = df_orders.pivot_table(
                index='day',
                columns='status',
                values='count',
                fill_value=0
            ).reset_index()
            
            # Calcular tasa de conversión diaria
            if 'created' in df_daily.columns and 'completed' in df_daily.columns:
                df_daily['conversion_rate'] = (
                    df_daily['completed'] / df_daily['created'] * 100
                ).fillna(0)
                
                fig_trend = go.Figure()
                
                fig_trend.add_trace(go.Scatter(
                    x=df_daily['day'],
                    y=df_daily['conversion_rate'],
                    mode='lines+markers',
                    name='Tasa de Conversión',
                    line=dict(color='#3b82f6', width=3),
                    marker=dict(size=8)
                ))
                
                fig_trend.update_layout(
                    title='Tasa de Conversión Diaria (Creadas → Completadas)',
                    xaxis_title='Fecha',
                    yaxis_title='Tasa de Conversión (%)',
                    height=400,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_trend, use_container_width=True)
            
            # Gráfico de área apilada
            st.markdown("#### 📊 Volumen de Órdenes por Estado")
            
            status_order = ['created', 'paid', 'shipped', 'completed', 'cancelled']
            status_colors = {
                'created': '#3b82f6',
                'paid': '#10b981',
                'shipped': '#f59e0b',
                'completed': '#8b5cf6',
                'cancelled': '#ef4444'
            }
            
            fig_stacked = go.Figure()
            
            for status in status_order:
                if status in df_daily.columns:
                    fig_stacked.add_trace(go.Scatter(
                        x=df_daily['day'],
                        y=df_daily[status],
                        mode='lines',
                        name=status.capitalize(),
                        stackgroup='one',
                        fillcolor=status_colors.get(status, '#gray'),
                        line=dict(width=0.5)
                    ))
            
            fig_stacked.update_layout(
                title='Órdenes por Estado a lo Largo del Tiempo',
                xaxis_title='Fecha',
                yaxis_title='Cantidad de Órdenes',
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_stacked, use_container_width=True)
        
        st.markdown("---")
        
        # ====================================================================
        # Insights y Recomendaciones
        # ====================================================================
        
        st.markdown("### 💡 Insights y Recomendaciones")
        
        # Identificar cuellos de botella
        bottlenecks = []
        
        if conversion_to_paid < 50:
            bottlenecks.append({
                "stage": "💳 Pago",
                "issue": "Baja conversión a pago",
                "rate": f"{conversion_to_paid:.1f}%",
                "recommendation": "Simplificar el proceso de pago, ofrecer más métodos de pago, reducir fricciones"
            })
        
        if conversion_to_shipped < 80:
            bottlenecks.append({
                "stage": "📦 Envío",
                "issue": "Demora en envíos",
                "rate": f"{conversion_to_shipped:.1f}%",
                "recommendation": "Optimizar logística de envío, mejorar comunicación con sellers"
            })
        
        if conversion_to_completed < 85:
            bottlenecks.append({
                "stage": "✅ Completado",
                "issue": "Baja tasa de completado",
                "rate": f"{conversion_to_completed:.1f}%",
                "recommendation": "Mejorar seguimiento de entregas, automatizar confirmaciones"
            })
        
        if cancellation_rate > 20:
            bottlenecks.append({
                "stage": "❌ Cancelaciones",
                "issue": "Alta tasa de cancelación",
                "rate": f"{cancellation_rate:.1f}%",
                "recommendation": "Analizar razones de cancelación, mejorar expectativas del producto"
            })
        
        if bottlenecks:
            st.warning("⚠️ **Cuellos de Botella Identificados:**")
            
            for bottleneck in bottlenecks:
                with st.expander(f"{bottleneck['stage']} - {bottleneck['issue']} ({bottleneck['rate']})"):
                    st.markdown(f"**Problema:** {bottleneck['issue']}")
                    st.markdown(f"**Tasa:** {bottleneck['rate']}")
                    st.markdown(f"**Recomendación:** {bottleneck['recommendation']}")
        else:
            st.success("✅ **Excelente desempeño del funnel!** No se identificaron cuellos de botella críticos.")
        
        # Estadísticas adicionales
        st.markdown("#### 📊 Estadísticas Clave")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "🎯 Mejor Conversión",
                f"{max(conversion_to_paid, conversion_to_shipped, conversion_to_completed):.1f}%"
            )
        
        with col2:
            st.metric(
                "⚠️ Peor Conversión",
                f"{min(conversion_to_paid, conversion_to_shipped, conversion_to_completed):.1f}%"
            )
        
        with col3:
            total_revenue_potential = total_created - total_completed
            st.metric(
                "💰 Órdenes Perdidas",
                format_number(total_revenue_potential),
                help="Órdenes que no llegaron a completarse"
            )
        
    else:
        st.info("No hay datos de conversión para el período seleccionado.")
        st.markdown("""
        **Nota:** Esta visualización requiere datos de órdenes en diferentes estados.
        Asegúrate de que el backend tenga órdenes registradas en el período seleccionado.
        """)


# Punto de entrada
if __name__ == "__main__":
    render_conversion_funnel_page()
