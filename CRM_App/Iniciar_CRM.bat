@echo off
cd /d "%~dp0"

if not exist venv (
    echo Criando ambiente virtual, aguarde...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

if not exist crm.db (
    echo Criando banco de dados a partir do Excel...
    python migrate.py
)

streamlit run app.py

pause
