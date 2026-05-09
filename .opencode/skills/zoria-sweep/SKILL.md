---
name: zoria-sweep
description: Testeo exhaustivo de barridos de frecuencia del EVAL-ADMX2001. Casos extremos: barrido completo 0.2 Hz - 10 MHz, N variable, LOG vs LINEAR, promedios, limites del firmware, timing empirico vs teorico, y bandas sub-Hz (minutos por punto). Solo usar bajo pedido explicito del usuario. Requiere hardware ADMX2001 conectado via TTL232R-3V3 a /dev/ttyUSB0.
---

# ZORIA Sweep

Skill de testeo exhaustivo de barridos para EVAL-ADMX2001. Solo para casos extremos -- usar unicamente cuando el usuario lo pida explicitamente. **Requiere hardware conectado**, sin excepciones.

## Herramientas disponibles

| Script | Proposito | Tiempo estimado |
|---|---|---|
| `python test_sweep_acquisition.py --hw` | Suite A (logica) + Suite B (hardware) | 5-15 min |
| `python test_full_sweep_hw.py --port /dev/ttyUSB0` | Suites C1-C8 exhaustivas | 30-60 min |
| `python test_n_limit_hw.py --port /dev/ttyUSB0` | Mapeo de limite N por decada | 10-20 min |
| `python benchmark_timing.py` | Perfilado empirico de timing | 5-10 min |

## Reglas del firmware (MEMORIZAR)

Estas reglas son la causa del 90% de los fallos en barridos:

1. **N maximo por ancho de banda:**
   ```
   Span < 0.5 dec → hasta 1000 pts
   Span 0.5-1 dec → hasta 500 pts
   Span 1-2 dec   → hasta 300 pts
   Span 2-3 dec   → hasta 255 pts
   Span 3-4 dec   → hasta 200 pts
   Span >= 4 dec  → hasta 100 pts  ← CRITICO
   ```
   `max_count_for_span(start_hz, end_hz)` en `lib/utils.py` calcula esto.

2. **Corrupcion de estado = 10 pts:**
   - Enviar N > limite → firmware se corrompe
   - **Siguiente sweep retorna exactamente 10 pts** (sin importar N solicitado)
   - Esto es un sintoma inequivoco de corrupcion
   - Solucion: **desconectar y reconectar** (no hay comando de reset)

3. **Timing por punto:**
   - 36 ciclos DFT × periodo de la frecuencia
   - Floor: 15ms (frecuencias altas)
   - Overhead fijo por sweep: ~3s
   - `_acquisition_time_ms(freq)` en `lib/utils.py`

4. **Rango de frecuencia:** 0.2 Hz – 10 MHz
   - Sub-Hz: extremadamente lento (0.2 Hz → ~180s/pt)
   - Usar `--include-sub-hz` explicitamente en tests

5. **Baudrate:** 115200 (NO 230400)

## Ejecucion de tests

### Paso previo: detectar puerto

```bash
python -c "
from lib.utils import get_preferred_usb_serial_ports
ports = get_preferred_usb_serial_ports()
for p in ports:
    print(f'{p.device} | {p.description} | prioridad={get_admx_port_priority(p)}')
" 2>/dev/null
```

El puerto con mayor prioridad es el cable TTL232R-3V3 del ADMX2001.

### Suite A — Logica pura (sin hardware)

```bash
python test_sweep_acquisition.py
```

Prueba sin hardware:
- Segmentacion (`max_points_per_segment()`)
- Timing teorico (`_acquisition_time_ms()`)
- Calculo de timeouts (`estimate_sweep_time()`)
- Flujo R/X → Z/phase (`process_point_realtime()`)
- Manejo de errores (MeasurementError, saturacion)
- HardwareTimingProfile (vacio, grabacion, interpolacion log-log)

Suite A deberia pasar 100% siempre. Si falla, hay bug en `lib/utils.py`.

### Suite B — Hardware: conectividad + bandas

```bash
python test_sweep_acquisition.py --hw --port /dev/ttyUSB0
```

Prueba con hardware:
- `*idn` y `selftest`
- 7 bandas de frecuencia (1 Hz – 10 MHz)
- Integridad de datos: frecuencias monotonas, R/X finitos
- Timing profile update (`update_from_sweep()`)
- Segmentacion ZORIA con hardware real

Para rapido (solo bandas altas):
```bash
python test_sweep_acquisition.py --hw --quick
```

### Suites C1-C8 — Exhaustivo

```bash
python test_full_sweep_hw.py --port /dev/ttyUSB0
```

| Suite | Descripcion | N pts | Notas |
|---|---|---|---|
| C1 | Rango completo 0.2 Hz – 10 MHz | 10,20,50,100 | LOG, requiere `--include-sub-hz` |
| C2 | Ancho minimo (2 pts/banda) | 2 por banda | 17 bandas, sub-Hz opcional |
| C3 | Por decadas | 10-20 | 8 decadas |
| C4 | N variable {2,5,10,20,50,100,200,500,1000} | variable | Banda 10 kHz-10 MHz |
| C5 | LOG vs LINEAR | 10-20 | 3 bandas × 2 escalas |
| C6 | Averages {1,2,4,8} | 10 | Verifica scaling lineal de tiempo |
| C7 | Limites N grandes | 500, 1000 | Bandas media y alta |
| C8 | Modos display | 10 | R_X, Z_DEG, CS_RS, LS_RS, CP_RP |

Suite especifica:
```bash
python test_full_sweep_hw.py --port /dev/ttyUSB0 --suite C4
```

Solo rapido (sin sub-Hz):
```bash
python test_full_sweep_hw.py --port /dev/ttyUSB0 --only-fast
```

### N-limit probing

```bash
python test_n_limit_hw.py --port /dev/ttyUSB0
```

Prueba N ∈ {10, 50, 100, 150, 200, 250, 300, 400, 500} en 9 rangos de decada para mapear empiricamente el limite del firmware. Genera tabla resumen de N maximo por decada.

```bash
python test_n_limit_hw.py --port /dev/ttyUSB0 --verbose
```

### Timing profiling

```bash
python benchmark_timing.py --port /dev/ttyUSB0
```

Mide tiempos reales inter-punto en 6 bandas y actualiza `hw_timing_profile.json`. Compara medicion empirica vs modelo teorico (36 DFT + 15ms floor).

Con averages:
```bash
python benchmark_timing.py --port /dev/ttyUSB0 --average 2
```

Incluyendo bandas sub-Hz (muy lento):
```bash
python benchmark_timing.py --port /dev/ttyUSB0 --full
```

Solo mostrar perfil guardado:
```bash
python benchmark_timing.py --show
```

## Interpretacion de resultados

### Resultados esperados (todo OK)
- Frecuencias **monotonas crecientes** (f[i] < f[i+1])
- R/X **finitos** (no NaN, no inf, no None)
- Cantidad de puntos recibidos **== cantidad solicitada**
- Tiempo medido ≈ tiempo teorico (puede variar ±20%)
- Sub-Hz: tiempos de minutos por punto (normal)

### Fallos comunes y diagnostico

| Sintoma | Causa probable | Accion |
|---|---|---|
| Sweep retorna 10 pts | Firmware corrupto (N > limite) | Desconectar y reconectar hardware |
| Timeout en sweep | `SWEEP_TIMEOUT` (600s) insuficiente para N grande + frecuencias bajas | Calcular tiempo esperado con `estimate_sweep_time()` |
| Frecuencias no monotonas | Firmware en estado inconsistente | Desconectar/reconectar, verificar `configure_sweep()` |
| R/X = NaN o inf | Saturacion o rango de ganancia incorrecto | Verificar `ImpedanceRange` vs frecuencia |
| `*idn` no responde | Puerto incorrecto o cable suelto | Verificar con `get_preferred_usb_serial_ports()` |
| `configure_sweep()` lanza excepcion | Parametros fuera de rango o firmware ocupado | Verificar `validate_frequency()`, `validate_count()` |
| Datos vacios post-sweep | `get_data()` no encuentra lineas validas | Verificar parseo ANSI en `clean_response_line()` |

### Verificacion de integridad de datos

Cada punto de sweep debe cumplir:
```python
import numpy as np
# Frecuencia > 0
assert all(p[0] > 0 for p in data)
# R finito (no NaN, no inf)
assert all(np.isfinite(p[1]) for p in data)
# X finito (no NaN, no inf)
assert all(np.isfinite(p[2]) for p in data)
# Frecuencias monotonas crecientes
assert all(data[i][0] < data[i+1][0] for i in range(len(data)-1))
```

## Timing: teorico vs empirico

### Modelo teorico (`lib/utils.py`)
```python
_HW_DFT_CYCLES = 36       # DFT integration cycles
_HW_FLOOR_MS = 15.0       # Hardware floor (UART mode)
_HW_SWEEP_STARTUP_MS = 3000  # Fixed overhead per sweep

def _acquisition_time_ms(frequency, average=1):
    period_ms = (1.0 / frequency) * 1000.0
    base_ms = _HW_DFT_CYCLES * period_ms
    base_ms = max(base_ms, _HW_FLOOR_MS)
    return base_ms * average
```

### Perfil empirico (`HardwareTimingProfile`)
- Guardado en `hw_timing_profile.json`
- `update_from_sweep()` actualiza con datos reales
- Interpolacion log-log para frecuencias no medidas
- `get_ms(freq)` retorna el tiempo empirico (preferido sobre el teorico)
- Se usa para estimar timeouts realistas

### Comparacion
```bash
python benchmark_timing.py --show  # Ver perfil guardado
python benchmark_timing.py         # Medir y comparar con teorico
```

Diferencias >30% entre teorico y empirico sugieren:
- Cambios en el firmware
- Problemas de comunicacion serial
- `HardwareTimingProfile` desactualizado

## Modos display (C8)

El ADMX2001 soporta 18 modos de visualizacion (`lib/enums.py:DisplayMode`):

| Modo | Display | Unidades |
|---|---|---|
| R_X (6) | Rectangular | Ω, Ω |
| Z_DEG (7) | Polar (grados) | Ω, ° |
| Z_RAD (8) | Polar (radianes) | Ω, rad |
| CS_RS (0) | Serie C+R | F, Ω |
| CS_D (1) | Serie C+D | F, adim |
| CS_Q (2) | Serie C+Q | F, adim |
| LS_RS (3) | Serie L+R | H, Ω |
| CP_RP (9) | Paralelo C+R | F, Ω |
| G_B (15) | Admitancia rect | S, S |
| Y_DEG (16) | Admitancia polar | S, ° |
| OFF (18) | Apagado | — |

El modo mas usado en ZORIA es R_X (6). La Suite C8 verifica que todos los modos producen datos validos.

## Precauciones

1. **NUNCA** enviar N > `max_count_for_span(start, end)` — corrompe el firmware
2. Sub-Hz es **extremadamente lento** (0.2 Hz = 3 min/pt) — usar solo con `--include-sub-hz`
3. `configure_sweep()` ya clampea N — no reclampear manualmente
4. Si el firmware se corrompe (10 pts), **desconectar fisicamente** el USB y reconectar
5. El baudrate es **115200**, no 230400
6. `device_state._operation_lock` puede causar deadlocks si dos operaciones compiten

## Despues del testeo

Si todos los tests pasan, actualizar `hw_timing_profile.json` con:
```bash
python benchmark_timing.py --port /dev/ttyUSB0
```

Esto asegura que los timeouts de la aplicacion ZORIA usen datos empiricos actualizados.

## Cuando NO usar esta skill

- Verificacion rapida post-cambio → usar `zoria-verify`
- Para simular sin hardware → ZORIA requiere hardware real
- Para testear la UI/Dash → la UI se testea con la app corriendo
