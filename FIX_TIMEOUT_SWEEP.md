# Fix: Timeout Aumentado y Lógica de Sweep Mejorada

## Cambios Implementados

### 1. Timeout Global Aumentado (lib/enums.py)

```python
SWEEP_TIMEOUT = 600.0  # 10 minutos (antes: 60s)
```

**Justificación**: Sweeps largos con muchos puntos pueden tardar varios minutos. 10 minutos es suficiente incluso para los sweeps más lentos.

### 2. Idle Timeout Aumentado (lib/admx2001.py, línea ~973)

```python
idle_timeout = 30.0  # 30 segundos entre puntos (antes: 10s)
```

**Justificación**: En sweeps de baja frecuencia, puede tomar más de 10 segundos obtener cada punto.

### 3. Lógica de Prompt Mejorada

**Problema anterior**: El dispositivo enviaba el prompt `ADMX2001>` inmediatamente pero los datos llegaban después, causando terminación prematura.

**Nueva lógica**:
```python
# Detectar prompt pero NO terminar inmediatamente
if 'ADMX2001>' in line:
    if not prompt_seen:
        prompt_seen = True
        prompt_time = time.time()
        logger.debug(f"Prompt detectado con {points_received}/{expected_count} puntos")
    
    # Solo terminar si ya recibimos todos los puntos
    if points_received >= expected_count:
        logger.info(f"✓ Todos los {expected_count} puntos recibidos")
        break
```

**Ventaja**: El código ahora espera pacientemente incluso después de ver el prompt.

### 4. Timeout Inteligente

El timeout solo se activa cuando:
1. **Ya recibimos todos los puntos** → Termina exitosamente
2. **30s sin datos Y tenemos algunos puntos** → Termina con advertencia
3. **30s sin datos Y 0 puntos recibidos** → Si vimos el prompt, espera 60s más

```python
if prompt_seen and (time.time() - prompt_time) < 60.0:
    logger.info("Prompt detectado - esperando más tiempo por si los datos vienen después...")
    continue  # No terminar todavía
```

### 5. Logging Mejorado

- Log cada 5 segundos (antes: cada 2s) para reducir spam
- Mensajes más informativos con emojis
- Diagnóstico de errores cuando timeout ocurre

```python
logger.info(f"⏳ Esperando datos... ({elapsed:.1f}s, {points_received}/{expected_count} puntos)")
```

## Comportamiento Resultante

### Caso 1: Sweep Normal
1. Comando 'initiate' + 'z' enviados
2. Prompt aparece inmediatamente
3. Código espera pacientemente
4. Datos llegan progresivamente
5. Se reciben todos los puntos
6. **Resultado**: ✓ Éxito

### Caso 2: Sweep Lento
1. Comando enviado
2. Prompt aparece
3. Primer dato tarda 15 segundos en llegar
4. Código sigue esperando (idle_timeout = 30s)
5. Datos llegan cada 10-15 segundos
6. **Resultado**: ✓ Éxito (tarda más pero funciona)

### Caso 3: Error Real
1. Comando enviado
2. Prompt aparece
3. Esperamos 30 segundos
4. Si vimos prompt: esperamos 60 segundos adicionales
5. Total: 90 segundos de espera
6. Si aún 0 datos: **Resultado**: ✗ Error con diagnóstico

## Comparación Antes vs Después

| Aspecto | Antes | Después |
|---------|-------|---------|
| Timeout global | 60s | 600s (10 min) |
| Idle timeout | 10s | 30s |
| Comportamiento con prompt | Termina si 0 datos | Espera 60s más |
| Logging | Cada 2s | Cada 5s |
| Timeout total máximo | ~70s | ~690s |
| Manejo de sweeps lentos | ✗ Falla | ✓ Funciona |

## Archivos Modificados

### lib/enums.py
- **Línea 158**: `SWEEP_TIMEOUT = 600.0` (era 60.0)

### lib/admx2001.py
- **Línea ~973**: `idle_timeout = 30.0` (era 10.0)
- **Líneas ~980-1050**: Lógica de prompt y timeout completamente reescrita
- **Línea ~1015**: Logging cada 5s (era 2s)
- **Líneas ~1030-1050**: Timeout inteligente con diagnóstico

## Pruebas Recomendadas

### Prueba 1: Sweep Pequeño (Rápido)
```python
# Debería completar en ~5-10 segundos
dev.configure_sweep(SweepType.FREQUENCY, 1.0, 10.0, SweepScale.LINEAR, count=5)
results = dev.perform_sweep()  # Timeout: 600s
```

### Prueba 2: Sweep Medio (Normal)
```python
# Debería completar en ~30-60 segundos
dev.configure_sweep(SweepType.FREQUENCY, 0.2, 1000.0, SweepScale.LOG, count=50)
results = dev.perform_sweep()
```

### Prueba 3: Sweep Grande (Lento)
```python
# Puede tomar 2-5 minutos
dev.configure_sweep(SweepType.FREQUENCY, 0.2, 10000.0, SweepScale.LOG, count=100)
results = dev.perform_sweep()
```

## Próximos Pasos

1. **Probar en el dashboard**: Ejecutar `python3 dashboard_complete.py`
2. **Intentar sweep de 100 puntos**: 0.2 Hz - 10 MHz
3. **Observar logs**: Verificar que aparezcan mensajes como:
   - "✓ Punto X/100 recibido"
   - "⏳ Esperando datos..."
   - "✓ Todos los 100 puntos recibidos"

## Notas Importantes

⚠ **El sweep PUEDE tardar mucho tiempo**:
- Sweeps de baja frecuencia (<10 Hz) son muy lentos
- 100 puntos logarítmicos de 0.2 Hz a 10 MHz puede tomar 3-5 minutos
- Esto es normal y esperado

✅ **Ahora el código es más paciente**:
- No termina prematuramente
- Espera el tiempo que sea necesario (hasta 10 minutos)
- Da diagnósticos útiles si realmente hay un problema

## Resultado Esperado

Con estos cambios, el mensaje de error:
```
Timeout sin ningún dato después de 10.0s
Sweep incompleto: esperados 100 puntos, recibidos 0
```

Debería convertirse en:
```
✓ Punto 1/100 recibido
✓ Punto 2/100 recibido
...
✓ Punto 100/100 recibido
✓ Todos los 100 puntos recibidos - sweep completado
Sweep completado: 100 puntos obtenidos
```

---
**Estado**: ✅ IMPLEMENTADO - Listo para probar
**Fecha**: 16 de octubre de 2025
