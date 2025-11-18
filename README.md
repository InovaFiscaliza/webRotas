[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/InovaFiscaliza/webRotas)

# webRotas

O webRotas é uma ferramenta de gerenciamento de rotas de veículos utilizada em atividades de inspeção da ANATEL. A aplicação permite gerar rotas a partir de diferentes estratégias de distribuição de pontos de interesse:

- PONTOS: calcula rotas que passem no entorno de um conjunto de pontos sob análise, como estações de telecomunicações. Para tanto, é necessário definir explicitamente os pontos a serem visitados.
- GRID: calcula rotas no entorno de pontos regularmente distribuídos em forma de grade em uma localidade. Para tanto, é necessário indicar a localidade de interesse e se a rota deve se restringir à área urbanizada.
- CÍRCULO: calcula rotas no entorno de pontos dispostos circularmente ao redor de um ponto central. Para tanto, é necessário definir o ponto central, além do raio e do espaçamento entre os pontos.

<img width="2802" height="1872" alt="webRotas" src="https://github.com/user-attachments/assets/652c51fb-bf4d-4546-bb4d-18b0bfd44dc4" />

#### REQUISITOS
- Windows 10 1709 (build 16299) ou posterior
- PowerShell 5.1 ou posterior
- WinGet 1.10 ou posterior
- Recursos de virtualização habilitados (veja [documentação do Subsistema Linux do Windows](https://learn.microsoft.com/en-us/windows/wsl/install-manual#step-3---enable-virtual-machine-feature))
- 16GB of RAM
- 10GB de espaço livre em disco
- Conexão de internet

Devido à necessidade de uso de recurso de virtualização, esta solução usualmente não será compatível com máquinas virtuais, a menos que estas tenham sido excepcionalmente configuradas para permitir o uso de virtualização.

#### EXECUÇÃO NO AMBIENTE DO VSCODE
Caso o aplicativo seja executado diretamente no VSCODE, é necessário:  
1. Clonar o presente repositório.
2. Instalar as dependências, executando o comando a seguir.  
```
uv sync
```

3. Download do arquivo [shapefiles.zip](https://anatel365.sharepoint.com/:f:/s/InovaFiscaliza/Et9ttcdpValOquc5FpKLd0IB7U8CJa1T6ZYuPMZ68mrenw?e=FEHZWH), descompactá-lo e mover os arquivos no formato .parquet para a raiz da pasta **.\src\resources**.
4. Executa-se o arquivo **.\src\backend\webdir\server.py**, o que iniciará o servidor do webRotas.
5. Em um navegador, abre-se a url do servidor (http://127.0.0.1:5002/webRotas, por exemplo), respeitando o protocolo, endereço e porta.

Informações complementares na página de [instalação](./Install/README.md).

#### ARQUIVOS DE TESTES
Na pasta **.\tests** consta mais de 10 arquivos de testes, como:
- Requisições iniciais no formato .json ("request_circle (Rio de Janeiro-RJ).json", "request_grid (Goiânia-GO).json" e "request_shortest (RR).json", por exemplo);
- Respostas do servidor no formato .json ("webRotas_2025.08.19_T08.50.47.json").

Ambos os tipos de arquivos são importados na GUI usando o botão de importação, localizado no toolbar.

Por fim, cabe observar que na pasta **.\src\backend\webdir\logs** ficam armazenados logs para depuração.
