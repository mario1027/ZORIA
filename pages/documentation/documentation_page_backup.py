"""
Página de Documentación Oficial ZORIA
Documentación completa para EVAL-ADMX2001
"""
from dash import html, dcc, Input, Output, callback
from dash_spa import register_page

from pages.common.sidebar import sideBar
from pages.common.mobile_nav import mobileNavBar
from pages.common.footer import footer
from pages.common.floating_terminal_button import floating_terminal_button

register_page(__name__, path='/documentacion', title='Documentación - ZORIA')

IMAGES = {
    'basic_connections': 'https://wiki.analog.com/lib/exe/fetch.php?media=resources:eval:user-guides:admx:eval-admx2001ebz_basic_connections_labeled.png',
    'open_load': 'https://wiki.analog.com/lib/exe/fetch.php?media=resources:eval:user-guides:admx:open_load.png',
    'bnc_load': 'https://wiki.analog.com/lib/exe/fetch.php?media=resources:eval:user-guides:admx:bnc_load.png',
    'photo_setup': 'https://wiki.analog.com/lib/exe/fetch.php?media=resources:eval:user-guides:admx:photo_setup_labeled.jpg',
    'cal_connections': 'https://wiki.analog.com/lib/exe/fetch.php?media=resources:eval:user-guides:admx:cal_connections_5.jpg',
    'open_config_clips': 'https://wiki.analog.com/lib/exe/fetch.php?media=resources:eval:user-guides:admx:open_config_test_clips_2.png',
    'uart_connection': 'https://wiki.analog.com/lib/exe/fetch.php?media=resources:eval:user-guides:admx:img_0937.jpg',
    'dev_mgr_vcp': 'https://wiki.analog.com/lib/exe/fetch.php?media=resources:eval:user-guides:admx:dev_mgr_vcp_installed.png',
}


def layout():
    return html.Div([
        mobileNavBar(),
        html.Div([
            sideBar(),
            html.Main([
                html.Div([
                    # Header
                    html.Div([
                        html.H1([
                            html.I(className="fas fa-book-open me-3 text-primary"),
                            "Documentación Oficial"
                        ], className="display-5 fw-bold mb-3"),
                        html.P([
                            "Guía completa del sistema EVAL-ADMX2001 + ZORIA"
                        ], className="lead mb-2"),
                        html.P("Hardware Rev. B/C | Firmware 1.3.1 - 1.3.3", className="text-muted small")
                    ], className="mb-5 pb-3 border-bottom"),
                    
                    dcc.Store(id='doc-active-tab', data='quickstart', storage_type='session'),
                    
                    # Navigation Tabs
                    html.Div([
                        html.Button([
                            html.I(className="fas fa-rocket me-2"), "Inicio Rápido"
                        ], id="btn-quickstart", className="btn btn-primary active me-2 mb-2 fw-bold"),
                        html.Button([
                            html.I(className="fas fa-box-open me-2"), "Kit de Evaluación"
                        ], id="btn-hardware", className="btn btn-outline-primary me-2 mb-2 fw-bold"),
                        html.Button([
                            html.I(className="fas fa-balance-scale me-2"), "Calibración"
                        ], id="btn-calibration", className="btn btn-outline-primary me-2 mb-2 fw-bold"),
                        html.Button([
                            html.I(className="fas fa-terminal me-2"), "Comandos CLI"
                        ], id="btn-cli", className="btn btn-outline-primary me-2 mb-2 fw-bold"),
                        html.Button([
                            html.I(className="fas fa-headset me-2"), "Soporte"
                        ], id="btn-support", className="btn btn-outline-primary me-2 mb-2 fw-bold"),
                    ], className="nav-pills mb-5 p-3 bg-light rounded-3 border"),
                    
                    # TAB 1: INICIO RÁPIDO
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-exclamation-triangle fa-2x text-warning me-3"),
                            html.Div([
                                html.H5("Importante", className="fw-bold mb-1"),
                                html.P("Se requieren AMBOS productos: ADMX2001B + EVAL-ADMX2001EBZ (vendidos por separado)", className="mb-0")
                            ])
                        ], className="alert alert-warning border-start border-4 border-warning d-flex py-4 mb-4"),
                        
                        html.H3("5 Pasos para Comenzar", className="mb-4 fw-bold"),
                        
                        # Step 1
                        html.Div([
                            html.Div([
                                html.Span("1", className="badge bg-primary rounded-circle fs-3 px-3 py-2"),
                            ], className="me-3"),
                            html.H4("Instalar Drivers FTDI VCP", className="fw-bold mb-0 mt-2")
                        ], className="d-flex align-items-center mb-3"),
                        html.Div([
                            html.P("Instala los drivers Virtual COM Port para el cable USB-UART incluido."),
                            html.A([
                                html.I(className="fas fa-download me-2"), "Descargar Drivers FTDI"
                            ], href="https://www.ftdichip.com/Drivers/VCP.htm", target="_blank", className="btn btn-primary btn-lg mb-3"),
                            html.Img(src=IMAGES['dev_mgr_vcp'], className="img-fluid rounded shadow mb-3", style={"maxHeight": "300px"}),
                            html.P("Verifica en Administrador de Dispositivos que aparezca el puerto COM.", className="text-muted fst-italic")
                        ], className="ps-5 mb-5"),
                        
                        # Step 2
                        html.Div([
                            html.Div([
                                html.Span("2", className="badge bg-success rounded-circle fs-3 px-3 py-2"),
                            ], className="me-3"),
                            html.H4("Configuración del Hardware", className="fw-bold mb-0 mt-2")
                        ], className="d-flex align-items-center mb-3"),
                        html.Div([
                            html.Ol([
                                html.Li(["Inserta el módulo ", html.Strong("ADMX2001B"), " en la placa (conectores codificados)"]),
                                html.Li(["Interruptores S1/S2 a posición ", html.Strong("OPEN"), " y ", html.Strong("GND")]),
                                html.Li("Conecta adaptador 9VDC"),
                                html.Li([html.Strong("Verifica LED:"), " Verde=OK, Verde/Rojo=Self-test falló, Rojo=Error grave"]),
                                html.Li("Cable UART: TX(naranja)→TX, RX(amarillo)→RX, GND(negro)→GND"),
                            ], className="fs-5"),
                            html.Img(src=IMAGES['basic_connections'], className="img-fluid rounded shadow mb-3", style={"maxHeight": "350px"}),
                            html.Div([
                                html.I(className="fas fa-info-circle me-2"),
                                "Jumper CLK_SEL debe estar en INT (reloj interno)"
                            ], className="alert alert-info")
                        ], className="ps-5 mb-5"),
                        
                        # Step 3
                        html.Div([
                            html.Div([
                                html.Span("3", className="badge bg-info rounded-circle fs-3 px-3 py-2"),
                            ], className="me-3"),
                            html.H4("Configuración para Medición", className="fw-bold mb-0 mt-2")
                        ], className="d-flex align-items-center mb-3"),
                        html.Div([
                            html.Ol([
                                html.Li(["Cambia interruptores a posición ", html.Strong("DUT"), " y ", html.Strong("GND")]),
                                html.Li([html.Span("Cables ROJOS", className="text-danger fw-bold"), " → HCUR/HPOT"]),
                                html.Li([html.Span("Cables NEGROS", className="text-dark fw-bold"), " → LPOT/LCUR"]),
                            ], className="fs-5"),
                            html.Img(src=IMAGES['photo_setup'], className="img-fluid rounded shadow mb-3", style={"maxHeight": "300px"}),
                            html.Div([
                                html.I(className="fas fa-exclamation-triangle me-2"),
                                "Inspecciona los clips BNC: el housing puede desenroscarse y evitar buen contacto"
                            ], className="alert alert-warning")
                        ], className="ps-5 mb-5"),
                        
                        # Alerta final
                        html.Div([
                            html.I(className="fas fa-exclamation-circle fa-2x text-danger me-3"),
                            html.Div([
                                html.H5("Calibración Requerida", className="fw-bold mb-1"),
                                html.P("Las mediciones NO serán precisas hasta completar calibración OPEN-SHORT-LOAD", className="mb-0")
                            ])
                        ], className="alert alert-danger border-start border-4 border-danger d-flex py-4"),
                        
                    ], id="content-quickstart"),
                    
                    # TAB 2: HARDWARE
                    html.Div([
                        html.H3("Contenido del Kit", className="mb-4 fw-bold"),
                        html.Div([
                            html.Div([
                                html.H5("Incluido:", className="fw-bold text-success"),
                                html.Ul([
                                    html.Li("EVAL-ADMX2001EBZ - Placa evaluación"),
                                    html.Li("Cable UART-USB (TTL-232R-RPI)"),
                                    html.Li("Adaptador 9VDC"),
                                    html.Li("Clips de prueba LCR"),
                                ], className="fs-5")
                            ], className="col-md-6 mb-4"),
                            html.Div([
                                html.H5("Requerido (separado):", className="fw-bold text-primary"),
                                html.Ul([
                                    html.Li("ADMX2001B - Módulo de análisis"),
                                ], className="fs-5"),
                                html.H6("Opcional:", className="fw-bold mt-3"),
                                html.Ul([
                                    html.Li("Estándares de calibración certificados"),
                                ])
                            ], className="col-md-6 mb-4"),
                        ], className="row mb-5"),
                        
                        html.H3("Especificaciones Técnicas", className="mb-4 fw-bold"),
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Div([
                                        html.I(className="fas fa-microchip me-2"),
                                        "ADMX2001B"
                                    ], className="card-header bg-primary text-white fw-bold"),
                                    html.Div([
                                        html.Ul([
                                            html.Li("Tamaño: 1.5 × 2.5 pulgadas"),
                                            html.Li("Frecuencia: 0.2 Hz - 10 MHz"),
                                            html.Li("Resolución ADC: 18 bits"),
                                            html.Li("Alimentación: 3.3V única"),
                                            html.Li("Interfaces: UART + SPI"),
                                            html.Li("18 modos de display SI"),
                                        ], className="list-unstyled mb-0")
                                    ], className="card-body")
                                ], className="card border-0 shadow h-100")
                            ], className="col-md-6 mb-4"),
                            html.Div([
                                html.Div([
                                    html.Div([
                                        html.I(className="fas fa-plug me-2"),
                                        "EVAL-ADMX2001EBZ"
                                    ], className="card-header bg-success text-white fw-bold"),
                                    html.Div([
                                        html.Ul([
                                            html.Li("Conectores BNC estándar"),
                                            html.Li("Interfaz UART con cable USB"),
                                            html.Li("Señales trigger/clock SMA"),
                                            html.Li("Headers estilo Arduino"),
                                            html.Li("Entrada 5V-12V"),
                                            html.Li("LED self-test bicolor"),
                                        ], className="list-unstyled mb-0")
                                    ], className="card-body")
                                ], className="card border-0 shadow h-100")
                            ], className="col-md-6 mb-4"),
                        ], className="row mb-5"),
                        
                        html.H3("Terminales 4-Wire Kelvin", className="mb-4 fw-bold"),
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.I(className="fas fa-arrow-up text-danger fa-2x mb-2"),
                                    html.H5("H_CUR", className="text-danger fw-bold mb-1"),
                                    html.P("High Current Source", className="small text-muted mb-0"),
                                    html.P("±5V @ 50mA", className="small fw-bold")
                                ], className="text-center p-3 border rounded bg-danger bg-opacity-10 h-100")
                            ], className="col-6 col-md-3 mb-3"),
                            html.Div([
                                html.Div([
                                    html.I(className="fas fa-arrow-up text-warning fa-2x mb-2"),
                                    html.H5("H_POT", className="text-warning fw-bold mb-1"),
                                    html.P("High Potential Sense", className="small text-muted mb-0"),
                                    html.P("Conectar con H_CUR", className="small text-muted")
                                ], className="text-center p-3 border rounded bg-warning bg-opacity-10 h-100")
                            ], className="col-6 col-md-3 mb-3"),
                            html.Div([
                                html.Div([
                                    html.I(className="fas fa-arrow-down text-info fa-2x mb-2"),
                                    html.H5("L_POT", className="text-info fw-bold mb-1"),
                                    html.P("Low Potential Sense", className="small text-muted mb-0"),
                                    html.P("Conectar con L_CUR", className="small text-muted")
                                ], className="text-center p-3 border rounded bg-info bg-opacity-10 h-100")
                            ], className="col-6 col-md-3 mb-3"),
                            html.Div([
                                html.Div([
                                    html.I(className="fas fa-arrow-down text-dark fa-2x mb-2"),
                                    html.H5("L_CUR", className="text-dark fw-bold mb-1"),
                                    html.P("Low Current Return", className="small text-muted mb-0"),
                                    html.P("Retorno de corriente", className="small text-muted")
                                ], className="text-center p-3 border rounded bg-secondary bg-opacity-10 h-100")
                            ], className="col-6 col-md-3 mb-3"),
                        ], className="row mb-5"),
                        
                    ], id="content-hardware", style={"display": "none"}),
                    
                    # TAB 3: CALIBRACIÓN
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-exclamation-triangle fa-2x text-danger me-3"),
                            html.Div([
                                html.H5("Calibración Obligatoria", className="fw-bold mb-1"),
                                html.P("Las mediciones NO serán precisas hasta completar los 3 pasos: OPEN → SHORT → LOAD", className="mb-0")
                            ])
                        ], className="alert alert-danger border-start border-4 border-danger d-flex py-4 mb-5"),
                        
                        html.H3("Proceso de Calibración", className="mb-4 fw-bold"),
                        
                        # Open
                        html.Div([
                            html.Div([
                                html.Span("1", className="badge bg-primary rounded-circle fs-3 px-3 py-2"),
                            ], className="me-3"),
                            html.H4("OPEN - Circuito Abierto", className="fw-bold mb-0 mt-2 text-primary")
                        ], className="d-flex align-items-center mb-3"),
                        html.Div([
                            html.P("Corrige parásitas cuando no hay carga."),
                            html.Ol([
                                html.Li("Conecta H_POT con H_CUR"),
                                html.Li("Conecta L_POT con L_CUR"),
                                html.Li("Deja H y L desconectadas entre sí"),
                            ]),
                            html.Div([
                                html.Span("$", className="text-success me-2 fw-bold"),
                                html.Span("calibrate open", className="text-light font-monospace")
                            ], className="bg-dark rounded p-3 font-monospace"),
                            html.Img(src=IMAGES['open_load'], className="img-fluid rounded shadow mt-3", style={"maxHeight": "250px"})
                        ], className="ps-5 mb-5"),
                        
                        # Short
                        html.Div([
                            html.Div([
                                html.Span("2", className="badge bg-warning rounded-circle fs-3 px-3 py-2"),
                            ], className="me-3"),
                            html.H4("SHORT - Cortocircuito", className="fw-bold mb-0 mt-2 text-warning")
                        ], className="d-flex align-items-center mb-3"),
                        html.Div([
                            html.P("Corrige impedancias parásitas con terminales unidas."),
                            html.Ol([
                                html.Li("Une todas las terminales (H_POT, H_CUR, L_POT, L_CUR)"),
                                html.Li("Solo cuando ganancia canal 1 es 0 o 1"),
                            ]),
                            html.Div([
                                html.Span("$", className="text-success me-2 fw-bold"),
                                html.Span("calibrate short", className="text-light font-monospace")
                            ], className="bg-dark rounded p-3 font-monospace"),
                        ], className="ps-5 mb-5"),
                        
                        # Load
                        html.Div([
                            html.Div([
                                html.Span("3", className="badge bg-success rounded-circle fs-3 px-3 py-2"),
                            ], className="me-3"),
                            html.H4("LOAD - Carga Conocida", className="fw-bold mb-0 mt-2 text-success")
                        ], className="d-flex align-items-center mb-3"),
                        html.Div([
                            html.P("Proporciona trazabilidad con estándar certificado."),
                            html.Ol([
                                html.Li("Conecta resistor de precisión conocido"),
                                html.Li("Valor cercano al DUT a medir"),
                            ]),
                            html.Div([
                                html.Span("$", className="text-success me-2 fw-bold"),
                                html.Span("calibrate rt 1000 xt 0", className="text-light font-monospace")
                            ], className="bg-dark rounded p-3 font-monospace mb-2"),
                            html.P("Ejemplo: Resistor de 1kΩ, reactancia 0", className="text-muted small")
                        ], className="ps-5 mb-5"),
                        
                        # Guardar
                        html.H4("Guardar Calibración", className="fw-bold mb-3"),
                        html.Div([
                            html.Div([
                                html.Span("$", className="text-success me-2 fw-bold"),
                                html.Span("calibrate commit 20251106", className="text-light font-monospace")
                            ], className="bg-dark rounded p-3 font-monospace mb-3"),
                            html.P(["Contraseña por defecto: ", html.Code("Analog123", className="bg-dark text-info px-2 py-1 rounded")]),
                            html.P("Capacidad: 25 calibraciones en EEPROM o 450 en Flash", className="text-muted small")
                        ], className="bg-light p-4 rounded border"),
                        
                    ], id="content-calibration", style={"display": "none"}),
                    
                    # TAB 4: CLI
                    html.Div([
                        html.H3("Comandos Esenciales", className="mb-4 fw-bold"),
                        
                        html.H5("Medición", className="fw-bold mb-3"),
                        html.Div([
                            html.Div([html.Span("$", className="text-success me-2"), html.Span("z", className="text-light")], className="mb-2"),
                            html.Div([html.Span("$", className="text-success me-2"), html.Span("frequency 1000", className="text-light")], className="mb-2"),
                            html.Div([html.Span("$", className="text-success me-2"), html.Span("magnitude 1.0", className="text-light")], className="mb-2"),
                            html.Div([html.Span("$", className="text-success me-2"), html.Span("average 200", className="text-light")], className="mb-2"),
                            html.Div([html.Span("$", className="text-success me-2"), html.Span("display 6", className="text-light")], className="mb-2"),
                        ], className="bg-dark rounded p-3 font-monospace mb-4"),
                        
                        html.H5("Barrido", className="fw-bold mb-3"),
                        html.Div([
                            html.Div([html.Span("$", className="text-success me-2"), html.Span("sweep_type frequency 100 10000", className="text-light")], className="mb-2"),
                            html.Div([html.Span("$", className="text-success me-2"), html.Span("sweep_scale log", className="text-light")], className="mb-2"),
                            html.Div([html.Span("$", className="text-success me-2"), html.Span("count 50", className="text-light")], className="mb-2"),
                        ], className="bg-dark rounded p-3 font-monospace mb-4"),
                        
                        html.H5("Sistema", className="fw-bold mb-3"),
                        html.Div([
                            html.Div([html.Span("$", className="text-success me-2"), html.Span("*idn", className="text-light")], className="mb-2"),
                            html.Div([html.Span("$", className="text-success me-2"), html.Span("help", className="text-light")], className="mb-2"),
                            html.Div([html.Span("$", className="text-success me-2"), html.Span("selftest", className="text-light")], className="mb-2"),
                        ], className="bg-dark rounded p-3 font-monospace mb-4"),
                        
                        html.H5("Modos de Display (0-17)", className="fw-bold mb-3"),
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.H6("Capacitancia", className="text-primary fw-bold"),
                                    html.P("0:Cs-Rs  1:Cs-D  2:Cs-Q", className="small mb-1"),
                                    html.P("3:Cp-Rp  4:Cp-D  5:Cp-Q", className="small mb-0")
                                ], className="col-6 col-md-3 mb-3"),
                                html.Div([
                                    html.H6("Inductancia", className="text-success fw-bold"),
                                    html.P("9:Ls-Rs  10:Ls-D  11:Ls-Q", className="small mb-1"),
                                    html.P("12:Lp-Rp  13:Lp-D  14:Lp-Q", className="small mb-0")
                                ], className="col-6 col-md-3 mb-3"),
                                html.Div([
                                    html.H6("Impedancia", className="text-warning fw-bold"),
                                    html.P("6:R-X", className="small mb-1"),
                                    html.P("7:Z-θ°  8:Z-θʳ", className="small mb-0")
                                ], className="col-6 col-md-3 mb-3"),
                                html.Div([
                                    html.H6("Admitancia", className="text-info fw-bold"),
                                    html.P("15:G-B", className="small mb-1"),
                                    html.P("16:Y-θ°  17:Y-θʳ", className="small mb-0")
                                ], className="col-6 col-md-3 mb-3"),
                            ], className="row")
                        ], className="bg-light p-3 rounded border"),
                        
                    ], id="content-cli", style={"display": "none"}),
                    
                    # TAB 5: SOPORTE
                    html.Div([
                        html.H3("Contacto y Recursos", className="mb-4 fw-bold"),
                        
                        html.Div([
                            html.Div([
                                html.H5("Soporte Técnico", className="fw-bold mb-3"),
                                html.A([
                                    html.I(className="fas fa-envelope me-2"),
                                    "admx-support@analog.com"
                                ], href="mailto:admx-support@analog.com", className="btn btn-primary btn-lg")
                            ], className="col-md-6 mb-4"),
                            html.Div([
                                html.H5("Recursos", className="fw-bold mb-3"),
                                html.Ul([
                                    html.Li(html.A("Wiki Analog", href="https://wiki.analog.com/resources/eval/user-guides/admx/eval-admx2001ebz", target="_blank")),
                                    html.Li(html.A("Drivers FTDI", href="https://www.ftdichip.com/Drivers/VCP.htm", target="_blank")),
                                    html.Li(html.A("TeraTerm", href="https://github.com/TeraTermProject/teraterm/releases", target="_blank")),
                                ])
                            ], className="col-md-6 mb-4"),
                        ], className="row"),
                        
                        html.Hr(),
                        html.P([
                            html.Strong("Desarrollado por: "),
                            "Mario Ricardo Montero, Juan Carlos Alvarez, Francisco J. Racedo N."
                        ], className="text-muted"),
                        
                    ], id="content-support", style={"display": "none"}),
                    
                ], className="container py-4 px-4", style={"maxWidth": "1200px"})
            ], className="main-content w-100")
        ], className="d-flex flex-grow-1"),
        footer(),
        floating_terminal_button()
    ], className="d-flex flex-column min-vh-100")


@callback(
    [Output('btn-quickstart', 'className'),
     Output('btn-hardware', 'className'),
     Output('btn-calibration', 'className'),
     Output('btn-cli', 'className'),
     Output('btn-support', 'className'),
     Output('content-quickstart', 'style'),
     Output('content-hardware', 'style'),
     Output('content-calibration', 'style'),
     Output('content-cli', 'style'),
     Output('content-support', 'style')],
    [Input('btn-quickstart', 'n_clicks'),
     Input('btn-hardware', 'n_clicks'),
     Input('btn-calibration', 'n_clicks'),
     Input('btn-cli', 'n_clicks'),
     Input('btn-support', 'n_clicks')]
)
def update_tabs(n1, n2, n3, n4, n5):
    from dash import ctx
    button_id = ctx.triggered_id if ctx.triggered_id else 'btn-quickstart'
    
    base = "btn btn-outline-primary me-2 mb-2 fw-bold"
    active = "btn btn-primary active me-2 mb-2 fw-bold"
    
    tabs = {'btn-quickstart': 0, 'btn-hardware': 1, 'btn-calibration': 2, 'btn-cli': 3, 'btn-support': 4}
    active_idx = tabs.get(button_id, 0)
    
    buttons = [base] * 5
    buttons[active_idx] = active
    
    contents = [{"display": "none"}] * 5
    contents[active_idx] = {"display": "block"}
    
    return buttons + contents
