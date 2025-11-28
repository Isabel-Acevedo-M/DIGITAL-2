# sensor_hx711.py – Sistema de detección de caída mediante HX711
from machine import Pin
import time
import buzzer

DT_PIN = 18
SCK_PIN = 5

# UMBRALES (AJUSTABLES)
UMBRAL_PRESENCIA = 5000      # Detectar persona en cama
UMBRAL_CAIDA = 20000         # Cambio brusco = caída
INTERVALO = 0.5              # Tiempo entre lecturas


class HX711:
    def __init__(self, dout, sck):
        self.dout = Pin(dout, Pin.IN, Pin.PULL_UP)
        self.sck = Pin(sck, Pin.OUT)
        self.sck.value(0)
        self.baseline = 0
        self.ultima_lectura = 0
        time.sleep(1)

    def is_ready(self):
        return self.dout.value() == 0

    def wait_ready(self, timeout=1000):
        t0 = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), t0) < timeout:
            if self.is_ready():
                return True
            time.sleep_ms(1)
        return False

    def read_raw(self):
        if not self.wait_ready():
            return None

        data = 0
        for _ in range(24):
            self.sck.value(1)
            time.sleep_us(1)
            data = (data << 1) | self.dout.value()
            self.sck.value(0)
            time.sleep_us(1)

        self.sck.value(1)
        time.sleep_us(1)
        self.sck.value(0)

        if data & 0x800000:
            data -= 0x1000000

        return data

    def promedio(self, n=5):
        total = 0
        c = 0
        for _ in range(n):
            v = self.read_raw()
            if v is not None:
                total += v
                c += 1
            time.sleep_ms(10)
        return total / c if c else 0

    def calibrar_baseline(self):
        print("Calibrando cama vacía...")
        self.baseline = self.promedio(20)
        self.ultima_lectura = self.baseline
        print(f" Línea base establecida: {self.baseline:.1f}")


# ===============================
# VARIABLES
# ===============================
hx = HX711(DT_PIN, SCK_PIN)
paciente_en_cama = False


# ===============================
# DETECCIÓN
# ===============================
def detectar_evento():
    global paciente_en_cama

    evento = "normal"
    lectura = hx.promedio(5)

    # CORRECCIÓN: NO usar abs()
    # Cuando hay peso, lectura baja → baseline - lectura = valor positivo
    diferencia = hx.baseline - lectura

    # Este sí va con abs() porque mide cambios bruscos
    cambio_brusco = abs(lectura - hx.ultima_lectura)

    # -------------------------
    # Detectar paciente se sube
    # -------------------------
    if diferencia > UMBRAL_PRESENCIA and not paciente_en_cama:
        print(" Paciente SE SUBIÓ a la cama")
        paciente_en_cama = True
        evento = "subio"

    # -------------------------
    # Detectar BAJADA normal
    # -------------------------
    elif diferencia < UMBRAL_PRESENCIA and paciente_en_cama:
        print("Paciente se BAJÓ de la cama")
        paciente_en_cama = False
        evento = "bajo"
        buzzer.alerta("panico")

    # -------------------------
    # Detectar CAÍDA
    # -------------------------
    elif paciente_en_cama and cambio_brusco > UMBRAL_CAIDA:
        print("CAÍDA DETECTADA")
        paciente_en_cama = False
        evento = "caida"
        buzzer.alerta("panico")

    hx.ultima_lectura = lectura
    return evento


# ===============================
# BUCLE PRINCIPAL
# ===============================
def ciclo_continuo():
    hx.calibrar_baseline()
    print("Monitoreo de cama iniciado...\n")

    while True:
        evento = detectar_evento()
        print("Evento:", evento)
        time.sleep(INTERVALO)
