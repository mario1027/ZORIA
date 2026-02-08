"""
Página de Documentación Oficial del Software ZORIA
Sistema completo de documentación para el analizador de impedancia EVAL-ADMX2001
Versión mejorada con UI/UX profesional y contenido exhaustivo
"""
from dash import html, dcc, Input, Output, callback, State
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


# ==================== URLs DE IMÁGENES LOCALES ====================
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

def doc_section(title, icon, content, id=None, bg_color="white"):
    """Sección de documentación con estilo mejorado"""
    # Construir props dinámicamente solo si id no es None
    props = {
        "className": f"doc-section mb-4 p-4 rounded shadow-sm bg-{bg_color}",
        "style": {"border": "1px solid #e9ecef"}
    }
    if id is not None:
        props["id"] = id
    
    return html.Div([
        html.Div([
            html.Div([
                html.I(className=f"fas fa-{icon} me-3 text-primary"),
                html.H4(title, className="mb-0 d-inline-block fw-bold")
            ], className="section-header mb-4 pb-3 border-bottom border-3 border-primary"),
            html.Div(content, className="section-content")
        ], **props)
    ])


def image_card(src, alt, caption=None, max_width="100%"):
    """Tarjeta de imagen con caption opcional mejorada"""
    children = [
        html.Div([
            html.Img(src=src, alt=alt, className="img-fluid rounded shadow", 
                    style={"maxWidth": max_width, "width": "100%", "border": "2px solid #dee2e6"}),
        ], className="image-container bg-light p-4 rounded text-center mb-2")
    ]
    if caption:
        children.append(
            html.Div([
                html.I(className="fas fa-image me-2 text-muted"),
                html.Span(caption, className="text-muted")
            ], className="small mt-2 mb-0 text-center fst-italic")
        )
    return html.Div(children, className="image-card mb-4")


def step_card(number, title, content, image_src=None, image_caption=None, color="primary"):
    """Tarjeta de paso numerado con imagen opcional mejorada"""
    card_children = [
        # Número y título con diseño mejorado
        html.Div([
            html.Div([
                html.Span(str(number), className="fs-4 fw-bold")
            ], className=f"step-number bg-{color} text-white rounded-circle d-flex align-items-center justify-content-center me-3", 
               style={"width": "50px", "height": "50px", "minWidth": "50px"}),
            html.H5(title, className="mb-0 fw-bold text-dark")
        ], className="step-header mb-3 d-flex align-items-center"),
        # Contenido
        html.Div(content, className="step-content ps-5 ms-1")
    ]
    # Imagen opcional
    if image_src:
        card_children.append(
            html.Div([image_card(image_src, title, image_caption, max_width="800px")], 
                    className="step-image mt-4 ps-5 ms-1")
        )
    return html.Div([
        html.Div(card_children, 
                className=f"step-card p-4 border-start border-5 border-{color} bg-white rounded shadow mb-4",
                style={"transition": "all 0.3s ease", "borderLeft": f"5px solid var(--bs-{color})"})
    ])


def info_box(content, type="info", icon=None):
    """Caja de información con icono mejorada"""
    icons_map = {
        "info": "info-circle",
        "warning": "exclamation-triangle",
        "danger": "exclamation-circle",
        "success": "check-circle",
        "tip": "lightbulb",
        "note": "sticky-note"
    }
    colors = {
        "info": "info",
        "warning": "warning",
        "danger": "danger", 
        "success": "success",
        "tip": "primary",
        "note": "secondary"
    }
    icon_class = icon or icons_map.get(type, 'info-circle')
    
    if not isinstance(content, list):
        content = [content]
    
    return html.Div([
        html.Div(
            [html.I(className=f"fas fa-{icon_class} me-3 fs-5")] + content,
            className=f"alert alert-{colors.get(type, 'info')} border-0 d-flex align-items-start shadow-sm mb-0"
        )
    ], className="mb-4")


def spec_badge(label, value, color="secondary", icon=None):
    """Badge con especificación técnica mejorado"""
    return html.Div([
        html.Div([
            icon and html.I(className=f"fas fa-{icon} me-2") or None,
            html.Span(label, className="text-muted small")
        ], className="mb-2"),
        html.Span(value, className=f"badge bg-{color} px-3 py-2 fs-6 shadow-sm")
    ], className="mb-3")


def command_card(command, description, output=None):
    """Card para comando CLI mejorado"""
    content = [
        html.Div([
            html.I(className="fas fa-terminal me-2 text-success"),
            html.Code(command, className="text-success")
        ], className="bg-dark p-3 rounded mb-2 font-monospace"),
        html.P(description, className="text-muted small mb-2")
    ]
    if output:
        content.append(
            html.Div([
                html.Strong("Salida:", className="text-muted small d-block mb-1"),
                html.Pre(output, className="bg-light p-2 rounded small border")
            ])
        )
    return html.Div(content, className="mb-3 border-start border-3 border-success ps-3")


def info_table(headers, rows, striped=True, hover=True):
    """Tabla de información con estilo Volt mejorada"""
    return html.Div([
        html.Table([
            html.Thead([
                html.Tr([html.Th(h, className="bg-primary text-white fw-bold py-3") for h in headers])
            ]),
            html.Tbody([
                html.Tr([html.Td(cell, className="py-3") for cell in row])
                for row in rows
            ])
        ], className=f"table {'table-striped' if striped else ''} {'table-hover' if hover else ''} mb-0 shadow-sm")
    ], className="table-responsive rounded border")


def collapsible_section(title, content, id_prefix, icon="chevron-down", color="primary", default_open=False):
    """Sección colapsable para organizar contenido"""
    collapse_id = f"collapse-{id_prefix}"
    return html.Div([
        html.Div([
            html.Button([
                html.I(className=f"fas fa-{icon} me-2"),
                html.Span(title, className="fw-bold"),
                html.I(className="fas fa-chevron-down ms-auto")
            ], className=f"btn btn-{color} w-100 text-start d-flex align-items-center shadow-sm",
               **{"data-bs-toggle": "collapse", "data-bs-target": f"#{collapse_id}", "aria-expanded": "true" if default_open else "false"})
        ]),
        html.Div([
            html.Div(content, className="p-4")
        ], id=collapse_id, className=f"collapse {'show' if default_open else ''} border border-top-0 rounded-bottom")
    ], className="mb-3")


def feature_card(icon, title, description, color="primary"):
    """Card de característica destacada"""
    return html.Div([
        html.Div([
            html.Div([
                html.I(className=f"fas fa-{icon} fa-3x text-{color} mb-3"),
                html.H5(title, className="fw-bold mb-2"),
                html.P(description, className="text-muted small mb-0")
            ], className="text-center p-4")
        ], className="h-100 border rounded shadow-sm bg-white", 
           style={"transition": "transform 0.3s ease", "cursor": "default"})
    ], className="col-lg-3 col-md-4 col-sm-6 mb-4")


# ==================== CONTENIDO DE PESTAÑAS ====================

def tab_quickstart():
    """Contenido de la pestaña Inicio Rápido"""
    return html.Div([
        # Hero Section
        html.Div([
            html.H3([
                html.I(className="fas fa-rocket me-3 text-primary"),
                "Inicio Rápido"
            ], className="mb-3 fw-bold"),
            html.P([
                "Esta guía te ayudará a configurar y comenzar a usar tu ",
                html.Strong("EVAL-ADMX2001", className="text-primary"),
                " en cinco simples pasos. Sigue cada paso cuidadosamente para garantizar mediciones precisas."
            ], className="lead text-muted mb-4")
        ], className="p-4 bg-light rounded shadow-sm mb-4"),
        
        # Paso 1: Drivers
        step_card(
            1,
            "Instalación de Drivers FTDI",
            [
                html.P([
                    "El ", html.Strong("EVAL-ADMX2001EBZ"), " se comunica con tu PC mediante UART. ",
                    "El cable USB-to-UART incluido requiere drivers ",
                    html.Strong("Virtual COM Port (VCP)"), " de FTDI."
                ]),
                html.Div([
                    html.A([
                        html.I(className="fas fa-download me-2"),
                        "Descargar Drivers FTDI"
                    ], href="https://www.ftdichip.com/Drivers/VCP.htm", target="_blank",
                       className="btn btn-primary btn-lg shadow")
                ], className="mb-3"),
                html.H6("Procedimiento:", className="fw-bold mt-3 mb-2"),
                html.Ol([
                    html.Li("Descarga el instalador para tu sistema operativo (Windows/Linux/macOS)"),
                    html.Li("Ejecuta el instalador y sigue las instrucciones"),
                    html.Li([html.Strong("Conecta"), " el cable USB-UART al PC"]),
                    html.Li(["Abre el Administrador de Dispositivos (Windows) o ejecuta ", html.Code("ls /dev/ttyUSB* (Linux)")]),
                    html.Li(["Verifica que aparezca un ", html.Strong("puerto COM/ttyUSB"), " nuevo"]),
                ]),
                info_box([
                    html.Strong("💡 Verificación: "),
                    "En Windows busca 'USB Serial Port (COMx)' bajo 'Ports (COM & LPT)'. ",
                    "En Linux el dispositivo aparecerá como /dev/ttyUSB0 o similar."
                ], "tip"),
            ],
            image_src=IMAGES.get('dev_mgr_vcp'),
            image_caption="Administrador de dispositivos Windows mostrando el puerto COM instalado correctamente",
            color="primary"
        ),

        # Paso 2: Hardware
        step_card(
            2,
            "Configuración del Hardware",
            [
                html.P("Sigue estos pasos en orden para la configuración inicial:"),
                html.Div([
                    html.Div([
                        html.Strong("2.1", className="badge bg-success me-2"),
                        html.Span("Ensamblaje del módulo")
                    ], className="mb-2 fw-bold"),
                    html.Ul([
                        html.Li([
                            "Inserta el módulo ", html.Strong("ADMX2001B", className="text-primary"),
                            " en la placa ", html.Strong("EVAL-ADMX2001EBZ"),
                            " (los conectores tienen guía de posición)"
                        ]),
                        html.Li("Asegúrate de que el módulo esté completamente insertado"),
                    ]),
                ], className="mb-3 p-3 border-start border-3 border-success bg-light rounded"),
                
                html.Div([
                    html.Strong("2.2", className="badge bg-success me-2"),
                    html.Span("Configuración de switches para self-test")
                ], className="mb-2 fw-bold"),
                html.Ul([
                    html.Li([html.Strong("S1"), " → Posición ", html.Span("OPEN", className="badge bg-warning text-dark")]),
                    html.Li([html.Strong("S2"), " → Posición ", html.Span("GND", className="badge bg-dark")]),
                ]),
                
                html.Div([
                    html.Strong("2.3", className="badge bg-success me-2"),
                    html.Span("Alimentación")
                ], className="mb-2 fw-bold mt-3"),
                html.Ul([
                    html.Li("Conecta el adaptador de corriente (9VDC) al jack de alimentación"),
                    html.Li("Conecta el adaptador a la toma de corriente"),
                    html.Li([
                        "Verifica que el LED de self-test esté ",
                        html.Span("VERDE", className="text-success fw-bold"),
                        " (visible desde la parte inferior del módulo)"
                    ]),
                ]),
                
                info_box([
                    html.Strong("⚠️ LED de Self-Test: "),
                    html.Ul([
                        html.Li([html.Span("🟢 Verde", className="text-success"), " → Self-test exitoso, módulo operativo"]),
                        html.Li([html.Span("🟠 Naranja/Rojo", className="text-warning"), " → Falla en self-test analógico, verificar switches"]),
                        html.Li([html.Span("🔴 Rojo", className="text-danger"), " → Error crítico (alimentación, firmware)"]),
                    ], className="mb-0 ps-0")
                ], "warning"),
            ],
            image_src=IMAGES.get('basic_connections'),
            image_caption="Diagrama de conexiones básicas y ubicación de componentes del EVAL-ADMX2001EBZ",
            color="success"
        ),

        # Paso 3: UART
        step_card(
            3,
            "Conexión UART",
            [
                html.P("Conecta el cable UART-to-USB siguiendo el código de colores:"),
                html.Div([
                    html.Table([
                        html.Thead([
                            html.Tr([
                                html.Th("Cable", className="bg-dark text-white"),
                                html.Th("Terminal", className="bg-dark text-white"),
                                html.Th("Función", className="bg-dark text-white")
                            ])
                        ]),
                        html.Tbody([
                            html.Tr([
                                html.Td([html.Span("Naranja", className="badge bg-warning text-dark")]),
                                html.Td([html.Strong("TX")]),
                                html.Td("Transmisión de datos")
                            ]),
                            html.Tr([
                                html.Td([html.Span("Amarillo", className="badge bg-warning")]),
                                html.Td([html.Strong("RX")]),
                                html.Td("Recepción de datos")
                            ]),
                            html.Tr([
                                html.Td([html.Span("Negro", className="badge bg-dark")]),
                                html.Td([html.Strong("GND")]),
                                html.Td("Tierra común")
                            ]),
                        ])
                    ], className="table table-sm mb-0")
                ], className="border rounded mb-3"),
                
                html.H6("Verificaciones:", className="fw-bold mt-3 mb-2"),
                html.Ul([
                    html.Li(["Jumper ", html.Strong("CLK_SEL"), " debe estar en posición ", 
                            html.Span("INT", className="badge bg-primary"), " (reloj interno)"]),
                    html.Li("Los tres cables deben estar firmemente conectados"),
                    html.Li("El cable USB debe estar conectado a un puerto USB del PC"),
                ]),
                
                info_box([
                    html.Strong("🔧 Importante: "),
                    "No conectes los cables rojo y verde del cable USB-UART. ",
                    "Solo usa Naranja (TX), Amarillo (RX) y Negro (GND)."
                ], "note"),
            ],
            image_src=IMAGES.get('uart_connection'),
            image_caption="Conexión correcta del cable UART-to-USB a los terminales de la placa",
            color="info"
        ),

        # Paso 4: Software ZORIA
        step_card(
            4,
            "Inicio del Software ZORIA",
            [
                html.P([
                    html.Strong("ZORIA"), " es una plataforma web moderna que transforma el ADMX2001 ",
                    "en un sistema de medición profesional con visualización científica en tiempo real."
                ]),
                
                html.Div([
                    html.H6("Características principales:", className="fw-bold mb-3"),
                    html.Div([
                        feature_card("plug", "Auto-Detección", "Detección y conexión automática del puerto serial", "success"),
                        feature_card("chart-line", "Visualización RT", "Diagramas de Bode y Nyquist en tiempo real", "primary"),
                        feature_card("download", "Exportación", "Exporta datos a CSV para análisis externo", "warning"),
                        feature_card("calculator", "Simulador RLC", "Calcula impedancias teóricas de circuitos", "info"),
                    ], className="row"),
                ], className="mb-4"),
                
                html.H6("Inicio rápido:", className="fw-bold mb-2"),
                html.Ol([
                    html.Li(["Abre una terminal en la carpeta de ZORIA"]),
                    html.Li([
                        "Ejecuta: ",
                        html.Code("python app.py", className="bg-dark text-success p-1 rounded")
                    ]),
                    html.Li([
                        "Abre tu navegador en: ",
                        html.A("http://localhost:8050", href="http://localhost:8050", 
                              target="_blank", className="btn btn-sm btn-primary ms-2")
                    ]),
                    html.Li("¡Comienza a realizar mediciones!"),
                ]),
                
                info_box([
                    html.Strong("📱 Multiplataforma: "),
                    "ZORIA funciona en cualquier dispositivo con navegador web. ",
                    "Puedes acceder desde tablets o smartphones conectados a la misma red."
                ], "success"),
            ],
            color="primary"
        ),

        # Paso 5: Primera medición
        step_card(
            5,
            "Primera Medición",
            [
                html.Div([
                    html.P("Configura el hardware para medición:"),
                    html.Ul([
                        html.Li([html.Strong("S1"), " → ", html.Span("DUT", className="badge bg-info")]),
                        html.Li([html.Strong("S2"), " → ", html.Span("GND", className="badge bg-dark")]),
                    ]),
                    html.P("Conecta las pinzas de prueba:", className="fw-bold mt-3"),
                    html.Ul([
                        html.Li([html.Span("🔴 Rojos", className="text-danger fw-bold"), " → Puertos HCUR y HPOT"]),
                        html.Li([html.Span("⚫ Negros", className="text-dark fw-bold"), " → Puertos LCUR y LPOT"]),
                    ]),
                ], className="p-3 bg-light rounded border mb-3"),
                
                html.H6("En la interfaz ZORIA:", className="fw-bold mb-2"),
                html.Ol([
                    html.Li("Navega a la página Dashboard"),
                    html.Li("Haz clic en el botón de conexión"),
                    html.Li("Selecciona el puerto COM/USB detectado"),
                    html.Li("Configura la frecuencia de medición (ej: 1 kHz)"),
                    html.Li("Haz clic en 'Iniciar Medición'"),
                    html.Li("Observa los resultados en tiempo real"),
                ]),
                
                info_box([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    html.Strong("Calibración Necesaria: "),
                    "Las primeras mediciones no serán precisas. Debes realizar la calibración ",
                    html.Strong("OPEN-SHORT-LOAD"),
                    " con estándares certificados. Consulta la pestaña 'Calibración' para más detalles."
                ], "danger"),
            ],
            image_src=IMAGES.get('photo_setup'),
            image_caption="Configuración completa lista para realizar mediciones con el DUT conectado",
            color="warning"
        ),

        # Próximos pasos
        html.Div([
            html.H4([
                html.I(className="fas fa-forward me-2 text-success"),
                "Próximos Pasos"
            ], className="mb-3 fw-bold"),
            html.Div([
                html.Div([
                    html.A([
                        html.Div([
                            html.I(className="fas fa-balance-scale fa-2x mb-2 text-primary"),
                            html.H6("Calibración", className="fw-bold"),
                            html.P("Aprende a calibrar tu dispositivo para mediciones precisas", className="small text-muted mb-0")
                        ], className="text-center p-4")
                    ], href="#", className="text-decoration-none"),
                ], className="col-md-4 mb-3"),
                
                html.Div([
                    html.A([
                        html.Div([
                            html.I(className="fas fa-book fa-2x mb-2 text-success"),
                            html.H6("Guía de Usuario", className="fw-bold"),
                            html.P("Explora todas las funciones y capacidades de ZORIA", className="small text-muted mb-0")
                        ], className="text-center p-4")
                    ], href="#", className="text-decoration-none"),
                ], className="col-md-4 mb-3"),
                
                html.Div([
                    html.A([
                        html.Div([
                            html.I(className="fas fa-terminal fa-2x mb-2 text-warning"),
                            html.H6("Comandos CLI", className="fw-bold"),
                            html.P("Domina la interfaz de línea de comandos avanzada", className="small text-muted mb-0")
                        ], className="text-center p-4")
                    ], href="#", className="text-decoration-none"),
                ], className="col-md-4 mb-3"),
            ], className="row"),
        ], className="bg-light p-4 rounded shadow-sm mt-4"),
        
    ], id="content-quickstart")


def tab_hardware():
    """Contenido de la pestaña Hardware"""
    return html.Div([
        # Hero
        html.Div([
            html.H3([
                html.I(className="fas fa-microchip me-3 text-primary"),
                "Especificaciones de Hardware"
            ], className="mb-3 fw-bold"),
            html.P([
                "Información técnica detallada sobre el ", html.Strong("EVAL-ADMX2001"),
                " y el módulo ", html.Strong("ADMX2001B"), "."
            ], className="lead text-muted mb-0")
        ], className="p-4 bg-light rounded shadow-sm mb-4"),
        
        # Módulo ADMX2001B
        doc_section(
            "ADMX2001B - Módulo Analizador de Impedancia",
            "microchip",
            [
                html.Div([
                    html.P([
                        "System-on-Module (SOM) de alto rendimiento para análisis de impedancia y caracterización de componentes."
                    ], className="lead mb-4"),
                    
                    html.H5("Especificaciones Principales", className="fw-bold mb-3"),
                    html.Div([
                        spec_badge("Factor de Forma", "1.5 × 2.5 pulgadas", "primary", "ruler-combined"),
                        spec_badge("Rango de Frecuencias", "0.2 Hz - 10 MHz", "success", "wave-square"),
                        spec_badge("Resolución ADC", "18 bits", "info", "microchip"),
                        spec_badge("Alimentación", "3.3V única", "warning", "bolt"),
                        spec_badge("Interfaces", "UART + SPI", "secondary", "network-wired"),
                        spec_badge("Modos de Display", "18 formatos", "primary", "th-list"),
                    ], className="row row-cols-2 row-cols-md-3 mb-4"),
                    
                    html.H5("Capacidades de Medición", className="fw-bold mb-3 mt-4"),
                    info_table(
                        ["Parámetro", "Rango", "Descripción"],
                        [
                            ["Impedancia (Z)", "< 1Ω a > 100MΩ", "Magnitud y fase"],
                            ["Capacitancia (C)", "< 1pF a > 100mF", "Serie y paralelo"],
                            ["Inductancia (L)", "< 1nH a > 100H", "Serie y paralelo"],
                            ["Resistencia DC", "< 1Ω a > 100MΩ", "Medición de 4 terminales"],
                            ["Factor Q", "0.001 a 10000", "Factor de calidad"],
                            ["Factor D", "0.0001 a 10", "Factor de disipación"],
                        ]
                    ),
                ]),
            ],
            bg_color="white"
        ),
        
        # EVAL-ADMX2001EBZ
        doc_section(
            "EVAL-ADMX2001EBZ - Placa de Evaluación",
            "server",
            [
                html.P([
                    "Placa de desarrollo y evaluación diseñada para facilitar el uso del módulo ADMX2001B ",
                    "con conectores estándar y alimentación regulada."
                ], className="lead mb-4"),
                
                html.H5("Características Principales", className="fw-bold mb-3"),
                html.Ul([
                    html.Li([html.Strong("Conectores BNC:"), " 4 conectores para sondas LCR estándar"]),
                    html.Li([html.Strong("Interfaz UART:"), " Compatible con cables USB-to-UART comerciales"]),
                    html.Li([html.Strong("Triggers y Clock:"), " Conectores SMA para sincronización externa"]),
                    html.Li([html.Strong("Headers Arduino:"), " Compatible con plataformas de desarrollo (SDP-K1)"]),
                    html.Li([html.Strong("Alimentación:"), " +5V a +12V DC, regulador interno a 3.3V"]),
                    html.Li([html.Strong("LEDs indicadores:"), " Estado, self-test, y alimentación"]),
                ]),
                
                html.H5("Descripción de Terminales", className="fw-bold mb-3 mt-4"),
                info_table(
                    ["Terminal", "Tipo", "Descripción"],
                    [
                        ["H_CUR", "BNC Rojo", "Fuente de señal de excitación (±5V @ 50mA máx)"],
                        ["H_POT", "BNC Rojo", "Sensado de voltaje alto, conectar a H_CUR en DUT"],
                        ["L_POT", "BNC Negro", "Sensado de voltaje bajo, conectar a L_CUR en DUT"],
                        ["L_CUR", "BNC Negro", "Retorno de corriente de excitación"],
                        ["UART TX/RX/GND", "Header", "Comunicación serial 115200-8-N-1, lógica 3.3V"],
                        ["CLK_SEL", "Jumper", "Selección reloj interno (INT) o externo (EXT)"],
                        ["TRIG_IN", "SMA", "Entrada de trigger externo (3.3V, >15μs)"],
                        ["TRIG_OUT", "SMA", "Salida de trigger al completar medición"],
                        ["CLK_IN/OUT", "SMA", "Reloj 50MHz entrada/salida LVCMOS"],
                        ["PMOD", "Header", "Puerto SPI para control avanzado"],
                        ["P6, P7", "Headers", "Salidas digitales y GPIO"],
                    ],
                    striped=True,
                    hover=True
                ),
                
                html.H5("Switches de Configuración", className="fw-bold mb-3 mt-4"),
                html.Div([
                    html.Div([
                        html.H6([
                            html.Span("S1", className="badge bg-primary me-2"),
                            "Selector de Carga"
                        ], className="fw-bold mb-2"),
                        html.Ul([
                            html.Li([html.Strong("OPEN:"), " Para calibración open y self-test"]),
                            html.Li([html.Strong("DUT:"), " Para mediciones normales del dispositivo bajo prueba"]),
                        ])
                    ], className="col-md-6 mb-3"),
                    html.Div([
                        html.H6([
                            html.Span("S2", className="badge bg-primary me-2"),
                            "Selector de Referencia"
                        ], className="fw-bold mb-2"),
                        html.Ul([
                            html.Li([html.Strong("GND:"), " Referencia a tierra (uso normal)"]),
                            html.Li([html.Strong("FLT:"), " Referencia flotante (aplicaciones especiales)"]),
                        ])
                    ], className="col-md-6 mb-3"),
                ], className="row"),
            ],
            bg_color="white"
        ),
        
        # Contenido del Kit
        doc_section(
            "Contenido del Kit y Accesorios",
            "box-open",
            [
                html.Div([
                    html.H5("EVAL-ADMX2001EBZ Kit Incluye:", className="fw-bold mb-3"),
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-check-circle text-success me-2"),
                            html.Span("Placa EVAL-ADMX2001EBZ")
                        ], className="mb-2"),
                        html.Div([
                            html.I(className="fas fa-check-circle text-success me-2"),
                            html.Span("Cable UART-to-USB (TTL-232R-RPI)")
                        ], className="mb-2"),
                        html.Div([
                            html.I(className="fas fa-check-circle text-success me-2"),
                            html.Span("Adaptador universal 9VDC")
                        ], className="mb-2"),
                        html.Div([
                            html.I(className="fas fa-check-circle text-success me-2"),
                            html.Span("Pinzas de prueba para LCR")
                        ], className="mb-2"),
                    ], className="p-3 bg-light rounded"),
                    
                    info_box([
                        html.I(className="fas fa-exclamation-triangle me-2"),
                        html.Strong("⚠️ CRÍTICO: "),
                        "El ", html.Strong("módulo ADMX2001B"), " se vende por separado. ",
                        "Es imprescindible adquirir AMBOS componentes para el funcionamiento completo."
                    ], "danger"),
                    
                    html.H5("Accesorios Opcionales Recomendados:", className="fw-bold mb-3 mt-4"),
                    info_table(
                        ["Categoría", "Descripción", "Uso"],
                        [
                            ["Fixtures LCR", "B+K Precision TL89S1, Keysight 16034G", "Mediciones SMD de precisión"],
                            ["Estándares Cal", "Resistores 1%, Capacitores NP0, Terminaciones", "Calibración trazable"],
                            ["LCR Meter Ref", "Keysight E4980A, Hioki IM3536", "Verificación y transferencia de cal"],
                            ["Cables BNC", "Cables de baja capacitancia <50pF", "Reducción de parásitas"],
                            ["USB Blaster", "Intel/Altera USB Blaster", "Actualización de firmware"],
                        ]
                    ),
                ]),
            ],
            bg_color="white"
        ),
        
        # Imágenes de referencia
        html.Div([
            html.H4("Galería de Referencias", className="fw-bold mb-4"),
            html.Div([
                html.Div([
                    image_card(IMAGES.get('basic_connections'), "Conexiones Básicas", 
                              "Diagrama completo de conexiones y componentes principales")
                ], className="col-lg-6 mb-4"),
                html.Div([
                    image_card(IMAGES.get('photo_setup'), "Configuración Real", 
                              "Ejemplo de configuración completa lista para mediciones")
                ], className="col-lg-6 mb-4"),
            ], className="row"),
        ], className="mt-4"),
        
    ], id="content-hardware", style={"display": "none"})


# Función auxiliar para crear contenido de otras pestañas (continuará...)
def tab_software():
    """Contenido de la pestaña Software - ZORIA"""
    return html.Div([
        html.Div([
            html.H3([
                html.I(className="fas fa-laptop-code me-3 text-primary"),
                "Software ZORIA"
            ], className="mb-3 fw-bold"),
            html.P([
                "ZORIA es una plataforma web de código abierto que transforma el EVAL-ADMX2001 ",
                "en un sistema profesional de análisis de impedancia con visualización científica en tiempo real."
            ], className="lead text-muted mb-0")
        ], className="p-4 bg-light rounded shadow-sm mb-4"),
        
        # Características
        doc_section(
            "Características Principales",
            "star",
            [
                html.Div([
                    feature_card("wifi", "Auto-Detección", "Detección y conexión automática del puerto serial", "success"),
                    feature_card("chart-area", "Visualización RT", "Diagramas de Bode y Nyquist actualizados en vivo", "primary"),
                    feature_card("redo", "Barridos Auto", "Barridos de frecuencia lineales y logarítmicos", "info"),
                    feature_card("save", "Persistencia", "Guarda sesiones y restaura gráficos automáticamente", "warning"),
                    feature_card("file-csv", "Exportación CSV", "Exporta datos para análisis en Excel, Python, MATLAB", "secondary"),
                    feature_card("calculator", "Simulador RLC", "Calcula impedancias teóricas de circuitos complejos", "success"),
                    feature_card("mobile-alt", "Responsive", "Interfaz adaptativa para desktop, tablet y móvil", "primary"),
                    feature_card("book-open", "Documentación", "Manual integrado completo y tutoriales interactivos", "info"),
                ], className="row")
            ]
        ),
        
        # Arquitectura
        doc_section(
            "Arquitectura del Sistema",
            "project-diagram",
            [
                html.P("ZORIA implementa una arquitectura modular de tres capas:", className="lead mb-4"),
                html.Div([
                    html.Div([
                        html.Div([
                            html.H5([
                                html.I(className="fas fa-layer-group me-2 text-primary"),
                                "1. Capa de Hardware"
                            ], className="fw-bold mb-3"),
                            html.Ul([
                                html.Li("Comunicación serial UART a 115200 bps"),
                                html.Li("Parsing y validación de comandos CLI"),
                                html.Li("Control de adquisición y sweeps"),
                                html.Li("Gestión de estados del dispositivo"),
                            ])
                        ], className="p-4 bg-white rounded shadow-sm h-100")
                    ], className="col-lg-4 mb-4"),
                    
                    html.Div([
                        html.Div([
                            html.H5([
                                html.I(className="fas fa-code me-2 text-success"),
                                "2. Capa de Lógica"
                            ], className="fw-bold mb-3"),
                            html.Ul([
                                html.Li("Procesamiento de datos de impedancia"),
                                html.Li("Conversión entre formatos (Z, Y, RLC)"),
                                html.Li("Gestión de calibraciones"),
                                html.Li("Simulador de circuitos RLC"),
                            ])
                        ], className="p-4 bg-white rounded shadow-sm h-100")
                    ], className="col-lg-4 mb-4"),
                    
                    html.Div([
                        html.Div([
                            html.H5([
                                html.I(className="fas fa-desktop me-2 text-warning"),
                                "3. Capa de Presentación"
                            ], className="fw-bold mb-3"),
                            html.Ul([
                                html.Li("Dashboard interactivo con Plotly"),
                                html.Li("Componentes reutilizables Dash"),
                                html.Li("Callbacks reactivos en tiempo real"),
                                html.Li("Sistema de navegación SPA"),
                            ])
                        ], className="p-4 bg-white rounded shadow-sm h-100")
                    ], className="col-lg-4 mb-4"),
                ], className="row"),
            ]
        ),
        
        # Módulos principales
        doc_section(
            "Módulos del Sistema",
            "cubes",
            [
                collapsible_section(
                    "lib/admx2001.py - Driver del Dispositivo",
                    [
                        html.P("Clase principal que encapsula toda la comunicación con el ADMX2001.", className="text-muted"),
                        html.H6("Métodos principales:", className="fw-bold mt-3 mb-2"),
                        html.Ul([
                            html.Li([html.Code("connect()"), " - Establece conexión serial"]),
                            html.Li([html.Code("measure()"), " - Realiza medición única"]),
                            html.Li([html.Code("sweep()"), " - Ejecuta barrido de parámetros"]),
                            html.Li([html.Code("calibrate()"), " - Gestiona proceso de calibración"]),
                            html.Li([html.Code("set_frequency()"), " - Configura frecuencia de medición"]),
                        ])
                    ],
                    "module-admx",
                    "file-code",
                    "primary"
                ),
                
                collapsible_section(
                    "lib/calibration.py - Sistema de Calibración",
                    [
                        html.P("Gestiona coeficientes de calibración y corrección de mediciones.", className="text-muted"),
                        html.H6("Funcionalidades:", className="fw-bold mt-3 mb-2"),
                        html.Ul([
                            html.Li("Almacenamiento de calibraciones Open-Short-Load"),
                            html.Li("Interpolación de coeficientes por frecuencia"),
                            html.Li("Backup y restauración de calibraciones"),
                            html.Li("Validación de rangos y configuraciones"),
                        ])
                    ],
                    "module-cal",
                    "balance-scale",
                    "success"
                ),
                
                collapsible_section(
                    "pages/simulator/ - Simulador RLC",
                    [
                        html.P("Calculadora de impedancias para circuitos RLC serie/paralelo.", className="text-muted"),
                        html.H6("Capacidades:", className="fw-bold mt-3 mb-2"),
                        html.Ul([
                            html.Li("Cálculo de impedancia compleja Z = R + jX"),
                            html.Li("Conversión a admitancia Y = G + jB"),
                            html.Li("Diagramas de Bode (módulo y fase)"),
                            html.Li("Exportación de datos teóricos"),
                        ])
                    ],
                    "module-sim",
                    "calculator",
                    "info"
                ),
            ]
        ),
        
        # Requisitos
        doc_section(
            "Requisitos del Sistema",
            "cogs",
            [
                html.Div([
                    html.Div([
                        html.H5("Software", className="fw-bold mb-3"),
                        spec_badge("Python", "3.8+ requerido", "primary", "python"),
                        spec_badge("Sistema Operativo", "Linux / Windows / macOS", "secondary", "laptop"),
                        html.H6("Dependencias principales:", className="fw-bold mt-3 mb-2"),
                        html.Ul([
                            html.Li([html.Code("dash"), " - Framework web"]),
                            html.Li([html.Code("dash-spa"), " - Navegación SPA"]),
                            html.Li([html.Code("plotly"), " - Visualización"]),
                            html.Li([html.Code("pyserial"), " - Comunicación serial"]),
                            html.Li([html.Code("pandas"), " - Manipulación de datos"]),
                            html.Li([html.Code("numpy"), " - Cálculos científicos"]),
                        ])
                    ], className="col-md-6 mb-4"),
                    
                    html.Div([
                        html.H5("Hardware", className="fw-bold mb-3"),
                        spec_badge("RAM", "Mínimo 2GB", "warning", "memory"),
                        spec_badge("Almacenamiento", "500MB libres", "info", "hdd"),
                        spec_badge("Puerto Serial", "USB libre", "success", "usb"),
                        html.H6("Navegadores compatibles:", className="fw-bold mt-3 mb-2"),
                        html.Ul([
                            html.Li("Google Chrome 90+"),
                            html.Li("Mozilla Firefox 88+"),
                            html.Li("Microsoft Edge 90+"),
                            html.Li("Safari 14+"),
                        ])
                    ], className="col-md-6 mb-4"),
                ], className="row")
            ]
        ),
        
    ], id="content-software", style={"display": "none"})


def tab_calibration():
    """Contenido de la pestaña Calibración"""
    return html.Div([
        html.Div([
            html.H3([
                html.I(className="fas fa-balance-scale me-3 text-primary"),
                "Procedimiento de Calibración"
            ], className="mb-3 fw-bold"),
            html.P([
                "La calibración es ", html.Strong("crítica"), " para obtener mediciones precisas. ",
                "El sistema ", html.Strong("Open-Short-Load"), " corrige parásitas y asegura trazabilidad."
            ], className="lead text-muted mb-0")
        ], className="p-4 bg-light rounded shadow-sm mb-4"),
        
        info_box([
            html.I(className="fas fa-exclamation-triangle me-2"),
            html.Strong("⚠️ IMPORTANTE: "),
            "Las mediciones sin calibración pueden tener errores superiores al 20%. ",
            "La calibración debe realizarse para cada combinación de frecuencia y ganancia que uses."
        ], "danger"),
        
        doc_section(
            "Fundamentos de Calibración",
            "graduation-cap",
            [
                html.P("El ADMX2001B utiliza calibración de tres puntos:", className="lead mb-4"),
                
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-times-circle fa-3x text-primary mb-3"),
                                html.H5("OPEN", className="fw-bold"),
                                html.P("Corrige capacitancias parásitas de cables y conectores", className="small text-muted")
                            ], className="text-center p-4 border rounded shadow-sm bg-white h-100")
                        ], className="col-md-4 mb-3"),
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-minus fa-3x text-success mb-3"),
                                html.H5("SHORT", className="fw-bold"),
                                html.P("Corrige inductancias parásitas y resistencias de contacto", className="small text-muted")
                            ], className="text-center p-4 border rounded shadow-sm bg-white h-100")
                        ], className="col-md-4 mb-3"),
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-equals fa-3x text-warning mb-3"),
                                html.H5("LOAD", className="fw-bold"),
                                html.P("Proporciona trazabilidad a estándar certificado conocido", className="small text-muted")
                            ], className="text-center p-4 border rounded shadow-sm bg-white h-100")
                        ], className="col-md-4 mb-3"),
                    ], className="row"),
                ]),
                
                html.H5("Orden de Calibración", className="fw-bold mb-3 mt-4"),
                html.Div([
                    html.Span("1", className="badge bg-primary rounded-circle me-2", style={"width": "30px", "height": "30px", "lineHeight": "20px"}),
                    html.Span("OPEN", className="fw-bold me-3"),
                    html.I(className="fas fa-arrow-right me-3 text-muted"),
                    html.Span("2", className="badge bg-success rounded-circle me-2", style={"width": "30px", "height": "30px", "lineHeight": "20px"}),
                    html.Span("SHORT", className="fw-bold me-3"),
                    html.I(className="fas fa-arrow-right me-3 text-muted"),
                    html.Span("3", className="badge bg-warning rounded-circle me-2", style={"width": "30px", "height": "30px", "lineHeight": "20px"}),
                    html.Span("LOAD", className="fw-bold"),
                ], className="p-3 bg-light rounded border d-flex align-items-center justify-content-center flex-wrap"),
                
                info_box([
                    html.Strong("📝 Nota: "),
                    "El SHORT solo es necesario para configuraciones de ganancia de corriente 0 o 1. ",
                    "Para ganancias 2 y 3 (alta impedancia), se puede omitir."
                ], "note"),
            ]
        ),
        
        doc_section(
            "Procedimiento Paso a Paso",
            "list-ol",
            [
                step_card(
                    1,
                    "Preparación del Sistema",
                    [
                        html.P("Configuración inicial antes de calibrar:", className="fw-bold mb-3"),
                        html.Ol([
                            html.Li([
                                "Deshabilitar autorange: ",
                                command_card("setgain ch0 0", "Fijar ganancia de voltaje (ejemplo: 0)"),
                                command_card("setgain ch1 1", "Fijar ganancia de corriente (ejemplo: 1)"),
                            ]),
                            html.Li([
                                "Configurar parámetros de medición: ",
                                command_card("frequency 100", "Frecuencia en kHz (ejemplo: 100kHz)"),
                                command_card("magnitude 1", "Amplitud de señal en V (ejemplo: 1V)"),
                                command_card("offset 0", "Offset DC en V (usualmente 0)"),
                            ]),
                            html.Li([
                                "Aumentar promediado para calibración: ",
                                command_card("average 200", "200-256 muestras para máxima precisión"),
                                command_card("tdelay 200", "Retardo de 200ms para estabilización"),
                            ]),
                            html.Li([
                                "Configurar switches en placa: ",
                                html.Ul([
                                    html.Li([html.Strong("S1"), " → ", html.Span("DUT", className="badge bg-info")]),
                                    html.Li([html.Strong("S2"), " → ", html.Span("GND", className="badge bg-dark")]),
                                ])
                            ]),
                        ], className="ps-3"),
                    ],
                    color="primary"
                ),
                
                step_card(
                    2,
                    "Calibración OPEN",
                    [
                        html.P("Conecta los terminales de medición según se muestra:", className="fw-bold mb-3"),
                        html.Ul([
                            html.Li("H_POT y H_CUR juntos (cable rojo #1)"),
                            html.Li("L_POT y L_CUR juntos (cable negro #1)"),
                            html.Li([html.Strong("NO"), " conectar rojos con negros entre sí"]),
                        ]),
                        command_card(
                            "calibrate open",
                            "Ejecutar calibración open",
                            "0,-1.117998e-09,1.162904e-06\nFrequency = 100.0000kHz\nCal Temp: 41.4 deg C\nopen:Done\nshort:Not Done\nload:Not Done"
                        ),
                        info_box([
                            html.Strong("✓ Verificación: "),
                            "Debe mostrar 'open:Done'. El valor medido representa las parásitas del setup."
                        ], "success"),
                    ],
                    image_src=IMAGES.get('open_config_clips'),
                    image_caption="Configuración OPEN: Terminales H juntos, L juntos, sin conexión entre H y L",
                    color="primary"
                ),
                
                step_card(
                    3,
                    "Calibración SHORT",
                    [
                        html.P("Configuración para impedancia muy baja:", className="fw-bold mb-3"),
                        html.Ul([
                            html.Li(["Reducir magnitud: ", html.Code("magnitude 0.2")]),
                            html.Li("Conectar TODAS las terminales juntas (H_POT, H_CUR, L_POT, L_CUR)"),
                            html.Li("Usar alambre grueso de cobre de longitud mínima (<5cm)"),
                        ]),
                        command_card(
                            "magnitude 0.2",
                            "Reducir amplitud para evitar saturación"
                        ),
                        command_card(
                            "calibrate short",
                            "Ejecutar calibración short",
                            "0,2.075835e-02,1.224807e-02\nFrequency = 100.0000kHz\nCal Temp: 41.4 deg C\nopen:Done\nshort:Done\nload:Not Done"
                        ),
                        info_box([
                            html.Strong("⚠️ Cuándo omitir: "),
                            "Para ganancias de corriente 2 y 3 (impedancias > 10kΩ), el SHORT no es necesario."
                        ], "warning"),
                    ],
                    color="success"
                ),
                
                step_card(
                    4,
                    "Calibración LOAD",
                    [
                        html.P("Conecta un estándar certificado conocido:", className="fw-bold mb-3"),
                        html.Ul([
                            html.Li(["Restaurar magnitud: ", html.Code("magnitude 1")]),
                            html.Li("Seleccionar resistor de precisión 1% o mejor"),
                            html.Li("Valor cercano a impedancia del DUT que medirás"),
                            html.Li("Resistor de 1kΩ es un buen estándar general"),
                        ]),
                        
                        html.H6("Estándares recomendados por rango:", className="fw-bold mb-2 mt-3"),
                        info_table(
                            ["Rango de Impedancia", "Estándar Recomendado", "Tipo"],
                            [
                                ["< 10Ω", "10Ω ±1%", "Resistor metal film"],
                                ["10Ω - 100Ω", "100Ω ±1%", "Resistor metal film"],
                                ["100Ω - 1kΩ", "1kΩ ±1%", "Resistor metal film"],
                                ["1kΩ - 10kΩ", "10kΩ ±1%", "Resistor metal film"],
                                ["> 10kΩ", "100kΩ ±1%", "Resistor metal film"],
                            ]
                        ),
                        
                        command_card(
                            "magnitude 1",
                            "Restaurar amplitud normal"
                        ),
                        command_card(
                            "calibrate rt 1000 xt 0.822",
                            "Calibrar con resistor de 1kΩ (rt=1000Ω, xt=reactancia si existe)",
                            "0,1.010381e+03,-1.254483e+01\nFrequency = 100.0000kHz\nCal Temp: 41.5 deg C\nopen:Done\nshort:Done\nload:Done"
                        ),
                        
                        info_box([
                            html.Strong("📐 Cálculo de reactancia: "),
                            "Para capacitores: xt = -1/(2πfC). Para inductores: xt = 2πfL. Para resistores puros: xt = 0"
                        ], "tip"),
                    ],
                    image_src=IMAGES.get('cal_connections'),
                    image_caption="Conexión del estándar de calibración (resistor) entre los terminales de medición",
                    color="warning"
                ),
                
                step_card(
                    5,
                    "Guardar Calibración",
                    [
                        html.P("Almacenar coeficientes en memoria no volátil:", className="fw-bold mb-3"),
                        command_card(
                            "calibrate commit",
                            "Guardar con timestamp automático (recomendado)",
                            "PASSWORD> Analog123\ncommit : success"
                        ),
                        html.P("O con timestamp personalizado:", className="mt-2"),
                        command_card(
                            "calibrate commit 1689959855",
                            "Guardar con timestamp UNIX específico"
                        ),
                        
                        info_box([
                            html.Strong("🔐 Contraseña: "),
                            "La contraseña por defecto es 'Analog123'. Puedes cambiarla con: ",
                            html.Code("calibrate password")
                        ], "note"),
                        
                        info_box([
                            html.Strong("✅ Verificación: "),
                            "Usa ", html.Code("calibrate list"), " para ver todas las calibraciones guardadas."
                        ], "success"),
                    ],
                    color="info"
                ),
            ]
        ),
        
        doc_section(
            "Calibración Multi-Frecuencia",
            "chart-line",
            [
                html.P([
                    "Desde firmware 1.2.2+, puedes almacenar calibraciones para múltiples frecuencias. ",
                    "El sistema interpolará automáticamente para frecuencias intermedias."
                ], className="lead mb-4"),
                
                html.H5("Comandos de Gestión", className="fw-bold mb-3"),
                command_card("calibrate list", "Lista todas las frecuencias calibradas", "Calibration frequencies:\n1000Hz\n5000Hz\n10000Hz\n100000Hz"),
                command_card("calibrate list 100000", "Lista configuraciones calibradas a 100kHz", "Frequency: 100kHz\nCh0=0, Ch1=0: Done\nCh0=0, Ch1=1: Done\nCh0=0, Ch1=2: Not Done"),
                command_card("calibrate reload", "Recarga calibración de frecuencia más cercana"),
                command_card("resetcal", "Borra calibración actual de RAM (no afecta flash)"),
                command_card("calibrate erase", "⚠️ BORRA TODAS las calibraciones de flash (requiere password)"),
                
                html.H5("Capacidad de Almacenamiento", className="fw-bold mb-3 mt-4"),
                html.Div([
                    spec_badge("Módulos con EEPROM", "25 conjuntos de calibración", "warning"),
                    spec_badge("Módulos con Flash", "450 conjuntos de calibración", "success"),
                ], className="row row-cols-2"),
            ]
        ),
        
    ], id="content-calibration", style={"display": "none"})


def tab_cli():
    """Contenido de la pestaña CLI"""
    return html.Div([
        html.Div([
            html.H3([
                html.I(className="fas fa-terminal me-3 text-primary"),
                "Interfaz de Línea de Comandos (CLI)"
            ], className="mb-3 fw-bold"),
            html.P([
                "El ADMX2001B incluye una poderosa interfaz CLI accesible por UART. ",
                "Todos los comandos están disponibles desde terminales como TeraTerm o desde el terminal integrado de ZORIA."
            ], className="lead text-muted mb-0")
        ], className="p-4 bg-light rounded shadow-sm mb-4"),
        
        doc_section(
            "Comandos Básicos",
            "keyboard",
            [
                collapsible_section(
                    "Identificación y Estado",
                    [
                        command_card("*idn", "Información del dispositivo", "Analog Devices,ADMX2001,v1.3.2,Build RT-2,Apr 18 2024,0x2820d10431c29880"),
                        command_card("help", "Lista todos los comandos disponibles"),
                        command_card("help <comando>", "Ayuda detallada de un comando específico", "Ejemplo: help display"),
                        command_card("selftest", "Ver resultado del último self-test", "PASS: Analog self-test passed"),
                        command_card("selftest run", "Ejecutar self-test nuevamente"),
                    ],
                    "cli-basic-1",
                    default_open=True
                ),
                
                collapsible_section(
                    "Configuración de Medición",
                    [
                        command_card("frequency <valor>", "Configurar frecuencia de medición", "frequency 100 → 100.0000kHz\nRango: 0.2 Hz a 10 MHz"),
                        command_card("magnitude <valor>", "Amplitud de señal de excitación (V)", "magnitude 1 → 1.0000V\nRango: 0 a 2.5V"),
                        command_card("offset <valor>", "Offset DC en voltios", "offset 0.5 → 0.5000V\nRango: -2.5V a +2.5V"),
                        command_card("average <n>", "Número de muestras a promediar", "average 100 → promedia 100 muestras\nRango: 1 a 256"),
                        command_card("count <n>", "Número de mediciones a realizar", "count 10 → realiza 10 lecturas"),
                    ],
                    "cli-basic-2"
                ),
                
                collapsible_section(
                    "Mediciones",
                    [
                        command_card("z", "Realizar medición con configuración actual", "0,5.677640e-13,8.062763e+07\nFormato: index,valor1,valor2"),
                        command_card("initiate", "Entrar en modo trigger (bloquea configuración)", "Se usa antes de trigger para optimizar velocidad"),
                        command_card("trigger", "Ejecutar medición en modo trigger", "Más rápido que 'z' (10-12ms)"),
                        command_card("tcount <n>", "Configurar contador de triggers", "tcount 65536 → modo trigger infinito"),
                        command_card("mdelay <ms>", "Retardo antes de cada medición (ms)", "mdelay 100 → espera 100ms"),
                        command_card("tdelay <ms>", "Retardo después de trigger (ms)", "tdelay 50 → espera 50ms post-trigger"),
                    ],
                    "cli-basic-3"
                ),
            ]
        ),
        
        doc_section(
            "Modos de Display",
            "th-list",
            [
                html.P("El ADMX2001B puede reportar mediciones en 18 formatos diferentes:", className="mb-3"),
                command_card("display <modo>", "Seleccionar modo de display (0-18)"),
                
                info_table(
                    ["Modo", "Descripción", "Formato", "Unidades"],
                    [
                        ["0", "Capacitancia serie + Rs", "Cs, Rs", "F, Ω"],
                        ["1", "Capacitancia serie + D", "Cs, D", "F, adim"],
                        ["2", "Capacitancia serie + Q", "Cs, Q", "F, adim"],
                        ["3", "Inductancia serie + Rs", "Ls, Rs", "H, Ω"],
                        ["4", "Inductancia serie + D", "Ls, D", "H, adim"],
                        ["5", "Inductancia serie + Q", "Ls, Q", "H, adim"],
                        ["6 ★", "Impedancia rectangular", "R, X", "Ω, Ω"],
                        ["7", "Impedancia polar (grados)", "Z, θ°", "Ω, deg"],
                        ["8", "Impedancia polar (rad)", "Z, θ", "Ω, rad"],
                        ["9", "Capacitancia paralelo + Rp", "Cp, Rp", "F, Ω"],
                        ["10", "Capacitancia paralelo + D", "Cp, D", "F, adim"],
                        ["11", "Capacitancia paralelo + Q", "Cp, Q", "F, adim"],
                        ["12", "Inductancia paralelo + Rp", "Lp, Rp", "H, Ω"],
                        ["13", "Inductancia paralelo + D", "Lp, D", "H, adim"],
                        ["14", "Inductancia paralelo + Q", "Lp, Q", "H, adim"],
                        ["15", "Admitancia rectangular", "G, B", "S, S"],
                        ["16", "Admitancia polar (grados)", "Y, θ°", "S, deg"],
                        ["17", "Admitancia polar (rad)", "Y, θ", "S, rad"],
                        ["18", "Apagado", "None", "-"],
                    ]
                ),
                
                info_box([
                    html.Strong("★ Modo 6 (default): "),
                    "Impedancia rectangular R+jX es el formato por defecto y el más versátil para análisis."
                ], "tip"),
            ]
        ),
        
        doc_section(
            "Control de Ganancia",
            "sliders-h",
            [
                html.P("El rango de medición se controla mediante las ganancias de voltaje (Ch0) y corriente (Ch1):", className="mb-3"),
                command_card("setgain ch0 <0-3>", "Ganancia de voltaje (0=±2.5V, 3=±312.5mV)"),
                command_card("setgain ch1 <0-3>", "Ganancia de corriente (0=25mA, 3=25μA)"),
                command_card("setgain auto", "Activar auto-ranging"),
                command_card("setgain", "Ver configuración actual"),
                
                html.H5("Tabla de Ganancias", className="fw-bold mb-3 mt-4"),
                html.Div([
                    html.Div([
                        html.H6("Canal 0 - Voltaje", className="fw-bold mb-2 text-primary"),
                        info_table(
                            ["Ganancia", "Rango Máx", "Factor"],
                            [
                                ["0", "±2.5V", "×1"],
                                ["1", "±1.25V", "×2"],
                                ["2", "±625mV", "×4"],
                                ["3", "±312.5mV", "×8"],
                            ],
                            striped=False
                        )
                    ], className="col-md-6 mb-3"),
                    html.Div([
                        html.H6("Canal 1 - Corriente", className="fw-bold mb-2 text-success"),
                        info_table(
                            ["Ganancia", "I Máx", "Transimpedancia"],
                            [
                                ["0", "25mA", "49.9Ω"],
                                ["1", "2.5mA", "499Ω"],
                                ["2", "250μA", "4.99kΩ"],
                                ["3", "25μA", "49.9kΩ"],
                            ],
                            striped=False
                        )
                    ], className="col-md-6 mb-3"),
                ], className="row"),
                
                html.H5("Rangos Recomendados", className="fw-bold mb-3 mt-4"),
                info_table(
                    ["Ch0", "Ch1", "Rango de Z", "Aplicación Típica"],
                    [
                        ["3", "0", "< 10Ω", "Resistencias muy bajas, ESR"],
                        ["2", "0", "< 25Ω", "Resistencias bajas"],
                        ["1", "0", "< 50Ω", "Impedancias bajas"],
                        ["0", "0", "100Ω - 1kΩ", "Rango medio-bajo"],
                        ["0", "1", "1kΩ - 10kΩ", "Rango medio (uso general)"],
                        ["0", "2", "10kΩ - 100kΩ", "Rango medio-alto"],
                        ["0", "3", "> 100kΩ", "Altas impedancias"],
                    ]
                ),
            ]
        ),
        
        doc_section(
            "Barridos Paramétricos",
            "chart-line",
            [
                html.P("Realizar barridos automáticos de frecuencia, DC bias o magnitud:", className="mb-3"),
                
                command_card("sweep_type frequency <inicio> <fin>", "Barrido de frecuencia (kHz)", "sweep_type frequency 1 1000\nBarrer de 1kHz a 1MHz"),
                command_card("sweep_type magnitude <inicio> <fin>", "Barrido de amplitud (V)"),
                command_card("sweep_type offset <inicio> <fin>", "Barrido de DC bias (V)"),
                command_card("sweep_scale <log|linear>", "Escala logarítmica o lineal", "sweep_scale log → espaciado logarítmico"),
                command_card("count <n>", "Número de puntos del barrido", "count 50 → 50 puntos en el barrido"),
                
                html.H6("Ejemplo completo:", className="fw-bold mt-4 mb-2"),
                html.Pre([
                    "ADMX2001> frequency 1\n",
                    "ADMX2001> count 21\n",
                    "ADMX2001> sweep_type frequency 1 1000\n",
                    "ADMX2001> sweep_scale log\n",
                    "ADMX2001> z\n",
                    "1.000000e+03,5.683433e-13,8.149236e+07\n",
                    "1.258925e+03,5.704062e-13,4.727518e+07\n",
                    "...\n"
                ], className="bg-dark text-success p-3 rounded small font-monospace"),
                
                info_box([
                    html.Strong("📊 Formato de salida: "),
                    "En modo sweep, la primera columna es el parámetro barrido, ",
                    "seguido de los valores de medición en el formato de display seleccionado."
                ], "info"),
            ]
        ),
        
    ], id="content-cli", style={"display": "none"})


def tab_firmware():
    """Contenido de la pestaña Firmware"""
    return html.Div([
        html.Div([
            html.H3([
                html.I(className="fas fa-microchip me-3 text-primary"),
                "Actualización de Firmware"
            ], className="mb-3 fw-bold"),
            html.P([
                "El firmware del ADMX2001B es actualizable por el usuario. ",
                "Las actualizaciones aportan mejoras de rendimiento, nuevas funciones y correcciones."
            ], className="lead text-muted mb-0")
        ], className="p-4 bg-light rounded shadow-sm mb-4"),
        
        info_box([
            html.I(className="fas fa-exclamation-triangle me-2"),
            html.Strong("⚠️ ADVERTENCIA CRÍTICA: "),
            "La actualización puede ", html.Strong("borrar todas las calibraciones"), " guardadas. ",
            "Haz ", html.Strong("respaldo completo"), " antes de proceder."
        ], "danger"),
        
        doc_section(
            "Versiones de Firmware",
            "code-branch",
            [
                html.H5("Historial de Versiones", className="fw-bold mb-3"),
                info_table(
                    ["Versión", "Estado", "Características Principales"],
                    [
                        ["1.3.2", "Estable ★", "Optimizaciones de tiempo, correcciones menores, GUI Python"],
                        ["1.3.1", "Estable", "Mejoras sustanciales de ruido, múltiples correcciones"],
                        ["1.2.4", "Estable", "Script de instalación, mismo firmware que 1.2.2"],
                        ["1.2.2", "Estable", "Calibración multi-frecuencia, salidas digitales, trigger externo"],
                        ["1.2.0", "Estable", "Correcciones, mejoras de ruido y repetibilidad"],
                        ["1.1.1", "Legacy", "Correcciones, no compatible con placas con flash"],
                        ["1.1.0", "Legacy", "Interfaz SPI, self-test integrado"],
                        ["1.0.x", "Legacy", "Versiones iniciales"],
                    ]
                ),
                
                html.H5("Beneficios de Actualizar", className="fw-bold mb-3 mt-4"),
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-tachometer-alt fa-2x text-success mb-2"),
                            html.H6("Velocidad", className="fw-bold"),
                            html.P("Mediciones 30% más rápidas en modo trigger", className="small text-muted mb-0")
                        ], className="text-center p-3 border rounded bg-white shadow-sm")
                    ], className="col-md-3 mb-3"),
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-chart-line fa-2x text-primary mb-2"),
                            html.H6("Precisión", className="fw-bold"),
                            html.P("Reducción significativa de ruido", className="small text-muted mb-0")
                        ], className="text-center p-3 border rounded bg-white shadow-sm")
                    ], className="col-md-3 mb-3"),
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-tools fa-2x text-warning mb-2"),
                            html.H6("Funciones", className="fw-bold"),
                            html.P("Nuevas capacidades y comandos", className="small text-muted mb-0")
                        ], className="text-center p-3 border rounded bg-white shadow-sm")
                    ], className="col-md-3 mb-3"),
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-shield-alt fa-2x text-info mb-2"),
                            html.H6("Estabilidad", className="fw-bold"),
                            html.P("Corrección de bugs conocidos", className="small text-muted mb-0")
                        ], className="text-center p-3 border rounded bg-white shadow-sm")
                    ], className="col-md-3 mb-3"),
                ], className="row"),
            ]
        ),
        
        doc_section(
            "Requisitos",
            "list-check",
            [
                html.H5("Hardware Necesario", className="fw-bold mb-3"),
                html.Ul([
                    html.Li([html.I(className="fas fa-check text-success me-2"), "Placa EVAL-ADMX2001EBZ"]),
                    html.Li([html.I(className="fas fa-check text-success me-2"), "Módulo ADMX2001B instalado"]),
                    html.Li([html.I(className="fas fa-exclamation-circle text-warning me-2"), html.Strong("Intel Altera USB Blaster"), " (programador JTAG)"]),
                    html.Li([html.I(className="fas fa-check text-success me-2"), "Adaptador de corriente 9VDC"]),
                    html.Li([html.I(className="fas fa-check text-success me-2"), "PC con puerto USB disponible"]),
                ]),
                
                html.H5("Software Requerido", className="fw-bold mb-3 mt-4"),
                html.Ul([
                    html.Li([html.Strong("Python 3.7+"), " (para ejecutar script de actualización)"]),
                    html.Li([html.Strong("Intel Quartus Prime Programmer"), " (versión 23.1+ recomendada)"]),
                    html.Li(["Drivers para ", html.Strong("Altera USB Blaster")]),
                    html.Li([html.Strong("pyserial"), " (", html.Code("pip install pyserial"), ")"]),
                ]),
                
                info_box([
                    html.Strong("📦 Descarga de Quartus Prime: "),
                    html.A("Intel Website", 
                          href="https://www.intel.com/content/www/us/en/software-kit/785086/", 
                          target="_blank", className="btn btn-sm btn-primary ms-2"),
                    html.Br(),
                    "Solo necesitas el componente 'Programmer And Tools' (~4GB), no el IDE completo."
                ], "info"),
            ]
        ),
        
        doc_section(
            "Procedimiento de Actualización",
            "clipboard-list",
            [
                step_card(
                    1,
                    "Respaldo de Calibraciones",
                    [
                        html.P([
                            html.Strong("CRÍTICO: "), 
                            "Guarda TODAS tus calibraciones antes de continuar."
                        ], className="text-danger fw-bold mb-3"),
                        
                        command_card("calibrate list", "Listar todas las frecuencias calibradas"),
                        html.P("Para cada frecuencia listada:", className="mt-2"),
                        command_card("calibrate list 1000", "Ver configuraciones calibradas a esa frecuencia"),
                        command_card("rdcal 0 1", "Leer coeficientes de una configuración específica"),
                        
                        info_box([
                            html.Strong("💾 Recomendación: "),
                            "Copia y pega toda la salida en un archivo de texto. ",
                            "También puedes usar el comando de backup de ZORIA."
                        ], "warning"),
                    ],
                    color="danger"
                ),
                
                step_card(
                    2,
                    "Obtener Firmware",
                    [
                        html.P("Contacta al soporte de Analog Devices:"),
                        html.Div([
                            html.Strong("Email: "),
                            html.A("admx-support@analog.com", 
                                  href="mailto:admx-support@analog.com",
                                  className="btn btn-primary ms-2")
                        ], className="mb-3"),
                        
                        html.P("Solicita:", className="fw-bold mt-3"),
                        html.Ul([
                            html.Li("Paquete de firmware versión 1.3.2"),
                            html.Li("Archivo .pof (Program Object File)"),
                            html.Li("Script admx2001_flash_pof.py"),
                            html.Li("Notas de release y changelog"),
                        ]),
                        
                        html.P("Recibirás un archivo comprimido con estructura:", className="fw-bold mt-3"),
                        html.Pre([
                            "Admx2001Firmware-Rel1.3.2/\n",
                            "├── Firmware/\n",
                            "│   └── admx_lcr_encrypted.pof\n",
                            "├── admx2001_flash_pof.py\n",
                            "├── GUI/\n",
                            "├── README.txt\n",
                            "└── RELEASE_NOTES.txt\n"
                        ], className="bg-dark text-info p-3 rounded small font-monospace"),
                    ],
                    color="info"
                ),
                
                step_card(
                    3,
                    "Conectar Hardware",
                    [
                        html.Ol([
                            html.Li("Conecta la placa EVAL-ADMX2001EBZ al adaptador 9VDC y enciéndela"),
                            html.Li("Conecta el USB Blaster al puerto JTAG de la placa"),
                            html.Li("Conecta el USB Blaster a tu PC"),
                            html.Li("Verifica que el USB Blaster sea detectado:"),
                        ]),
                        
                        html.Div([
                            html.Strong("Windows:", className="me-2"),
                            "Debe aparecer en Administrador de Dispositivos"
                        ], className="mb-2"),
                        html.Div([
                            html.Strong("Linux:", className="me-2"),
                            html.Code("lsusb | grep Altera")
                        ], className="mb-2"),
                        
                        info_box([
                            html.Strong("🔌 Problema de detección: "),
                            "En Linux, puede requerir configuración de udev rules. ",
                            "Consulta la documentación de Quartus Prime."
                        ], "warning"),
                    ],
                    color="warning"
                ),
                
                step_card(
                    4,
                    "Ejecutar Actualización",
                    [
                        html.P("Navega a la carpeta del firmware y ejecuta:", className="mb-3"),
                        html.Pre([
                            'cd Admx2001Firmware-Rel1.3.2\n',
                            'python admx2001_flash_pof.py --pof "Firmware/admx_lcr_encrypted.pof"\n'
                        ], className="bg-dark text-success p-3 rounded font-monospace"),
                        
                        html.P("El script automáticamente:", className="fw-bold mt-3"),
                        html.Ul([
                            html.Li("Detecta el USB Blaster"),
                            html.Li("Carga el firmware al ADMX2001B"),
                            html.Li("Verifica la programación"),
                            html.Li("Reporta éxito o errores"),
                        ]),
                        
                        html.P("Duración: 20-30 segundos", className="text-muted mt-2"),
                        
                        info_box([
                            html.I(className="fas fa-exclamation-triangle me-2"),
                            html.Strong("⚠️ NO interrumpir: "),
                            "No desconectes la placa ni el USB Blaster durante el proceso. ",
                            "Interrumpir puede dañar el firmware."
                        ], "danger"),
                    ],
                    color="success"
                ),
                
                step_card(
                    5,
                    "Verificación",
                    [
                        html.P("Después de la actualización:", className="mb-3"),
                        html.Ol([
                            html.Li("Desconecta el USB Blaster"),
                            html.Li("Reinicia la placa (ciclo de alimentación)"),
                            html.Li("Conecta mediante UART"),
                            html.Li("Verifica la versión:"),
                        ]),
                        
                        command_card("*idn", "Ver información del dispositivo", "Debe mostrar firmware 1.3.2"),
                        command_card("selftest", "Verificar que el self-test pase"),
                        
                        html.P("Restaura tus calibraciones usando el respaldo.", className="fw-bold text-warning mt-3"),
                    ],
                    color="primary"
                ),
            ]
        ),
        
    ], id="content-firmware", style={"display": "none"})


def tab_support():
    """Contenido de la pestaña Soporte"""
    return html.Div([
        html.Div([
            html.H3([
                html.I(className="fas fa-question-circle me-3 text-primary"),
                "Soporte y Recursos"
            ], className="mb-3 fw-bold"),
            html.P([
                "Información de contacto, recursos adicionales y solución de problemas comunes."
            ], className="lead text-muted mb-0")
        ], className="p-4 bg-light rounded shadow-sm mb-4"),
        
        doc_section(
            "Canales de Soporte",
            "headset",
            [
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-envelope fa-3x text-primary mb-3"),
                            html.H5("Email Oficial", className="fw-bold"),
                            html.P("Soporte técnico de Analog Devices", className="text-muted mb-3"),
                            html.A([
                                html.I(className="fas fa-paper-plane me-2"),
                                "admx-support@analog.com"
                            ], href="mailto:admx-support@analog.com", className="btn btn-primary btn-lg")
                        ], className="text-center p-4 border rounded shadow-sm bg-white h-100")
                    ], className="col-md-6 mb-4"),
                    
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-book fa-3x text-success mb-3"),
                            html.H5("Wiki Oficial", className="fw-bold"),
                            html.P("Documentación y guías de Analog Devices", className="text-muted mb-3"),
                            html.A([
                                html.I(className="fas fa-external-link-alt me-2"),
                                "Wiki ADMX2001"
                            ], href="https://wiki.analog.com/resources/eval/user-guides/admx/eval-admx2001ebz", 
                               target="_blank", className="btn btn-success btn-lg")
                        ], className="text-center p-4 border rounded shadow-sm bg-white h-100")
                    ], className="col-md-6 mb-4"),
                ], className="row"),
            ]
        ),
        
        doc_section(
            "Recursos Adicionales",
            "link",
            [
                html.H5("Software y Drivers", className="fw-bold mb-3"),
                html.Ul([
                    html.Li([
                        html.A("Drivers FTDI VCP", href="https://www.ftdichip.com/Drivers/VCP.htm", target="_blank"),
                        " - Virtual COM Port para cable USB-UART"
                    ]),
                    html.Li([
                        html.A("TeraTerm", href="https://github.com/TeraTermProject/teraterm/releases", target="_blank"),
                        " - Emulador de terminal recomendado"
                    ]),
                    html.Li([
                        html.A("Intel Quartus Prime", href="https://www.intel.com/content/www/us/en/software-kit/785086/", target="_blank"),
                        " - Para actualización de firmware"
                    ]),
                ]),
                
                html.H5("Comunidad ZORIA", className="fw-bold mb-3 mt-4"),
                html.Ul([
                    html.Li([
                        html.A("GitHub Repository", href="https://github.com/mario1027/ZORIA", target="_blank"),
                        " - Código fuente, issues y contribuciones"
                    ]),
                    html.Li([
                        html.A("GitHub Discussions", href="https://github.com/mario1027/ZORIA/discussions", target="_blank"),
                        " - Foro de la comunidad"
                    ]),
                ]),
            ]
        ),
        
        doc_section(
            "Problemas Comunes",
            "wrench",
            [
                collapsible_section(
                    "No se detecta el puerto serial",
                    [
                        html.P("Soluciones:", className="fw-bold mb-2"),
                        html.Ul([
                            html.Li("Verifica que los drivers FTDI estén instalados"),
                            html.Li(["En Linux, agrega tu usuario al grupo 'dialout': ", html.Code("sudo usermod -a -G dialout $USER")]),
                            html.Li("Reinicia la aplicación después de conectar el cable"),
                            html.Li("Prueba con otro puerto USB"),
                            html.Li("Verifica el cable USB-UART (puede estar dañado)"),
                        ])
                    ],
                    "faq-1",
                    "usb",
                    "warning",
                    default_open=True
                ),
                
                collapsible_section(
                    "LED de self-test en rojo",
                    [
                        html.P("Causas posibles:", className="fw-bold mb-2"),
                        html.Ul([
                            html.Li("Switches S1/S2 no en posición OPEN/GND para self-test"),
                            html.Li("Módulo ADMX2001B no insertado correctamente"),
                            html.Li("Firmware corrupto o faltante"),
                            html.Li("Problema de alimentación (verificar adaptador 9VDC)"),
                        ]),
                        html.P("Solución:", className="fw-bold mt-2 mb-2"),
                        html.Ol([
                            html.Li("Posicionar switches en OPEN y GND"),
                            html.Li("Reiniciar la placa"),
                            html.Li(["Ejecutar: ", html.Code("selftest run")]),
                        ])
                    ],
                    "faq-2",
                    "lightbulb",
                    "danger"
                ),
                
                collapsible_section(
                    "Mediciones inconsistentes",
                    [
                        html.P("Verificaciones:", className="fw-bold mb-2"),
                        html.Ul([
                            html.Li([html.Strong("Calibración: "), "¿Está calibrado para la frecuencia y ganancia actuales?"]),
                            html.Li([html.Strong("Cables: "), "¿Están en buen estado? ¿Introducen capacitancia parásita?"]),
                            html.Li([html.Strong("Promediado: "), "Aumenta 'average' a 100-200 para reducir ruido"]),
                            html.Li([html.Strong("Rango: "), "¿La ganancia es apropiada para la impedancia del DUT?"]),
                            html.Li([html.Strong("Frecuencia: "), "¿Está dentro del rango óptimo del DUT?"]),
                        ])
                    ],
                    "faq-3",
                    "chart-line",
                    "info"
                ),
                
                collapsible_section(
                    "Error al actualizar firmware",
                    [
                        html.P("Soluciones:", className="fw-bold mb-2"),
                        html.Ul([
                            html.Li("Verifica que Quartus Prime esté instalado y en PATH"),
                            html.Li("Confirma que el USB Blaster esté conectado y detectado"),
                            html.Li("En Linux, configura udev rules para USB Blaster"),
                            html.Li("Reinicia la placa y reintenta"),
                            html.Li(["Contacta ", html.A("admx-support@analog.com", href="mailto:admx-support@analog.com"), " si persiste"]),
                        ])
                    ],
                    "faq-4",
                    "microchip",
                    "danger"
                ),
            ]
        ),
        
        doc_section(
            "Equipo de Desarrollo",
            "users",
            [
                html.P("ZORIA es desarrollado y mantenido por:", className="mb-3"),
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-user-circle fa-3x text-primary mb-2"),
                            html.H6("Mario Ricardo Montero", className="fw-bold"),
                            html.P("Lead Developer", className="text-muted small mb-0")
                        ], className="text-center p-3 border rounded bg-white shadow-sm")
                    ], className="col-md-4 mb-3"),
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-user-circle fa-3x text-success mb-2"),
                            html.H6("Juan Carlos Alvarez", className="fw-bold"),
                            html.P("Developer", className="text-muted small mb-0")
                        ], className="text-center p-3 border rounded bg-white shadow-sm")
                    ], className="col-md-4 mb-3"),
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-user-circle fa-3x text-info mb-2"),
                            html.H6("Francisco J. Racedo N.", className="fw-bold"),
                            html.P("Developer", className="text-muted small mb-0")
                        ], className="text-center p-3 border rounded bg-white shadow-sm")
                    ], className="col-md-4 mb-3"),
                ], className="row"),
                
                html.Hr(className="my-4"),
                
                html.P([
                    "Agradecimientos especiales a ",
                    html.Strong("Analog Devices"),
                    " por el soporte técnico y documentación del ADMX2001."
                ], className="text-center text-muted"),
            ]
        ),
        
    ], id="content-support", style={"display": "none"})


# ==================== LAYOUT PRINCIPAL ====================

def layout():
    """Layout principal de la página de documentación"""
    return html.Div([
        mobileNavBar(),
        html.Div([
            sideBar(),
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
                                html.Strong("ZORIA", className="text-primary"),
                                " y el analizador de impedancia ",
                                html.Strong("EVAL-ADMX2001", className="text-success")
                            ], className="text-muted mb-0 fs-5")
                        ], className="col-12 col-md-8 mb-3 mb-md-0"),
                        html.Div([
                            html.A([
                                html.I(className="fas fa-external-link-alt me-2"),
                                "Wiki Analog"
                            ], href="https://wiki.analog.com/resources/eval/user-guides/admx/eval-admx2001ebz", 
                               target="_blank", className="btn btn-outline-primary me-2 shadow-sm"),
                            html.Span([
                                html.I(className="fas fa-code-branch me-2"),
                                "v1.3.2"
                            ], className="badge bg-success px-3 py-2 fs-6 shadow-sm")
                        ], className="col-12 col-md-4 d-flex justify-content-md-end align-items-center flex-wrap gap-2")
                    ], className="row align-items-center py-4 mb-4 bg-gradient border-bottom border-3 border-primary rounded shadow"),

                    # Navegación por pestañas mejorada
                    html.Div([
                        html.Div([
                            html.Button([
                                html.I(className="fas fa-rocket me-2"),
                                "Inicio Rápido"
                            ], id="btn-quickstart", className="btn btn-primary active me-2 mb-2 fw-bold shadow-sm"),
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
                                html.I(className="fas fa-microchip me-2"),
                                "Firmware"
                            ], id="btn-firmware", className="btn btn-outline-primary me-2 mb-2 fw-bold"),
                            html.Button([
                                html.I(className="fas fa-question-circle me-2"),
                                "Soporte"
                            ], id="btn-support", className="btn btn-outline-primary me-2 mb-2 fw-bold"),
                        ], className="nav-pills-container p-3 bg-white rounded shadow border")
                    ], className="mb-4"),

                    # Contenido de las pestañas
                    html.Div([
                        tab_quickstart(),
                        tab_hardware(),
                        tab_software(),
                        tab_calibration(),
                        tab_cli(),
                        tab_firmware(),
                        tab_support(),
                    ], className="container-fluid px-0")
                    
                ], className="container py-4 px-4", style={"maxWidth": "1400px"})
            ], className="main-content w-100")
        ], className="d-flex flex-grow-1"),
        footer(),
        floating_terminal_button()
    ], className="d-flex flex-column min-vh-100")


@callback(
    [Output('btn-quickstart', 'className'),
     Output('btn-hardware', 'className'),
     Output('btn-software', 'className'),
     Output('btn-calibration', 'className'),
     Output('btn-cli', 'className'),
     Output('btn-firmware', 'className'),
     Output('btn-support', 'className'),
     Output('content-quickstart', 'style'),
     Output('content-hardware', 'style'),
     Output('content-software', 'style'),
     Output('content-calibration', 'style'),
     Output('content-cli', 'style'),
     Output('content-firmware', 'style'),
     Output('content-support', 'style')],
    [Input('btn-quickstart', 'n_clicks'),
     Input('btn-hardware', 'n_clicks'),
     Input('btn-software', 'n_clicks'),
     Input('btn-calibration', 'n_clicks'),
     Input('btn-cli', 'n_clicks'),
     Input('btn-firmware', 'n_clicks'),
     Input('btn-support', 'n_clicks')]
)
def update_tabs(n1, n2, n3, n4, n5, n6, n7):
    from dash import ctx
    button_id = ctx.triggered_id if ctx.triggered_id else 'btn-quickstart'
    
    base = "btn btn-outline-primary me-2 mb-2 fw-bold"
    active = "btn btn-primary active me-2 mb-2 fw-bold shadow-sm"
    
    tabs = {
        'btn-quickstart': 0, 
        'btn-hardware': 1, 
        'btn-software': 2,
        'btn-calibration': 3, 
        'btn-cli': 4,
        'btn-firmware': 5,
        'btn-support': 6
    }
    active_idx = tabs.get(button_id, 0)
    
    buttons = [base] * 7
    buttons[active_idx] = active
    
    contents = [{"display": "none"}] * 7
    contents[active_idx] = {"display": "block"}
    
    return buttons + contents
