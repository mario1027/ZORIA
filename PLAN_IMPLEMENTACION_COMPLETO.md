# 🚀 Plan de Implementación Completo - ADMX2001 Dashboard

## ❌ Errores Corregidos

### 1. Error de Alert
**Error:** `TypeError: Alert.__init__() got an unexpected keyword argument 'confirmButtonText'`

**Solución:** ✅ Eliminado parámetro `confirmButtonText` de todos los `Alert()`. La API de dash_spa usa SweetAlert2 directamente sin este parámetro.

### 2. Footer Vertical
**Error:** Footer aparecía vertical a la izquierda en vez de horizontal abajo.

**Solución:** ✅ Actualizado footer con:
- Clase `mt-auto w-100` para posicionamiento
- Clase `border-top py-4` para estilo
- Eliminado `rounded shadow` que causaba conflictos
- Centrado horizontal con `text-center`

---

## 📋 Funcionalidades Faltantes (Según Documentación Oficial)

Basándome en `DOCUMENTACION_OFICIAL.md` y la biblioteca `lib/admx2001.py`, las siguientes funcionalidades están ausentes:

### 1. ⚙️ **CALIBRACIÓN COMPLETA**

#### Estado Actual
- ❌ No hay página de calibración
- ❌ No se puede realizar calibración Open/Short/Load
- ❌ No se pueden guardar/cargar coeficientes
- ❌ No se muestra tabla de coeficientes
- ❌ No se puede cambiar entre conjuntos (evalkit/default)

#### Funcionalidades Requeridas (según docs)
```python
# Calibración básica
device.calibrate_open()
device.calibrate_short()
device.calibrate_load(resistance, reactance)
device.calibrate_commit()

# Gestión de coeficientes
device.calibration.read_coefficients()
device.calibration.write_coefficients(coeffs)
device.calibration.switch_set('evalkit')  # o 'default'

# Temperatura
device.measure_temperature()
```

#### Implementación Requerida
- **Página:** `pages/calibration/calibration_page.py`
- **Ruta:** `/calibration`
- **Componentes:**
  - Card con botones: Open, Short, Load, Commit
  - Inputs para Load (R, X)
  - Display de temperatura actual
  - Selector de conjunto (evalkit/default)
  - Tabla de coeficientes con:
    - Frecuencia
    - Gain CH0/CH1
    - Go, Gs (complex)
    - Gc, Gf (complex)
    - Paginación (10 filas por página)
    - Búsqueda por frecuencia
    - Botón exportar CSV

---

### 2. 📐 **CONFIGURACIÓN AVANZADA**

#### Estado Actual
- ⚠️ Display Mode: Solo 1 opción (R, X)
- ❌ Gain: No configurable (siempre auto)
- ❌ Triggers: No disponibles
- ❌ GPIO: No disponible
- ❌ LED: No disponible

#### Funcionalidades Requeridas

**A. 18 Modos de Display**

Según documentación oficial (página 222):

| Modo | Nombre | Unidades |
|------|--------|----------|
| 0 | Cs, Rs | Farads, Ohms |
| 1 | Cs, D | Farads, Dimensionless |
| 2 | Cs, Q | Farads, Dimensionless |
| 3 | Ls, Rs | Henries, Ohms |
| 4 | Ls, D | Henries, Dimensionless |
| 5 | Ls, Q | Henries, Dimensionless |
| 6 | R, X | Ohms, Ohms |
| 7 | G, B | Siemens, Siemens |
| 8 | |Z|, θ° | Ohms, Degrees |
| 9 | |Z|, θr | Ohms, Radians |
| 10 | |Y|, θ° | Siemens, Degrees |
| 11 | |Y|, θr | Siemens, Radians |
| 12 | Cp, Rp | Farads, Ohms |
| 13 | Cp, D | Farads, Dimensionless |
| 14 | Cp, Q | Farads, Dimensionless |
| 15 | Lp, Rp | Henries, Ohms |
| 16 | Lp, D | Henries, Dimensionless |
| 17 | Lp, Q | Henries, Dimensionless |
| 18 | Lp, Gp | Henries, Siemens |

```python
device.set_display_mode(DisplayMode.R_X)  # Modo 6
```

**B. Configuración de Ganancia**

```python
# Auto-ranging (default)
device.set_gain_auto()

# Manual
device.set_gain_manual(ch0_gain=0, ch1_gain=2)

# Por canal
device.set_gain(channel=0, gain=1)
```

Rangos:
- CH0 (Voltaje): 0-3
- CH1 (Corriente): 0-3

**C. Triggers**

```python
device.set_trigger_mode('internal')  # o 'external'
device.set_trigger_delay(delay_ms)
device.set_tcount(count)
```

**D. GPIO y LED**

```python
device.set_gpio(pin, state)
device.set_led(state)
```

#### Implementación Requerida
- **Página:** `pages/config/config_page.py`
- **Ruta:** `/config`
- **Componentes:**
  - **Card "Modos de Display":**
    - Tabla con todos los 18 modos
    - Descripción de cada uno
    - Botón "Seleccionar" por fila
    - Modo actual resaltado
  - **Card "Ganancia":**
    - Radio: Auto / Manual
    - Si Manual: Sliders para CH0 (0-3) y CH1 (0-3)
    - Info de rangos de impedancia recomendados
  - **Card "Triggers":**
    - Radio: Internal / External
    - Input: Trigger Delay (ms)
    - Input: Trigger Count
  - **Card "GPIO/LED":**
    - Switches para GPIO pins
    - Toggle para LED

---

### 3. 💾 **BASE DE DATOS DE MEDICIONES**

#### Estado Actual
- ❌ No hay almacenamiento persistente
- ❌ No hay historial de mediciones
- ❌ No se pueden exportar mediciones individuales
- ❌ No hay búsqueda/filtrado

#### Funcionalidades Requeridas

**Almacenamiento:**
- SQLite local con tabla `measurements`:
  - id (autoincrement)
  - timestamp
  - frequency (Hz)
  - magnitude (V)
  - offset (V)
  - display_mode
  - value1 (depende del modo)
  - value2 (depende del modo)
  - z_real, z_imag, z_mag, phase
  - notes (texto opcional)

**Interfaz:**
- Tabla con paginación (10/25/50/100 por página)
- Búsqueda por:
  - Rango de fechas
  - Rango de frecuencias
  - Display mode
- Ordenamiento por columna
- Botones:
  - Ver detalles (modal con toda la info)
  - Exportar selección (CSV/Excel)
  - Eliminar
- Gráficos:
  - Histograma de frecuencias medidas
  - Timeline de mediciones
  - Comparar múltiples mediciones

#### Implementación Requerida
- **Página:** `pages/database/database_page.py`
- **Ruta:** `/database`
- **Backend:** `lib/database.py` con SQLAlchemy
- **Componentes:**
  - Filtros (fecha, frecuencia, modo)
  - Tabla con paginación estilo Volt
  - Botones de acción
  - Modal de detalles
  - Gráficos con plotly

---

### 4. ℹ️ **INFORMACIÓN DEL SISTEMA**

#### Estado Actual
- ❌ No se muestra información del dispositivo
- ❌ No hay diagnósticos
- ❌ No hay logs visibles

#### Funcionalidades Requeridas

**Información del Dispositivo:**
```python
idn = device.get_idn()  # Identificación
version = device.version()  # Versión firmware
temp = device.measure_temperature()  # Temperatura
```

**Diagnósticos:**
- Estado de conexión
- Última calibración
- Configuración actual completa
- Estado de memoria
- Logs de errores

#### Implementación Requerida
- **Página:** `pages/system/system_page.py`
- **Ruta:** `/system`
- **Componentes:**
  - Card "Información del Dispositivo"
  - Card "Estado del Sistema"
  - Card "Logs" (tabla con timestamp, nivel, mensaje)
  - Botón "Diagnóstico Completo"

---

## 🎨 Actualización del Sidebar

### Estructura Actual
```
📊 Dashboard ADMX2001
🎯 Simulador RLC
```

### Estructura Requerida (Jerárquica con Dropdowns)

```
📊 Dashboard Principal (/)
🎯 Simulador RLC (/simulator)
────────────────────────────
⚙️ Calibración ▼
   └─ Calibración Básica (/calibration)
   └─ Tabla de Coeficientes (/calibration/coefficients)
📐 Configuración ▼
   └─ Modos de Display (/config/display)
   └─ Ganancia (/config/gain)
   └─ Triggers (/config/triggers)
   └─ GPIO/LED (/config/gpio)
💾 Base de Datos ▼
   └─ Mediciones (/database/measurements)
   └─ Historial (/database/history)
   └─ Exportar (/database/export)
ℹ️ Sistema ▼
   └─ Información (/system/info)
   └─ Diagnósticos (/system/diagnostics)
   └─ Logs (/system/logs)
```

### Implementación
Usar componente `DropdownFolderAIO` existente en `pages/common/dropdown_folder_aoi.py`

---

## 📦 Plan de Desarrollo por Fases

### FASE 1: Calibración (PRIORITARIO)
**Tiempo estimado:** 2-3 horas

1. ✅ Crear `pages/calibration/` directory
2. ✅ Crear `calibration_page.py` con layout básico
3. ✅ Implementar botones Open/Short/Load/Commit
4. ✅ Agregar selector de conjunto (evalkit/default)
5. ✅ Mostrar temperatura actual
6. ✅ Tabla de coeficientes con paginación
7. ✅ Integrar con `lib/calibration.py`
8. ✅ Actualizar sidebar

### FASE 2: Configuración Avanzada
**Tiempo estimado:** 2-3 horas

1. ✅ Crear `pages/config/` directory
2. ✅ Crear `config_page.py` con tabs
3. ✅ Implementar tabla de 18 modos de display
4. ✅ Implementar configuración de ganancia
5. ✅ Implementar configuración de triggers
6. ✅ Implementar control GPIO/LED
7. ✅ Actualizar sidebar con dropdown

### FASE 3: Base de Datos
**Tiempo estimado:** 3-4 horas

1. ✅ Crear `lib/database.py` con SQLAlchemy
2. ✅ Definir modelo `Measurement`
3. ✅ Crear `pages/database/` directory
4. ✅ Implementar tabla con paginación
5. ✅ Implementar búsqueda/filtrado
6. ✅ Implementar exportación CSV/Excel
7. ✅ Agregar gráficos históricos
8. ✅ Integrar con callbacks del dashboard principal

### FASE 4: Sistema e Información
**Tiempo estimado:** 1-2 horas

1. ✅ Crear `pages/system/` directory
2. ✅ Implementar página de información
3. ✅ Implementar diagnósticos
4. ✅ Implementar visor de logs
5. ✅ Actualizar sidebar

### FASE 5: Testing y Documentación
**Tiempo estimado:** 1-2 horas

1. ✅ Tests de navegación
2. ✅ Tests de cada página
3. ✅ Verificar responsive
4. ✅ Actualizar documentación
5. ✅ Crear guía de usuario

---

## 🎯 Prioridades

### CRÍTICO (Hacer YA)
1. ✅ Arreglar error de Alert
2. ✅ Arreglar footer
3. ⚠️ Crear página de Calibración (FUNCIONALIDAD CORE)
4. ⚠️ Agregar 18 modos de display

### IMPORTANTE (Próximo)
1. ⚠️ Base de datos de mediciones
2. ⚠️ Configuración de ganancia
3. ⚠️ Sistema de información

### DESEABLE (Futuro)
1. ⚠️ Triggers externos
2. ⚠️ GPIO/LED
3. ⚠️ Gráficos históricos avanzados

---

## 📝 Notas de Implementación

### Tablas con Paginación (Estilo Plantilla)

Usar componente dash-bootstrap-components `Table` con callbacks custom:

```python
def create_paginated_table(data, page_size=10):
    return html.Div([
        # Búsqueda
        dbc.Input(id='table-search', placeholder='Buscar...'),
        
        # Tabla
        dbc.Table(
            id='data-table',
            bordered=True,
            hover=True,
            responsive=True,
            striped=True
        ),
        
        # Paginación
        dbc.Row([
            dbc.Col([
                dbc.Select(
                    id='page-size',
                    options=[
                        {'label': '10', 'value': 10},
                        {'label': '25', 'value': 25},
                        {'label': '50', 'value': 50},
                        {'label': '100', 'value': 100}
                    ],
                    value=10
                )
            ], width=2),
            dbc.Col([
                dbc.Pagination(id='pagination', max_value=10)
            ])
        ])
    ])
```

### SPA Notifications Correctas

```python
# Toast (Notyf)
notyf = Notyf(
    message='<b>Éxito</b><br>Operación completada',
    type='success',  # 'success', 'error', 'warning', 'info'
    duration=3000
)
return notyf.report()

# Alert (SweetAlert2)
alert = Alert(
    'Título',
    'Mensaje',
    icon='success'  # 'success', 'error', 'warning', 'info', 'question'
    # NO usar confirmButtonText, timer, showConfirmButton, etc.
)
return alert.report()
```

---

## ✅ Estado Actual del Proyecto

### Completado
- [x] Componentes compartidos (sidebar, navbar, footer)
- [x] Dashboard principal con gráficos
- [x] Simulador RLC
- [x] Navegación bidireccional
- [x] Modal de conexión
- [x] Notificaciones SPA básicas
- [x] Fix error Alert
- [x] Fix footer horizontal

### En Progreso
- [ ] **Calibración** (0%)
- [ ] **Configuración Avanzada** (0%)
- [ ] **Base de Datos** (0%)
- [ ] **Sistema** (0%)

### Pendiente
- [ ] Tests de nuevas páginas
- [ ] Documentación actualizada
- [ ] Responsive testing completo

---

## 🚀 Próximos Pasos INMEDIATOS

1. **Crear estructura de directorios:**
   ```bash
   mkdir -p pages/calibration
   mkdir -p pages/config
   mkdir -p pages/database
   mkdir -p pages/system
   ```

2. **Implementar Página de Calibración** (PRIORITARIO)
   - Crear `calibration_page.py`
   - Agregar al `app.py`
   - Actualizar sidebar con dropdown

3. **Implementar Tabla de 18 Modos de Display**
   - Crear `config_page.py`
   - Tabla interactiva con selección
   - Integrar con dashboard principal

4. **Crear Base de Datos SQLite**
   - Schema para mediciones
   - CRUD operations
   - Página de visualización

---

**Última actualización:** 20 de octubre de 2025  
**Estado:** Plan completo listo para implementación  
**Progreso general:** 40% completado
