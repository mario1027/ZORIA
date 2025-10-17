# 🎛️ Simulador de Circuitos RLC

Aplicación web profesional para el análisis de circuitos RLC mediante diagramas de Bode y Nyquist.

## ✨ Características

- **11 tipos de circuitos**:
  - Componentes individuales: R, L, C
  - Combinaciones RC: Serie y Paralelo
  - Combinaciones RL: Serie y Paralelo
  - Combinaciones LC: Serie y Paralelo
  - Circuitos RLC: Serie y Paralelo

- **Análisis completo**:
  - Diagrama de Bode (Magnitud y Fase)
  - Diagrama de Nyquist (Plano complejo)
  - Frecuencia de resonancia (LC y RLC)
  - Factor de calidad Q (RLC)

- **Interfaz profesional**:
  - Tema Volt Bootstrap 5 Dashboard
  - Diseño responsivo
  - Formularios con iconos
  - Gráficas interactivas con Plotly

## 🚀 Instalación

1. **Clonar o navegar al directorio del proyecto**:
```bash
cd simulador-rlc
```

2. **Crear entorno virtual** (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# venv\Scripts\activate  # En Windows
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

## 🎮 Uso

### Modo Desarrollo
```bash
python app.py
```
La aplicación estará disponible en: `http://localhost:5000`

### Modo Producción
```bash
python server.py
```
La aplicación estará disponible en: `http://localhost:8050`

## 📊 Guía de Uso

1. **Seleccionar tipo de circuito** en el selector desplegable
2. **Ingresar valores de componentes**:
   - Resistencia (R) en Ohmios (Ω)
   - Inductancia (L) en Henrios (H)
   - Capacitancia (C) en Faradios (F)
3. **Configurar rango de frecuencias**:
   - Frecuencia inicial (Hz)
   - Frecuencia final (Hz)
   - Número de puntos (100-10000)
4. **Hacer clic en "Calcular Impedancia"**
5. **Visualizar resultados**:
   - Diagrama de Bode con magnitud y fase
   - Diagrama de Nyquist en plano complejo
   - Información del circuito (resonancia, Q, etc.)

## 🧮 Ejemplos de Valores

### RC Pasa-Altos (RC Serie)
- R = 1000 Ω (1 kΩ)
- C = 0.000001 F (1 µF)
- Frecuencia: 1 Hz - 100 kHz

### RL Pasa-Bajos (RL Serie)
- R = 1000 Ω (1 kΩ)
- L = 0.001 H (1 mH)
- Frecuencia: 1 Hz - 1 MHz

### RLC Resonante Serie
- R = 100 Ω
- L = 0.001 H (1 mH)
- C = 0.000001 F (1 µF)
- Frecuencia de resonancia ≈ 5033 Hz

## 📦 Dependencias Principales

- **Flask**: Servidor web
- **Dash**: Framework de aplicaciones web
- **dash-spa**: Sistema de enrutamiento de páginas
- **Plotly**: Gráficas interactivas
- **NumPy**: Cálculos numéricos
- **Waitress**: Servidor WSGI de producción

## 🏗️ Estructura del Proyecto

```
simulador-rlc/
├── app.py                      # Configuración principal de la aplicación
├── server.py                   # Servidor de producción
├── themes.py                   # Configuración del tema Volt
├── requirements.txt            # Dependencias Python
├── assets/                     # Recursos estáticos (CSS, JS, imágenes)
└── pages/
    ├── simulator_page.py       # Página principal del simulador
    ├── common/                 # Componentes comunes (sidebar, topbar, footer)
    ├── icons/                  # Sistema de iconos
    └── simulator/
        ├── components.py       # Componentes UI del simulador
        └── impedance_calculator.py  # Motor de cálculo de impedancias
```

## 🎨 Tema Visual

El proyecto utiliza el tema **Volt Bootstrap 5 Dashboard**, que proporciona:
- Esquema de colores profesional con fondo oscuro
- Componentes Bootstrap 5 nativos
- Iconos Font Awesome 5
- Diseño responsivo y moderno

## 🧪 Tecnología

- **Backend**: Flask + DashSPA
- **Frontend**: Dash + Bootstrap 5
- **Cálculos**: NumPy (números complejos)
- **Visualización**: Plotly (gráficas interactivas)
- **Estilo**: Volt Dashboard Theme

## 📝 Notas Técnicas

### Cálculo de Impedancia
La impedancia se calcula usando números complejos de NumPy:
- `Z_R = R` (resistencia pura)
- `Z_L = j*ω*L` (inductancia pura)
- `Z_C = 1/(j*ω*C)` (capacitancia pura)

### Diagramas
- **Bode**: Muestra magnitud (dB) y fase (°) vs frecuencia (escala log)
- **Nyquist**: Muestra parte imaginaria vs parte real de la impedancia

### Resonancia
Para circuitos LC y RLC:
- Frecuencia: `f₀ = 1/(2π√(LC))`
- Factor de calidad (serie): `Q = (ωL)/R = 1/(ωRC)`
- Factor de calidad (paralelo): `Q = R/(ωL) = ωRC`

## 🤝 Créditos

- **Plantilla Base**: Volt Bootstrap 5 Dashboard
- **Framework**: Dash by Plotly
- **Enrutamiento**: dash-spa

## 📄 Licencia

Este proyecto es de uso educativo y demostrativo.

---

**¡Disfruta analizando circuitos RLC! ⚡🔋🌊**
