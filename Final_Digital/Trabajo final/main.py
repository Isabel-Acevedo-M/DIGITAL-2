# main.py — ESP32: Telegram COMPLETO + API para PC
import time
import gc
import config_sistema as cfg
import sensor_dht
import sensor_hx711
import sensor_ldr
import sensor_proximidad
import boton_panico

# =============================================
# TELEGRAM COMPLETO
# =============================================

ultimo_update_id = 0
ultimo_check = 0

def telegram_enviar(chat_id, texto):
    """Envía mensaje a Telegram"""
    try:
        import usocket as socket
        import ssl
        
        texto = texto.replace(' ', '%20').replace('\n', '%0A')
        texto = texto.replace(':', '%3A').replace('/', '%2F')
        texto = texto[:250]
        
        path = f"/bot{cfg.TELEGRAM_TOKEN}/sendMessage?chat_id={chat_id}&text={texto}"
        req = f"GET {path} HTTP/1.1\r\nHost: api.telegram.org\r\nConnection: close\r\n\r\n"
        
        addr = socket.getaddrinfo("api.telegram.org", 443)[0][-1]
        s = socket.socket()
        s.settimeout(3)
        s.connect(addr)
        s = ssl.wrap_socket(s, server_hostname="api.telegram.org")
        s.write(req.encode())
        s.read(100)
        s.close()
        del s
        gc.collect()
        return True
    except:
        gc.collect()
        return False

def telegram_verificar():
    """Verifica comandos cada 5 seg"""
    global ultimo_update_id, ultimo_check
    
    if time.time() - ultimo_check < 5:
        return
    ultimo_check = time.time()
    
    try:
        import usocket as socket
        import ssl
        
        path = f"/bot{cfg.TELEGRAM_TOKEN}/getUpdates?offset={ultimo_update_id+1}&timeout=0"
        req = f"GET {path} HTTP/1.1\r\nHost: api.telegram.org\r\nConnection: close\r\n\r\n"
        
        addr = socket.getaddrinfo("api.telegram.org", 443)[0][-1]
        s = socket.socket()
        s.settimeout(3)
        s.connect(addr)
        s = ssl.wrap_socket(s, server_hostname="api.telegram.org")
        s.write(req.encode())
        
        data = b""
        while len(data) < 2048:
            chunk = s.read(256)
            if not chunk:
                break
            data += chunk
        s.close()
        del s
        
        if b'"update_id":' in data:
            pos = data.rfind(b'"update_id":')
            end = data.find(b',', pos)
            ultimo_update_id = int(data[pos+12:end])
            
            cid = None
            cpos = data.rfind(b'"chat":{"id":')
            if cpos != -1:
                cend = data.find(b',', cpos+13)
                try:
                    cid = int(data[cpos+13:cend])
                except:
                    pass
            
            if cid:
                procesar_comando(cid, data)
        
        gc.collect()
    except:
        gc.collect()

def procesar_comando(chat_id, data):
    """Procesa TODOS los comandos"""
    
    if b'/start' in data:
        cfg.agregar_chat_id(chat_id)
        msg1 = "Bienvenido al Sistema de Monitoreo"
        msg2 = "GESTION: /ingresar /retirar /activar /apagar /estado"
        msg3 = "SENSORES: /sensor_dht_on _off /sensor_peso_on _off /sensor_luz_on _off /sensor_prox_on _off /sensor_panico_on _off"
        msg4 = "CONFIG: /set temp_max 28 - /umbral /ayuda"
        telegram_enviar(chat_id, msg1)
        time.sleep(1)
        telegram_enviar(chat_id, msg2)
        time.sleep(1)
        telegram_enviar(chat_id, msg3)
        time.sleep(1)
        telegram_enviar(chat_id, msg4)
        print("✅ /start")
    
    elif b'/ingresar' in data:
        cfg.ingresar_paciente()
        telegram_enviar(chat_id, "Paciente INGRESADO - Sistema ACTIVO - Todos los sensores ON")
        print("✅ /ingresar")
    
    elif b'/retirar' in data:
        cfg.retirar_paciente()
        telegram_enviar(chat_id, "Paciente RETIRADO - Sensor de peso OFF")
        print("✅ /retirar")
    
    elif b'/activar' in data:
        cfg.activar_sistema()
        telegram_enviar(chat_id, "Sistema ACTIVADO")
        print("✅ /activar")
    
    elif b'/apagar' in data:
        cfg.desactivar_sistema()
        telegram_enviar(chat_id, "Sistema APAGADO - Todos los sensores OFF")
        print("✅ /apagar")
    
    elif b'/estado' in data:
        s = "ON" if cfg.sistema_activo else "OFF"
        p = "SI" if cfg.paciente_presente else "NO"
        try:
            t, h = sensor_dht.leer_sensor()
            luz = sensor_ldr.leer_ldr()
            telegram_enviar(chat_id, f"Sistema {s} - Paciente {p} - Temp {t}C - Hum {h}% - Luz {luz}")
        except:
            telegram_enviar(chat_id, f"Sistema {s} - Paciente {p}")
        print("✅ /estado")
    
    elif b'/sensor_dht_on' in data:
        cfg.activar_sensor('dht')
        telegram_enviar(chat_id, "Sensor Temperatura/Humedad ACTIVADO")
        print("✅ /sensor_dht_on")
    
    elif b'/sensor_dht_off' in data:
        cfg.desactivar_sensor('dht')
        telegram_enviar(chat_id, "Sensor Temperatura/Humedad DESACTIVADO")
        print("✅ /sensor_dht_off")
    
    elif b'/sensor_peso_on' in data:
        if cfg.paciente_presente:
            cfg.activar_sensor('peso')
            telegram_enviar(chat_id, "Sensor de Peso ACTIVADO")
        else:
            telegram_enviar(chat_id, "Primero debe ingresar un paciente con /ingresar")
        print("✅ /sensor_peso_on")
    
    elif b'/sensor_peso_off' in data:
        cfg.desactivar_sensor('peso')
        telegram_enviar(chat_id, "Sensor de Peso DESACTIVADO")
        print("✅ /sensor_peso_off")
    
    elif b'/sensor_luz_on' in data:
        cfg.activar_sensor('luz')
        telegram_enviar(chat_id, "Sensor de Luz ACTIVADO")
        print("✅ /sensor_luz_on")
    
    elif b'/sensor_luz_off' in data:
        cfg.desactivar_sensor('luz')
        telegram_enviar(chat_id, "Sensor de Luz DESACTIVADO")
        print("✅ /sensor_luz_off")
    
    elif b'/sensor_prox_on' in data:
        cfg.activar_sensor('proximidad')
        telegram_enviar(chat_id, "Sensor de Proximidad ACTIVADO")
        print("✅ /sensor_prox_on")
    
    elif b'/sensor_prox_off' in data:
        cfg.desactivar_sensor('proximidad')
        telegram_enviar(chat_id, "Sensor de Proximidad DESACTIVADO")
        print("✅ /sensor_prox_off")
    
    elif b'/sensor_panico_on' in data:
        cfg.activar_sensor('panico')
        telegram_enviar(chat_id, "Boton de Panico ACTIVADO")
        print("✅ /sensor_panico_on")
    
    elif b'/sensor_panico_off' in data:
        cfg.desactivar_sensor('panico')
        telegram_enviar(chat_id, "Boton de Panico DESACTIVADO")
        print("✅ /sensor_panico_off")
    
    elif b'/set ' in data:
        try:
            text_pos = data.find(b'"text":"')
            if text_pos != -1:
                text_end = data.find(b'"', text_pos + 8)
                comando = data[text_pos+8:text_end].decode('utf-8')
                
                partes = comando.split()
                if len(partes) == 3:
                    parametro = partes[1]
                    valor = float(partes[2])
                    
                    if cfg.actualizar_umbral(parametro, valor):
                        telegram_enviar(chat_id, f"Umbral {parametro} = {valor}")
                    else:
                        telegram_enviar(chat_id, f"Parametro invalido: {parametro}")
        except:
            telegram_enviar(chat_id, "Uso: /set parametro valor - Ej: /set temp_max 28")
        print("✅ /set")
    
    elif b'/umbral' in data:
        msg1 = "Parametros disponibles:"
        msg2 = "temp_min temp_max hum_min hum_max"
        msg3 = "peso_presencia peso_caida"
        msg4 = "luz_oscuridad luz_exceso distancia_umbral"
        msg5 = "Uso: /set parametro valor"
        telegram_enviar(chat_id, msg1)
        time.sleep(1)
        telegram_enviar(chat_id, msg2)
        time.sleep(1)
        telegram_enviar(chat_id, msg3)
        time.sleep(1)
        telegram_enviar(chat_id, msg4)
        time.sleep(1)
        telegram_enviar(chat_id, msg5)
        print("✅ /umbral")
    
    elif b'/ayuda' in data or b'/help' in data:
        msg1 = "COMANDOS PRINCIPALES:"
        msg2 = "/ingresar /retirar /activar /apagar /estado"
        msg3 = "SENSORES (X=dht peso luz prox panico):"
        msg4 = "/sensor_X_on /sensor_X_off"
        msg5 = "CONFIGURACION: /set /umbral"
        telegram_enviar(chat_id, msg1)
        time.sleep(1)
        telegram_enviar(chat_id, msg2)
        time.sleep(1)
        telegram_enviar(chat_id, msg3)
        time.sleep(1)
        telegram_enviar(chat_id, msg4)
        time.sleep(1)
        telegram_enviar(chat_id, msg5)
        print("✅ /ayuda")

# =============================================
# API PARA PC (CORREGIDA)
# =============================================

def obtener_datos():
    """Datos actuales en JSON"""
    try:
        t, h = sensor_dht.leer_sensor()
    except:
        t, h = 0, 0
    
    try:
        luz = sensor_ldr.leer_ldr()
    except:
        luz = 0
    
    try:
        dist = sensor_proximidad.medir_distancia()
    except:
        dist = 0
    
    datos = {
        'sistema_activo': cfg.sistema_activo,
        'paciente_presente': cfg.paciente_presente,
        'temperatura': t,
        'humedad': h,
        'luz': luz,
        'distancia': round(dist, 1),
        'sensores': {
            'dht': cfg.sensores_activos['dht'],
            'peso': cfg.sensores_activos['peso'],
            'luz': cfg.sensores_activos['luz'],
            'proximidad': cfg.sensores_activos['proximidad'],
            'panico': cfg.sensores_activos['panico']
        },
        'umbrales': cfg.umbrales
    }
    
    return datos

def api_servidor():
    """API HTTP en puerto 8080 (MEJORADA)"""
    try:
        import usocket as socket
        import ujson
        
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', 8080))
        s.listen(1)
        s.settimeout(0.05)  # Timeout más corto
        
        try:
            c, a = s.accept()
            peticion = c.recv(512)
            
            # Responder a OPTIONS (CORS preflight)
            if b'OPTIONS' in peticion:
                c.send(b'HTTP/1.1 200 OK\r\n')
                c.send(b'Access-Control-Allow-Origin: *\r\n')
                c.send(b'Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n')
                c.send(b'Access-Control-Allow-Headers: *\r\n')
                c.send(b'Connection: close\r\n\r\n')
            else:
                datos = obtener_datos()
                json_str = ujson.dumps(datos)
                
                c.send(b'HTTP/1.1 200 OK\r\n')
                c.send(b'Content-Type: application/json\r\n')
                c.send(b'Access-Control-Allow-Origin: *\r\n')
                c.send(b'Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n')
                c.send(b'Connection: close\r\n\r\n')
                c.send(json_str)
            
            c.close()
        except OSError:
            pass
        
        s.close()
        del s
        gc.collect()
    except:
        pass

# =============================================
# ALERTAS AUTOMÁTICAS
# =============================================

ultima_alerta_enviada = {}
COOLDOWN_ALERTA = 60  # segundos entre alertas del mismo tipo

def enviar_alerta_telegram(tipo, datos=""):
    """Envía alerta a Telegram con cooldown"""
    tiempo_actual = time.time()
    ultima = ultima_alerta_enviada.get(tipo, 0)
    
    if tiempo_actual - ultima > COOLDOWN_ALERTA:
        for chat_id in cfg.CHAT_IDS_AUTORIZADOS:
            telegram_enviar(chat_id, f"ALERTA {tipo} - {datos}")
        ultima_alerta_enviada[tipo] = tiempo_actual

# =============================================
# MONITOREO SENSORES
# =============================================

c_dht, c_peso, c_luz, c_prox = 0, 0, 0, 0

def monitorear():
    """Monitorea sensores"""
    global c_dht, c_peso, c_luz, c_prox
    
    if not cfg.sistema_activo:
        try:
            import buzzer, actuador_luz
            buzzer.alerta('off')
            actuador_luz.apagar()
        except:
            pass
        return
    
    c_dht += 1
    if c_dht >= 20 and cfg.sensores_activos['dht']:
        c_dht = 0
        try:
            sensor_dht.TEMP_MIN = cfg.umbrales['temp_min']
            sensor_dht.TEMP_MAX = cfg.umbrales['temp_max']
            sensor_dht.HUM_MIN = cfg.umbrales['hum_min']
            sensor_dht.HUM_MAX = cfg.umbrales['hum_max']
            t, h = sensor_dht.leer_sensor()
            sensor_dht.control_ventilador(t)
            
            # ALERTAS DE TEMPERATURA
            if t < sensor_dht.TEMP_MIN:
                enviar_alerta_telegram('TEMP_BAJA', f'{t}C')
            elif t > sensor_dht.TEMP_MAX:
                enviar_alerta_telegram('TEMP_ALTA', f'{t}C')
            
            # ALERTAS DE HUMEDAD
            if h < sensor_dht.HUM_MIN:
                enviar_alerta_telegram('HUM_BAJA', f'{h}%')
            elif h > sensor_dht.HUM_MAX:
                enviar_alerta_telegram('HUM_ALTA', f'{h}%')
        except:
            pass
    
    c_peso += 1
    if c_peso >= 10 and cfg.sensores_activos['peso'] and cfg.paciente_presente:
        c_peso = 0
        try:
            evento = sensor_hx711.detectar_evento()
            
            # ALERTAS DE PESO
            if evento == 'caida':
                enviar_alerta_telegram('CAIDA', 'Paciente ha caido')
            elif evento == 'bajo':
                enviar_alerta_telegram('FUERA_CAMA', 'Bajo de la cama')
        except:
            pass
    
    c_luz += 1
    if c_luz >= 10 and cfg.sensores_activos['luz']:
        c_luz = 0
        try:
            valor = sensor_ldr.leer_ldr()
            sensor_ldr.controlar_luz(valor)
        except:
            pass
    
    c_prox += 1
    if c_prox >= 5 and cfg.sensores_activos['proximidad']:
        c_prox = 0
        try:
            dist = sensor_proximidad.medir_distancia()
            t = time.time()
            if dist > 0 and dist < cfg.umbrales['distancia_umbral'] and not sensor_proximidad.puerta_abierta:
                import buzzer, actuador_puerta
                buzzer.alerta('peso')
                actuador_puerta.abrir()
                sensor_proximidad.puerta_abierta = True
                sensor_proximidad.ultimo_cierre = t
            if sensor_proximidad.puerta_abierta and t - sensor_proximidad.ultimo_cierre > 5:
                import actuador_puerta
                actuador_puerta.cerrar()
                sensor_proximidad.puerta_abierta = False
        except:
            pass
    
    if cfg.sensores_activos['panico']:
        try:
            estado_anterior = boton_panico.estado_anterior
            boton_panico.verificar()
            
            # ALERTA DE PÁNICO
            if boton_panico.estado_anterior == 0 and estado_anterior == 1:
                enviar_alerta_telegram('PANICO', 'Boton presionado')
        except:
            pass

# =============================================
# INIT
# =============================================

import network
wlan = network.WLAN(network.STA_IF)
ip_esp = wlan.ifconfig()[0]

print("\n" + "="*50)
print("ESP32 + PC - Sistema Completo")
print("="*50)
print(f"✅ Telegram: Activo")
print(f"✅ API: http://{ip_esp}:8080")
print(f"   👆 USA ESTA IP EN dashboard.html")
print("="*50 + "\n")

try:
    sensor_hx711.hx.calibrar_baseline()
except:
    pass

print("Sistema listo\n")

# =============================================
# BUCLE
# =============================================

cgc = 0

while True:
    try:
        telegram_verificar()
        monitorear()
        api_servidor()
        
        cgc += 1
        if cgc > 50:
            gc.collect()
            cgc = 0
        
        time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nDetenido")
        break
    except Exception as e:
        gc.collect()
        time.sleep(1)