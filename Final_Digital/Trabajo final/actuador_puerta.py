# actuador_puerta.py – Control de servo para puerta
from machine import Pin, PWM
import time

PIN_SERVO = 23   # ← Servo SG90 en pin 23

servo = PWM(Pin(PIN_SERVO), freq=50)

def mover(ang):
    # Conversión 0–180 grados al rango PWM
    duty = int((ang / 180) * 102 + 26)
    servo.duty(duty)

def abrir():
    mover(90)   # Ajustar si tu servo abre más/menos
    print("Puerta ABIERTA")

def cerrar():
    mover(0)
    print("Puerta CERRADA")