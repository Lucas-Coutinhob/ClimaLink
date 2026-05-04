import re
import time
import serial
import psycopg2
from datetime import datetime

# ---------------------------
# CONFIGURAÇÕES
# ---------------------------

# Porta COM do ESP8266 (ajuste conforme o Gerenciador de Dispositivos)
PORTA = "COM3"           # exemplo: "COM5"
BAUD  = 115200

# Banco PostgreSQL (Docker)
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "climalink"
DB_USER = "postgres"
DB_PASS = "senha123"

DEVICE_ID = "esp8266-d2"

# ---------------------------
# REGEX (linhas do ESP)
# ---------------------------

# Ex.: [UPTIME 00:10:00] TempC: 23.41 | LED: OFF
# ou   [2025-11-11 10:56:00] TempC: 23.41 | LED: OFF  (se um dia usar NTP)
RX_NORMAL = re.compile(
    r'\[(?P<ts>.+?)\]\s*TempC:\s*(?P<temp>[-\d\.]+)\s*\|\s*LED:\s*(?P<led>ON|OFF)',
    re.IGNORECASE
)
RX_ERROR = re.compile(r'ERRO_ADC', re.IGNORECASE)

def main():
    print("🔗 Conectando ao PostgreSQL…")
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )
    conn.autocommit = True
    cur = conn.cursor()
    print("✅ Conectado ao banco:", DB_NAME)

    print(f"🧠 Aguardando dados na porta {PORTA} ({BAUD} baud)…")
    with serial.Serial(PORTA, BAUD, timeout=1) as ser:
        while True:
            try:
                line = ser.readline().decode(errors='ignore').strip()
                if not line:
                    time.sleep(0.05)
                    continue

                m = RX_NORMAL.search(line)
                if m:
                    ts_txt = m.group('ts')
                    temp = float(m.group('temp'))
                    led_on = (m.group('led').upper() == 'ON')

                    # Se vier UPTIME (sem NTP), usa hora local do PC
                    if ts_txt.upper().startswith("UPTIME"):
                        ts = datetime.now()
                    else:
                        ts = datetime.fromisoformat(ts_txt)

                    cur.execute("""
                        INSERT INTO iot.leitura (ts, temp_c, led_on, source, device_id)
                        VALUES (%s, %s, %s, 'serial', %s);
                    """, (ts, temp, led_on, DEVICE_ID))

                    print(f"📥 Inserido: {ts} | TempC={temp:.2f}°C | LED={'ON' if led_on else 'OFF'}")

                elif RX_ERROR.search(line):
                    cur.execute("""
                        INSERT INTO iot.alerta (temp_c, tipo, device_id)
                        VALUES (%s, %s, %s);
                    """, (None, 'ERROR', DEVICE_ID))
                    print("⚠️ Erro ADC registrado no banco.")

                else:
                    # linha fora do padrão -> ignora silenciosamente
                    pass

            except KeyboardInterrupt:
                print("\n🛑 Interrompido pelo usuário (Ctrl+C).")
                break
            except Exception as e:
                print("❌ Erro de parsing/insert:", e)
                time.sleep(0.2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário (Ctrl+C).")
    except serial.SerialException as se:
        print("❌ Erro serial:", se)
    except Exception as e:
        print("❌ Erro geral:", e)
