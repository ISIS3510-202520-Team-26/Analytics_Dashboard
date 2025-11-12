@echo off
echo ========================================
echo  Analytics Dashboard - Iniciando
echo ========================================
echo.

cd /d "%~dp0"

echo Ejecutando dashboard...
echo.
echo El dashboard se abrira en tu navegador en: http://localhost:8501
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python -m streamlit run dashboard.py

pause
