"""
Página de Features (BQ 5.x)
============================
Visualización de métricas de uso de features específicas.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from services.api_client import get_api_client
from components.filters import date_range_filter
from components.metrics import metric_row, format_number
from components.charts import line_chart, pie_chart, horizontal_bar_chart
from utils.config import API_BASE_URL


def render_features_page():
    """Renderiza la página de Features."""
    
    st.title("⚡ Uso de Features")
    st.markdown("Análisis de adopción y uso de features específicas de la aplicación.")
    
    # Filtro de fechas
    start_date, end_date = date_range_filter(key="features", default_days=30)
    
    # Obtener cliente API
    api = get_api_client(API_BASE_URL)
    
    # Contenedor para loading
    with st.spinner("Cargando datos de features..."):
        try:
            # BQ 5.1 - Quick View por categoría
            quickview_data = api.get_quick_view_by_category(start_date, end_date)
            df_quickview = pd.DataFrame(quickview_data)
            
        except Exception as e:
            st.error(f"Error al cargar datos: {str(e)}")
            return
    
    # ========================================================================
    # Sección: Quick View
    # ========================================================================
    
    st.markdown("## 👁️ Quick View Feature")
    st.markdown("""
    La feature **Quick View** permite a los usuarios ver un preview rápido de un listing
    sin navegar a la página completa. Analicemos su adopción y uso.
    """)
    
    if not df_quickview.empty:
        # KPIs de quick view
        total_quick_views = df_quickview['count'].sum()
        unique_categories = df_quickview['category_id'].nunique()
        avg_per_day = df_quickview.groupby('day')['count'].sum().mean()
        
        metrics = [
            {
                "label": "👁️ Total Quick Views",
                "value": format_number(total_quick_views),
                "help": "Veces que se usó la feature"
            },
            {
                "label": "📁 Categorías Activas",
                "value": format_number(unique_categories),
                "help": "Categorías con quick views"
            },
            {
                "label": "📊 Promedio Diario",
                "value": format_number(int(avg_per_day)),
                "help": "Quick views promedio por día"
            }
        ]
        
        metric_row(metrics)
        
        st.markdown("---")
        
        # Gráfico de tendencia
        st.markdown("### 📈 Tendencia de Uso")
        
        df_quickview_by_day = df_quickview.groupby('day')['count'].sum().reset_index()
        
        fig_trend = line_chart(
            df_quickview_by_day,
            x='day',
            y='count',
            title='Quick Views por Día',
            height=400
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Análisis por categoría
        st.markdown("### 📁 Uso por Categoría")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de pastel
            df_by_category = df_quickview.groupby('category_id')['count'].sum().reset_index()
            df_by_category['category_id'] = df_by_category['category_id'].fillna('Sin categoría')
            
            fig_pie = pie_chart(
                df_by_category,
                names='category_id',
                values='count',
                title='Distribución por Categoría',
                height=400
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Gráfico de barras horizontales
            df_sorted = df_by_category.sort_values('count', ascending=False).head(10)
            
            fig_bar = horizontal_bar_chart(
                df_sorted,
                x='count',
                y='category_id',
                title='Top 10 Categorías',
                height=400
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Tabla detallada
        st.markdown("### 📊 Detalle por Categoría")
        
        df_category_summary = df_by_category.copy()
        total = df_category_summary['count'].sum()
        df_category_summary['percentage'] = (df_category_summary['count'] / total * 100).round(1)
        df_category_summary = df_category_summary.sort_values('count', ascending=False)
        
        st.dataframe(
            df_category_summary.rename(columns={
                'category_id': 'Categoría',
                'count': 'Quick Views',
                'percentage': '% del Total'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        
        # ====================================================================
        # Insights y Recomendaciones
        # ====================================================================
        
        st.markdown("### 💡 Insights")
        
        # Categoría más popular
        top_category = df_by_category.loc[df_by_category['count'].idxmax()]
        top_pct = (top_category['count'] / total * 100)
        
        # Calcular tasa de adopción (asumir datos de listings si existen)
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"""
            **🏆 Categoría Más Popular:**
            
            **{top_category['category_id']}**
            - {format_number(top_category['count'])} quick views
            - {top_pct:.1f}% del total
            
            Esta categoría lidera en engagement con la feature Quick View.
            """)
        
        with col2:
            # Tendencia
            if len(df_quickview_by_day) >= 7:
                recent = df_quickview_by_day.tail(7)['count'].mean()
                older = df_quickview_by_day.head(7)['count'].mean()
                trend = "📈 creciendo" if recent > older else "📉 decreciendo"
                change = ((recent - older) / older * 100) if older > 0 else 0
            else:
                trend = "sin datos suficientes"
                change = 0
            
            st.info(f"""
            **📊 Tendencia de Adopción:**
            
            La feature está {trend}
            {f'({change:+.1f}% vs período anterior)' if change != 0 else ''}
            
            Uso promedio: {avg_per_day:.0f} quick views/día
            """)
        
        # Recomendaciones
        st.markdown("### 🎯 Recomendaciones")
        
        if avg_per_day < 100:
            st.warning("""
            **⚠️ Bajo uso de la feature:**
            
            - Considerar hacer la feature más visible en la UI
            - Agregar tooltips o onboarding para nuevos usuarios
            - Analizar si el placement del botón es óptimo
            - Considerar A/B testing de diferentes diseños
            """)
        elif avg_per_day < 500:
            st.info("""
            **📊 Uso moderado:**
            
            - La feature está siendo adoptada gradualmente
            - Continuar monitoreando la tendencia
            - Considerar optimizaciones de performance
            - Recopilar feedback de usuarios
            """)
        else:
            st.success("""
            **🎉 Excelente adopción:**
            
            - La feature es muy valorada por los usuarios
            - Mantener la calidad y performance
            - Considerar features similares para otras áreas
            - Usar como caso de éxito interno
            """)
        
        # Distribución temporal
        with st.expander("📅 Ver distribución temporal detallada"):
            st.dataframe(
                df_quickview.rename(columns={
                    'day': 'Día',
                    'category_id': 'Categoría',
                    'count': 'Quick Views'
                }),
                use_container_width=True
            )
    
    else:
        st.warning("⚠️ No hay datos de Quick View para el período seleccionado.")
        st.info("""
        **Posibles razones:**
        - La feature aún no está implementada
        - No hay eventos siendo registrados
        - El período seleccionado no tiene actividad
        """)
    
    # ========================================================================
    # Placeholder para features adicionales
    # ========================================================================
    
    st.markdown("---")
    st.markdown("## 🚀 Otras Features")
    st.info("""
    📝 **Próximamente:** Análisis de otras features como:
    - 💬 Chat directo
    - ⭐ Sistema de reviews
    - 🔔 Notificaciones push
    - 📍 Búsqueda geográfica
    - 🎯 Recomendaciones personalizadas
    
    Agrega eventos en el backend para estas features y aparecerán aquí automáticamente.
    """)


if __name__ == "__main__":
    render_features_page()
