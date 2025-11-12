"""
Componentes de Gráficos Reutilizables
======================================
Funciones para crear gráficos consistentes usando Plotly.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Optional


def line_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    height: int = 400
) -> go.Figure:
    """
    Crea un gráfico de líneas.
    
    Args:
        data: DataFrame con los datos
        x: Columna para el eje X
        y: Columna para el eje Y
        title: Título del gráfico
        color: Columna opcional para agrupar por color
        height: Altura del gráfico en píxeles
        
    Returns:
        Figura de Plotly
    """
    fig = px.line(
        data,
        x=x,
        y=y,
        color=color,
        title=title,
        height=height
    )
    
    fig.update_layout(
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    
    return fig


def bar_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    orientation: str = 'v',
    height: int = 400
) -> go.Figure:
    """
    Crea un gráfico de barras.
    
    Args:
        data: DataFrame con los datos
        x: Columna para el eje X
        y: Columna para el eje Y
        title: Título del gráfico
        color: Columna opcional para agrupar por color
        orientation: 'v' para vertical, 'h' para horizontal
        height: Altura del gráfico en píxeles
        
    Returns:
        Figura de Plotly
    """
    fig = px.bar(
        data,
        x=x,
        y=y,
        color=color,
        title=title,
        orientation=orientation,
        height=height
    )
    
    fig.update_layout(
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    
    return fig


def pie_chart(
    data: pd.DataFrame,
    names: str,
    values: str,
    title: str,
    height: int = 400
) -> go.Figure:
    """
    Crea un gráfico de pastel.
    
    Args:
        data: DataFrame con los datos
        names: Columna con los nombres de las categorías
        values: Columna con los valores
        title: Título del gráfico
        height: Altura del gráfico en píxeles
        
    Returns:
        Figura de Plotly
    """
    fig = px.pie(
        data,
        names=names,
        values=values,
        title=title,
        height=height
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def stacked_bar_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    color: str,
    title: str,
    height: int = 400
) -> go.Figure:
    """
    Crea un gráfico de barras apiladas.
    
    Args:
        data: DataFrame con los datos
        x: Columna para el eje X
        y: Columna para el eje Y
        color: Columna para apilar por color
        title: Título del gráfico
        height: Altura del gráfico en píxeles
        
    Returns:
        Figura de Plotly
    """
    fig = px.bar(
        data,
        x=x,
        y=y,
        color=color,
        title=title,
        height=height,
        barmode='stack'
    )
    
    fig.update_layout(
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    
    return fig


def area_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: Optional[str] = None,
    height: int = 400
) -> go.Figure:
    """
    Crea un gráfico de área.
    
    Args:
        data: DataFrame con los datos
        x: Columna para el eje X
        y: Columna para el eje Y
        title: Título del gráfico
        color: Columna opcional para agrupar por color
        height: Altura del gráfico en píxeles
        
    Returns:
        Figura de Plotly
    """
    fig = px.area(
        data,
        x=x,
        y=y,
        color=color,
        title=title,
        height=height
    )
    
    fig.update_layout(
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    
    return fig


def horizontal_bar_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    height: int = 400
) -> go.Figure:
    """
    Crea un gráfico de barras horizontales (útil para rankings).
    
    Args:
        data: DataFrame con los datos
        x: Columna para los valores
        y: Columna para las categorías
        title: Título del gráfico
        height: Altura del gráfico en píxeles
        
    Returns:
        Figura de Plotly
    """
    # Ordenar por valores
    data_sorted = data.sort_values(x, ascending=True)
    
    fig = px.bar(
        data_sorted,
        x=x,
        y=y,
        title=title,
        orientation='h',
        height=height
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    
    return fig
