# actuador_luz.py – Control simple de luz
from machine import Pin

PIN_LUZ = 26  
luz = Pin(PIN_LUZ, Pin.OUT)
luz.value(0)

def encender():
    luz.value(1)

def apagar():
    luz.value(0)

def estado():
    return luz.value()