# boot.py — Inicialización básica del sistema
import network
import time

SSID = "WIFI-ITM"          
PASSWORD = ""    

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Conectando a WiFi...")
        wlan.connect(SSID, PASSWORD)

        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

    if wlan.isconnected():
        print("Conectado a WiFi")
        print("IP:", wlan.ifconfig()[0])
    else:
        print("Error: no se pudo conectar")

conectar_wifi()
print("boot.py listo.\n")
