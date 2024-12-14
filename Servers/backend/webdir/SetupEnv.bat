
@echo off

:: Verificar se Conda está instalado
call conda --version > nul 2>&1
if errorlevel 1 (
    echo Conda não está instalado ou configurado no PATH.
    exit /b 1
)

echo Conda está instalado.

:: Verificar a existência do ambiente "webrotas"
set "ENV_NAME=webrotaszz"
set "ENV_FOUND=0"

for /f "delims=" %%i in ('call conda env list') do (
    echo %%i | find "%ENV_NAME%" > nul
    if not errorlevel 1 (
        set "ENV_FOUND=1"
        goto :env_exists
    )
)

:: Criar o ambiente caso ele não exista
echo O ambiente "%ENV_NAME%" não existe. Criando agora...
call conda env create -f environment.yml
if errorlevel 1 (
    echo Erro ao criar o ambiente.
    exit /b 1
)
echo Ambiente criado com sucesso.
exit /b 0

:env_exists
echo O ambiente "%ENV_NAME%" já existe. Nenhuma ação necessária.
exit /b 0



