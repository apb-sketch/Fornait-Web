@echo off
setlocal

where bun.exe >nul 2>&1
if errorlevel 1 (
    echo Bun no esta disponible en PATH. Instala Bun y vuelve a abrir este archivo.
    pause
    exit /b 1
)

pushd "%~dp0"
if errorlevel 1 (
    echo No se pudo abrir la carpeta de PlayCanvas.
    pause
    exit /b 1
)

bun.exe install
if errorlevel 1 goto install_error

bun.exe run dev
set "dev_exit=%errorlevel%"
popd
if not "%dev_exit%"=="0" pause
exit /b %dev_exit%

:install_error
set "install_exit=%errorlevel%"
popd
echo Fallo bun install. El servidor de desarrollo no se ha iniciado.
pause
exit /b %install_exit%
