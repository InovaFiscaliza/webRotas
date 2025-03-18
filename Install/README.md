<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->

<a name="indexerd-md-top"></a>

<!-- PROJECT SHIELDS -->

<!--
*** based on https://github.com/othneildrew/Best-README-Template
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

<!-- TABLE OF CONTENTS -->

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#sobre-o-webrotas">Sobre o WebRotas</a></li>
    <li><a href="#requisitos-do-sistema">Requisitos do sistema</a></li>
    <li><a href="#instalação">Instalação</a></li>
        <ul>
            <li><a href="#1-instale-o-git">Instale o Git</a></li>
            <li><a href="#2-baixe-o-webrotas">Baixe o WebRotas</a></li>
            <li><a href="#3-instale-o-wsl">Instale o WSL</a></li>
            <li><a href="#4-instale-o-podman">Instale o Podman</a></li>
            <li><a href="#5-instale-o-uv">Instale o UV</a></li>
        </ul>
    <li><a href="#baixar-dados-de-referência">Baixar Dados de Referência</a></li>
        <ul>
            <li><a href="#1---limites-municipais-brasileiros---2023">Limites Municipais Brasileiros - 2023</a></li>
            <li><a href="#2---favelas-e-comunidades-urbanas---2022">Favelas e Comunidades Urbanas - 2022</a></li>
            <li><a href="#3---áreas-urbanizadas-do-brasil---2019">Áreas Urbanizadas do Brasil - 2019</a></li>
            <li><a href="#4---arruamento-para-cálculo-de-rotas-osm">Arruamento para cálculo de rotas OSM</a></li>
        </ul>
    <li><a href="#configuração-do-ambiente-de-trabalho">Configuração do ambiente de trabalho</a></li>
        <ul>
            <li><a href="#1--criação-do-ambiente-conda">Criação do Ambiente Conda</a></li>
            <li><a href="#2--criação-do-ambiente-podman">Criação do Ambiente Podman</a></li>
        </ul>
    <li><a href="#inicializando-o-servidor">Inicializando o Servidor</a></li>
    <li><a href="#teste-e-uso-do-webrotas">Teste e uso do WebRotas</a></li>
    <li><a href="#contribuindo">Contribuindo</a></li>
    <li><a href="#licença">Licença</a></li>
    <li><a href="#referências-adicionais">Referências adicionais</a></li>

</ol>
</details>

<!-- ABOUT -->

# Sobre Instalação do *webRotas*

Este documento descreve o processo de instalação do *webRotas* em um ambiente windows, estando dividido em duas sessões, a primeira descreve a instalação do *webRotas* para usuários finais, e a segunda descreve a instalação para desenvolvedores.

# Requisitos do sistema

- Windows 10 1709 (build 16299) ou posterior
- Conexão com a internet
- 10 GB de espaço em disco
- 16 GB de memória RAM

Vc pode verificar a versão do Windows usando o comando

```shell
winver
```

# Instalação para Todos os Usuários

## 1. Obtenha as Ferramentas de Instalação

Verifique se você possui as seguintes ferramentas instaladas:

- PowerShell 7.4 ou posterior
- WinGet 1.10 ou posterior

Abra o terminal PowerShell utilizando as teclas `Win + R` ou o menu iniciar (teclas windows) e digitando `powershell`, ou utilizando o seu aplicativo de terminal preferido:

### 1.1 Instale o **WinGet**

Verifique se dispõe do Winget digitando o comando em um terminal:

```shell
winget --version
```

Usualmente `Winget` não estará disponível até que você tenha feito login no Windows como usuário pela primeira vez, acionando o Microsoft Store para registrar o Windows Package Manager como parte de um processo assíncrono. Consulte [MS Use o WinGet tool para instalar e gerenciar aplicativos](https://learn.microsoft.com/en-us/windows/package-manager/winget/) para mais informações.

Alternativamente, winget pode ser obtido usando a seguinte sequência de comandos, conforme sugerido por [Vladan](https://stackoverflow.com/questions/74166150/install-winget-by-the-command-line-powershell#answers-header):

```shell
# get latest download url
$URL = "https://api.github.com/repos/microsoft/winget-cli/releases/latest"
$URL = (Invoke-WebRequest -Uri $URL).Content | ConvertFrom-Json | Select-Object -ExpandProperty "assets" | Where-Object "browser_download_url" -Match '.msixbundle' | Select-Object -ExpandProperty "browser_download_url"

# download
Invoke-WebRequest -UseBasicParsing -Uri $URL -OutFile "Setup.msix"

# install
Add-AppxPackage -Path "Setup.msix"

# delete file
Remove-Item "Setup.msix"
```

Outra alternativa é realizar o download do arquivo  `msixbundle` do repositório `https://github.com/microsoft/winget-cli/releases` utilizando um navegador e instalar o aplicativo clicando duas vezes sobre ele ou executando o comando `Add-AppxPackage` acima descrito, usando como argumento o caminho para o arquivo baixado.

### 1.2 Verifique a versão PowerShell

Verifique a versão PowerShell usando o comando

```shell
$PSVersionTable.PSVersion
```

PowerShell pode ser atualizado para a versão mais recente utilizando winget com o seguinte comando:

```shell
winget install Microsoft.PowerShell
```

 Para outros métodos, verifique o [procedimento de instalação do PowerShell](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-windows?view=powershell-7.5)

<div style="margin: auto; border: 1px solid darkgray; border-radius: 10px; background-color: lightgray; padding: 10px; color: black; width: 80%; align: center;">
        <strong>⚠️ IMPORTANTE</strong> <br><br>
        Todos os comandos indicados à seguir devem ser executados no terminal do <strong>PowerShell</strong><br><br>
</div>

<div align="right">
    <a href="#indexerd-md-top">
        <img src="../docs/images/up-arrow.svg" style="width: 2em; height: 2em;" title="Back to the top of this page">
    </a>
</div>

## 2. Instale o **wsl**

WSL é um recurso padrão do windows nas versões 10 2004 (build 19041) ou posterior, mas pode estar desabilitado ou não configurado corretamente.

Verifique se WSL está instalado utilizando o comando:

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

<div align="right">
    <a href="#indexerd-md-top">
        <img src="./docs/images/up-arrow.svg" style="width: 2em; height: 2em;" title="Back to the top of this page">
    </a>
</div>

## 3. Instale o **podman**

Verifique se o podman engine está instalado utilizando o comando:

```shell
podman --version
```

É esperado que esteja disponível na versão 5.4 ou superior.

Caso necessário, instale o podman engine utilizando winget

```shell
winget install RedHat.Podman
```

O processo de instalação inciará uma janela própria, que demandará a elevação do usuário para administrador.

Para facilitar o uso do podman, vc pode também instalar o podman desktop, que é uma interface gráfica para o podman engine.

No processo de instalação e para uso do *webRotas*, não se utilizará diretamente o PodmanDesktop.

Mais detalhes sobre a instalação e uso deste podem ser obtidos em: [https://podman-desktop.io/docs/installation/windows-install](https://podman-desktop.io/docs/installation/windows-install), incluindo opções para instalação via Winget e Chocolatey.

Após instalado, o sistema deverá ser reinicializado.


<div align="right">
    <a href="#indexerd-md-top">
        <img src="./docs/images/up-arrow.svg" style="width: 2em; height: 2em;" title="Back to the top of this page">
    </a>
</div>

## 5. Instale o **UV**

Instale o `uv` utilizando o comando:

```shell
winget install --id=astral-sh.uv  -e
```

https://github.com/astral-sh/uv/issues/11466

Após a instalação, com o terminal na pasta raiz do projeto *webRotas* e execute os seguintes comandos:

```shell
uv init

uv pip install https://github.com/cgohlke/geospatial-wheels/releases/download/v2025.1.20/GDAL-3.10.1-cp313-cp313-win_amd64.whl
```

Com a execução dos comandos acima, serão descarregadas as bibliotecas necessárias e configurado o ambiente python para execução do *webRotas*, o que pode levar alguns minutos.

<div align="right">
    <a href="#indexerd-md-top">
        <img src="./docs/images/up-arrow.svg" style="width: 2em; height: 2em;" title="Back to the top of this page">
    </a>
</div>


# Instalação para Usuários Finais

# Instalação para Desenvolvedores

Os passos descritos a seguir são destinados ao uso por desenvolvedores que desejam contribuir com o projeto *webRotas*.


## 1. Instale o **Git**

Verifique se o git está instalado utilizando o seguinte comando:

```shell
git --version
```

Caso negativo, instale git usando:

```shell
winget install Git.Git
```

<div align="right">
    <a href="#indexerd-md-top">
        <img src="./docs/images/up-arrow.svg" style="width: 2em; height: 2em;" title="Back to the top of this page">
    </a>
</div>

## 2. Baixe o *WebRotas*

Defina uma pasta para guardar o projeto.

De preferência escolha uma pasta que atenda aos seguintes critérios:

- fácil acesso;
- não protegida por permissões de administrador;
- não sincronizadas com serviços de nuvem como OneDrive, Google Drive, etc.

Por exemplo, crie uma pasta chamada `C:\Users\<SeuNomeDeUsuario>\github` ou se tiver um disco de dados, utilize `D:\github`, por exemplo, deixando a pasta com um caminho mais curta e de fácil acesso.

Para criar a pasta e navegar até ela, utilize os seguintes comandos:

```shell
mkdir D:\github

cd D:\github
```

Clone o repositório com o comando:

```shell
git clone https://github.com/InovaFiscaliza/webRotas.git
```

Após esse comando ser executado, será criada uma pasta chamada `webRotas` com todos os arquivos do projeto.

<div style="margin: auto; border: 1px solid darkgray; border-radius: 10px; background-color: lightgray; padding: 10px; color: black; width: 80%; align: center;">
        <strong>⚠️ IMPORTANTE</strong> <br><br>
        A pasta raiz do projeto será referenciada nos passos seguintes apenas como `.\`, referindo-se à pasta `webRotas` criada no passo anterior.
</div>

<div align="right">
    <a href="#indexerd-md-top">
        <img src="./docs/images/up-arrow.svg" style="width: 2em; height: 2em;" title="Back to the top of this page">
    </a>
</div>

