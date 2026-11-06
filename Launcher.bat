@echo off
setlocal
title Prestige Tracker - Launcher

:: Vai para a pasta do script
cd /d "%~dp0"

set "PYEXE="
set "PY_URL=https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
set "PY_LOCAL=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
set "PY_ALL=%ProgramFiles%\Python312\python.exe"

echo [1/4] Procurando Python 3.10 a 3.12...

:: Tentativa 1: py launcher
py -3.12 -c "import sys" >nul 2>&1
if %errorlevel% equ 0 for /f "delims=" %%i in ('py -3.12 -c "import sys;print(sys.executable)"') do set "PYEXE=%%i"
if defined PYEXE goto :python_found

:: Tentativa 2: python no PATH (aceita so versoes compativeis com as libs)
python -c "import sys;sys.exit(0 if (3,10)<=sys.version_info[:2]<=(3,12) else 1)" >nul 2>&1
if %errorlevel% equ 0 for /f "delims=" %%i in ('python -c "import sys;print(sys.executable)"') do set "PYEXE=%%i"
if defined PYEXE goto :python_found

:: Tentativa 3: caminhos padrao de instalacao
if exist "%PY_LOCAL%" set "PYEXE=%PY_LOCAL%"
if defined PYEXE goto :python_found
if exist "%PY_ALL%" set "PYEXE=%PY_ALL%"
if defined PYEXE goto :python_found

echo Python compativel nao encontrado. Tentando instalar via WinGet...
winget install --id Python.Python.3.12 --exact --silent --accept-source-agreements --accept-package-agreements >nul 2>nul
if exist "%PY_LOCAL%" set "PYEXE=%PY_LOCAL%"
if defined PYEXE goto :python_found
if exist "%PY_ALL%" set "PYEXE=%PY_ALL%"
if defined PYEXE goto :python_found

echo [AVISO] WinGet nao funcionou. Baixando instalador oficial do Python 3.12...
set "INSTALLER=%TEMP%\python_installer_312.exe"
curl -L -f -o "%INSTALLER%" "%PY_URL%"
if errorlevel 1 goto :erro_download
if not exist "%INSTALLER%" goto :erro_download

echo Instalando Python 3.12 para o seu usuario (aguarde)...
start /wait "" "%INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
del "%INSTALLER%" >nul 2>&1

if exist "%PY_LOCAL%" set "PYEXE=%PY_LOCAL%"
if not defined PYEXE goto :erro_instalacao

:python_found
echo Usando: %PYEXE%

echo [2/4] Verificando ambiente virtual (venv)...
if not exist "venv\Scripts\python.exe" goto :criar_venv
"venv\Scripts\python.exe" --version >nul 2>&1
if %errorlevel% equ 0 goto :venv_ok

echo [AVISO] Venv corrompida ou de outra versao do Python. Recriando...
rmdir /s /q "venv"

:criar_venv
echo Criando ambiente virtual...
"%PYEXE%" -m venv venv
if not exist "venv\Scripts\python.exe" goto :erro_venv

:venv_ok
echo [3/4] Verificando dependencias...
if not exist "requirements.txt" goto :erro_req

:: So reinstala se o requirements.txt mudou desde a ultima vez
fc /b "requirements.txt" "venv\.req_ok" >nul 2>&1
if %errorlevel% equ 0 goto :deps_ok

echo Instalando dependencias (pode demorar na primeira vez)...
"venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto :erro_pip
copy /y "requirements.txt" "venv\.req_ok" >nul

:deps_ok
echo [4/4] Iniciando Prestige Tracker...
echo --------------------------------------------------
if not exist "main.py" goto :erro_main
"venv\Scripts\python.exe" main.py
if errorlevel 1 goto :erro_run
echo --------------------------------------------------
goto :fim

:erro_download
echo [ERRO] Nao foi possivel baixar o Python. Verifique sua conexao
echo        ou instale o Python 3.12 manualmente em python.org/downloads
goto :falha

:erro_instalacao
echo [ERRO] A instalacao do Python falhou. Instale o Python 3.12
echo        manualmente em python.org/downloads (marque "Add to PATH")
echo        e abra este arquivo de novo.
goto :falha

:erro_venv
echo [ERRO] Nao foi possivel criar a pasta venv.
goto :falha

:erro_req
echo [ERRO] requirements.txt nao encontrado nesta pasta.
goto :falha

:erro_pip
echo [ERRO] Falha ao instalar as dependencias. Verifique a conexao.
goto :falha

:erro_main
echo [ERRO] main.py nao encontrado nesta pasta.
goto :falha

:erro_run
echo --------------------------------------------------
echo [ERRO] O programa fechou com erro. Leia a mensagem acima.
goto :falha

:falha
echo.
pause
exit /b 1

:fim
exit /b 0
