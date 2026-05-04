🌡️ ClimaLink — Sistema IoT de Monitoramento de Temperatura
[Mostrar Imagem](https://img.shields.io/badge/Python-3.13-3776AB?style=flat&logo=python&logoColor=white)
[Mostrar Imagem](https://img.shields.io/badge/MicroPython-ESP8266-2C2C2C?style=flat&logo=micropython&logoColor=white)
[Mostrar Imagem](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat&logo=postgresql&logoColor=white)
[Mostrar Imagem](https://img.shields.io/badge/Docker-20.10-2496ED?style=flat&logo=docker&logoColor=white)
[Mostrar Imagem](https://img.shields.io/badge/Status-Conclu%C3%ADdo-brightgreen?style=flat)
[Mostrar Imagem](https://img.shields.io/badge/License-MIT-green?style=flat)

Projeto acadêmico de Internet das Coisas (IoT) desenvolvido para a disciplina
de Ciência de Dados e IA do IESB. Sistema completo de captura, transmissão,
armazenamento e análise de dados de temperatura em tempo real usando ESP8266,
termistor NTC, PostgreSQL e Python.


📌 Índice

Sobre o Projeto
Arquitetura do Sistema
Componentes
Pipeline de Dados
Resultados
Estrutura do Repositório
Hardware Necessário
Tecnologias Utilizadas
Como Reproduzir
Análise Exploratória
Limitações e Melhorias Futuras
Autor


📋 Sobre o Projeto
O ClimaLink é um sistema de monitoramento de temperatura ambiente em tempo
real que demonstra a aplicação prática de conceitos de Internet das Coisas (IoT)
e Ciência de Dados em um contexto educacional.
Objetivos

Capturar leituras de temperatura com sensor NTC a cada 10 segundos
Alertar visualmente (LED) quando temperatura sair da faixa de conforto (20-24°C)
Transmitir dados via porta serial (USB) para computador host
Armazenar dados estruturados em banco PostgreSQL (Docker)
Analisar série temporal de 1.728 leituras coletadas

Contexto Acadêmico
Projeto desenvolvido em novembro/2025 como trabalho prático da disciplina
de Ciência de Dados e Inteligência Artificial (5º semestre) no IESB, Brasília-DF.
Demonstra conhecimentos em:

Sistemas embarcados (MicroPython no ESP8266)
Banco de dados relacional (PostgreSQL + Docker)
Pipeline ETL (Extração via serial, Transformação com regex, Load no banco)
Análise exploratória de dados (Python + pandas + matplotlib)
Modelagem de dados (schema IoT)


🏗️ Arquitetura do Sistema
┌────────────────────────────────────────────────────────────────┐
│                     CAMADA FÍSICA (HARDWARE)                   │
│  ESP8266 (NodeMCU) + Termistor NTC 10kΩ + LED + Resistores     │
│  • Leitura ADC (A0): divisor de tensão 10kΩ/NTC               │
│  • GPIO4 (D2): controle do LED de alerta                       │
│  • Intervalo: 10 segundos (configu rável via SAMPLE_INTERVAL_S) │
└──────────────────────┬─────────────────────────────────────────┘
                       │ USB Serial (115200 baud)
                       │ Formato: [UPTIME hh:mm:ss] TempC: XX.XX | LED: ON/OFF
                       ▼
┌────────────────────────────────────────────────────────────────┐
│                   CAMADA DE COLETA (ClimaLink.py)              │
│  Script Python rodando no PC host                              │
│  • Leitura da porta serial COM3 (ajustável)                   │
│  • Parsing com regex (captura timestamp, temp, status LED)     │
│  • Conexão PostgreSQL via psycopg2                             │
│  • Insert em tempo real: iot.leitura                           │
└──────────────────────┬─────────────────────────────────────────┘
                       │ psycopg2 → localhost:5432
                       ▼
┌────────────────────────────────────────────────────────────────┐
│              CAMADA DE PERSISTÊNCIA (PostgreSQL 16)            │
│  Banco rodando em container Docker                             │
│  • Schema: iot                                                  │
│  • Tabelas: leitura, alerta                                    │
│  • Índices: idx_leitura_ts, idx_leitura_device, idx_alerta_ts  │
│  • VIEW: vw_leituras_resumidas (timezone America/Sao_Paulo)    │
└──────────────────────┬─────────────────────────────────────────┘
                       │ Export CSV → Leituras.csv
                       ▼
┌────────────────────────────────────────────────────────────────┐
│          CAMADA DE ANÁLISE (AnaliseExploratoria.ipynb)         │
│  Jupyter Notebook com pandas, matplotlib, seaborn              │
│  • EDA: 1.728 leituras coletadas                              │
│  • Estatísticas descritivas                                   │
│  • Visualizações: série temporal, histograma, boxplot          │
│  • Conclusões: estabilidade térmica, ausência de falhas        │
└────────────────────────────────────────────────────────────────┘

🔧 Componentes
1. main.py — Firmware MicroPython (ESP8266)
Função: Executado no microcontrolador ESP8266, responsável por:

Leitura do ADC (termistor NTC via divisor de tensão)
Conversão da tensão para temperatura usando equação de Steinhart-Hart
Controle do LED de alerta (liga se temp < 20°C ou > 24°C)
Transmissão via serial no formato padronizado

Conceitos aplicados:

Divisor de tensão resistivo
Equação de termistores NTC: Rt=R0⋅eβ(1T−1T0)R_t = R_0 \cdot e^{\beta \left(\frac{1}{T} - \frac{1}{T_0}\right)}
Rt​=R0​⋅eβ(T1​−T0​1​)
Oversampling (média de 16 leituras) para reduzir ruído


2. ClimaLink.py — Script de Coleta (Python)
Função: Executado no PC host, responsável por:

Leitura contínua da porta serial COM3
Parsing com regex de duas linhas possíveis:

Leitura normal: [UPTIME 00:10:00] TempC: 23.41 | LED: OFF
Erro ADC: ERRO_ADC (registrado na tabela alerta)


Insert automático no banco PostgreSQL
Tratamento de exceções (serial, parsing, banco)

Decisões técnicas:

Regex compilado para eficiência
Timestamp do PC (sem NTP no ESP8266)
Autocommit ativado para persistência imediata


3. Script_DDL.sql — Modelo de Dados
Função: Criação da estrutura do banco PostgreSQL
Tabelas:
TabelaPropósitoColunas-chaveiot.leituraArmazenar todas as mediçõests, temp_c, led_on, device_idiot.alertaRegistrar eventos críticosts, temp_c, tipo (LOW/HIGH/ERROR)
Índices criados:

idx_leitura_ts — busca por intervalo temporal
idx_leitura_device — filtragem por dispositivo
idx_alerta_ts — histórico de alertas

VIEW auxiliar:

vw_leituras_resumidas — conversão automática para timezone America/Sao_Paulo


4. AnaliseExploratoria.ipynb — Análise de Dados
Função: Notebook Jupyter com análise estatística completa
Etapas executadas:

Carregamento do CSV exportado do PostgreSQL
Estatísticas descritivas (describe())
Visualizações:

Série temporal da temperatura
Histograma de distribuição
Boxplot (identificação de outliers)


Detecção de valores ausentes (resultado: 0 NaN)
Identificação de outliers (26 leituras > 24°C de 1.728 totais)


📊 Pipeline de Dados
ESP8266 (MicroPython)
  ↓ Serial USB 115200 baud
ClimaLink.py (Regex + psycopg2)
  ↓ INSERT INTO iot.leitura
PostgreSQL 16 (Docker)
  ↓ COPY TO CSV
Leituras.csv
  ↓ pd.read_csv()
AnaliseExploratoria.ipynb
  ↓ Visualizações
Conclusões + Apresentação
Formato da linha serial:
[UPTIME 00:15:30] TempC: 22.85 | LED: OFF
Regex de captura:
pythonr'\[(?P<ts>.+?)\]\s*TempC:\s*(?P<temp>[-\d\.]+)\s*\|\s*LED:\s*(?P<led>ON|OFF)'

📈 Resultados
Estatísticas Descritivas (1.728 leituras)
MétricaValorTemperatura Média22,85°CDesvio Padrão0,51°CTemperatura Mínima21,47°CTemperatura Máxima27,26°CMediana (Q2)22,82°CLeituras fora da faixa de conforto26 (1,5%)Valores ausentes0
Insights

✅ Estabilidade térmica: baixo desvio padrão (0,51°C) indica ambiente
controlado
✅ Ausência de falhas: 0 valores NaN em 1.728 leituras (pipeline confiável)
✅ Outliers mínimos: apenas 1,5% das leituras fora da faixa de conforto
✅ Consistência: temperatura permaneceu majoritariamente entre 22-24°C

Conclusão da Análise

"As leituras coletadas pelo ESP8266, enviadas via porta USB para o PowerShell
e posteriormente armazenadas no banco de dados PostgreSQL por meio de um script
Python, forneceram uma série temporal estável e consistente. (...) Esses
resultados demonstram que tanto o hardware quanto o pipeline de coleta,
transmissão e armazenamento funcionaram corretamente, gerando dados confiáveis
para as etapas seguintes do projeto."


📁 Estrutura do Repositório
climalink/
│
├── 📂 hardware/
│   └── main.py                      # Firmware MicroPython (ESP8266)
│
├── 📂 scripts/
│   ├── ClimaLink.py                 # Script de coleta (porta serial → PostgreSQL)
│   └── Script_DDL.sql               # Modelo de dados (schema + tabelas + índices)
│
├── 📂 data/
│   └── Leituras.csv                 # Export de 1.728 leituras coletadas
│
├── 📂 notebooks/
│   └── AnaliseExploratoria.ipynb    # Jupyter: EDA + visualizações
│
├── 📂 docs/
│   └── Apresentação.pptx            # Slide deck do projeto (contexto acadêmico)
│
├── .gitignore
├── requirements.txt                 # Dependências Python
├── README.md
└── LICENSE

🛠️ Hardware Necessário
ComponenteEspecificaçãoQuantidadeMicrocontroladorESP8266 (NodeMCU)1TermistorNTC 10kΩ @ 25°C (β=3950)1Resistor fixo10kΩ (divisor de tensão)1LEDQualquer cor (5mm)1Resistor limitador220Ω (para o LED)1Cabo USBMicro USB (dados + alimentação)1Protoboard400 pontos (opcional)1JumpersMacho-macho~5
Diagrama de Conexão
3V3 ──┬── 10kΩ ──┬── NTC ── GND
      │          │
      │          └── A0 (ADC)
      │
      └── GPIO4 ── LED(+) ── LED(-) ── 220Ω ── GND
Observações:

NTC: resistência diminui com aumento de temperatura
Divisor: quando NTC esquenta, tensão em A0 aumenta
ADC: resolução 10 bits (0-1023) mapeado para 0-3.3V


💻 Tecnologias Utilizadas
CategoriaTecnologiaVersãoMicrocontroladorMicroPython1.20+LinguagemPython3.13Banco de DadosPostgreSQL16ContainerizaçãoDocker20.10+ComunicaçãopySerial3.5Driver PostgreSQLpsycopg2-binary2.9.9Análise de Dadospandas2.xVisualizaçãomatplotlib, seaborn3.xAmbienteJupyter Notebook—

🚀 Como Reproduzir
Pré-requisitos

Docker instalado (para PostgreSQL)
Python 3.13+ instalado
ESP8266 com MicroPython flashado
Thonny IDE ou similar (upload de main.py)

1. Clone o repositório
bashgit clone https://github.com/seu-usuario/climalink.git
cd climalink
2. Suba o banco PostgreSQL
bashdocker run --name postgres-climalink \
  -e POSTGRES_PASSWORD=senha123 \
  -e POSTGRES_DB=climalink \
  -p 5432:5432 \
  -d postgres:16
3. Crie a estrutura do banco
bashdocker exec -i postgres-climalink psql -U postgres -d climalink < scripts/Script_DDL.sql
4. Instale dependências Python
bashpip install -r requirements.txt
5. Carregue o firmware no ESP8266

Conecte o ESP8266 via USB
Abra o Thonny IDE
Configure: MicroPython (ESP8266)
Faça upload do arquivo hardware/main.py
Execute no ESP8266

6. Execute o script de coleta
bash# Ajuste a porta COM em ClimaLink.py (linha 12)
# Windows: "COM3", Linux: "/dev/ttyUSB0", macOS: "/dev/cu.usbserial"

python scripts/ClimaLink.py
Saída esperada:
🔗 Conectando ao PostgreSQL…
✅ Conectado ao banco: climalink
🧠 Aguardando dados na porta COM3 (115200 baud)…
📥 Inserido: 2025-11-14 11:20:48 | TempC=23.12°C | LED=OFF
📥 Inserido: 2025-11-14 11:20:58 | TempC=23.29°C | LED=OFF
...
7. Exporte os dados
bashdocker exec -i postgres-climalink psql -U postgres -d climalink -c \
  "COPY (SELECT id, ts, temp_c, led_on FROM iot.leitura ORDER BY ts DESC) 
   TO STDOUT WITH CSV HEADER" > data/Leituras.csv
8. Execute a análise
bashjupyter notebook notebooks/AnaliseExploratoria.ipynb

📊 Análise Exploratória
Visualizações Geradas
1. Série Temporal

Temperatura ao longo do tempo
Identificação de variações naturais do ambiente

2. Histograma

Distribuição de frequência das temperaturas
Concentração entre 22-24°C

3. Boxplot

Identificação visual de outliers
Q1, mediana, Q3 claramente definidos

Código de Exemplo
pythonimport pandas as pd
import matplotlib.pyplot as plt

# Carregar dados
df = pd.read_csv('data/Leituras.csv')

# Série temporal
plt.figure(figsize=(14, 6))
plt.plot(df['ts'], df['temp_c'], linewidth=0.8)
plt.axhline(20, color='blue', linestyle='--', label='Limite Inferior')
plt.axhline(24, color='red', linestyle='--', label='Limite Superior')
plt.title('Série Temporal de Temperatura - ClimaLink')
plt.xlabel('Timestamp')
plt.ylabel('Temperatura (°C)')
plt.legend()
plt.grid(alpha=0.3)
plt.show()

⚠️ Limitações e Melhorias Futuras
Limitações Identificadas

Timestamp: ESP8266 não sincroniza NTP — timestamp é do PC host
Comunicação: dependente de cabo USB (sem Wi-Fi implementado)
Alerta: apenas visual (LED) — sem notificação remota
Intervalo: 10s fixo — não configurável em runtime

Melhorias Propostas
MelhoriaTecnologia SugeridaImpactoSincronização NTPntptime MicroPythonTimestamp real no ESP8266Transmissão Wi-FiMQTT (broker Mosquitto)Sem dependência de caboDashboard em tempo realGrafana + TimescaleDBVisualização liveConfiguração remotaAPI REST (Flask/FastAPI)Ajuste de parâmetros via webMulti-sensoresDHT22 (temp + umidade)Dados complementaresArmazenamento localSD Card no ESP8266Backup offline

👤 Autor
Lucas Coutinho Boros
Estudante de Ciência de Dados e IA (5º semestre) no IESB, Brasília-DF.
Desenvolvedor com experiência em Python, SQL, Power BI e Machine Learning.
[Mostrar Imagem](https://www.linkedin.com/in/lucas-coutinho-boros)
[Mostrar Imagem](https://github.com/Lucas-Coutinhob)

📝 Licença
Este projeto está sob a licença MIT. Consulte o arquivo LICENSE para mais detalhes.

🙏 Agradecimentos

IESB — Instituto de Educação Superior de Brasília
Disciplina: Ciência de Dados e Inteligência Artificial (5º Semestre)
MicroPython Community — documentação e exemplos
PostgreSQL — banco de dados robusto e confiável


Projeto desenvolvido em novembro/2025 como trabalho acadêmico.
Dados coletados: 14/nov/2025 | 1.728 leituras em ~4,8 horas contínuas.