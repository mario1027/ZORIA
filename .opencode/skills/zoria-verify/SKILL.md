---
name: zoria-verify
description: Verifica que todo el sistema ZORIA funciona correctamente despues de cualquier cambio de codigo. No es solo test de barrido: comprueba arranque de la app Dash, conectividad con el ADMX2001 via serial, pipeline minimo de medicion, configuracion, calibracion, y callbacks de UI. Si algo falla diagnostica en la capa correcta (firmware/driver/UI). Usar por defecto tras cualquier modificacion del proyecto.
---

# ZORIA Verify

Skill de verificacion rapida post-cambio. Comprueba el sistema completo -- no solo el barrido -- y diagnostica fallos en la capa correcta.

## Arquitectura del sistema

```
UI (Dash/Flask)  →  Driver (lib/admx2001.py)  →  Firmware (EVAL-ADMX2001 via serial)
     ↑                        ↑                              ↑
  app.py              lib/device_state.py            /dev/ttyUSB0 @ 115200 baud
  pages/dashboard/    lib/utils.py                   Cable TTL232R-3V3
  pages/calibration/  lib/calibration.py             *idn → ADMX/2001/ANALOG
```

**DeviceState** (`lib/device_state.py`) es el singleton global que mantiene la conexion. Todas las paginas y callbacks acceden via `device_state.device`.

## Flujo de verificacion

Ejecutar en orden. Si un paso falla, diagnosticar antes de continuar.

### 1. Arranque de la aplicacion

```bash
python -c "
import sys; sys.path.insert(0, '.')
from app import DEFAULT_CONFIG
print('app.py importa OK')
print('DashSPA + VOLT + page_container listos')
"
```

Verificar que:
- `app.py` importa sin errores (DashSPA, VOLT, page_container)
- `config/spa_config.ini` se parsea correctamente (host, port, debug)
- No hay imports circulares (lib → lib → ...)
- `requirements.txt` y `requirements-dev.txt` estan presentes y completos

### 2. Conectividad con el hardware

```bash
python -c "
import serial.tools.list_ports
from lib.utils import get_preferred_usb_serial_ports, is_likely_admx_port
from lib import ADMX2001

ports = get_preferred_usb_serial_ports()
print(f'Puertos USB: {[p.device for p in ports]}')

if not ports:
    print('ERROR: No hay puertos USB detectados')
    exit(1)

# Tomar el mejor puerto (prioridad TTL232R-3V3 > FT232R > otros)
port = ports[0]
dev = ADMX2001(port.device, baudrate=115200, timeout=1.2)
resp = dev.send_command('*idn')
print(f'*idn: {resp}')

if resp and any(x in str(resp).upper() for x in ['ADMX', '2001', 'ANALOG']):
    selftest = dev.send_command('selftest')
    print(f'selftest: {selftest}')
    dev.close()
    print('OK: ADMX2001 responde a *idn y selftest')
else:
    print(f'ERROR: dispositivo en {port.device} no es ADMX2001')
    dev.close()
    exit(1)
"
```

Reglas de deteccion de puerto:
- Prioridad: TTL232R-3V3 (120) > TTL-232R-RPI (115) > FT232R (95) > FTDI USB (90)
- `get_preferred_usb_serial_ports()` ordena por prioridad descendente
- `is_likely_admx_port()` retorna True si prioridad >= 80
- Baudrate fijo: **115200** (no 230400)
- Timeout: 1.2s para comandos, 5.0s default, 600s para sweeps largos

### 3. Pipeline minimo de medicion

```bash
python -c "
import sys; sys.path.insert(0, '.')
from lib.utils import get_preferred_usb_serial_ports, max_count_for_span
from lib import ADMX2001
from lib.enums import DisplayMode, SweepType, SweepScale

ports = get_preferred_usb_serial_ports()
dev = ADMX2001(ports[0].device, baudrate=115200, timeout=1.2)

# Configurar barrido rapido (pocos puntos, banda alta donde timing es minimo)
N = 5
dev.configure_sweep(
    sweep_type=SweepType.FREQUENCY,
    start_hz=1000,
    end_hz=100000,
    count=N,
    scale=SweepScale.LOG,
    average=1,
    display=DisplayMode.R_X
)

dev.run_sweep()
data = dev.get_data()

if data and len(data) == N:
    freqs = [p[0] for p in data if p[0] > 0]
    r_vals = [p[1] for p in data if p[1] is not None]
    x_vals = [p[2] for p in data if p[2] is not None]

    monotonic = all(freqs[i] < freqs[i+1] for i in range(len(freqs)-1))
    finite = all(np.isfinite(v) for v in r_vals + x_vals)

    if monotonic and finite:
        print(f'OK: {len(data)} pts, freqs monotonas, R/X finitos')
    else:
        print(f'ERROR: datos no validos (monotonic={monotonic}, finite={finite})')
else:
    print(f'ERROR: se esperaban {N} puntos, se recibieron {len(data) if data else 0}')

dev.close()
"
```

Lo que verifica el pipeline minimo:
- `configure_sweep()` → parametros validos, clamp automatico de N
- `run_sweep()` → firmware ejecuta sin timeout ni errores
- `get_data()` → datos retornados correctamente
- Datos: frecuencias monotonas crecientes, R/X finitos (no NaN, no inf)
- Cantidad de puntos recibidos == cantidad solicitada

### 4. Configuracion del sistema

Verificar `config/spa_config.ini`:
- Seccion `[spa]` con `title`, `version`
- Seccion `[server]` con `host`, `port`
- Puerto configurado existe en el sistema

```bash
python -c "
import configparser
cfg = configparser.ConfigParser()
cfg.read('config/spa_config.ini')
assert 'spa' in cfg
assert 'server' in cfg
print(f'SPA config: {cfg[\"spa\"][\"title\"]} v{cfg[\"spa\"][\"version\"]}')
print(f'Server: {cfg[\"server\"][\"host\"]}:{cfg[\"server\"][\"port\"]}')
print('OK: spa_config.ini valido')
"
```

### 5. Calibracion

Verificar que las tablas y el parser funcionan:

```bash
python -c "
import sys; sys.path.insert(0, '.')
from lib.calibration_parser import CalibrationParser
from lib.calibration import CalibrationManager
from lib.device_state import device_state

# Verificar parser
parser = CalibrationParser()
print(f'Parser: {type(parser).__name__}')

# Verificar CalibrationManager
mgr = CalibrationManager(device_state)
print(f'CalibrationManager: {type(mgr).__name__}')
print('OK: modulos de calibracion importan sin errores')
"
```

### 6. Callbacks de Dash / UI

Verificar que los callbacks principales no tienen errores de sintaxis o de IDs:

- `register_global_connection_callbacks(app)` — sidebar, auto-connect, monitor
- `register_global_terminal_callbacks(app)` — CLI, streaming, keyboard
- Callbacks de `pages/dashboard/dashboard_page.py` — `prevent_initial_call=True` en callbacks con `allow_duplicate`
- IDs de componentes coinciden entre layout y callbacks

Si la app esta corriendo, revisar la consola de Flask en busca de errores de callback.

## Diagnostico por capa

Cuando algo falla, diagnosticar en la capa correcta:

### Capa Firmware (hardware)
- `check_device_state.py` → estado de device_state
- `*idn` y `selftest` → responde el dispositivo?
- Puerto serial abierto? `device.serial.is_open`
- Cable TTL232R-3V3 detectado por `is_likely_admx_port()`?

**Sintomas de firmware corrupto:**
- Sweep retorna solo 10 pts (se envio N > limite del span)
- `*idn` responde pero `configure_sweep()` falla
- Reset necesario: desconectar y reconectar

### Capa Driver (lib/admx2001.py)
- `configure_sweep()` → excepciones, timeouts, parametros invalidos
- `run_sweep()` → `SWEEP_TIMEOUT` (600s) vs tiempo real
- `get_data()` → parseo de lineas, limpieza ANSI, datos crudos vs procesados
- `_operation_lock` → deadlocks, timeouts de 90s

### Capa UI (Dash/Flask)
- Callbacks con `allow_duplicate` sin `prevent_initial_call=True`
- IDs de componentes incorrectos (error silencioso en consola Flask)
- `device_state.device` es None porque no se conecto desde el sidebar
- `spa_config.ini` no encontrado en ruta esperada

## Reglas criticas del firmware ADMX2001

1. **Limite N por ancho de banda:**
   - Span ≥ 4 decadas → max **100 pts**
   - Span < 4 decadas → max **200 pts**
   - `max_count_for_span(start_hz, end_hz)` en `lib/utils.py` calcula el limite
   - `configure_sweep()` ya clampea N → NO reclampear en capas superiores

2. **Corrupcion de estado:**
   - Si se envia N > limite → firmware se corrompe
   - Siguiente sweep retorna **exactamente 10 pts**
   - Unica solucion: **desconectar y reconectar** (power cycle del firmware)

3. **Timing:**
   - 36 ciclos DFT por punto + 15ms floor + 3s overhead por sweep
   - `_acquisition_time_ms(freq)` en `lib/utils.py`
   - Sub-Hz es extremadamente lento (0.2 Hz → 180s por punto)

4. **Baudrate:** 115200 fijo (no 230400)

5. **Identidad:** `*idn` debe contener ADMX, 2001, o ANALOG

## Scripts de diagnostico disponibles

| Script | Proposito |
|---|---|
| `python check_device_state.py` | Estado rapido de device_state |
| `python benchmark_timing.py` | Perfilado empirico de timing |
| `python benchmark_timing.py --show` | Mostrar perfil guardado |
| `bash diagnostico_calibracion.sh` | Diagnostico de calibracion |
| `python -m pytest tests/ -v` | Tests unitarios (si existen) |

## Cuando NO usar esta skill

- Para testeo exhaustivo de barridos → usar `zoria-sweep`
- Para testear solo la UI sin hardware → no es el proposito de ZORIA
- Para simular sin hardware → ZORIA requiere hardware real
