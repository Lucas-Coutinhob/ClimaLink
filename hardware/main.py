# ClimaLink – ESP8266 (sem NTP), leitura a cada 5 min
# Montagem:
# - Divisor NTC: 3V3 -> 10k -> nó -> NTC -> GND ; A0 no nó
# - LED externo: GPIO4 -> Ânodo(LED) ; Cátodo(LED) -> 220Ω -> GND

from machine import Pin, ADC
import time, math

# -------- Config --------
SAMPLE_INTERVAL_S = 5 * 60   # 5 minutos
TMIN, TMAX = 20.0, 24.0      # °C (faixa de conforto)

# -------- Hardware --------
adc = ADC(0)                 # A0 (0..1023)
led = Pin(4, Pin.OUT)        # GPIO4 (D2)

# -------- Termistor --------
VCC     = 3.3
R_FIXED = 10.0               # kΩ
R0      = 10.0               # kΩ @25°C
BETA    = 3950.0
T0K     = 273.15 + 25.0

_boot_ticks = time.ticks_ms()

def now_uptime_str():
    # Sem NTP: imprimimos UPTIME hh:mm:ss
    ms = time.ticks_diff(time.ticks_ms(), _boot_ticks)
    s  = ms // 1000
    h  = (s // 3600) % 24
    m  = (s % 3600) // 60
    ss = s % 60
    return f"UPTIME {h:02d}:{m:02d}:{ss:02d}"

def adc_media(n=16, us=300):
    s = 0
    for _ in range(n):
        s += adc.read()
        time.sleep_us(us)
    return s / n

def ler_temp_c():
    raw = adc_media()
    v = (raw / 1023.0) * VCC
    if v <= 0.0 or v >= VCC:
        return None
    Rt = R_FIXED * (v / (VCC - v))         # kΩ
    invT = (1.0 / T0K) + (1.0 / BETA) * math.log(Rt / R0)
    Tk = 1.0 / invT
    return Tk - 273.15

def dentro_da_faixa(tC):
    return (TMIN <= tC <= TMAX)

print("ClimaLink main.py iniciado (sem NTP)")
try:
    while True:
        tC = ler_temp_c()
        if tC is None:
            led.value(1)
            print(f"[{now_uptime_str()}] ERRO_ADC | LED: ON")
        else:
            alerta = not dentro_da_faixa(tC)
            led.value(1 if alerta else 0)
            print(f"[{now_uptime_str()}] TempC: {tC:.2f} | LED: {'ON' if alerta else 'OFF'}")
        time.sleep(SAMPLE_INTERVAL_S)

except KeyboardInterrupt:
    led.value(0)
    print("Parado pelo usuário")
