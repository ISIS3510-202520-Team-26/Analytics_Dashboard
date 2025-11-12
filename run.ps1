# Script para ejecutar el dashboard
# Uso: .\run.ps1

Write-Host "Iniciando Analytics Dashboard..." -ForegroundColor Cyan
Write-Host ""

# Verificar si el entorno virtual está activado
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Ejecutar Streamlit
Write-Host "Abriendo dashboard en el navegador..." -ForegroundColor Green
Write-Host ""
streamlit run dashboard.py
