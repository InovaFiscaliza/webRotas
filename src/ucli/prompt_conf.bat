echo off
REM Definição de variáveis de ambiente
cd ..\..
set WEBROTAS_HOME=%CD%
cd src\ucli

REM Configura aparência do terminal
REG QUERY HKCU\Console | findstr /i "VirtualTerminalLevel" >nul
if errorlevel 1 (
    REG ADD HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul
)
set PROMPT=$E[32m[webRotas]$E[0m $P$G 
title webRotas

REM Configura o alias com doskey
doskey webrotas=uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" $*
doskey exemplos=copy "%WEBROTAS_HOME%\tests\*.json" .
doskey limpa="%WEBROTAS_HOME%\src\ucli\limpa.bat"
doskey ajuda=type "%WEBROTAS_HOME%\src\ucli\mensagens.txt"

REM Configura a página de código para UTF-8
chcp 65001 >nul

REM Apresenta splash screen
cls
echo.
echo Bem vindo ao prompt para uso do webRotas.
type mensagens.txt

REM Leva usuário ao diretório padrão
cd /D %USERPROFILE%
