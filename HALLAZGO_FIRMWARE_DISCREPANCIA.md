# HALLAZGO: Discrepancia entre Firmware 1.2.2 y Documentación Oficial

**Fecha**: 16 de Octubre, 2025  
**Dispositivo**: EVAL-ADMX2001  
**Firmware actual**: 1.2.2 (Build RT-2, Abril 2024)

---

## 📋 RESUMEN EJECUTIVO

La solución implementada (enviar comando `z` por cada punto) es **correcta para firmware 1.2.2**, pero **difiere de la documentación oficial** de Analog Devices.

---

## 🔍 HALLAZGO PRINCIPAL

### Lo que dice la Documentación Oficial:

```bash
ADMX2001> count 11
sampleCount = 11
ADMX2001> sweep_type frequency 100 1000
sweep type is frequency
ADMX2001> sweep_scale log
Sweep scale is log
ADMX2001> z
1.000000e+05,5.683433e-13,8.149236e+07   ← Punto 1
1.258925e+05,5.704062e-13,4.727518e+07   ← Punto 2
...                                       ← Puntos 3-11
```

**Comportamiento esperado**: Un solo comando `z` devuelve TODOS los puntos del sweep.

### Lo que hace Firmware 1.2.2:

```bash
ADMX2001> count 5
sampleCount = 5
ADMX2001> sweep_type frequency 1 100
sweep type is frequency
ADMX2001> sweep_scale linear
Sweep scale is linear
ADMX2001> z
1.000000e+03,2.137901e+01,-1.537983e+03   ← Solo 1 punto
ADMX2001>                                  ← Prompt regresa
```

**Comportamiento real**: Solo devuelve el PRIMER punto. Para obtener los demás, hay que enviar `z` de nuevo.

---

## ✅ SOLUCIÓN IMPLEMENTADA

Modificamos `lib/admx2001.py` método `perform_sweep()` para:

```python
# Configurar sweep
configure_sweep(...)

# Para cada punto del sweep
for point_num in range(expected_count):
    send('z')              # Solicitar punto individual
    data = read_response() # Leer respuesta
    parse_and_store(data)  # Guardar datos
```

**Resultado**: ✓ 5/5 puntos recibidos correctamente en 26 segundos.

---

## 📊 PRUEBAS REALIZADAS

| Método | Descripción | Resultado | Puntos |
|--------|-------------|-----------|--------|
| Solo `z` | Configurar sweep + un `z` | ❌ | 1/5 |
| `tcount` + `z` | Configurar tcount + un `z` | ❌ | 1/5 |
| `initiate` + `trigger` | Modo trigger múltiple | ❌ | 1/5 |
| **Múltiples `z`** | **Enviar `z` por punto** | **✓** | **5/5** |

**Archivo de prueba**: `test_official_method.py`

---

## 🤔 POSIBLES EXPLICACIONES

### 1. Versiones de Firmware Diferentes

La documentación oficial dice:

> **Nota Importante**: Esta página aplica a las revisiones de hardware B y C, y versiones de firmware **1.3.1, 1.3.2, y 1.3.3**.

Nuestro firmware es **1.2.2**, que es **anterior** a las versiones mencionadas en la documentación.

### 2. Características Añadidas en Versiones Posteriores

Tabla de versiones de firmware de la documentación:

| Versión | Estado | Características |
|---------|--------|-----------------|
| **1.3.2** | Estable | **Optimizaciones de tiempo de medición**, correcciones menores |
| **1.3.1** | Estable | Mejoras sustanciales de ruido, correcciones y más |
| 1.2.4 | Estable | Mismo que 1.2.2, script de instalación añadido |
| **1.2.2** | Estable | Calibración sobre frecuencia, salidas digitales, trigger externo |

Las "optimizaciones de tiempo de medición" en 1.3.2 probablemente incluyen sweeps automáticos.

### 3. Modo Trigger Optimizado

La documentación menciona un "modo trigger" optimizado en versiones 1.3.2+:

> **Modo Trigger:**
> - Usar `initiate` para entrar en modo trigger
> - Usar `trigger` para ejecutar medición
> - Los atributos se bloquean, ahorrando tiempo de configuración
> - **Mediciones típicas: 10-12 ms**

En firmware 1.2.2, cada punto toma **~5 segundos**. En 1.3.2+ podría ser **~12 ms**, una mejora de **400x**.

---

## 💡 RECOMENDACIONES

### Opción 1: Mantener Solución Actual ✓
- **Ventajas**: Ya funciona, probado, no requiere cambios de hardware
- **Desventajas**: Sweeps lentos (~5 seg/punto = 500 seg para 100 puntos)
- **Cuándo usar**: Si no tienes acceso a programador USB Blaster

### Opción 2: Actualizar a Firmware 1.3.2 ⭐ (RECOMENDADO)
- **Ventajas**: 
  - Sweeps potencialmente 400x más rápidos (12ms vs 5s por punto)
  - Comportamiento consistente con documentación
  - Mejoras de ruido y correcciones
  - Código más simple (un solo `z` por sweep)
- **Desventajas**:
  - Requiere Intel Altera USB Blaster (~$50 USD)
  - Posible pérdida de calibración
  - Proceso delicado (20-30 segundos sin interrupciones)
- **Cuándo usar**: Si necesitas sweeps de muchos puntos frecuentemente

### Opción 3: Solución Híbrida
- Mantener código actual compatible con ambas versiones
- Detectar versión de firmware al inicio
- Usar método apropiado según versión
- **Ventajas**: Máxima compatibilidad
- **Desventajas**: Código más complejo

---

## 📝 ACTUALIZACIÓN NECESARIA EN CÓDIGO

Si actualizas a firmware 1.3.2, podrías simplificar `perform_sweep()`:

```python
def perform_sweep(self, timeout=None):
    # ... configuración ...
    
    # Enviar UN solo comando 'z'
    self.serial.write(b'z\n')
    self.serial.flush()
    
    # Leer TODOS los puntos
    all_data_lines = []
    while len(all_data_lines) < expected_count:
        line = self.serial.readline()
        if is_data_line(line):
            all_data_lines.append(line)
        if is_prompt(line) and len(all_data_lines) == expected_count:
            break
    
    # Parsear resultados
    return parse_results(all_data_lines)
```

Mucho más simple y rápido.

---

## 📞 SIGUIENTE PASO

**Para obtener firmware 1.3.2**:

Email: **admx-support@analog.com**

Solicitar:
- Firmware 1.3.2 para ADMX2001B
- Script de instalación `admx2001_flash_pof.py`
- Instrucciones de actualización
- Confirmación de si sweeps automáticos están implementados

**Equipo necesario**:
- Intel Altera USB Blaster (Amazon ~$50)
- Python 3.7+
- Intel Quartus Prime Programmer And Tools (gratis)

---

## 🔗 REFERENCIAS

- **DOCUMENTACION_OFICIAL.md**: Documentación completa del dispositivo
- **SOLUCION_SWEEP_TIMEOUT.md**: Solución implementada para firmware 1.2.2
- **test_official_method.py**: Script de pruebas comparativas
- **check_firmware_version.py**: Script para verificar versión de firmware

---

## ✅ ESTADO ACTUAL

| Item | Estado |
|------|--------|
| Problema identificado | ✓ |
| Causa raíz descubierta | ✓ |
| Solución para 1.2.2 implementada | ✓ |
| Solución validada | ✓ (5/5 puntos) |
| Documentado | ✓ |
| Discrepancia con docs explicada | ✓ |
| Actualización a 1.3.2 | ⏳ Pendiente |

---

**Conclusión**: La solución actual es correcta y funcional para firmware 1.2.2. Actualizar a 1.3.2 podría mejorar drásticamente el rendimiento de sweeps.
