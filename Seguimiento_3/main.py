from machine import Pin, ADC, Timer
import time

# Configuración ADC
sensor = ADC(Pin(34))
sensor.atten(ADC.ATTN_11DB)      # Configura el rango de tensión hasta ~3.3V
sensor.width(ADC.WIDTH_12BIT)    # Resolución de 12 bits (0 - 4095)

# led
luzIndicadora = Pin(4, Pin.OUT)   # LED conectado al pin 4

# Variables globales para filtros
coeficienteSuavizado = 0.1   # Coeficiente para el filtro exponencial
salidaFiltro = 0             # Valor almacenado en el filtro exponencial
listaLecturas = []           # Lista de lecturas para promedio móvil
listaLecturasMediana = []    # Lista de lecturas para filtro de mediana
ultimaLectura = 0            # Último valor leído por el ADC

# Variables de muestreo (para la toma del tiempo)
temporizador = Timer(0)
frecuenciaMuestreo = 50      # Hz
tiempoMuestreo = int(1000 / frecuenciaMuestreo)  # Periodo en ms

# Bandera para activar activar o desactivar el sistema
adquisicionActiva = False    # Controla si la adquisición está corriendo

# filtro 1: Promedio móvil
def promedioMovil(valores, cantidad=10):
    if len(valores) == 0:
        return 0
    datos = valores[-cantidad:] if len(valores) >= cantidad else valores
    return sum(datos) / len(datos)

# filtro 2: Filtro exponencial
def filtroExponencial(valorEntrada):
    global salidaFiltro
    if salidaFiltro == 0:
        salidaFiltro = valorEntrada
    salidaFiltro = coeficienteSuavizado * valorEntrada + (1 - coeficienteSuavizado) * salidaFiltro
    return salidaFiltro

# Filtro 3: Filtro de mediana
def filtroMediana(valorActual, cantidad=5):
    global listaLecturasMediana
    listaLecturasMediana.append(valorActual)
    if len(listaLecturasMediana) > cantidad:
        listaLecturasMediana.pop(0)
    if len(listaLecturasMediana) < 3:
        return valorActual
    datosOrdenados = sorted(listaLecturasMediana)
    return datosOrdenados[len(datosOrdenados) // 2]

# Para determinar los filtros en cascada o no
def seleccionarDosFiltros():
    print("\n Filtración de datos con dos filtros en cascada ")
    print("1. Promedio móvil")
    print("2. Filtro exponencial")
    print("3. Filtro de mediana")
    try:
        filtroUno = int(input("Primer filtro: "))
        if filtroUno not in [1, 2, 3]:
            print("Opción inválida")
            return 0
        filtroDos = int(input("Segundo filtro: "))
        if filtroDos not in [1, 2, 3]:
            print("Opción inválida")
            return 0
        nombres = ["", "Promedio móvil", "Filtro exponencial", "Filtro de mediana"]
        print("\nFiltros configurados en cascada:")
        print("1º:", nombres[filtroUno])
        print("2º:", nombres[filtroDos])
        return 10 + filtroUno * 10 + filtroDos
    except:
        print("Error en la selección")
        return 0

# Muestrear y guardar datos leídos
def muestrear():
    global ultimaLectura
    ultimaLectura = sensor.read()

# Aplica el filtro que se elija si solo se elige 1
def aplicarFiltroIndividual(valor, tipo):
    global listaLecturas
    if tipo == 1:
        listaLecturas.append(valor)
        if len(listaLecturas) > 50:
            listaLecturas.pop(0)
        return promedioMovil(listaLecturas, min(10, len(listaLecturas))) if len(listaLecturas) >= 3 else valor
    elif tipo == 2:
        return filtroExponencial(valor)
    elif tipo == 3:
        return filtroMediana(valor, 5)
    else:
        return valor

# Para cuando se selecciona uno o más filtros (para la cascada)
def aplicarFiltro(valor, tipoFiltro):
    if tipoFiltro == 1:
        return aplicarFiltroIndividual(valor, 1)
    elif tipoFiltro == 2:
        return aplicarFiltroIndividual(valor, 2)
    elif tipoFiltro == 3:
        return aplicarFiltroIndividual(valor, 3)
    elif tipoFiltro == 5:  # Tres filtros en cascada
        pasoUno = aplicarFiltroIndividual(valor, 1)
        pasoDos = filtroExponencial(pasoUno)
        return filtroMediana(pasoDos, 5)
    else:
        return valor

# Se muestran todos los datos tomados por el sensor y se aplican los filtros elegidos
def capturarConFiltro(tipoFiltro):
    global adquisicionActiva, frecuenciaMuestreo, tiempoMuestreo
    print("\n Se inicia la toma de datos (Ctrl+C para detener) ")
    try:
        adquisicionActiva = True
        luzIndicadora.on()
        temporizador.init(period=tiempoMuestreo, mode=Timer.PERIODIC, callback=lambda t: muestrear())
        contador = 0
        while adquisicionActiva:
            valor = sensor.read()
            valorFiltrado = aplicarFiltro(valor, tipoFiltro)
            contador += 1
            if contador >= 10:
                print("Cruda: {:.0f} - Filtrada: {:.2f}".format(valor, valorFiltrado))
                contador = 0
            time.sleep(tiempoMuestreo / 1000.0)
    except KeyboardInterrupt:
        print("\nAdquisición detenida por el usuario")
    finally:
        adquisicionActiva = False
        temporizador.deinit()
        luzIndicadora.off()

# Para que el usuario pueda cambiar la frecuencia de muestreo
def configurarFrecuencia():
    global frecuenciaMuestreo, tiempoMuestreo
    try:
        nuevaFrecuencia = float(input("Nueva frecuencia (Hz): "))
        if 1 <= nuevaFrecuencia <= 1000:
            frecuenciaMuestreo = nuevaFrecuencia
            tiempoMuestreo = int(1000 / frecuenciaMuestreo)
            print("Frecuencia configurada en:", frecuenciaMuestreo, "Hz")
        else:
            print("La frecuencia debe estar entre 1 y 1000 Hz")
    except:
        print("Error al configurar frecuencia")

# Función que aplica dos filtros en cascada
def capturarConFiltrosPersonalizados(codigoFiltros):
    global adquisicionActiva, frecuenciaMuestreo, tiempoMuestreo
    filtroUno = (codigoFiltros - 10) // 10
    filtroDos = (codigoFiltros - 10) % 10
    print("\n Adquiriendo datos con filtros seleccionados... ")
    try:
        adquisicionActiva = True
        luzIndicadora.on()
        temporizador.init(period=tiempoMuestreo, mode=Timer.PERIODIC, callback=lambda t: muestrear())
        contador = 0
        while adquisicionActiva:
            valor = sensor.read()
            pasoUno = aplicarFiltroIndividual(valor, filtroUno)
            valorFiltrado = aplicarFiltroIndividual(pasoUno, filtroDos)
            contador += 1
            if contador >= 10:
                print("Cruda: {:.0f} - Filtrada: {:.2f}".format(valor, valorFiltrado))
                contador = 0
            time.sleep(tiempoMuestreo / 1000.0)
    except KeyboardInterrupt:
        print("\nAdquisición detenida por el usuario")
    finally:
        adquisicionActiva = False
        temporizador.deinit()
        luzIndicadora.off()

#<fUNCION QUE PERMITE SELECCIONAR FILTRPO
def menuPrincipal():
    global frecuenciaMuestreo
    print("HOLA, BIENVENIDO AL SISTEMA ECG AD8232")
    while True:
        print("\n Menú Principal ")
        print("1. Filtro Promedio Móvil")
        print("2. Filtro Exponencial")
        print("3. Filtro de Mediana")
        print("4. Dos filtros en cascada (personalizados)")
        print("5. Tres filtros en cascada")
        print("6. Sin filtro (señal cruda)")
        print("7. Configurar frecuencia ({} Hz)".format(frecuenciaMuestreo)) #Si el usuario decide configurar fm
        print("0. Salir")
        try:
            opcion = int(input("Seleccione opción: "))
            if opcion == 0:
                print("Cerrando sistema...")
                break
            elif opcion == 7:
                configurarFrecuencia()
            elif opcion == 1:
                capturarConFiltro(1)
            elif opcion == 2:
                capturarConFiltro(2)
            elif opcion == 3:
                capturarConFiltro(3)
            elif opcion == 4:
                codigo = seleccionarDosFiltros()
                if codigo > 0:
                    capturarConFiltrosPersonalizados(codigo)
            elif opcion == 5:
                capturarConFiltro(5)
            elif opcion == 6:
                capturarConFiltro(0)
            else:
                print("Opción inválida")
        except KeyboardInterrupt:
            print("\nSistema interrumpido")
            break

#para que inicie el menú
if __name__ == "__main__":
    menuPrincipal()
