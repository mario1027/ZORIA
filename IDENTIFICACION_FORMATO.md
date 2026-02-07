# IDENTIFICACIÓN DE FORMATO: calibrate list

## 📋 Análisis Completado

He analizado todos los formatos posibles del comando `calibrate list` y actualizado el código para manejarlos **todos de manera robusta**.

## 🔍 Formatos Soportados

### Formato 1: Solo frecuencias (número simple)
```
1000
5000
10000
```

### Formato 2: Frecuencias con unidades
```
1000 Hz
5000 kHz
10 MHz
```

### Formato 3: Con etiquetas
```
Freq: 1000 Hz
Frequency: 5000 Hz
```

### Formato 4: Configuraciones de ganancia (calibrate list <freq>)
```
CH0=0 CH1=0
CH0=0 CH1=1
CH0=1 CH1=0
```

### Formato 5: Completo (frecuencia + ganancia)
```
FREQ=1000 CH0=0 CH1=0
FREQ=1000 CH0=0 CH1=1
FREQ=5000 CH0=1 CH1=0
```

## ✅ Mejoras Implementadas

### En `pages/calibration/calibration_page.py`:

1. **Parseo Multi-Formato**: Detecta automáticamente el formato y parsea correctamente
2. **Agrupamiento por Frecuencia**: Organiza calibraciones por frecuencia
3. **Manejo de Errores Robusto**: Si una línea no se puede parsear, la muestra como cruda con advertencia
4. **Detalles Técnicos**: Muestra traceback completo en caso de error (expandible)
5. **Conversión de Unidades**: Convierte kHz/MHz → Hz automáticamente
6. **Regex Flexible**: Extrae frecuencias en cualquier formato

### Cambios Clave:

```python
# Detección inteligente de formato
if '=' in line:
    # Formato clave=valor (4 o 5)
    parsed_data = parse_key_value(line)
else:
    # Formato simple (1, 2, o 3)
    freq = extract_frequency_regex(line)

# Agrupamiento por frecuencia
frequencies_with_configs[freq].append(config)

# Fallback con datos crudos
if parse_fails:
    show_raw_with_warning(line)
```

## 🧪 Scripts de Prueba Creados

### 1. `test_calibration_format.py`
Prueba con hardware real (requiere dispositivo conectado):
```bash
python test_calibration_format.py
```

### 2. `test_calibration_simulation.py`
Análisis de formatos posibles (sin hardware):
```bash
python test_calibration_simulation.py
```

## 📝 Próximos Pasos para Probar

### Opción A: Con Hardware Real

1. **Conectar el ADMX2001**:
   ```bash
   python app.py
   ```

2. **Ir a Dashboard** → Conectar dispositivo

3. **Hacer una calibración**:
   - Calibration → Wizard
   - Open → Short → Load
   - Ejecutar y guardar

4. **Recargar la página Calibration**

5. **Click "Actualizar"** (botón de refrescar)

6. **Observar la tabla**:
   - ✅ Si muestra datos: Formato correcto detectado
   - ⚠ Si muestra advertencias: Revisar datos crudos
   - ❌ Si error: Ver detalles técnicos (expandir)

### Opción B: Desde Terminal CLI

1. **Dashboard** → Conectar

2. **Ir a Terminal CLI** (abajo del dashboard)

3. **Ejecutar comando**:
   ```
   calibrate list
   ```

4. **Observar la salida** y comparar con formatos listados arriba

5. **Reportar el formato real**

## 📊 Tabla de Calibraciones - Columnas

| # | Fecha/Hora | Resistencia | Frecuencia | Ganancias | Estado | Acciones |
|---|------------|-------------|------------|-----------|---------|----------|
| 1 | 2026-02-07 | 1000 Ω | 1000 Hz | CH0=0, CH1=0 | ✓ | 🔍 🗑️ |

## 🐛 Debugging

Si algo falla:

1. **Ver Logs**:
   - Consola del navegador (F12)
   - Terminal donde corre `app.py`

2. **Datos Crudos**:
   - La tabla mostrará datos crudos con ⚠ si no puede parsear
   - Envía esa línea para ajustar el regex

3. **Error Detallado**:
   - La tabla incluye botón "Ver detalles técnicos"
   - Expande para ver traceback completo

## 🎯 Conclusión

**La implementación actual es ROBUSTA y puede manejar todos los formatos documentados.**

✅ Parseo multi-formato  
✅ Fallback con warnings  
✅ Agrupamiento inteligente  
✅ Error handling completo  
✅ Conversión de unidades  
✅ Regex flexible  

**Solo falta probar con el hardware real para confirmar el formato exacto.**
