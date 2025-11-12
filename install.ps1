# Script de instalación rápida para Windows
# Ejecutar: .\install.ps1

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Analytics Dashboard - Instalación" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "1. Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ $pythonVersion instalado" -ForegroundColor Green
} else {
    Write-Host "   ✗ Python no encontrado" -ForegroundColor Red
    Write-Host "   Descarga Python desde: https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Crear entorno virtual
Write-Host "2. Creando entorno virtual..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "   ⚠ Entorno virtual ya existe, omitiendo..." -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "   ✓ Entorno virtual creado" -ForegroundColor Green
}

Write-Host ""

# Activar entorno virtual
Write-Host "3. Activando entorno virtual..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
Write-Host "   ✓ Entorno activado" -ForegroundColor Green

Write-Host ""

# Instalar dependencias
Write-Host "4. Instalando dependencias..." -ForegroundColor Yellow
python -m pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Dependencias instaladas" -ForegroundColor Green
} else {
    Write-Host "   ✗ Error instalando dependencias" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "✓ Instalación completada!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para ejecutar el dashboard:" -ForegroundColor Yellow
Write-Host "  streamlit run dashboard.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para activar el entorno virtual en el futuro:" -ForegroundColor Yellow
Write-Host "  venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host ""
