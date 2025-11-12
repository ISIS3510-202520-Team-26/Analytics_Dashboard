"""
Página de UX Tuning Analytics
===============================
Análisis específico para el sistema de UX Tuning de la app Flutter.
Basado en los datos reales que genera tu TelemetryRepository.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from services.api_client import get_api_client
from components.filters import date_range_filter
from components.metrics import metric_row, format_number
from components.charts import line_chart, bar_chart, horizontal_bar_chart, pie_chart
from utils.config import API_BASE_URL


def render_ux_tuning_page():
    """Renderiza la página de UX Tuning Analytics."""
    
    st.title("🎯 UX Tuning Analytics")
    st.markdown("""
    Análisis de datos usados por `UxTuningService` para personalizar la experiencia de usuario.
    Basado en BQ 2.1, 2.2 y 2.4.
    """)
    
    # Filtro de fechas (por defecto últimas 24 horas como en el servicio)
    start_date, end_date = date_range_filter(key="ux_tuning", default_days=1)
    
    # Obtener cliente API
    api = get_api_client(API_BASE_URL)
    
    # Contenedor para loading
    with st.spinner("Cargando datos de UX Tuning..."):
        try:
            # BQ 2.1 - Eventos por tipo
            events_data = api.get_events_per_type_by_day(start_date, end_date)
            df_events = pd.DataFrame(events_data)
            
        except Exception as e:
            st.error(f"❌ Error al cargar datos: {str(e)}")
            return
    
    if df_events.empty:
        st.warning("⚠️ No hay datos de eventos para este período")
        return
    
    # Agregar por tipo de evento
    df_agg = df_events.groupby('event_type')['count'].sum().reset_index()
    
    # ========================================================================
    # Análisis de Búsquedas y Filtros
    # ========================================================================
    
    st.markdown("## 🔍 Análisis de Búsquedas y Filtros")
    st.markdown("_Usado para decidir `autoOpenFiltersAfterNPlainSearches`_")
    
    searches = df_agg[df_agg['event_type'] == 'search.performed']['count'].sum()
    filter_used = df_agg[df_agg['event_type'] == 'search.filter.used']['count'].sum()
    
    filter_ratio = (filter_used / searches * 100) if searches > 0 else 0
    low_filter_usage = filter_ratio < 25
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🔎 Búsquedas Totales",
            value=format_number(int(searches)),
            help="Eventos de tipo 'search.performed'"
        )
    
    with col2:
        st.metric(
            label="🔄 Veces Usado",
            value=format_number(int(searches)),
            help="Número total de veces que se usó el buscador"
        )
    
    with col3:
        st.metric(
            label="🎛️ Filtros Aplicados",
            value=format_number(int(filter_used)),
            help="Veces que se usaron filtros en búsquedas"
        )
    
    if low_filter_usage:
        st.warning("""
        ⚠️ **Recomendación UX:** `autoOpenFiltersAfterNPlainSearches = true`
        
        El ratio de uso de filtros es bajo (<25%). El sistema debería auto-abrir 
        los filtros después de 2 búsquedas sin filtros para aumentar el engagement.
        """)
    else:
        st.success("""
        ✅ **UX Óptimo:** Los usuarios usan filtros regularmente.
        No es necesario auto-abrir los filtros.
        """)
    
    st.markdown("---")
    
    # ========================================================================
    # Análisis de Categorías
    # ========================================================================
    
    st.markdown("## 📁 Análisis de Categorías")
    st.markdown("_Usado para `recommendedCategoryIds`_")
    
    try:
        # Obtener clicks por botón que incluye categorías
        clicks_data = api.get_clicks_by_button_by_day(start_date, end_date)
        df_clicks = pd.DataFrame(clicks_data)
        
        if not df_clicks.empty:
            # Filtrar solo categorías (botones que empiezan con "category_")
            df_categories = df_clicks[df_clicks['button'].str.startswith('category_', na=False)].copy()
            
            if not df_categories.empty:
                # Agrupar por categoría y sumar clicks
                df_cat_agg = df_categories.groupby('button')['count'].sum().reset_index()
                df_cat_agg = df_cat_agg.sort_values('count', ascending=False)
                
                # Limpiar nombres de categorías (remover prefijo "category_")
                df_cat_agg['category'] = df_cat_agg['button'].str.replace('category_', '', regex=False)
                
                st.info("""
                💡 **Nota:** Las categorías recomendadas se calculan principalmente desde 
                el almacenamiento local (`recordLocalCategoryUse`) pero los eventos de 
                `category.clicked` pueden usarse como indicador de interés.
                """)
                
                # Mostrar gráfico
                fig_categories = horizontal_bar_chart(
                    df_cat_agg,
                    x='count',
                    y='category',
                    title='Clicks por Categoría',
                    height=max(300, len(df_cat_agg) * 30)
                )
                st.plotly_chart(fig_categories, use_container_width=True)
                
                # Tabla con detalles
                with st.expander("📋 Ver tabla de categorías"):
                    st.dataframe(
                        df_cat_agg[['category', 'count']].rename(columns={
                            'category': 'Categoría',
                            'count': 'Clicks'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
            else:
                st.info("No hay clicks de categorías en este período")
        else:
            st.info("No hay datos de clicks disponibles para este período")
            
    except Exception as e:
        st.warning(f"⚠️ No se pudieron cargar los datos de categorías: {str(e)}")
    
    st.markdown("---")
    
    # ========================================================================
    # Análisis de CTAs (Call-to-Actions)
    # ========================================================================
    
    st.markdown("## 🎯 Análisis de CTAs")
    st.markdown("_Usado para `ctaPriority` basado en dwell time (BQ 2.4)_")
    
    st.info("""
    📝 **Mapeo de Pantallas a CTAs:**
    - `login`, `register` → CTA: **'auth'**
    - `home` → CTAs: **'search'**, **'publish'**
    - `create_listing` → CTA: **'publish'**
    
    El orden de prioridad se determina por el `total_seconds` (dwell time) 
    de cada pantalla en BQ 2.4.
    """)
    
    # Mostrar eventos relacionados con autenticación y listings
    auth_events = df_agg[df_agg['event_type'].str.contains('auth', case=False, na=False)]
    listing_events = df_agg[df_agg['event_type'].str.contains('listing', case=False, na=False)]
    search_events = df_agg[df_agg['event_type'].str.contains('search', case=False, na=False)]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔐 Auth CTA")
        auth_count = auth_events['count'].sum()
        st.metric("Eventos Auth", format_number(int(auth_count)))
        if auth_count > 0:
            with st.expander("Ver eventos"):
                st.dataframe(auth_events, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### 🔍 Search CTA")
        search_count = search_events['count'].sum()
        st.metric("Eventos Search", format_number(int(search_count)))
        if search_count > 0:
            with st.expander("Ver eventos"):
                st.dataframe(search_events.head(5), use_container_width=True, hide_index=True)
    
    with col3:
        st.markdown("### 📝 Publish CTA")
        listing_count = listing_events['count'].sum()
        st.metric("Eventos Listing", format_number(int(listing_count)))
        if listing_count > 0:
            with st.expander("Ver eventos"):
                st.dataframe(listing_events, use_container_width=True, hide_index=True)
    
    # Sugerir prioridad basada en volumen de eventos
    cta_volumes = [
        ('search', search_count),
        ('publish', listing_count),
        ('auth', auth_count)
    ]
    cta_volumes.sort(key=lambda x: x[1], reverse=True)
    
    st.markdown("### 🏆 Prioridad Sugerida (basada en volumen)")
    priority_str = " → ".join([f"**{cta[0]}** ({format_number(int(cta[1]))})" for cta in cta_volumes])
    st.success(f"📊 {priority_str}")
    
    st.info("""
    💡 **Nota:** Esta es una aproximación basada en volumen de eventos. 
    La prioridad real del `UxTuningService` se basa en **dwell time** (BQ 2.4),
    que mide cuánto tiempo pasan los usuarios en cada pantalla.
    """)
    
    st.markdown("---")
    
    # ========================================================================
    # Todos los Eventos
    # ========================================================================
    
    st.markdown("## 📊 Resumen de Todos los Eventos")
    
    # Gráfico de pastel
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pie = pie_chart(
            df_agg.head(10),
            names='event_type',
            values='count',
            title='Top 10 Tipos de Eventos',
            height=400
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        fig_bar = horizontal_bar_chart(
            df_agg.sort_values('count', ascending=False).head(15),
            x='count',
            y='event_type',
            title='Top 15 Eventos',
            height=400
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Tabla completa
    with st.expander("📋 Ver tabla completa de eventos"):
        st.dataframe(
            df_agg.sort_values('count', ascending=False).rename(columns={
                'event_type': 'Tipo de Evento',
                'count': 'Cantidad'
            }),
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown("---")
    
    # ========================================================================
    # Recomendaciones
    # ========================================================================
    
    st.markdown("## 💡 Recomendaciones para Mejorar UX Tuning")
    
    recommendations = []
    
    # Verificar si hay datos de BQ 2.4
    try:
        time_data = api.get_time_by_screen(start_date, end_date)
        if not time_data:
            recommendations.append({
                "type": "warning",
                "title": "⚠️ Falta BQ 2.4 (Dwell Time)",
                "message": """
                Para que el `UxTuningService` calcule correctamente la prioridad de CTAs,
                necesita datos de BQ 2.4 (tiempo en pantallas).
                
                **Acción requerida:** Implementar `trackScreenView()` en la app Flutter
                para registrar eventos de tipo `screen.view`.
                """
            })
    except:
        recommendations.append({
            "type": "error",
            "title": "❌ Error al verificar BQ 2.4",
            "message": "No se pudo verificar la disponibilidad de datos de dwell time."
        })
    
    # Mostrar recomendaciones
    for rec in recommendations:
        if rec["type"] == "warning":
            st.warning(f"**{rec['title']}**\n\n{rec['message']}")
        elif rec["type"] == "error":
            st.error(f"**{rec['title']}**\n\n{rec['message']}")
        else:
            st.info(f"**{rec['title']}**\n\n{rec['message']}")


if __name__ == "__main__":
    render_ux_tuning_page()
