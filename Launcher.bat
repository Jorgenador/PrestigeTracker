@echo off
title Inicializador Python Seguro

:: Força ir para a pasta do script
cd /d "%~dp0"

echo [1/4] Checando Python global...
python --version >nul 2>&1
if %errorlevel% equ 0 goto :python_found

echo Python nao instalado, tentando instalar via WinGet...
winget install --id Python.Python.3.12 --exact --silent --accept-source-agreements --accept-package-agreements >nul 2>nul
if %errorlevel% equ 0 goto :python_refresh

echo [AVISO] WinGet falhou. Tentando baixar instalador oficial...
set "PYTHON_URL=https://python.org"
set "INSTALLER_NAME=python_installer.exe"

curl -L -o "%INSTALLER_NAME%" "%PYTHON_URL%"
if not exist "%INSTALLER_NAME%" goto :erro_download

echo Instalando Python silenciosamente (Aguarde...).
start /wait "" "%INSTALLER_NAME%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
del "%INSTALLER_NAME%"

:python_refresh
echo Atualizando caminhos do sistema...
set "PATH=%PATH%;%USERPROFILE%\AppData\Local\Programs\Python\Python312;C:\Program Files\Python312"

:python_found
echo [2/4] Verificando integridade da Venv...

:: Se a venv existe, testa se ela responde. Se nao responder, deleta.
if not exist "venv\Scripts\python.exe" goto :criar_venv
"venv\Scripts\python.exe" --version >nul 2>&1
if %errorlevel% equ 0 goto :venv_ok

echo [AVISO] Venv corrompida ou antiga detectada. Removendo...
rmdir /s /q "venv"

:criar_venv
echo Criando novo Ambiente Virtual (venv)...
python -m venv venv
if not exist "venv\Scripts\python.exe" goto :erro_venv

:venv_ok
echo [3/4] Atualizando dependencias (Pip / Requirements)...
"venv\Scripts\python.exe" -m pip install --upgrade pip -q

if not exist "requirements.txt" echo [AVISO] requirements.txt nao encontrado. Pulando pacotes.
if exist "requirements.txt" "venv\Scripts\python.exe" -m pip install -r requirements.txt

echo [4/4] Executando main.py...
echo --------------------------------------------------
if exist "main.py" "venv\Scripts\python.exe" main.py
if not exist "main.py" echo [ERRO] O arquivo main.py nao foi encontrado nesta pasta!
echo --------------------------------------------------
goto :end

:erro_download
echo [ERRO] Nao foi possivel baixar o Python. Verifique sua conexao.
goto :end

:erro_venv
echo [ERRO] Falha critica ao tentar criar a pasta venv.
goto :end

:end
echo.
echo Processo finalizado.
pause