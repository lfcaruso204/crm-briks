@echo off
title Iniciando Streamlit - RICEX CRM

:: 1. Entra na pasta do seu projeto
cd /d "C:\Users\Luca Caruso\Desktop\Projetos\Case Ricex\RICEX_CRM_CARTOES\CRM_App"

:: 2. Ativa o ambiente 'base' usando o caminho correto do seu Anaconda
call "C:\Anaconda\Scripts\activate.bat" "C:\Anaconda"

:: 3. Executa o streamlit explicitamente pelo Python do ambiente atualizado
python -m streamlit run app.py
pause
