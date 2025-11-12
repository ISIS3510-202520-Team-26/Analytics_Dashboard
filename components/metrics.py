"""
Componentes de Métricas
========================
Funciones para mostrar métricas y KPIs de manera consistente.
"""

import streamlit as st
from typing import Optional, Union


def metric_card(
    label: str,
    value: Union[str, int, float],
    delta: Optional[Union[str, int, float]] = None,
    delta_color: str = "normal",
    help_text: Optional[str] = None
):
    """
    Muestra una tarjeta de métrica usando st.metric.
    
    Args:
        label: Etiqueta de la métrica
        value: Valor principal
        delta: Cambio respecto al período anterior (opcional)
        delta_color: Color del delta ("normal", "inverse", "off")
        help_text: Texto de ayuda opcional
    """
    st.metric(
        label=label,
        value=value,
        delta=delta,
        delta_color=delta_color,
        help=help_text
    )


def metric_row(metrics: list):
    """
    Muestra una fila de métricas en columnas.
    
    Args:
        metrics: Lista de dicts con keys: label, value, delta (opcional), help (opcional)
        
    Ejemplo:
        metric_row([
            {"label": "DAU", "value": 1234, "delta": 10},
            {"label": "Revenue", "value": "$5,678", "delta": -5},
            {"label": "Orders", "value": 42}
        ])
    """
    cols = st.columns(len(metrics))
    
    for col, metric_data in zip(cols, metrics):
        with col:
            metric_card(
                label=metric_data.get("label", ""),
                value=metric_data.get("value", "—"),
                delta=metric_data.get("delta"),
                delta_color=metric_data.get("delta_color", "normal"),
                help_text=metric_data.get("help")
            )


def format_currency(cents: int) -> str:
    """
    Formatea centavos a formato de moneda.
    
    Args:
        cents: Cantidad en centavos
        
    Returns:
        String formateado (ej: "$1,234.56")
    """
    dollars = cents / 100
    return f"${dollars:,.2f}"


def format_number(number: Union[int, float], decimals: int = 0) -> str:
    """
    Formatea un número con separadores de miles.
    
    Args:
        number: Número a formatear
        decimals: Cantidad de decimales
        
    Returns:
        String formateado (ej: "1,234" o "1,234.56")
    """
    if decimals == 0:
        return f"{int(number):,}"
    else:
        return f"{number:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Formatea un valor decimal a porcentaje.
    
    Args:
        value: Valor decimal (ej: 0.1234)
        decimals: Cantidad de decimales
        
    Returns:
        String formateado (ej: "12.3%")
    """
    return f"{value * 100:.{decimals}f}%"


def calculate_growth(current: float, previous: float) -> Optional[float]:
    """
    Calcula el crecimiento porcentual entre dos valores.
    
    Args:
        current: Valor actual
        previous: Valor anterior
        
    Returns:
        Crecimiento como decimal (ej: 0.15 para 15%) o None si previous es 0
    """
    if previous == 0:
        return None
    
    return (current - previous) / previous
