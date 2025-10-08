# 🔌 Modo DC Resistance - ADMX2001

## 📋 Resumen

El ADMX2001 puede medir **resistencia DC** además de impedancia AC. Este modo especial se activa configurando la frecuencia a **0 Hz**.

---

## ⚙️ Configuración del Modo DC

### Requisitos según Documentación Oficial

Para usar el modo DC correctamente, se deben cumplir estos requisitos:

1. **Frecuencia = 0 Hz**
   ```python
   device.set_frequency(0)
   ```

2. **Display Mode = 6 (R, X - Impedancia Rectangular)**
   ```python
   device.set_display_mode(DisplayMode.R_X)  # Mode 6
   ```

3. **Offset NEGATIVO** (para detectar saturación)
   ```python
   device.set_offset(-1.0)  # Valor recomendado: -1V
   ```

### ⚠️ Advertencia Importante

Si no se cumple con estos requisitos, el dispositivo puede:
- No retornar mediciones válidas
- Generar errores de timeout
- Retornar valores incorrectos

---

## 🎯 Ejemplo de Uso

### Desde Terminal/Comandos

```bash
ADMX2001> frequency 0
DC Resistance mode enabled

ADMX2001> display 6
Measurement model: 6 - Impedance in rectangular coordinates (default) (Rs,Xs)

ADMX2001> offset -1
Offset = -1.0000

ADMX2001> z
0,4.995231e+01
```

**Resultado**: `49.95 Ω` (solo se retorna resistencia DC)

### Desde Python

```python
from lib import ADMX2001
from lib.enums import DisplayMode

# Conectar
device = ADMX2001('/dev/ttyUSB0')

# Configurar modo DC
device.set_frequency(0)              # Activar modo DC
device.set_display_mode(DisplayMode.R_X)  # Mode 6
device.set_offset(-1.0)              # Offset negativo
device.set_magnitude(0.5)            # Magnitud no afecta en DC

# Medir
r, x = device.measure()
print(f"Resistencia DC: {r:.3f} Ω")  # x se ignora en modo DC
```

### Desde Dashboard

1. **Frecuencia**: Poner `0`
2. **Offset**: Poner valor negativo (ej: `-1`)
3. **Modo de Medición**: Seleccionar `R, X - Impedancia (Default)`
4. Click en **Aplicar Config**
5. Iniciar medición

---

## 📊 Características del Modo DC

### ✅ Ventajas

- Medición de resistencia DC precisa
- Útil para verificar continuidad
- No requiere señal AC
- Ideal para resistores de bajo valor

### ⚠️ Limitaciones

1. **Solo retorna resistencia**: El valor `X` (reactancia) se ignora
2. **Solo modo R,X**: Otros modos de medición no funcionan
3. **Offset negativo obligatorio**: Para detectar saturación
4. **Sin información de fase**: No aplica en DC

### 🔍 Detalles Técnicos

- **Rango de medición**: Depende de la configuración de ganancia
- **Precisión**: Similar a mediciones AC en frecuencias bajas
- **Tiempo de medición**: Típicamente más rápido que AC
- **Saturación**: Detectada cuando offset < 0

---

## 🐛 Troubleshooting

### Problema: "No se pudo obtener medición válida"

**Causa**: Frecuencia = 0 sin configuración correcta

**Solución**:
```python
# Verificar configuración
freq = device.get_frequency()
if freq == 0:
    device.set_display_mode(DisplayMode.R_X)  # Mode 6
    device.set_offset(-1.0)  # Offset negativo
```

### Problema: Timeout en medición

**Causa**: El dispositivo espera offset negativo

**Solución**:
```python
device.set_offset(-1.0)  # Cambiar a negativo
```

### Problema: Valores incorrectos

**Causa**: Modo de display incorrecto

**Solución**:
```python
device.set_display_mode(DisplayMode.R_X)  # Solo mode 6 funciona
```

---

## 📝 Ejemplos Prácticos

### Medir Resistor de 100Ω

```python
device.set_frequency(0)
device.set_display_mode(DisplayMode.R_X)
device.set_offset(-1.0)
device.set_magnitude(0.5)  # No afecta en DC

r, x = device.measure()
print(f"Resistencia medida: {r:.2f} Ω")
# Resultado esperado: ~100 Ω
```

### Verificar Continuidad (< 1Ω)

```python
device.set_frequency(0)
device.set_display_mode(DisplayMode.R_X)
device.set_offset(-1.0)

r, x = device.measure()
if r < 1.0:
    print("✓ Continuidad OK")
else:
    print("✗ Circuito abierto o alta resistencia")
```

### Medir Resistencia de Cable

```python
# Modo DC
device.set_frequency(0)
device.set_display_mode(DisplayMode.R_X)
device.set_offset(-1.0)

# Múltiples mediciones para promedio
resistencias = []
for i in range(10):
    r, x = device.measure()
    resistencias.append(r)
    time.sleep(0.1)

r_promedio = sum(resistencias) / len(resistencias)
print(f"Resistencia cable: {r_promedio:.4f} Ω")
```

---

## 🔄 Cambio entre Modo DC y AC

### De AC a DC

```python
# Estaba en modo AC
device.set_frequency(1000)  # 1 kHz
device.set_display_mode(DisplayMode.Z_PHASE_DEG)
device.set_offset(0)

# Cambiar a DC
device.set_frequency(0)  # ← Activar modo DC
device.set_display_mode(DisplayMode.R_X)  # ← Cambiar a mode 6
device.set_offset(-1.0)  # ← Offset negativo
```

### De DC a AC

```python
# Estaba en modo DC
device.set_frequency(0)
device.set_offset(-1.0)

# Cambiar a AC
device.set_offset(0)  # ← Offset a 0 o positivo
device.set_frequency(1000)  # ← Frecuencia AC
# Display mode puede ser cualquiera
```

---

## 📚 Validaciones en el Dashboard

El dashboard implementa validaciones automáticas:

```python
def apply_config(n, freq, mag, offset, display_mode, mdelay, tdelay):
    # Validar modo DC
    if freq == 0:
        # Requiere display mode 6
        if display_mode != 6:
            return "⚠️ Modo DC requiere display mode R,X (6)"
        
        # Requiere offset negativo
        if offset >= 0:
            return "⚠️ Modo DC requiere offset negativo (ej: -1)"
    
    # Aplicar configuración...
```

**Feedback visual**:
- 🟡 Hint amarillo cuando `freq = 0`: "⚠️ Usar offset negativo si freq=0 (DC)"
- ✅ Confirmación: "✓ Modo DC activado (R only, offset=-1V)"
- ❌ Error: "⚠️ Modo DC requiere offset negativo (ej: -1)"

---

## 🎓 Casos de Uso Recomendados

### 1. Verificación de Conexiones
- Resistencia muy baja (< 1Ω): Continuidad OK
- Resistencia alta (> 1MΩ): Circuito abierto

### 2. Caracterización de Resistores
- Medición precisa de valor DC
- Comparación con valor nominal
- Detección de deriva térmica

### 3. Medición de Cables/PCB
- Resistencia de trazas PCB
- Resistencia de cables de alimentación
- Pérdidas en conectores

### 4. Test de Componentes
- Resistores (valor DC)
- Fusibles (continuidad)
- Switches (abierto/cerrado)
- Relés (estado contactos)

---

## 📖 Referencias

- **Documentación Oficial**: [DOCUMENTACION_OFICIAL.md](DOCUMENTACION_OFICIAL.md#mediciones-de-resistencia-dc)
- **Sección**: "Mediciones de Resistencia DC"
- **README**: [README.md](README.md)
- **Dashboard**: [README_DASHBOARD.md](README_DASHBOARD.md)

---

**Última actualización**: Octubre 2025  
**Versión Dashboard**: 3.2+  
**Firmware Compatible**: 1.3.2+
