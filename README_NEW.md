# EVAL-ADMX2001 - Analizador de Impedancia de Precisión

Sistema completo de control, medición y análisis para el analizador de impedancia **EVAL-ADMX2001** de Analog Devices.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Dash](https://img.shields.io/badge/Dash-2.0+-red.svg)](https://dash.plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 Descripción

Dashboard web profesional con interfaz gráfica para control total del dispositivo EVAL-ADMX2001:

- **Mediciones en tiempo real** de impedancia, fase, y parámetros RLC
- **Barridos de frecuencia** con visualización Bode y Nyquist
- **Calibración completa** (Open, Short, Load)
- **Export CSV** optimizado para Origin, pandas, Excel, MATLAB, R
- **Zoom funcional** en gráficos durante y después de barridos ✨ **NUEVO**

---

## ✨ Características Principales

### Dashboard Web Interactivo
- 🎨 Interfaz moderna con Bootstrap y SweetAlert2
- 📊 Gráficos interactivos con Plotly (zoom, pan, export PNG)
- 🔄 Actualización en tiempo real (500ms)
- 📈 Visualización simultánea Bode + Nyquist
- 💾 Export CSV con 9 columnas de datos

### Mejoras Recientes (Octubre 2025)

#### ✅ Zoom Persistente
- **Problema resuelto**: El zoom ya no se revierte durante barridos
- **Implementación**: Sistema de detección de cambios con `dash.no_update`
- **Resultado**: Análisis detallado completamente funcional
- Ver: [ZOOM_FIX_README.md](ZOOM_FIX_README.md)

#### ✅ Export CSV Mejorado
- 9 columnas con múltiples escalas de frecuencia
- Formato científico (%.6e) compatible con software profesional
- Listo para Origin, pandas, Excel, MATLAB, R
- Documentación completa de uso

#### ✅ Gráficos Profesionales
- **Bode**: Eje dual (magnitud log + fase lineal) en un solo gráfico
- **Nyquist**: Colormap por frecuencia, aspecto ratio 1:1, hover con frecuencia
- **Controles**: Zoom, pan, box select, lasso select, exportar PNG

---

## 🚀 Instalación Rápida

### Requisitos
- Python 3.8+
- Puerto serie USB disponible
- EVAL-ADMX2001 conectado

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/mario1027/libeval.git
cd libeval

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar dashboard
python3 dashboard_complete.py
```

Abrir navegador en: **http://localhost:8050**

---

## 📖 Uso Básico

### 1. Conectar Dispositivo
1. Conectar EVAL-ADMX2001 por USB
2. En el dashboard, seleccionar puerto serie
3. Click en "Conectar"
4. Esperar confirmación (ícono verde)

### 2. Medición en Tiempo Real
1. Configurar frecuencia (100 Hz - 10 MHz)
2. Seleccionar rango de impedancia
3. Click en "Iniciar Medición"
4. Ver valores en tiempo real

### 3. Barrido de Frecuencia
1. Configurar rango: Inicio, Fin, Puntos
2. Seleccionar escala: Lineal/Logarítmica
3. Click en "Iniciar Barrido"
4. Ver progreso en tiempo real
5. Analizar con zoom en gráficos ✨
6. Exportar datos a CSV

### 4. Calibración
1. Menú Calibración
2. Seguir pasos: Open → Short → Load
3. Confirmar calibración
4. ¡Listo para mediciones precisas!

---

## 📁 Estructura del Proyecto

```
EVAL-ADMX2001/
├── dashboard_complete.py          # Dashboard web completo
├── lib/                           # Biblioteca Python
│   ├── __init__.py
│   ├── admx2001.py               # Clase principal del dispositivo
│   ├── enums.py                  # Enumeraciones (modos, rangos)
│   ├── calibration.py            # Sistema de calibración
│   ├── exceptions.py             # Excepciones personalizadas
│   └── utils.py                  # Utilidades
├── requirements.txt              # Dependencias
├── README.md                     # Este archivo
├── ZOOM_FIX_README.md           # Documentación fix de zoom
├── DOCUMENTACION_OFICIAL.md     # Referencia del dispositivo
├── INDICE.md                    # Índice de documentación
├── FIX_MODO_DC.md               # Fix modo DC
├── MODO_DC_RESISTANCE.md        # Documentación modo DC
└── IMPLEMENTACION_DELAYS_NATIVOS.md  # Delays nativos
```

---

## 🎨 Dashboard Web

### Funcionalidades

#### Medición en Tiempo Real
- Gráfico actualizado cada 500ms
- Valores numéricos: Z', Z'', |Z|, θ
- Indicadores de estado
- Control de rango automático/manual

#### Barrido de Frecuencia
- **Configuración flexible**:
  - Rango: 0.2 Hz - 10 MHz
  - Puntos: 2-255 (según ancho de banda)
  - Escala: Lineal o Logarítmica
  - Delays configurables (mdelay, tdelay)

- **Visualización dual**:
  - Diagrama de Bode (magnitud + fase)
  - Diagrama de Nyquist (Z' vs -Z'')
  
- **Zoom funcional** ✨:
  - Persiste durante el barrido
  - Funciona después de completar
  - Análisis detallado sin interrupciones

- **Export CSV**:
  - Botón de descarga instantánea
  - 9 columnas de datos
  - Compatible con software profesional

#### Sistema de Calibración
- Interfaz guiada paso a paso
- Validación de cada etapa
- Persistencia en memoria del dispositivo
- Indicadores visuales de estado

---

## 📚 Documentación

### Archivos de Referencia
- **[DOCUMENTACION_OFICIAL.md](DOCUMENTACION_OFICIAL.md)**: Manual completo del dispositivo
- **[INDICE.md](INDICE.md)**: Índice de toda la documentación
- **[ZOOM_FIX_README.md](ZOOM_FIX_README.md)**: Fix de zoom persistente ✨
- **[FIX_MODO_DC.md](FIX_MODO_DC.md)**: Corrección modo DC
- **[MODO_DC_RESISTANCE.md](MODO_DC_RESISTANCE.md)**: Mediciones DC
- **[IMPLEMENTACION_DELAYS_NATIVOS.md](IMPLEMENTACION_DELAYS_NATIVOS.md)**: Delays del dispositivo

### Comandos Principales

```python
from lib import ADMX2001, DisplayMode, ImpedanceRange

# Conectar
device = ADMX2001('/dev/ttyUSB0')
device.connect()

# Medir
result = device.measure_impedance(freq_hz=1000, 
                                  range_val=ImpedanceRange.AUTO)
print(f"Z = {result['z_magnitude']:.2f} Ω")

# Barrido
results = device.frequency_sweep(
    start_hz=100,
    end_hz=100000,
    points=50,
    scale='log'
)

# Calibrar
device.calibrate_open()
device.calibrate_short()
device.calibrate_load(100)  # 100Ω
device.commit_calibration()
```

---

## 🛠️ Tecnologías

- **Python 3.8+**: Lenguaje base
- **Dash 2.0+**: Framework web interactivo
- **Plotly**: Gráficos interactivos profesionales
- **Bootstrap 5**: Diseño responsive
- **SweetAlert2**: Alertas elegantes
- **pandas**: Manipulación de datos
- **numpy**: Cálculos numéricos
- **pyserial**: Comunicación serie

---

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Puerto serie por defecto
export ADMX2001_PORT=/dev/ttyUSB0

# Nivel de logging
export ADMX2001_DEBUG=1
```

### Parámetros del Dashboard
Editar en `dashboard_complete.py`:
```python
# Puerto del servidor
PORT = 8050

# Intervalo de actualización (ms)
INTERVAL = 500

# Tamaño de buffer
QUEUE_SIZE = 100
```

---

## 🐛 Solución de Problemas

### Dispositivo no conecta
- Verificar cable USB
- Verificar permisos: `sudo usermod -a -G dialout $USER`
- Reiniciar dispositivo
- Probar otro puerto USB

### Zoom no funciona
- ✅ **RESUELTO** en última versión
- Ver [ZOOM_FIX_README.md](ZOOM_FIX_README.md)

### Barrido lento
- Reducir número de puntos
- Aumentar `mdelay` (estabilización)
- Verificar rango de impedancia

### Datos inconsistentes
- Realizar calibración completa
- Verificar conexiones del DUT
- Usar rango apropiado

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas:

1. Fork del repositorio
2. Crear rama: `git checkout -b feature/nueva-caracteristica`
3. Commit: `git commit -m 'Agregar nueva característica'`
4. Push: `git push origin feature/nueva-caracteristica`
5. Pull Request

---

## 📝 Changelog

### Versión Actual (Octubre 2025)
- ✨ **Fix: Zoom persistente** en gráficos Bode y Nyquist
- 📊 **Mejora: Gráficos profesionales** con eje dual en Bode
- 💾 **Feature: Export CSV** con 9 columnas optimizado
- 🎨 **Mejora: Hover tooltips** con información de frecuencia
- ⚡ **Optimización: Performance** con detección de cambios

### Versiones Anteriores
- Fix modo DC resistance
- Implementación delays nativos
- Sistema de calibración completo
- Dashboard web inicial

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 👤 Autor

**mario1027**
- GitHub: [@mario1027](https://github.com/mario1027)
- Proyecto: [libeval](https://github.com/mario1027/libeval)

---

## 🙏 Agradecimientos

- Analog Devices por la documentación del EVAL-ADMX2001
- Comunidad de Dash y Plotly
- Contribuidores del proyecto

---

## 📞 Soporte

¿Problemas o preguntas?
- 📧 Abrir un [Issue en GitHub](https://github.com/mario1027/libeval/issues)
- 📖 Revisar la [Documentación](DOCUMENTACION_OFICIAL.md)
- 💬 Revisar issues cerrados

---

<div align="center">

**⭐ Si este proyecto te resulta útil, considera darle una estrella en GitHub ⭐**

[Reportar Bug](https://github.com/mario1027/libeval/issues) · [Solicitar Feature](https://github.com/mario1027/libeval/issues) · [Ver Documentación](DOCUMENTACION_OFICIAL.md)

</div>
