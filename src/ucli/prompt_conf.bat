echo off
REM Definição de variáveis de ambiente
rem set WEBROTAS_HOME=C:\ProgramData\Anatel\webRotas
set WEBROTAS_HOME=D:\NetbeansProjects\webRotas

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
doskey ajuda=cat "%WEBROTAS_HOME%\src\ucli\mensagens.txt"

REM Configura a página de código para UTF-8
chcp 65001 >nul

REM Apresenta splash screen
cls
echo.
echo Bem vindo ao prompt para uso do webRotas.
type mensagens.txt

REM Leva usuário ao diretório padrão
cd /D %USERPROFILE%
