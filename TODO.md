# NOTAS SOBRE ENTRADAS E SAÍDAS

## Entradas

- **Polígono do Mapa**: Criar uma rotina que o defina automaticamente. (Por exemplo: os limites de latitude e longitude formam um polígono, extrapolam-se esses limites em 50 km para norte, sul, leste e oeste, e usa-se esse mapa como referência). Importante aqui é ter um cache que analise os pontos de interesse e verifique se eles estão contidos nos mapas em cache. (Implantado)
- **Polígonos de Exclusão**: Criar a possibilidade de inserir diretamente os vértices (num JSON, como é hoje) ou receber um KML com um ou mais polígonos desenhados no Google Earth, por exemplo.
- **Polígono de Interesse da Localidade**: Criar a possibilidade de passar o nome da localidade (num JSON, como é hoje) ou um KML. Verificar o formato exportado pelo Mosaico, por exemplo, com o contorno protegido (se é que isso existe).

## Saídas

- **HTML** (Já implantado)
- **KML** (Implantado)
- **Arquivo para importação em ferramentas de navegação** (Explorar compatibilidade com MapsME, MyMaps, etc.)

---

# NOTAS SOBRE O PROCESSAMENTO

## Aspectos Prioritários

1. **Definir Ponto Inicial da Rota**: Evoluir o HTML, criando um painel que apresenta a ordem de execução da rota, possibilitando definir o seu ponto inicial (por meio de um dropdown). Como a rota azul é estática e o JS do HTML offline não vai recalcular, uma opção seria criar uma "rota fechada", que começa e termina no mesmo ponto, passando por todos os outros. Exemplo:
   - `P1 > P2 > P3 > P4 > P1`
   - Se o usuário indicar `P3` como ponto inicial, a sequência seria `P3 > P4 > P1 > P2 > P3`.
   - O objetivo é garantir que o HTML continue estático e funcional, mesmo sem o servidor rodando ao fundo.
2. **Inserir Tag nos Ícones dos Pontos de Interesse**: Incluir tags como `P1`, `P2`, `P3`, etc. (Implementado e aguardando avaliação)
3. **Alterar Ícone com Proximidade**: Criar código em JS que mude o ícone dos pontos quando o veículo se aproximar deles.

## Aspectos Não Prioritários (mas importantes)

1. **Obter a Elevação dos Pontos de Interesse**: Depois de definidos os pontos de interesse que nortearão a rota, obter a elevação de cada um e usar essa informação para definir as cores dos ícones (em vez do azul estático).
2. **Métrica de Distância Mínima Aceitável**: Avaliar a inclusão de uma métrica de distância mínima aceitável entre a rota e os pontos de interesse, evitando sair das vias principais apenas para "tocar" nos pontos.
3. **Interface Gráfica**: Desenvolver uma interface para dar maior fluidez à interação com o sistema.

---

# FUNCIONALIDADES E REQUISITOS

## Notas do Lobão

- Exportar KML.
- Definir ponto de início.
- Definir sequência de execução (ordem da rota).
- Não repetir ruas.
- Incluir/excluir pontos e recalcular rota completa (azul).
- Acesso ao app a partir do navegador veicular (AndroidAuto/Screenshare).
- Descrever procedimento de carga de dados gerados para aplicações de navegação (Google Maps, etc.).
- Integrar dados de elevação do terreno (apresentação da elevação na cor do navegador).
- Pontos e polígonos baseados na elevação do terreno (identificação de pontos mais altos ou mais baixos de uma região).
- Importação de contornos protegidos de radiodifusores.
- Integração com **RF.DataHub**.
- Navegação intermunicipal.
- Para integração no **appColeta**, considerar **multiView**, permitindo acesso simultâneo do motorista e do fiscal.
- Repositório de polígonos editados por usuários.

---

# REQUISITOS ÚLTIMA REUNIÃO SEXTA PRÉ-CARNAVAL - 28/02/2025

- [x] Mudar nome da pasta de **Servers** para **src**.
- [x] Migrar **images** para **docs/images** e ajustar path do `README.md`.
- [x] Migrar arquivos de teste **Test.py**, **Test1.py** e **Test2.py** para a pasta **tests**.
- [x] Migrar arquivos de suporte ao código para uma subpasta **src/resources** (por exemplo: `src/resources/IBGE`, `src/resources/Docker`, etc.). Ajustar os paths dos arquivos que os requisitam.
- [x] Eliminar todo e qualquer experimento que não está incluído na versão atual da aplicação.

### Padronização de Arquivos de Teste

- Os arquivos de teste devem ser descritivos e começar com **`test_`**. Exemplo: `test_<funcionalidade>.py`.
- Em Python, nenhum arquivo ou pasta deve começar com letra maiúscula (isso é prática de outras linguagens).

---

# REQUISITOS ÚLTIMA REUNIÃO SEMANAL - 10/03/2025

- Ajustei nomes dos arquivos de saída.
- Modifiquei **drive-test** para **contorno**.
- Implementei as **áreas urbanizadas**, avaliar resultados e verificar a possibilidade de fazer a interseção para cortar partes fora do município.
- Criar um arquivo de **debug**.
- Segmentar arquivos para melhor organização.

