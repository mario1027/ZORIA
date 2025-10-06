# ⏱️ Implementación de Delays Nativos del Dispositivo

## Resumen de Cambios

Se ha actualizado el dashboard para usar correctamente los comandos de delay nativos del dispositivo ADMX2001 (`mdelay` y `tdelay`) en lugar de delays de Python (`time.sleep()`), siguiendo la documentación oficial.

---

## 🎯 Optimización de Timing de Medición

### Conceptos Clave

Según la documentación oficial del ADMX2001, el tiempo de medición depende de varios factores:
- Tiempo de transmisión de comandos
- Delays configurados (**mdelay** y **tdelay**)
- Tiempo de setup de la fuente
- Tiempo de adquisición del ADC
- Configuración de `count` y `average`

**Objetivo**: Reducir tiempo de medición a ~10-12 ms (firmware 1.3.2+)

---

## 📊 Comandos de Delay del Dispositivo

### 1. **mdelay** (Measurement Delay)

**Definición**: Delay observado **antes de cada medición**, pero **no entre muestras** durante averaging.

**Uso**:
```python
device.set_mdelay(1)  # 1 ms de delay
```

**Características**:
- ✅ Se aplica antes de cada medición
- ✅ Se aplica durante sweeps
- ✅ Se aplica entre múltiples counts
- ⚠️ NO se aplica entre samples al promediar
- 🔋 Durante el delay: DC offset y señal AC están habilitados
- 📊 ADCs no capturan hasta que transcurre el delay

**Cuándo usar**:
- `mdelay 0`: Máxima velocidad (mediciones rápidas)
- `mdelay 1-5`: Balance velocidad/estabilidad
- `mdelay 10-200`: DUTs capacitivos grandes que necesitan settling time
- `mdelay 200+`: Calibración de alta precisión

### 2. **tdelay** (Trigger Delay)

**Definición**: Delay observado **solo después de eventos de trigger** controlados por `tcount`.

**Uso**:
```python
device.set_tdelay(0)  # Sin trigger delay
device.set_tdelay(10) # 10 ms para multiplexores
```

**Características**:
- ✅ Útil con tarjetas de escaneo o multiplexores externos
- ✅ Permite debounce y settling time
- 🔋 Si está configurado, DC offset se habilita durante tdelay
- ⚡ Señal AC solo inicia para captura de datos

**Cuándo usar**:
- `tdelay 0`: No se usan triggers externos (modo normal)
- `tdelay 5-20`: Con multiplexores o switches
- `tdelay 50+`: Settling time largo para configuraciones complejas

---

## 🔧 Implementación en el Dashboard

### 1. **Interfaz de Usuario**

**En Control y Medición:**
```python
dbc.Label("⏱️ Delays (ms):", className="mt-2"),
dbc.Row([
    dbc.Col([
        dbc.Label("mdelay:", style={'fontSize': '0.9em'}),
        dbc.Input(id="realtime-mdelay", type="number", 
                  value=1, min=0, max=10000, step=1, size="sm"),
        html.Small("0-10000", className="text-muted")
    ], width=6),
    dbc.Col([
        dbc.Label("tdelay:", style={'fontSize': '0.9em'}),
        dbc.Input(id="realtime-tdelay", type="number",
                  value=0, min=0, max=10000, step=1, size="sm"),
        html.Small("0-10000", className="text-muted")
    ], width=6)
])
```

**En Barridos:**
- Mismo diseño de controles
- Valor por defecto mdelay: -1 (auto)
- Valor por defecto tdelay: 0

### 2. **Conexión Inicial**

```python
def handle_connection(connect_n, disconnect_n, port):
    if triggered == 'connect-btn' and port:
        device = ADMX2001(port, timeout=5.0)
        is_connected.set()
        
        # Configurar delays iniciales
        device.set_mdelay(1)  # 1ms por defecto
        device.set_tdelay(0)  # Sin triggers
        
        return "Conectado", "success", {'connected': True}
```

### 3. **Aplicar Configuración**

```python
def apply_config(n, freq, mag, offset, display_mode, mdelay, tdelay):
    device.set_frequency(freq)
    device.set_magnitude(mag)
    device.set_offset(offset)
    device.set_display_mode(DisplayMode(display_mode))
    
    # Configurar delays desde la UI
    if mdelay is not None and 0 <= mdelay <= 10000:
        device.set_mdelay(mdelay)
    else:
        device.set_mdelay(1)  # Default
    
    if tdelay is not None and 0 <= tdelay <= 10000:
        device.set_tdelay(tdelay)
    else:
        device.set_tdelay(0)  # Default
```

### 4. **Barridos con Auto-configuración**

```python
def sweep_worker(config):
    mdelay = config.get('mdelay', -1)  # -1 = auto
    tdelay = config.get('tdelay', 0)
    
    # Modo automático según frecuencia
    if mdelay == -1:
        if start >= 10000:      # > 10 kHz
            actual_mdelay = 0   # Máxima velocidad
        elif start >= 1000:     # 1-10 kHz
            actual_mdelay = 1   # Balance
        else:                   # < 1 kHz
            actual_mdelay = 2   # Estabilidad
        device.set_mdelay(actual_mdelay)
    else:
        device.set_mdelay(mdelay)
    
    device.set_tdelay(tdelay)
```

---

## 📈 Secuencia de Medición

### Single Measurement
```
[mdelay] → [Medición ADC] → [Retorno datos]
   1ms         ~10ms            <1ms
```

### Multiple Samples (Average)
```
[mdelay] → [S1] → [S2] → ... → [SN] → [Promedio]
   1ms     ~10ms   ~10ms        ~10ms     <1ms
   
⚠️ mdelay solo se aplica una vez al inicio
```

### Multiple Counts
```
Count 1: [mdelay] → [Medición] → [Retorno]
Count 2: [mdelay] → [Medición] → [Retorno]
Count 3: [mdelay] → [Medición] → [Retorno]
```

### Con Triggers
```
Trigger 1: [tdelay] → [mdelay] → [Medición] → [Retorno]
Trigger 2: [tdelay] → [mdelay] → [Medición] → [Retorno]
```

---

## 🎯 Recomendaciones de Uso

### Para Mediciones Rápidas
```python
device.set_mdelay(0)      # Sin delay
device.set_average(1)     # Sin promediado
device.set_count(1)       # Single measurement
```
**Resultado**: ~10-12 ms por medición

### Para Mediciones Estables
```python
device.set_mdelay(1)      # 1 ms delay
device.set_average(10)    # 10 promedios
device.set_count(1)       # Single count
```
**Resultado**: ~100-120 ms, más estable

### Para DUTs Capacitivos
```python
device.set_mdelay(10)     # 10 ms settling time
device.set_average(10)    # 10 promedios
```
**Resultado**: Mayor precisión en capacitores grandes

### Para Calibración
```python
device.set_mdelay(200)    # 200 ms settling
device.set_average(200)   # 200 promedios
device.set_tdelay(200)    # 200 ms trigger delay
```
**Resultado**: Máxima precisión

---

## 🚀 Beneficios de la Implementación

### ✅ Ventajas

1. **Rendimiento Optimizado**
   - Delays manejados por firmware
   - Timing preciso y consistente
   - Aprovecha optimizaciones del hardware

2. **Configuración Flexible**
   - Ajuste desde interfaz UI
   - Auto-configuración inteligente
   - Control manual disponible

3. **Cumplimiento con Documentación**
   - Usa comandos nativos del dispositivo
   - Best practices oficiales
   - Compatible con firmware 1.3.2+

4. **Mejor Estabilidad**
   - Delays aplicados en momento correcto
   - Sincronización hardware
   - Menos errores de timing

### ❌ Eliminado

1. **time.sleep() innecesarios**
   - ❌ Delays arbitrarios en Python
   - ❌ Delays entre configuraciones
   - ✅ Solo sleep(0.1) en worker para CPU

2. **Delays redundantes**
   - ❌ Pre/post medición delays
   - ✅ Dispositivo maneja todo

---

## 📊 Comparativa: Antes vs Después

### ❌ Antes (con time.sleep())

```python
device.set_frequency(freq)
time.sleep(0.1)  # ❌ Innecesario

device.set_magnitude(mag)
time.sleep(0.05)  # ❌ Innecesario

time.sleep(0.05)  # ❌ Pre-medición
val1, val2 = device.measure()
time.sleep(0.05)  # ❌ Post-medición
time.sleep(0.4)   # ❌ Entre mediciones
```

**Problemas**: Lento, impreciso, no sincronizado

### ✅ Después (con mdelay/tdelay)

```python
# Configuración una vez
device.set_frequency(freq)
device.set_magnitude(mag)
device.set_mdelay(1)  # ✅ En dispositivo

# Mediciones
val1, val2 = device.measure()  # ✅ mdelay automático
time.sleep(0.1)  # ✅ Solo CPU throttle
```

**Beneficios**: Rápido, preciso, sincronizado por hardware

---

## 🔍 Troubleshooting

### Problema: Mediciones inestables
**Solución**: Aumentar mdelay
```python
device.set_mdelay(5)  # Probar 5 ms
```

### Problema: Mediciones muy lentas
**Solución**: Reducir mdelay y average
```python
device.set_mdelay(0)
device.set_average(1)
```

### Problema: Capacitor no se estabiliza
**Solución**: Aumentar mdelay considerablemente
```python
device.set_mdelay(50)  # 50 ms settling
```

---

## 📚 Referencias

- **Documentación Oficial**: [DOCUMENTACION_OFICIAL.md](DOCUMENTACION_OFICIAL.md#optimización-de-timing-de-medición)
- **Sección**: "Optimizing Measurement Timing"
- **Subsección**: "Delay Usage and Measurement Sequencing"
- **README**: [README.md](README.md)
- **Índice**: [INDICE.md](INDICE.md)

---

**Implementado**: Octubre 2025  
**Versión Dashboard**: 3.2  
**Firmware Compatible**: 1.3.2+
