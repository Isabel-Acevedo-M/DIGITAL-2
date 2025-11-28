# sensor_proximidad.py – HC-SR04 + servo puerta
from machine import Pin, time_pulse_us
import time
import actuador_puerta
import buzzer

TRIG = Pin(12, Pin.OUT)   # TRIG en pin 12
ECHO = Pin(13, Pin.IN)    # ECHO en pin 13

DIST_UMBRAL = 25          # cm para abrir la puerta
TIEMPO_ABIERTA = 5        # segundos que la puerta queda abierta

puerta_abierta = False
ultimo_cierre = 0

def medir_distancia():
    """
    Genera un pulso en TRIG y mide el tiempo en ECHO.
    Maneja errores de time_pulse_us devolviendo un valor muy grande (no detección).
    """
    # Asegurar estados iniciales
    try:
        TRIG.value(0)
    except Exception:
        # En algunos ports el value puede lanzar; ignoramos
        pass

    # Pulso de trigger
    time.sleep_us(5)
    TRIG.value(1)
    time.sleep_us(10)
    TRIG.value(0)

    # time_pulse_us devuelve duración en microsegundos, o -2/-1 en error en algunas builds
    try:
        duracion = time_pulse_us(ECHO, 1, 30000)  # timeout 30 ms
    except Exception as e:
        # Si falla la medición, devolvemos distancia alta para no activar la puerta
        print("⚠️ time_pulse_us error:", e)
        return 999.0

    # Manejo de retornos no válidos
    if duracion is None:
        return 999.0
    if isinstance(duracion, int) and duracion <= 0:
        return 999.0

    # Convertir microsegundos a cm: (duracion/2) / 29.1
    distancia = (duracion / 2) / 29.1
    return distancia

def ciclo_continuo():
    """
    Ciclo independiente si lo quieres correr (opcional).
    Nota: tu main usa medir_distancia() desde su loop, así que esto es opcional.
    """
    global puerta_abierta, ultimo_cierre

    while True:
        distancia = medir_distancia()
        print(f" Distancia: {distancia:.1f} cm")

        # Mano detectada
        if distancia > 0 and distancia < DIST_UMBRAL and not puerta_abierta:
            print(" Mano detectada: ABRIENDO PUERTA")
            try:
                buzzer.alerta('peso')  # sonido suave
            except Exception as e:
                print("buzzer alerta error:", e)
            try:
                actuador_puerta.abrir()
            except Exception as e:
                print("actuador_puerta.open error:", e)
            puerta_abierta = True
            ultimo_cierre = time.time()

        # Cerrar automáticamente después del tiempo configurado
        if puerta_abierta and (time.time() - ultimo_cierre > TIEMPO_ABIERTA):
            try:
                actuador_puerta.cerrar()
            except Exception as e:
                print("actuador_puerta.close error:", e)
            puerta_abierta = False

        time.sleep(0.2)
