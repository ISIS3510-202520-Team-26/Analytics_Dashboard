# 🚀 Guía Rápida de Inicio

## ✅ Dashboard Instalado y Funcionando

Tu dashboard de analytics ya está configurado y listo para usar.

## 📋 Comandos Básicos

### Ejecutar el Dashboard

**Opción más fácil:**
```
Doble click en: run.bat
```

**O desde PowerShell:**
```powershell
cd D:\University\DevelopmentMobileApps\analytics-dashboard
python -m streamlit run dashboard.py
```

### Acceder al Dashboard

Una vez ejecutado, abre tu navegador en:
```
http://localhost:8501
```

### Detener el Dashboard

Presiona `Ctrl + C` en la terminal donde está corriendo.

## 📊 Navegación

El dashboard tiene 6 secciones principales:

1. **🏠 Inicio** - Vista general
2. **📦 Listings & Escrow (BQ 1.x)** - Métricas de listings y escrow
3. **👥 Comportamiento (BQ 2.x)** - Eventos, clicks y tiempo en pantallas
4. **🔥 Engagement (BQ 3.x)** - DAU y sesiones
5. **💰 Revenue (BQ 4.x)** - GMV y órdenes
6. **⚡ Features (BQ 5.x)** - Uso de features específicas

## 🔧 Configuración

El dashboard se conecta automáticamente a tu backend en AWS:
```
http://3.19.208.242:8000/v1
```

Si necesitas cambiar la URL, edita el archivo `.env`:
```env
API_BASE_URL=http://tu-servidor:8000/v1
```

## 📅 Filtros de Fecha

Cada página incluye filtros con presets:
- Últimos 7 días
- Últimos 30 días
- Últimos 90 días
- Este mes
- Mes anterior
- Personalizado

## 🐛 Solución de Problemas

### Error de conexión
Si ves "Error de conexión", verifica que:
1. El backend esté corriendo
2. La URL en `.env` sea correcta
3. Tu firewall permita conexiones

### No hay datos
Si ves "No hay datos disponibles":
1. Verifica que haya datos en el backend para ese rango de fechas
2. Prueba con un rango más amplio
3. Asegúrate que la app móvil esté generando eventos

### Puerto en uso
Si el puerto 8501 está en uso:
```powershell
python -m streamlit run dashboard.py --server.port 8502
```

## 📚 Más Información

- README completo: `README.md`
- Documentación de Streamlit: https://docs.streamlit.io
- Documentación del backend: `../Backend/README.md`

## 🎯 Próximos Pasos

1. Explora cada sección del dashboard
2. Prueba los diferentes filtros de fecha
3. Exporta datos desde los expandibles
4. Personaliza los colores en `utils/config.py`

¡Disfruta visualizando tus métricas! 📊✨
