"""
Sistema de Autenticación
=========================
Manejo de login y tokens para el dashboard.
"""

import streamlit as st
import requests
from typing import Optional

def login(email: str, password: str, api_url: str) -> Optional[tuple[str, str]]:
    """
    Realiza login en el backend y retorna access_token y refresh_token.
    
    Args:
        email: Email del usuario
        password: Contraseña
        api_url: URL base del API
        
    Returns:
        (access_token, refresh_token) si el login es exitoso, None en caso contrario
    """
    try:
        response = requests.post(
            f"{api_url}/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            refresh_token = data.get('refresh_token')
            
            if access_token and refresh_token:
                return (access_token, refresh_token)
            else:
                st.error("Respuesta del servidor incompleta")
                return None
        else:
            error_detail = "Credenciales inválidas" if response.status_code == 401 else f"Error {response.status_code}"
            st.error(f"Error en login: {error_detail}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("❌ No se pudo conectar al servidor. Verifica que el backend esté corriendo.")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Timeout: El servidor tardó demasiado en responder")
        return None
    except Exception as e:
        st.error(f"Error inesperado: {str(e)}")
        return None


def get_or_create_token(api_url: str, email: str = "t@t.com", password: str = "12345678") -> Optional[str]:
    """
    Obtiene el token guardado en session_state o crea uno nuevo haciendo login.
    
    Args:
        api_url: URL base del API
        email: Email por defecto para login
        password: Contraseña por defecto para login
        
    Returns:
        access_token si está disponible o se pudo obtener, None en caso contrario
    """
    # Verificar si ya tenemos token en session_state
    if 'auth_token' in st.session_state and st.session_state.auth_token:
        return st.session_state.auth_token
    
    # Si no hay token, hacer login automático
    with st.spinner("🔐 Autenticando con el backend..."):
        result = login(email, password, api_url)
        
        if result:
            access_token, refresh_token = result
            st.session_state.auth_token = access_token
            st.session_state.refresh_token = refresh_token
            st.session_state.auth_email = email
            st.success("✅ Autenticación exitosa")
            return access_token
        else:
            st.error("❌ No se pudo autenticar. Verifica las credenciales y la conexión.")
            return None


def clear_token():
    """Limpia el token de autenticación de la sesión."""
    if 'auth_token' in st.session_state:
        del st.session_state.auth_token
    if 'refresh_token' in st.session_state:
        del st.session_state.refresh_token
    if 'auth_email' in st.session_state:
        del st.session_state.auth_email


def is_authenticated() -> bool:
    """Verifica si hay un token válido en la sesión."""
    return 'auth_token' in st.session_state and st.session_state.auth_token is not None
