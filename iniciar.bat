@echo off
title Rincon de Familias - Buscador
echo ==============================================
echo   Iniciando Rincon de Familias...
echo ==============================================
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m streamlit run app.py
) else (
    python -m streamlit run app.py
)
pause
