@echo off
REM Configura aparência do terminal
REG QUERY HKCU\Console | findstr /i "VirtualTerminalLevel" >nul
if errorlevel 1 (
    REG ADD HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul
)
set PROMPT=$E[32m[webRotas]$E[0m $P$G 
title webRotas

REM Configura o alias com doskey
doskey webrotas=uv run --project "C:\ProgramData\Anatel\webRotas" "C:\ProgramData\Anatel\webRotas\src\ucli\webrota_client.py" $*
doskey limpa=D:\webRotas\src\backend\webdir\limpaTodosArquivosTemporarios.bat

REM Mensagem de confirmação
cls
echo.
echo Bem vindo ao prompt para uso do webRotas.
echo.
echo Utilize o comando 'webrotas <nome_do_arquivo>.json' para realizar o cálculo de rotas com o arquivo de configuração desejado.
echo.
echo Utilize o comando 'limpa' para limpar todos os arquivos temporários gerados pelo webRotas.
echo.