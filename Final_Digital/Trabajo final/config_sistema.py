# config_sistema.py — Configuración centralizada del sistema
import json

# =============================================
# CONFIGURACIÓN DEL BOT DE TELEGRAM
# =============================================
TELEGRAM_TOKEN = "7935777862:AAFYFwGPMmI9Cy1AArMWEeMYVvJK4dBCYpM"
CHAT_IDS_AUTORIZADOS = [8213202666]  # Tu ID ya autorizado

# =============================================
# ESTADO DEL SISTEMA
# =============================================
sistema_activo = False  # Sistema completo ON/OFF
paciente_presente = False  # Hay paciente en la sala

# Estados individuales de sensores
sensores_activos = {
    'dht': True,        # Temperatura y humedad
    'peso': False,      # HX711 (solo si hay paciente)
    'luz': True,        # LDR
    'proximidad': True, # HC-SR04
    'panico': True      # Botón de pánico
}

# =============================================
# UMBRALES CONFIGURABLES
# =============================================
umbrales = {
    # DHT22
    'temp_min': 18,
    'temp_max': 30,
    'hum_min': 30,
    'hum_max': 70,
    
    # HX711
    'peso_presencia': 5000,
    'peso_caida': 20000,
    
    # LDR
    'luz_oscuridad': 150,
    'luz_exceso': 250,
    
    # HC-SR04
    'distancia_umbral': 25,
    'tiempo_puerta': 5
}

# =============================================
# FUNCIONES DE GESTIÓN
# =============================================

def activar_sistema():
    """Enciende el sistema completo"""
    global sistema_activo
    sistema_activo = True
    print("Sistema ACTIVADO")

def desactivar_sistema():
    """Apaga el sistema completo"""
    global sistema_activo, paciente_presente
    sistema_activo = False
    paciente_presente = False
    # Desactivar todos los sensores
    for sensor in sensores_activos:
        sensores_activos[sensor] = False
    print("Sistema DESACTIVADO")

def ingresar_paciente():
    """Registra ingreso de paciente"""
    global paciente_presente, sistema_activo
    paciente_presente = True
    sistema_activo = True
    # Activar todos los sensores
    for sensor in sensores_activos:
        sensores_activos[sensor] = True
    print("Paciente INGRESADO - Todos los sensores activados")

def retirar_paciente():
    """Registra salida de paciente"""
    global paciente_presente
    paciente_presente = False
    sensores_activos['peso'] = False  # Desactivar sensor de peso
    print("Paciente RETIRADO - Sensor de peso desactivado")

def activar_sensor(sensor):
    """Activa un sensor específico"""
    if sensor in sensores_activos:
        sensores_activos[sensor] = True
        print(f"Sensor {sensor} ACTIVADO")
        return True
    return False

def desactivar_sensor(sensor):
    """Desactiva un sensor específico"""
    if sensor in sensores_activos:
        sensores_activos[sensor] = False
        print(f"Sensor {sensor} DESACTIVADO")
        return True
    return False

def actualizar_umbral(parametro, valor):
    """Actualiza un umbral específico"""
    if parametro in umbrales:
        umbrales[parametro] = valor
        print(f"{parametro} = {valor}")
        return True
    return False

def get_estado():
    """Retorna el estado completo del sistema"""
    return {
        'sistema_activo': sistema_activo,
        'paciente_presente': paciente_presente,
        'sensores': sensores_activos.copy(),
        'umbrales': umbrales.copy()
    }

def get_info_texto():
    """Genera texto legible del estado del sistema"""
    estado = "ACTIVO" if sistema_activo else "INACTIVO"
    paciente = "SÍ" if paciente_presente else "NO"
    
    texto = f"""
ESTADO DEL SISTEMA
━━━━━━━━━━━━━━━━━━━
Sistema: {estado}
Paciente: {paciente}

 SENSORES:
"""
    
    iconos = {
        'dht': '',
        'peso': '',
        'luz': '',
        'proximidad': '',
        'panico': ''
    }
    
    nombres = {
        'dht': 'Temp/Humedad',
        'peso': 'Peso/Caída',
        'luz': 'Luz ambiente',
        'proximidad': 'Proximidad',
        'panico': 'Botón pánico'
    }
    
    for sensor, activo in sensores_activos.items():
        icono = iconos.get(sensor, '🔹')
        nombre = nombres.get(sensor, sensor)
        estado_sensor = "" if activo else ""
        texto += f"{icono} {nombre}: {estado_sensor}\n"
    
    texto += f"""
UMBRALES:
️ Temp: {umbrales['temp_min']}°C - {umbrales['temp_max']}°C
Hum: {umbrales['hum_min']}% - {umbrales['hum_max']}%
Peso presencia: {umbrales['peso_presencia']}
Peso caída: {umbrales['peso_caida']}
Luz oscuridad: {umbrales['luz_oscuridad']}
Luz exceso: {umbrales['luz_exceso']}
Distancia: {umbrales['distancia_umbral']} cm
"""
    
    return texto

def agregar_chat_id(chat_id):
    """Agrega un chat ID autorizado"""
    if chat_id not in CHAT_IDS_AUTORIZADOS:
        CHAT_IDS_AUTORIZADOS.append(chat_id)
        print(f" Chat ID {chat_id} autorizado")

def esta_autorizado(chat_id):
    """Verifica si un chat ID está autorizado"""
    return len(CHAT_IDS_AUTORIZADOS) == 0 or chat_id in CHAT_IDS_AUTORIZADOS