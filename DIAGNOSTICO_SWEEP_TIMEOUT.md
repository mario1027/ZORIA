# Diagnóstico: Problema de Sweep Timeout

## Síntomas Reportados

```
📊 Modo de medición: R, X
⚡ mdelay = 2 ms (auto: estabilidad)
Timeout sin ningún dato después de 10.0s
Sweep incompleto: esperados 100 puntos, recibidos 0
Advertencia: se esperaban 100 puntos pero solo se parsearon 0
```

## Problema Identificado

El dispositivo ADMX2001 no está respondiendo al comando de sweep ('z'), resultando en timeout sin recibir ningún dato.

### Causas Posibles

1. **Comando 'initiate' faltante**: Algunos dispositivos requieren un comando 'initiate' antes de poder ejecutar 'z'
2. **Buffer serial sucio**: Puede haber datos residuales en el buffer
3. **Timing inadecuado**: El dispositivo puede necesitar más tiempo entre comandos
4. **Configuración incompleta**: Falta algún parámetro de configuración

## Soluciones Implementadas

### 1. Agregado comando 'initiate' (lib/admx2001.py, línea ~948)

```python
# IMPORTANTE: Algunos dispositivos requieren 'initiate' antes de poder ejecutar 'z'
try:
    logger.debug("Enviando comando 'initiate' para preparar el sweep...")
    self.serial.write(b'initiate\n')
    time.sleep(0.5)  # Dar tiempo al dispositivo para prepararse
    # Limpiar cualquier respuesta del initiate
    while self.serial.in_waiting > 0:
        self.serial.readline()
    logger.debug("Comando 'initiate' ejecutado")
except Exception as e:
    logger.warning(f"Error en 'initiate' (puede ser opcional): {e}")
```

**Mejora**: El comando 'initiate' prepara el dispositivo para ejecutar el sweep.

### 2. Logging Mejorado (lib/admx2001.py, línea ~975)

```python
# Log periódico cada 2 segundos para mostrar progreso
if int(time.time() - start_time) % 2 == 0 and (time.time() - start_time) > 1:
    elapsed = time.time() - start_time
    logger.debug(f"Esperando datos... ({elapsed:.1f}s transcurridos, {points_received} puntos recibidos)")

# Log cuando se recibe cada punto
logger.info(f"✓ Punto {points_received}/{expected_count} recibido")
```

**Mejora**: Mejor visibilidad de lo que está pasando durante el sweep.

### 3. Script de Diagnóstico (test_sweep_diagnostic.py)

Script paso a paso que:
- Conecta al dispositivo
- Verifica configuración básica
- Prueba medición simple
- Configura sweep pequeño (5 puntos)
- Ejecuta sweep con logging detallado
- Muestra resultados

**Uso**:
```bash
python3 test_sweep_diagnostic.py
```

## Pasos para Diagnosticar

### Paso 1: Ejecutar el script de diagnóstico

```bash
cd /home/mrmontero/Documents/impedancia/EVAL-ADMX2001
python3 test_sweep_diagnostic.py
```

El script probará:
1. ✓ Conexión al dispositivo
2. ✓ Configuración básica
3. ✓ Medición simple (para verificar que el dispositivo responde)
4. ✓ Configuración de sweep
5. ✓ Ejecución de sweep (5 puntos para prueba rápida)

### Paso 2: Verificar los logs

Los logs mostrarán exactamente qué está pasando:
- Si el comando 'initiate' se ejecuta correctamente
- Si el comando 'z' se envía
- Si se reciben líneas de respuesta
- Cuántos puntos se reciben

### Paso 3: Ajustar según resultados

**Si el diagnóstico funciona pero el dashboard no**:
- El problema está en el dashboard, no en la librería
- Revisar la configuración de los parámetros del sweep

**Si el diagnóstico también falla**:
- Problema con el dispositivo o la comunicación serial
- Verificar cables, conexiones
- Verificar que no hay otro programa usando el puerto

## Archivos Modificados

### lib/admx2001.py
- **Línea ~948**: Agregado comando 'initiate' antes de 'z'
- **Línea ~965**: Logging mejorado con información de progreso
- **Línea ~975**: Log periódico cada 2 segundos
- **Línea ~982**: Log cuando se recibe cada punto

### test_sweep_diagnostic.py (NUEVO)
- Script completo de diagnóstico paso a paso
- Prueba sweep pequeño (5 puntos)
- Muestra información detallada de cada paso

## Verificaciones Adicionales

### 1. Verificar que el dispositivo esté respondiendo

```bash
python3 -c "
from lib import ADMX2001
dev = ADMX2001.find_and_connect()
print('ID:', dev.get_idn())
r, x = dev.measure()
print(f'Medición: R={r:.2f}Ω, X={x:.2f}Ω')
dev.disconnect()
"
```

**Resultado esperado**: Debe mostrar el ID del dispositivo y una medición válida.

### 2. Verificar configuración del sweep

```bash
python3 -c "
from lib import ADMX2001, SweepType, SweepScale
dev = ADMX2001.find_and_connect()
dev.configure_sweep(SweepType.FREQUENCY, 1.0, 10.0, SweepScale.LINEAR, count=5)
print('✓ Sweep configurado correctamente')
dev.disconnect()
"
```

**Resultado esperado**: Debe configurar sin errores.

### 3. Probar sweep mínimo

```bash
python3 test_sweep_diagnostic.py
```

**Resultado esperado**: Debe ejecutar sweep y recibir 5 puntos.

## Próximos Pasos

1. **Ejecutar test_sweep_diagnostic.py** para ver si el problema está en la librería o en el dashboard
2. **Revisar los logs** para identificar exactamente dónde falla
3. **Si el diagnóstico funciona**, el problema está en cómo el dashboard llama al sweep
4. **Si el diagnóstico falla**, necesitamos investigar la comunicación serial

## Notas Importantes

- El comando 'initiate' puede ser necesario según la versión del firmware
- El timeout de 10s puede ser insuficiente para sweeps grandes
- Los sweeps logarítmicos con muchos puntos pueden tardar minutos
- Algunos dispositivos necesitan un delay adicional después de 'configure_sweep'

## Estado Actual

🔄 **EN DIAGNÓSTICO**

- ✅ Comando 'initiate' agregado
- ✅ Logging mejorado
- ✅ Script de diagnóstico creado
- ⏳ Pendiente: Ejecutar diagnóstico para identificar causa exacta

---
**Próxima acción recomendada**: Ejecutar `python3 test_sweep_diagnostic.py` y revisar el output.
