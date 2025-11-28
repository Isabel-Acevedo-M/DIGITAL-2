# boton_panico.py – Botón de pánico (PIN 14)
from machine import Pin
import time
import buzzer

# =====================
# CONFIGURACIÓN
# =====================
BOTON_PIN = 14

# Botón con resistencia interna pull-up
boton = Pin(BOTON_PIN, Pin.IN, Pin.PULL_UP)

estado_anterior = 1  # suelto

def verificar():
    """
    Función que se llama repetidamente (no se queda bloqueada).
    Detecta si el botón está presionado.
    """
    global estado_anterior

    estado = boton.value()  # 1 = suelto, 0 = presionado

    # Cambio: suelto → presionado
    if estado == 0 and estado_anterior == 1:
        print("BOTÓN DE PÁNICO PRESIONADO")
        buzzer.alerta("panico")

    # Cambio: presionado → suelto
    elif estado == 1 and estado_anterior == 0:
        print("Botón liberado")
        buzzer.alerta("off")

    estado_anterior = estado


def ciclo_continuo():
    """Bucle para probar solo el botón."""
    print("Monitor de botón de pánico iniciado (PIN 14)")

    while True:
        verificar()
        time.sleep(0.05)
