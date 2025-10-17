# Test: Checkbox de Fase Positiva/Negativa

## Cambios Implementados

### 1. Checkbox agregado en la UI
**Ubicación**: Tab "Barridos", panel de configuración izquierdo  
**Después de**: Sección de "Delays (ms)"  
**Antes de**: Botón "Iniciar Barrido"

```python
dbc.Label("📊 Visualización de Fase:", className="mt-2"),
dbc.Checklist(
    options=[
        {"label": " Invertir fase (mostrar -Fase)", "value": "negative"}
    ],
    value=["negative"],  # Por defecto mostrar -Fase
    id="phase-negative-checkbox",
    switch=True,
),
```

### 2. Callback modificado
**Agregado**: Input `'phase-negative-checkbox'` como nuevo parámetro
**Función**: `update_sweep()` ahora recibe `phase_negative` como parámetro

### 3. Lógica de graficación
```python
# Determinar si aplicar negativo según checkbox
is_phase_negative = phase_negative and 'negative' in phase_negative

if is_phase_negative:
    phase_data = [-1 * p for p in phase]
    phase_label = '-Fase (θ)'
    phase_axis_label = "-Fase (°)"
else:
    phase_data = phase
    phase_label = 'Fase (θ)'
    phase_axis_label = "Fase (°)"
```

## Funcionalidad

### Checkbox ACTIVADO (por defecto)
- ✅ Fase se multiplica por -1
- ✅ Etiqueta muestra: "-Fase (θ)"
- ✅ Eje Y2 muestra: "-Fase (°)"
- ✅ Convención Bode estándar (capacitiva = negativa)

### Checkbox DESACTIVADO
- ✅ Fase se muestra sin invertir (positiva)
- ✅ Etiqueta muestra: "Fase (θ)"
- ✅ Eje Y2 muestra: "Fase (°)"
- ✅ Valores originales del dispositivo

## Comportamiento en Tiempo Real

- ⚡ Al cambiar el checkbox, el gráfico se regenera INMEDIATAMENTE
- 🔄 No se pierde el zoom del gráfico (se preserva el estado)
- 📊 Solo afecta al gráfico de Bode (eje Y2 - fase)
- 🎯 No afecta al gráfico de Nyquist

## Testing Sugerido

1. **Iniciar dashboard**: `python3 dashboard_complete.py`
2. **Conectar dispositivo**
3. **Realizar un barrido** (50 puntos, rango 100Hz - 100kHz)
4. **Verificar**: Fase muestra valores negativos (checkbox activado)
5. **Desactivar checkbox**: Observar que fase cambia a positiva inmediatamente
6. **Activar checkbox**: Observar que fase vuelve a negativa inmediatamente
7. **Zoom en el gráfico**: Verificar que al cambiar checkbox se mantiene el zoom

## Notas Técnicas

### Preservación del zoom
El callback distingue entre:
- `triggered == 'interval-sweep-progress'` + `not data_changed` → usa `no_update` (preserva zoom)
- `triggered == 'phase-negative-checkbox'` → regenera gráfico (pero preserva datos de zoom de Plotly)

### Valores por defecto
- Checkbox activado (`["negative"]`) = convención Bode estándar
- Texto informativo: "Convención Bode: fase negativa para impedancias capacitivas"

### Compatibilidad
- ✅ Compatible con método optimizado de sweep (4.8x más rápido)
- ✅ Compatible con todos los modos de medición
- ✅ Compatible con escalas log/linear
- ✅ No afecta el rendimiento (solo cambia visualización)
