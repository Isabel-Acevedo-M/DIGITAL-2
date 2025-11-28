# sensor_dht.py — DHT22 + ventilador (solo lectura y control)
from machine import Pin
import time
import dht
import buzzer

# ============================
# CONFIGURACIÓN
# ============================
PIN_DHT = 4             # Sensor DHT22
PIN_VENTILADOR = 32     # LED o ventilador

# Valores por defecto (main actualiza desde config_sistema)
TEMP_MIN = 18
TEMP_MAX = 30
HUM_MIN  = 30
HUM_MAX  = 70

INTERVALO = 2           # segundos entre lecturas
# ============================

sensor = dht.DHT22(Pin(PIN_DHT))
vent = Pin(PIN_VENTILADOR, Pin.OUT)
try:
    vent.value(0)
except Exception:
    pass

temp = 0.0
hum = 0.0

# ---------- LECTURA ----------
def leer_sensor():
    """
    Intenta leer el sensor varias veces y devuelve (temp, hum).
    Mantiene últimos valores si falla.
    """
    global temp, hum
    for _ in range(3):
        try:
            sensor.measure()
            t = sensor.temperature()
            h = sensor.humidity()
            # forzar float y redondeo seguro
            temp = float(round(t, 1))
            hum = float(round(h, 1))
            return temp, hum
        except Exception as e:
            print("Error DHT22 (intento):", e)
            time.sleep_ms(300)

    # si no se pudo leer, devolvemos últimos valores conocidos
    print("Manteniendo últimos valores DHT")
    return temp, hum


def control_ventilador(t):
    """Ventilador automático según temperatura (usa TEMP_MAX actual)"""
    try:
        if t is None:
            return
        if t > TEMP_MAX:
            vent.value(1)
        else:
            vent.value(0)
    except Exception as e:
        print("Error control ventilador:", e)
