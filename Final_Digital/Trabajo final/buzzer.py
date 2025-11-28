# buzzer.py — Control básico de alertas
from machine import Pin, PWM
import time

BUZZER_PIN = 27  # ← Ajusta si usas otro pin

pwm = PWM(Pin(BUZZER_PIN))
pwm.duty(0)

def _beep(freq, duration=150):
    pwm.freq(freq)
    pwm.duty(400)
    time.sleep_ms(duration)
    pwm.duty(0)

def alerta(tipo):
    if tipo == 'panico':
        for _ in range(3):
            _beep(1000, 200)
            time.sleep_ms(100)

    elif tipo == 'temp_alta':
        _beep(1500, 250)

    elif tipo == 'temp_baja':
        _beep(600, 250)

    elif tipo == 'hum_alta':
        _beep(1300, 200)

    elif tipo == 'hum_baja':
        _beep(500, 200)

    elif tipo == 'peso':
        _beep(900, 180)

    elif tipo == 'luz':
        _beep(750, 120)

    elif tipo == 'prox':
        _beep(1100, 150)

    elif tipo == 'off':
        pwm.duty(0)
