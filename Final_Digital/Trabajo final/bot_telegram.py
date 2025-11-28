# bot_telegram.py — Bot de Telegram para control del sistema
import time
import config_sistema as cfg
import usocket as socket
import ssl
import ujson as json

# =============================================
# VARIABLES GLOBALES
# =============================================
ultimo_update_id = 0
ultimo_check = 0
INTERVALO_CHECK = 1  # segundos entre checks

# =============================================
# FUNCIONES DE API (USANDO SOCKET)
# =============================================

def enviar_mensaje(chat_id, texto):
    """Envía un mensaje de texto al chat usando socket directo"""
    try:
        # URL encode del texto para GET request
        texto_encoded = texto.replace(' ', '%20').replace('\n', '%0A').replace(':', '%3A').replace('/', '%2F')
        
        # Construir request HTTP
        path = f"/bot{cfg.TELEGRAM_TOKEN}/sendMessage?chat_id={chat_id}&text={texto_encoded}"
        
        request = f"GET {path} HTTP/1.1\r\n"
        request += "Host: api.telegram.org\r\n"
        request += "Connection: close\r\n\r\n"
        
        # Conectar
        addr = socket.getaddrinfo("api.telegram.org", 443)[0][-1]
        s = socket.socket()
        s.settimeout(10)
        s.connect(addr)
        
        # SSL
        s = ssl.wrap_socket(s, server_hostname="api.telegram.org")
        
        # Enviar request
        s.write(request.encode())
        
        # Leer respuesta
        response = b""
        while True:
            try:
                chunk = s.read(512)
                if not chunk:
                    break
                response += chunk
            except:
                break
        
        s.close()
        
        # Verificar respuesta
        return b'"ok":true' in response
        
    except Exception as e:
        print(f" Error enviando mensaje: {e}")
        return False

def get_updates():
    """Obtiene nuevas actualizaciones del bot usando socket directo"""
    global ultimo_update_id
    
    try:
        # Construir request HTTP
        path = f"/bot{cfg.TELEGRAM_TOKEN}/getUpdates?offset={ultimo_update_id + 1}&timeout=0"
        
        request = f"GET {path} HTTP/1.1\r\n"
        request += "Host: api.telegram.org\r\n"
        request += "Connection: close\r\n\r\n"
        
        # Conectar
        addr = socket.getaddrinfo("api.telegram.org", 443)[0][-1]
        s = socket.socket()
        s.settimeout(10)
        s.connect(addr)
        
        # SSL
        s = ssl.wrap_socket(s, server_hostname="api.telegram.org")
        
        # Enviar request
        s.write(request.encode())
        
        # Leer respuesta completa
        response = b""
        while True:
            try:
                chunk = s.read(1024)
                if not chunk:
                    break
                response += chunk
            except:
                break
        
        s.close()
        
        # Separar headers y body
        parts = response.split(b'\r\n\r\n', 1)
        if len(parts) > 1:
            body = parts[1]
            data = json.loads(body)
            if data.get('ok'):
                return data.get('result', [])
        return []
        
    except Exception as e:
        print(f" Error obteniendo updates: {e}")
        return []

# =============================================
# PROCESAMIENTO DE COMANDOS
# =============================================

def procesar_comando(chat_id, mensaje):
    """Procesa los comandos recibidos"""
    
    msg = mensaje.strip().lower()
    
    # ========== COMANDOS PRINCIPALES ==========
    
    if msg == '/start':
        cfg.agregar_chat_id(chat_id)
        texto = """Bienvenido al Sistema de Monitoreo

GESTION DE PACIENTES:
/ingresar - Registrar ingreso de paciente
/retirar - Registrar salida de paciente

CONTROL DEL SISTEMA:
/activar - Encender sistema
/apagar - Apagar sistema
/estado - Ver estado completo

SENSORES:
/sensor_dht_on - Activar temp/humedad
/sensor_dht_off - Desactivar temp/humedad
/sensor_peso_on - Activar sensor peso
/sensor_peso_off - Desactivar sensor peso
/sensor_luz_on - Activar luz
/sensor_luz_off - Desactivar luz
/sensor_prox_on - Activar proximidad
/sensor_prox_off - Desactivar proximidad
/sensor_panico_on - Activar boton panico
/sensor_panico_off - Desactivar boton panico

CONFIGURACION:
/umbral - Ver ayuda de configuracion

Usa /ayuda para mas informacion."""
        enviar_mensaje(chat_id, texto)
    
    elif msg == '/ayuda' or msg == '/help':
        texto = """AYUDA - CONFIGURACION DE UMBRALES

Para cambiar umbrales, usa:
/set [parametro] [valor]

Ejemplos:
/set temp_min 20
/set temp_max 28
/set hum_min 35
/set hum_max 65
/set peso_presencia 6000
/set peso_caida 25000
/set luz_oscuridad 200
/set luz_exceso 300
/set distancia_umbral 30

Parametros disponibles:
temp_min, temp_max
hum_min, hum_max
peso_presencia, peso_caida
luz_oscuridad, luz_exceso
distancia_umbral"""
        enviar_mensaje(chat_id, texto)
    
    # ========== GESTIÓN DE PACIENTES ==========
    
    elif msg == '/ingresar':
        cfg.ingresar_paciente()
        enviar_mensaje(chat_id, "Paciente INGRESADO - Sistema activado - Todos los sensores encendidos")
    
    elif msg == '/retirar':
        cfg.retirar_paciente()
        enviar_mensaje(chat_id, "Paciente RETIRADO - Sensor de peso desactivado - Otros sensores siguen activos")
    
    # ========== CONTROL DEL SISTEMA ==========
    
    elif msg == '/activar':
        cfg.activar_sistema()
        enviar_mensaje(chat_id, "Sistema ACTIVADO")
    
    elif msg == '/apagar':
        cfg.desactivar_sistema()
        enviar_mensaje(chat_id, "Sistema APAGADO - Todos los sensores desactivados")
    
    elif msg == '/estado':
        estado = cfg.get_info_texto()
        # Simplificar el texto para evitar problemas de encoding
        estado = estado.replace('ON').replace('OFF').replace('ON')
        estado = estado.replace('NO').replace('T').replace('H')
        estado = estado.replace('P').replace('L').replace('D')
        estado = estado.replace( '!').replace('-')
        enviar_mensaje(chat_id, estado)
    
    # ========== CONTROL DE SENSORES ==========
    
    elif msg == '/sensor_dht_on':
        cfg.activar_sensor('dht')
        enviar_mensaje(chat_id, "Sensor de Temperatura/Humedad ACTIVADO")
    
    elif msg == '/sensor_dht_off':
        cfg.desactivar_sensor('dht')
        enviar_mensaje(chat_id, "Sensor de Temperatura/Humedad DESACTIVADO")
    
    elif msg == '/sensor_peso_on':
        if cfg.paciente_presente:
            cfg.activar_sensor('peso')
            enviar_mensaje(chat_id, "Sensor de Peso ACTIVADO")
        else:
            enviar_mensaje(chat_id, "Primero debe ingresar un paciente - Usa /ingresar")
    
    elif msg == '/sensor_peso_off':
        cfg.desactivar_sensor('peso')
        enviar_mensaje(chat_id, "Sensor de Peso DESACTIVADO - El paciente puede moverse libremente")
    
    elif msg == '/sensor_luz_on':
        cfg.activar_sensor('luz')
        enviar_mensaje(chat_id, "Sensor de Luz ACTIVADO")
    
    elif msg == '/sensor_luz_off':
        cfg.desactivar_sensor('luz')
        enviar_mensaje(chat_id, "Sensor de Luz DESACTIVADO")
    
    elif msg == '/sensor_prox_on':
        cfg.activar_sensor('proximidad')
        enviar_mensaje(chat_id, "Sensor de Proximidad ACTIVADO")
    
    elif msg == '/sensor_prox_off':
        cfg.desactivar_sensor('proximidad')
        enviar_mensaje(chat_id, "Sensor de Proximidad DESACTIVADO")
    
    elif msg == '/sensor_panico_on':
        cfg.activar_sensor('panico')
        enviar_mensaje(chat_id, "Boton de Panico ACTIVADO")
    
    elif msg == '/sensor_panico_off':
        cfg.desactivar_sensor('panico')
        enviar_mensaje(chat_id, "Boton de Panico DESACTIVADO")
    
    # ========== CONFIGURACIÓN DE UMBRALES ==========
    
    elif msg.startswith('/set '):
        partes = mensaje.split()
        if len(partes) == 3:
            parametro = partes[1].lower()
            try:
                valor = float(partes[2])
                if cfg.actualizar_umbral(parametro, valor):
                    enviar_mensaje(chat_id, f"{parametro} actualizado a {valor}")
                else:
                    enviar_mensaje(chat_id, f"Parametro desconocido: {parametro} - Usa /ayuda para ver la lista")
            except ValueError:
                enviar_mensaje(chat_id, "Valor invalido. Debe ser un numero")
        else:
            enviar_mensaje(chat_id, "Formato incorrecto - Uso: /set [parametro] [valor] - Ejemplo: /set temp_max 28")
    
    elif msg == '/umbral':
        enviar_mensaje(chat_id, "CONFIGURACION DE UMBRALES - Usa: /set [parametro] [valor] - Ejemplos: /set temp_max 28 - /set hum_min 40 - Usa /ayuda para ver todos los parametros")
    
    else:
        enviar_mensaje(chat_id, "Comando no reconocido - Usa /start para ver los comandos disponibles")

# =============================================
# BUCLE PRINCIPAL
# =============================================

def verificar_mensajes():
    """Verifica nuevos mensajes (se llama desde main)"""
    global ultimo_update_id, ultimo_check
    
    # Limitar frecuencia de checks
    tiempo_actual = time.time()
    if tiempo_actual - ultimo_check < INTERVALO_CHECK:
        return
    
    ultimo_check = tiempo_actual
    
    updates = get_updates()
    
    for update in updates:
        ultimo_update_id = update.get('update_id', ultimo_update_id)
        
        # Procesar mensaje de texto
        if 'message' in update:
            mensaje = update['message']
            chat_id = mensaje.get('chat', {}).get('id')
            texto = mensaje.get('text', '')
            
            if chat_id and texto:
                # Verificar autorización
                if cfg.esta_autorizado(chat_id):
                    print(f" Comando recibido: {texto}")
                    procesar_comando(chat_id, texto)
                else:
                    enviar_mensaje(chat_id, "No estas autorizado - Contacta al administrador")

# =============================================
# FUNCIONES DE ALERTAS
# =============================================

def enviar_alerta(tipo, datos=""):
    """Envía una alerta a todos los chats autorizados"""
    
    mensajes = {
        'panico': "ALERTA - BOTON DE PANICO - El paciente ha presionado el boton de panico!",
        'temp_alta': f"ALERTA - TEMPERATURA ALTA - {datos}",
        'temp_baja': f"ALERTA - TEMPERATURA BAJA - {datos}",
        'hum_alta': f"ALERTA - HUMEDAD ALTA - {datos}",
        'hum_baja': f"ALERTA - HUMEDAD BAJA - {datos}",
        'caida': "ALERTA CRITICA - CAIDA DETECTADA - El paciente ha sufrido una caida!",
        'bajo_cama': "ALERTA - PACIENTE FUERA DE CAMA - El paciente se ha bajado de la cama",
    }
    
    mensaje = mensajes.get(tipo, f"Alerta: {tipo}")
    
    # Enviar a todos los chats autorizados
    for chat_id in cfg.CHAT_IDS_AUTORIZADOS:
        enviar_mensaje(chat_id, mensaje)

# =============================================
# INICIALIZACIÓN
# =============================================

def inicializar():
    """Inicializa el bot"""
    print("Bot de Telegram inicializado")
    print(f"Token configurado: {cfg.TELEGRAM_TOKEN[:10]}...")
    print("Usando socket directo (modo compatible)")
    
    # Verificar conectividad básica
    try:
        addr = socket.getaddrinfo("api.telegram.org", 443)[0][-1]
        print(f"DNS resuelto: {addr}")
    except Exception as e:
        print(f"No se pudo resolver DNS: {e}")