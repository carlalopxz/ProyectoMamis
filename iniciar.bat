@echo off
title Rincon de Familias - Buscador
echo ==============================================
echo   Iniciando Rincon de Familias...
echo ==============================================
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python -m streamlit run app.py
pause
