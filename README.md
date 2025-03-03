# webRotas

Kit de ferramentas para gerenciamento de rotas de veículos, para atividades de inspeção da Agência Nacional de Telecomunicações do Brasil, Anatel.

<p align="center">
  <img src="images/pntsVisita.jpg" width="200" style="margin-right: 10px;">
  <img src="images/drvTest.jpg" width="200" style="margin-right: 10px;">
  <img src="images/abrangencia.jpg" width="200">
</p>

## Requisitos do sistema

- Windows 10 1709 (build 16299) ou posterior
- PowerShell 7.4 ou posterior
- WinGet 1.10 ou posterior
  
- 8GB of RAM
- 10GB de espaço livre em disco
  
- Conexão de internet

## Verificaçao do ambiente

    Verifique a versão do Windows usando o comando

    ```shell
    winver
    ```

    Verifique se dispõe do Winget digitando o comando:

    ```shell
    winget --version
    ```

   `Winget` não estará disponível até que você tenha feito login no Windows como usuário pela primeira vez, acionando o Microsoft Store para registrar o Windows Package Manager como parte de um processo assíncrono. Consulte [MS Use o WinGet tool para instalar e gerenciar aplicativos](https://learn.microsoft.com/en-us/windows/package-manager/winget/) para mais informações.

    Verifique a versão PowerShell usando o comando
    
    ```shell
    $PSVersionTable.PSVersion
    ```

    PowerShell pode ser atualizado para a versão mais recente utilizando o seguinte comando ou por métodos alternativos conforme [procedimeento de instalação do PowerShell](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-windows?view=powershell-7.5)

    ```shell
    winget install Microsoft.PowerShell
    ```

## Instalação

1. Verifique se o Git está instalado

   Abra o Prompt de Comando (cmd) ou PowerShell e digite:

    ```shell
    git --version
    ```

   Caso negativo, instale usando:

    ```shell
    winget install Git.Git
    ```

2. Clonar o repositório

   Utilize uma pasta para salvar o projeto. De preferência escolha uma pasta que atenda aos seguintes critérios:

   - fácil acesso;
   - não protegida por permissões de administrador;
   - não sincronizadas com serviços de nuvem.

    Por exemplo, crie uma pasta chamada `C:\Users\<SeuNomeDeUsuario>\anatel`
    
    Utilizando os seguintes comandos para criar a pasta e navegar até ela:

    ```shell
    mkdir C:\Users\<SeuNomeDeUsuario>\appdata\Local\anatel

    cd C:\Users\<SeuNomeDeUsuario>\appdata\Local\anatel
    ```

    Clone o repositório com o comando:

    ```shell
    git clone https://github.com/InovaFiscaliza/webRotas.git
    ```

    Após esse comando, será criada uma pasta chamada `webRotas` com todos os arquivos do projeto.

    A pasta raiz escolhida para o projeto será referenciada nos passos seguintes apenas como `.\webRotas`

3. Instalar o wsl

    Verifique se WSL está instalado utiliz

    ```shell
    wsl.exe --version
    ```

    Caso não esteja instalado, execute:

    ```shell
    wsl.exe --install
    ```

   Em alguns sistemas, pode ser necessário habilitar o recurso de máquina virtual. Neste site, você encontrará mais detalhes na [documentação do Subsistema Linux do Windows](dhttps://learn.microsoft.com/en-us/windows/wsl/install-manual#step-3---enable-virtual-machine-feature)

   O procedimento pode variar dependendo do modelo da BIOS e do tipo de CPU.

   Em algumas máquinas, pode ser necessário habilitar a opção manualmente. Outra alternativa é abrir o PowerShell como administrador e executar o seguinte comando:

    ```shell
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
    ```

    Feitas essa operações, repita a instalação do wsl com o comando `wsl.exe --install`

4. Baixar o podman engine

    Instale o podman engine utilizando winget
    
    ```shell
    winget install RedHat.Podman
    ```

    Para facilitar o uso do podman, vc pode também instalar o podman desktop, que é uma interface gráfica para o podman engine.

    ```shell	
    winget install RedHat.PodmanDesktop
    ```

    Utilize a opção: `docker-compose with Podman, enable docker compatibility` quando solicitado.

    Após instalado, o sistema deverá ser reinicializado.

5. Baixar e instalar o python

    ```shell
    winget install miniconda3
    ```

    Após a instalação, abra o Anaconda Prompt e execute o comando:

    ```shell
    conda init
    ```

    Feche o terminal de comando e abra novamente.

6. Configure seu ambiente de trabalho

    Crie o ambiente de trabalho com o comando:

    ```shell
    conda env create -f https://raw.githubusercontent.com/InovaFiscaliza/webRotas/refs/heads/main/Servers/backend/webdir/environment.yaml
    ```

    Ative o ambiente de trabalho com o comando:

    ```shell
    conda activate webRotas
    ```

    Verifique se o caminho onde o ambiente criado usando o comando:

    ```shell
    conda env list
    ```

7.  Baixar os arquivos de dados

    * Dados de **limites municipais** com a seguinte sequência de comandos:

        ```shell
        cd .\webRotas\Servers\BR_Municipios #! Ajustar diretório para versão 2023
        
        Invoke-WebRequest -OutFile Invoke-WebRequest -OutFile BR_Municipios_2023.zip -Uri https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2023/Brasil/BR_Municipios_2023.zip
        
        Expand-Archive -LiteralPath BR_Municipios_2023.zip -DestinationPath .\

        rm BR_Municipios_2023.zip
        ```

    * Dados de [**Favelas e Comunidades Urbanas - 2022**](https://inde.gov.br/AreaDownload#) com a seguinte sequência de comandos:

        ```shell
        cd .\webRotas\Servers\Comunidades

        Invoke-WebRequest -OutFile qg_2022_670_fcu_agreg.zip -Uri https://geoservicos.ibge.gov.br/geoserver/CGMAT/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=CGMAT:qg_2022_670_fcu_agreg&outputFormat=SHAPE-ZIP

        Expand-Archive -LiteralPath qg_2022_670_fcu_agreg.zip -DestinationPath .\

        rm qg_2022_670_fcu_agreg.zip
        ```

    * Dados de [**Áreas Urbanizadas do Brasil - 2019**](https://inde.gov.br/AreaDownload#) com a seguinte sequência de comandos:

        ```shell
        cd .\webRotas\Servers\Urbanizacao

        Invoke-WebRequest -OutFile areas_urbanizadas_2019.zip -Uri https://geoservicos.ibge.gov.br/geoserver/CGEO/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=CGEO:AU_2022_AreasUrbanizadas2019_Brasil&outputFormat=SHAPE-ZIP

        Expand-Archive -LiteralPath areas_urbanizadas_2019.zip -DestinationPath .\

        rm areas_urbanizadas_2019.zip
        ```

   * Dados de [**Arrumento**](https://download.geofabrik.de/south-america/brazil.html) com a seguinte sequência de comandos:

        ```shell
        cd .\webRotas\Servers\Osmosis\brazil

        Invoke-WebRequest -OutFile brazil-latest.osm.pbf -Uri https://download.geofabrik.de/south-america/brazil-latest.osm.pbf

        ```

    * Imagens de containeres a serem utilizados [**osmosis**](https://github.com/yagajs/docker-osmosis) e [**osrm-backend**](https://github.com/Project-OSRM/osrm-backend) com a seguinte sequência de comandos:

        ```shell
        podman pull yagajs/osmosis

        podman pull osrm/osrm-backend
        ```


8. Preparar pastas e imagem do container para o Osmosis

    ```shell
    cd .\webRotas\Servers\Osmosis

    mkdir TempData

    mkdir brazil

    podman run --name osmr -v .:/data osrm/osrm-backend

    podman commit osmr osmr_webrota

    podman save -o osmr_webrota.tar osmr_webrota
    ```	

    Tendo sido realizadas todas as operações, deve ser possível visualizar cópia da imagem do container `osmosis_webrota.tar` no diretório `.\webRotas\Servers\Osmosis`.

9. Preparar pastas e imagem do container para o OSRM

    ```shell
    cd .\webRotas\Servers\OSRM

    mkdir TempData

    podman run --name osmr -v .:/data osrm/osrm-backend

    podman commit osmr osmr_webrota

    podman save -o osmr_webrota.tar osmr_webrota
    ```

    Tendo sido realizadas todas as operações, deve ser possível visualizar cópia da imagem do container `osmr_webrota.tar` no diretório `.\webRotas\Servers\OSRM`.

10. Preparar pastas e arquivos para o servidor

    ```shell
    cd .\webRotas\Servers\backend\webdir
    
    mkdir logs
    
    mkdir templates
    ```

11. Testar a execução do sistema

    Clique no arquivo C:\Users\SeuNomeDeUsuario\webRotas\Servers\backend\webdir\promptwork.bat por duas vezes e abra dois prompts de trabalho.

    Verifique no Podman Desktop se o podman está executando, Olhe nas ultimas linhas do Dashboard e verifique se ele está com o status RUNNING.

    No primeiro prompt digite python Server.py para executar o servidor python.

    No segundo prompt digite python Test2.py para executar um testa de execução do sistema.

    Ao fim da execução do script Test2.py ele mostrará a resposta json do server e se for posível abrirá uma janela web com a resposta
    em html.

    Importante, durante o desenvolvimento pode ocorrer de o sistema falhar no meio de uma criação de indices, mapa ou outros eventos diversos. Para limpar todos arquivos de cache ou temporários do sistema e reiniciar seu estado, execute o script \webRotas\Servers\backend\webdir\LimpaTodosArquivosTemporarios.bat.

    No diretório \webRotas\Servers\backend\webdir\logs você encontra os logs de depuração, uma parte destes logs você vê na tela do python Server.py, mas alguns detalhes na execução dos container estão nesse log.

    Outra opção para depurar os containers é usar o Podman Desktop. Na interface, você pode visualizar a lista de containers em execução, clicar sobre um deles e acessar suas telas de saída e logs.
