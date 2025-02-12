
rem call C:\Users\andre\miniconda3\condabin\conda.bat activate webrotas
rem title Webdir
rem cmd

rem Não precisa mais atualizar o path do usuario
@echo off
call "%USERPROFILE%\miniconda3\condabin\conda.bat" activate webrotas
title Webdir
cmd


rem // ngrok http 5001 