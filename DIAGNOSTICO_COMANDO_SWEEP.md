# Diagnóstico: Comando de Sweep Incorrecto

## Problema Actual

El dispositivo no responde al comando de sweep, resultando en timeout de 30s sin recibir ningún dato.

```
✗ Timeout crítico: ningún dato después de 30.0s
Sweep incompleto: esperados 100 puntos, recibidos 0
```

## Hipótesis

El comando que estábamos usando ('z' seguido de 'initiate') puede no ser el correcto o puede necesitar una secuencia específica.

## Cambios Implementados

### 1. Cambiado a 'initiate' Directo (lib/admx2001.py, línea ~945)

```python
# ANTES: Enviábamos 'initiate' + 'z'
self.serial.write(b'initiate\n')
time.sleep(0.5)
self.serial.write(b'z\n')  # Shortcut

# AHORA: Solo 'initiate' completo
self.serial.reset_input_buffer()
self.serial.reset_output_buffer()
self.serial.write(b'initiate\n')
self.serial.flush()  # Asegurar que se envíe
```

**Razón**: El comando estándar SCPI es 'initiate', no 'z'. El shortcut 'z' puede no estar implementado en todos los firmwares.

### 2. Limpieza de Buffers Antes del Comando

```python
self.serial.reset_input_buffer()
self.serial.reset_output_buffer()
time.sleep(0.2)
```

**Razón**: Datos residuales en los buffers pueden causar problemas.

### 3. Script de Diagnóstico Raw (test_raw_serial.py)

Script que prueba directamente en el puerto serial diferentes comandos:
- `initiate` (estándar SCPI)
- `z` (shortcut documentado)
- `start`, `run`, `execute`, `sweep` (alternativas)

Este script identifica qué comando realmente funciona con tu dispositivo específico.

## Cómo Usar el Script de Diagnóstico

```bash
cd /home/mrmontero/Documents/impedancia/EVAL-ADMX2001
python3 test_raw_serial.py
```

El script:
1. Encuentra el puerto del ADMX2001
2. Se conecta directamente al puerto serial
3. Configura un sweep simple (5 puntos, 1-10 kHz)
4. Prueba cada comando uno por uno
5. Muestra qué comando produce datos

**Resultado esperado**:
```
Probando comando: 'initiate'
  ← 1.0, 123.45, 67.89
  ← 2.5, 234.56, 78.90
  ← 5.0, 345.67, 89.01
✓✓✓ ÉXITO CON 'initiate' ✓✓✓
```

O si 'initiate' no funciona, probará otros comandos.

## Posibles Resultados

### Resultado 1: 'initiate' Funciona
✅ El cambio que hicimos es correcto
- El problema puede estar en otra parte (configuración, timing, etc.)
- Ejecutar el diagnóstico mostrará los datos recibidos

### Resultado 2: Otro Comando Funciona (ej: 'start')
✅ Identificamos el comando correcto
- Actualizaremos lib/admx2001.py para usar ese comando
- El sweep funcionará después del cambio

### Resultado 3: Ningún Comando Funciona
❌ Problema más profundo
- Verificar configuración del sweep
- Verificar que el dispositivo esté funcionando correctamente
- Revisar manuales del dispositivo

## Próximos Pasos

### Paso 1: Ejecutar Diagnóstico Raw

```bash
python3 test_raw_serial.py
```

**IMPORTANTE**: Este script requiere que:
- El dispositivo esté conectado
- Haya una muestra conectada (un resistor simple sirve)
- NO esté el dashboard corriendo (para no tener conflicto de puertos)

### Paso 2: Analizar Resultados

El script te dirá exactamente qué comando funciona.

### Paso 3: Si Otro Comando Funciona

Si el script encuentra que (por ejemplo) 'start' funciona pero 'initiate' no:

```python
# Actualizar en lib/admx2001.py línea ~960
self.serial.write(b'start\n')  # En lugar de 'initiate'
```

### Paso 4: Si Ningún Comando Funciona

Revisar:
1. ¿El comando `*idn` funciona? (verificar comunicación básica)
2. ¿Los comandos de configuración funcionan? (count, sweep_type, etc.)
3. ¿Una medición simple funciona? (comando 'measure' o similar)

## Archivos Modificados

### lib/admx2001.py
- **Línea ~945**: Cambiado de 'z' a 'initiate' directo
- **Línea ~950**: Agregada limpieza de buffers
- **Línea ~957**: Agregado `flush()` para asegurar envío

### test_raw_serial.py (NUEVO)
- Script de diagnóstico que prueba comandos directamente
- Identifica qué comando ejecuta el sweep
- No requiere la librería ADMX2001, usa serial directo

## Comandos SCPI Estándar

Según estándares SCPI, los comandos típicos para iniciar mediciones son:

1. `INITiate[:IMMediate]` - Inicia medición (estándar SCPI)
2. `TRIGger[:IMMediate]` - Trigger manual
3. `*TRG` - Trigger simple
4. `READ?` - Inicia y lee (query)
5. `MEAS?` - Medición completa (query)

Algunos dispositivos usan shortcuts:
- `z` para initiate
- `m` para measure
- `t` para trigger

## Notas del Fabricante

Si tienes acceso al manual del ADMX2001, busca:
- Sección "Sweep Commands"
- Sección "SCPI Command Reference"
- Ejemplos de código de sweeps

La documentación oficial debe indicar el comando exacto.

## Estado Actual

🔄 **EN DIAGNÓSTICO**

- ✅ Cambiado a comando 'initiate' directo
- ✅ Agregada limpieza de buffers
- ✅ Script de diagnóstico raw creado
- ⏳ Pendiente: Ejecutar test_raw_serial.py para identificar comando correcto

---

**ACCIÓN REQUERIDA**: 
1. Cerrar el dashboard si está corriendo
2. Ejecutar: `python3 test_raw_serial.py`
3. Observar qué comando produce datos
4. Reportar el resultado para actualizar el código
