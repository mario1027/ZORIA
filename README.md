# EVAL-ADMX2001 - Analizador de Impedancia de Precisión# EVAL-ADMX2001 - Analizador de Impedancia de Precisión



Sistema completo de control, medición y análisis para el analizador de impedancia **EVAL-ADMX2001** de Analog Devices.Sistema completo de control, medición y análisis para el analizador de impedancia **EVAL-ADMX2001** de Analog Devices.



[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)



------



## 📋 Contenido## 📋 Tabla de Contenidos



- [Descripción](#-descripción)- [Descripción](#-descripción)

- [Características](#-características)- [Características](#-características)

- [Instalación Rápida](#-instalación-rápida)- [Estructura del Proyecto](#-estructura-del-proyecto)

- [Uso Básico](#-uso-básico)- [Instalación Rápida](#-instalación-rápida)

- [Documentación](#-documentación)- [Uso Básico](#-uso-básico)

- [Soporte](#-soporte)- [Documentación](#-documentación)

- [Dashboard Web](#-dashboard-web)

---- [Biblioteca Python](#-biblioteca-python)

- [Soporte](#-soporte)

## 🎯 Descripción- [Licencia](#-licencia)



Este proyecto proporciona una solución completa para trabajar con el **EVAL-ADMX2001**, incluyendo:---



- **Biblioteca Python** (`lib/`) - Control completo del dispositivo vía puerto serie## 🎯 Descripción

- **Dashboard Web Interactivo** - Interfaz gráfica profesional con Dash/Plotly

- **Documentación Exhaustiva** - Guías, ejemplos y referencia completa de APIEste proyecto proporciona una solución completa para trabajar con el **EVAL-ADMX2001**, incluyendo:



**Características del ADMX2001B:**- **Biblioteca Python** (`lib/`) - Control completo del dispositivo vía puerto serie

- 🔬 Mediciones de impedancia de **0.2 Hz a 10 MHz**- **Dashboard Web Interactivo** - Interfaz gráfica profesional con Dash/Plotly

- 📊 Canales de adquisición de **18 bits**- **Documentación Exhaustiva** - Guías, ejemplos y referencia completa de API

- 🎛️ **18 modos de display** en unidades SI

- 🔌 Interfaces **UART y SPI**El **ADMX2001B** es un módulo analizador de impedancia de alto rendimiento:

- ⚡ Opera desde **3.3V** único- 🔬 Mediciones de impedancia de **0.2 Hz a 10 MHz**

- 📊 Canales de adquisición de **18 bits**

---- 🎛️ **18 modos de display** en unidades SI

- 🔌 Interfaces **UART y SPI**

## ✨ Características- ⚡ Opera desde **3.3V** único



### Biblioteca Python (`lib/`)---

- ✅ Conexión y comunicación robusta por puerto serie

- ✅ Configuración completa (frecuencia, magnitud, offset, ganancia, promediado)## ✨ Características

- ✅ Mediciones de impedancia, temperatura, DCR, Vdc, Idc

- ✅ Barridos (frequency sweeps, EIS)### Biblioteca Python (`lib/`)

- ✅ Sistema de calibración completo- ✅ Conexión y comunicación robusta por puerto serie

- ✅ Control GPIO y LED- ✅ Configuración completa (frecuencia, magnitud, offset, ganancia, promediado)

- ✅ Caching inteligente y delays adaptativos- ✅ Mediciones de impedancia, temperatura, DCR, Vdc, Idc

- ✅ Métricas de rendimiento integradas- ✅ Barridos (frequency sweeps, EIS)

- ✅ Sistema de calibración completo

### Dashboard Web- ✅ Control GPIO y LED

- 🖥️ Interfaz profesional con Bootstrap y Plotly- ✅ Caching inteligente y delays adaptativos

- 📊 Visualización en tiempo real- ✅ Métricas de rendimiento integradas

- 📈 Gráficos de Bode y Nyquist interactivos

- 🔄 Barridos de frecuencia con actualización en vivo### Dashboard Web

- 🛠️ Control total de configuración del dispositivo- 🖥️ Interfaz profesional con Bootstrap y Plotly

- 💾 Exportación de datos a CSV- 📊 Visualización en tiempo real

- 🎨 Diseño responsive y moderno- 📈 Gráficos de Bode y Nyquist interactivos

- 🔄 Barridos de frecuencia con actualización en vivo

---- 🛠️ Control total de configuración del dispositivo

- 💾 Exportación de datos a CSV

## 📁 Estructura del Proyecto- 🎨 Diseño responsive y moderno



```---

EVAL-ADMX2001-relase 1.0/

├── README.md                          # Este archivo## 📁 Estructura del Proyecto

├── requirements.txt                   # Dependencias Python

├── dashboard_complete.py              # Dashboard web principal```

│EVAL-ADMX2001-relase 1.0/

├── lib/                               # Biblioteca Python├── 📄 README.md                          # Este archivo

│   ├── __init__.py├── 📄 requirements.txt                   # Dependencias Python

│   ├── admx2001.py                    # Driver principal├── 🐍 dashboard_complete.py              # Dashboard web principal

│   ├── calibration.py                 # Sistema de calibración│

│   ├── enums.py                       # Enumeraciones├── 📚 lib/                               # Biblioteca Python

│   ├── exceptions.py                  # Excepciones personalizadas│   ├── __init__.py

│   └── utils.py                       # Utilidades│   ├── admx2001.py                       # Driver principal

││   ├── calibration.py                    # Sistema de calibración

└── Documentación/                     # Documentación en Markdown│   ├── enums.py                          # Enumeraciones

    ├── DOCUMENTACION_OFICIAL.md       # Manual oficial del hardware│   ├── exceptions.py                     # Excepciones personalizadas

    ├── README_LIB.md                  # API de la biblioteca│   └── utils.py                          # Utilidades

    ├── README_DASHBOARD.md            # Guía del dashboard│

    ├── INICIO_RAPIDO.md               # Guía de inicio rápido└── 📖 docs/                              # Documentación

    └── ...                            # Más guías y reportes    ├── DOCUMENTACION_OFICIAL.md          # Manual oficial del hardware

```    ├── README_LIB.md                     # Documentación de la biblioteca

    ├── README_DASHBOARD.md               # Guía del dashboard

---    ├── INICIO_RAPIDO.md                  # Guía de inicio rápido

    ├── INSTRUCCIONES_USO.md              # Instrucciones detalladas

## ⚡ Instalación Rápida    └── ...                               # Reportes y guías adicionales

```

### 1. Requisitos

---

- **Python 3.8+**

- **Puerto USB disponible**Requisitos e instalación

- **Linux**: Permisos para acceder a `/dev/ttyUSB*`------------------------



### 2. Instalar DependenciasRequisitos mínimos:



```bash- Python 3.8 o superior

pip install -r requirements.txt- Paquete Python `pyserial` (para manejar la comunicación serie)

```

Instalación rápida:

### 3. Configurar Permisos (Linux)

1) Con pip (usuario actual):

```bash

# Agregar usuario al grupo dialout```bash

sudo usermod -a -G dialout $USERpython3 -m pip install --user "pyserial>=3.5"

# Reiniciar sesión para que tome efecto```

```

2) En un entorno virtual (recomendado para desarrollo):

### 4. Verificar Puerto

```bash

```bashpython3 -m venv .venv

ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/nullsource .venv/bin/activate

```pip install "pyserial>=3.5"

```

---

Explicación para dummies:

## 🚀 Uso Básico- `pyserial` permite que Python hable por un puerto serie (como cuando conectas el ADMX2001 por USB).

- Un entorno virtual es como una caja que contiene sólo las librerías que necesita este proyecto, así no ensucias el Python del sistema.

### Biblioteca Python

-------------------------------------------------------------------------------

```python

from lib import ADMX2001Permisos y detección del puerto (Linux)

--------------------------------------

# Conectar al dispositivo

with ADMX2001('/dev/ttyUSB0') as device:Cuando conectas el EVAL-ADMX2001 por USB, el sistema crea un archivo especial en `/dev/` como `/dev/ttyUSB0` o `/dev/ttyACM0`.

    # Configurar frecuencia

    device.set_frequency(1000)  # 1 kHz1) Para ver qué puertos serie hay disponibles ejecuta:

    

    # Realizar medición```bash

    result = device.measure()ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null

    print(f"Z = {result[0]} Ω")```

```

2) Si no aparece nada o al intentar abrir el puerto obtienes un error de permisos, agrega tu usuario al grupo `dialout` (comando que requiere privilegios):

### Dashboard Web

```bash

```bashsudo usermod -a -G dialout $USER

python dashboard_complete.py# Cierra sesión y vuelve a iniciar sesión para que el cambio tenga efecto

``````



Abrir navegador en: **http://localhost:8050**Explicación para dummies:

- El sistema operativo controla el acceso a los dispositivos. Añadir tu usuario a `dialout` le da permiso para usar puertos serie.

---

-------------------------------------------------------------------------------

## 📖 Documentación

Conceptos básicos: ¿qué hace la librería? (para dummies)

### Documentación Principal-------------------------------------------------------



| Documento | Descripción |Imagina que el ADMX2001 es una persona que habla por texto (línea de comandos). Tú le envías instrucciones como "pon la frecuencia a 1kHz" y él responde con números (por ejemplo: magnitud, fase). `levalib` es el traductor entre tu programa Python y esa persona.

|-----------|-------------|

| **[Documentación Oficial](DOCUMENTACION_OFICIAL.md)** | Manual completo del hardware EVAL-ADMX2001 |Elementos clave:

| **[Biblioteca Python](README_LIB.md)** | API completa y ejemplos de uso |- Puerto: la puerta por la que hablamos (ej. `/dev/ttyUSB0`).

| **[Dashboard](README_DASHBOARD.md)** | Guía del dashboard web interactivo |- Comandos: frases cortas que le mandamos al dispositivo (ej. `frequency 1000`).

| **[Inicio Rápido](INICIO_RAPIDO.md)** | Primeros pasos y configuración |- Respuesta: lo que el dispositivo devuelve (ej. "0, 10.0, -5.0").

| **[Instrucciones](INSTRUCCIONES_USO.md)** | Guía detallada de operación |- Parsers: funciones que convierten las respuestas en números útiles (ej. calcular magnitud y fase).



### Guías Especializadas-------------------------------------------------------------------------------



| Guía | Tema |Uso rápido — ejemplo mínimo (funciona si tienes el dispositivo conectado)

|------|------|-----------------------------------------------------------------------

| [Guía Rápida](GUIA_RAPIDA.md) | Referencia rápida de comandos |

| [Optimización Sweeps](OPTIMIZACION_SWEEPS.md) | Optimización de barridos |Archivo ejemplo `quick_example.py`:

| [Solución Timeouts](SOLUCION_TIMEOUTS.md) | Solución de problemas |

| [Mejoras Bode](MEJORAS_BODE_DIAGRAM.md) | Mejoras en diagramas |```python

| [Mejoras UX](MEJORAS_UX_DASHBOARD.md) | Experiencia de usuario |from lib.levalib import ADMX2001

| [Resultados Pruebas](RESULTADOS_PRUEBAS_BARRIDOS.md) | Pruebas exhaustivas |

PORT = '/dev/ttyUSB0'  # Cambia esto a tu puerto real

### Reportes Técnicos

def main():

| Reporte | Contenido |    try:

|---------|-----------|        with ADMX2001(PORT) as dev:

| [Resumen Ejecutivo V3.2](RESUMEN_EJECUTIVO_V3.2.md) | Resumen de la versión actual |            print('Conectado:', dev.is_connected)

| [Reporte Verificación](REPORTE_VERIFICACION.md) | Verificación de funcionalidades |            res = dev.quick_impedance_measurement(1000)  # 1 kHz

| [Reporte Coherencia](REPORTE_COHERENCIA.md) | Análisis de coherencia |            if res['impedance']['success']:

| [Resumen Optimizaciones](RESUMEN_OPTIMIZACIONES.md) | Optimizaciones implementadas |                z = res['impedance']

                print(f"|Z| = {z['magnitude']:.2f} Ω, fase = {z['phase_degrees']:.1f}°")

---            else:

                print('Error en medición:', res['impedance'].get('error'))

## 🔧 Ejemplos    except Exception as e:

        print('Error general:', e)

### Ejemplo 1: Medición Simple

if __name__ == '__main__':

```python    main()

from lib import ADMX2001```



with ADMX2001('/dev/ttyUSB0') as device:Ejecuta:

    device.set_frequency(1000)

    z_real, z_imag = device.measure()```bash

    z_magnitude = (z_real**2 + z_imag**2)**0.5python3 quick_example.py

    print(f"|Z| = {z_magnitude:.2f} Ω")```

```

Qué esperar:

### Ejemplo 2: Barrido de Frecuencia- Si todo está bien verás los resultados de impedancia y la temperatura.

- Si falla, el script imprimirá un error; revisa puerto y permisos.

```python

from lib import ADMX2001, SweepScale-------------------------------------------------------------------------------



with ADMX2001('/dev/ttyUSB0') as device:API completa (explicada detalladamente)

    device.sweep_frequency(100, 100000)--------------------------------------

    device.sweep_scale(SweepScale.LOG)

    device.sweep_points(50)La clase central es `ADMX2001` (archivo `lib/levalib.py`). A continuación se listan los métodos más útiles con una explicación clara, ejemplos de entrada/salida y notas "para dummies".

    data = device.sweep_run()

```Constructor y atributos

- `ADMX2001(port, baudrate=115200, timeout=2.0)`

### Ejemplo 3: Calibración  - Qué hace: abre el puerto serie y trata de inicializar comunicación.

  - Parámetros: `port` (ej. `/dev/ttyUSB0`), `baudrate` (velocidad, por defecto 115200), `timeout` (segundos para esperar respuestas).

```python  - Atributos importantes:

from lib import ADMX2001    - `is_connected` (bool): True si la conexión fue exitosa.

    - `last_error` (str): Mensaje del último error ocurrido.

with ADMX2001('/dev/ttyUSB0') as device:

    device.calibrate_open()Nota para dummies: el constructor intenta conectar de inmediato. Si prefieres manejo manual de errores, envuelve la creación en try/except.

    device.calibrate_short()

    device.calibrate_load(1000.0, 0.0)Comandos básicos (sistema y ayuda)

    device.calibrate_commit()- `get_idn()` — pide identificación del dispositivo (firmware/hardware)

```- `version()` — versión de firmware

- `help(command=None)` — ayuda del dispositivo

---- `reset()` — reinicia el dispositivo

- `abort()` — aborta operación en curso

## 💡 Solución de Problemas

Ejemplo:

### No se puede abrir el puerto serie

```python

```bashdev.get_idn()

# Verificar puertodev.version()

ls -l /dev/ttyUSB0```



# Agregar permisosMediciones principales

sudo usermod -a -G dialout $USER- `measure_impedance()`

# Reiniciar sesión  - Qué hace: ejecuta la secuencia `initiate` -> `trigger` y devuelve las líneas en bruto que contienen la medición.

```  - Retorna: lista de cadenas; por ejemplo `['0, 100.0, -50.0']`.

  - Nota: usar `parse_impedance_result()` para convertir en valores numéricos.

### Timeouts en mediciones

- `measure_dcr()` — mide resistencia DC (DCR)

- Aumentar timeout: `ADMX2001(port, timeout=10.0)`- `measure_vdc()` — mide voltaje DC

- Reducir promedios: `device.set_average(5)`- `measure_idc()` — mide corriente DC

- Ver [SOLUCION_TIMEOUTS.md](SOLUCION_TIMEOUTS.md)- `get_temperature()` — lee la temperatura interna



### Dashboard no iniciaConfiguración de señal

- `set_frequency(freq)` — configura la frecuencia de excitación en Hz

```bash  - Validaciones: rango permitido 1–100000 Hz (1 Hz a 100 kHz).

# Reinstalar dependencias  - Optimización: usa cache para no re-enviar el mismo valor repetidamente.

pip install --upgrade -r requirements.txt

- `set_magnitude(val)` — amplitud en voltios (0.01–2.0 V)

# Verificar puerto- `set_offset(val)` — offset DC (-2.0–2.0 V)

lsof -i :8050- `set_gain_auto()` — modo auto de ganancia

```- `set_gain_ch0(gain)` — ganancia manual del canal 0 (0–3)



---Promediado y repeticiones

- `set_average(n)` — promedios internos (1–100)

## 📊 Rendimiento- `set_count(n)` — número de mediciones repetidas (1–100)



| Operación | Tiempo Típico |Formatos y display

|-----------|---------------|- `set_display(mode)` — controla qué aparece en la salida

| Medición simple | 10-50 ms |- `set_format(fmt)` — formato `ascii` o `hex`

| Medición optimizada | ~10 ms |

| Barrido 100 puntos | 5-30 s |Sweeps (barridos)

| Calibración completa | 30-60 s |- `sweep_frequency(start, end)` — define inicio y fin de sweep

- `sweep_scale(mode)` — `log` o `linear`

Ver [RESULTADOS_PRUEBAS_BARRIDOS.md](RESULTADOS_PRUEBAS_BARRIDOS.md) para detalles.- `sweep_points(n)` — número de puntos

- `sweep_run()` — ejecuta el sweep y devuelve respuesta cruda

---

Calibración

## 🤝 Soporte- `calibrate_open()`, `calibrate_short()`, `calibrate_load(r, x)` — cal disponible

- `calibrate_commit(timestamp=None)` — guarda en flash

### Recursos- `calibrate_reload()`, `calibrate_erase()`, `calibrate_list()`



- 📖 **Documentación**: Ver archivos `.md` en el proyectoGPIO y auxiliares

- 🌐 **Analog Devices**: https://www.analog.com- `gpio_ctrl(value)` — controlar pines GPIO

- 📧 **Soporte**: admx-support@analog.com- `gpio_read()` — leer estado GPIO

- `led(state)` — controlar LED (`on`, `off`, `blink`)

---

Parsing y utilidades

## 📝 Licencia- `send_command(cmd, priority='auto', cache_result=False, keep_raw_response=False)`

  - Envío genérico de comandos

Licencia MIT - Ver archivo LICENSE  - Implementa delays adaptativos, limpieza de respuesta y caching opcional



---- `parse_impedance_result(raw_result)`

  - Convierte una lista de líneas crudas en diccionario con `magnitude`, `phase_degrees`, `resistance`, `reactance`, `conductance`, `susceptance`, `timestamp`, etc.

## 📅 Versión

- `parse_temperature_result(raw_result)`

**Versión 3.2** (Actual)  - Extrae un valor de temperatura si la línea contiene `deg C`.

- ✨ Dashboard web completo

- 🚀 Optimizaciones de velocidad- `quick_impedance_measurement(frequency=1000)`

- 📊 Mejoras en gráficos  - Flujo "todo en uno": configura frecuencia, parámetros básicos, realiza medición, parsea resultado y lee temperatura. Retorna diccionario estructurado con `impedance`, `temperature`, `measurement_info`.

- 🐛 Correcciones de estabilidad

- 📖 Documentación renovada-------------------------------------------------------------------------------



Ver [RESUMEN_EJECUTIVO_V3.2.md](RESUMEN_EJECUTIVO_V3.2.md) para changelog completo.Ejemplos



---Esta sección recoge ejemplos exhaustivos y documentados de todo lo que puedes hacer con `levalib` y el EVAL-ADMX2001. Cada ejemplo incluye: objetivo, explicación paso a paso, código y qué esperar como salida. Se cubren mediciones individuales, lecturas de temperatura, DCR/Vdc/Idc, sweeps (frecuencia, magnitud, offset), calibración completa, control GPIO, parsing, caching, logging, performance, guardado a CSV y graficado.



**Desarrollado para EVAL-ADMX2001 de Analog Devices**Nota sobre formatos de respuesta: el firmware del ADMX2001 puede variar. Los ejemplos muestran patrones habituales y cómo adaptar el parseo si el formato difiere.



*Última actualización: Octubre 2025*A. Medición simple y parseo (paso a paso)


Objetivo: realizar una medición de impedancia a una frecuencia concreta y obtener los valores numéricos (R, X, |Z|, fase).

Código:

```python
from lib.levalib import ADMX2001

PORT = '/dev/ttyUSB0'

with ADMX2001(PORT) as dev:
  # 1) Configurar la frecuencia deseada (ej. 1 kHz)
  dev.set_frequency(1000)

  # 2) Ajustar magnitud y promedios (opcional)
  dev.set_magnitude(0.5)  # 0.5 V
  dev.set_average(10)     # 10 promedios

  # 3) Ejecutar la medición en bruto
  raw = dev.measure_impedance()

  # 4) Parsear el resultado a valores numéricos
  parsed = dev.parse_impedance_result(raw)

  if parsed['success']:
    print('Resistencia (R):', parsed['resistance'])
    print('Reactancia (X):', parsed['reactance'])
    print('|Z|:', parsed['magnitude'])
    print('Fase (°):', parsed['phase_degrees'])
  else:
    print('No se pudo parsear la medición. Raw response:')
    print(parsed.get('raw_response'))
```

Qué buscar en la salida:
- Si `parsed['success']` es True, tendrás campos numéricos listos para usar.
- Si no, inspecciona `raw` o `parsed['raw_response']` para ajustar el parser.

B. `quick_impedance_measurement` — flujo todo en uno

Objetivo: ejemplo recomendado para uso interactivo — configura, mide, parsea y obtiene temperatura en una sola llamada.

Código:

```python
from lib.levalib import ADMX2001

with ADMX2001('/dev/ttyUSB0') as dev:
  result = dev.quick_impedance_measurement(10000)  # 10 kHz

  imp = result['impedance']
  temp = result['temperature']

  if imp['success']:
    print(f"Impedancia: |Z|={imp['magnitude']:.3f} Ω, fase={imp['phase_degrees']:.2f}° @ {imp.get('frequency_hz', 'N/A')} Hz")
  else:
    print('Error en impedancia:', imp.get('error'))

  if temp['success']:
    print(f"Temperatura interna: {temp['temperature_celsius']:.2f} °C")
  else:
    print('Error leyendo temperatura:', temp.get('error'))
```

Notas:
- `quick_impedance_measurement` hace varias llamadas internas (`set_frequency`, `magnitude 1`, `setgain auto`, `average 10`, `measure_impedance`, `get_temperature`). Revisa `measurement_info` en el resultado para metadatos.

C. Lectura de temperatura y parseo (detallado)

Objetivo: obtener la temperatura interna y usarla para decisiones (p. ej. evitar mediciones críticas si la temperatura es alta).

```python
with ADMX2001('/dev/ttyUSB0') as dev:
  raw_temp = dev.get_temperature()
  temp_parsed = dev.parse_temperature_result(raw_temp)
  if temp_parsed['success']:
    t_c = temp_parsed['temperature_celsius']
    print(f"Temperatura: {t_c:.2f} °C")
    if t_c > 60:
      print('Advertencia: temperatura alta — esperar a estabilizar antes de mediciones críticas')
  else:
    print('No se pudo parsear temperatura. Raw:', raw_temp)
```

D. Medidas DC: DCR, Vdc, Idc

Objetivo: ejemplos para medir resistencia DC, voltaje DC y corriente DC.

```python
with ADMX2001('/dev/ttyUSB0') as dev:
  dcr = dev.measure_dcr()
  vdc = dev.measure_vdc()
  idc = dev.measure_idc()

  print('DCR raw:', dcr)
  print('Vdc raw:', vdc)
  print('Idc raw:', idc)

  # Opcional: intentar parseo simple si la respuesta es una línea con número
  try:
    dcr_val = float(dcr[0]) if dcr and isinstance(dcr[0], str) else None
    print('DCR (Ω):', dcr_val)
  except Exception:
    pass
```

E. Barridos (sweeps) — frecuencia, magnitud y offset (completo)

Objetivo: detallar opciones y cómo ejecutar y parsear sweeps, además de recomendaciones de performance y guardado.

1) Preparación y parámetros clave
- `sweep_frequency(start, end)` — define inicio y fin del barrido (Hz).
- `sweep_scale(mode)` — `'log'` (logarítmico) o `'linear'`.
- `sweep_points(n)` — número de puntos a medir.
- `set_average(n)` y `set_count(n)` afectan el tiempo por punto.

Estimación de tiempo: usar `get_performance_metrics()` y la función interna `_estimate_sweep_time` (si disponible) para prever duración. Como regla rápida: tiempo ≈ puntos × tiempo_por_punto + setup_overhead.

2) Ejecutar un sweep de frecuencia y guardar resultados (CSV)

```python
import csv
from lib.levalib import ADMX2001

with ADMX2001('/dev/ttyUSB0') as dev:
  dev.set_average(5)
  dev.sweep_frequency(100, 100000)
  dev.sweep_scale('log')
  dev.sweep_points(100)
  raw = dev.sweep_run()

  # Parse robusto: detectar líneas con comas y extraer números
  rows = []
  for line in raw:
    # limpiar y comprobar
    if not isinstance(line, str):
      continue
    s = line.strip()
    if not s:
      continue
    if ',' in s:
      parts = [p.strip() for p in s.split(',')]
      rows.append(parts)

  # Guardar CSV (ajusta cabeceras según formato real)
  with open('sweep_freq.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['col1', 'col2', 'col3'])
    writer.writerows(rows)

  print('Sweep guardado en sweep_freq.csv (primeras 5 filas):', rows[:5])
```

3) Graficar sweep con matplotlib (opcional)

```python
import matplotlib.pyplot as plt
import numpy as np

# Asumimos rows como [['freq', 'mag', 'phase'], ...]
freqs = [float(r[0]) for r in rows if len(r) >= 3]
mags = [float(r[1]) for r in rows if len(r) >= 3]
phs = [float(r[2]) for r in rows if len(r) >= 3]

plt.figure()
plt.subplot(2,1,1)
plt.semilogx(freqs, mags)
plt.title('Sweep de frecuencia')
plt.ylabel('|Z|')

plt.subplot(2,1,2)
plt.semilogx(freqs, phs)
plt.ylabel('Fase (°)')
plt.xlabel('Frecuencia (Hz)')
plt.tight_layout()
plt.show()
```

Consejos para sweeps:
- Si el sweep es muy largo, reduce `average` o subdivide el sweep en rangos.
- Para barridos logarítmicos largos, usa menos puntos en las bandas donde no esperas cambios.
- Si el firmware devuelve datos en bloques grandes, `send_command` podría devolver una estructura optimizada; inspecciona `raw` cuidadosamente.

F. Barrido de magnitud y offset

Los comandos `sweep_magnitude(start, end)` o `sweep_offset(start, end)` se usan de forma análoga a `sweep_frequency` y permiten estudiar la respuesta del DUT ante cambios de amplitud o polarización.

G. Calibración completa (procedimiento seguro)

Objetivo: guiar por el proceso de calibración para máxima precisión.

Procedimiento recomendado:

1. Preparación: asegúrate de tener referencias conocidas: open (sin conexión), short (cortocircuito) y load (resistencia conocida).
2. Ejecutar `calibrate_open()` y seguir instrucciones físicas.
3. Ejecutar `calibrate_short()`.
4. Ejecutar `calibrate_load(r, x)` con la resistencia/reactancia conocida.
5. Comprobar resultados parciales (`calibrate_list()` o `rdcal`) y luego `calibrate_commit()` para guardar en flash.

Ejemplo interactivo:

```python
with ADMX2001('/dev/ttyUSB0') as dev:
  input('Coloca OPEN (sin DUT) y presiona Enter...')
  dev.calibrate_open()
  input('Coloca SHORT y presiona Enter...')
  dev.calibrate_short()
  input('Coloca LOAD conocida y presiona Enter...')
  dev.calibrate_load(100.0, 0.0)
  dev.calibrate_commit()
  print('Calibración completada y guardada')
```

H. Control GPIO y LED

Ejemplo: encender LED, leer GPIO y escribir un valor directo.

```python
with ADMX2001('/dev/ttyUSB0') as dev:
  dev.led('on')
  print('GPIO state:', dev.gpio_read())
  dev.gpio_ctrl(0xFF)  # escribir 255 en registros GPIO (según hardware)
  dev.led('blink')
```

I. Ganancia: automática vs manual

- `set_gain_auto()` es recomendable para empezar: el dispositivo ajusta ganancia para evitar saturación.
- Para reproducibilidad máxima, usa `set_gain_ch0(gain)` y `set_gain_ch1(gain)` con valores fijos (0-3).

Ejemplo:

```python
with ADMX2001('/dev/ttyUSB0') as dev:
  dev.set_gain_auto()
  # ... realizar mediciones ...
  dev.set_gain_ch0(3)  # fijar ganancia para mediciones repetibles
```

J. Caching y `send_command` (comportamiento avanzado)

`send_command` acepta `cache_result=True` para almacenar resultados y evitar reenviar comandos de configuración idénticos. Ejemplo:

```python
with ADMX2001('/dev/ttyUSB0') as dev:
  dev.send_command('frequency 1000', cache_result=True)
  # segunda llamada no enviará físicamente el comando si sigue en cache
  dev.send_command('frequency 1000', cache_result=True)
```

Nota: la cache tiene un timeout interno; si necesitas forzar reenvío, no uses `cache_result` o limpia manualmente según implementación.

K. Logging y diagnóstico profundo

Activar debug:

```python
import logging
logging.getLogger('ADMX2001').setLevel(logging.DEBUG)
```

Ejemplo de uso para ver líneas crudas:

```python
with ADMX2001('/dev/ttyUSB0') as dev:
  print('IDN raw:', dev.send_command('*idn'))
```

L. Métricas de rendimiento

Usa `get_performance_metrics()` para obtener estadísticas: uptime, comandos enviados, cache hits/misses, tiempos acumulados.

```python
with ADMX2001('/dev/ttyUSB0') as dev:
  print(dev.get_performance_metrics())
```

M. Manejo robusto de errores en scripts

Plantilla recomendada para scripts automatizados:

```python
from lib.levalib import ADMX2001
import time

def safe_measure(port, freq):
  try:
    with ADMX2001(port) as dev:
      dev.set_frequency(freq)
      dev.set_average(10)
      res = dev.quick_impedance_measurement(freq)
      return res
  except Exception as e:
    # Guardar error y reintentar o abortar según política
    print('Error en medición:', e)
    return None

res = safe_measure('/dev/ttyUSB0', 1000)
if res is None:
  print('Medición fallida')
```

N. Tests y mocking para integración continua

Para funciones de parsing, crea tests unitarios que no dependan del hardware. Para integraciones que sí lo requieren, usa fixtures o mocks (p. ej. `unittest.mock` para simular `serial.Serial`).

Ejemplo de test unitario (parse_impedance_result):

```python
def test_parse_impedance_basic():
  from lib.levalib import ADMX2001
  dummy = ADMX2001.__new__(ADMX2001)
  raw = ["0, 10.0, -5.0"]
  out = ADMX2001.parse_impedance_result(dummy, raw)
  assert out['success']
  assert abs(out['magnitude'] - ((10.0**2 + (-5.0)**2)**0.5)) < 1e-6
```

O. CLI mínimo para mediciones (ejecutable)

Archivo `tools/measure.py` (sugerencia):

```python
#!/usr/bin/env python3
import argparse
from lib.levalib import ADMX2001
import json

parser = argparse.ArgumentParser(description='Medición rápida con EVAL-ADMX2001')
parser.add_argument('--port', required=True)
parser.add_argument('--freq', type=float, default=1000)
parser.add_argument('--out', default='-')
args = parser.parse_args()

with ADMX2001(args.port) as dev:
  r = dev.quick_impedance_measurement(args.freq)
  out = json.dumps(r, indent=2)
  if args.out == '-':
    print(out)
  else:
    with open(args.out, 'w') as f:
      f.write(out)
```

P. Consideraciones finales y adaptaciones por firmware

- Si tu firmware imprime encabezados, prompts o textos extra, ajusta los parsers (buscar líneas con comas numéricas, usar regex para extraer números).
- Para flujos automáticos a largo plazo, monitoriza `get_temperature()` durante el experimento y registra `get_performance_metrics()` para detectar degradación.

---

Fin de la sección de Ejemplos.

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

Aclaraciones y correcciones importantes
---------------------------------------

He revisado la implementación en `lib/levalib.py` y ajustado la documentación para reflejar con precisión el comportamiento actual del código. Estos son puntos críticos que corregimos en la documentación para evitar confusiones:

- connect()/disconnect(): NO existen como métodos en la clase `ADMX2001`.
  - Uso correcto: la clase abre la conexión en el constructor (`__init__`). Para cerrar la conexión use `close()` o preferiblemente el context manager `with ADMX2001(port) as dev:`. Para intentar una reconexión use `reconnect()`.

- Getters explícitos (p. ej. `get_average()`, `get_offset()`, `get_gain()`, `get_frequency()`): no están implementados como métodos separados.
  - Cómo obtener valores actuales:
    - Pregunte al dispositivo con `send_command('<param>')` (por ejemplo `send_command('average')`), si el firmware responde con el valor.
    - La librería mantiene un cache interno (`self._config_cache`) con claves como `'current_frequency'` cuando se usa `set_frequency`. Puede consultar `dev._config_cache.get('current_frequency')` (nota: es API privada).
    - Recomendación: usar `send_command` para consultar el valor la primera vez y luego confiar en `set_*` y en `get_performance_metrics()` para telemetría.

- `is_connected` y comprobación activa:
  - La clase expone un atributo booleano `device.is_connected` que indica el estado conocido internamente.
  - Para una comprobación activa (enviar un comando y verificar respuesta) use `device.is_device_connected()` — este método realiza un ping al dispositivo.
  - Atención: en el código existe una definición de método llamada `is_connected(self)` (versión antigua), pero en la práctica al inicializar la instancia el atributo `is_connected` (bool) sobrescribe ese nombre en la instancia. Para evitar ambigüedad, la documentación recomienda usar `device.is_connected` (atributo) y `device.is_device_connected()` (verificación activa).

- CLI y scripts: el README contiene un ejemplo de `tools/measure.py` como plantilla; ese archivo no está incluido actualmente en el repositorio. Si quieres, puedo añadir ese script tal y como está sugerido en la documentación.

- Formato de respuesta y parsing: el formato exacto de las líneas devueltas por el dispositivo depende del firmware. La documentación ahora insiste en inspeccionar la primera respuesta `raw` y adaptar el parser (`parse_impedance_result`) si es necesario.

Con estas correcciones la documentación queda alineada con la implementación actual y evita llamadas a métodos inexistentes o confusas.


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
.