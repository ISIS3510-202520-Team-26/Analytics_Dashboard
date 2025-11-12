"""
Componentes de Filtros
=======================
Filtros reutilizables para el dashboard.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Tuple


def date_range_filter(
    key: str = "date_range",
    default_days: int = 30
) -> Tuple[datetime, datetime]:
    """
    Filtro de rango de fechas con presets comunes.
    
    Args:
        key: Key única para el componente de Streamlit
        default_days: Días por defecto hacia atrás
        
    Returns:
        Tupla de (start_date, end_date)
    """
    st.markdown("### 📅 Rango de Fechas")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        preset = st.selectbox(
            "Período",
            [
                "Últimos 7 días",
                "Últimos 30 días",
                "Últimos 90 días",
                "Este mes",
                "Mes anterior",
                "Personalizado"
            ],
            key=f"{key}_preset"
        )
    
    # Calcular fechas según preset
    end_date = datetime.now()
    
    if preset == "Últimos 7 días":
        start_date = end_date - timedelta(days=7)
    elif preset == "Últimos 30 días":
        start_date = end_date - timedelta(days=30)
    elif preset == "Últimos 90 días":
        start_date = end_date - timedelta(days=90)
    elif preset == "Este mes":
        start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif preset == "Mes anterior":
        first_day_this_month = end_date.replace(day=1)
        end_date = first_day_this_month - timedelta(days=1)
        start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:  # Personalizado
        with col2:
            date_col1, date_col2 = st.columns(2)
            with date_col1:
                start_date = st.date_input(
                    "Desde",
                    value=end_date - timedelta(days=default_days),
                    key=f"{key}_start"
                )
                start_date = datetime.combine(start_date, datetime.min.time())
            with date_col2:
                end_date_input = st.date_input(
                    "Hasta",
                    value=end_date,
                    key=f"{key}_end"
                )
                end_date = datetime.combine(end_date_input, datetime.max.time())
        
        return start_date, end_date
    
    # Mostrar fechas seleccionadas
    with col2:
        st.info(f"📅 {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}")
    
    return start_date, end_date


def category_filter(categories: list, key: str = "category") -> list:
    """
    Filtro multi-select de categorías.
    
    Args:
        categories: Lista de categorías disponibles
        key: Key única para el componente
        
    Returns:
        Lista de categorías seleccionadas
    """
    return st.multiselect(
        "Filtrar por Categorías",
        options=categories,
        default=categories,
        key=key
    )


def status_filter(statuses: list, key: str = "status") -> list:
    """
    Filtro multi-select de estados.
    
    Args:
        statuses: Lista de estados disponibles
        key: Key única para el componente
        
    Returns:
        Lista de estados seleccionados
    """
    return st.multiselect(
        "Filtrar por Estado",
        options=statuses,
        default=statuses,
        key=key
    )
