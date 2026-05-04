-- ==============================
-- Projeto: ClimaLink (Lucas)
-- Banco: PostgreSQL 16 (Docker)
-- Descrição: Estrutura base para armazenamento das leituras de temperatura e alertas
-- ==============================

-- 1️⃣ Criar schema
CREATE SCHEMA IF NOT EXISTS iot AUTHORIZATION postgres;

COMMENT ON SCHEMA iot IS 'Schema de dados do projeto ClimaLink (Internet das Coisas).';

-- 2️⃣ Tabela principal de leituras
CREATE TABLE IF NOT EXISTS iot.leitura (
    id          BIGSERIAL PRIMARY KEY,
    ts          TIMESTAMPTZ NOT NULL DEFAULT NOW(),     -- timestamp da leitura (UTC)
    temp_c      NUMERIC(6,3),                           -- temperatura em °C
    led_on      BOOLEAN NOT NULL,                       -- estado do LED (True=Alerta ON)
    raw_adc     SMALLINT,                               -- leitura bruta do ADC (0–1023)
    v_volts     REAL,                                   -- tensão calculada em volts
    rt_kohm     REAL,                                   -- resistência do termistor em kΩ
    device_id   TEXT NOT NULL DEFAULT 'esp8266-d2',     -- identificador do dispositivo
    source      TEXT NOT NULL DEFAULT 'serial'          -- origem da leitura: serial/http/mqtt
);

COMMENT ON TABLE iot.leitura IS 'Armazena as leituras de temperatura captadas pelo termistor do ClimaLink.';
COMMENT ON COLUMN iot.leitura.ts IS 'Data/hora da leitura, em UTC.';
COMMENT ON COLUMN iot.leitura.temp_c IS 'Temperatura medida em graus Celsius.';
COMMENT ON COLUMN iot.leitura.led_on IS 'Indica se o LED de alerta estava aceso (fora da faixa de conforto).';

-- 3️⃣ Tabela de alertas
CREATE TABLE IF NOT EXISTS iot.alerta (
    id          BIGSERIAL PRIMARY KEY,
    ts          TIMESTAMPTZ NOT NULL DEFAULT NOW(),     -- timestamp do evento
    temp_c      NUMERIC(6,3),                           -- temperatura no momento do alerta
    tipo        TEXT NOT NULL CHECK (tipo IN ('LOW','HIGH','ERROR')),  -- tipo do alerta
    min_c       NUMERIC(6,3) NOT NULL DEFAULT 20.0,     -- limite inferior da faixa de conforto
    max_c       NUMERIC(6,3) NOT NULL DEFAULT 24.0,     -- limite superior da faixa de conforto
    device_id   TEXT NOT NULL DEFAULT 'esp8266-d2'      -- dispositivo que gerou o alerta
);

COMMENT ON TABLE iot.alerta IS 'Registra eventos de temperatura fora da faixa de conforto ou erros de leitura.';

-- 4️⃣ Índices
CREATE INDEX IF NOT EXISTS idx_leitura_ts      ON iot.leitura (ts DESC);
CREATE INDEX IF NOT EXISTS idx_leitura_device  ON iot.leitura (device_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_alerta_ts       ON iot.alerta (ts DESC);

-- 5️⃣ Visualização rápida (opcional)
-- Cria uma VIEW consolidando leituras e status
CREATE OR REPLACE VIEW iot.vw_leituras_resumidas AS
SELECT 
    id,
    ts AT TIME ZONE 'America/Sao_Paulo' AS data_hora_local,
    temp_c,
    CASE 
        WHEN led_on THEN 'Fora da faixa' 
        ELSE 'Normal' 
    END AS status_led
FROM iot.leitura
ORDER BY ts DESC;

COMMENT ON VIEW iot.vw_leituras_resumidas IS 'Resumo das leituras com hora local e status de alerta.';

-- 6️⃣ Teste rápido (verificação)
SELECT '✅ Estrutura ClimaLink criada com sucesso!' AS status;
