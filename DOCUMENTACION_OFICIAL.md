# EVAL-ADMX2001 LCR Meter - Documentación Oficial

> **Nota Importante**: Esta página aplica a las revisiones de hardware B y C, y versiones de firmware 1.3.1, 1.3.2, y 1.3.3.

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Contenido del Kit](#contenido-del-kit)
3. [Inicio Rápido](#inicio-rápido)
   - [Instalación de Drivers](#1-instalación-de-drivers)
   - [Terminal Emulator](#2-instalación-del-emulador-de-terminal)
   - [Configuración de Hardware](#3-configuración-básica-de-hardware)
   - [Abrir Sesión](#4-abrir-sesión-con-teraterm)
   - [Mediciones Básicas](#5-realizar-mediciones-básicas)
4. [Uso del Sistema de Ayuda CLI](#uso-del-sistema-de-ayuda-cli)
5. [Guía de Uso](#guía-de-uso)
   - [Modos de Display](#modos-de-display-de-medición)
   - [Selección de Rango](#selección-de-rango-de-medición)
   - [Estimación de Impedancia](#estimación-de-impedancia-y-admitancia)
   - [Reducción de Ruido](#reducción-de-ruido-en-mediciones)
   - [Mejora de Precisión](#mejora-de-precisión)
   - [Barridos Paramétricos](#barridos-paramétricos-sweeps)
   - [Mediciones DC](#mediciones-de-resistencia-dc)
   - [Graficación de Datos](#graficación-de-datos)
   - [Optimización de Timing](#optimización-de-timing-de-medición)
6. [Calibración](#procedimiento-de-calibración)
   - [Pasos de Calibración](#pasos-de-calibración)
   - [Ejemplo de Calibración](#ejemplo-de-calibración)
   - [Calibración sobre Frecuencia](#calibración-sobre-frecuencia)
   - [Coeficientes Precargados](#conjuntos-de-calibración-precargados)
7. [Descripción de Terminales](#descripción-de-terminales-eval-admx2001ebz)
8. [Interfaz SPI](#interfaz-spi)
9. [Puertos Trigger](#puertos-de-entrada--salida-trigger)
10. [Actualización de Firmware](#actualizaciones-de-firmware)
11. [Scripting Python](#scripting-python)
12. [GUI Python](#interfaz-gráfica-python)
13. [Soporte](#soporte)

---

## Introducción

El **EVAL-ADMX2001 LCR Meter Demo** es un sistema de evaluación que comprende tanto la placa **ADMX2001B** como la **EVAL-ADMX2001EBZ**.

### ADMX2001B - Módulo Analizador de Impedancia

- **Altamente compacto**: System-on-Module (SOM) de 1.5 × 2.5 pulgadas
- **Mediciones de resistencia DC** o impedancia de 0.2 Hz a 10 MHz
- **Canales de adquisición de 18 bits**
- Opera desde una **fuente única de 3.3V**
- Interfaces **UART y SPI** flexibles
- **18 formatos de display** en unidades SI

### EVAL-ADMX2001EBZ - Placa de Evaluación

- **Conectores BNC** para sondas y accesorios de medición LCR estándar
- **Interfaz UART** para cables USB-to-UART que se conectan a PC
- Señales de **trigger y sincronización de reloj** disponibles mediante conectores SMA
- **Headers estilo Arduino** para desarrollo embebido (ej. SDP-K1)
- **Conector de alimentación** que acepta adaptadores AC/DC de +5V a +12V

---

## Contenido del Kit

### EVAL-ADMX2001EBZ Evaluation Kit Incluye:
- Placa **EVAL-ADMX2001EBZ**
- Cable **UART a USB** (TTL-232R-RPI)
- Adaptador de corriente universal con salida de **9VDC**
- **Pinzas de prueba** para medidor LCR

### Equipo Adicional Requerido:
- **Módulo ADMX2001B** High-Performance Precision Impedance Analyzer

> ⚠️ **IMPORTANTE**: Es crítico comprar **AMBOS** el módulo **ADMX2001B** y la placa de demostración **EVAL-ADMX2001EBZ**. Se venden por separado.

### Equipo Opcional:
- Accesorios para medidor LCR (fixtures, cables, adaptadores)
- Estándares y accesorios de calibración (resistores, capacitores, terminaciones open/short)
- Medidor LCR para verificación y transferencia de calibración

---

## Inicio Rápido

Cinco pasos simples para comenzar a evaluar el ADMX2001:

### 1. Instalación de Drivers

La interfaz de comunicación por defecto al EVAL-ADMX2001EBZ es mediante su puerto UART. Al usar el cable UART a USB incluido (TTL-232R-RPI), se deben descargar los drivers **Virtual COM Port (VCP)** de FTDI.

**Pasos de instalación:**
1. Descargar el **setup executable** del driver para tu sistema operativo desde: https://www.ftdichip.com/Drivers/VCP.htm
2. Descomprimir y ejecutar el setup
3. **Conectar el cable USB to UART al PC**
4. Abrir el Administrador de Dispositivos
5. Verificar que el Puerto Serial USB aparezca bajo "Ports (COM & LPT)" con un identificador asignado

### 2. Instalación del Emulador de Terminal

Para comunicarse con el ADMX2001B mediante su interfaz de línea de comandos y UART, se recomienda un emulador de terminal como **TeraTerm**.

**Descargar TeraTerm** desde: https://github.com/TeraTermProject/teraterm/releases

> 💡 **Tip**: TeraTerm soporta códigos de escape ANSI que manipulan posición del cursor y color de texto. Alternativas como PuTTY pueden tener problemas.

### 3. Configuración Básica de Hardware

**Pasos de configuración:**

1. **Insertar el módulo ADMX2001B** en la placa EVAL-ADMX2001EBZ (los conectores tienen guía)
2. **Configurar switches de carga** a OPEN y GND para el self-test
3. **Conectar el adaptador de corriente** al conector de alimentación y al tomacorriente
4. **Verificar** que el LED de self-test esté verde (en la parte inferior del módulo)
5. **Conectar cable UART a USB**:
   - TX (naranja) → TX
   - RX (amarillo) → RX  
   - GND (negro) → GND
6. **Verificar** que el jumper CLK_SEL esté en posición INT (reloj interno)
7. **Configurar switches** a DUT y GND
8. **Usar las pinzas de prueba** para conectar al dispositivo bajo prueba (DUT):
   - Conectores BNC rojos → puertos HCUR/HPOT
   - Conectores BNC negros → puertos LPOT/LCUR

> ⚠️ **IMPORTANTE**: Inspeccionar los conectores BNC de las pinzas. La carcasa puede aflojarse parcialmente. Al usar en configuración "open", cada pinza debe sujetar su propio trozo de alambre para asegurar conexión eléctrica.

#### Funcionalidad de Self-Test

Cuando el ADMX2001B se enciende, ejecuta automáticamente un self-test. El LED bicolor:
- **Verde**: Pasa el self-test
- **Verde/Rojo**: Falla el self-test  
- **Rojo**: Problema mayor (alimentación, firmware faltante, etc.)

Para pasar el componente analógico del self-test, los switches S1 y S2 deben estar en OPEN y GND.

**Comandos del self-test:**
- `selftest` - Ver estado del último self-test
- `selftest run` - Reejecutar el self-test

### 4. Abrir Sesión con TeraTerm

**Configuración de TeraTerm:**

1. Abrir TeraTerm y elegir conexión **Serial**
2. Seleccionar el puerto COM identificado en el Administrador de Dispositivos
3. Ir a Setup → Serial port y configurar:
   - Speed = **115200**
   - Data = **8 bits**
   - Parity = **none**
   - Stop bits = **1 bits**
   - Flow control = **none**
4. Click "New setting"
5. Opcionalmente guardar configuración (Setup → Save setup)

**Para verificar la conexión:**
- Presionar ENTER para mostrar el prompt `ADMX2001>`
- Escribir `*idn` y presionar ENTER para mostrar versión de firmware
- Escribir `help` y presionar ENTER para ver lista de comandos

> 💡 **Nota**: Cerrar la ventana de TeraTerm no resetea la configuración del ADMX2001B de la última sesión.

### 5. Realizar Mediciones Básicas

Al abrir una sesión, el ADMX2001B está listo para realizar mediciones de impedancia.

> ⚠️ **IMPORTANTE**: Las mediciones no serán precisas hasta que el módulo haya sido calibrado. Ver sección [Procedimiento de Calibración](#procedimiento-de-calibración).

**Configuración por defecto:**
- Mediciones de impedancia en coordenadas rectangulares
- Señal de 1V pk (magnitude = 1) a 1kHz
- Sin offset DC

Para iniciar una medición: escribir `z` en el prompt y presionar ENTER.

#### Ejemplo

Realizar una medición de capacitancia en paralelo con resistor equivalente (Cp-Rp) a 100kHz con amplitud de 1V (2V pk-pk). Retornar 5 lecturas, cada una promediando 10 muestras:

```
ADMX2001> frequency 100
frequency = 100.0000kHz
ADMX2001> display 9
Measurement model: 9 - Capacitance and equivalent parallel resistance (Cp,Rp)
ADMX2001> magnitude 1
magnitude = 1.0000
ADMX2001> average 10
average = 10
ADMX2001> count 5
sampleCount = 5
ADMX2001> z
0,5.677640e-13,8.062763e+07
1,5.668012e-13,8.305672e+07
2,5.675237e-13,8.208995e+07
3,5.673763e-13,8.276912e+07
4,5.683635e-13,8.463327e+07
```

> 💡 **Info**: Por defecto está seleccionado auto-range. Para deshabilitar, usar el comando `setgain <ch> <setting>` para seleccionar un rango específico.

---

## Uso del Sistema de Ayuda CLI

El comando `help` muestra todos los comandos disponibles desde la interfaz de línea de comandos (CLI).

Para obtener ayuda sobre cualquier comando:
```
ADMX2001> help <comando>
```

**Ejemplo** - Ayuda sobre modos de display:
```
ADMX2001> help display
```

---

## Guía de Uso

### Modos de Display de Medición

El ADMX2001B retorna resultados en uno de 18 modos de display diferentes. El resultado siempre se reporta en la unidad SI base.

| Modo | Nombre | Forma | Unidad SI |
|------|--------|-------|-----------|
| 0 | Capacitancia y resistencia serie equivalente | Cs, Rs | Farads, Ohms |
| 1 | Capacitancia serie y factor de disipación | Cs, D | Farads, Sin dimensión |
| 2 | Capacitancia serie y factor de calidad | Cs, Q | Farads, Sin dimensión |
| 3 | Inductancia y resistencia serie equivalente | Ls, Rs | Henries, Ohms |
| 4 | Inductancia serie y factor de disipación | Ls, D | Henries, Sin dimensión |
| 5 | Inductancia serie y factor de calidad | Ls, Q | Henries, Sin dimensión |
| 6 | Impedancia en coordenadas rectangulares (default) | R, X | Ohms, Ohms |
| 7 | Impedancia en magnitud y fase en grados | Z, deg | Ohms, Grados |
| 8 | Impedancia en magnitud y fase en radianes | Z, rad | Ohms, Radianes |
| 9 | Capacitancia y resistencia paralela equivalente | Cp, Rp | Farads, Ohms |
| 10 | Capacitancia paralela y factor de disipación | Cp, D | Farads, Sin dimensión |
| 11 | Capacitancia paralela y factor de calidad | Cp, Q | Farads, Sin dimensión |
| 12 | Inductancia y resistencia paralela equivalente | Lp, Rp | Henries, Ohms |
| 13 | Inductancia paralela y factor de disipación | Lp, D | Henries, Sin dimensión |
| 14 | Inductancia paralela y factor de calidad | Lp, Q | Henries, Sin dimensión |
| 15 | Admitancia en coordenadas rectangulares | G, B | Siemens, Siemens |
| 16 | Admitancia en magnitud y fase en grados | Y, deg | Siemens, Grados |
| 17 | Admitancia en magnitud y fase en radianes | Y, rad | Siemens, Radianes |
| 18 | Apagado | None | None |

### Selección de Rango de Medición

Por defecto, el ADMX2001B está en modo **auto-ranging**, que optimizará la ganancia de medición de los canales de voltaje y corriente.

> ℹ️ **Info**: El algoritmo de auto-ranging solo se aplica a las condiciones de la primera medición. Al realizar barridos de frecuencia, la impedancia del DUT cambiará y podría salir del rango seleccionado.

El rango de medición está principalmente afectado por la transimpedancia del canal 1 y la magnitud de la señal de prueba.

#### Tabla de Configuraciones de Ganancia de Corriente (Ch1)

| Ganancia Ch1 | Corriente Máxima | Transimpedancia |
|--------------|------------------|-----------------|
| 0 | 25mA | 49.9Ω |
| 1 | 2.5mA | 499Ω |
| 2 | 250uA | 4.99kΩ |
| 3 | 25uA | 49.9kΩ |

#### Tabla de Configuraciones de Ganancia de Voltaje (Ch0)

| Ganancia Ch0 | Rango Máximo de Voltaje | Factor de Ganancia |
|--------------|-------------------------|-------------------|
| 0 | ±2.5V | 1 |
| 1 | ±1.25V | 2 |
| 2 | ±625mV | 4 |
| 3 | ±312.5mV | 8 |

#### Rangos de Medición de Impedancia Recomendados

| Ganancia Ch0 | Ganancia Ch1 | Rango de Impedancia |
|--------------|--------------|---------------------|
| 3 | 0 | < 10Ω |
| 2 | 0 | < 25Ω |
| 1 | 0 | < 50Ω |
| 0 | 0 | 100Ω a 1kΩ |
| 0 | 1 | 1kΩ a 10kΩ |
| 0 | 2 | 10kΩ a 100kΩ |
| 0 | 3 | > 100kΩ |

**Comandos:**
```
ADMX2001> setgain ch0 <0-3>    # Configurar ganancia de voltaje
ADMX2001> setgain ch1 <0-3>    # Configurar ganancia de corriente
ADMX2001> setgain auto         # Activar auto-ranging
ADMX2001> setgain              # Ver configuración actual
```

### Estimación de Impedancia y Admitancia

Para dispositivos capacitivos e inductivos:

**Impedancia:**
- Capacitores: `Z = X = -1/(2πfC)`
- Inductores: `Z = X = 2πfL`
- Resistores: `Z = R`

**Admitancia:**
- Capacitores: `Y = B = 2πfC`
- Inductores: `Y = B = -1/(2πfL)`
- Resistores: `Y = G = 1/R`

**Magnitudes:**
- `|Z| = sqrt(R² + X²)`
- `|Y| = sqrt(G² + B²)`

### Reducción de Ruido en Mediciones

El comando `average` determina cuántas muestras se promedian para cada lectura. El promediado reduce el ruido.

```
ADMX2001> average <1-256>
```

> 💡 **Tip**: Valores mayores que 256 tienen poco efecto en la reducción de ruido y impactan significativamente la velocidad de medición.

### Mejora de Precisión

Para mediciones precisas y exactas, se deben usar **fixtures de prueba apropiados**. Los cables de medición pueden introducir errores debido a impedancias parásitas.

> 💡 **Tip**: Las pinzas incluidas con el kit pueden introducir fluctuaciones de pocos picofarads dependiendo de su posición. Este efecto es más notable con frecuencias superiores a 100kHz.

**Fixtures recomendados:**
- Para componentes SMD: B+K Precision TL89S1, Keysight 16034G

### Barridos Paramétricos (Sweeps)

El ADMX2001B puede realizar automáticamente mediciones que barren diferentes parámetros:
- **Frecuencia** (común en EIS - Espectroscopia de Impedancia Electroquímica)
- **Bias DC** (común en mediciones C-V para dispositivos semiconductores)
- **Magnitud**

**Comandos:**
```
ADMX2001> sweep_type frequency <inicio> <fin>
ADMX2001> sweep_scale <log|linear>
ADMX2001> count <número_puntos>
ADMX2001> z
```

#### Ejemplo: Barrido Logarítmico de Frecuencia

Realizar un barrido logarítmico de 11 puntos de 100kHz a 1MHz:

```
ADMX2001> count 11
sampleCount = 11
ADMX2001> sweep_type frequency 100 1000
Frequency
sweepStart = +100.0000KHz
sweepEnd = +1000.0000KHz
ADMX2001> sweep_scale log
Sweep scale is log
ADMX2001> z
1.000000e+05,5.683433e-13,8.149236e+07
1.258925e+05,5.704062e-13,4.727518e+07
...
```

> ℹ️ **Info**: Al barrer parámetros, el primer valor impreso será el parámetro barrido, seguido de la medición en el formato de display seleccionado.

### Mediciones de Resistencia DC

La función de medición de resistencia DC se selecciona fácilmente configurando la frecuencia de prueba a cero:

```
ADMX2001> frequency 0
DC Resistance mode enabled
ADMX2001> display 6
Measurement model: 6 - Impedance in rectangular coordinates (default) (Rs,Xs)
ADMX2001> offset -1
Offset = -1.0000
ADMX2001> z
0,4.995231e+01
```

> ℹ️ **Nota**: En modo de resistencia DC, solo se retorna el valor de resistencia DC. El offset debe ser negativo para detectar saturación.

### Graficación de Datos

TeraTerm permite guardar un log que puede copiarse a un archivo *.csv para abrir con aplicaciones de hojas de cálculo como Microsoft Excel®.

**Pasos:**
1. En TeraTerm: File → Log, guardar con extensión **.csv**
2. Configurar ADMX2001B y ejecutar comando `z`
3. En ventana "TeraTerm:Log", hacer click en close
4. Abrir archivo con Excel
5. Seleccionar datos y crear gráfico scatter

### Optimización de Timing de Medición

Los comandos `mdelay` (measurement delay) y `tdelay` (trigger delay) controlan el tiempo de estabilización entre mediciones:

- **mdelay**: Retardo antes de cada medición (no entre muestras al promediar)
- **tdelay**: Retardo solo después de eventos trigger (útil con multiplexores externos)

```
ADMX2001> mdelay <milisegundos>
ADMX2001> tdelay <milisegundos>
```

#### Optimización de Mediciones de Punto Único

En versión 1.3.2, se añadieron optimizaciones para reducir el tiempo de medición:

**Modo Trigger:**
- Usar `initiate` para entrar en modo trigger
- Usar `trigger` para ejecutar medición
- Los atributos se bloquean, ahorrando tiempo de configuración
- Mediciones típicas: 10-12 ms

**Factores para mediciones más rápidas:**
1. **Interfaz**: SPI es la más rápida
2. **Fuente de trigger**: Comando SPI TRIGGER (0x18) es preferido
3. **Trigger count**: `tcount 65536` para modo trigger infinito
4. **Autorange**: Deshabilitado para máxima velocidad
5. **Delays**: `tdelay 0` y `mdelay 0` típicamente seguros
6. **Frecuencia**: Mediciones más rápidas sobre ~3 kHz
7. **Display mode**: Formatos rectangulares (modos 6, 15) son los más rápidos

---

## Procedimiento de Calibración

Después del encendido, el ADMX2001B está listo para realizar mediciones, pero la precisión solo puede evaluarse después de realizar calibración con una fuente externa certificada.

### Pasos Básicos de Calibración

Tres pasos básicos de calibración:
1. **Open calibration** - Corrige parásitas del módulo y cables de prueba
2. **Short calibration** - Corrige parásitas (puede omitirse en ciertos rangos)
3. **Load calibration** - Proporciona trazabilidad a fuente externa

> ⚠️ **IMPORTANTE**: Los pasos deben realizarse en orden: open → short → load

> 💡 **Tip**: Al realizar calibración de carga para una configuración de ganancia y frecuencia, el dispositivo de carga óptimo (usualmente resistor) es uno con magnitud de impedancia cercana al DUT eventual.

### Configuraciones de Calibración

Cada configuración de front-end (combinación de ganancia ch0 y ch1) necesita calibrarse por separado. Hay 16 combinaciones posibles.

> ℹ️ **Info**: Si se usa autorange o solo las 7 combinaciones de ganancia estándar, las otras configuraciones no necesitan calibrarse.

> ⚠️ **IMPORTANTE**: Cada punto de calibración es para una frecuencia específica. Las mediciones a diferentes frecuencias pueden estar fuera de tolerancia. Siempre calibrar lo más cerca posible de la frecuencia de prueba deseada.

### Pasos de Calibración

1. Seleccionar la configuración de medición deseada (ganancia, frecuencia, magnitud, offset)
   - ⚠️ **Autorange debe estar deshabilitado durante calibración**
2. Configurar promediado a al menos 200 muestras: `average 200`
3. Asegurar que los switches estén en posiciones DUT y GND
4. Conectar terminales H_POT/H_CUR juntos y L_POT/L_CUR juntos
5. Ejecutar `calibrate open`
6. Conectar todas las terminales juntas
   - ⚠️ Short calibration solo cuando ganancia canal 1 es 0 o 1
7. Ejecutar `calibrate short` (si es posible)
8. Conectar impedancia conocida entre cables de medición
9. Ejecutar `calibrate rt <valor1> xt <valor2>`
   - valor1 = componente resistivo (Ohms)
   - valor2 = componente reactivo (Ohms)

### Guardar Calibración

Después de completar los pasos, los coeficientes se generan y almacenan en RAM. Para guardarlos en memoria no volátil (flash):

```
ADMX2001> calibrate commit <timestamp>
PASSWORD> Analog123
```

El timestamp es opcional (segundos desde 01/01/1970 UTC).

> ℹ️ **Info**: La contraseña por defecto es `Analog123`. Puede cambiarse con `calibrate password`.

### Ejemplo de Calibración

Calibrar configuración de ganancia (0, 1) a 100kHz con resistor de 1kΩ:

```
ADMX2001> setgain ch0 0
voltGain = 0
ADMX2001> setgain ch1 1
currGain = 1
ADMX2001> frequency 100
frequency = 100.0000kHz
ADMX2001> magnitude 1
magnitude = 1.0000
ADMX2001> offset 0
Offset = 0.0000
ADMX2001> average 200
average = 200
ADMX2001> tdelay 200
triggerDelay = 200.0000msec

# Conectar carga open ahora
ADMX2001> calibrate open
0,-1.117998e-09,1.162904e-06
Frequency = 100.0000kHz
Cal Temp: 41.4 deg C
open:Done
short:Not Done
load:Not Done

ADMX2001> magnitude 0.2
magnitude = 0.2000

# Conectar carga short ahora
ADMX2001> calibrate short
0,2.075835e-02,1.224807e-02
Frequency = 100.0000kHz
Cal Temp: 41.4 deg C
open:Done
short:Done
load:Not Done

ADMX2001> magnitude 1
magnitude = 1.0000

# Conectar carga de calibración (resistor 1kΩ)
ADMX2001> calibrate rt 1e+3 xt 0.822
0,1.010381e+03,-1.254483e+01
Frequency = 100.0000kHz
Cal Temp: 41.5 deg C
open:Done
short:Done
load:Done

ADMX2001> calibrate commit 1689959855
PASSWORD> Analog123
commit : success

ADMX2001> display 6
Measurement model: 6 - Impedance in rectangular coordinates (default) (Rs,Xs)
ADMX2001> z
0,1.000021e+03,8.220137e-01
```

### Lectura y Escritura de Coeficientes

**Leer coeficientes:**
```
ADMX2001> rdcal <vgain> <igain>
```

**Escribir coeficientes:**
```
ADMX2001> storecal <vgain> <igain> <nombre_coeficiente> <valor>
```

### Calibración sobre Frecuencia

Desde firmware versión 1.2.2, se implementó soporte para calibración sobre múltiples frecuencias. Esto permite calibrar todas las 16 configuraciones de ganancia en múltiples puntos de frecuencia.

**Comandos nuevos:**
- `resetcal` - Borra solo el conjunto de calibración cargado actualmente de RAM
- `calibrate reload` - Carga los coeficientes de frecuencia más cercana desde memoria no volátil
- `calibrate erase` - Elimina permanentemente todos los conjuntos de calibración (¡requiere contraseña!)
- `calibrate list` - Reporta todas las frecuencias con datos de calibración guardados
- `calibrate list <freq>` - Reporta qué configuraciones de ganancia están calibradas a una frecuencia

**Capacidad de almacenamiento:**
- Módulos con **EEPROM**: 25 conjuntos de calibración
- Módulos con **Flash**: 450 conjuntos de calibración

### Conjuntos de Calibración Precargados

Versión 1.2.2 añade soporte para módulos ADMX2001B que envían con coeficientes de calibración precargados.

**Comandos:**
```
ADMX2001> calibrate switch <evalkit|default>
```
- `evalkit` - Aplica coeficientes precargados
- `default` - Aplica coeficientes generados por usuario

> ℹ️ **Nota**: Los coeficientes precargados pueden no aplicar a una configuración de prueba dada y su precisión no está garantizada.

---

## Descripción de Terminales EVAL-ADMX2001EBZ

| Terminal | Descripción |
|----------|-------------|
| **H_CUR** | Terminal de fuente de señal. Genera la excitación requerida para medición. Puede proveer hasta ±5V @ 50mA |
| **H_POT** | Terminal de sensado de voltaje. Conectar a H_CUR en el DUT |
| **L_POT** | Terminal de sensado de voltaje. Conectar a L_CUR en el DUT |
| **L_CUR** | Terminal de sensado de corriente. Ruta de retorno para señal de excitación |
| **UART TX** | Pin transmisor UART. Lógica 3.3V |
| **UART RX** | Pin receptor UART. Lógica 3.3V |
| **UART GND** | Tierra UART |
| **CLK_SEL** | Selección de reloj interno o externo por jumper |
| **TRIG_IN** | Entrada de trigger. Para adquisición sincronizada por hardware |
| **TRIG_OUT** | Salida de trigger al completar medición |
| **CLK_IN** | Entrada de reloj externo. Usar señal LVCMOS 50MHz |
| **CLK_OUT** | Salida de reloj. Réplica del reloj principal de 50MHz |
| **PMOD** | Terminales PMOD para puerto SPI |
| **P6[9-10]** | Salidas digitales 0-1 |
| **P7[1-6]** | Salidas digitales 2-7 |

---

## Interfaz SPI

El ADMX2001B soporta interfaz SPI además de la interfaz UART CLI. El bus SPI es accesible en Header P6 y headers PMOD del EVAL-ADMX2001EBZ.

**Referencia completa de comandos SPI:** Contactar soporte para documentación detallada.

---

## Puertos de Entrada / Salida Trigger

El EVAL-ADMX2001EBZ tiene terminales SMA para puertos de entrada y salida de trigger. Pueden usarse para sincronizar múltiples módulos o controlar timing de medición con instrumento externo.

**Configurar modo trigger externo:**
```
ADMX2001> trig_mode external
ADMX2001> tcount <cantidad>
ADMX2001> initiate
```

**Modo trigger infinito:**
```
ADMX2001> tcount 65536
```

**Características del pulso trigger:**
- Voltaje: 3.3V
- Duración mínima: 15μs

> ⚠️ **Advertencia**: Al ejecutar `initiate`, la placa recarga automáticamente datos de calibración desde flash. Cualquier coeficiente no guardado se perderá.

---

## Actualizaciones de Firmware

El firmware del módulo ADMX2001B es actualizable por el usuario. Los archivos de programación deben solicitarse contactando admx-support@analog.com.

> ⚠️ **Advertencia**: Actualizar entre ciertas versiones de firmware puede causar pérdida de coeficientes de calibración guardados.

### Lista de Equipo Requerido:
- Placa EVAL-ADMX2001EBZ
- Módulo ADMX2001B
- Intel Altera USB Blaster
- Adaptador de corriente 9VDC

### Software Requerido:
- Python 3.7 o superior
- Intel Quartus Prime Programmer And Tools (última versión)
- Drivers para Altera USB Blaster
- Carpeta de firmware conteniendo archivo *.pof

### Método de Actualización con Script

**Versiones 1.2.4+** incluyen script de instalación:

```bash
python admx2001_flash_pof.py --pof "C:\Analog Devices\Admx2001Firmware-Relx.y.z\Firmware\admx_lcr_encrypted.pof"
```

> ⚠️ **IMPORTANTE**: No desconectar la placa ni interrumpir el proceso de programación. El proceso toma 20-30 segundos.

### Versiones de Firmware Disponibles

| Versión | Estado | Características Principales |
|---------|--------|----------------------------|
| 1.3.2 | Estable | Optimizaciones de tiempo de medición, correcciones menores |
| 1.3.1 | Estable | Mejoras sustanciales de ruido, correcciones y más |
| 1.2.4 | Estable | Mismo firmware que 1.2.2, script de instalación añadido |
| 1.2.2 | Estable | Calibración sobre frecuencia, salidas digitales configurables, soporte trigger externo |
| 1.2.0 | Estable | Correcciones, mejoras de ruido y repetibilidad |
| 1.1.1 | Legacy | Mismas correcciones que 1.2.0, no compatible con placas con flash |
| 1.1.0 | Legacy | Interfaz SPI añadida, self test integrado |
| 1.0.1 | Legacy | - |
| 1.0.0 | Legacy | - |

---

## Scripting Python

Para facilitar la optimización de mediciones en PC, existe una biblioteca de funciones Python que facilita operar la interfaz de línea de comandos desde un script Python.

**Disponibilidad**: Por solicitud contactando admx-support@analog.com

La descarga incluye scripts de ejemplo que muestran cómo:
- Configurar puerto Serial
- Configurar mediciones
- Recolectar datos
- Realizar barridos

---

## Interfaz Gráfica Python

Desde firmware versión 1.3.2, las descargas de firmware incluyen una interfaz gráfica de usuario (GUI) basada en Python.

**Características actuales:**
- Selección de ganancia automática y manual
- Mediciones calibradas
- Mediciones continuas o singulares
- 18 modos de display en unidades SI
- Configuraciones de frecuencia, offset, magnitud y promediado

**Requisitos**: Bibliotecas Python de terceros (instrucciones en README.txt incluido)

**Disponibilidad**: Por solicitud contactando admx-support@analog.com

---

## Soporte

Para soporte, preguntas generales o ayuda con actualización de firmware:

**Email**: admx-support@analog.com

---

*Documento basado en la documentación oficial de Analog Devices para EVAL-ADMX2001*
