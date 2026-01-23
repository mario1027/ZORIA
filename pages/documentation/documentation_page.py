"""
Página de Documentación Oficial del Software ZORIA
Sistema completo de documentación para el analizador de impedancia EVAL-ADMX2001
"""
from dash import html, dcc, Input, Output, callback
from dash_spa import register_page

# Importar componentes comunes compartidos
from pages.common.sidebar import sideBar
from pages.common.mobile_nav import mobileNavBar
from pages.common.footer import footer

# Registrar la página
register_page(
    __name__,
    path='/documentacion',
    title='Documentación - ZORIA',
    name='Documentación Oficial'
)


# ==================== COMPONENTES DE DOCUMENTACIÓN ====================

def doc_card(title, icon, content, color="primary"):
    """Tarjeta de documentación con estilo consistente"""
    return html.Div([
        html.Div([
            html.Div([
                html.H5([
                    html.I(className=f"fas fa-{icon} me-2 text-{color}"),
                    title
                ], className="mb-0")
            ], className=f"card-header border-bottom border-gray-300 p-3"),
            html.Div(content, className="card-body p-4")
        ], className="card border-0 shadow-sm h-100 mb-0")
    ], className="col-12 mb-4")


def info_table(headers, rows):
    """Tabla de información con estilo Volt"""
    return html.Div([
        html.Table([
            html.Thead([
                html.Tr([html.Th(h, className="border-bottom") for h in headers])
            ]),
            html.Tbody([
                html.Tr([html.Td(cell, className="border-bottom") for cell in row])
                for row in rows
            ])
        ], className="table table-hover")
    ])


def spec_badge(label, value, color="secondary"):
    """Badge con especificación técnica"""
    return html.Div([
        html.Span(label, className="text-muted small d-block mb-1"),
        html.Span(value, className=f"badge bg-{color} px-3 py-2 fs-6")
    ], className="mb-3")


def command_card(command, description):
    """Card para comando CLI"""
    return html.Div([
        html.Code(command, className="bg-dark text-success p-2 rounded d-block mb-2"),
        html.P(description, className="text-muted small mb-0")
    ], className="mb-3")


# ==================== LAYOUT ====================

def layout():
    """Layout principal de la página de documentación"""
    return html.Div([
        # Mobile Navbar
        mobileNavBar(),

        # Contenedor flex para sidebar y contenido
        html.Div([
            # Sidebar
            sideBar(),

            # Contenido principal
            html.Main([
                html.Div([
                    # Header
                    html.Div([
                        html.Div([
                            html.H2([
                                html.I(className="fas fa-book me-3"),
                                "Documentación Oficial"
                            ], className="h3 mb-1"),
                            html.P("Guía completa del software ZORIA y el analizador de impedancia EVAL-ADMX2001",
                                   className="text-muted mb-0 small")
                        ], className="col-12 col-md-8 mb-2 mb-md-0"),
                        html.Div([
                            html.Span([
                                html.I(className="fas fa-code-branch me-2"),
                                "v1.3.2"
                            ], className="badge bg-success px-3 py-2")
                        ], className="col-12 col-md-4 d-flex justify-content-md-end align-items-center")
                    ], className="row align-items-center py-4 mb-4"),

                    # Store para la pestaña activa
                    dcc.Store(id='doc-active-tab', data='quickstart', storage_type='session'),
                    
                    # Navegación por pestañas - Estilo mejorado
                    html.Div([
                        html.Button([
                            html.I(className="fas fa-rocket me-2"),
                            "Inicio Rápido"
                        ], id="btn-quickstart", className="btn btn-outline-primary active me-2 mb-2"),
                        html.Button([
                            html.I(className="fas fa-microchip me-2"),
                            "Hardware"
                        ], id="btn-hardware", className="btn btn-outline-primary me-2 mb-2"),
                        html.Button([
                            html.I(className="fas fa-laptop-code me-2"),
                            "Software"
                        ], id="btn-software", className="btn btn-outline-primary me-2 mb-2"),
                        html.Button([
                            html.I(className="fas fa-balance-scale me-2"),
                            "Calibración"
                        ], id="btn-calibration", className="btn btn-outline-primary me-2 mb-2"),
                        html.Button([
                            html.I(className="fas fa-terminal me-2"),
                            "CLI"
                        ], id="btn-cli", className="btn btn-outline-primary me-2 mb-2"),
                        html.Button([
                            html.I(className="fas fa-question-circle me-2"),
                            "Soporte"
                        ], id="btn-support", className="btn btn-outline-primary me-2 mb-2"),
                    ], className="d-flex flex-wrap mb-4 pb-3 border-bottom border-gray-300"),

                    # Contenido de las pestañas
                    html.Div([
                        
                        # ========== TAB 1: INICIO RÁPIDO ==========
                        html.Div([
                            html.Div([
                                # Paso 1
                                doc_card(
                                    "1. Instalación de Drivers",
                                    "download",
                                    [
                                        html.P([
                                            "Descarga e instala los drivers ",
                                            html.Strong("Virtual COM Port (VCP)"),
                                            " de FTDI para habilitar la comunicación UART."
                                        ], className="mb-3"),
                                        html.A([
                                            html.I(className="fas fa-external-link-alt me-2"),
                                            "Descargar Drivers FTDI"
                                        ], href="https://www.ftdichip.com/Drivers/VCP.htm", target="_blank",
                                           className="btn btn-primary btn-sm"),
                                    ],
                                    "info"
                                ),

                                # Paso 2
                                doc_card(
                                    "2. Conexión del Hardware",
                                    "plug",
                                    [
                                        html.Ol([
                                            html.Li("Inserta el módulo ADMX2001B en la placa EVAL-ADMX2001EBZ"),
                                            html.Li("Conecta el adaptador de corriente (9VDC)"),
                                            html.Li("Verifica que el LED de self-test esté verde"),
                                            html.Li("Conecta el cable UART a USB al puerto COM del PC")
                                        ], className="mb-0")
                                    ],
                                    "success"
                                ),

                                # Paso 3
                                doc_card(
                                    "3. Configuración Básica del Hardware",
                                    "cog",
                                    [
                                        html.P("Conexiones básicas requeridas para evaluar el EVAL-ADMX2001:", className="mb-3"),
                                        html.Ol([
                                            html.Li("Inserta el módulo ADMX2001B en la placa EVAL-ADMX2001EBZ (los conectores están codificados)"),
                                            html.Li("Configura los interruptores de selección de carga a OPEN y GND"),
                                            html.Li("Conecta el adaptador de corriente al jack de alimentación (9VDC)"),
                                            html.Li("Verifica que la luz LED de self-test sea verde (visible desde el lado inferior)"),
                                            html.Li("Conecta el cable UART a USB: TX(naranja)→TX, RX(amarillo)→RX, GND(negro)→GND"),
                                            html.Li("Asegura que el jumper CLK_SEL esté en posición INT (reloj interno)"),
                                            html.Li("Cambia los interruptores a posición DUT y GND"),
                                            html.Li("Usa los cables de prueba para conectar al dispositivo bajo prueba (DUT)")
                                        ], className="mb-3"),
                                        html.Div([
                                            html.I(className="fas fa-info-circle me-2"),
                                            html.Small("Los BNC rojos van a HCUR/HPOT, los BNC negros van a LPOT/LCUR")
                                        ], className="alert alert-info border-0 mt-3")
                                    ],
                                    "warning"
                                ),

                                # Paso 4
                                doc_card(
                                    "4. Uso del Software ZORIA",
                                    "laptop-code",
                                    [
                                        html.P("ZORIA proporciona una interfaz web moderna que elimina la necesidad de terminales CLI:", className="mb-3"),
                                        html.Div([
                                            html.Div([
                                                html.I(className="fas fa-chart-pie fa-3x text-primary mb-2"),
                                                html.H6("Dashboard", className="fw-bold mt-2"),
                                                html.P("Barridos de frecuencia con diagramas de Bode y Nyquist en tiempo real", className="small text-muted mb-0")
                                            ], className="col-md-6 text-center p-3 border rounded"),
                                            html.Div([
                                                html.I(className="fas fa-calculator fa-3x text-success mb-2"),
                                                html.H6("Simulador RLC", className="fw-bold mt-2"),
                                                html.P("Calculadora de impedancias teóricas para planificación experimental", className="small text-muted mb-0")
                                            ], className="col-md-6 text-center p-3 border rounded"),
                                        ], className="row g-3")
                                    ],
                                    "primary"
                                ),

                                # Advertencia
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            html.I(className="fas fa-exclamation-triangle fa-2x text-warning me-3"),
                                            html.Div([
                                                html.H6("⚠️ Calibración Requerida", className="mb-1"),
                                                html.P("Las mediciones no serán precisas hasta realizar la calibración con estándares certificados. Consulta la sección de Calibración.", className="mb-0 small")
                                            ])
                                        ], className="d-flex align-items-center")
                                    ], className="alert alert-warning border-0 shadow-sm")
                                ], className="col-12 mb-4"),

                            ], className="row")
                        ], className="", id="content-quickstart", style={"display": "block"}),

                        # ========== TAB 2: HARDWARE ==========
                        html.Div([
                            html.Div([
                                # Especificaciones
                                doc_card(
                                    "Especificaciones Técnicas - ADMX2001B",
                                    "microchip",
                                    [
                                        html.Div([
                                            html.Div([
                                                spec_badge("Rango de Frecuencia", "0.2 Hz - 10 MHz", "primary"),
                                                spec_badge("Resolución ADC", "18 bits", "success"),
                                                spec_badge("Alimentación", "3.3V única", "info"),
                                            ], className="col-md-4"),
                                            html.Div([
                                                spec_badge("Interfaces", "UART + SPI", "secondary"),
                                                spec_badge("Baud Rate", "115200", "dark"),
                                                spec_badge("Modos de Display", "18 formatos", "warning"),
                                            ], className="col-md-4"),
                                            html.Div([
                                                spec_badge("Tamaño", "1.5 × 2.5 in", "secondary"),
                                                spec_badge("Firmware", "v1.3.2", "success"),
                                                spec_badge("Rango Temp.", "-40°C a +85°C", "info"),
                                            ], className="col-md-4"),
                                        ], className="row")
                                    ]
                                ),

                                # Rangos de Impedancia
                                doc_card(
                                    "Rangos de Impedancia y Configuración de Ganancia",
                                    "sliders-h",
                                    [
                                        html.P("Configuración de ganancias para diferentes rangos de impedancia:", className="mb-3"),
                                        info_table(
                                            ["Ganancia Ch0", "Ganancia Ch1", "Rango de Impedancia"],
                                            [
                                                ["3", "0", "< 10Ω"],
                                                ["2", "0", "< 25Ω"],
                                                ["1", "0", "< 50Ω"],
                                                ["0", "0", "100Ω - 1kΩ"],
                                                ["0", "1", "1kΩ - 10kΩ"],
                                                ["0", "2", "10kΩ - 100kΩ"],
                                                ["0", "3", "> 100kΩ"],
                                            ]
                                        ),
                                        html.Div([
                                            html.I(className="fas fa-info-circle me-2"),
                                            html.Small("Usa auto-ranging para selección automática de ganancia óptima")
                                        ], className="alert alert-info border-0 mt-3")
                                    ]
                                ),

                                # Terminales
                                doc_card(
                                    "Terminales de Conexión (4-Wire Kelvin)",
                                    "sitemap",
                                    [
                                        html.P("Medición de 4 hilos (Kelvin) para eliminar resistencia de cables:", className="mb-3"),
                                        html.Div([
                                            html.Div([
                                                html.Div([
                                                    html.I(className="fas fa-circle text-danger me-2"),
                                                    html.Strong("H_CUR")
                                                ], className="d-flex align-items-center mb-2"),
                                                html.P("Terminal de fuente de señal (±5V @ 50mA)", className="text-muted small mb-0")
                                            ], className="col-md-6 mb-3 p-3 border rounded"),
                                            html.Div([
                                                html.Div([
                                                    html.I(className="fas fa-circle text-warning me-2"),
                                                    html.Strong("H_POT")
                                                ], className="d-flex align-items-center mb-2"),
                                                html.P("Sensado de voltaje alto (conectar con H_CUR en DUT)", className="text-muted small mb-0")
                                            ], className="col-md-6 mb-3 p-3 border rounded"),
                                            html.Div([
                                                html.Div([
                                                    html.I(className="fas fa-circle text-info me-2"),
                                                    html.Strong("L_POT")
                                                ], className="d-flex align-items-center mb-2"),
                                                html.P("Sensado de voltaje bajo (conectar con L_CUR en DUT)", className="text-muted small mb-0")
                                            ], className="col-md-6 mb-3 p-3 border rounded"),
                                            html.Div([
                                                html.Div([
                                                    html.I(className="fas fa-circle text-dark me-2"),
                                                    html.Strong("L_CUR")
                                                ], className="d-flex align-items-center mb-2"),
                                                html.P("Sensado de corriente / retorno de señal", className="text-muted small mb-0")
                                            ], className="col-md-6 mb-3 p-3 border rounded"),
                                        ], className="row")
                                    ]
                                ),

                            ], className="row")
                        ], className="", id="content-hardware", style={"display": "none"}),

                        # ========== TAB 3: SOFTWARE ==========
                        html.Div([
                            html.Div([
                                # Dashboard
                                doc_card(
                                    "Dashboard de Medición",
                                    "chart-line",
                                    [
                                        html.P("El dashboard principal realiza mediciones de impedancia con visualización científica en tiempo real:", className="mb-3"),
                                        
                                        html.H6("🔌 Panel de Conexión", className="mt-3 mb-2"),
                                        html.Ul([
                                            html.Li("Auto-detección del puerto serial FTDI/ADMX2001"),
                                            html.Li("Indicador visual del estado de conexión (verde=conectado, rojo=desconectado)"),
                                            html.Li("Botón de desconexión rápida")
                                        ]),
                                        
                                        html.H6("⚙️ Configuración de Barridos", className="mt-3 mb-2"),
                                        info_table(
                                            ["Parámetro", "Rango", "Unidad"],
                                            [
                                                ["Frecuencia Inicial/Final", "0.2 Hz - 10 MHz", "Hz"],
                                                ["Número de Puntos", "≥ 2 (sin límite)", "puntos"],
                                                ["Escala", "Lineal / Logarítmica", "-"],
                                                ["Magnitud", "0.001 - 10", "Vpk"],
                                            ]
                                        ),
                                        
                                        html.H6("📊 Visualizaciones Científicas", className="mt-3 mb-2"),
                                        html.Div([
                                            html.Div([
                                                html.I(className="fas fa-chart-area fa-2x text-primary mb-2"),
                                                html.Strong("Diagrama de Bode", className="d-block"),
                                                html.Small("Magnitud |Z| y fase θ vs frecuencia (escala log-log)", className="text-muted")
                                            ], className="col-md-6 text-center p-3 border rounded"),
                                            html.Div([
                                                html.I(className="fas fa-circle-notch fa-2x text-success mb-2"),
                                                html.Strong("Diagrama de Nyquist", className="d-block"),
                                                html.Small("Plano complejo Re[Z] vs Im[Z] con color por frecuencia", className="text-muted")
                                            ], className="col-md-6 text-center p-3 border rounded"),
                                        ], className="row g-3 mt-2"),
                                        
                                        html.Div([
                                            html.I(className="fas fa-info-circle me-2"),
                                            html.Small("Los gráficos Plotly son interactivos: zoom, pan, hover para análisis detallado")
                                        ], className="alert alert-info border-0 mt-3")
                                    ]
                                ),

                                # Modos de Display
                                doc_card(
                                    "Modos de Display del ADMX2001B",
                                    "list-alt",
                                    [
                                        html.P("El ADMX2001B soporta 18 modos de display diferentes en unidades SI:", className="mb-3"),
                                        html.Div([
                                            html.Div([
                                                html.Strong("Capacitivos (Serie/Paralelo):", className="text-primary d-block mb-2"),
                                                html.Ul([
                                                    html.Li("Cs-Rs, Cs-D, Cs-Q (Serie)"),
                                                    html.Li("Cp-Rp, Cp-D, Cp-Q (Paralelo)")
                                                ], className="small")
                                            ], className="col-md-6"),
                                            html.Div([
                                                html.Strong("Inductivos (Serie/Paralelo):", className="text-success d-block mb-2"),
                                                html.Ul([
                                                    html.Li("Ls-Rs, Ls-D, Ls-Q (Serie)"),
                                                    html.Li("Lp-Rp, Lp-D, Lp-Q (Paralelo)")
                                                ], className="small")
                                            ], className="col-md-6"),
                                        ], className="row mb-3"),
                                        html.Div([
                                            html.Div([
                                                html.Strong("Impedancia:", className="text-warning d-block mb-2"),
                                                html.Ul([
                                                    html.Li("R-X (Rectangular)"),
                                                    html.Li("Z-θ° (Polar grados)"),
                                                    html.Li("Z-θʳ (Polar radianes)")
                                                ], className="small")
                                            ], className="col-md-6"),
                                            html.Div([
                                                html.Strong("Admitancia:", className="text-info d-block mb-2"),
                                                html.Ul([
                                                    html.Li("G-B (Rectangular)"),
                                                    html.Li("Y-θ° (Polar grados)"),
                                                    html.Li("Y-θʳ (Polar radianes)")
                                                ], className="small")
                                            ], className="col-md-6"),
                                        ], className="row")
                                    ],
                                    "secondary"
                                ),

                                # Simulador
                                doc_card(
                                    "Simulador RLC",
                                    "calculator",
                                    [
                                        html.P("Calculadora de impedancia para planificación experimental:", className="mb-3"),
                                        html.Ul([
                                            html.Li("Soporta circuitos ideales y reales con parásitos"),
                                            html.Li("Componentes individuales: R, L, C"),
                                            html.Li("Configuraciones serie y paralelo"),
                                            html.Li("Salida: magnitud, fase, componentes real/imaginaria")
                                        ]),
                                        html.Div([
                                            html.I(className="fas fa-lightbulb me-2"),
                                            html.Small("Usa el simulador para predecir comportamiento antes de medir")
                                        ], className="alert alert-info border-0 mt-3")
                                    ],
                                    "success"
                                ),

                                # Persistencia
                                doc_card(
                                    "Persistencia de Datos",
                                    "database",
                                    [
                                        html.P("Los datos de barrido se guardan automáticamente:", className="mb-3"),
                                        html.Ul([
                                            html.Li("Almacenamiento en sesión del navegador (session storage)"),
                                            html.Li("Navegación entre páginas sin pérdida de datos"),
                                            html.Li("Gráficos restaurados al regresar al Dashboard"),
                                            html.Li("Exportación a CSV disponible")
                                        ])
                                    ],
                                    "info"
                                ),

                            ], className="row")
                        ], className="", id="content-software", style={"display": "none"}),

                        # ========== TAB 4: CALIBRACIÓN ==========
                        html.Div([
                            html.Div([
                                # Importancia
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            html.I(className="fas fa-exclamation-circle fa-2x text-danger me-3"),
                                            html.Div([
                                                html.H5("⚠️ Calibración Obligatoria", className="mb-1"),
                                                html.P("Las mediciones NO serán precisas hasta completar la calibración con estándares certificados. Los tres pasos (open, short, load) deben realizarse en orden estricto.", className="mb-0")
                                            ])
                                        ], className="d-flex align-items-center")
                                    ], className="alert alert-danger border-0 shadow-sm")
                                ], className="col-12 mb-4"),

                                # Pasos
                                doc_card(
                                    "1️⃣ Open Calibration",
                                    "circle",
                                    [
                                        html.P("Corrige parásitas del módulo y cables cuando no hay carga conectada.", className="mb-3"),
                                        html.Strong("Configuración:"),
                                        html.Ul([
                                            html.Li("Conecta H_POT con H_CUR (cortocircuito)"),
                                            html.Li("Conecta L_POT con L_CUR (cortocircuito)"),
                                            html.Li("Deja H y L desconectadas entre sí (circuito abierto)"),
                                        ]),
                                        command_card("calibrate open", "Ejecutar calibración open")
                                    ],
                                    "primary"
                                ),

                                doc_card(
                                    "2️⃣ Short Calibration",
                                    "compress-arrows-alt",
                                    [
                                        html.P("Corrige impedancias parásitas cuando todas las terminales están cortocircuitadas.", className="mb-3"),
                                        html.Strong("Configuración:"),
                                        html.Ul([
                                            html.Li("Conecta todas las terminales juntas (H_POT, H_CUR, L_POT, L_CUR)"),
                                            html.Li("Solo cuando ganancia canal 1 es 0 o 1"),
                                            html.Li("Reduce la magnitud a 0.2V"),
                                        ]),
                                        command_card("calibrate short", "Ejecutar calibración short")
                                    ],
                                    "warning"
                                ),

                                doc_card(
                                    "3️⃣ Load Calibration",
                                    "weight-hanging",
                                    [
                                        html.P("Proporciona trazabilidad a fuente externa certificada (resistor de precisión típicamente).", className="mb-3"),
                                        html.Strong("Configuración:"),
                                        html.Ul([
                                            html.Li("Conecta impedancia conocida entre terminales"),
                                            html.Li("Valor cercano a la impedancia del DUT a medir"),
                                        ]),
                                        command_card("calibrate rt 1000 xt 0", "Ejemplo: resistor de 1kΩ (valores en Ohms)")
                                    ],
                                    "success"
                                ),

                                # Guardar
                                doc_card(
                                    "Guardar Calibración",
                                    "save",
                                    [
                                        html.P("Después de completar los 3 pasos, guarda los coeficientes:", className="mb-3"),
                                        command_card("calibrate commit 20251106", "Guardar en memoria no volátil"),
                                        html.P([
                                            "Contraseña por defecto: ",
                                            html.Code("Analog123", className="text-info bg-dark p-1 rounded")
                                        ], className="mt-2"),
                                        html.Div([
                                            html.I(className="fas fa-info-circle me-2"),
                                            html.Small("Soporta hasta 25 calibraciones (EEPROM) o 450 (Flash) en múltiples frecuencias")
                                        ], className="alert alert-info border-0 mt-3")
                                    ],
                                    "info"
                                ),

                            ], className="row")
                        ], className="", id="content-calibration", style={"display": "none"}),

                        # ========== TAB 5: CLI ==========
                        html.Div([
                            html.Div([
                                html.H2([
                                    html.I(className="fas fa-terminal me-2"),
                                    "Interfaz de Línea de Comandos (CLI)"
                                ], className="mb-4"),

                                # Tabla de modos
                                doc_card(
                                    "Tabla de Modos de Display (display <0-17>)",
                                    "table",
                                    [
                                        html.P("El ADMX2001B soporta 18 formatos de salida. Selecciona con comando 'display':", className="mb-3"),
                                        info_table(
                                            ["Modo", "Formato", "Descripción"],
                                            [
                                                ["0", "Cs-Rs", "Capacitancia serie + Resistencia serie"],
                                                ["1", "Cs-D", "Capacitancia serie + Factor de disipación"],
                                                ["2", "Cs-Q", "Capacitancia serie + Factor de calidad"],
                                                ["3", "Cp-Rp", "Capacitancia paralelo + Resistencia paralelo"],
                                                ["4", "Cp-D", "Capacitancia paralelo + Factor de disipación"],
                                                ["5", "Cp-Q", "Capacitancia paralelo + Factor de calidad"],
                                                ["6", "R-X", "Resistencia + Reactancia (rectangular)"],
                                                ["7", "Z-θ°", "Magnitud impedancia + Fase en grados (polar)"],
                                                ["8", "Z-θʳ", "Magnitud impedancia + Fase en radianes (polar)"],
                                                ["9", "Ls-Rs", "Inductancia serie + Resistencia serie"],
                                                ["10", "Ls-D", "Inductancia serie + Factor de disipación"],
                                                ["11", "Ls-Q", "Inductancia serie + Factor de calidad"],
                                                ["12", "Lp-Rp", "Inductancia paralelo + Resistencia paralelo"],
                                                ["13", "Lp-D", "Inductancia paralelo + Factor de disipación"],
                                                ["14", "Lp-Q", "Inductancia paralelo + Factor de calidad"],
                                                ["15", "G-B", "Conductancia + Susceptancia (rectangular)"],
                                                ["16", "Y-θ°", "Magnitud admitancia + Fase en grados (polar)"],
                                                ["17", "Y-θʳ", "Magnitud admitancia + Fase en radianes (polar)"],
                                            ]
                                        ),
                                        html.Div([
                                            html.Strong("Ejemplo: "),
                                            html.Code("display 6", className="bg-light px-2 py-1 rounded ms-2"),
                                            html.Span(" selecciona modo R-X (resistencia-reactancia)", className="ms-2")
                                        ], className="alert alert-secondary border-0 mt-3")
                                    ],
                                    "primary"
                                ),

                                # Medición
                                doc_card(
                                    "Comandos de Medición Básica",
                                    "crosshairs",
                                    [
                                        command_card("z", "Realizar medición de impedancia (retorna 2 valores según modo activo)"),
                                        command_card("frequency 1000", "Configurar frecuencia de excitación (Hz) - Rango: 0.2Hz a 10MHz"),
                                        command_card("magnitude 1.0", "Amplitud pico de señal (V) - Rango: 0.001V a 10V"),
                                        command_card("average 200", "Número de muestras para promedio (1-256) - Mayor = más preciso pero más lento"),
                                        html.Div([
                                            html.Strong("Ejemplo de sesión:"),
                                            html.Pre([
                                                "> frequency 1000\n",
                                                "> magnitude 0.5\n",
                                                "> display 6\n",
                                                "> z\n",
                                                "147.23 -52.18  # R=147.23Ω, X=-52.18Ω"
                                            ], className="bg-dark text-light p-3 rounded mt-2 small")
                                        ], className="border rounded p-3 mt-3")
                                    ]
                                ),

                                # Barrido
                                doc_card(
                                    "Comandos de Barrido Paramétrico",
                                    "chart-line",
                                    [
                                        html.H6("🔹 Barrido de Frecuencia", className="mb-2"),
                                        command_card("sweep_type frequency 100 10000", "Barrido entre 100Hz y 10kHz"),
                                        command_card("sweep_scale log", "Escala logarítmica (o 'linear')"),
                                        command_card("count 50", "Número de puntos de medición en el barrido"),
                                        
                                        html.Hr(className="my-3"),
                                        
                                        html.H6("🔹 Barrido de Bias DC", className="mb-2"),
                                        command_card("sweep_type bias -2 2", "Barrido de bias de -2V a +2V (útil para caracterización de diodos/transistores)"),
                                        
                                        html.Hr(className="my-3"),
                                        
                                        html.H6("🔹 Barrido de Magnitud", className="mb-2"),
                                        command_card("sweep_type magnitude 0.1 5", "Barrido de amplitud de 0.1V a 5V (útil para detección de no-linealidades)"),
                                        
                                        html.Div([
                                            html.I(className="fas fa-info-circle me-2"),
                                            html.Small("Los barridos devuelven múltiples mediciones automáticamente. Usa 'mdelay' para ajustar velocidad vs estabilidad.")
                                        ], className="alert alert-info border-0 mt-3")
                                    ],
                                    "warning"
                                ),

                                # Ganancia y Timing
                                doc_card(
                                    "Configuración Avanzada: Ganancia y Timing",
                                    "sliders-h",
                                    [
                                        html.H6("⚙️ Control de Ganancia", className="mb-2"),
                                        html.P("Las ganancias determinan el rango de medición:", className="small text-muted mb-2"),
                                        command_card("setgain ch0 <0-3>", "Ganancia canal 0 (voltaje) - Afecta rango de impedancia medible"),
                                        command_card("setgain ch1 <0-3>", "Ganancia canal 1 (corriente) - Valores más altos para impedancias más altas"),
                                        command_card("setgain auto", "Modo auto-ranging activado (recomendado para uso general)"),
                                        
                                        html.Hr(className="my-3"),
                                        
                                        html.H6("⏱️ Optimización de Timing", className="mb-2"),
                                        html.P("Ajusta retardos para equilibrar velocidad y precisión:", className="small text-muted mb-2"),
                                        command_card("mdelay <ms>", "Retardo entre mediciones (ms) - Aumenta para mayor estabilidad"),
                                        command_card("tdelay <ms>", "Retardo de asentamiento transitorio (ms) - Crítico para frecuencias bajas"),
                                        
                                        html.Div([
                                            html.Strong("Guía de timing:"),
                                            html.Ul([
                                                html.Li("f > 1kHz: mdelay=50-100ms, tdelay=10-20ms (mediciones rápidas)"),
                                                html.Li("f = 100Hz-1kHz: mdelay=100-200ms, tdelay=50-100ms (balance)"),
                                                html.Li("f < 100Hz: mdelay=200-500ms, tdelay=200-500ms (máxima precisión)"),
                                            ], className="small mb-0")
                                        ], className="alert alert-secondary border-0 mt-3")
                                    ],
                                    "info"
                                ),

                                # Sistema
                                doc_card(
                                    "Comandos de Sistema y Diagnóstico",
                                    "wrench",
                                    [
                                        command_card("*idn", "Identificación del dispositivo (fabricante, modelo, serial, versión firmware)"),
                                        command_card("help", "Lista todos los comandos disponibles en el firmware"),
                                        command_card("help <comando>", "Ayuda detallada sobre comando específico (ej: help frequency)"),
                                        command_card("selftest", "Ver resultado del último self-test automático"),
                                        command_card("reset", "Reiniciar el sistema (vuelve a configuración por defecto)"),
                                        html.Div([
                                            html.I(className="fas fa-lightbulb me-2"),
                                            html.Small("Ejecuta 'selftest' después de encender para verificar que hardware está OK")
                                        ], className="alert alert-success border-0 mt-3")
                                    ]
                                ),

                            ], className="row")
                        ], className="", id="content-cli", style={"display": "none"}),

                        # ========== TAB 6: SOPORTE ==========
                        html.Div([
                            html.Div([
                                # Contacto
                                doc_card(
                                    "Contacto de Soporte",
                                    "envelope",
                                    [
                                        html.P("Para soporte técnico, preguntas o actualizaciones de firmware:", className="mb-3"),
                                        html.A([
                                            html.I(className="fas fa-envelope me-2"),
                                            "admx-support@analog.com"
                                        ], href="mailto:admx-support@analog.com", className="btn btn-primary btn-lg")
                                    ],
                                    "primary"
                                ),

                                # Recursos
                                doc_card(
                                    "Recursos Externos",
                                    "link",
                                    [
                                        html.Div([
                                            html.I(className="fas fa-download me-2"),
                                            html.A("Drivers FTDI VCP", href="https://www.ftdichip.com/Drivers/VCP.htm", target="_blank")
                                        ], className="mb-2"),
                                        html.Div([
                                            html.I(className="fas fa-terminal me-2"),
                                            html.A("TeraTerm (Emulador)", href="https://github.com/TeraTermProject/teraterm/releases", target="_blank")
                                        ], className="mb-2"),
                                        html.Div([
                                            html.I(className="fab fa-github me-2"),
                                            html.A("Repositorio GitHub - ZORIA", href="https://github.com/mario1027/libeval", target="_blank")
                                        ]),
                                    ],
                                    "info"
                                ),

                                # Firmware
                                doc_card(
                                    "Versiones de Firmware",
                                    "microchip",
                                    [
                                        info_table(
                                            ["Versión", "Estado", "Características"],
                                            [
                                                ["1.3.2", "✅ Estable", "Optimizaciones de tiempo"],
                                                ["1.3.1", "✅ Estable", "Mejoras de ruido"],
                                                ["1.2.4", "✅ Estable", "Script de instalación"],
                                                ["1.2.2", "✅ Estable", "Calibración multi-frecuencia"],
                                            ]
                                        )
                                    ],
                                    "success"
                                ),

                                # Sobre ZORIA
                                doc_card(
                                    "Sobre ZORIA",
                                    "code",
                                    [
                                        html.P([
                                            "ZORIA es un software ",
                                            html.Strong("open-source (MIT License)"),
                                            " que moderniza el analizador EVAL-ADMX2001 con una interfaz web intuitiva."
                                        ], className="mb-3"),
                                        html.P([
                                            html.Strong("Desarrollado por: "),
                                            "Mario Ricardo Montero, Juan Carlos Alvarez, Francisco J. Racedo N."
                                        ]),
                                        html.Hr(),
                                        html.Div([
                                            html.I(className="fas fa-book me-2"),
                                            "Documentación completa del hardware disponible en ",
                                            html.Code("DOCUMENTACION_OFICIAL.md")
                                        ], className="text-muted small")
                                    ],
                                    "secondary"
                                ),

                            ], className="row")
                        ], className="", id="content-support", style={"display": "none"}),

                    ], className=""),

                ], className="container-fluid py-4")
            ], className="main-content w-100")
        ], className="d-flex flex-grow-1"),

        # Footer
        footer()
    ], className="d-flex flex-column min-vh-100")


# ==================== CALLBACKS ====================

@callback(
    [Output('btn-quickstart', 'className'),
     Output('btn-hardware', 'className'),
     Output('btn-software', 'className'),
     Output('btn-calibration', 'className'),
     Output('btn-cli', 'className'),
     Output('btn-support', 'className'),
     Output('content-quickstart', 'style'),
     Output('content-hardware', 'style'),
     Output('content-software', 'style'),
     Output('content-calibration', 'style'),
     Output('content-cli', 'style'),
     Output('content-support', 'style')],
    [Input('btn-quickstart', 'n_clicks'),
     Input('btn-hardware', 'n_clicks'),
     Input('btn-software', 'n_clicks'),
     Input('btn-calibration', 'n_clicks'),
     Input('btn-cli', 'n_clicks'),
     Input('btn-support', 'n_clicks')]
)
def update_tab(n1, n2, n3, n4, n5, n6):
    """Controla qué pestaña está activa y visible"""
    from dash import ctx
    
    # Determinar qué botón se presionó
    button_id = ctx.triggered_id if ctx.triggered_id else 'btn-quickstart'
    
    # Clases base para botones
    base_class = "btn btn-outline-primary me-2 mb-2"
    active_class = "btn btn-primary me-2 mb-2"
    
    # Estilos para contenido
    hidden = {"display": "none"}
    visible = {"display": "block"}
    
    # Mapeo de estados
    tabs = {
        'btn-quickstart': 0,
        'btn-hardware': 1,
        'btn-software': 2,
        'btn-calibration': 3,
        'btn-cli': 4,
        'btn-support': 5
    }
    
    active_tab = tabs.get(button_id, 0)
    
    # Crear listas de salida
    button_classes = [base_class] * 6
    button_classes[active_tab] = active_class
    
    content_styles = [hidden] * 6
    content_styles[active_tab] = visible
    
    return button_classes + content_styles
