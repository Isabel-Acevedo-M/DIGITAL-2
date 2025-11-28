# sensor_ldr.py — LDR invertido (valor bajo = oscuridad)
from machine import ADC, Pin
import time
import actuador_luz

PIN_LDR = 34
INTERVALO = 1

# Nuevos umbrales para tu caso:
UMBRAL_OSCURIDAD = 150   # Menos de 150 → ENCENDER luz
UMBRAL_LUZ = 250         # Más de 250 → APAGAR

ldr = ADC(Pin(PIN_LDR))
ldr.atten(ADC.ATTN_11DB)
ldr.width(ADC.WIDTH_12BIT)

ultimo_estado = "normal"

def leer_ldr():
    return ldr.read()

def controlar_luz(valor):

    # ---- OSCURIDAD ----
    if valor < UMBRAL_OSCURIDAD:
        actuador_luz.encender()
        return "oscuridad"

    # ---- LUZ FUERTE ----
    if valor > UMBRAL_LUZ:
        actuador_luz.apagar()
        return "exceso_luz"

    # ---- LUZ NORMAL ----
    actuador_luz.apagar()
    return "normal"

def ciclo_continuo():
    global ultimo_estado

    while True:
        valor = leer_ldr()
        estado = controlar_luz(valor)

        if estado != ultimo_estado:
            print(f"Estado: {estado} | Valor LDR: {valor}")
            ultimo_estado = estado

        print(f"Nivel de luz: {valor}")
        time.sleep(INTERVALO)


