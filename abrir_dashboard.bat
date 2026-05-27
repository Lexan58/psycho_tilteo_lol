@echo off
title Tilteo Coach

cd /d "D:\Python\psycho_tilteo_lol"

echo Iniciando dashboard mental...
echo.

venv\Scripts\python.exe -m streamlit run dashboard.py

pause