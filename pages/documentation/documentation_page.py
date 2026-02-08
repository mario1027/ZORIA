"""
Página de Documentación Oficial del Software ZORIA
Sistema completo de documentación para el analizador de impedancia EVAL-ADMX2001
Con imágenes de la wiki oficial de Analog Devices
"""
from dash import html, dcc, Input, Output, callback
from dash_spa import register_page

# Importar componentes comunes compartidos
from pages.common.sidebar import sideBar
from pages.common.mobile_nav import mobileNavBar
from pages.common.footer import footer
from pages.common.terminal_component import global_terminal_component
from pages.common.floating_terminal_button import floating_terminal_button

# Registrar la página
register_page(
    __name__,
    path='/documentacion',
    title='Documentación - ZORIA',
    name='Documentación Oficial'
)


# ==================== URLs DE IMÁGENES DE LA WIKI DE ANALOG ====================
IMAGES = {
    'basic_connections': '/assets/images/documentation/basic_connections.png',
    'open_load': '/assets/images/documentation/open_load.png',
    'bnc_load': '/assets/images/documentation/bnc_load.png',
    'photo_setup': '/assets/images/documentation/photo_setup.jpg',
    'cal_connections': '/assets/images/documentation/cal_connections.jpg',
    'open_config_clips': '/assets/images/documentation/open_config_clips.png',
    'uart_connection': '/assets/images/documentation/uart_connection.jpg',
    'dev_mgr_vcp': '/assets/images/documentation/dev_mgr_vcp.png',
}



# ==================== COMPONENTES DE DOCUMENTACIÓN ====================

def doc_section(title, icon, content, id=None):
    """Sección de documentación con estilo mejorado"""
    # Asegurar que content sea una lista
    if not isinstance(content, list):
        content = [content]
    return html.Div([
        html.Div([
            html.Div([
                html.I(className=f"fas fa-{icon} me-3"),
                html.H4(title, className="mb-0 d-inline-block")
            ], className="section-header mb-4 pb-3 border-bottom border-2 border-primary"),
            html.Div(content, className="section-content")
        ], className="doc-section mb-5", id=id)
    ])


def image_card(src, alt, caption=None, max_width="100%"):
    """Tarjeta de imagen con caption opcional"""
    children = [
        html.Div([
            html.Img(src=src, alt=alt, className="img-fluid rounded shadow-sm", 
                    style={"maxWidth": max_width, "width": "100%"}),
        ], className="image-container bg-light p-3 rounded border text-center")
    ]
    if caption:
        children.append(html.P(caption, className="text-muted small mt-2 mb-0 text-center fst-italic"))
    return html.Div(children, className="image-card mb-4")


def step_card(number, title, content, image_src=None, image_caption=None, color="primary"):
    """Tarjeta de paso numerado con imagen opcional"""
    # Asegurar que content sea una lista
    if not isinstance(content, list):
        content = [content]
    card_children = [
        # Número y título
        html.Div([
            html.Span(str(number), className=f"step-number badge bg-{color} rounded-circle me-3 fs-5"),
            html.H5(title, className="mb-0 d-inline-block fw-bold")
        ], className="step-header mb-3 d-flex align-items-center"),
        # Contenido
        html.Div(content, className="step-content ps-5")
    ]
    # Imagen opcional
    if image_src:
        card_children.append(
            html.Div([image_card(image_src, title, image_caption)], className="step-image mt-3 ps-5")
        )
    return html.Div([
        html.Div(card_children, className=f"step-card p-4 border-start border-4 border-{color} bg-white rounded shadow-sm mb-4")
    ])


def info_box(content, type="info"):
    """Caja de información con icono"""
    icons = {
        "info": "info-circle",
        "warning": "exclamation-triangle",
        "danger": "exclamation-circle",
        "success": "check-circle",
        "tip": "lightbulb"
    }
    colors = {
        "info": "primary",
        "warning": "warning",
        "danger": "danger", 
        "success": "success",
        "tip": "info"
    }
    # Asegurar que content sea una lista
    if not isinstance(content, list):
        content = [content]
    return html.Div([
        html.Div(
            [html.I(className=f"fas fa-{icons.get(type, 'info-circle')} me-2")] + content,
            className=f"alert alert-{colors.get(type, 'info')} border-0 d-flex align-items-start"
        )
    ], className="mb-4")


def spec_badge(label, value, color="secondary"):
    """Badge con especificación técnica"""
    return html.Div([
        html.Span(label, className="text-muted small d-block mb-1"),
        html.Span(value, className=f"badge bg-{color} px-3 py-2 fs-6")
    ], className="mb-3")


def command_card(command, description):
    """Card para comando CLI"""
    return html.Div([
        html.Code(command, className="bg-dark text-success p-2 rounded d-block mb-2 font-monospace"),
        html.P(description, className="text-muted small mb-0")
    ], className="mb-3")


def info_table(headers, rows):
    """Tabla de información con estilo Volt"""
    return html.Div([
        html.Table([
            html.Thead([
                html.Tr([html.Th(h, className="border-bottom bg-light") for h in headers])
            ]),
            html.Tbody([
                html.Tr([html.Td(cell, className="border-bottom") for cell in row])
                for row in rows
            ])
        ], className="table table-hover table-striped")
    ], className="table-responsive")


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
                    # Header mejorado
                    html.Div([
                        html.Div([
                            html.H2([
                                html.I(className="fas fa-book-open me-3 text-primary"),
                                "Documentación Oficial"
                            ], className="h2 mb-2 fw-bold"),
                            html.P([
                                "Guía completa del software ",
                                html.Strong("ZORIA"),
                                " y el analizador de impedancia ",
                                html.Strong("EVAL-ADMX2001")
                            ], className="text-muted mb-0 fs-5")
                        ], className="col-12 col-md-8 mb-2 mb-md-0"),
                        html.Div([
                            html.A([
                                html.I(className="fas fa-external-link-alt me-2"),
                                "Wiki Analog"
                            ], href="https://wiki.analog.com/resources/eval/user-guides/admx/eval-admx2001ebz", 
                               target="_blank", className="btn btn-outline-primary me-2"),
                            html.Span([
                                html.I(className="fas fa-code-branch me-2"),
                                "v1.3.2"
                            ], className="badge bg-success px-3 py-2 fs-6")
                        ], className="col-12 col-md-4 d-flex justify-content-md-end align-items-center flex-wrap gap-2")
                    ], className="row align-items-center py-4 mb-4 bg-light p-4 rounded shadow-sm"),

                    # Store para la pestaña activa
                    dcc.Store(id='doc-active-tab', data='quickstart', storage_type='session'),
                    
                    # Navegación por pestañas - Estilo mejorado tipo pills
                    html.Div([
                        html.Div([
                            html.Button([
                                html.I(className="fas fa-rocket me-2"),
                                "Inicio Rápido"
                            ], id="btn-quickstart", className="btn btn-primary active me-2 mb-2 fw-bold"),
                            html.Button([
                                html.I(className="fas fa-microchip me-2"),
                                "Hardware"
                            ], id="btn-hardware", className="btn btn-outline-primary me-2 mb-2 fw-bold"),
                            html.Button([
                                html.I(className="fas fa-laptop-code me-2"),
                                "Software"
                            ], id="btn-software", className="btn btn-outline-primary me-2 mb-2 fw-bold"),
                            html.Button([
                                html.I(className="fas fa-balance-scale me-2"),
                                "Calibración"
                            ], id="btn-calibration", className="btn btn-outline-primary me-2 mb-2 fw-bold"),
                            html.Button([
                                html.I(className="fas fa-terminal me-2"),
                                "CLI"
                            ], id="btn-cli", className="btn btn-outline-primary me-2 mb-2 fw-bold"),
                            html.Button([
                                html.I(className="fas fa-question-circle me-2"),
                                "Soporte"
                            ], id="btn-support", className="btn btn-outline-primary me-2 mb-2 fw-bold"),
                        ], className="nav-pills-container p-3 bg-white rounded shadow-sm border")
                    ], className="mb-4"),

                    # Contenido de las pestañas
                    html.Div([
                        
                        # ========== TAB 1: INICIO RÁPIDO ==========
                        html.Div([
                            # Intro
                            html.Div([
                                html.P([
                                    "Esta guía te ayudará a configurar y comenzar a usar tu ",
                                    html.Strong("EVAL-ADMX2001"),
                                    " en cinco simples pasos. Sigue cada paso cuidadosamente para garantizar mediciones precisas."
                                ], className="lead mb-4")
                            ]),
                            
                            # Paso 1: Drivers
                            step_card(
                                1,
                                "Instalación de Drivers",
                                [
                                    html.P([
                                        "Descarga e instala los drivers ",
                                        html.Strong("Virtual COM Port (VCP)"),
                                        " de FTDI para habilitar la comunicación UART con el dispositivo."
                                    ]),
                                    html.A([
                                        html.I(className="fas fa-download me-2"),
                                        "Descargar Drivers FTDI"
                                    ], href="https://www.ftdichip.com/Drivers/VCP.htm", target="_blank",
                                       className="btn btn-primary mb-3"),
                                    info_box([
                                        "Después de instalar, conecta el cable USB-UART y verifica en el ",
                                        html.Strong("Administrador de Dispositivos"),
                                        " que aparezca un puerto COM asignado."
                                    ], "tip"),
                                ],
                                image_src=IMAGES.get('dev_mgr_vcp'),
                                image_caption="Administrador de dispositivos mostrando el puerto COM instalado",
                                color="primary"
                            ),

                            # Paso 2: Hardware
                            step_card(
                                2,
                                "Conexión del Hardware",
                                [
                                    html.P("Sigue estos pasos para configurar correctamente el hardware:"),
                                    html.Ol([
                                        html.Li([
                                            "Inserta el módulo ",
                                            html.Strong("ADMX2001B"),
                                            " en la placa ",
                                            html.Strong("EVAL-ADMX2001EBZ"),
                                            " (los conectores están codificados)"
                                        ]),
                                        html.Li([
                                            "Configura los interruptores de selección de carga a ",
                                            html.Strong("OPEN"),
                                            " y ",
                                            html.Strong("GND")
                                        ]),
                                        html.Li("Conecta el adaptador de corriente al jack de alimentación (9VDC)"),
                                        html.Li([
                                            "Verifica que el LED de self-test esté ",
                                            html.Span("verde", className="text-success fw-bold"),
                                            " (visible desde el lado inferior)"
                                        ]),
                                    ]),
                                    info_box([
                                        html.Strong("Importante: "),
                                        "El LED de self-test debe estar verde antes de continuar. Si está rojo o naranja, revisa las conexiones."
                                    ], "warning"),
                                ],
                                image_src=IMAGES.get('basic_connections'),
                                image_caption="Diagrama de conexiones básicas del EVAL-ADMX2001EBZ",
                                color="success"
                            ),

                            # Paso 3: Configuración UART
                            step_card(
                                3,
                                "Configuración UART",
                                [
                                    html.P("Conecta el cable UART a USB siguiendo el esquema de colores:"),
                                    html.Div([
                                        html.Div([
                                            html.Span("• TX (naranja) → TX", className="text-warning fw-bold d-block"),
                                            html.Span("• RX (amarillo) → RX", className="text-warning fw-bold d-block"),
                                            html.Span("• GND (negro) → GND", className="text-dark fw-bold d-block"),
                                        ], className="bg-light p-3 rounded border mb-3 font-monospace")
                                    ]),
                                    html.P([
                                        "Asegura que el jumper ",
                                        html.Strong("CLK_SEL"),
                                        " esté en posición ",
                                        html.Strong("INT"),
                                        " (reloj interno)"
                                    ]),
                                ],
                                image_src=IMAGES.get('uart_connection'),
                                image_caption="Conexión del cable UART a los terminales",
                                color="info"
                            ),

                            # Paso 4: Configuración DUT
                            step_card(
                                4,
                                "Configuración para Medición",
                                [
                                    html.P("Para realizar mediciones en un dispositivo bajo prueba (DUT):"),
                                    html.Ol([
                                        html.Li([
                                            "Cambia los interruptores a posición ",
                                            html.Strong("DUT"),
                                            " y ",
                                            html.Strong("GND")
                                        ]),
                                        html.Li([
                                            "Conecta los cables de prueba BNC:"
                                        ]),
                                        html.Ul([
                                            html.Li([html.Span("Rojos", className="text-danger fw-bold"), " → HCUR/HPOT"]),
                                            html.Li([html.Span("Negros", className="text-dark fw-bold"), " → LPOT/LCUR"]),
                                        ]),
                                    ]),
                                    info_box([
                                        "Inspecciona los conectores BNC. El housing puede desenroscarse parcialmente, ",
                                        "impidiendo buen contacto. Asegúrate de que ambos lados del clip estén conectados eléctricamente."
                                    ], "warning"),
                                ],
                                image_src=IMAGES.get('photo_setup'),
                                image_caption="Configuración completa lista para medición",
                                color="warning"
                            ),

                            # Paso 5: Software
                            step_card(
                                5,
                                "Uso del Software ZORIA",
                                [
                                    html.P([
                                        "ZORIA proporciona una interfaz web moderna que elimina la necesidad de ",
                                        "terminales CLI tradicionales:"
                                    ]),
                                    html.Div([
                                        html.Div([
                                            html.Div([
                                                html.I(className="fas fa-chart-pie fa-3x text-primary mb-3"),
                                                html.H5("Dashboard", className="fw-bold"),
                                                html.P("Barridos de frecuencia con diagramas de Bode y Nyquist en tiempo real", 
                                                      className="small text-muted")
                                            ], className="text-center p-4 border rounded bg-white shadow-sm h-100"),
                                        ], className="col-md-6 mb-3"),
                                        html.Div([
                                            html.Div([
                                                html.I(className="fas fa-calculator fa-3x text-success mb-3"),
                                                html.H5("Simulador RLC", className="fw-bold"),
                                                html.P("Calculadora de impedancias teóricas para planificación experimental", 
                                                      className="small text-muted")
                                            ], className="text-center p-4 border rounded bg-white shadow-sm h-100"),
                                        ], className="col-md-6 mb-3"),
                                    ], className="row mt-3"),
                                ],
                                color="primary"
                            ),

                            # Advertencia final
                            html.Div([
                                html.Div([
                                    html.Div([
                                        html.I(className="fas fa-exclamation-triangle fa-2x text-warning me-3"),
                                        html.Div([
                                            html.H5("⚠️ Calibración Requerida", className="mb-1 fw-bold"),
                                            html.P([
                                                "Las mediciones no serán precisas hasta realizar la calibración ",
                                                html.Strong("OPEN-SHORT-LOAD"),
                                                " con estándares certificados. Consulta la sección de Calibración."
                                            ], className="mb-0")
                                        ])
                                    ], className="d-flex align-items-center")
                                ], className="alert alert-warning border-0 shadow-sm py-4")
                            ], className="col-12 mb-4 mt-4"),

                        ], className="", id="content-quickstart", style={"display": "block"}),

                        # ========== TAB 2: HARDWARE ==========
                        html.Div([
                            # Especificaciones en grid
                            html.Div([
                                html.H4([
                                    html.I(className="fas fa-microchip me-2 text-primary"),
                                    "Especificaciones Técnicas"
                                ], className="mb-4 pb-3 border-bottom border-2 border-primary"),
                                
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            html.H5("ADMX2001B", className="card-title text-primary fw-bold"),
                                            html.Hr(),
                                            html.Div([
                                                spec_badge("Rango de Frecuencia", "0.2 Hz - 10 MHz", "primary"),
                                                spec_badge("Resolución ADC", "18 bits", "success"),
                                                spec_badge("Alimentación", "3.3V única", "info"),
                                                spec_badge("Interfaces", "UART + SPI", "secondary"),
                                                spec_badge("Baud Rate", "115200", "dark"),
                                                spec_badge("Modos de Display", "18 formatos", "warning"),
                                                spec_badge("Tamaño", "1.5 × 2.5 in", "secondary"),
                                                spec_badge("Rango Temp.", "-40°C a +85°C", "info"),
                                            ])
                                        ], className="card-body")
                                    ], className="card border-0 shadow-sm h-100")
                                ], className="col-md-6 mb-4"),
                                
                                html.Div([
                                    html.Div([
                                        html.H5("EVAL-ADMX2001EBZ", className="card-title text-success fw-bold"),
                                        html.Hr(),
                                        html.Ul([
                                            html.Li("Conectores BNC para sondas LCR estándar"),
                                            html.Li("Interfaz UART con cable USB incluido"),
                                            html.Li("Señales de trigger y clock vía SMA"),
                                            html.Li("Headers estilo Arduino para desarrollo"),
                                            html.Li("Entrada de alimentación +5V a +12V"),
                                            html.Li("LED indicador de self-test"),
                                        ], className="list-unstyled"),
                                        info_box([
                                            "Incluye: placa evaluación, cable UART-USB, adaptador 9VDC, clips de prueba LCR"
                                        ], "success")
                                    ], className="card border-0 shadow-sm h-100 p-4")
                                ], className="col-md-6 mb-4"),
                            ], className="row"),

                            # Rangos de Impedancia
                            html.Div([
                                html.H4([
                                    html.I(className="fas fa-sliders-h me-2 text-primary"),
                                    "Rangos de Impedancia y Configuración de Ganancia"
                                ], className="mb-4 pb-3 border-bottom border-2 border-primary"),
                                
                                html.P("Configuración de ganancias para diferentes rangos de impedancia:", className="mb-3"),
                                info_table(
                                    ["Ganancia Ch0", "Ganancia Ch1", "Rango de Impedancia", "Aplicación Típica"],
                                    [
                                        ["3", "0", "< 10Ω", "Resistencias muy bajas"],
                                        ["2", "0", "< 25Ω", "Resistencias bajas"],
                                        ["1", "0", "< 50Ω", "Resistencias medias"],
                                        ["0", "0", "100Ω - 1kΩ", "Uso general"],
                                        ["0", "1", "1kΩ - 10kΩ", "Resistencias altas"],
                                        ["0", "2", "10kΩ - 100kΩ", "Impedancias muy altas"],
                                        ["0", "3", "> 100kΩ", "Alta impedancia"],
                                    ]
                                ),
                                info_box([
                                    html.Strong("Recomendación: "),
                                    "Usa auto-ranging (",
                                    html.Code("setgain auto"),
                                    ") para selección automática de ganancia óptima en la mayoría de casos."
                                ], "tip"),
                            ], className="mb-5"),

                            # Terminales
                            html.Div([
                                html.H4([
                                    html.I(className="fas fa-sitemap me-2 text-primary"),
                                    "Terminales de Conexión (4-Wire Kelvin)"
                                ], className="mb-4 pb-3 border-bottom border-2 border-primary"),
                                
                                html.P([
                                    "La medición de ",
                                    html.Strong("4 hilos (Kelvin)"),
                                    " elimina la resistencia de los cables para mediciones precisas:"
                                ], className="mb-4"),
                                
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            html.Div([
                                                html.I(className="fas fa-circle text-danger me-2"),
                                                html.Strong("H_CUR (High Current)")
                                            ], className="d-flex align-items-center mb-2"),
                                            html.P("Terminal de fuente de señal (±5V @ 50mA)", className="text-muted small mb-0")
                                        ], className="p-3 border rounded bg-white"),
                                    ], className="col-md-6 mb-3"),
                                    html.Div([
                                        html.Div([
                                            html.Div([
                                                html.I(className="fas fa-circle text-warning me-2"),
                                                html.Strong("H_POT (High Potential)")
                                            ], className="d-flex align-items-center mb-2"),
                                            html.P("Sensado de voltaje alto - conectar con H_CUR en DUT", className="text-muted small mb-0")
                                        ], className="p-3 border rounded bg-white"),
                                    ], className="col-md-6 mb-3"),
                                    html.Div([
                                        html.Div([
                                            html.Div([
                                                html.I(className="fas fa-circle text-info me-2"),
                                                html.Strong("L_POT (Low Potential)")
                                            ], className="d-flex align-items-center mb-2"),
                                            html.P("Sensado de voltaje bajo - conectar con L_CUR en DUT", className="text-muted small mb-0")
                                        ], className="p-3 border rounded bg-white"),
                                    ], className="col-md-6 mb-3"),
                                    html.Div([
                                        html.Div([
                                            html.Div([
                                                html.I(className="fas fa-circle text-dark me-2"),
                                                html.Strong("L_CUR (Low Current)")
                                            ], className="d-flex align-items-center mb-2"),
                                            html.P("Sensado de corriente / retorno de señal", className="text-muted small mb-0")
                                        ], className="p-3 border rounded bg-white"),
                                    ], className="col-md-6 mb-3"),
                                ], className="row"),
                                
                                info_box([
                                    html.Strong("Configuración típica: "),
                                    "Conecta los BNC rojos (H) a un lado del DUT y los negros (L) al otro lado. "
                                ], "info"),
                            ], className="mb-5"),

                        ], className="", id="content-hardware", style={"display": "none"}),

                        # ========== TAB 3: SOFTWARE ==========
                        html.Div([
                            # Dashboard
                            html.Div([
                                html.H4([
                                    html.I(className="fas fa-chart-line me-2 text-primary"),
                                    "Dashboard de Medición"
                                ], className="mb-4 pb-3 border-bottom border-2 border-primary"),
                                
                                html.P([
                                    "El dashboard principal realiza mediciones de impedancia con ",
                                    html.Strong("visualización científica en tiempo real"),
                                    ":"
                                ], className="mb-4"),
                                
                                html.Div([
                                    html.Div([
                                        html.H6([
                                            html.I(className="fas fa-plug me-2 text-success"),
                                            "Panel de Conexión"
                                        ], className="fw-bold mb-3"),
                                        html.Ul([
                                            html.Li("Auto-detección del puerto serial FTDI/ADMX2001"),
                                            html.Li([
                                                "Indicador visual del estado: ",
                                                html.Span("● verde", className="text-success"),
                                                "=conectado, ",
                                                html.Span("● rojo", className="text-danger"),
                                                "=desconectado"
                                            ]),
                                            html.Li("Botón de desconexión rápida en sidebar"),
                                        ])
                                    ], className="col-md-6 mb-4"),
                                    html.Div([
                                        html.H6([
                                            html.I(className="fas fa-cog me-2 text-primary"),
                                            "Configuración de Barridos"
                                        ], className="fw-bold mb-3"),
                                        info_table(
                                            ["Parámetro", "Rango", "Unidad"],
                                            [
                                                ["Frecuencia", "0.2 Hz - 10 MHz", "Hz"],
                                                ["Puntos", "≥ 2 (sin límite)", "puntos"],
                                                ["Escala", "Lineal / Logarítmica", "-"],
                                                ["Magnitud", "0.001 - 10", "Vpk"],
                                            ]
                                        )
                                    ], className="col-md-6 mb-4"),
                                ], className="row"),
                                
                                html.H6([
                                    html.I(className="fas fa-chart-area me-2 text-primary"),
                                    "Visualizaciones Científicas"
                                ], className="fw-bold mb-3 mt-3"),
                                
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            html.I(className="fas fa-wave-square fa-3x text-primary mb-3"),
                                            html.H5("Diagrama de Bode", className="fw-bold"),
                                            html.P("Magnitud |Z| y fase θ vs frecuencia (escala log-log)", 
                                                  className="small text-muted mb-2"),
                                            html.Span("Interactivo: zoom, pan, hover", className="badge bg-light text-dark")
                                        ], className="text-center p-4 border rounded bg-white shadow-sm h-100"),
                                    ], className="col-md-6 mb-3"),
                                    html.Div([
                                        html.Div([
                                            html.I(className="fas fa-bullseye fa-3x text-success mb-3"),
                                            html.H5("Diagrama de Nyquist", className="fw-bold"),
                                            html.P("Plano complejo Re[Z] vs Im[Z] con color por frecuencia", 
                                                  className="small text-muted mb-2"),
                                            html.Span("Análisis de impedancia compleja", className="badge bg-light text-dark")
                                        ], className="text-center p-4 border rounded bg-white shadow-sm h-100"),
                                    ], className="col-md-6 mb-3"),
                                ], className="row"),
                            ], className="mb-5"),

                            # Modos de Display
                            html.Div([
                                html.H4([
                                    html.I(className="fas fa-list-alt me-2 text-primary"),
                                    "Modos de Display del ADMX2001B"
                                ], className="mb-4 pb-3 border-bottom border-2 border-primary"),
                                
                                html.P([
                                    "El ADMX2001B soporta ",
                                    html.Strong("18 modos de display"),
                                    " diferentes en unidades SI:"
                                ], className="mb-4"),
                                
                                html.Div([
                                    html.Div([
                                        html.H6("Capacitivos (Serie)", className="text-primary fw-bold border-bottom pb-2"),
                                        html.Ul([
                                            html.Li([html.Code("Cs-Rs"), " - Capacitancia + Resistencia serie"]),
                                            html.Li([html.Code("Cs-D"), " - Capacitancia + Factor de disipación"]),
                                            html.Li([html.Code("Cs-Q"), " - Capacitancia + Factor de calidad"]),
                                        ], className="small")
                                    ], className="col-md-4 mb-3"),
                                    html.Div([
                                        html.H6("Capacitivos (Paralelo)", className="text-primary fw-bold border-bottom pb-2"),
                                        html.Ul([
                                            html.Li([html.Code("Cp-Rp"), " - Capacitancia + Resistencia paralelo"]),
                                            html.Li([html.Code("Cp-D"), " - Capacitancia + Factor de disipación"]),
                                            html.Li([html.Code("Cp-Q"), " - Capacitancia + Factor de calidad"]),
                                        ], className="small")
                                    ], className="col-md-4 mb-3"),
                                    html.Div([
                                        html.H6("Inductivos (Serie)", className="text-success fw-bold border-bottom pb-2"),
                                        html.Ul([
                                            html.Li([html.Code("Ls-Rs"), " - Inductancia + Resistencia serie"]),
                                            html.Li([html.Code("Ls-D"), " - Inductancia + Factor de disipación"]),
                                            html.Li([html.Code("Ls-Q"), " - Inductancia + Factor de calidad"]),
                                        ], className="small")
                                    ], className="col-md-4 mb-3"),
                                    html.Div([
                                        html.H6("Inductivos (Paralelo)", className="text-success fw-bold border-bottom pb-2"),
                                        html.Ul([
                                            html.Li([html.Code("Lp-Rp"), " - Inductancia + Resistencia paralelo"]),
                                            html.Li([html.Code("Lp-D"), " - Inductancia + Factor de disipación"]),
                                            html.Li([html.Code("Lp-Q"), " - Inductancia + Factor de calidad"]),
                                        ], className="small")
                                    ], className="col-md-4 mb-3"),
                                    html.Div([
                                        html.H6("Impedancia", className="text-warning fw-bold border-bottom pb-2"),
                                        html.Ul([
                                            html.Li([html.Code("R-X"), " - Resistencia + Reactancia (rectangular)"]),
                                            html.Li([html.Code("Z-θ°"), " - Magnitud + Fase en grados"]),
                                            html.Li([html.Code("Z-θʳ"), " - Magnitud + Fase en radianes"]),
                                        ], className="small")
                                    ], className="col-md-4 mb-3"),
                                    html.Div([
                                        html.H6("Admitancia", className="text-info fw-bold border-bottom pb-2"),
                                        html.Ul([
                                            html.Li([html.Code("G-B"), " - Conductancia + Susceptancia"]),
                                            html.Li([html.Code("Y-θ°"), " - Magnitud admitancia + Fase grados"]),
                                            html.Li([html.Code("Y-θʳ"), " - Magnitud admitancia + Fase radianes"]),
                                        ], className="small")
                                    ], className="col-md-4 mb-3"),
                                ], className="row"),
                                
                                info_box([
                                    html.Strong("Uso: "),
                                    "Selecciona el modo con el comando ",
                                    html.Code("display <0-17>"),
                                    " según el tipo de componente que estés midiendo."
                                ], "tip"),
                            ], className="mb-5"),

                            # Simulador
                            html.Div([
                                html.H4([
                                    html.I(className="fas fa-calculator me-2 text-success"),
                                    "Simulador RLC"
                                ], className="mb-4 pb-3 border-bottom border-2 border-success"),
                                
                                html.P([
                                    "Calculadora de impedancia para ",
                                    html.Strong("planificación experimental"),
                                    ":"
                                ], className="mb-3"),
                                
                                html.Ul([
                                    html.Li("Soporta circuitos ideales y reales con parásitos"),
                                    html.Li("Componentes individuales: R, L, C"),
                                    html.Li("Configuraciones serie y paralelo"),
                                    html.Li("Salida: magnitud, fase, componentes real/imaginaria"),
                                ]),
                                
                                info_box([
                                    html.I(className="fas fa-lightbulb me-2"),
                                    "Usa el simulador para predecir el comportamiento antes de realizar mediciones físicas."
                                ], "tip"),
                            ], className="mb-5"),

                            # Persistencia
                            html.Div([
                                html.H4([
                                    html.I(className="fas fa-database me-2 text-info"),
                                    "Persistencia de Datos"
                                ], className="mb-4 pb-3 border-bottom border-2 border-info"),
                                
                                html.P("Los datos de barrido se guardan automáticamente:", className="mb-3"),
                                
                                html.Ul([
                                    html.Li("Almacenamiento en sesión del navegador (session storage)"),
                                    html.Li("Navegación entre páginas sin pérdida de datos"),
                                    html.Li("Gráficos restaurados al regresar al Dashboard"),
                                    html.Li("Exportación a CSV disponible"),
                                ]),
                            ], className="mb-5"),

                        ], className="", id="content-software", style={"display": "none"}),

                        # ========== TAB 4: CALIBRACIÓN ==========
                        html.Div([
                            # Importancia
                            html.Div([
                                html.Div([
                                    html.Div([
                                        html.I(className="fas fa-exclamation-circle fa-2x text-danger me-3"),
                                        html.Div([
                                            html.H4("⚠️ Calibración Obligatoria", className="mb-1 fw-bold"),
                                            html.P([
                                                "Las mediciones ",
                                                html.Strong("NO serán precisas"),
                                                " hasta completar la calibración ",
                                                html.Strong("OPEN-SHORT-LOAD"),
                                                " con estándares certificados. Los tres pasos deben realizarse en orden estricto."
                                            ], className="mb-0")
                                        ])
                                    ], className="d-flex align-items-center")
                                ], className="alert alert-danger border-0 shadow-sm py-4 mb-5")
                            ]),

                            # Proceso de calibración
                            html.H4([
                                html.I(className="fas fa-clipboard-check me-2 text-primary"),
                                "Proceso de Calibración"
                            ], className="mb-4 pb-3 border-bottom border-2 border-primary"),

                            # Paso Open
                            step_card(
                                1,
                                "Open Calibration (Circuito Abierto)",
                                [
                                    html.P([
                                        "Corrige parásitas del módulo y cables cuando ",
                                        html.Strong("no hay carga conectada"),
                                        "."
                                    ]),
                                    html.H6("Configuración:", className="fw-bold mt-3"),
                                    html.Ol([
                                        html.Li("Conecta H_POT con H_CUR (cortocircuito)"),
                                        html.Li("Conecta L_POT con L_CUR (cortocircuito)"),
                                        html.Li("Deja H y L desconectadas entre sí (circuito abierto)"),
                                    ]),
                                    command_card("calibrate open", "Ejecutar calibración open"),
                                ],
                                image_src=IMAGES.get('open_load'),
                                image_caption="Configuración OPEN - Interruptores en posición OPEN y GND",
                                color="primary"
                            ),

                            # Paso Short
                            step_card(
                                2,
                                "Short Calibration (Cortocircuito)",
                                [
                                    html.P([
                                        "Corrige impedancias parásitas cuando ",
                                        html.Strong("todas las terminales están cortocircuitadas"),
                                        "."
                                    ]),
                                    html.H6("Configuración:", className="fw-bold mt-3"),
                                    html.Ol([
                                        html.Li("Conecta todas las terminales juntas (H_POT, H_CUR, L_POT, L_CUR)"),
                                        html.Li("Solo cuando ganancia canal 1 es 0 o 1"),
                                        html.Li("Reduce la magnitud a 0.2V para evitar saturación"),
                                    ]),
                                    command_card("calibrate short", "Ejecutar calibración short"),
                                ],
                                image_src=IMAGES.get('cal_connections'),
                                image_caption="Conexiones para calibración SHORT - Todas las terminales unidas",
                                color="warning"
                            ),

                            # Paso Load
                            step_card(
                                3,
                                "Load Calibration (Carga Known)",
                                [
                                    html.P([
                                        "Proporciona ",
                                        html.Strong("trazabilidad"),
                                        " a fuente externa certificada (resistor de precisión típicamente)."
                                    ]),
                                    html.H6("Configuración:", className="fw-bold mt-3"),
                                    html.Ol([
                                        html.Li("Conecta impedancia conocida entre terminales H y L"),
                                        html.Li("El valor debe ser cercano a la impedancia del DUT a medir"),
                                        html.Li("Usa un resistor de precisión certificado (ej: 1kΩ ±0.1%)"),
                                    ]),
                                    html.Div([
                                        html.Strong("Ejemplos:"),
                                        html.Pre(
                                            "calibrate rt 1000 xt 0    # Resistor de 1kΩ, reactancia 0",
                                            className="bg-dark text-light p-2 rounded mt-2 small"
                                        )
                                    ], className="mt-3"),
                                ],
                                color="success"
                            ),

                            # Guardar
                            html.Div([
                                html.H4([
                                    html.I(className="fas fa-save me-2 text-info"),
                                    "Guardar Calibración"
                                ], className="mb-4"),
                                
                                html.P([
                                    "Después de completar los 3 pasos, guarda los coeficientes en memoria no volátil:"
                                ]),
                                
                                command_card("calibrate commit 20251106", "Guardar calibración en EEPROM"),
                                
                                html.Div([
                                    html.P([
                                        html.Strong("Contraseña por defecto: "),
                                        html.Code("Analog123", className="bg-dark text-info px-2 py-1 rounded")
                                    ]),
                                    html.P([
                                        html.Strong("Capacidad: "),
                                        "Hasta 25 calibraciones en EEPROM o 450 en Flash, en múltiples frecuencias."
                                    ], className="small text-muted mb-0")
                                ], className="bg-light p-3 rounded border mt-3"),
                                
                                info_box([
                                    html.I(className="fas fa-lightbulb me-2"),
                                    "Realiza calibraciones en las frecuencias que más uses para máxima precisión."
                                ], "tip"),
                            ], className="mb-5 p-4 border rounded bg-white shadow-sm"),

                        ], className="", id="content-calibration", style={"display": "none"}),

                        # ========== TAB 5: CLI ==========
                        html.Div([
                            html.Div([
                                html.H2([
                                    html.I(className="fas fa-terminal me-2 text-dark"),
                                    "Interfaz de Línea de Comandos (CLI)"
                                ], className="mb-4 pb-3 border-bottom border-2 border-dark"),
                                
                                html.P([
                                    "El ADMX2001B se controla mediante comandos de texto vía UART. "
                                    "Esta sección describe los comandos más importantes."
                                ], className="lead mb-4"),
                            ]),

                            # Tabla de modos
                            html.Div([
                                html.H4([
                                    html.I(className="fas fa-table me-2 text-primary"),
                                    "Tabla de Modos de Display"
                                ], className="mb-4"),
                                
                                html.P([
                                    "Selecciona el modo con el comando ",
                                    html.Code("display <0-17>"),
                                    ":"
                                ], className="mb-3"),
                                
                                info_table(
                                    ["Modo", "Formato", "Descripción"],
                                    [
                                        ["0", "Cs-Rs", "Capacitancia serie + Resistencia"],
                                        ["1", "Cs-D", "Capacitancia serie + Factor D"],
                                        ["2", "Cs-Q", "Capacitancia serie + Factor Q"],
                                        ["3", "Cp-Rp", "Capacitancia paralelo + Resistencia"],
                                        ["4", "Cp-D", "Capacitancia paralelo + Factor D"],
                                        ["5", "Cp-Q", "Capacitancia paralelo + Factor Q"],
                                        ["6", "R-X", "Resistencia + Reactancia (rectangular)"],
                                        ["7", "Z-θ°", "Magnitud + Fase en grados"],
                                        ["8", "Z-θʳ", "Magnitud + Fase en radianes"],
                                        ["9", "Ls-Rs", "Inductancia serie + Resistencia"],
                                        ["10", "Ls-D", "Inductancia serie + Factor D"],
                                        ["11", "Ls-Q", "Inductancia serie + Factor Q"],
                                        ["12", "Lp-Rp", "Inductancia paralelo + Resistencia"],
                                        ["13", "Lp-D", "Inductancia paralelo + Factor D"],
                                        ["14", "Lp-Q", "Inductancia paralelo + Factor Q"],
                                        ["15", "G-B", "Conductancia + Susceptancia"],
                                        ["16", "Y-θ°", "Admitancia + Fase grados"],
                                        ["17", "Y-θʳ", "Admitancia + Fase radianes"],
                                    ]
                                ),
                            ], className="mb-5"),

                            # Comandos básicos
                            html.Div([
                                html.H4([
                                    html.I(className="fas fa-crosshairs me-2 text-primary"),
                                    "Comandos de Medición"
                                ], className="mb-4"),
                                
                                command_card("z", "Realizar medición de impedancia"),
                                command_card("frequency 1000", "Frecuencia de excitación (Hz) - Rango: 0.2Hz a 10MHz"),
                                command_card("magnitude 1.0", "Amplitud pico (V) - Rango: 0.001V a 10V"),
                                command_card("average 200", "Número de muestras para promedio (1-256)"),
                                
                                html.Div([
                                    html.Strong("Ejemplo de sesión:"),
                                    html.Pre([
                                        "> frequency 1000          # Configurar 1kHz\n",
                                        "> magnitude 0.5           # Amplitud 0.5Vpk\n",
                                        "> display 6               # Modo R-X\n",
                                        "> z                       # Medir\n",
                                        "147.23 -52.18           # R=147.23Ω, X=-52.18Ω"
                                    ], className="bg-dark text-light p-3 rounded mt-2 small")
                                ], className="border rounded p-3 mt-3 bg-light"),
                            ], className="mb-5"),

                            # Barrido
                            html.Div([
                                html.H4([
                                    html.I(className="fas fa-chart-line me-2 text-warning"),
                                    "Comandos de Barrido"
                                ], className="mb-4"),
                                
                                html.H6("🔹 Barrido de Frecuencia", className="mb-2"),
                                command_card("sweep_type frequency 100 10000", "Barrido entre 100Hz y 10kHz"),
                                command_card("sweep_scale log", "Escala logarítmica (o 'linear')"),
                                command_card("count 50", "Número de puntos de medición"),
                                
                                html.H6("🔹 Barrido de Bias DC", className="mb-2 mt-3"),
                                command_card("sweep_type bias -2 2", "Barrido de bias -2V a +2V"),
                                
                                html.H6("🔹 Barrido de Magnitud", className="mb-2 mt-3"),
                                command_card("sweep_type magnitude 0.1 5", "Barrido de amplitud 0.1V a 5V"),
                                
                                info_box([
                                    "Los barridos devuelven múltiples mediciones automáticamente. "
                                    "Usa 'mdelay' para ajustar velocidad vs estabilidad."
                                ], "info"),
                            ], className="mb-5"),

                            # Ganancia y Timing
                            html.Div([
                                html.H4([
                                    html.I(className="fas fa-sliders-h me-2 text-info"),
                                    "Configuración Avanzada"
                                ], className="mb-4"),
                                
                                html.H6("⚙️ Control de Ganancia", className="mb-2"),
                                command_card("setgain ch0 <0-3>", "Ganancia canal 0 (voltaje)"),
                                command_card("setgain ch1 <0-3>", "Ganancia canal 1 (corriente)"),
                                command_card("setgain auto", "Modo auto-ranging (recomendado)"),
                                
                                html.H6("⏱️ Optimización de Timing", className="mb-2 mt-3"),
                                command_card("mdelay <ms>", "Retardo entre mediciones"),
                                command_card("tdelay <ms>", "Retardo de asentamiento transitorio"),
                                
                                html.Div([
                                    html.Strong("Guía de timing:"),
                                    html.Ul([
                                        html.Li("f > 1kHz: mdelay=50-100ms, tdelay=10-20ms (rápido)"),
                                        html.Li("f = 100Hz-1kHz: mdelay=100-200ms, tdelay=50-100ms (balance)"),
                                        html.Li("f < 100Hz: mdelay=200-500ms, tdelay=200-500ms (precisión)"),
                                    ], className="small mb-0 mt-2")
                                ], className="bg-light p-3 rounded border mt-3"),
                            ], className="mb-5"),

                            # Sistema
                            html.Div([
                                html.H4([
                                    html.I(className="fas fa-wrench me-2 text-secondary"),
                                    "Comandos de Sistema"
                                ], className="mb-4"),
                                
                                command_card("*idn", "Identificación del dispositivo"),
                                command_card("help", "Lista todos los comandos disponibles"),
                                command_card("help <comando>", "Ayuda detallada sobre comando específico"),
                                command_card("selftest", "Ver resultado del último self-test"),
                                command_card("reset", "Reiniciar el sistema"),
                                
                                info_box([
                                    html.I(className="fas fa-check-circle me-2"),
                                    "Ejecuta 'selftest' después de encender para verificar que el hardware está OK."
                                ], "success"),
                            ], className="mb-5"),

                        ], className="", id="content-cli", style={"display": "none"}),

                        # ========== TAB 6: SOPORTE ==========
                        html.Div([
                            html.Div([
                                # Contacto
                                html.Div([
                                    html.H4([
                                        html.I(className="fas fa-envelope me-2 text-primary"),
                                        "Contacto de Soporte"
                                    ], className="mb-4"),
                                    
                                    html.P([
                                        "Para soporte técnico, preguntas o actualizaciones de firmware:"
                                    ], className="mb-4"),
                                    
                                    html.A([
                                        html.I(className="fas fa-envelope me-2"),
                                        "admx-support@analog.com"
                                    ], href="mailto:admx-support@analog.com", 
                                       className="btn btn-primary btn-lg mb-2"),
                                ], className="mb-5"),

                                # Recursos
                                html.Div([
                                    html.H4([
                                        html.I(className="fas fa-link me-2 text-info"),
                                        "Recursos Externos"
                                    ], className="mb-4"),
                                    
                                    html.Div([
                                        html.A([
                                            html.I(className="fas fa-book me-2"),
                                            html.Strong("Wiki Analog - ADMX2001")
                                        ], href="https://wiki.analog.com/resources/eval/user-guides/admx/eval-admx2001ebz", 
                                           target="_blank", className="d-block mb-3 fs-5"),
                                        html.A([
                                            html.I(className="fas fa-download me-2"),
                                            "Drivers FTDI VCP"
                                        ], href="https://www.ftdichip.com/Drivers/VCP.htm", 
                                           target="_blank", className="d-block mb-2"),
                                        html.A([
                                            html.I(className="fas fa-terminal me-2"),
                                            "TeraTerm (Emulador Terminal)"
                                        ], href="https://github.com/TeraTermProject/teraterm/releases", 
                                           target="_blank", className="d-block mb-2"),
                                        html.A([
                                            html.I(className="fab fa-github me-2"),
                                            "Repositorio GitHub - ZORIA"
                                        ], href="https://github.com/mario1027/libeval", 
                                           target="_blank", className="d-block"),
                                    ]),
                                ], className="mb-5"),

                                # Firmware
                                html.Div([
                                    html.H4([
                                        html.I(className="fas fa-microchip me-2 text-success"),
                                        "Versiones de Firmware"
                                    ], className="mb-4"),
                                    
                                    info_table(
                                        ["Versión", "Estado", "Características"],
                                        [
                                            ["1.3.3", "✅ Estable", "Última versión recomendada"],
                                            ["1.3.2", "✅ Estable", "Optimizaciones de tiempo"],
                                            ["1.3.1", "✅ Estable", "Mejoras de ruido"],
                                            ["1.2.4", "✅ Estable", "Script de instalación"],
                                        ]
                                    ),
                                ], className="mb-5"),

                                # Sobre ZORIA
                                html.Div([
                                    html.H4([
                                        html.I(className="fas fa-code me-2 text-secondary"),
                                        "Sobre ZORIA"
                                    ], className="mb-4"),
                                    
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
                                ], className="mb-5"),

                            ], className="max-width-800")
                        ], className="", id="content-support", style={"display": "none"}),

                    ], className="doc-content"),

                ], className="container-fluid py-4 px-4")
            ], className="main-content w-100")
        ], className="d-flex flex-grow-1"),

        # Footer
        footer(),
        
        # Botón flotante del terminal
        floating_terminal_button()
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
    base_class = "btn btn-outline-primary me-2 mb-2 fw-bold"
    active_class = "btn btn-primary me-2 mb-2 fw-bold"
    
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
