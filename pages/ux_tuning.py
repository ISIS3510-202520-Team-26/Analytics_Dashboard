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
    
    # Obtener catálogo de categorías para mapear IDs a nombres
    categories_map = {}
    try:
        categories_data = api.get_categories()
        if categories_data:
            # Crear mapeo con diferentes variantes del ID
            for cat in categories_data:
                cat_id = str(cat['id'])
                cat_name = cat.get('name', cat_id)
                categories_map[cat_id] = cat_name
                categories_map[cat_id.lower()] = cat_name
                categories_map[cat_id.upper()] = cat_name
    except Exception as e:
        st.warning(f"⚠️ No se pudo cargar el catálogo de categorías: {str(e)}")
    
    # Intentar obtener datos de categorías desde múltiples fuentes
    df_categories = None
    data_source = None
    
    # OPCIÓN 1: Buscar en todos los eventos category.clicked (BQ 2.1)
    # El evento category.clicked podría tener el categoryId en properties
    category_events = df_agg[df_agg['event_type'] == 'category.clicked']
    
    if not category_events.empty:
        total_clicks = category_events['count'].sum()
        if total_clicks > 0:
            # Por ahora no tenemos el desglose por categoría individual desde BQ 2.1
            # Pero sabemos cuántos clicks totales hay
            print(f"[UX Tuning] Total category.clicked events: {total_clicks}")
    
    # OPCIÓN 2: Intentar desde BQ 2.2 (clicks por botón)
    try:
        clicks_data = api.get_clicks_by_button_by_day(start_date, end_date)
        df_clicks = pd.DataFrame(clicks_data)
        
        if not df_clicks.empty and 'button' in df_clicks.columns:
            # Filtrar valores nulos o vacíos en button
            df_clicks = df_clicks[df_clicks['button'].notna() & (df_clicks['button'] != '')]
            
            if not df_clicks.empty:
                df_categories = df_clicks.groupby('button')['count'].sum().reset_index()
                df_categories.columns = ['category_id', 'count']
                data_source = "clicks"
    except:
        pass
    
    # OPCIÓN 3: Si no hay datos de clicks con button, usar listings creados por categoría
    if df_categories is None or df_categories.empty:
        try:
            listings_data = api.get_listings_per_day_by_category(start_date, end_date)
            df_listings = pd.DataFrame(listings_data)
            
            if not df_listings.empty and 'category_id' in df_listings.columns:
                df_listings = df_listings[df_listings['category_id'].notna() & (df_listings['category_id'] != '')]
                
                if not df_listings.empty:
                    df_categories = df_listings.groupby('category_id')['count'].sum().reset_index()
                    data_source = "listings"
        except:
            pass
    
    # Mostrar resultados
    if df_categories is not None and not df_categories.empty:
        # Ordenar por count
        df_categories = df_categories.sort_values('count', ascending=False)
        
        # Convertir category_id a string para el mapeo
        df_categories['category_id'] = df_categories['category_id'].astype(str)
        
        # Mapear category_id a nombres
        if categories_map:
            df_categories['category_name'] = df_categories['category_id'].apply(
                lambda x: categories_map.get(x, f"Cat: {x[:8]}...")
            )
        else:
            # Si no hay categorías, mostrar solo primeros caracteres del UUID
            df_categories['category_name'] = df_categories['category_id'].apply(
                lambda x: f"Cat: {x[:8]}..." if len(x) > 8 else x
            )
        
        # Mensaje según la fuente de datos
        if data_source == "clicks":
            st.info("""
            💡 **Nota:** Las categorías recomendadas se calculan principalmente desde 
            el almacenamiento local (`recordLocalCategoryUse`) pero los eventos de 
            `category.clicked` pueden usarse como indicador de interés.
            """)
            metric_label = "🖱️ Total Clicks en Categorías"
        else:
            st.warning("""
            ⚠️ **Datos alternativos:** No hay eventos `category.clicked` con el campo `button` 
            correctamente configurado. Mostrando datos de **listings creados por categoría** como proxy.
            
            Para ver clicks reales, asegúrate de que la app Flutter envíe:
            ```dart
            telemetry.trackEvent(
              eventType: 'category.clicked',
              properties: {'button': categoryId},
            );
            ```
            """)
            metric_label = "📝 Listings por Categoría"
        
        # Mostrar total
        total_count = df_categories['count'].sum()
        st.metric(
            label=metric_label,
            value=format_number(int(total_count)),
            help="Total registrado en el período seleccionado"
        )
        
        st.markdown("---")
        
        # Mostrar gráfico
        fig_categories = horizontal_bar_chart(
            df_categories,
            x='count',
            y='category_name',
            title='Actividad por Categoría',
            height=max(300, len(df_categories) * 40)
        )
        st.plotly_chart(fig_categories, use_container_width=True)
        
        # Tabla con detalles
        with st.expander("📋 Ver tabla de categorías"):
            st.dataframe(
                df_categories[['category_name', 'category_id', 'count']].rename(columns={
                    'category_name': 'Categoría',
                    'category_id': 'ID',
                    'count': 'Clicks' if data_source == "clicks" else 'Listings'
                }),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("""
        No hay datos de categorías disponibles para este período.
        
        💡 **Para ver datos aquí:**
        - Asegúrate de que hay eventos `category.clicked` con `properties.button = categoryId`
        - O que hay listings creados con `category_id` definido
        """)
    
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
