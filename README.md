# EVAL-ADMX2001 — Documentación completa y guía "para dummies"

Este documento es una guía exhaustiva, formal y detallada para usar y desarrollar sobre la biblioteca `levalib` incluida en este repositorio. Está escrita en español y está diseñada para personas que necesitan instrucciones claras, paso a paso, con explicaciones sencillas y ejemplos prácticos.

Contenido
- Introducción rápida
- Requisitos e instalación (con ejemplos)
- Permisos y detección del puerto (Linux)
- Conceptos básicos: ¿qué hace la librería? (explicado como para dummies)
- Uso rápido — ejemplo mínimo
- API completa (métodos y explicaciones detalladas)
- Ejemplos avanzados (sweeps, calibración, análisis de componentes)
- Debugging y manejo de errores (paso a paso)
- Tests y desarrollo
- Preguntas frecuentes (FAQ)
- Siguientes pasos

-------------------------------------------------------------------------------

Introducción rápida
-------------------

`levalib` es una biblioteca en Python que permite controlar el analizador de impedancia EVAL-ADMX2001 de Analog Devices a través de un puerto serie (normalmente por USB). El objetivo de esta guía es que puedas:

- Conectar el dispositivo a tu ordenador.
- Configurar parámetros (frecuencia, amplitud, offset, ganancia).
- Realizar mediciones de impedancia y leer temperatura, DC, etc.
- Ejecutar barridos (sweeps) y calibraciones.

No necesitas ser un experto en electrónica ni en Python para seguir esta guía — cada paso incluye explicaciones y qué esperar.

-------------------------------------------------------------------------------

Requisitos e instalación
------------------------

Requisitos mínimos:

- Python 3.8 o superior
- Paquete Python `pyserial` (para manejar la comunicación serie)

Instalación rápida:

1) Con pip (usuario actual):

```bash
python3 -m pip install --user "pyserial>=3.5"
```

2) En un entorno virtual (recomendado para desarrollo):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install "pyserial>=3.5"
```

Explicación para dummies:
- `pyserial` permite que Python hable por un puerto serie (como cuando conectas el ADMX2001 por USB).
- Un entorno virtual es como una caja que contiene sólo las librerías que necesita este proyecto, así no ensucias el Python del sistema.

-------------------------------------------------------------------------------

Permisos y detección del puerto (Linux)
--------------------------------------

Cuando conectas el EVAL-ADMX2001 por USB, el sistema crea un archivo especial en `/dev/` como `/dev/ttyUSB0` o `/dev/ttyACM0`.

1) Para ver qué puertos serie hay disponibles ejecuta:

```bash
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

2) Si no aparece nada o al intentar abrir el puerto obtienes un error de permisos, agrega tu usuario al grupo `dialout` (comando que requiere privilegios):

```bash
sudo usermod -a -G dialout $USER
# Cierra sesión y vuelve a iniciar sesión para que el cambio tenga efecto
```

Explicación para dummies:
- El sistema operativo controla el acceso a los dispositivos. Añadir tu usuario a `dialout` le da permiso para usar puertos serie.

-------------------------------------------------------------------------------

Conceptos básicos: ¿qué hace la librería? (para dummies)
-------------------------------------------------------

Imagina que el ADMX2001 es una persona que habla por texto (línea de comandos). Tú le envías instrucciones como "pon la frecuencia a 1kHz" y él responde con números (por ejemplo: magnitud, fase). `levalib` es el traductor entre tu programa Python y esa persona.

Elementos clave:
- Puerto: la puerta por la que hablamos (ej. `/dev/ttyUSB0`).
- Comandos: frases cortas que le mandamos al dispositivo (ej. `frequency 1000`).
- Respuesta: lo que el dispositivo devuelve (ej. "0, 10.0, -5.0").
- Parsers: funciones que convierten las respuestas en números útiles (ej. calcular magnitud y fase).

-------------------------------------------------------------------------------

Uso rápido — ejemplo mínimo (funciona si tienes el dispositivo conectado)
-----------------------------------------------------------------------

Archivo ejemplo `quick_example.py`:

```python
from lib.levalib import ADMX2001

PORT = '/dev/ttyUSB0'  # Cambia esto a tu puerto real

def main():
    try:
        with ADMX2001(PORT) as dev:
            print('Conectado:', dev.is_connected)
            res = dev.quick_impedance_measurement(1000)  # 1 kHz
            if res['impedance']['success']:
                z = res['impedance']
                print(f"|Z| = {z['magnitude']:.2f} Ω, fase = {z['phase_degrees']:.1f}°")
            else:
                print('Error en medición:', res['impedance'].get('error'))
    except Exception as e:
        print('Error general:', e)

if __name__ == '__main__':
    main()
```

Ejecuta:

```bash
python3 quick_example.py
```

Qué esperar:
- Si todo está bien verás los resultados de impedancia y la temperatura.
- Si falla, el script imprimirá un error; revisa puerto y permisos.

-------------------------------------------------------------------------------

API completa (explicada detalladamente)
--------------------------------------

La clase central es `ADMX2001` (archivo `lib/levalib.py`). A continuación se listan los métodos más útiles con una explicación clara, ejemplos de entrada/salida y notas "para dummies".

Constructor y atributos
- `ADMX2001(port, baudrate=115200, timeout=2.0)`
  - Qué hace: abre el puerto serie y trata de inicializar comunicación.
  - Parámetros: `port` (ej. `/dev/ttyUSB0`), `baudrate` (velocidad, por defecto 115200), `timeout` (segundos para esperar respuestas).
  - Atributos importantes:
    - `is_connected` (bool): True si la conexión fue exitosa.
    - `last_error` (str): Mensaje del último error ocurrido.

Nota para dummies: el constructor intenta conectar de inmediato. Si prefieres manejo manual de errores, envuelve la creación en try/except.

Comandos básicos (sistema y ayuda)
- `get_idn()` — pide identificación del dispositivo (firmware/hardware)
- `version()` — versión de firmware
- `help(command=None)` — ayuda del dispositivo
- `reset()` — reinicia el dispositivo
- `abort()` — aborta operación en curso

Ejemplo:

```python
dev.get_idn()
dev.version()
```

Mediciones principales
- `measure_impedance()`
  - Qué hace: ejecuta la secuencia `initiate` -> `trigger` y devuelve las líneas en bruto que contienen la medición.
  - Retorna: lista de cadenas; por ejemplo `['0, 100.0, -50.0']`.
  - Nota: usar `parse_impedance_result()` para convertir en valores numéricos.

- `measure_dcr()` — mide resistencia DC (DCR)
- `measure_vdc()` — mide voltaje DC
- `measure_idc()` — mide corriente DC
- `get_temperature()` — lee la temperatura interna

Configuración de señal
- `set_frequency(freq)` — configura la frecuencia de excitación en Hz
  - Validaciones: rango permitido 1–100000 Hz (1 Hz a 100 kHz).
  - Optimización: usa cache para no re-enviar el mismo valor repetidamente.

- `set_magnitude(val)` — amplitud en voltios (0.01–2.0 V)
- `set_offset(val)` — offset DC (-2.0–2.0 V)
- `set_gain_auto()` — modo auto de ganancia
- `set_gain_ch0(gain)` — ganancia manual del canal 0 (0–3)

Promediado y repeticiones
- `set_average(n)` — promedios internos (1–100)
- `set_count(n)` — número de mediciones repetidas (1–100)

Formatos y display
- `set_display(mode)` — controla qué aparece en la salida
- `set_format(fmt)` — formato `ascii` o `hex`

Sweeps (barridos)
- `sweep_frequency(start, end)` — define inicio y fin de sweep
- `sweep_scale(mode)` — `log` o `linear`
- `sweep_points(n)` — número de puntos
- `sweep_run()` — ejecuta el sweep y devuelve respuesta cruda

Calibración
- `calibrate_open()`, `calibrate_short()`, `calibrate_load(r, x)` — cal disponible
- `calibrate_commit(timestamp=None)` — guarda en flash
- `calibrate_reload()`, `calibrate_erase()`, `calibrate_list()`

GPIO y auxiliares
- `gpio_ctrl(value)` — controlar pines GPIO
- `gpio_read()` — leer estado GPIO
- `led(state)` — controlar LED (`on`, `off`, `blink`)

Parsing y utilidades
- `send_command(cmd, priority='auto', cache_result=False, keep_raw_response=False)`
  - Envío genérico de comandos
  - Implementa delays adaptativos, limpieza de respuesta y caching opcional

- `parse_impedance_result(raw_result)`
  - Convierte una lista de líneas crudas en diccionario con `magnitude`, `phase_degrees`, `resistance`, `reactance`, `conductance`, `susceptance`, `timestamp`, etc.

- `parse_temperature_result(raw_result)`
  - Extrae un valor de temperatura si la línea contiene `deg C`.

- `quick_impedance_measurement(frequency=1000)`
  - Flujo "todo en uno": configura frecuencia, parámetros básicos, realiza medición, parsea resultado y lee temperatura. Retorna diccionario estructurado con `impedance`, `temperature`, `measurement_info`.

-------------------------------------------------------------------------------

Ejemplos avanzados (con explicaciones paso a paso)
-----------------------------------------------

1) Sweep de frecuencia y guardado a CSV

```python
from lib.levalib import ADMX2001
import csv

PORT = '/dev/ttyUSB0'

with ADMX2001(PORT) as dev:
    dev.sweep_frequency(100, 100000)  # 100 Hz a 100 kHz
    dev.sweep_scale('log')
    dev.sweep_points(50)
    raw = dev.sweep_run()

    # raw puede ser una lista de líneas. Aquí hacemos un parse sencillo asumiendo 'freq, mag, phase' por línea
    rows = []
    for line in raw:
        if ',' in line:
            parts = [p.strip() for p in line.split(',')]
            rows.append(parts)

    with open('sweep.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['freq', 'magnitude', 'phase'])
        writer.writerows(rows)

    print('Sweep guardado en sweep.csv')
```

Explicación para dummies:
- El dispositivo puede devolver las líneas en distintos formatos según firmware. Aquí asumimos que cada línea tiene `freq, magnitude, phase`. Si tu firmware devuelve otro formato, ajusta el parseo.

2) Calibración rápida

```python
with ADMX2001('/dev/ttyUSB0') as dev:
    print('Inicia calibración open...')
    dev.calibrate_open()
    input('Conecta short y presiona Enter para calibrate short...')
    dev.calibrate_short()
    input('Conecta carga conocida y presiona Enter para calibrate load...')
    dev.calibrate_load(100.0, 0.0)  # ejemplo: 100 ohm, 0 reactancia
    dev.calibrate_commit()
    print('Calibración guardada')
```

Explicación:
- La calibración mejora la exactitud. `calibrate_commit()` guarda los coeficientes en la memoria del dispositivo.

3) Detección de tipo de componente (R/L/C) básica

```python
with ADMX2001('/dev/ttyUSB0') as dev:
    freqs = [100, 1000, 10000]
    results = []
    for f in freqs:
        r = dev.quick_impedance_measurement(f)
        if r['impedance']['success']:
            results.append((f, r['impedance']['phase_degrees']))

    # Regla simple: phase > +45 -> inductivo; phase < -45 -> capacitivo; else resistivo
    for f, ph in results:
        if ph > 45:
            kind = 'Inductor probable'
        elif ph < -45:
            kind = 'Capacitor probable'
        else:
            kind = 'Resistor probable'
        print(f"{f} Hz: {ph:.1f}° -> {kind}")
```

-------------------------------------------------------------------------------

Debugging y manejo de errores (paso a paso)
-----------------------------------------

1) Error al abrir puerto (SerialException):
- Verifica el nombre del puerto (`ls /dev/ttyUSB* /dev/ttyACM*`).
- Revisa permisos (`ls -l /dev/ttyUSB0`).
- Asegúrate de que no haya otro proceso usando el puerto (`lsof /dev/ttyUSB0`).

2) Sin respuesta o respuestas con caracteres raros:
- Activa logging detallado en la librería:

```python
import logging
logging.getLogger('ADMX2001').setLevel(logging.DEBUG)
```

- Inspecciona `dev.last_error` después de una operación fallida.
- Usa `send_command('help')` o `send_command('version')` para ver si el dispositivo responde a comandos simples.

3) `quick_impedance_measurement` devuelve `success=False` en `impedance`:
- Imprime `raw_response` dentro del diccionario devuelto para ver las líneas exactas retornadas.
- Aumenta `average` y `count` para ver si es ruido.

Explicación para dummies:
- Muchas veces el problema no es Python sino el cable, el puerto o que el dispositivo esté en un estado inesperado. Probar comandos simples (como `version`) ayuda a aislar si el problema es de conexión o de medición.

-------------------------------------------------------------------------------

Tests y desarrollo
------------------

Recomendación: usar `pytest` para pruebas unitarias del parsing y lógica no dependiente del hardware.

Ejemplo de test para `parse_impedance_result`:

```python
def test_parse_impedance_basic():
    from lib.levalib import ADMX2001
    dummy = ADMX2001.__new__(ADMX2001)
    raw = ["0, 10.0, -5.0"]
    out = ADMX2001.parse_impedance_result(dummy, raw)
    assert out['success']
    assert abs(out['magnitude'] - ((10.0**2 + (-5.0)**2)**0.5)) < 1e-6

```

Ejecución de tests:

```bash
pip install pytest
pytest -q
```

-------------------------------------------------------------------------------

Preguntas frecuentes (FAQ)
-------------------------

P: ¿Puedo usar la librería sin el hardware?
A: Parcialmente. Los parsers y utilidades puras funcionan, pero comandos que envían/reciben por serie requieren el dispositivo.

P: ¿Qué hago si mi firmware responde en otro formato?
A: Usa `send_command` para obtener la respuesta cruda y ajusta `parse_impedance_result` o crea una función de parseo personalizada.

P: ¿Cómo recuperar la configuración por defecto?
A: `dev.reset()` reinicia el dispositivo; algunas calibraciones pueden requerir `calibrate_reload()`.

-------------------------------------------------------------------------------

Siguientes pasos sugeridos (puedo implementarlos ahora)
-----------------------------------------------------

1) Generar un Jupyter Notebook con ejemplos interactivos y gráficos de sweeps.
2) Crear una carpeta `tests/` con tests unitarios (pytest) y ejecutarlos.
3) Añadir un pequeño CLI `tools/measure.py` para ejecutar mediciones desde la terminal y guardar CSV.

Dime cuál quieres que implemente ahora y lo hago (crear archivos, tests y/o notebook y ejecutar tests si corresponde).

-------------------------------------------------------------------------------

Licencia: MIT (ver cabecera en `lib/levalib.py`).
# EVAL-ADMX2001 — levalib

Documentación completa y ejemplos de uso para la biblioteca `levalib` (control del analizador de impedancia EVAL-ADMX2001) ubicada en `lib/levalib.py`.

> Nota: Este README está en español y busca ser una guía práctica, técnica y exhaustiva para usuarios y desarrolladores.

## Resumen

`levalib` es una biblioteca Python para controlar el EVAL-ADMX2001 (Analog Devices) vía puerto serie (USB-UART). Proporciona:

- Conexión y manejo robusto de serie
- Comandos de configuración y medición (frecuencia, magnitud, offset, ganancia, promedio, etc.)
- Medición y parseo de impedancia, temperatura, DCR, Vdc, Idc
- Barridos (sweeps), calibración y control GPIO
- Mecanismos internos: caching, delays adaptativos, logging y métricas de rendimiento

Archivo principal: `lib/levalib.py` (clase `ADMX2001`).

## Requisitos

- Python 3.8 o superior
- pyserial >= 3.5

Instalación rápida del requisito:

```bash
python3 -m pip install --user "pyserial>=3.5"
```

Si vas a usar un entorno virtual (recomendado):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install "pyserial>=3.5"
```

## Estructura del proyecto

- `lib/levalib.py` — Implementación completa de la clase `ADMX2001`.
- `README.md` — Este archivo.

Si ejecutas scripts desde la raíz del repositorio, importa mediante `from lib.levalib import ADMX2001`.

## Primeros pasos: permisos y puerto serie (Linux)

1. Conecta el EVAL-ADMX2001 por USB.
2. Identifica el puerto (por ejemplo `/dev/ttyUSB0` o `/dev/ttyACM0`):

```bash
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

3. Si falta permiso, agrega tu usuario al grupo `dialout`:

```bash
sudo usermod -a -G dialout $USER
# Cierra sesión o reinicia la sesión para que tome efecto
```

## Uso básico

Ejemplo mínimo (context manager recomendado):

```python
from lib.levalib import ADMX2001

PORT = "/dev/ttyUSB0"  # Cambiar según tu sistema

with ADMX2001(PORT) as dev:
    # Medición rápida a 1 kHz
    res = dev.quick_impedance_measurement(1000)
    if res['impedance']['success']:
        imp = res['impedance']
        print(f"|Z| = {imp['magnitude']:.2f} Ω, phase = {imp['phase_degrees']:.2f}°")
    else:
        print("Error en medición:", res['impedance'].get('error'))

    # Temperatura del dispositivo
    if res['temperature']['success']:
        print(f"Temperatura: {res['temperature']['temperature_celsius']:.1f}°C")

```

Nota: `ADMX2001.__init__` intenta conectar inmediatamente y realiza una lectura básica de info. Usa try/except para manejo de errores en entornos no interactivos.

## Importante: cómo importar según tu proyecto

- Si ejecutas desde la raíz del repo: `from lib.levalib import ADMX2001`.
- Si copias `levalib.py` al directorio de tu script: `from levalib import ADMX2001`.

## API principal (resumen)

La clase principal es `ADMX2001`. A continuación se listan los métodos más usados por categoría, con breve descripción y ejemplo de uso.

Conexión y estado:

- `ADMX2001(port, baudrate=115200, timeout=2.0)` — Constructor.
- `is_connected` — Atributo booleano de estado.

Comandos de ayuda y sistema:

- `get_idn()` — Identifica firmware/hardware.
- `help(command=None)` — Muestra ayuda.
- `version()` — Versión de firmware.
- `reset()`, `abort()` — Control básico del dispositivo.

Mediciones principales:

- `measure_impedance()` — Ejecuta secuencia `initiate` + `trigger` y devuelve respuesta cruda.
- `measure_dcr()` — Mide resistencia DC.
- `measure_vdc()` — Mide voltaje DC.
- `measure_idc()` — Mide corriente DC.
- `get_temperature()` — Lee temperatura interna.

Configuración de excitación y señal:

- `set_frequency(freq)` — Configura frecuencia (Hz). Usa caching.
- `set_magnitude(val)` — Amplitud en V.
- `set_offset(val)` — Offset DC en V.
- `set_gain_auto()`, `set_gain_ch0(gain)`, `set_gain_ch1(gain)` — Control de ganancia.

Promediado y repeticiones:

- `set_average(n)` — Promedios internos (1-100).
- `set_count(n)` — Repeticiones de medición (1-100).

Display y formato:

- `set_display(mode)` — Modo de visualización.
- `set_format(fmt)` — `ascii` o `hex`.

Sweeps (barridos):

- `sweep_frequency(start, end)` — Define barrido en frecuencia.
- `sweep_scale(mode)` — `log` o `linear`.
- `sweep_points(n)` — Puntos del sweep.
- `sweep_run()` — Ejecuta el sweep.

Calibración:

- `calibrate_open()`, `calibrate_short()`, `calibrate_load(r, x)` — Calibraciones.
- `calibrate_commit(timestamp=None)`, `calibrate_reload()`, `calibrate_erase()` — Gestión de calibraciones en flash.

GPIO y auxiliares:

- `gpio_ctrl(value)`, `gpio_read()` — Control/lectura GPIO.
- `led(state)` — Control del LED: `on`, `off`, `blink`.

Herramientas y parsing:

- `send_command(cmd, ...)` — Envío de comando arbitrario con delays adaptativos y cache.
- `parse_impedance_result(raw)` — Parsea la respuesta cruda y calcula magnitud, fase, conductancia, etc.
- `parse_temperature_result(raw)` — Extrae valor de temperatura de la respuesta.
- `quick_impedance_measurement(freq=1000)` — Flujo todo-en-uno (configura, mide, parsea, incluye temperatura).

Ejemplo: medición avanzada con parseo manual

```python
from lib.levalib import ADMX2001

with ADMX2001('/dev/ttyUSB0') as dev:
    dev.set_frequency(1000)
    dev.set_magnitude(0.5)
    raw = dev.measure_impedance()
    parsed = dev.parse_impedance_result(raw)
    if parsed['success']:
        print('R =', parsed['resistance'], 'Ω')
        print('X =', parsed['reactance'], 'Ω')
        print('|Z| =', parsed['magnitude'], 'Ω')
    else:
        print('Parse error:', parsed.get('error'))

```

Uso de `quick_impedance_measurement` (recomendado para la mayoría de casos):

```python
with ADMX2001('/dev/ttyUSB0') as dev:
    r = dev.quick_impedance_measurement(10000)  # 10 kHz
    if r['impedance']['success']:
        print(f"{r['impedance']['magnitude']:.2f} Ω @ {r['impedance']['frequency_hz']} Hz")
    else:
        print('Error:', r['impedance'].get('error'))

```

### Sweeps de frecuencia

Ejemplo para ejecutar un sweep logarítmico de 100 Hz a 100 kHz con 50 puntos:

```python
with ADMX2001('/dev/ttyUSB0') as dev:
    dev.sweep_frequency(100, 100000)
    dev.sweep_scale('log')
    dev.sweep_points(50)
    resp = dev.sweep_run()
    # `resp` puede contener líneas con datos; parsea según firmware
    print('Sweep ejecutado, respuesta (primeras líneas):', resp[:10])

```

## Manejo de errores y debugging

- `ADMX2001.last_error` contiene el último error con mensaje legible.
- Usa logging para diagnóstico: la librería usa `logging.getLogger('ADMX2001')`.
  Para ver más detalles activa DEBUG:

```python
import logging
logging.getLogger('ADMX2001').setLevel(logging.DEBUG)
```

- Si no hay respuesta del dispositivo, revisa:
  - Puerto correcto
  - Permisos de dispositivo
  - Cable y alimentación
  - Versión de firmware (algunas respuestas dependen de firmware)

## Performance y consideraciones internas

La biblioteca implementa:

- Caching de configuraciones para evitar comandos redundantes (ej. `set_frequency`).
- Delays adaptativos por tipo de comando (perfil rápido/normal/estable/slow).
- Lectura robusta con limpieza de códigos ANSI y detección del prompt `ADMX2001>`.
- Métricas disponibles vía `get_performance_metrics()`.

Consejos de uso:

- Para barridos largos, reduce `average` o aumenta `sweep_points` con cuidado: tiempo total ≈ count × average × tiempo_por_punto.
- Para máxima repetibilidad, usa ganancia manual fija y desconecta el modo `set_gain_auto()`.

## Troubleshooting común

- No se abre `/dev/ttyUSB0`:
  - Verifica permisos, usa `ls -l /dev/ttyUSB0`.
  - Comprueba que no haya otro proceso usando el puerto (`lsof /dev/ttyUSB0`).

- Respuestas con caracteres raros:
  - Activar `logging` en DEBUG para ver líneas crudas.
  - `levalib` intenta limpiar códigos ANSI, pero firmware inusual puede requerir parsing adicional.

- Mediciones inesperadas (valores erráticos):
  - Verifica conexiones físicas, tierra común entre instrumento y DUT
  - Aumenta `average` y/o `count` para estabilizar
  - Revisa configuración de `magnitude` y `offset`

## Buenas prácticas

- Usa context manager (`with ADMX2001(...) as dev:`) para asegurar cierre ordenado.
- Antes de mediciones críticas, realizar una calibración (`calibrate_open`, `calibrate_short`, `calibrate_commit`).
- Registrar `get_performance_metrics()` periódicamente para detectar cambios de rendimiento.

## Desarrollo y tests

Si vas a desarrollar sobre la biblioteca:

1. Crea un entorno virtual.
2. Instala dependencias (`pyserial`).
3. Añade tests unitarios pequeños para funciones de parseo (`parse_impedance_result`, `parse_temperature_result`).

Ejemplo de test mínimo (pytest):

```python
def test_parse_impedance_basic():
    from lib.levalib import ADMX2001
    dummy = ADMX2001.__new__(ADMX2001)
    raw = ["0, 10.0, -5.0"]
    out = ADMX2001.parse_impedance_result(dummy, raw)
    assert out['success']
    assert abs(out['magnitude'] - (10.0**2 + (-5.0)**2)**0.5) < 1e-6

```

## Notas sobre compatibilidad y firmware

Algunas respuestas y formatos dependen de la versión de firmware del dispositivo. `levalib` implementa normalizaciones (por ejemplo unidades de frecuencia) y tolerancias, pero si tu firmware tiene un formato no estándar es posible que necesites adaptar ligeramente el parser o usar `send_command` para inspeccionar respuestas crudas.

## Contribuciones

Si deseas contribuir:

1. Haz fork y crea una rama con cambios claros.
2. Añade tests para nuevas funcionalidades.
3. Abre un Pull Request con la descripción de cambios y motivación.

Por favor mantén el estilo de documentación en español y asegúrate de no incluir secretos.

## Licencia

Proyecto licenciado bajo MIT (ver cabecera en `lib/levalib.py`).

---

Si quieres, puedo:

- Añadir ejemplos de Jupyter Notebook con gráficos de sweeps.
- Generar tests unitarios automáticos y un pequeño script CLI para ejecutar mediciones.

Dime cuál de esos siguientes pasos prefieres y lo implemento.
# libeval
# libeval
