"""
ZORIA Documentation Page - Diseño Premium con Contenido Completo
Documentación completa con navegación tipo cards y todo el contenido original
"""
from dash import html, dcc, register_page
from dash_spa import register_page

# Importar componentes comunes
from pages.common.sidebar import sideBar
from pages.common.mobile_nav import mobileNavBar
from pages.common.footer import footer
from pages.common.floating_terminal_button import floating_terminal_button

# Registrar la página
register_page(
    __name__,
    path='/documentacion',
    title='Documentación - ZORIA',
    name='Documentación'
)


# ==================== IMÁGENES ====================
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


# ==================== COMPONENTES AUXILIARES ====================

def info_box(content, type="info"):
    """Caja de información estilizada — token-based, dual-theme"""
    colors = {
        "info": ("var(--z-color-info-subtle)", "var(--z-color-primary)", "var(--z-color-info-border)"),
        "warning": ("var(--z-color-warning-subtle)", "var(--z-color-warning)", "var(--z-color-warning)"),
        "danger": ("var(--z-color-danger-subtle)", "var(--z-color-danger)", "var(--z-color-danger)"),
        "success": ("var(--z-color-success-subtle)", "var(--z-color-success)", "var(--z-color-success)"),
        "tip": ("var(--z-color-warning-subtle)", "var(--z-color-warning)", "var(--z-footer-accent)")
    }
    bg, text, border = colors.get(type, colors["info"])
    
    return html.Div(
        content,
        style={
            'background': bg,
            'borderLeft': f'4px solid {border}',
            'padding': '15px 20px',
            'borderRadius': '8px',
            'marginBottom': '20px',
            'color': text
        }
    )


def step_number(number, color="var(--z-footer-accent)"):
    """Número de paso circular"""
    return html.Span(
        str(number),
        style={
            'display': 'inline-flex',
            'width': '32px',
            'height': '32px',
            'background': color,
            'color': 'var(--z-color-text-inverse)',
            'borderRadius': '50%',
            'alignItems': 'center',
            'justifyContent': 'center',
            'fontWeight': '700',
            'fontSize': '0.9rem',
            'marginRight': '12px'
        }
    )


def image_card(src, caption=None):
    """Tarjeta de imagen con caption"""
    return html.Div([
        html.Img(
            src=src,
            style={
                'width': '100%',
                'maxWidth': '800px',
                'borderRadius': '12px',
                'border': '1px solid var(--z-color-border)',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.1)'
            }
        ),
        html.P(
            caption,
            style={
                'fontSize': '0.85rem',
                'color': 'var(--z-color-text-tertiary)',
                'fontStyle': 'italic',
                'marginTop': '10px',
                'textAlign': 'center'
            }
        ) if caption else None
    ], style={'marginBottom': '30px', 'textAlign': 'center'})


# ==================== CONTENIDO: INICIO RÁPIDO ====================

def content_inicio_rapido():
    return html.Div([
        # Intro
        html.Div([
            html.H3([
                html.I(className="fas fa-rocket me-3", style={'color': 'var(--z-footer-accent)'}),
                html.Span("Inicio Rápido - Five Simple Steps", **{'data-i18n': 'doc.section.start'})
            ], className="mb-3 fw-bold", style={'color': 'var(--z-color-text-primary)'}),
            html.P([
                "Esta guía te ayudará a configurar y comenzar a usar tu ",
                html.Strong("EVAL-ADMX2001", style={'color': 'var(--z-footer-accent)'}),
                " en cinco simples pasos para realizar tus primeras mediciones."
            ], style={'color': 'var(--z-color-text-secondary)', 'fontSize': '1.1rem', 'marginBottom': '30px'})
        ]),
        
        info_box([
            html.Strong("Contenido del Kit:"),
            html.Ul([
                html.Li("Placa EVAL-ADMX2001EBZ"),
                html.Li("Cable UART a USB (TTL-232R-RPI)"),
                html.Li("Adaptador de corriente universal con salida de 9VDC"),
                html.Li("Pinzas de prueba para medidor LCR")
            ], style={'marginBottom': '0'}),
            html.Div([
                html.Strong("IMPORTANTE: "), 
                "El módulo ADMX2001B se vende por separado. Es crítico comprar AMBOS componentes."
            ], style={'marginTop': '15px', 'padding': '10px', 'background': 'var(--z-color-warning-subtle)', 'borderRadius': '6px'})
        ], "info"),
        
        # Paso 1
        html.Div([
            html.H5([step_number(1), html.Span("Instalación de Drivers FTDI VCP", **{'data-i18n': 'doc.qs.h5.ftdi'})], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),
            html.P([
                "El ", html.Strong("EVAL-ADMX2001EBZ"), " se comunica con tu PC mediante UART. "
                "El cable USB-to-UART incluido requiere drivers ",
                html.Strong("Virtual COM Port (VCP)"), " de FTDI."
            ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '15px'}),
            html.Div([
                html.H6("Procedimiento:", className="fw-bold mt-3 mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.qs.h6.procedure'}),
                html.Ol([
                    html.Li([
                        "Descargar el setup executable del driver desde: ",
                        html.A("https://www.ftdichip.com/Drivers/VCP.htm", href="https://www.ftdichip.com/Drivers/VCP.htm", target="_blank", style={'color': 'var(--z-color-primary)'})
                    ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '10px'}),
                    html.Li("Descomprimir y ejecutar el instalador", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '10px'}),
                    html.Li([html.Strong("Conectar"), " el cable USB-UART al PC"], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '10px'}),
                    html.Li("Abrir el Administrador de Dispositivos (Windows) / System Profiler (Mac)", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '10px'}),
                    html.Li("Verificar que el Puerto Serial USB aparezca bajo 'Ports (COM & LPT)' con un identificador asignado (ej. COM3)", style={'color': 'var(--z-color-text-secondary)'})
                ])
            ], style={'background': 'var(--z-color-bg-primary)', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '15px'}),
            info_box([
                html.Strong("Verificación: "),
                "En Windows busca 'USB Serial Port (COMx)' bajo 'Ports (COM & LPT)'. Anota el número de puerto COM para el paso 4."
            ], "tip"),
            image_card(IMAGES.get('dev_mgr_vcp'), "Administrador de dispositivos Windows mostrando puerto COM")
        ], style={'marginBottom': '40px'}),
        
        # Paso 2
        html.Div([
            html.H5([step_number(2), html.Span("Instalación del Emulador de Terminal", **{'data-i18n': 'doc.qs.h5.terminal'})], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),
            html.P([
                "Para comunicarse con el ADMX2001B mediante su interfaz CLI y UART, se recomienda ",
                html.Strong("TeraTerm"), " (soporta códigos ANSI para colores y cursor)."
            ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '15px'}),
            html.A([
                html.I(className="fas fa-download me-2"),
                "Descargar TeraTerm"
            ], href="https://github.com/TeraTermProject/teraterm/releases", target="_blank",
               className="btn mb-3", style={'background': 'var(--z-footer-accent)', 'color': '#ffffff', 'textDecoration': 'none', 'display': 'inline-block', 'padding': '10px 20px', 'borderRadius': '8px'}),
            html.P([
                html.Strong("Alternativas: "), "PuTTY, CoolTerm (pueden tener problemas con códigos ANSI)"
            ], style={'color': 'var(--z-color-text-tertiary)', 'fontSize': '0.9rem', 'marginTop': '15px'}),
            html.Div([
                html.H6("Configuración de TeraTerm:", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.qs.h6.teraterm_config'}),
                html.Ul([
                    html.Li([html.Strong("Speed: "), "115200"], style={'color': 'var(--z-color-text-secondary)'}),
                    html.Li([html.Strong("Data: "), "8 bits"], style={'color': 'var(--z-color-text-secondary)'}),
                    html.Li([html.Strong("Parity: "), "none"], style={'color': 'var(--z-color-text-secondary)'}),
                    html.Li([html.Strong("Stop bits: "), "1 bits"], style={'color': 'var(--z-color-text-secondary)'}),
                    html.Li([html.Strong("Flow control: "), "none"], style={'color': 'var(--z-color-text-secondary)'})
                ])
            ], style={'background': 'var(--z-color-bg-primary)', 'padding': '15px', 'borderRadius': '8px', 'marginTop': '15px'})
        ], style={'marginBottom': '40px'}),
        
        # Paso 3
        html.Div([
            html.H5([step_number(3), html.Span("Configuración de Hardware", **{'data-i18n': 'doc.qs.h5.hardware_config'})], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),
            html.P("Sigue estos pasos para la configuración inicial:", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '15px'}),
            html.Div([
                html.Div([
                    html.Strong("3.1 Ensamblaje del módulo", style={'color': 'var(--z-color-text-primary)', 'display': 'block', 'marginBottom': '8px'}),
                    html.Ul([
                        html.Li("Insertar el módulo ADMX2001B en la placa EVAL-ADMX2001EBZ"),
                        html.Li("Los conectores tienen guía - asegúrate de que esté completamente insertado")
                    ], style={'color': 'var(--z-color-text-secondary)'})
                ], style={'background': 'var(--z-color-bg-elevated)', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '15px'}),
                html.Div([
                    html.Strong("3.2 Configuración de switches para self-test inicial", style={'color': 'var(--z-color-text-primary)', 'display': 'block', 'marginBottom': '8px'}),
                    html.Ul([
                        html.Li([html.Strong("S1"), " → Posición OPEN"]),
                        html.Li([html.Strong("S2"), " → Posición GND"])
                    ])
                ], style={'background': 'var(--z-color-bg-elevated)', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '15px'}),
                html.Div([
                    html.Strong("3.3 Alimentación:", style={'color': 'var(--z-color-text-primary)', 'display': 'block', 'marginBottom': '8px'}),
                    html.Ul([
                        html.Li("Conectar el adaptador de corriente al conector de alimentación y al tomacorriente"),
                        html.Li([html.Strong("Verificar: "), "El LED de self-test debe iluminarse en VERDE (parte inferior del módulo)"])
                    ])
                ], style={'background': 'var(--z-color-bg-elevated)', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '15px'}),
                html.Div([
                    html.Strong("3.4 Conexión UART:", style={'color': 'var(--z-color-text-primary)', 'display': 'block', 'marginBottom': '8px'}),
                    html.Ul([
                        html.Li("TX (naranja) → TX del evaluador"),
                        html.Li("RX (amarillo) → RX del evaluador"),
                        html.Li("GND (negro) → GND del evaluador")
                    ])
                ], style={'background': 'var(--z-color-bg-elevated)', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '15px'}),
                html.Div([
                    html.Strong("3.5 Verificaciones finales:", style={'color': 'var(--z-color-text-primary)', 'display': 'block', 'marginBottom': '8px'}),
                    html.Ul([
                        html.Li("Jumper CLK_SEL en posición INT (reloj interno)"),
                        html.Li("Cambiar switches a DUT y GND para mediciones"),
                        html.Li("Conectar pinzas de prueba: BNC rojos → HCUR/HPOT, BNC negros → LPOT/LCUR")
                    ])
                ], style={'background': 'var(--z-color-bg-elevated)', 'padding': '15px', 'borderRadius': '8px'})
            ]),
            info_box([
                html.Strong("IMPORTANTE sobre pinzas: "),
                "Inspeccionar los conectores BNC de las pinzas. La carcasa puede aflojarse parcialmente. ",
                "Al usar en configuración 'open', cada pinza debe sujetar su propio trozo de alambre para asegurar conexión eléctrica."
            ], "warning"),
            image_card(IMAGES.get('basic_connections'), "Diagrama de conexiones básicas"),
            image_card(IMAGES.get('uart_connection'), "Detalle de conexión UART")
        ], style={'marginBottom': '40px'}),
        
        # Paso 4
        html.Div([
            html.H5([step_number(4), html.Span("Abrir Sesión con TeraTerm", **{'data-i18n': 'doc.qs.h5.teraterm'})], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),
            html.Div([
                html.Strong("Configuración inicial:", style={'display': 'block', 'marginBottom': '10px'}),
                html.Ol([
                    html.Li("Abrir TeraTerm y elegir conexión Serial", style={'marginBottom': '8px'}),
                    html.Li("Seleccionar el puerto COM identificado en el Administrador de Dispositivos", style={'marginBottom': '8px'}),
                    html.Li("Ir a Setup → Serial port y configurar: 115200, 8, none, 1, none", style={'marginBottom': '8px'}),
                    html.Li("Click en 'New setting'", style={'marginBottom': '8px'}),
                    html.Li("(Opcional) Guardar configuración: Setup → Save setup", style={'marginBottom': '8px'})
                ], style={'color': 'var(--z-color-text-secondary)'}),
                html.Strong("Verificar la conexión:", style={'display': 'block', 'marginTop': '20px', 'marginBottom': '10px'}),
                html.Ul([
                    html.Li([
                        "Presionar ", html.Code("ENTER", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '2px 8px', 'borderRadius': '4px'}),
                        " para mostrar el prompt ", html.Code("ADMX2001>")
                    ], style={'marginBottom': '8px'}),
                    html.Li([
                        "Escribir ", html.Code("*idn", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '2px 8px', 'borderRadius': '4px'}),
                        " y presionar ENTER para ver versión de firmware"
                    ], style={'marginBottom': '8px'}),
                    html.Li([
                        "Escribir ", html.Code("help", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '2px 8px', 'borderRadius': '4px'}),
                        " y presionar ENTER para ver lista de comandos disponibles"
                    ])
                ], style={'color': 'var(--z-color-text-secondary)'})
            ], style={'background': 'var(--z-color-bg-primary)', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '15px'}),
            info_box([
                html.Strong("Tip: "),
                "Cerrar la ventana de TeraTerm no resetea la configuración del ADMX2001B de la última sesión."
            ], "tip")
        ], style={'marginBottom': '40px'}),
        
        # Paso 5
        html.Div([
            html.H5([step_number(5), html.Span("Primeras Mediciones", **{'data-i18n': 'doc.qs.h5.first_measurements'})], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),
            html.P([
                "Al abrir una sesión, el ADMX2001B está listo para realizar mediciones de impedancia. ",
                html.Strong("Las mediciones no serán precisas hasta calibrar el módulo (ver sección Calibración).")
            ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '15px'}),
            html.Div([
                html.Strong("Configuración por defecto:", style={'display': 'block', 'marginBottom': '10px'}),
                html.Ul([
                    html.Li("Mediciones de impedancia en coordenadas rectangulares (mode 6: R, X)"),
                    html.Li("Señal de 1V pk (magnitude = 1) a 1kHz"),
                    html.Li("Sin offset DC"),
                    html.Li("Auto-ranging habilitado")
                ], style={'color': 'var(--z-color-text-secondary)'})
            ], style={'background': 'var(--z-color-bg-primary)', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '20px'}),
            html.H6("Ejemplo: Medición de Capacitancia", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.qs.h6.example_cap'}),
            html.P("Realizar una medición Cp-Rp a 100kHz con amplitud de 1V, retornar 5 lecturas promediando 10 muestras:", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '10px'}),
            html.Pre("""ADMX2001> frequency 100
frequency = 100.0000kHz

ADMX2001> display 9
Measurement model: 9 - Capacitance and equivalent parallel resistance (Cp,Rp)

ADMX2001> magnitude 1
magnitude = 1.0000

ADMX2001> average 10
average = 10

ADMX2001> count 5
sampleCount = 5

ADMX2001> z
0,5.677640e-13,8.062763e+07
1,5.668012e-13,8.305672e+07
2,5.675237e-13,8.208995e+07
3,5.673763e-13,8.276912e+07
4,5.683635e-13,8.463327e+07
""", style={
                'background': 'var(--z-color-bg-card)',
                'color': 'var(--z-color-text-secondary)',
                'padding': '20px',
                'borderRadius': '12px',
                'fontFamily': 'monospace',
                'fontSize': '0.85rem',
                'overflowX': 'auto',
                'lineHeight': '1.6'
            }),
            info_box([
                html.Strong("¡Listo! "),
                "Tu EVAL-ADMX2001 está configurado. Para mediciones de precision, continúa con el procedimiento de calibración."
            ], "success")
        ])
    ])


# ==================== CONTENIDO: HARDWARE ====================

def content_hardware():
    return html.Div([
        html.Div([
            html.H3([
                html.I(className="fas fa-microchip me-3", style={'color': 'var(--z-color-primary)'}),
                html.Span("Especificaciones de Hardware", **{'data-i18n': 'doc.section.hardware'})
            ], className="mb-3 fw-bold", style={'color': 'var(--z-color-text-primary)'}),
            html.P([
                "El ", html.Strong("EVAL-ADMX2001 LCR Meter Demo", style={'color': 'var(--z-color-primary)'}),
                " comprende el módulo ", html.Strong("ADMX2001B"), " y la placa de evaluación ",
                html.Strong("EVAL-ADMX2001EBZ"), "."
            ], style={'color': 'var(--z-color-text-secondary)', 'fontSize': '1.1rem', 'marginBottom': '30px'})
        ]),
        
        info_box([
            html.Strong("IMPORTANTE: "),
            "Es crítico comprar AMBOS el módulo ADMX2001B y la placa EVAL-ADMX2001EBZ. Se venden por separado."
        ], "warning"),
        
        # ADMX2001B Module
        html.Div([
            html.H5("ADMX2001B - Módulo Analizador de Impedancia", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.hw.h5.module'}),
            html.Div([
                html.Ul([
                    html.Li([html.Strong("Altamente compacto: "), "System-on-Module (SOM) de 1.5 × 2.5 pulgadas"]),
                    html.Li([html.Strong("Rango de frecuencia: "), "0.2 Hz a 10 MHz"]),
                    html.Li([html.Strong("Mediciones: "), "Resistencia DC o impedancia AC"]),
                    html.Li([html.Strong("Canales ADC: "), "18 bits de resolución"]),
                    html.Li([html.Strong("Alimentación: "), "Fuente única de 3.3V"]),
                    html.Li([html.Strong("Interfaces: "), "UART y SPI flexibles"]),
                    html.Li([html.Strong("Formatos: "), "18 modos de display en unidades SI"])
                ], style={'color': 'var(--z-color-text-secondary)'})
            ], style={
                'background': 'var(--z-color-bg-card)',
                'borderRadius': '12px',
                'border': '1px solid var(--z-color-border)',
                'padding': '20px',
                'marginBottom': '30px'
            })
        ]),
        
        # EVAL-ADMX2001EBZ Board
        html.Div([
            html.H5("EVAL-ADMX2001EBZ - Placa de Evaluación", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.hw.h5.eval_board'}),
            html.Div([
                html.Ul([
                    html.Li([html.Strong("Conectores BNC: "), "Para sondas y accesorios LCR estándar"]),
                    html.Li([html.Strong("Interfaz UART: "), "Cable USB-to-UART para conexión a PC"]),
                    html.Li([html.Strong("Triggers SMA: "), "Sincronización y triggers por hardware"]),
                    html.Li([html.Strong("Headers Arduino: "), "Para desarrollo embebido (ej. SDP-K1)"]),
                    html.Li([html.Strong("Alimentación: "), "Conector para adaptadores AC/DC de +5V a +12V"]),
                    html.Li([html.Strong("Headers PMOD: "), "Acceso a interfaz SPI"]),
                    html.Li([html.Strong("I/Os digitales: "), "8 salidas digitales configurables"])
                ], style={'color': 'var(--z-color-text-secondary)'})
            ], style={
                'background': 'var(--z-color-bg-card)',
                'borderRadius': '12px',
                'border': '1px solid var(--z-color-border)',
                'padding': '20px',
                'marginBottom': '30px'
            })
        ]),
        
        # Descripción de Terminales
        html.Div([
            html.H5("Descripción de Terminales", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.hw.h5.terminals'}),
            html.Div([
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("Terminal", style={'color': 'var(--z-color-text-primary)', 'fontWeight': '600', 'padding': '12px', 'borderBottom': '2px solid #3b82f6'}),
                            html.Th("Descripción", style={'color': 'var(--z-color-text-primary)', 'fontWeight': '600', 'padding': '12px', 'borderBottom': '2px solid #3b82f6'})
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([
                            html.Td(html.Strong("H_CUR"), style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td("Terminal de fuente de señal. Genera la excitación requerida. Puede proveer hasta ±5V @ 50mA", style={'padding': '12px', 'color': 'var(--z-color-text-secondary)', 'borderBottom': '1px solid var(--z-color-border)'})
                        ]),
                        html.Tr([
                            html.Td(html.Strong("H_POT"), style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td("Terminal de sensado de voltaje. Conectar a H_CUR en el DUT", style={'padding': '12px', 'color': 'var(--z-color-text-secondary)', 'borderBottom': '1px solid var(--z-color-border)'})
                        ]),
                        html.Tr([
                            html.Td(html.Strong("L_POT"), style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td("Terminal de sensado de voltaje. Conectar a L_CUR en el DUT", style={'padding': '12px', 'color': 'var(--z-color-text-secondary)', 'borderBottom': '1px solid var(--z-color-border)'})
                        ]),
                        html.Tr([
                            html.Td(html.Strong("L_CUR"), style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td("Terminal de sensado de corriente. Ruta de retorno para señal de excitación", style={'padding': '12px', 'color': 'var(--z-color-text-secondary)', 'borderBottom': '1px solid var(--z-color-border)'})
                        ]),
                        html.Tr([
                            html.Td(html.Strong("UART TX/RX"), style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td("Pines de comunicación UART. Lógica 3.3V", style={'padding': '12px', 'color': 'var(--z-color-text-secondary)', 'borderBottom': '1px solid var(--z-color-border)'})
                        ]),
                        html.Tr([
                            html.Td(html.Strong("TRIG_IN"), style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td("Entrada de trigger para adquisición sincronizada por hardware (3.3V, mín 15μs)", style={'padding': '12px', 'color': 'var(--z-color-text-secondary)', 'borderBottom': '1px solid var(--z-color-border)'})
                        ]),
                        html.Tr([
                            html.Td(html.Strong("TRIG_OUT"), style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td("Salida de trigger al completar medición", style={'padding': '12px', 'color': 'var(--z-color-text-secondary)', 'borderBottom': '1px solid var(--z-color-border)'})
                        ]),
                        html.Tr([
                            html.Td(html.Strong("CLK_IN/OUT"), style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td("Entrada/salida de reloj. Señal LVCMOS 50MHz", style={'padding': '12px', 'color': 'var(--z-color-text-secondary)', 'borderBottom': '1px solid var(--z-color-border)'})
                        ])
                    ])
                ], style={'width': '100%', 'borderCollapse': 'collapse'})
            ], style={
                'background': 'var(--z-color-bg-card)',
                'borderRadius': '12px',
                'border': '1px solid var(--z-color-border)',
                'padding': '20px',
                'marginBottom': '30px',
                'overflowX': 'auto'
            })
        ]),
        
        # Self-Test
        html.Div([
            html.H5("Funcionalidad de Self-Test", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.hw.h5.selftest'}),
            html.P("Al encender, el ADMX2001B ejecuta automáticamente un self-test. El LED bicolor indica el estado:", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '15px'}),
            html.Div([
                html.Div([
                    html.Span("●", style={'color': 'var(--z-color-success)', 'fontSize': '24px', 'marginRight': '12px'}),
                    html.Strong("Verde: ", style={'color': 'var(--z-color-text-primary)'}),
                    html.Span("Pasa el self-test", style={'color': 'var(--z-color-text-secondary)'})
                ], style={'padding': '12px', 'marginBottom': '8px'}),
                html.Div([
                    html.Span("●", style={'color': 'var(--z-color-warning)', 'fontSize': '24px', 'marginRight': '12px'}),
                    html.Strong("Verde/Rojo: ", style={'color': 'var(--z-color-text-primary)'}),
                    html.Span("Falla el self-test", style={'color': 'var(--z-color-text-secondary)'})
                ], style={'padding': '12px', 'marginBottom': '8px'}),
                html.Div([
                    html.Span("●", style={'color': 'var(--z-color-danger)', 'fontSize': '24px', 'marginRight': '12px'}),
                    html.Strong("Rojo: ", style={'color': 'var(--z-color-text-primary)'}),
                    html.Span("Problema mayor (alimentación, firmware faltante)", style={'color': 'var(--z-color-text-secondary)'})
                ], style={'padding': '12px'})
            ], style={'background': 'var(--z-color-bg-primary)', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '15px'}),
            html.P([
                html.Strong("Comandos del self-test:")
            ], style={'color': 'var(--z-color-text-primary)', 'marginTop': '20px', 'marginBottom': '10px'}),
            html.Ul([
                html.Li([html.Code("selftest", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '2px 8px', 'borderRadius': '4px'}), " - Ver estado del último self-test"]),
                html.Li([html.Code("selftest run", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '2px 8px', 'borderRadius': '4px'}), " - Reejecutar el self-test"])
            ], style={'color': 'var(--z-color-text-secondary)'}),
            info_box([
                html.Strong("Importante: "),
                "Para pasar el componente analógico del self-test, los switches S1 y S2 deben estar en OPEN y GND."
            ], "warning")
        ], style={'marginBottom': '40px'}),
        
        # Switches
        html.Div([
            html.H5("Configuración de Switches", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.hw.h5.switches'}),
            html.P("Los switches S1 y S2 configuran el modo de operación:", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '15px'}),
            html.Div([
                html.Div([
                    html.Strong("Self-Test Mode:"),
                    html.Ul([
                        html.Li("S1 → OPEN"),
                        html.Li("S2 → GND")
                    ])
                ], style={'background': 'var(--z-color-bg-elevated)', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '10px'}),
                html.Div([
                    html.Strong("Medición Normal (DUT):"),
                    html.Ul([
                        html.Li("S1 → LOAD"),
                        html.Li("S2 → GND")
                    ])
                ], style={'background': 'var(--z-color-bg-elevated)', 'padding': '15px', 'borderRadius': '8px'})
            ])
        ], style={'marginBottom': '40px'}),
        
        image_card(IMAGES.get('basic_connections'), "Diagrama de conexiones del evaluador")
    ])


# ==================== CONTENIDO: SOFTWARE ====================

def content_software():
    return html.Div([
        html.Div([
            html.H3([
                html.I(className="fas fa-laptop-code me-3", style={'color': 'var(--z-color-success)'}),
                html.Span("Guía de Software ZORIA", **{'data-i18n': 'doc.section.software'})
            ], className="mb-3 fw-bold", style={'color': 'var(--z-color-text-primary)'}),
            html.P([
                "ZORIA es una plataforma web de código abierto que transforma el analizador de impedancia ",
                html.Strong("EVAL-ADMX2001"), " (Analog Devices) en un sistema de medición moderno con ",
                "visualización científica en tiempo real."
            ], style={'color': 'var(--z-color-text-secondary)', 'fontSize': '1.1rem', 'marginBottom': '30px'})
        ]),
        
        # Arquitectura
        html.Div([
            html.H5("Arquitectura de ZORIA", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h5.architecture'}),
            html.P("ZORIA implementa una arquitectura modular de tres capas:", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '15px'}),
            html.Div([
                html.Div([
                    html.H6("1. Capa de Hardware", className="fw-bold mb-2", style={'color': 'var(--z-color-success)'}, **{'data-i18n': 'doc.sw.h6.hw_layer'}),
                    html.Ul([
                        html.Li("Comunicación serial con EVAL-ADMX2001 via protocolo UART"),
                        html.Li("Parsing y validación de comandos"),
                        html.Li("Adquisición de datos y control de barridos"),
                        html.Li("Detección automática de dispositivo y manejo de conexión")
                    ], style={'color': 'var(--z-color-text-secondary)'})
                ], style={'background': 'var(--z-color-success-subtle)', 'padding': '20px', 'borderRadius': '12px', 'marginBottom': '15px', 'border': '2px solid var(--z-color-success)'}),
                
                html.Div([
                    html.H6("2. Backend (Python)", className="fw-bold mb-2", style={'color': 'var(--z-color-success)'}, **{'data-i18n': 'doc.sw.h6.backend'}),
                    html.Pre("""lib/
├── admx2001.py       # Clase principal de control del dispositivo (43 métodos)
├── calibration.py    # Gestión de calibración (open/short/load)
├── utils.py          # Utilidades de validación y procesamiento
├── enums.py          # Constantes, modos y configuraciones
└── exceptions.py     # Jerarquía de excepciones custom""", style={
                        'background': 'var(--z-color-bg-card)',
                        'color': 'var(--z-color-success)',
                        'padding': '15px',
                        'borderRadius': '8px',
                        'fontFamily': 'monospace',
                        'fontSize': '0.85rem',
                        'lineHeight': '1.5'
                    })
                ], style={'background': 'var(--z-color-success-subtle)', 'padding': '20px', 'borderRadius': '12px', 'marginBottom': '15px', 'border': '2px solid var(--z-color-success)'}),
                
                html.Div([
                    html.H6("3. Frontend (Dash-SPA)", className="fw-bold mb-2", style={'color': 'var(--z-color-success)'}, **{'data-i18n': 'doc.sw.h6.frontend'}),
                    html.Pre("""pages/
├── dashboard/        # Interfaz de medición en tiempo real
├── simulator/        # Calculadora de impedancia RLC
├── documentation/    # Documentación integrada de usuario
└── common/          # Componentes UI reutilizables""", style={
                        'background': 'var(--z-color-bg-card)',
                        'color': 'var(--z-color-success)',
                        'padding': '15px',
                        'borderRadius': '8px',
                        'fontFamily': 'monospace',
                        'fontSize': '0.85rem',
                        'lineHeight': '1.5'
                    })
                ], style={'background': 'var(--z-color-success-subtle)', 'padding': '20px', 'borderRadius': '12px', 'border': '2px solid var(--z-color-success)'})
            ])
        ], style={'marginBottom': '40px'}),
        
        # Biblioteca Python
        html.Div([
            html.H5("Biblioteca Python - lib/admx2001.py", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h5.library'}),
            html.P("La clase ADMX2001 proporciona 43 métodos para control completo del dispositivo:", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '15px'}),
            html.Div([
                html.Div([
                    html.H6("Conexión y Comunicación:", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h6.connection'}),
                    html.Ul([
                        html.Li([html.Code("connect()"), " - Establecer conexión serial"]),
                        html.Li([html.Code("disconnect()"), " - Cerrar conexión"]),
                        html.Li([html.Code("send_command(cmd)"), " - Enviar comando CLI"]),
                        html.Li([html.Code("check_connection()"), " - Verificar estado de conexión"]),
                        html.Li([html.Code("reconnect()"), " - Reconectar automáticamente"]),
                        html.Li([html.Code("get_idn()"), " - Obtener identificación del dispositivo"]),
                        html.Li([html.Code("get_version()"), " - Obtener versión de firmware"])
                    ], style={'color': 'var(--z-color-text-secondary)', 'fontSize': '0.9rem'})
                ], style={'marginBottom': '20px'}),
                
                html.Div([
                    html.H6("Configuración de Medición:", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h6.measurement_config'}),
                    html.Ul([
                        html.Li([html.Code("set_frequency(freq)"), " - Configurar frecuencia (0.2 Hz - 10 MHz)"]),
                        html.Li([html.Code("set_magnitude(mag)"), " - Configurar amplitud de señal (0 - 2.5 V pk)"]),
                        html.Li([html.Code("set_offset(offset)"), " - Configurar offset DC (±2.5 V)"]),
                        html.Li([html.Code("set_average(avg)"), " - Configurar promediado (1-256 muestras)"]),
                        html.Li([html.Code("set_count(count)"), " - Número de lecturas por medición"]),
                        html.Li([html.Code("set_display_mode(mode)"), " - Modo de display (0-17)"])
                    ], style={'color': 'var(--z-color-text-secondary)', 'fontSize': '0.9rem'})
                ], style={'marginBottom': '20px'}),
                
                html.Div([
                    html.H6("Control de Ganancia:", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h6.gain_control'}),
                    html.Ul([
                        html.Li([html.Code("set_gain_auto()"), " - Activar auto-ranging"]),
                        html.Li([html.Code("set_gain_manual(ch0, ch1)"), " - Configurar ganancias manualmente"]),
                        html.Li([html.Code("set_gain(channel, gain)"), " - Configurar ganancia específica"]),
                        html.Li([html.Code("recommend_impedance_range(z)"), " - Recomendar ganancia para impedancia"])
                    ], style={'color': 'var(--z-color-text-secondary)', 'fontSize': '0.9rem'})
                ], style={'marginBottom': '20px'}),
                
                html.Div([
                    html.H6("Mediciones:", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h6.measurements'}),
                    html.Ul([
                        html.Li([html.Code("measure_impedance()"), " - Medición de impedancia AC"]),
                        html.Li([html.Code("measure()"), " - Retorna tupla (valor1, valor2)"]),
                        html.Li([html.Code("measure_temperature()"), " - Medir temperatura interna"]),
                        html.Li([html.Code("measure_dcr()"), " - Medición de resistencia DC"]),
                        html.Li([html.Code("parse_impedance_response()"), " - Parsear respuesta del dispositivo"])
                    ], style={'color': 'var(--z-color-text-secondary)', 'fontSize': '0.9rem'})
                ], style={'marginBottom': '20px'}),
                
                html.Div([
                    html.H6("Barridos:", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h6.sweeps'}),
                    html.Ul([
                        html.Li([html.Code("configure_sweep(type, start, end, points, scale)"), " - Configurar barrido"]),
                        html.Li([html.Code("perform_sweep(timeout)"), " - Ejecutar barrido y retornar datos"]),
                        html.Li([html.Code("disable_sweep()"), " - Deshabilitar modo barrido"])
                    ], style={'color': 'var(--z-color-text-secondary)', 'fontSize': '0.9rem'})
                ], style={'marginBottom': '20px'}),
                
                html.Div([
                    html.H6("Utilidades:", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h6.utilities'}),
                    html.Ul([
                        html.Li([html.Code("set_mdelay(ms)"), " - Retardo entre mediciones"]),
                        html.Li([html.Code("set_tdelay(ms)"), " - Retardo después de trigger"]),
                        html.Li([html.Code("selftest(run)"), " - Ejecutar/ver self-test"]),
                        html.Li([html.Code("reset()"), " - Reset del dispositivo"]),
                        html.Li([html.Code("get_help(cmd)"), " - Obtener ayuda de comando"]),
                        html.Li([html.Code("get_status()"), " - Obtener estado completo del dispositivo"])
                    ], style={'color': 'var(--z-color-text-secondary)', 'fontSize': '0.9rem'})
                ])
            ], style={
                'background': 'var(--z-color-bg-card)',
                'borderRadius': '12px',
                'border': '1px solid var(--z-color-border)',
                'padding': '20px',
                'marginBottom': '20px'
            })
        ], style={'marginBottom': '40px'}),
        
        # Ejemplos de código
        html.Div([
            html.H5("Ejemplos de Código Python", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h5.code_examples'}),
            
            html.H6("1. Conexión y Medición Simple:", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h6.ex1_simple'}),
            html.Pre("""from lib import ADMX2001

# Inicializar y conectar
device = ADMX2001(port='/dev/ttyUSB0', baudrate=115200)
device.connect()

# Verificar conexión
identity = device.get_identity()
print(f"Conectado a: {identity}")

# Configurar medición
device.set_frequency(1000)      # 1 kHz
device.set_magnitude(1.0)       # 1 V peak
device.set_average(10)          # Promediar 10 muestras

# Medir impedancia
measurement = device.measure_impedance()
print(f"Z = {measurement['magnitude']:.2f} Ω")
print(f"θ = {measurement['phase']:.2f}°")
print(f"R = {measurement['real']:.2f} Ω")
print(f"X = {measurement['imaginary']:.2f} Ω")

device.disconnect()
""", style={
                'background': 'var(--z-color-bg-card)',
                'color': 'var(--z-color-text-secondary)',
                'padding': '20px',
                'borderRadius': '12px',
                'fontFamily': 'monospace',
                'fontSize': '0.85rem',
                'overflowX': 'auto',
                'lineHeight': '1.5',
                'marginBottom': '20px'
            }),
            
            html.H6("2. Barrido de Frecuencia Logarítmico:", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h6.ex2_sweep'}),
            html.Pre("""from lib import ADMX2001, SweepType, SweepScale

device = ADMX2001(port='/dev/ttyUSB0')
device.connect()

# Configurar barrido logarítmico
device.configure_sweep(
    sweep_type=SweepType.FREQUENCY,
    scale=SweepScale.LOGARITHMIC,
    start=100,          # 100 Hz
    stop=100000,        # 100 kHz
    points=100
)

# Ejecutar barrido
results = device.perform_sweep()

# Procesar resultados
for point in results:
    freq = point['frequency']
    mag = point['magnitude']
    phase = point['phase']
    print(f"{freq:.2f} Hz: |Z| = {mag:.2f} Ω, θ = {phase:.2f}°")

# Exportar a CSV
device.export_csv('medicion.csv', results)

device.disconnect()
""", style={
                'background': 'var(--z-color-bg-card)',
                'color': 'var(--z-color-text-secondary)',
                'padding': '20px',
                'borderRadius': '12px',
                'fontFamily': 'monospace',
                'fontSize': '0.85rem',
                'overflowX': 'auto',
                'lineHeight': '1.5',
                'marginBottom': '20px'
            }),
            
            html.H6("3. Uso del Simulador RLC:", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h6.ex3_rlc'}),
            html.Pre("""from pages.simulator.impedance_calculator import ImpedanceCalculator

# Crear calculadora con rango de frecuencia
calc = ImpedanceCalculator(
    freq_start=10,
    freq_end=100000,
    points=1000
)

# Calcular impedancia para circuito RC serie
Z = calc.rc_series(R=1000, C=1e-6)  # 1kΩ, 1µF

# Obtener datos para gráficos Bode
bode_data = calc.get_bode_data(Z)
magnitude = bode_data['magnitude']
phase = bode_data['phase']

# Obtener datos para gráfico Nyquist
nyquist_data = calc.get_nyquist_data(Z)
real = nyquist_data['real']
imag = nyquist_data['imaginary']

# Calcular resonancia (para circuitos RLC)
Z_rlc = calc.rlc_series(R=100, L=1e-3, C=1e-6)
f_resonance = calc.find_resonance(Z_rlc)
print(f"Frecuencia de resonancia: {f_resonance:.2f} Hz")
""", style={
                'background': 'var(--z-color-bg-card)',
                'color': 'var(--z-color-text-secondary)',
                'padding': '20px',
                'borderRadius': '12px',
                'fontFamily': 'monospace',
                'fontSize': '0.85rem',
                'overflowX': 'auto',
                'lineHeight': '1.5'
            })
        ], style={'marginBottom': '40px'}),
        
        # =============== USO DEL DASHBOARD DE ZORIA ===============
        html.Div([
            html.H5(" Uso del Dashboard de Medición", className="fw-bold mb-3", style={'color': 'var(--z-color-success)'}, **{'data-i18n': 'doc.sw.h5.dashboard'}),
            html.P("El Dashboard es la página principal de ZORIA donde se realizan mediciones en tiempo real y barridos de frecuencia.", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '20px'}),
            
            # Conexión al dispositivo
            html.Div([
                html.H6("1. Conexión al Dispositivo", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h6.db1_connect'}),
                html.Ul([
                    html.Li([html.Strong("Botón \"Conectar ADMX2001\":"), " Hacer clic en el botón principal de conexión"]),
                    html.Li([html.Strong("Detección automática:"), " El sistema detecta puertos USB-Serial disponibles (FTDI, Silicon Labs, CH340)"]),
                    html.Li([html.Strong("Selección manual:"), " Elegir puerto específico si hay múltiples dispositivos"]),
                    html.Li([html.Strong("Verificación:"), " Al conectar exitosamente, aparece información del dispositivo (IDN, versión firmware)"]),
                    html.Li([html.Strong("LED de estado:"), " Indicador verde cuando la conexión está activa"])
                ], style={'color': 'var(--z-color-text-secondary)'})
            ], style={'background': 'var(--z-color-success-subtle)', 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid var(--z-color-success)', 'marginBottom': '20px'}),
            
            # Medición simple
            html.Div([
                html.H6("2. Medición Simple (Punto Único)", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h6.db2_single'}),
                html.Ul([
                    html.Li([html.Strong("Modo de Display:"), " Seleccionar uno de los 18 modos (Z-θ, R-X, Cp-D, Cs-D, Ls-Q, etc.)"]),
                    html.Li([html.Strong("Frecuencia:"), " Configurar frecuencia de medición (0.2 Hz - 10 MHz)"]),
                    html.Li([html.Strong("Magnitud:"), " Ajustar amplitud de señal (0 - 2.5 V pk) o usar auto"]),
                    html.Li([html.Strong("Promediado:"), " Configurar número de promedios (1-256) para reducir ruido"]),
                    html.Li([html.Strong("Botón \"Medir\":"), " Ejecutar medición única - resultados en display numérico grande"]),
                    html.Li([html.Strong("Visualización:"), " Valor principal y secundario según modo (ej: |Z| y θ)"])
                ], style={'color': 'var(--z-color-text-secondary)'})
            ], style={'background': 'var(--z-color-bg-card)', 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid var(--z-color-border)', 'marginBottom': '20px'}),
            
            # Barrido de frecuencia
            html.Div([
                html.H6("3. Barrido de Frecuencia", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h6.db3_sweep'}),
                html.Ul([
                    html.Li([html.Strong("Panel de configuración:"), " Tarjeta \"Configuración de Barrido\" en la parte inferior"]),
                    html.Li([html.Strong("Frecuencia inicial (Hz):"), " Punto de inicio del barrido"]),
                    html.Li([html.Strong("Frecuencia final (Hz):"), " Punto final del barrido"]),
                    html.Li([html.Strong("Número de puntos:"), " Resolución del barrido (10-1000 puntos)"]),
                    html.Li([html.Strong("Escala:"), " Lineal o Logarítmica (logarítmico recomendado para rangos amplios)"]),
                    html.Li([html.Strong("Botón \"Iniciar Barrido\":"), " Ejecutar barrido automático"]),
                    html.Li([html.Strong("Progreso en tiempo real:"), " Barra de progreso muestra avance (% completado)"]),
                    html.Li([html.Strong("Gráficos dinámicos:"), " Bode y Nyquist se actualizan durante el barrido"])
                ], style={'color': 'var(--z-color-text-secondary)'})
            ], style={'background': 'var(--z-color-warning-subtle)', 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid #fb923c', 'marginBottom': '20px'}),
            
            # Gráficos científicos
            html.Div([
                html.H6("4. Gráficos Científicos en Tiempo Real", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h6.db4_graphs'}),
                
                html.Div([
                    html.Strong(" Diagrama de Bode:", style={'color': 'var(--z-color-success)'}),
                    html.Ul([
                        html.Li("Eje X: Frecuencia (escala logarítmica)"),
                        html.Li("Eje Y izquierdo: Magnitud |Z| en dB (línea cyan)"),
                        html.Li("Eje Y derecho: Fase θ en grados (línea rosa)"),
                        html.Li("Interactividad: Zoom, pan, hover para valores exactos"),
                        html.Li("Exportar imagen PNG desde menú del gráfico")
                    ], style={'color': 'var(--z-color-text-secondary)', 'fontSize': '0.9rem'})
                ], className="mb-3"),
                
                html.Div([
                    html.Strong(" Diagrama de Nyquist:", style={'color': 'var(--z-color-success)'}),
                    html.Ul([
                        html.Li("Eje X: Z' (parte real de impedancia en Ω)"),
                        html.Li("Eje Y: -Z'' (parte imaginaria negativa en Ω)"),
                        html.Li("Colormap: Gradiente de color según frecuencia (Viridis)"),
                        html.Li("Útil para: Identificar circuitos RC, RL, resonancia, EIS de baterías"),
                        html.Li("Exportar imagen PNG desde menú")
                    ], style={'color': 'var(--z-color-text-secondary)', 'fontSize': '0.9rem'})
                ])
            ], style={'background': 'var(--z-color-info-subtle)', 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid var(--z-color-primary)', 'marginBottom': '20px'}),
            
            # Exportación de datos
            html.Div([
                html.H6("5. Exportación de Datos", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h6.db5_export'}),
                html.Ul([
                    html.Li([html.Strong("Botón \"Exportar CSV\":"), " Descargar datos del último barrido"]),
                    html.Li([html.Strong("Formato:"), " CSV con columnas: Frecuencia(Hz), Z_real(Ω), Z_imag(Ω), |Z|(Ω), Phase(°)"]),
                    html.Li([html.Strong("Timestamp:"), " Nombre de archivo incluye fecha y hora (ej: sweep_20260209_143025.csv)"]),
                    html.Li([html.Strong("Compatible:"), " Importar en Excel, Python pandas, MATLAB, Origin"])
                ], style={'color': 'var(--z-color-text-secondary)'})
            ], style={'background': 'var(--z-color-success-subtle)', 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid var(--z-color-success)', 'marginBottom': '20px'}),
            
            # Terminal flotante
            html.Div([
                html.H6("6. Terminal CLI Integrada", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h6.db6_cli'}),
                html.Ul([
                    html.Li([html.Strong("Acceso:"), " Presionar ", html.Kbd("Alt + T"), " o botón flotante inferior derecho"]),
                    html.Li([html.Strong("Comandos CLI:"), " Enviar comandos directos al ADMX2001"]),
                    html.Li([html.Strong("Historial:"), " Navegación con flechas arriba/abajo"]),
                    html.Li([html.Strong("Autocompletado:"), " Presionar Tab para sugerencias"]),
                    html.Li([html.Strong("Ejemplos:"), html.Code(" IDN? "), ", ", html.Code(" FREQ 1000 "), ", ", html.Code(" SWEEP? ")])
                ], style={'color': 'var(--z-color-text-secondary)'})
            ], style={'background': 'var(--z-color-warning-subtle)', 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid var(--z-color-warning)', 'marginBottom': '20px'}),
            
            # Características avanzadas
            html.Div([
                html.H6(" Características Avanzadas", className="fw-bold mb-2", style={'color': 'var(--z-color-success)'}, **{'data-i18n': 'doc.sw.h6.db7_adv'}),
                html.Div([
                    html.Div([
                        html.I(className="fas fa-database me-2", style={'color': 'var(--z-color-success)'}),
                        html.Strong("Persistencia de sesión: "),
                        html.Span("Configuración guardada automáticamente (puerto, frecuencia, modo)")
                    ], style={'padding': '10px 0', 'borderBottom': '1px solid var(--z-color-border)'}),
                    html.Div([
                        html.I(className="fas fa-sync-alt me-2", style={'color': 'var(--z-color-success)'}),
                        html.Strong("Reconexión automática: "),
                        html.Span("Al desconectar, reconecta con último puerto usado")
                    ], style={'padding': '10px 0', 'borderBottom': '1px solid var(--z-color-border)'}),
                    html.Div([
                        html.I(className="fas fa-moon me-2", style={'color': 'var(--z-color-success)'}),
                        html.Strong("Tema claro/oscuro: "),
                        html.Span("Botón para cambiar tema de gráficos (optimizado para publicaciones)")
                    ], style={'padding': '10px 0', 'borderBottom': '1px solid var(--z-color-border)'}),
                    html.Div([
                        html.I(className="fas fa-mobile-alt me-2", style={'color': 'var(--z-color-success)'}),
                        html.Strong("Responsive: "),
                        html.Span("Interfaz adaptable a tablets y móviles")
                    ], style={'padding': '10px 0'})
                ], style={'padding': '10px'})
            ], style={'background': 'var(--z-color-bg-card)', 'borderRadius': '12px', 'border': '1px solid var(--z-color-border)'})
        ], style={'marginBottom': '40px'}),
        
        # =============== SIMULADOR RLC ===============
        html.Div([
            html.H5(" Simulador de Circuitos RLC", className="fw-bold mb-3", style={'color': 'var(--z-color-success)'}, **{'data-i18n': 'doc.sw.h5.simulator'}),
            html.P("El Simulador permite calcular y visualizar la respuesta en frecuencia de circuitos RLC antes de realizar mediciones físicas.", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '20px'}),
            
            html.Div([
                html.H6("Uso del Simulador", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h6.sim1_usage'}),
                html.Ol([
                    html.Li([html.Strong("Acceso:"), " Menú lateral → Simulador RLC"]),
                    html.Li([html.Strong("Seleccionar circuito:"), " Dropdown con 10 topologías (RC serie/paralelo, RL serie/paralelo, RLC serie/paralelo, etc.)"]),
                    html.Li([html.Strong("Configurar componentes:"), " Ingresar valores de R(Ω), L(H), C(F)"]),
                    html.Li([html.Strong("Rango de frecuencia:"), " Frecuencia inicial, final y número de puntos (10-10,000,000 Hz)"]),
                    html.Li([html.Strong("Calcular:"), " Presionar botón \"Calcular Impedancia\""]),
                    html.Li([html.Strong("Visualización:"), " Diagramas de Bode y Nyquist actualizados instantáneamente"]),
                    html.Li([html.Strong("Información:"), " Panel inferior muestra impedancia en frecuencias clave (mín, máx, resonancia)"])
                ], style={'color': 'var(--z-color-text-secondary)'})
            ], style={'background': 'var(--z-color-warning-subtle)', 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid var(--z-color-warning)', 'marginBottom': '20px'}),
            
            html.Div([
                html.H6("Circuitos Disponibles", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h6.sim2_circuits'}),
                html.Ul([
                    html.Li("RC Serie / RC Paralelo"),
                    html.Li("RL Serie / RL Paralelo"),
                    html.Li("RLC Serie / RLC Paralelo"),
                    html.Li("Solo R / Solo L / Solo C"),
                    html.Li("Circuitos personalizados con combinaciones")
                ], style={'color': 'var(--z-color-text-secondary)'})
            ], style={'background': 'var(--z-color-info-subtle)', 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid var(--z-color-primary)', 'marginBottom': '20px'}),
            
            html.Div([
                html.H6("Aplicaciones del Simulador", className="fw-bold mb-2", style={'color': 'var(--z-color-success)'}, **{'data-i18n': 'doc.sw.h6.sim3_apps'}),
                html.Ul([
                    html.Li("Predecir respuesta de circuitos antes de construirlos"),
                    html.Li("Comparar mediciones reales vs. teóricas para validación"),
                    html.Li("Diseñar filtros RC/RL con frecuencias de corte específicas"),
                    html.Li("Calcular frecuencia de resonancia de circuitos RLC"),
                    html.Li("Educación: Visualizar comportamiento de componentes pasivos")
                ], style={'color': 'var(--z-color-text-secondary)'})
            ], style={'background': 'var(--z-color-success-subtle)', 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid var(--z-color-success)'})
        ], style={'marginBottom': '40px'}),
        
        # Casos de uso
        html.Div([
            html.H5("Casos de Uso", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h5.use_cases'}),
            html.Div([
                html.Div([
                    html.H6("1. Caracterización de Resonadores RLC", className="fw-bold mb-2", style={'color': 'var(--z-color-success)'}, **{'data-i18n': 'doc.sw.h6.uc1'}),
                    html.P("Medir frecuencia de resonancia, factor de calidad (Q) y ancho de banda en circuitos resonantes para aplicaciones RF y diseño de filtros.", style={'color': 'var(--z-color-text-secondary)', 'fontSize': '0.9rem'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.H6("2. Análisis de Baterías (EIS)", className="fw-bold mb-2", style={'color': 'var(--z-color-success)'}, **{'data-i18n': 'doc.sw.h6.uc2'}),
                    html.P("Espectroscopia de Impedancia Electroquímica para determinar State of Health (SOH) y State of Charge (SOC) en sistemas de gestión de baterías.", style={'color': 'var(--z-color-text-secondary)', 'fontSize': '0.9rem'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.H6("3. Caracterización de Materiales", className="fw-bold mb-2", style={'color': 'var(--z-color-success)'}, **{'data-i18n': 'doc.sw.h6.uc3'}),
                    html.P("Medir propiedades dieléctricas, conductividad y tangente de pérdida de materiales en función de la frecuencia.", style={'color': 'var(--z-color-text-secondary)', 'fontSize': '0.9rem'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.H6("4. Diseño de Filtros y Redes de Acoplamiento", className="fw-bold mb-2", style={'color': 'var(--z-color-success)'}, **{'data-i18n': 'doc.sw.h6.uc4'}),
                    html.P("Verificar impedancia característica, pérdida de inserción y parámetros S de filtros y redes de acoplamiento de impedancia.", style={'color': 'var(--z-color-text-secondary)', 'fontSize': '0.9rem'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.H6("5. Desarrollo de Sensores", className="fw-bold mb-2", style={'color': 'var(--z-color-success)'}, **{'data-i18n': 'doc.sw.h6.uc5'}),
                    html.P("Caracterización de sensores impedimétricos para biosensores, sensores químicos y monitoreo ambiental.", style={'color': 'var(--z-color-text-secondary)', 'fontSize': '0.9rem'})
                ])
            ], style={
                'background': 'var(--z-color-success-subtle)',
                'borderRadius': '12px',
                'border': '1px solid var(--z-color-success)',
                'padding': '20px'
            })
        ], style={'marginBottom': '40px'}),
        
        # Atajos de teclado
        html.Div([
            html.H5("Atajos de Teclado", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.sw.h5.shortcuts'}),
            html.Div([
                html.Div([
                    html.Kbd("Alt + T", style={
                        'background': 'var(--z-color-bg-elevated)',
                        'border': '1px solid var(--z-color-border)',
                        'borderRadius': '4px',
                        'padding': '4px 10px',
                        'fontSize': '0.85rem'
                    }),
                    html.Span(" Terminal flotante", style={'color': 'var(--z-color-text-tertiary)', 'marginLeft': '12px'})
                ], style={'padding': '10px 0', 'borderBottom': '1px solid var(--z-color-border)'}),
                html.Div([
                    html.Kbd("Ctrl + L", style={
                        'background': 'var(--z-color-bg-elevated)',
                        'border': '1px solid var(--z-color-border)',
                        'borderRadius': '4px',
                        'padding': '4px 10px',
                        'fontSize': '0.85rem'
                    }),
                    html.Span(" Limpiar gráficos", style={'color': 'var(--z-color-text-tertiary)', 'marginLeft': '12px'})
                ], style={'padding': '10px 0', 'borderBottom': '1px solid var(--z-color-border)'}),
                html.Div([
                    html.Kbd("Esc", style={
                        'background': 'var(--z-color-bg-elevated)',
                        'border': '1px solid var(--z-color-border)',
                        'borderRadius': '4px',
                        'padding': '4px 10px',
                        'fontSize': '0.85rem'
                    }),
                    html.Span(" Cerrar modal/ventana", style={'color': 'var(--z-color-text-tertiary)', 'marginLeft': '12px'})
                ], style={'padding': '10px 0'})
            ], style={
                'background': 'var(--z-color-bg-card)',
                'borderRadius': '12px',
                'border': '1px solid var(--z-color-border)',
                'padding': '10px 25px'
            })
        ])
    ])


# ==================== CONTENIDO: CALIBRACIÓN ====================

def content_matematica_background():
    return html.Div([
        html.Div([
            html.H3([
                html.I(className="fas fa-square-root-alt me-3", style={'color': 'var(--z-color-primary)'}),
                html.Span("Matemática Background: Hardware + Software", **{'data-i18n': 'doc.section.math'})
            ], className="mb-3 fw-bold", style={'color': 'var(--z-color-text-primary)'}),
            html.P([
                "Marco matemático y físico de extremo a extremo: desde el front-end analógico real "
                "del ADMX2001 hasta el pipeline de software de ZORIA (adquisición, streaming, calibración, "
                "sweep segmentado, Bode/Nyquist y ajuste de modelos)."
            ], style={'color': 'var(--z-color-text-secondary)', 'fontSize': '1.05rem', 'marginBottom': '30px'})
        ]),

        info_box([
            html.Strong("Alcance auditado para esta sección:"),
            html.Ul([
                html.Li("Documentación oficial completa (modos, timing, calibración, trigger, firmware)"),
                html.Li("Implementación real del backend: ADMX2001, device_state, utils, calibration"),
                html.Li("Flujo runtime del dashboard: workers, streaming, segmentación, recuperación por saturación"),
                html.Li("Modelos matemáticos de simulación y fitting RC/RLC")
            ], style={'marginBottom': '0'})
        ], "success"),

        html.Div([
            dcc.Markdown(
                r"""
### 1) Núcleo matemático de impedancia

En todo el sistema se trabaja con impedancia compleja:

$$
Z(\omega)=R+jX, \quad Y(\omega)=\frac{1}{Z}=G+jB
$$

$$
|Z|=\sqrt{R^2+X^2}, \quad \theta=\operatorname{atan2}(X,R)
$$

Elementos ideales:

$$
Z_R=R, \qquad Z_L=j\omega L, \qquad Z_C=\frac{1}{j\omega C}=-\frac{j}{\omega C}
$$

Relaciones usadas en modos de display:

- Rectangular de impedancia: $(R, X)$
- Polar de impedancia: $(|Z|, \theta)$
- Rectangular de admitancia: $(G, B)$
- Polar de admitancia: $(|Y|, \theta)$

Factores de pérdidas:

$$
D=\tan(\delta), \qquad Q=\frac{1}{D} \;\; (\text{ideal})
$$
""",
                mathjax=True,
                style={'color': 'var(--z-color-text-secondary)', 'fontSize': '1rem', 'lineHeight': '1.75'}
            )
        ], style={'background': 'var(--z-color-bg-card)', 'padding': '22px', 'borderRadius': '12px', 'border': '1px solid var(--z-color-border)', 'marginBottom': '24px'}),

        html.Div([
            dcc.Markdown(
                r"""
### 2) Física del hardware real (no ideal)

En ZORIA se considera explícitamente el front-end real del evaluador:

- Resistencia de fuente: $100\,\Omega$
- Resistencia de protección: $10\,\Omega$
- Total serie efectivo: $R_s=110\,\Omega$

Por tanto, para una excitación configurada $V_{cfg}$:

$$
V_{DUT}=V_{cfg}\frac{|Z_{DUT}|}{|Z_{DUT}|+110},
\qquad
I_{DUT}=\frac{V_{cfg}}{|Z_{DUT}|+110}
$$

Consecuencia experimental:

- Si $|Z_{DUT}|\ll110\,\Omega$, cae fuerte $V_{DUT}$
- Si $|Z_{DUT}|\gg110\,\Omega$, cae fuerte $I_{DUT}$

Esto fundamenta la lógica de selección de ganancia y autorange para preservar SNR y evitar saturación.

Canal de voltaje (CH0): rangos típicos $\pm2.5V, \pm1.25V, \pm625mV, \pm312.5mV$.

Canal de corriente (CH1): transimpedancias típicas $49.9\Omega, 499\Omega, 4.99k\Omega, 49.9k\Omega$.
""",
                mathjax=True,
                style={'color': 'var(--z-color-text-secondary)', 'fontSize': '1rem', 'lineHeight': '1.75'}
            )
        ], style={'background': 'var(--z-color-info-subtle)', 'padding': '22px', 'borderRadius': '12px', 'border': '1px solid var(--z-color-primary)', 'marginBottom': '24px'}),

        html.Div([
            dcc.Markdown(
                r"""
### 3) Flujo de trabajo real del sistema (end-to-end)

#### A. Conexión y estado global

1. Autodetección de puertos USB-Serial (FTDI/CP210/TTYUSB/TTYACM).
2. Verificación activa con `*idn`.
3. Estado compartido en `device_state` con lock de operación para evitar I/O simultáneo.

#### B. Medición continua

1. Configuración de `display`, `frequency`, `mdelay`, `tdelay`, `magnitude`.
2. Lectura periódica (`measure`) en worker dedicado.
3. Ventana deslizante de datos para actualización en tiempo real.

#### C. Sweep de frecuencia (pipeline robusto)

1. Forzar `setgain auto` para reducir saturación al barrer décadas.
2. Aplicar `average`, `mdelay`, `tdelay` efectivos.
3. Segmentar barridos largos (chunks) para robustez operativa.
4. Streaming de puntos en tiempo real al buffer de sweep.
5. Si hay saturación, reintento con magnitud reducida (estrategia de recuperación).
6. Consolidación final y render de Bode/Nyquist.

#### D. Calibración OSL

1. `open` (obligatorio)
2. `short` (condicionado: recomendado cuando CH1 es 0 o 1)
3. `load` con patrón conocido $(R_t, X_t)$
4. `commit` con contraseña para persistencia en NVM

La calibración es específica de la tupla:

$$
(\text{gain}_{ch0},\;\text{gain}_{ch1},\;f)
$$
""",
                mathjax=True,
                style={'color': 'var(--z-color-text-secondary)', 'fontSize': '1rem', 'lineHeight': '1.75'}
            )
        ], style={'background': 'var(--z-color-bg-card)', 'padding': '22px', 'borderRadius': '12px', 'border': '1px solid var(--z-color-border)', 'marginBottom': '24px'}),

        html.Div([
            dcc.Markdown(
                r"""
### 4) Diagramas Bode y Nyquist (convención usada por ZORIA)

Bode:

$$
|Z|_{dB}=20\log_{10}(|Z|), \qquad \phi_{deg}=\angle Z
$$

Nyquist (impedancia):

$$
x=\Re\{Z\}, \qquad y=-\Im\{Z\}
$$

Interpretación práctica:

- Semiplano con $\Im(Z)<0$: comportamiento dominante capacitivo.
- Semiplano con $\Im(Z)>0$: comportamiento dominante inductivo.
- Arcos no ideales/deprimidos: suelen indicar parásitos, dispersión o no idealidad del DUT.
""",
                mathjax=True,
                style={'color': 'var(--z-color-text-secondary)', 'fontSize': '1rem', 'lineHeight': '1.75'}
            )
        ], style={'background': 'var(--z-color-success-subtle)', 'padding': '22px', 'borderRadius': '12px', 'border': '1px solid var(--z-color-success)', 'marginBottom': '24px'}),

        html.Div([
            dcc.Markdown(
                r"""
### 5) Modelos implementados en software (simulación + fitting)

Modelos ideales usados en simulador:

$$
Z_{RC,serie}=R+\frac{1}{j\omega C},
\qquad
Z_{RC,paralelo}=\frac{R}{1+j\omega RC}
$$

$$
Z_{RL,serie}=R+j\omega L,
\qquad
Z_{RLC,serie}=R+j\omega L+\frac{1}{j\omega C}
$$

Resonancia ideal:

$$
f_0=\frac{1}{2\pi\sqrt{LC}}
$$

Ajuste RC en backend:

- Se ajustan **simultáneamente** partes real e imaginaria.
- Se usan restricciones físicas ($R>0$, $C>0$, y en modelos extendidos $R_{leak}>0$).
- Incluye modelo no ideal tipo serie con fuga: $R + (C \parallel R_{leak})$.
""",
                mathjax=True,
                style={'color': 'var(--z-color-text-secondary)', 'fontSize': '1rem', 'lineHeight': '1.75'}
            )
        ], style={'background': 'var(--z-color-bg-card)', 'padding': '22px', 'borderRadius': '12px', 'border': '1px solid var(--z-color-border)', 'marginBottom': '24px'}),

        html.Div([
            dcc.Markdown(
                r"""
### 6) Tiempo de medición: compromiso velocidad vs precisión

Estimador usado en utilidades:

$$
t_{acq,min}\approx\frac{3}{f},
\qquad
t_{sample}=\max\left(t_{acq,min}, 10\,ms\right)
$$

$$
t_{total}\approx t_{sample}\cdot count + mdelay\cdot count + tdelay + overhead
$$

Promediado (aprox. estadística):

$$
\sigma_{noise}\propto\frac{1}{\sqrt{N_{avg}}}
$$

Es decir, subir `average` mejora ruido, pero incrementa latencia total.

Técnica recomendada en práctica:

1. Sweep rápido inicial (`setgain auto`, delays bajos, average moderado).
2. Identificar subrangos críticos (resonancia, cambios de pendiente, bucles Nyquist).
3. Refinar localmente con mayor promedio y/o delays.
""",
                mathjax=True,
                style={'color': 'var(--z-color-text-secondary)', 'fontSize': '1rem', 'lineHeight': '1.75'}
            )
        ], style={'background': 'var(--z-color-warning-subtle)', 'padding': '22px', 'borderRadius': '12px', 'border': '1px solid #fb923c', 'marginBottom': '24px'}),

        html.Div([
            dcc.Markdown(
                r"""
### 7) Streaming Worker del terminal CLI (lo que faltaba)

Este flujo está implementado como **streaming asíncrono con polling** y no como lectura bloqueante directa en UI.

#### Estado interno (`device_state`)

- Buffer incremental de líneas: `_streaming_buffer`
- Lock de buffer: `_streaming_lock`
- Flag de comando activo: `_command_in_progress`
- Evento de finalización: `_streaming_complete`
- Señal de stop cooperativo: `_stop_requested`
- Mutex global de I/O serie: `_operation_lock`

#### Máquina de estados simplificada

1. `start_streaming_command(cmd)` limpia estado y levanta thread daemon.
2. El thread adquiere `_operation_lock` (exclusión mutua con otras operaciones seriales).
3. Envía comando y entra en bucle de lectura incremental.
4. Limpia ANSI/VT100, filtra eco inicial y detecta prompt `ADMX2001>`.
5. Publica líneas nuevas en `_streaming_buffer`.
6. Al finalizar/error: marca `_streaming_complete`, baja `_command_in_progress` y libera lock.

#### Integración con UI

- `terminal-streaming-interval` hace poll cada 100 ms.
- `get_streaming_lines()` drena buffer y actualiza salida incremental.
- Si llega un nuevo comando y hay streaming activo: auto-stop controlado (`abort` + `stop`).

#### Modelo temporal

Si el polling es cada $\Delta t_{poll}=100\,ms$ y llegan $n_k$ líneas por ciclo:

$$
    \text{throughput}_{ui}\approx\frac{\sum_k n_k}{\sum_k \Delta t_{poll}}
$$

Con latencia visual aproximada en el orden de $\Delta t_{poll}$ más jitter de scheduler.
""",
                mathjax=True,
                style={'color': 'var(--z-color-text-secondary)', 'fontSize': '1rem', 'lineHeight': '1.75'}
            )
        ], style={'background': 'var(--z-color-info-subtle)', 'padding': '22px', 'borderRadius': '12px', 'border': '1px solid #8b5cf6', 'marginBottom': '24px'}),

        html.Div([
            dcc.Markdown(
                r"""
### 8) Streaming Worker del sweep (adquisición científica en tiempo real)

El sweep en ZORIA combina:

1. **Worker de adquisición** (`sweep_worker`)  
2. **Buffer de puntos de sweep** en `device_state`  
3. **Polling rápido** (`sweep-streaming-interval`, 100 ms) para pintar Bode/Nyquist en vivo

#### Flujo real

1. Preconfiguración robusta: `display`, `setgain auto`, `average`, `mdelay`, `tdelay`, `magnitude`.
2. Segmentación para barridos grandes (evita operaciones monolíticas frágiles).
3. Ejecución de `perform_sweep(..., point_callback=...)`.
4. Cada punto callback hace `add_sweep_point(freq, z_real, z_imag, z_mag, phase)`.
5. El callback de UI consume `get_sweep_points()` y actualiza gráficas/progreso.
6. Cierre con `end_sweep_streaming()` o cancelación por usuario/error.

#### Progreso y consistencia

El progreso no es estimado por tiempo fijo; se basa en puntos realmente recibidos:

$$
    \text{progress}(\%) = 100\cdot\frac{N_{recibidos}}{N_{total}}
$$

Esto evita falsos 100% cuando el hardware aún no terminó.

#### Recuperación de fallos incluida

- Saturación ADC / `measurement failed`: reintento con magnitud reducida.
- Sweep "abandonado" (sin puntos nuevos por ventana larga): cierre automático seguro.
- Lock global serial para impedir colisiones con comandos concurrentes.

#### Cadena de datos física → gráfica

Para `display mode = 6`:

$$
\text{measurement}=(R, X),\quad |Z|=\sqrt{R^2+X^2},\quad \phi=\operatorname{atan2}(X,R)
$$

y se grafica en tiempo real:

- Bode: $(f, 20\log_{10}|Z|)$ y $(f,\phi)$
- Nyquist: $(Z', -Z'') = (R, -X)$
""",
                mathjax=True,
                style={'color': 'var(--z-color-text-secondary)', 'fontSize': '1rem', 'lineHeight': '1.75'}
            )
    ], style={'background': 'var(--z-color-bg-card)', 'padding': '22px', 'borderRadius': '12px', 'border': '1px solid var(--z-color-border)', 'marginBottom': '24px'}),

    # ── §9 Diagramas Mermaid ───────────────────────────────────────────────
    html.Div([
        html.H4([
            html.I(className="fas fa-project-diagram me-2", style={'color': 'var(--z-color-primary)'}),
            "9) Diagramas de arquitectura y flujos"
        ], className="fw-bold mb-1", style={'color': 'var(--z-color-primary)', 'fontSize': '1.4rem'}),
        html.P("Cada diagrama cubre una capa del sistema. Los de flujo muestran el camino exacto del dato desde el hardware hasta la UI.",
               style={'color': 'var(--z-color-text-tertiary)', 'fontSize': '0.92rem', 'marginBottom': '24px'}),

        # ── 9.1 Arquitectura general (ancho completo) ───────────────────────
        html.Div([
            html.Div([
                html.Span("9.1", className="diagram-badge"),
                html.Span("Arquitectura general ZORIA + ADMX2001", className="fw-semibold"),
            ], className="diagram-header"),
            html.Div("""graph TD
    U(["Usuario"])

    subgraph FE["Capa de Presentacion  —  pages/*"]
        direction LR
        D["Dashboard"] --- CAL["Calibracion"] --- TERM["Terminal CLI"] --- DOC["Documentacion"]
    end

    subgraph BE["Capa de Negocio  —  lib/*"]
        direction LR
        APP["app.py"] --- DS["device_state.py"] --- ADM["admx2001.py"] --- CALB["calibration.py"]
    end

    subgraph HW["Hardware  —  EVAL-ADMX2001EBZ"]
        direction LR
        MCU["ADMX2001B"] -->|"4-wire sense"| DUT["DUT"]
    end

    U       -->|"Browser / HTTP"| FE
    FE      -->|"callbacks + dcc.Store"| BE
    BE      -->|"UART 115200 bps  /dev/ttyUSBx"| HW

    style U   fill:#1e40af,color:#fff,stroke:#1e3a8a
    style FE  fill:#eff6ff,stroke:#3b82f6,color:#1e293b
    style BE  fill:#f0fdf4,stroke:#22c55e,color:#14532d
    style HW  fill:#fff7ed,stroke:#f97316,color:#7c2d12
    classDef default fill:#f8fafc,stroke:#cbd5e1,color:#1e293b
""", className="mermaid diagram-canvas"),
        ], className="diagram-card diagram-card--blue diagram-card--full"),

        # ── Fila 1: 9.2 + 9.3 ──────────────────────────────────────────────
        html.Div([

            # 9.2
            html.Div([
                html.Div([
                    html.Span("9.2", className="diagram-badge diagram-badge--cyan"),
                    html.Span("Flujo de conexion global", className="fw-semibold"),
                ], className="diagram-header"),
                html.Div("""flowchart TD
    A(["Quick Connect"]) --> B["Escanear puertos USB"]
    B --> C["ADMX2001(port, 115200)"]
    C --> D["send_command('*idn')"]
    D --> E{Respuesta OK?}
    E -->|Si| F["device_state.set_device()"]
    E -->|No| G["Siguiente puerto"]
    G -->|Sin puertos| H(["Error: sin dispositivo"])
    F --> I["Monitor verify_connection()"]
    I --> J{Responde?}
    J -->|No| K(["clear_device()"])
    J -->|Si| I

    classDef ok fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef err fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    classDef default fill:#f0f9ff,stroke:#7dd3fc,color:#0c4a6e
    class F,I ok
    class H,K err
""", className="mermaid diagram-canvas"),
            ], className="diagram-card diagram-card--cyan"),

            # 9.3
            html.Div([
                html.Div([
                    html.Span("9.3", className="diagram-badge diagram-badge--green"),
                    html.Span("Streaming del Terminal CLI", className="fw-semibold"),
                ], className="diagram-header"),
                html.Div("""flowchart TD
    A(["Comando de usuario"]) --> B["handle_terminal_command()"]
    B --> C{Streaming activo?}
    C -->|Si| D["stop_streaming_command()"]
    C -->|No| E
    D --> E["start_streaming_command()"]
    E --> F[["Thread daemon"]]
    F --> G["acquire _operation_lock"]
    G --> H["serial.write + readline loop"]
    H --> I["Limpiar ANSI, filtrar eco"]
    I --> J{Prompt ADMX2001>?}
    J -->|No| H
    J -->|Si| K["_streaming_complete.set()"]
    K -.->|poll 100ms| L(["Render terminal"])

    classDef thread fill:#d1fae5,stroke:#059669,color:#064e3b
    classDef out fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef default fill:#f0fdf4,stroke:#86efac,color:#14532d
    class F thread
    class L out
""", className="mermaid diagram-canvas"),
            ], className="diagram-card diagram-card--green"),

        ], className="diagram-row"),

        # ── Fila 2: 9.4 + 9.5 ──────────────────────────────────────────────
        html.Div([

            # 9.4
            html.Div([
                html.Div([
                    html.Span("9.4", className="diagram-badge diagram-badge--purple"),
                    html.Span("Sweep streaming en tiempo real", className="fw-semibold"),
                ], className="diagram-header"),
                html.Div("""flowchart TD
    A(["Iniciar Barrido"]) --> B["sweep_worker()"]
    B --> C["preconfig + auto-gain"]
    C --> D{N > 200 pts?}
    D -->|Si| E["Segmentar bloques"]
    D -->|No| F
    E --> F["start_sweep_streaming(N)"]
    F --> G["perform_sweep(callback)"]
    G --> H{Saturacion?}
    H -->|Si| I["Retry magnitude x 0.5"]
    I --> G
    H -->|No| J["end_sweep_streaming()"]
    G -.->|point_callback| K["(R,X) -> |Z|, fase"]
    K -.->|poll 100ms| L(["Bode + Nyquist actualizado"])

    classDef cb fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef out fill:#f5f3ff,stroke:#a78bfa,color:#4c1d95
    classDef default fill:#faf5ff,stroke:#c4b5fd,color:#4c1d95
    class K cb
    class L out
""", className="mermaid diagram-canvas"),
            ], className="diagram-card diagram-card--purple"),

            # 9.5
            html.Div([
                html.Div([
                    html.Span("9.5", className="diagram-badge diagram-badge--amber"),
                    html.Span("Calibracion OSL + commit", className="fw-semibold"),
                ], className="diagram-header"),
                html.Div("""flowchart TD
    A(["Wizard: Configuracion"]) --> B["Auto-gain por R_load"]
    B --> S1["PASO 1: OPEN"]
    S1 --> C["H-H / L-L en circuito abierto"]
    C --> D["calibrate open"]
    D --> S2["PASO 2: SHORT"]
    S2 --> E["Cortocircuitar H-H / L-L"]
    E --> F["calibrate short"]
    F --> S3["PASO 3: LOAD"]
    S3 --> G["Conectar R de referencia"]
    G --> H["calibrate rt R xt X"]
    H --> S4["PASO 4: COMMIT"]
    S4 --> I["calibrate commit timestamp"]
    I --> J{"PASSWORD>"}
    J -->|"Analog123"| K["NVM persistida"]
    K --> L(["Calibracion guardada"])

    classDef step fill:#f97316,color:#fff,stroke:#c2410c
    classDef ok fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef default fill:#fffbeb,stroke:#fcd34d,color:#78350f
    class S1,S2,S3,S4 step
    class K,L ok
""", className="mermaid diagram-canvas"),
            ], className="diagram-card diagram-card--amber"),

        ], className="diagram-row"),

        # ── 9.6 Secuencia de locks (ancho completo) ─────────────────────────
        html.Div([
            html.Div([
                html.Span("9.6", className="diagram-badge diagram-badge--red"),
                html.Span("Sincronizacion de locks y concurrencia", className="fw-semibold"),
            ], className="diagram-header"),
            html.Div("""sequenceDiagram
    participant UI as Thread UI (Dash callbacks)
    participant W  as Thread Streaming
    participant S  as Puerto Serial

    UI ->> W  : start_streaming_command(cmd)
    W  ->> W  : acquire _operation_lock
    W  ->> S  : serial.write(cmd)
    loop readline hasta ADMX2001>
        S  -->> W : linea de datos
        W  ->>  W : append _streaming_buffer
    end
    UI ->> W  : poll get_streaming_lines() cada 100ms
    W -->> UI : nuevas lineas -> render incremental
    S -->> W  : prompt ADMX2001> detectado
    W  ->> W  : _streaming_complete.set()
    W  ->> W  : release _operation_lock
    W -->> UI : done -> deshabilitar interval
""", className="mermaid diagram-canvas"),
        ], className="diagram-card diagram-card--red diagram-card--full"),

    ], style={'background': 'var(--z-color-bg-elevated)', 'padding': '28px', 'borderRadius': '16px',
              'border': '1px solid var(--z-color-border)', 'marginBottom': '10px'})
    ])


# ==================== CONTENIDO: CALIBRACIÓN ====================

def content_calibracion():
    return html.Div([
        html.Div([
            html.H3([
                html.I(className="fas fa-balance-scale me-3", style={'color': 'var(--z-color-warning)'}),
                html.Span("Procedimiento de Calibración OSL", **{'data-i18n': 'doc.section.calibration'})
            ], className="mb-3 fw-bold", style={'color': 'var(--z-color-text-primary)'}),
            html.P([
                "La calibración Open/Short/Load (OSL) es esencial para mediciones precisas. ",
                "Elimina los efectos de cables y conectores, proporcionando mediciones precisas del DUT."
            ], style={'color': 'var(--z-color-text-secondary)', 'fontSize': '1.1rem', 'marginBottom': '30px'})
        ]),
        
        # ========== WIZARD DE CALIBRACIÓN EN ZORIA ==========
        html.Div([
            html.H4(" Wizard de Calibración Automatizado en ZORIA", className="fw-bold mb-3", style={'color': 'var(--z-color-success)', 'fontSize': '1.5rem'}, **{'data-i18n': 'doc.cal.h4.wizard'}),
            html.P([
                "ZORIA incluye un ",
                html.Strong("Wizard de Calibración Automatizado"),
                " que simplifica el proceso completo de calibración OSL con ",
                "cálculo automático de ganancias óptimas, guía visual paso a paso y validación en tiempo real."
            ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '20px', 'fontSize': '1.05rem'}),
            
            # Acceso al Wizard
            html.Div([
                html.H6(" Acceso al Wizard", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cal.h6.wizard_access'}),
                html.Ol([
                    html.Li("Navega a la página \"Calibración\" en el menú lateral izquierdo", style={'marginBottom': '8px'}),
                    html.Li("Haz clic en el botón \" Iniciar Wizard de Calibración\"", style={'marginBottom': '8px'}),
                    html.Li("Se abre una ventana arrastrable con 5 pasos guiados")
                ], style={'color': 'var(--z-color-text-secondary)', 'fontSize': '0.95rem'})
            ], style={'background': 'var(--z-color-success-subtle)', 'padding': '20px', 'borderRadius': '12px', 'marginBottom': '25px', 'border': '2px solid var(--z-color-success)'}),
            
            # Pasos del Wizard
            html.Div([
                html.H6(" Pasos del Wizard de Calibración", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cal.h6.wizard_steps'}),
                
                # Paso 1: Configuración
                html.Div([
                    html.Div([
                        html.Span("1", className="badge bg-primary me-2", style={'fontSize': '1.1rem', 'padding': '8px 12px'}),
                        html.Strong("Configuración Automática", style={'fontSize': '1.05rem'})
                    ], className="mb-2"),
                    html.Ul([
                        html.Li([html.Strong("Resistencia de calibración (Ω): "), "Ingresar valor de resistencia patrón (ej: 1000Ω)"]),
                        html.Li([html.Strong("Frecuencia (Hz): "), "Frecuencia a la que se realizará la calibración (ej: 1000 Hz)"]),
                        html.Li([html.Strong(" Cálculo automático de ganancia: "), "El wizard calcula automáticamente las ganancias óptimas CH0 y CH1 basándose en la impedancia ingresada"]),
                        html.Li([html.Strong("Indicador visual: "), "Muestra las ganancias calculadas (ej: CH0: 0, CH1: 1)"]),
                        html.Li("Presionar \"▶ Iniciar Calibración\" para continuar al siguiente paso")
                    ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '0', 'fontSize': '0.9rem'})
                ], style={'background': 'var(--z-color-info-subtle)', 'padding': '18px', 'borderRadius': '10px', 'marginBottom': '15px', 'border': '1px solid var(--z-color-primary)'}),
                
                # Paso 2: Open
                html.Div([
                    html.Div([
                        html.Span("2", className="badge bg-info me-2", style={'fontSize': '1.1rem', 'padding': '8px 12px'}),
                        html.Strong("Open Calibration", style={'fontSize': '1.05rem'})
                    ], className="mb-2"),
                    html.Ul([
                        html.Li([html.Strong("Conexión: "), "H_CUR con H_POT (cable corto), L_CUR con L_POT (cable corto)"]),
                        html.Li([html.Strong("Separación: "), "Dejar pares H y L separados (circuito abierto)"]),
                        html.Li([html.I(className="fas fa-eye me-1"), "El wizard muestra ", html.Strong("diagrama visual animado"), " con las conexiones exactas"]),
                        html.Li("Presionar \"Ejecutar Open\" → barra de progreso en tiempo real"),
                        html.Li([html.I(className="fas fa-check-circle me-1", style={'color': 'var(--z-color-success)'}), "Validación automática de resultados al completar"])
                    ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '0', 'fontSize': '0.9rem'})
                ], style={'background': 'var(--z-color-success-subtle)', 'padding': '18px', 'borderRadius': '10px', 'marginBottom': '15px', 'border': '1px solid #14b8a6'}),
                
                # Paso 3: Short
                html.Div([
                    html.Div([
                        html.Span("3", className="badge bg-warning text-dark me-2", style={'fontSize': '1.1rem', 'padding': '8px 12px'}),
                        html.Strong("Short Calibration", style={'fontSize': '1.05rem'})
                    ], className="mb-2"),
                    html.Ul([
                        html.Li([html.Strong("Conexión: "), "Conectar ", html.Strong("TODOS los terminales juntos"), " con un cable (H_CUR, H_POT, L_POT, L_CUR)"]),
                        html.Li([html.Strong(" Reducción automática: "), "El wizard reduce la magnitud a 0.2V ", html.Strong("automáticamente"), " para proteger el circuito"]),
                        html.Li([html.I(className="fas fa-eye me-1"), "Diagrama visual muestra cortocircuito entre todos los terminales"]),
                        html.Li("Presionar \"Ejecutar Short\" → progreso con animación"),
                        html.Li([html.I(className="fas fa-info-circle me-1", style={'color': 'var(--z-color-warning)'}), "Solo necesario para ganancias CH1 = 0 o 1"])
                    ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '0', 'fontSize': '0.9rem'})
                ], style={'background': 'var(--z-color-warning-subtle)', 'padding': '18px', 'borderRadius': '10px', 'marginBottom': '15px', 'border': '1px solid var(--z-color-warning)'}),
                
                # Paso 4: Load
                html.Div([
                    html.Div([
                        html.Span("4", className="badge bg-success me-2", style={'fontSize': '1.1rem', 'padding': '8px 12px'}),
                        html.Strong("Load Calibration", style={'fontSize': '1.05rem'})
                    ], className="mb-2"),
                    html.Ul([
                        html.Li([html.Strong("Resistencia patrón: "), "Conectar resistencia de calibración entre terminales H y L"]),
                        html.Li([html.Strong("Valor mostrado: "), "El wizard muestra el valor configurado en pantalla grande (ej: ", html.Code("1000 Ω"), ")"]),
                        html.Li([html.I(className="fas fa-diagram-project me-1"), "Diagrama interactivo con símbolo de resistencia"]),
                        html.Li([html.Strong(" Medición automática: "), "El sistema mide automáticamente R y X de la carga"]),
                        html.Li("Presionar \"Ejecutar Load\" → resultados en tiempo real"),
                        html.Li([html.I(className="fas fa-check-circle me-1", style={'color': 'var(--z-color-success)'}), "Muestra valores medidos: R real, X reactiva"])
                    ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '0', 'fontSize': '0.9rem'})
                ], style={'background': 'var(--z-color-success-subtle)', 'padding': '18px', 'borderRadius': '10px', 'marginBottom': '15px', 'border': '1px solid var(--z-color-success)'}),
                
                # Paso 5: Guardar
                html.Div([
                    html.Div([
                        html.Span("5", className="badge bg-dark me-2", style={'fontSize': '1.1rem', 'padding': '8px 12px'}),
                        html.Strong("Guardar Calibración", style={'fontSize': '1.05rem'})
                    ], className="mb-2"),
                    html.Ul([
                        html.Li([html.Strong("Nombre descriptivo: "), "Asignar nombre (ej: \"Cal_1kHz_1kOhm_20260209\")"]),
                        html.Li([html.Strong(" Commit a Flash: "), "Guardar permanentemente en memoria no volátil del dispositivo"]),
                        html.Li([html.Strong(" Password: "), "Por defecto ", html.Code("Analog123"), " (configurable en settings)"]),
                        html.Li([html.I(className="fas fa-history me-1"), "Historial de calibraciones guardadas en sesión"]),
                        html.Li([html.I(className="fas fa-file-export me-1"), "Botón para exportar calibración a archivo .txt para respaldo"]),
                        html.Li([html.Strong("Validación final: "), "El wizard verifica que todos los pasos se completaron exitosamente"])
                    ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '0', 'fontSize': '0.9rem'})
                ], style={'background': 'var(--z-color-bg-primary)', 'padding': '18px', 'borderRadius': '10px', 'marginBottom': '15px', 'border': '1px solid #64748b'})
            ], style={'background': 'var(--z-color-bg-card)', 'padding': '25px', 'borderRadius': '12px', 'border': '1px solid var(--z-color-border)', 'marginBottom': '25px'}),
            
            # Ventajas del Wizard
            html.Div([
                html.H6(" Ventajas del Wizard Automatizado", className="fw-bold mb-3", style={'color': 'var(--z-color-success)'}, **{'data-i18n': 'doc.cal.h6.wizard_adv'}),
                html.Div([
                    html.Div([
                        html.I(className="fas fa-magic me-2", style={'color': 'var(--z-color-success)', 'fontSize': '1.2rem'}),
                        html.Strong("Cálculo automático de ganancias óptimas"),
                        html.Span(" según la impedancia del DUT", style={'color': 'var(--z-color-text-tertiary)', 'fontSize': '0.9rem', 'marginLeft': '8px'})
                    ], style={'padding': '12px 0', 'borderBottom': '1px solid var(--z-color-border)'}),
                    html.Div([
                        html.I(className="fas fa-eye me-2", style={'color': 'var(--z-color-success)', 'fontSize': '1.2rem'}),
                        html.Strong("Diagramas visuales animados"),
                        html.Span(" para cada paso con conexiones claramente marcadas", style={'color': 'var(--z-color-text-tertiary)', 'fontSize': '0.9rem', 'marginLeft': '8px'})
                    ], style={'padding': '12px 0', 'borderBottom': '1px solid var(--z-color-border)'}),
                    html.Div([
                        html.I(className="fas fa-check-double me-2", style={'color': 'var(--z-color-success)', 'fontSize': '1.2rem'}),
                        html.Strong("Validación automática de resultados"),
                        html.Span(" en cada paso con mensajes de error descriptivos", style={'color': 'var(--z-color-text-tertiary)', 'fontSize': '0.9rem', 'marginLeft': '8px'})
                    ], style={'padding': '12px 0', 'borderBottom': '1px solid var(--z-color-border)'}),
                    html.Div([
                        html.I(className="fas fa-chart-line me-2", style={'color': 'var(--z-color-success)', 'fontSize': '1.2rem'}),
                        html.Strong("Progreso en tiempo real"),
                        html.Span(" con barra de progreso durante mediciones", style={'color': 'var(--z-color-text-tertiary)', 'fontSize': '0.9rem', 'marginLeft': '8px'})
                    ], style={'padding': '12px 0', 'borderBottom': '1px solid var(--z-color-border)'}),
                    html.Div([
                        html.I(className="fas fa-save me-2", style={'color': 'var(--z-color-success)', 'fontSize': '1.2rem'}),
                        html.Strong("Guardado directo en flash"),
                        html.Span(" del dispositivo con un solo clic", style={'color': 'var(--z-color-text-tertiary)', 'fontSize': '0.9rem', 'marginLeft': '8px'})
                    ], style={'padding': '12px 0', 'borderBottom': '1px solid var(--z-color-border)'}),
                    html.Div([
                        html.I(className="fas fa-history me-2", style={'color': 'var(--z-color-success)', 'fontSize': '1.2rem'}),
                        html.Strong("Historial persistente"),
                        html.Span(" de calibraciones en sesión del navegador", style={'color': 'var(--z-color-text-tertiary)', 'fontSize': '0.9rem', 'marginLeft': '8px'})
                    ], style={'padding': '12px 0', 'borderBottom': '1px solid var(--z-color-border)'}),
                    html.Div([
                        html.I(className="fas fa-file-export me-2", style={'color': 'var(--z-color-success)', 'fontSize': '1.2rem'}),
                        html.Strong("Exportación a archivos"),
                        html.Span(" de respaldo (.txt) con todos los parámetros", style={'color': 'var(--z-color-text-tertiary)', 'fontSize': '0.9rem', 'marginLeft': '8px'})
                    ], style={'padding': '12px 0'})
                ], style={'padding': '15px'})
            ], style={'background': 'var(--z-color-success-subtle)', 'borderRadius': '12px', 'border': '2px solid var(--z-color-success)', 'marginBottom': '40px'}),
            
            html.Hr(style={'margin': '40px 0', 'border': 'none', 'borderTop': '2px solid #e2e8f0'})
        ], style={'marginBottom': '50px'}),
        
        html.Div([
            html.H4("⌨ Calibración Manual por CLI", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)', 'fontSize': '1.5rem'}, **{'data-i18n': 'doc.cal.h4.manual_cli'}),
            html.P([
                "Para usuarios avanzados que prefieren control total, la calibración puede realizarse manualmente ",
                "usando comandos CLI directamente en el terminal del dispositivo."
            ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '30px', 'fontSize': '1.05rem'})
        ]),
        
        # Importancia
        info_box([
            html.Strong("IMPORTANTE: "),
            "Realiza la calibración cada vez que cambies de rango de frecuencia o después de 30 minutos de inactividad. ",
            "Los pasos deben realizarse en orden: ", html.Strong("open → short → load")
        ], "warning"),
        
        # Configuraciones de calibración
        html.Div([
            html.H5("Configuraciones de Calibración", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cal.h5.configurations'}),
            html.P([
                "Cada configuración de front-end (combinación de ganancia ch0 y ch1) necesita calibrarse por separado. ",
                "Hay ", html.Strong("16 combinaciones posibles"), " (4 ganancias ch0 × 4 ganancias ch1)."
            ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '15px'}),
            info_box([
                html.Strong("Info: "),
                "Si usas autorange o solo las 7 combinaciones de ganancia estándar, las otras configuraciones no necesitan calibrarse."
            ], "tip"),
            info_box([
                html.Strong("Frecuencia: "),
                "Cada punto de calibración es para una frecuencia específica. Siempre calibra lo más cerca posible de la frecuencia de prueba deseada."
            ], "warning")
        ], style={'marginBottom': '40px'}),
        
        # Pasos previos
        html.Div([
            html.H5("Preparación para Calibración", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cal.h5.preparation'}),
            html.Ol([
                html.Li("Seleccionar la configuración de medición deseada (ganancia, frecuencia, magnitud, offset)", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '10px'}),
                html.Li([html.Strong("Deshabilitar autorange: "), "setgain ch0 <0-3> y setgain ch1 <0-3>"], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '10px'}),
                html.Li("Configurar promediado a al menos 200 muestras: average 200", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '10px'}),
                html.Li("Asegurar que los switches estén en posiciones DUT y GND", style={'color': 'var(--z-color-text-secondary)'})
            ], style={'marginBottom': '20px'})
        ], style={'marginBottom': '40px'}),
        
        # Pasos de calibración
        html.Div([
            html.H5("Procedimiento Paso a Paso", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cal.h5.step_by_step'}),
            
            # Paso 1: OPEN
            html.Div([
                html.H6([
                    html.Span("1", style={
                        'display': 'inline-block',
                        'width': '32px',
                        'height': '32px',
                        'background': 'var(--z-color-warning)',
                        'color': '#ffffff',
                        'borderRadius': '50%',
                        'textAlign': 'center',
                        'lineHeight': '32px',
                        'fontSize': '1rem',
                        'marginRight': '12px',
                        'fontWeight': '700'
                    }),
                    html.Span("Calibración OPEN", **{'data-i18n': 'doc.cal.h6.open'})
                ], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),
                html.Ol([
                    html.Li("Conectar terminales H_POT/H_CUR juntos y L_POT/L_CUR juntos (sin conectarlos entre sí)", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '10px'}),
                    html.Li([
                        "Ejecutar: ",
                        html.Code("calibrate open", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-warning)', 'padding': '4px 10px', 'borderRadius': '4px', 'marginLeft': '8px'})
                    ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '10px'}),
                    html.Li("Esperar a que complete la medición", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '10px'}),
                    html.Li("Verificar que muestre 'open:Done'", style={'color': 'var(--z-color-text-secondary)'})
                ], style={'marginLeft': '44px'})
            ], style={'background': 'var(--z-color-warning-subtle)', 'padding': '25px', 'borderRadius': '12px', 'border': '2px solid #f59e0b', 'marginBottom': '20px'}),
            
            image_card(IMAGES.get('open_load'), "Configuración OPEN: H_POT/H_CUR juntos, L_POT/L_CUR juntos"),
            
            # Paso 2: SHORT
            html.Div([
                html.H6([
                    html.Span("2", style={
                        'display': 'inline-block',
                        'width': '32px',
                        'height': '32px',
                        'background': 'var(--z-color-warning)',
                        'color': '#ffffff',
                        'borderRadius': '50%',
                        'textAlign': 'center',
                        'lineHeight': '32px',
                        'fontSize': '1rem',
                        'marginRight': '12px',
                        'fontWeight': '700'
                    }),
                    html.Span("Calibración SHORT", **{'data-i18n': 'doc.cal.h6.short'})
                ], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),
                html.Ol([
                    html.Li("Conectar TODAS las terminales juntas (H_CUR, H_POT, L_POT, L_CUR)", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '10px'}),
                    html.Li([
                        html.Strong("Solo cuando ganancia ch1 es 0 o 1"), " (omitir para ganancias 2 y 3)"
                    ], style={'color': 'var(--z-color-danger)', 'marginBottom': '10px'}),
                    html.Li([
                        "Reducir magnitude a 0.2: ",
                        html.Code("magnitude 0.2", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-warning)', 'padding': '4px 10px', 'borderRadius': '4px', 'marginLeft': '8px'})
                    ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '10px'}),
                    html.Li([
                        "Ejecutar: ",
                        html.Code("calibrate short", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-warning)', 'padding': '4px 10px', 'borderRadius': '4px', 'marginLeft': '8px'})
                    ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '10px'}),
                    html.Li("Verificar que muestre 'short:Done'", style={'color': 'var(--z-color-text-secondary)'})
                ], style={'marginLeft': '44px'})
            ], style={'background': 'var(--z-color-warning-subtle)', 'padding': '25px', 'borderRadius': '12px', 'border': '2px solid #f59e0b', 'marginBottom': '20px'}),
            
            # Paso 3: LOAD
            html.Div([
                html.H6([
                    html.Span("3", style={
                        'display': 'inline-block',
                        'width': '32px',
                        'height': '32px',
                        'background': 'var(--z-color-warning)',
                        'color': '#ffffff',
                        'borderRadius': '50%',
                        'textAlign': 'center',
                        'lineHeight': '32px',
                        'fontSize': '1rem',
                        'marginRight': '12px',
                        'fontWeight': '700'
                    }),
                    html.Span("Calibración LOAD", **{'data-i18n': 'doc.cal.h6.load'})
                ], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),
                html.Ol([
                    html.Li([
                        "Restaurar magnitude a 1: ",
                        html.Code("magnitude 1", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-warning)', 'padding': '4px 10px', 'borderRadius': '4px', 'marginLeft': '8px'})
                    ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '10px'}),
                    html.Li([
                        "Conectar impedancia conocida entre cables de medición. ",
                        html.Strong("Tip: "), "Usar resistor con impedancia cercana al DUT esperado"
                    ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '10px'}),
                    html.Li([
                        "Ejecutar: ",
                        html.Code("calibrate rt <R_ohms> xt <X_ohms>", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-warning)', 'padding': '4px 10px', 'borderRadius': '4px', 'marginLeft': '8px'}),
                        html.Br(),
                        html.Span("donde R es la componente resistiva y X la componente reactiva en Ohms", style={'fontSize': '0.9rem', 'color': 'var(--z-color-text-tertiary)', 'marginLeft': '8px'})
                    ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '10px'}),
                    html.Li("Verificar que muestre 'load:Done'", style={'color': 'var(--z-color-text-secondary)'})
                ], style={'marginLeft': '44px'})
            ], style={'background': 'var(--z-color-warning-subtle)', 'padding': '25px', 'borderRadius': '12px', 'border': '2px solid #f59e0b', 'marginBottom': '20px'}),
            
            image_card(IMAGES.get('bnc_load'), "Resistor de calibración conectado entre terminales")
        ]),
        
        # Guardar calibración
        html.Div([
            html.H5("Guardar en Memoria No Volátil", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cal.h5.save_nvm'}),
            html.P("Después de completar los pasos, los coeficientes se generan y almacenan en RAM. Para guardarlos en memoria flash:", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '15px'}),
            html.Pre("""ADMX2001> calibrate commit
PASSWORD> Analog123
commit : success
""", style={
                'background': 'var(--z-color-bg-card)',
                'color': 'var(--z-color-success)',
                'padding': '20px',
                'borderRadius': '12px',
                'fontFamily': 'monospace',
                'fontSize': '0.9rem',
                'marginBottom': '20px'
            }),
            info_box([
                html.Strong(" Password: "),
                "La contraseña por defecto es ", html.Code("Analog123", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '2px 8px', 'borderRadius': '4px'}),
                ". Puede cambiarse con ", html.Code("calibrate password")
            ], "info")
        ], style={'marginBottom': '40px'}),
        
        # ========== COMANDOS DE CALIBRACIÓN EN TERMINAL ==========
        html.Div([
            html.H5([
                html.I(className="fas fa-balance-scale me-2", style={'color': 'var(--z-color-warning)'}),
                html.Span("Comandos de Calibración en Terminal", **{'data-i18n': 'doc.cal.h5.cli_commands'})
            ], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),
            html.P([
                "La calibración Open/Short/Load (OSL) puede realizarse directamente desde el terminal CLI. "
                "Esta sección describe todos los comandos disponibles para calibración manual."
            ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '20px'}),
            
            # Preparación
            html.Div([
                html.H6("Preparación para Calibración", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cal.h6.prep'}),
                html.Ol([
                    html.Li([
                        "Deshabilitar autorange y configurar ganancias manualmente:"
                    ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '8px'}),
                    html.Pre("""ADMX2001> setgain ch0 0
ADMX2001> setgain ch1 1""", style={
                        'background': 'var(--z-color-bg-card)',
                        'color': 'var(--z-color-success)',
                        'padding': '12px',
                        'borderRadius': '6px',
                        'fontFamily': 'monospace',
                        'fontSize': '0.85rem',
                        'marginBottom': '10px'
                    }),
                    html.Li([
                        "Configurar frecuencia de calibración (ej: 1kHz):"
                    ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '8px'}),
                    html.Pre("ADMX2001> frequency 1000", style={
                        'background': 'var(--z-color-bg-card)',
                        'color': 'var(--z-color-success)',
                        'padding': '8px 12px',
                        'borderRadius': '6px',
                        'fontFamily': 'monospace',
                        'fontSize': '0.85rem',
                        'marginBottom': '10px',
                        'display': 'inline-block'
                    }),
                    html.Li([
                        "Configurar promediado alto para mejor precisión:"
                    ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '8px'}),
                    html.Pre("ADMX2001> average 200", style={
                        'background': 'var(--z-color-bg-card)',
                        'color': 'var(--z-color-success)',
                        'padding': '8px 12px',
                        'borderRadius': '6px',
                        'fontFamily': 'monospace',
                        'fontSize': '0.85rem',
                        'marginBottom': '10px',
                        'display': 'inline-block'
                    }),
                    html.Li([
                        "Asegurar que los switches S1 y S2 estén en posición DUT/GND"
                    ], style={'color': 'var(--z-color-text-secondary)'})
                ], style={'marginLeft': '20px'})
            ], style={'background': 'var(--z-color-bg-primary)', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '20px'}),
            
            # Comandos de calibración
            html.Div([
                html.H6("Comandos de Calibración OSL", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cal.h6.osl_cmds'}),
                
                # Calibrate Open
                html.Div([
                    html.Code("calibrate open", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-warning)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P([
                        "Ejecuta calibración de circuito abierto. ",
                        html.Strong("Conexión: "), "H_POT/H_CUR juntos, L_POT/L_CUR juntos (sin conectar H con L)"
                    ], style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px', 'marginBottom': '15px'})
                ]),
                
                # Calibrate Short
                html.Div([
                    html.Code("calibrate short", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-warning)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P([
                        "Ejecuta calibración de cortocircuito. ",
                        html.Strong("Conexión: "), "TODOS los terminales juntos (H_CUR, H_POT, L_POT, L_CUR)",
                        html.Br(),
                        html.Span("Solo para ganancias CH1 = 0 o 1. Reducir magnitud a 0.2V antes.", style={'color': 'var(--z-color-warning)', 'fontSize': '0.9rem'})
                    ], style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px', 'marginBottom': '15px'})
                ]),
                
                # Calibrate Load
                html.Div([
                    html.Code("calibrate rt <R> xt <X>", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-warning)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P([
                        "Ejecuta calibración de carga. ",
                        html.Strong("Parámetros: "),
                        html.Br(),
                        html.Code("rt"), " = componente resistiva en Ohms",
                        html.Br(),
                        html.Code("xt"), " = componente reactiva en Ohms (0 para resistores puros)"
                    ], style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px', 'marginBottom': '15px'}),
                    html.P([
                        html.Strong("Ejemplo: "),
                        html.Code("calibrate rt 1e+3 xt 0", style={'background': 'var(--z-color-bg-elevated)', 'padding': '2px 6px', 'borderRadius': '4px'}),
                        " - Calibra con resistor de 1kΩ"
                    ], style={'color': 'var(--z-color-text-secondary)', 'fontSize': '0.9rem', 'marginLeft': '20px'})
                ]),
                
                # Calibrate Commit
                html.Div([
                    html.Code("calibrate commit [timestamp]", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-warning)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P([
                        "Guarda los coeficientes de calibración en memoria no volátil (flash).",
                        html.Br(),
                        "Solicitará password (por defecto: ", html.Code("Analog123"), ")"
                    ], style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px', 'marginBottom': '15px'}),
                    html.Pre("""ADMX2001> calibrate commit
PASSWORD> Analog123
commit : success""", style={
                        'background': 'var(--z-color-bg-card)',
                        'color': 'var(--z-color-success)',
                        'padding': '12px',
                        'borderRadius': '6px',
                        'fontFamily': 'monospace',
                        'fontSize': '0.85rem',
                        'marginTop': '10px'
                    })
                ]),
                
                info_box([
                    html.Strong("Importante: "),
                    "Los pasos deben realizarse en orden: ", html.Strong("open → short → load → commit"), 
                    ". Cada punto de calibración es específico para la frecuencia y ganancias configuradas."
                ], "warning")
                
            ], style={'background': 'var(--z-color-bg-card)', 'borderRadius': '12px', 'border': '1px solid var(--z-color-border)', 'padding': '20px', 'marginBottom': '20px'}),
            
            # Comandos adicionales de calibración
            html.Div([
                html.H6("Comandos Adicionales de Calibración", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cal.h6.additional_cmds'}),
                
                html.Div([
                    html.Code("calibrate list", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Lista todas las frecuencias con datos de calibración guardados en flash", style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px', 'marginBottom': '15px'})
                ]),
                
                html.Div([
                    html.Code("calibrate list <freq>", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Muestra qué configuraciones de ganancia están calibradas para una frecuencia específica", style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px', 'marginBottom': '15px'})
                ]),
                
                html.Div([
                    html.Code("calibrate reload", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Carga los coeficientes de la frecuencia más cercana desde la memoria flash", style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px', 'marginBottom': '15px'})
                ]),
                
                html.Div([
                    html.Code("calibrate switch <evalkit|default>", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P([
                        "Cambia entre coeficientes precargados (evalkit) o coeficientes de usuario (default)",
                        html.Br(),
                        html.Span("Los coeficientes precargados pueden no aplicar a tu configuración específica.", style={'color': 'var(--z-color-text-tertiary)', 'fontSize': '0.85rem'})
                    ], style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px', 'marginBottom': '15px'})
                ]),
                
                html.Div([
                    html.Code("resetcal", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-danger)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Borra el conjunto de calibración cargado actualmente en RAM (no afecta flash)", style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px', 'marginBottom': '15px'})
                ]),
                
                html.Div([
                    html.Code("calibrate erase", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-danger)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P([
                        html.Strong("¡PELIGRO! "), "Elimina PERMANENTEMENTE todos los conjuntos de calibración de la flash. Requiere password.",
                        html.Br(),
                        html.Span("Use con extrema precaución.", style={'color': 'var(--z-color-danger)', 'fontWeight': 'bold'})
                    ], style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px'})
                ])
            ], style={'background': 'var(--z-color-bg-primary)', 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid var(--z-color-border)', 'marginBottom': '20px'}),
            
            # Ejemplo completo de calibración en terminal
            html.Div([
                html.H6("Ejemplo Completo de Calibración en Terminal", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cal.h6.terminal_example'}),
                html.P("Calibración a 1kHz con resistor de 1kΩ (configuración CH0=0, CH1=1):", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '15px'}),
                html.Pre("""# 1. Configurar ganancias (autorange OFF durante calibración)
ADMX2001> setgain ch0 0
voltGain = 0

ADMX2001> setgain ch1 1
currGain = 1

# 2. Configurar frecuencia y promediado
ADMX2001> frequency 1000
frequency = 1.0000kHz

ADMX2001> average 200
average = 200

# 3. CALIBRACIÓN OPEN
# Conectar: H_POT/H_CUR juntos, L_POT/L_CUR juntos
ADMX2001> calibrate open
0,-1.117998e-09,1.162904e-06
Frequency = 1.0000kHz
Cal Temp: 41.4 deg C
open:Done
short:Not Done
load:Not Done

# 4. CALIBRACIÓN SHORT (solo para CH1 = 0 o 1)
# Reducir magnitud para proteger el circuito
ADMX2001> magnitude 0.2
magnitude = 0.2000

# Conectar: TODOS los terminales juntos
ADMX2001> calibrate short
0,2.075835e-02,1.224807e-02
Frequency = 1.0000kHz
Cal Temp: 41.4 deg C
open:Done
short:Done
load:Not Done

# 5. CALIBRACIÓN LOAD
# Restaurar magnitud
ADMX2001> magnitude 1
magnitude = 1.0000

# Conectar: Resistor 1kΩ entre terminales H y L
ADMX2001> calibrate rt 1000 xt 0
0,1.000381e+03,-1.254483e+00
Frequency = 1.0000kHz
Cal Temp: 41.5 deg C
open:Done
short:Done
load:Done

# 6. GUARDAR EN FLASH
ADMX2001> calibrate commit
PASSWORD> Analog123
commit : success

# 7. Verificación
ADMX2001> display 6
ADMX2001> z
0,1.000021e+03,8.220137e-01""", style={
                    'background': 'var(--z-color-bg-card)',
                    'color': 'var(--z-color-text-secondary)',
                    'padding': '20px',
                    'borderRadius': '12px',
                    'fontFamily': 'monospace',
                    'fontSize': '0.85rem',
                    'overflowX': 'auto',
                    'lineHeight': '1.5'
                })
            ], style={'marginBottom': '20px'}),
            
            info_box([
                html.Strong("Consejo: "),
                "Usa el comando ", html.Code("calibrate list"), " después de guardar para verificar que la calibración se almacenó correctamente. "
                "La capacidad de almacenamiento es de 25 conjuntos (EEPROM) o 450 conjuntos (Flash) dependiendo del módulo."
            ], "tip")
            
        ], style={'marginBottom': '40px'}),
        
        # Ejemplo completo
        html.Div([
            html.H5("Ejemplo Completo de Calibración", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cal.h5.complete_example'}),
            html.P("Calibrar configuración de ganancia (ch0=0, ch1=1) a 100kHz con resistor de 1kΩ:", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '15px'}),
            html.Pre("""ADMX2001> setgain ch0 0
voltGain = 0

ADMX2001> setgain ch1 1
currGain = 1

ADMX2001> frequency 100
frequency = 100.0000kHz

ADMX2001> magnitude 1
magnitude = 1.0000

ADMX2001> offset 0
Offset = 0.0000

ADMX2001> average 200
average = 200

ADMX2001> tdelay 200
triggerDelay = 200.0000msec

# --- Conectar carga OPEN ahora ---
ADMX2001> calibrate open
0,-1.117998e-09,1.162904e-06
Frequency = 100.0000kHz
Cal Temp: 41.4 deg C
open:Done
short:Not Done
load:Not Done

ADMX2001> magnitude 0.2
magnitude = 0.2000

# --- Conectar carga SHORT ahora ---
ADMX2001> calibrate short
0,2.075835e-02,1.224807e-02
Frequency = 100.0000kHz
Cal Temp: 41.4 deg C
open:Done
short:Done
load:Not Done

ADMX2001> magnitude 1
magnitude = 1.0000

# --- Conectar resistor 1kΩ ahora ---
ADMX2001> calibrate rt 1e+3 xt 0
0,1.010381e+03,-1.254483e+01
Frequency = 100.0000kHz
Cal Temp: 41.5 deg C
open:Done
short:Done
load:Done

ADMX2001> calibrate commit 1689959855
PASSWORD> Analog123
commit : success

# --- Verificación ---
ADMX2001> display 6
Measurement model: 6 - Impedance in rectangular coordinates (Rs,Xs)

ADMX2001> z
0,1.000021e+03,8.220137e-01
""", style={
                'background': 'var(--z-color-bg-card)',
                'color': 'var(--z-color-text-secondary)',
                'padding': '20px',
                'borderRadius': '12px',
                'fontFamily': 'monospace',
                'fontSize': '0.85rem',
                'overflowX': 'auto',
                'lineHeight': '1.5'
            })
        ], style={'marginBottom': '40px'}),
        
        # Calibración sobre frecuencia
        html.Div([
            html.H5("Calibración sobre Frecuencia", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cal.h5.freq_cal'}),
            html.P([
                "Desde firmware versión 1.2.2, se soporta calibración en múltiples puntos de frecuencia. ",
                "Esto permite calibrar todas las 16 configuraciones de ganancia en varias frecuencias."
            ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '15px'}),
            html.Div([
                html.H6("Comandos Adicionales:", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cal.h6.additional_cal'}),
                html.Ul([
                    html.Li([
                        html.Code("calibrate list", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-warning)', 'padding': '2px 8px', 'borderRadius': '4px'}),
                        " - Reporta todas las frecuencias con datos guardados"
                    ]),
                    html.Li([
                        html.Code("calibrate reload", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-warning)', 'padding': '2px 8px', 'borderRadius': '4px'}),
                        " - Carga coeficientes de frecuencia más cercana desde flash"
                    ]),
                    html.Li([
                        html.Code("resetcal", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-warning)', 'padding': '2px 8px', 'borderRadius': '4px'}),
                        " - Borra solo el conjunto cargado en RAM"
                    ]),
                    html.Li([
                        html.Code("calibrate erase", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-warning)', 'padding': '2px 8px', 'borderRadius': '4px'}),
                        " - Elimina TODOS los conjuntos permanentemente (requiere password)"
                    ])
                ], style={'color': 'var(--z-color-text-secondary)'})
            ], style={'background': 'var(--z-color-bg-primary)', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '15px'}),
            html.P([
                html.Strong("Capacidad de almacenamiento:"),
                html.Br(),
                "• Módulos con EEPROM: 25 conjuntos de calibración",
                html.Br(),
                "• Módulos con Flash: 450 conjuntos de calibración"
            ], style={'color': 'var(--z-color-text-secondary)', 'marginTop': '15px'})
        ], style={'marginBottom': '40px'}),
        
        # Coeficientes precargados
        html.Div([
            html.H5("Conjuntos de Calibración Precargados", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cal.h5.preloaded'}),
            html.P("Algunos módulos envían con coeficientes de calibración precargados:", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '15px'}),
            html.Pre("""ADMX2001> calibrate switch evalkit    # Usar coeficientes precargados
ADMX2001> calibrate switch default    # Usar coeficientes de usuario
""", style={
                'background': 'var(--z-color-bg-card)',
                'color': 'var(--z-color-success)',
                'padding': '15px',
                'borderRadius': '8px',
                'fontFamily': 'monospace',
                'fontSize': '0.9rem'
            }),
            info_box([
                html.Strong("Advertencia: "),
                "Los coeficientes precargados pueden no aplicar a tu configuración de prueba específica y su precisión no está garantizada."
            ], "warning")
        ])
    ])


# ==================== CONTENIDO: CLI ====================

def content_cli():
    return html.Div([
        html.Div([
            html.H3([
                html.I(className="fas fa-terminal me-3", style={'color': 'var(--z-color-primary)'}),
                html.Span("Terminal CLI - Interfaz de Línea de Comandos", **{'data-i18n': 'doc.section.cli'})
            ], className="mb-3 fw-bold", style={'color': 'var(--z-color-text-primary)'}),
            html.P([
                "La interfaz de línea de comandos CLI permite control completo del sistema ADMX2001B. ",
                "Usa ", html.Code("help <comando>"), " para obtener ayuda sobre cualquier comando."
            ], style={'color': 'var(--z-color-text-secondary)', 'fontSize': '1.1rem', 'marginBottom': '30px'})
        ]),
        
        # Modos de Display
        html.Div([
            html.H5("Modos de Display de Medición", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cli.h5.display_modes'}),
            html.P("El ADMX2001B retorna resultados en uno de 18 modos de display diferentes. El resultado siempre se reporta en la unidad SI base.", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '15px'}),
            html.Div([
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("Modo", style={'color': 'var(--z-color-text-primary)', 'fontWeight': '600', 'padding': '10px', 'borderBottom': '2px solid var(--z-color-primary)'}),
                            html.Th("Nombre", style={'color': 'var(--z-color-text-primary)', 'fontWeight': '600', 'padding': '10px', 'borderBottom': '2px solid var(--z-color-primary)'}),
                            html.Th("Forma", style={'color': 'var(--z-color-text-primary)', 'fontWeight': '600', 'padding': '10px', 'borderBottom': '2px solid var(--z-color-primary)'}),
                            html.Th("Unidad SI", style={'color': 'var(--z-color-text-primary)', 'fontWeight': '600', 'padding': '10px', 'borderBottom': '2px solid var(--z-color-primary)'})
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([html.Td("0", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("Capacitancia serie y resistencia equivalente", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("Cs, Rs", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)', 'fontFamily': 'monospace'}), html.Td("Farads, Ohms", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("1", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("Capacitancia serie y factor de disipación", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("Cs, D", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)', 'fontFamily': 'monospace'}), html.Td("Farads, adimensional", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("2", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("Capacitancia serie y factor de calidad", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("Cs, Q", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)', 'fontFamily': 'monospace'}), html.Td("Farads, adimensional", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("3", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("Inductancia serie y resistencia equivalente", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("Ls, Rs", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)', 'fontFamily': 'monospace'}), html.Td("Henries, Ohms", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("4", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("Inductancia serie y factor de disipación", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("Ls, D", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)', 'fontFamily': 'monospace'}), html.Td("Henries, adimensional", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("5", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("Inductancia serie y factor de calidad", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("Ls, Q", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)', 'fontFamily': 'monospace'}), html.Td("Henries, adimensional", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("6", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'background': 'var(--z-color-warning-subtle)'}), html.Td("Impedancia en coordenadas rectangulares (default)", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)', 'background': 'var(--z-color-warning-subtle)'}), html.Td("R, X", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)', 'fontFamily': 'monospace', 'background': 'var(--z-color-warning-subtle)'}), html.Td("Ohms, Ohms", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)', 'background': 'var(--z-color-warning-subtle)'})]),
                        html.Tr([html.Td("7", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("Impedancia en magnitud y fase (grados)", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("Z, deg", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)', 'fontFamily': 'monospace'}), html.Td("Ohms, Grados", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("8", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("Impedancia en magnitud y fase (radianes)", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("Z, rad", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)', 'fontFamily': 'monospace'}), html.Td("Ohms, Radianes", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("9", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("Capacitancia paralela y resistencia equivalente", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("Cp, Rp", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)', 'fontFamily': 'monospace'}), html.Td("Farads, Ohms", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("10", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("Capacitancia paralela y factor de disipación", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("Cp, D", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)', 'fontFamily': 'monospace'}), html.Td("Farads, adimensional", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("11", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("Capacitancia paralela y factor de calidad", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("Cp, Q", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)', 'fontFamily': 'monospace'}), html.Td("Farads, adimensional", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("12", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("Inductancia paralela y resistencia equivalente", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("Lp, Rp", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)', 'fontFamily': 'monospace'}), html.Td("Henries, Ohms", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("13", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("Inductancia paralela y factor de disipación", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("Lp, D", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)', 'fontFamily': 'monospace'}), html.Td("Henries, adimensional", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("14", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("Inductancia paralela y factor de calidad", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("Lp, Q", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)', 'fontFamily': 'monospace'}), html.Td("Henries, adimensional", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("15", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("Admitancia en coordenadas rectangulares", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("G, B", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)', 'fontFamily': 'monospace'}), html.Td("Siemens, Siemens", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("16", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("Admitancia en magnitud y fase (grados)", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("Y, deg", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)', 'fontFamily': 'monospace'}), html.Td("Siemens, Grados", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("17", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("Admitancia en magnitud y fase (radianes)", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("Y, rad", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)', 'fontFamily': 'monospace'}), html.Td("Siemens, Radianes", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("18", style={'padding': '8px'}), html.Td("Apagado", style={'padding': '8px', 'color': 'var(--z-color-text-secondary)'}), html.Td("None", style={'padding': '8px', 'color': 'var(--z-color-text-secondary)', 'fontFamily': 'monospace'}), html.Td("None", style={'padding': '8px', 'color': 'var(--z-color-text-secondary)'})])
                    ])
                ], style={'width': '100%', 'borderCollapse': 'collapse', 'fontSize': '0.9rem'})
            ], style={
                'background': 'var(--z-color-bg-card)',
                'borderRadius': '12px',
                'border': '1px solid var(--z-color-border)',
                'padding': '20px',
                'marginBottom': '30px',
                'overflowX': 'auto'
            })
        ]),
        
        # Selección de Ganancia
        html.Div([
            html.H5("Selección de Ganancia y Rango", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cli.h5.gain'}),
            html.P("Por defecto, el ADMX2001B está en modo auto-ranging. Para seleccionar manualmente:", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '15px'}),
            html.Div([
                html.H6("Ganancias de Corriente (Ch1)", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cli.h6.current_gain'}),
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("Ganancia", style={'padding': '8px', 'borderBottom': '2px solid var(--z-color-primary)'}),
                            html.Th("Corriente Máxima", style={'padding': '8px', 'borderBottom': '2px solid var(--z-color-primary)'}),
                            html.Th("Transimpedancia", style={'padding': '8px', 'borderBottom': '2px solid var(--z-color-primary)'})
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([html.Td("0", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("25mA", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("49.9Ω", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("1", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("2.5mA", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("499Ω", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("2", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("250μA", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("4.99kΩ", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("3", style={'padding': '8px'}), html.Td("25μA", style={'padding': '8px', 'color': 'var(--z-color-text-secondary)'}), html.Td("49.9kΩ", style={'padding': '8px', 'color': 'var(--z-color-text-secondary)'})])
                    ])
                ], style={'width': '100%', 'borderCollapse': 'collapse', 'marginBottom': '20px'}),
                
                html.H6("Ganancias de Voltaje (Ch0)", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cli.h6.voltage_gain'}),
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("Ganancia", style={'padding': '8px', 'borderBottom': '2px solid var(--z-color-primary)'}),
                            html.Th("Rango Máximo", style={'padding': '8px', 'borderBottom': '2px solid var(--z-color-primary)'}),
                            html.Th("Factor de Ganancia", style={'padding': '8px', 'borderBottom': '2px solid var(--z-color-primary)'})
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([html.Td("0", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("±2.5V", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("1", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("1", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("±1.25V", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("2", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("2", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("±625mV", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'}), html.Td("4", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("3", style={'padding': '8px'}), html.Td("±312.5mV", style={'padding': '8px', 'color': 'var(--z-color-text-secondary)'}), html.Td("8", style={'padding': '8px', 'color': 'var(--z-color-text-secondary)'})])
                    ])
                ], style={'width': '100%', 'borderCollapse': 'collapse', 'marginBottom': '20px'}),
                
                html.H6("Rangos de Impedancia Recomendados", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cli.h6.impedance_ranges'}),
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("Ganancia Ch0", style={'padding': '8px', 'borderBottom': '2px solid var(--z-color-primary)'}),
                            html.Th("Ganancia Ch1", style={'padding': '8px', 'borderBottom': '2px solid var(--z-color-primary)'}),
                            html.Th("Rango de Impedancia", style={'padding': '8px', 'borderBottom': '2px solid var(--z-color-primary)'})
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([html.Td("3", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("0", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("< 10Ω", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("2", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("0", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("< 25Ω", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("1", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("0", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("< 50Ω", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("0", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("0", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("100Ω a 1kΩ", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("0", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("1", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("1kΩ a 10kΩ", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("0", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("2", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)'}), html.Td("10kΩ a 100kΩ", style={'padding': '8px', 'borderBottom': '1px solid var(--z-color-border)', 'color': 'var(--z-color-text-secondary)'})]),
                        html.Tr([html.Td("0", style={'padding': '8px'}), html.Td("3", style={'padding': '8px'}), html.Td("> 100kΩ", style={'padding': '8px', 'color': 'var(--z-color-text-secondary)'})])
                    ])
                ], style={'width': '100%', 'borderCollapse': 'collapse'})
            ], style={
                'background': 'var(--z-color-bg-card)',
                'borderRadius': '12px',
                'border': '1px solid var(--z-color-border)',
                'padding': '20px',
                'marginBottom': '30px',
                'overflowX': 'auto'
            })
        ]),
        
        # Comandos básicos
        html.Div([
            html.H5("Comandos Básicos", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cli.h5.basic_commands'}),
            html.Div([
                html.Div([
                    html.Code("z", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Inicia una medición de impedancia", style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.Code("frequency <Hz>", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Configura frecuencia de medición (0.2 Hz a 10 MHz, 0=DC)", style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.Code("display <0-18>", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Selecciona modo de display de medición", style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.Code("magnitude <V>", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Configura amplitud de señal de excitación (0 a 2.5V pk)", style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.Code("offset <V>", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Configura offset DC (±2.5V)", style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.Code("average <1-256>", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Número de muestras para promediar (reduce ruido)", style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.Code("setgain ch0 <0-3>", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Configura ganancia de voltaje (canal 0)", style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.Code("setgain ch1 <0-3>", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Configura ganancia de corriente (canal 1)", style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.Code("setgain auto", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Activa auto-ranging de ganancia", style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px'})
                ])
            ], style={
                'background': 'var(--z-color-bg-card)',
                'borderRadius': '12px',
                'border': '1px solid var(--z-color-border)',
                'padding': '25px',
                'marginBottom': '30px'
            })
        ]),
        
        # Barridos
        html.Div([
            html.H5("Barridos Paramétricos (Sweeps)", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cli.h5.sweeps'}),
            html.P("El ADMX2001B puede realizar barridos automáticos:", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '15px'}),
            html.Div([
                html.Div([
                    html.Code("sweep_type frequency <inicio> <fin>", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Barrido de frecuencia (común en EIS)", style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px'})
                ], style={'marginBottom': '15px'}),
                html.Div([
                    html.Code("sweep_type bias <inicio> <fin>", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Barrido de offset DC (mediciones C-V)", style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px'})
                ], style={'marginBottom': '15px'}),
                html.Div([
                    html.Code("sweep_scale <log|linear>", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Escala logarítmica o lineal", style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px'})
                ], style={'marginBottom': '15px'}),
                html.Div([
                    html.Code("count <puntos>", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Número de puntos en el barrido", style={'color': 'var(--z-color-text-tertiary)', 'marginTop': '8px'})
                ])
            ], style={
                'background': 'var(--z-color-bg-card)',
                'borderRadius': '12px',
                'border': '1px solid var(--z-color-border)',
                'padding': '20px',
                'marginBottom': '30px'
            })
        ]),
        
        # Ejemplo
        html.Div([
            html.H5("Ejemplo de Uso Completo", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cli.h5.example'}),
            html.Pre("""ADMX2001> frequency 100
frequency = 100.0000kHz

ADMX2001> display 9
Measurement model: 9 - Capacitance and equivalent parallel resistance (Cp,Rp)

ADMX2001> magnitude 1
magnitude = 1.0000

ADMX2001> average 10
average = 10

ADMX2001> count 5
sampleCount = 5

ADMX2001> z
0,5.677640e-13,8.062763e+07
1,5.668012e-13,8.305672e+07
2,5.675237e-13,8.208995e+07
3,5.673763e-13,8.276912e+07
4,5.683635e-13,8.463327e+07
""", style={
                'background': 'var(--z-color-bg-card)',
                'color': 'var(--z-color-text-secondary)',
                'padding': '20px',
                'borderRadius': '12px',
                'fontFamily': 'monospace',
                'fontSize': '0.85rem',
                'overflowX': 'auto',
                'marginBottom': '20px'
            }),
            
            html.H6("Barrido Logarítmico:", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.cli.h6.log_sweep'}),
            html.Pre("""ADMX2001> count 11
ADMX2001> sweep_type frequency 100 1000
ADMX2001> sweep_scale log
ADMX2001> z
1.000000e+05,5.683433e-13,8.149236e+07
1.258925e+05,5.704062e-13,4.727518e+07
...
""", style={
                'background': 'var(--z-color-bg-card)',
                'color': 'var(--z-color-text-secondary)',
                'padding': '20px',
                'borderRadius': '12px',
                'fontFamily': 'monospace',
                'fontSize': '0.85rem',
                'overflowX': 'auto'
            })
        ])
    ])


# ==================== CONTENIDO: FIRMWARE ====================

def content_firmware():
    return html.Div([
        html.Div([
            html.H3([
                html.I(className="fas fa-code me-3", style={'color': 'var(--z-color-danger)'}),
               html.Span("Actualización de Firmware ADMX2001B", **{'data-i18n': 'doc.section.firmware'})
            ], className="mb-3 fw-bold", style={'color': 'var(--z-color-text-primary)'}),
            html.P([
                "El firmware del módulo ADMX2001B es actualizable por el usuario. ",
                "Mantén tu dispositivo actualizado con la última versión para mejoras de rendimiento y correcciones."
            ], style={'color': 'var(--z-color-text-secondary)', 'fontSize': '1.1rem', 'marginBottom': '30px'})
        ]),
        
        info_box([
            html.Strong("ADVERTENCIA CRÍTICA: "),
            "Actualizar entre ciertas versiones de firmware puede causar pérdida de coeficientes de calibración guardados. ",
            "Respalda tu calibración antes de actualizar contactando admx-support@analog.com para asistencia."
        ], "danger"),
        
        # Versiones disponibles
        html.Div([
            html.H5("Versiones de Firmware Disponibles", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.fw.h5.versions'}),
            html.Div([
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("Versión", style={'color': 'var(--z-color-text-primary)', 'fontWeight': '600', 'padding': '12px', 'borderBottom': '2px solid var(--z-color-danger)'}),
                            html.Th("Estado", style={'color': 'var(--z-color-text-primary)', 'fontWeight': '600', 'padding': '12px', 'borderBottom': '2px solid var(--z-color-danger)'}),
                            html.Th("Características Principales", style={'color': 'var(--z-color-text-primary)', 'fontWeight': '600', 'padding': '12px', 'borderBottom': '2px solid var(--z-color-danger)'})
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([
                            html.Td(html.Span("1.3.2", style={'background': 'var(--z-color-success)', 'color': '#ffffff', 'padding': '4px 12px', 'borderRadius': '16px', 'fontSize': '0.9rem', 'fontWeight': '600'}), style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td(html.Span("Estable", style={'color': 'var(--z-color-success)', 'fontWeight': '600'}), style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td("Optimizaciones de tiempo de medición, GUI Python incluida, correcciones menores", style={'padding': '12px', 'color': 'var(--z-color-text-secondary)', 'borderBottom': '1px solid var(--z-color-border)'})
                        ]),
                        html.Tr([
                            html.Td("1.3.1", style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td(html.Span("Estable", style={'color': 'var(--z-color-success)', 'fontWeight': '600'}), style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td("Mejoras sustanciales de ruido, correcciones y más", style={'padding': '12px', 'color': 'var(--z-color-text-secondary)', 'borderBottom': '1px solid var(--z-color-border)'})
                        ]),
                        html.Tr([
                            html.Td("1.2.4", style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td(html.Span("Estable", style={'color': 'var(--z-color-success)', 'fontWeight': '600'}), style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td("Igual que 1.2.2, script de instalación Python añadido", style={'padding': '12px', 'color': 'var(--z-color-text-secondary)', 'borderBottom': '1px solid var(--z-color-border)'})
                        ]),
                        html.Tr([
                            html.Td("1.2.2", style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td(html.Span("Estable", style={'color': 'var(--z-color-success)', 'fontWeight': '600'}), style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td("Calibración sobre frecuencia, salidas digitales configurables, soporte trigger externo", style={'padding': '12px', 'color': 'var(--z-color-text-secondary)', 'borderBottom': '1px solid var(--z-color-border)'})
                        ]),
                        html.Tr([
                            html.Td("1.2.0", style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td(html.Span("Estable", style={'color': 'var(--z-color-success)', 'fontWeight': '600'}), style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td("Correcciones, mejoras de ruido y repetibilidad", style={'padding': '12px', 'color': 'var(--z-color-text-secondary)', 'borderBottom': '1px solid var(--z-color-border)'})
                        ]),
                        html.Tr([
                            html.Td("1.1.1", style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td(html.Span("Legacy", style={'color': 'var(--z-color-text-tertiary)', 'fontWeight': '600'}), style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td("Mismas correcciones que 1.2.0, no compatible con placas con flash", style={'padding': '12px', 'color': 'var(--z-color-text-secondary)', 'borderBottom': '1px solid var(--z-color-border)'})
                        ]),
                        html.Tr([
                            html.Td("1.1.0", style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td(html.Span("Legacy", style={'color': 'var(--z-color-text-tertiary)', 'fontWeight': '600'}), style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td("Interfaz SPI añadida, self test integrado", style={'padding': '12px', 'color': 'var(--z-color-text-secondary)', 'borderBottom': '1px solid var(--z-color-border)'})
                        ]),
                        html.Tr([
                            html.Td("1.0.1", style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td(html.Span("Legacy", style={'color': 'var(--z-color-text-tertiary)', 'fontWeight': '600'}), style={'padding': '12px', 'borderBottom': '1px solid var(--z-color-border)'}),
                            html.Td("Versión inicial", style={'padding': '12px', 'color': 'var(--z-color-text-secondary)', 'borderBottom': '1px solid var(--z-color-border)'})
                        ]),
                        html.Tr([
                            html.Td("1.0.0", style={'padding': '12px'}),
                            html.Td(html.Span("Legacy", style={'color': 'var(--z-color-text-tertiary)', 'fontWeight': '600'}), style={'padding': '12px'}),
                            html.Td("Primera versión de lanzamiento", style={'padding': '12px', 'color': 'var(--z-color-text-secondary)'})
                        ])
                    ])
                ], style={'width': '100%', 'borderCollapse': 'collapse'})
            ], style={
                'background': 'var(--z-color-bg-card)',
                'borderRadius': '12px',
                'border': '1px solid var(--z-color-border)',
                'padding': '20px',
                'marginBottom': '30px',
                'overflowX': 'auto'
            })
        ]),
        
        # Equipo requerido
        html.Div([
            html.H5("Equipo y Software Requerido", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.fw.h5.requirements'}),
            html.Div([
                html.Div([
                    html.H6("Hardware:", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.fw.h6.hardware'}),
                    html.Ul([
                        html.Li("Placa EVAL-ADMX2001EBZ"),
                        html.Li("Módulo ADMX2001B"),
                        html.Li([html.Strong("Intel Altera USB Blaster"), " (programador JTAG)"]),
                        html.Li("Adaptador de corriente 9VDC"),
                        html.Li("Cable USB para USB Blaster")
                    ], style={'color': 'var(--z-color-text-secondary)'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.H6("Software:", className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.fw.h6.software'}),
                    html.Ul([
                        html.Li("Python 3.7 o superior"),
                        html.Li([html.Strong("Intel Quartus Prime Programmer And Tools"), " (última versión)"]),
                        html.Li("Drivers para Altera USB Blaster"),
                        html.Li("Carpeta de firmware conteniendo archivo *.pof")
                    ], style={'color': 'var(--z-color-text-secondary)'})
                ], style={'marginBottom': '20px'})
            ], style={
                'background': 'var(--z-color-bg-primary)',
                'padding': '20px',
                'borderRadius': '12px',
                'border': '1px solid var(--z-color-border)',
                'marginBottom': '30px'
            })
        ]),
        
        # Método con script
        html.Div([
            html.H5("Método de Actualización con Script Python", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.fw.h5.python_method'}),
            html.P([
                html.Strong("Versiones 1.2.4+"), " incluyen un script de instalación Python que automatiza el proceso:"
            ], style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '15px'}),
            html.Pre("""python admx2001_flash_pof.py --pof "C:\\Analog Devices\\Admx2001Firmware-Relx.y.z\\Firmware\\admx_lcr_encrypted.pof"
""", style={
                'background': 'var(--z-color-bg-card)',
                'color': 'var(--z-color-success)',
                'padding': '20px',
                'borderRadius': '12px',
                'fontFamily': 'monospace',
                'fontSize': '0.9rem',
                'overflowX': 'auto',
                'marginBottom': '15px'
            }),
            info_box([
                html.Strong("IMPORTANTE: "),
                "NO desconectar la placa ni interrumpir el proceso de programación. ",
                "El proceso toma entre 20-30 segundos. Una interrupción puede dañar permanentemente el módulo."
            ], "danger")
        ], style={'marginBottom': '40px'}),
        
        # Procedimiento manual
        html.Div([
            html.H5("Procedimiento Manual de Actualización", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.fw.h5.manual'}),
            
            html.Div([
                html.H6([
                    html.Span("1", style={
                        'display': 'inline-block',
                        'width': '32px',
                        'height': '32px',
                        'background': 'var(--z-color-danger)',
                        'color': '#ffffff',
                        'borderRadius': '50%',
                        'textAlign': 'center',
                        'lineHeight': '32px',
                        'fontSize': '1rem',
                        'marginRight': '12px',
                        'fontWeight': '700'
                    }),
                    html.Span("Descargar Firmware", **{'data-i18n': 'doc.fw.h6.step1_download'})
                ], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),
                html.P([
                    "Contacta ", html.Strong("admx-support@analog.com"), " para obtener el archivo de programación (*.pof) más reciente."
                ], style={'color': 'var(--z-color-text-secondary)', 'marginLeft': '44px'})
            ], style={'background': 'var(--z-color-danger-subtle)', 'padding': '20px', 'borderRadius': '12px', 'border': '2px solid var(--z-color-danger)', 'marginBottom': '20px'}),
            
            html.Div([
                html.H6([
                    html.Span("2", style={
                        'display': 'inline-block',
                        'width': '32px',
                        'height': '32px',
                        'background': 'var(--z-color-danger)',
                        'color': '#ffffff',
                        'borderRadius': '50%',
                        'textAlign': 'center',
                        'lineHeight': '32px',
                        'fontSize': '1rem',
                        'marginRight': '12px',
                        'fontWeight': '700'
                    }),
                    html.Span("Instalar Software", **{'data-i18n': 'doc.fw.h6.step2_install'})
                ], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),
                html.Ol([
                    html.Li("Descargar e instalar Intel Quartus Prime Programmer", style={'marginBottom': '8px'}),
                    html.Li("Instalar drivers para Altera USB Blaster", style={'marginBottom': '8px'}),
                    html.Li("Verificar Python 3.7+ instalado", style={'marginBottom': '8px'})
                ], style={'color': 'var(--z-color-text-secondary)', 'marginLeft': '44px'})
            ], style={'background': 'var(--z-color-danger-subtle)', 'padding': '20px', 'borderRadius': '12px', 'border': '2px solid var(--z-color-danger)', 'marginBottom': '20px'}),
            
            html.Div([
                html.H6([
                    html.Span("3", style={
                        'display': 'inline-block',
                        'width': '32px',
                        'height': '32px',
                        'background': 'var(--z-color-danger)',
                        'color': '#ffffff',
                        'borderRadius': '50%',
                        'textAlign': 'center',
                        'lineHeight': '32px',
                        'fontSize': '1rem',
                        'marginRight': '12px',
                        'fontWeight': '700'
                    }),
                    html.Span("Conexión de Hardware", **{'data-i18n': 'doc.fw.h6.step3_connect'})
                ], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),
                html.Ol([
                    html.Li("Conectar adaptador de corriente 9VDC a la placa EVAL-ADMX2001EBZ", style={'marginBottom': '8px'}),
                    html.Li("Conectar cable del Altera USB Blaster al conector JTAG de la placa", style={'marginBottom': '8px'}),
                    html.Li("Conectar USB Blaster a la PC", style={'marginBottom': '8px'}),
                    html.Li("Verificar que el LED de power esté encendido", style={'marginBottom': '8px'})
                ], style={'color': 'var(--z-color-text-secondary)', 'marginLeft': '44px'})
            ], style={'background': 'var(--z-color-danger-subtle)', 'padding': '20px', 'borderRadius': '12px', 'border': '2px solid var(--z-color-danger)', 'marginBottom': '20px'}),
            
            html.Div([
                html.H6([
                    html.Span("4", style={
                        'display': 'inline-block',
                        'width': '32px',
                        'height': '32px',
                        'background': 'var(--z-color-danger)',
                        'color': '#ffffff',
                        'borderRadius': '50%',
                        'textAlign': 'center',
                        'lineHeight': '32px',
                        'fontSize': '1rem',
                        'marginRight': '12px',
                        'fontWeight': '700'
                    }),
                    html.Span("Programación", **{'data-i18n': 'doc.fw.h6.step4_program'})
                ], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),
                html.P("Ejecutar el script de programación:", style={'color': 'var(--z-color-text-secondary)', 'marginLeft': '44px', 'marginBottom': '10px'}),
                html.Pre("""python admx2001_flash_pof.py --pof firmware.pof
""", style={
                    'background': 'var(--z-color-bg-card)',
                    'color': 'var(--z-color-success)',
                    'padding': '15px',
                    'borderRadius': '8px',
                    'fontFamily': 'monospace',
                    'fontSize': '0.9rem',
                    'marginLeft': '44px',
                    'marginBottom': '10px'
                }),
                html.P([
                    html.Strong("Duración esperada: "), "20-30 segundos"
                ], style={'color': 'var(--z-color-text-secondary)', 'marginLeft': '44px'})
            ], style={'background': 'var(--z-color-danger-subtle)', 'padding': '20px', 'borderRadius': '12px', 'border': '2px solid var(--z-color-danger)', 'marginBottom': '20px'}),
            
            html.Div([
                html.H6([
                    html.Span("5", style={
                        'display': 'inline-block',
                        'width': '32px',
                        'height': '32px',
                        'background': 'var(--z-color-danger)',
                        'color': '#ffffff',
                        'borderRadius': '50%',
                        'textAlign': 'center',
                        'lineHeight': '32px',
                        'fontSize': '1rem',
                        'marginRight': '12px',
                        'fontWeight': '700'
                    }),
                    html.Span("Verificación", **{'data-i18n': 'doc.fw.h6.step5_verify'})
                ], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),
                html.Ol([
                    html.Li("Desconectar el USB Blaster", style={'marginBottom': '8px'}),
                    html.Li("Conectar cable UART-USB", style={'marginBottom': '8px'}),
                    html.Li("Abrir terminal (TeraTerm, 115200 baud)", style={'marginBottom': '8px'}),
                    html.Li([
                        "Ejecutar comando: ",
                        html.Code("*idn", style={'background': 'var(--z-color-bg-card)', 'color': 'var(--z-color-success)', 'padding': '2px 8px', 'borderRadius': '4px'}),
                        " para verificar la nueva versión"
                    ], style={'marginBottom': '8px'}),
                    html.Li("Verificar self-test (LED verde)", style={'marginBottom': '8px'})
                ], style={'color': 'var(--z-color-text-secondary)', 'marginLeft': '44px'})
            ], style={'background': 'var(--z-color-danger-subtle)', 'padding': '20px', 'borderRadius': '12px', 'border': '2px solid var(--z-color-danger)', 'marginBottom': '20px'})
        ]),
        
        # Obtener archivos
        html.Div([
            html.H5("Cómo Obtener Archivos de Firmware", className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}, **{'data-i18n': 'doc.fw.h5.get_files'}),
            html.P("Los archivos de programación deben solicitarse directamente a Analog Devices:", style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '15px'}),
            html.Div([
                html.Div([
                    html.I(className="fas fa-envelope", style={'color': 'var(--z-color-danger)', 'fontSize': '2rem', 'marginBottom': '15px'}),
                    html.Br(),
                    html.Strong("Email de Soporte:", style={'display': 'block', 'marginBottom': '8px'}),
                    html.A("admx-support@analog.com", href="mailto:admx-support@analog.com", style={'color': 'var(--z-color-primary)', 'textDecoration': 'none', 'fontSize': '1.1rem'})
                ], style={'textAlign': 'center', 'padding': '30px'})
            ], style={
                'background': 'var(--z-color-bg-card)',
                'borderRadius': '12px',
                'border': '2px solid var(--z-color-danger)',
                'marginBottom': '20px'
            })
        ])
    ])


# ==================== COMPONENTES PREMIUM ====================

def hero_section():
    """Hero ejecutivo para documentación"""
    return html.Div([
        html.Div([
            # Badge
            html.Div([
                html.Span("●", style={
                    'color': 'var(--z-footer-accent)',
                    'fontSize': '8px',
                    'marginRight': '12px',
                    'animation': 'pulse 2s infinite'
                }),
                html.Span("DOCUMENTACIÓN OFICIAL", style={
                    'fontSize': '0.75rem',
                    'letterSpacing': '0.3em',
                    'fontWeight': '500',
                    'color': 'var(--z-color-text-tertiary)'
                }, **{'data-i18n': 'doc.hero.badge'})
            ], style={
                'marginBottom': '40px',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center'
            }),
            
            # Título
            html.H1([
                html.Span("Guía ZORIA", style={
                    'display': 'block',
                    'fontSize': 'clamp(3rem, 8vw, 6rem)',
                    'fontWeight': '200',
                    'letterSpacing': '-0.03em',
                    'lineHeight': '0.9',
                    'color': 'var(--z-color-text-primary)',
                    'marginBottom': '10px'
                }, **{'data-i18n': 'doc.hero.title'}),
                html.Span("EVAL-ADMX2001", style={
                    'display': 'block',
                    'fontSize': 'clamp(1rem, 2vw, 1.5rem)',
                    'fontWeight': '300',
                    'letterSpacing': '0.3em',
                    'color': 'var(--z-footer-accent)',
                    'textTransform': 'uppercase'
                })
            ], style={
                'textAlign': 'center',
                'marginBottom': '40px'
            }),
            
            # Línea decorativa
            html.Div(style={
                'width': '60px',
                'height': '1px',
                'background': 'linear-gradient(90deg, transparent, #d4af37, transparent)',
                'margin': '0 auto 40px'
            }),
            
            # Descripción
            html.P([
                html.Span("Documentación completa del sistema de análisis de impedancia.", **{'data-i18n': 'doc.hero.desc1'}),
                html.Br(),
                html.Span("Selecciona una sección para comenzar.", **{'data-i18n': 'doc.hero.desc2'})
            ], style={
                'fontSize': 'clamp(1rem, 1.5vw, 1.25rem)',
                'fontWeight': '300',
                'color': 'var(--z-color-text-secondary)',
                'textAlign': 'center',
                'maxWidth': '600px',
                'margin': '0 auto'
            })
        ], style={
            'maxWidth': '1200px',
            'margin': '0 auto',
            'padding': '100px 40px 60px'
        })
    ], style={
        'background': 'var(--z-color-bg-card)',
        'position': 'relative'
    })


# ==================== CONTENIDO: OVERVIEW ZORIA ====================

def content_overview():
    """
    Sección completa: qué hace ZORIA, beneficios, capacidades y limitaciones.
    """

    # ── Helper local: tarjeta de feature ──────────────────────────────────────
    def feature_card(icon, title, description, color="#3b82f6"):
        return html.Div([
            html.Div([
                html.I(className=f"{icon} fa-lg", style={'color': color}),
            ], style={
                'width': '48px', 'height': '48px',
                'background': f'{color}18',
                'borderRadius': '12px',
                'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center',
                'marginBottom': '16px', 'flexShrink': '0',
            }),
            html.H6(title, className="fw-bold mb-2", style={'color': 'var(--z-color-text-primary)', 'fontSize': '0.95rem'}),
            html.P(description, style={'color': 'var(--z-color-text-tertiary)', 'fontSize': '0.875rem', 'marginBottom': '0', 'lineHeight': '1.6'}),
        ], style={
            'background': 'var(--z-color-bg-card)',
            'border': '1px solid var(--z-color-border)',
            'borderRadius': '12px',
            'padding': '20px',
            'boxShadow': '0 1px 4px rgba(0,0,0,0.06)',
        })

    # ── Helper local: tarjeta benefit/limitation ───────────────────────────────
    def bl_row(icon, color, title, items):
        return html.Div([
            html.Div([
                html.I(className=icon, style={'color': color, 'fontSize': '1.1rem'}),
                html.Span(title, className="fw-bold ms-2", style={'color': 'var(--z-color-text-primary)'}),
            ], style={'marginBottom': '12px', 'display': 'flex', 'alignItems': 'center'}),
            html.Ul([
                html.Li(
                    item if isinstance(item, list) else item,
                    style={'color': 'var(--z-color-text-secondary)', 'marginBottom': '8px', 'lineHeight': '1.6'}
                ) for item in items
            ], style={'paddingLeft': '20px', 'marginBottom': '0'})
        ], style={
            'background': 'var(--z-color-bg-primary)',
            'border': f'1px solid {color}40',
            'borderLeft': f'4px solid {color}',
            'borderRadius': '8px',
            'padding': '18px 20px',
            'marginBottom': '16px',
        })

    # ── Helper local: stat pill ───────────────────────────────────────────────
    def stat_pill(value, label, color="#d4af37"):
        return html.Div([
            html.Div(value, style={'fontSize': '1.8rem', 'fontWeight': '800', 'color': color, 'lineHeight': '1'}),
            html.Div(label, style={'fontSize': '0.75rem', 'color': 'var(--z-color-text-tertiary)', 'marginTop': '4px', 'textAlign': 'center'}),
        ], style={
            'background': 'var(--z-color-bg-card)',
            'border': '1px solid var(--z-color-border)',
            'borderRadius': '12px',
            'padding': '16px 20px',
            'textAlign': 'center',
            'minWidth': '110px',
            'boxShadow': '0 1px 3px rgba(0,0,0,0.06)',
        })

    return html.Div([

        # ── Presentación ─────────────────────────────────────────────────────
        html.Div([
            html.H3([
                html.I(className="fas fa-layer-group me-3", style={'color': 'var(--z-footer-accent)'}),
                html.Span("¿Qué es ZORIA?", **{'data-i18n': 'doc.section.overview'})
            ], className="mb-3 fw-bold", style={'color': 'var(--z-color-text-primary)'}),
            html.P([
                html.Strong("ZORIA", style={'color': 'var(--z-footer-accent)'}),
                " (", html.Em("Z-analyzer Open Responsive Impedance Application"), ") es una aplicación web "
                "de código abierto para el análisis de impedancia de circuitos electrónicos, desarrollada sobre "
                "el ecosistema ", html.Strong("Dash/Plotly"), " de Python. Actúa como interfaz gráfica avanzada "
                "para el kit de evaluación ", html.Strong("EVAL-ADMX2001EBZ"), " de Analog Devices — "
                "sustituyendo la interacción por terminal de texto con un entorno visual moderno, accesible y extensible."
            ], style={'color': 'var(--z-color-text-secondary)', 'fontSize': '1.05rem', 'lineHeight': '1.8', 'marginBottom': '24px'}),

            # Stats rápidos
            html.Div([
                stat_pill("6", "Idiomas", "#d4af37"),
                stat_pill("100+", "Traducciones", "#3b82f6"),
                stat_pill("OSL", "Calibración 3-punt.", "#10b981"),
                stat_pill("Bode+Nyquist", "Diagramas", "#8b5cf6"),
                stat_pill("CLI", "Terminal integrado", "#f59e0b"),
                stat_pill("MIT", "Licencia libre", "#64748b"),
            ], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '12px', 'marginBottom': '32px'}),
        ]),

        # ── Qué hace ZORIA ───────────────────────────────────────────────────
        html.H4([
            html.I(className="fas fa-bolt me-2", style={'color': 'var(--z-footer-accent)'}),
            html.Span("Capacidades principales", **{'data-i18n': 'doc.ov.h4.capabilities'})
        ], className="fw-bold mb-3 mt-2", style={'color': 'var(--z-color-text-primary)'}),

        html.Div([
            feature_card(
                "fas fa-wave-square", "Barrido de frecuencia",
                "Realiza sweeps logarítmicos y lineales desde 1 Hz hasta 300 kHz. "
                "Streaming en tiempo real punto-a-punto directamente desde el dispositivo.",
                "#3b82f6"
            ),
            feature_card(
                "fas fa-chart-line", "Diagramas de Bode y Nyquist",
                "Visualización interactiva de magnitud (dB), fase (°), parte real e imaginaria "
                "con zoom, pan, selección de rango y exportación SVG/PNG.",
                "#8b5cf6"
            ),
            feature_card(
                "fas fa-balance-scale", "Calibración OSL",
                "Procedimiento guiado de tres puntos: Open (circuito abierto), Short (cortocircuito) "
                "y Load (resistencia de referencia). Almacenamiento de múltiples perfiles con nombre.",
                "#10b981"
            ),
            feature_card(
                "fas fa-atom", "Modelos RC/RL",
                "Ajuste automático de modelos equivalentes serie/paralelo a partir de los "
                "datos medidos. Extracción de R, L, C, Q, ESR y frecuencia de resonancia.",
                "#f59e0b"
            ),
            feature_card(
                "fas fa-terminal", "Terminal CLI integrado",
                "Ventana de terminal arrastrable con historial de comandos, "
                "auto-scroll, soporte ANSI y streaming bidireccional con el dispositivo.",
                "#ef4444"
            ),
            feature_card(
                "fas fa-file-csv", "Importar / Exportar CSV",
                "Carga y guarda mediciones en formato CSV compatible con Excel, MATLAB, "
                "Python/Pandas y herramientas SPICE. Superposición de múltiples archivos.",
                "#06b6d4"
            ),
            feature_card(
                "fas fa-desktop", "SPA multi-página",
                "Arquitectura de Single Page Application con rutas dedicadas para Dashboard, "
                "Calibración, Simulador RLC, Documentación y About. Sin recargas de página.",
                "#d4af37"
            ),
            feature_card(
                "fas fa-language", "Soporte multilenguaje",
                "Interfaz disponible en Español, English, Português, 中文 (Chino), "
                "Русский (Ruso) y Deutsch (Alemán). Selección persistente en el navegador.",
                "#ec4899"
            ),
            feature_card(
                "fas fa-flask", "Simulador RLC",
                "Simulación numérica de circuitos RC, RL y RLC serie/paralelo con "
                "parámetros ajustables en tiempo real. Ideal para comparar con mediciones reales.",
                "#0ea5e9"
            ),
        ], style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(auto-fill, minmax(280px, 1fr))',
            'gap': '16px',
            'marginBottom': '40px',
        }),

        # ── Beneficios ───────────────────────────────────────────────────────
        html.H4([
            html.I(className="fas fa-thumbs-up me-2", style={'color': 'var(--z-color-success)'}),
            html.Span("Beneficios de usar ZORIA", **{'data-i18n': 'doc.ov.h4.benefits'})
        ], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),

        bl_row(
            "fas fa-check-circle", "#10b981",
            "Productividad y facilidad de uso",
            [
                html.Span(["Elimina la necesidad de escribir comandos UART manualmente. ",
                 "Una sola interfaz reemplaza TeraTerm, scripts de Python y hojas de cálculo."]),
                html.Span(["Wizard guiado de calibración con instrucciones paso a paso: ",
                 "reduce errores humanos en el procedimiento OSL."]),
                html.Span(["Visualización instantánea del barrido en tiempo real: ",
                 "el gráfico se construye punto a punto conforme llegan los datos."]),
                "Historial de comandos CLI con navegación ↑↓ y atajos de teclado (Ctrl+L para limpiar).",
                "Detección automática del puerto USB/COM: no es necesario conocer el puerto de antemano.",
            ]
        ),
        bl_row(
            "fas fa-code-branch", "#3b82f6",
            "Código abierto y extensible",
            [
                html.Span(["Licencia ", html.Strong("MIT"), ": uso libre en proyectos académicos, comerciales y de investigación."]),
                html.Span(["Arquitectura modular en Python: cada página, componente y callback es independiente, "
                 "facilitando añadir nuevas funcionalidades sin romper las existentes."]),
                "API interna documentada: lib/admx2001.py, lib/calibration.py y lib/rc_model.py son "
                "usables de forma independiente como librerías Python.",
                "Sistema i18n propio extensible: añadir un nuevo idioma es tan simple como agregar "
                "un diccionario de 100 entradas en lib/i18n.py.",
            ]
        ),
        bl_row(
            "fas fa-wifi", "#8b5cf6",
            "Acceso remoto y multiplataforma",
            [
                html.Span(["Al ser una app web (Dash/Flask), puede servirse en red local: ",
                 "conexión del dispositivo al servidor y acceso desde cualquier navegador del laboratorio."]),
                "Compatible con Windows, Linux y macOS sin instalar software adicional más allá de Python.",
                "Interfaz responsive: usable en tablets para consultar mientras se trabaja en el banco.",
            ]
        ),
        bl_row(
            "fas fa-graduation-cap", "#f59e0b",
            "Valor educativo y de investigación",
            [
                "Documentación completa e integrada: no es necesario consultar el datasheet del ADMX2001B en otro lugar.",
                "Sección de matemática con derivaciones del modelo de impedancia, polos/ceros y método OSL.",
                "Simulador RLC integrado: permite comparar resultados teóricos vs. medidos en la misma sesión.",
                "Diagramas de arquitectura interactivos (Mermaid) que explican el flujo de datos del sistema.",
            ]
        ),

        # ── Limitaciones ────────────────────────────────────────────────────
        html.H4([
            html.I(className="fas fa-exclamation-triangle me-2", style={'color': 'var(--z-color-warning)'}),
            html.Span("Limitaciones actuales", **{'data-i18n': 'doc.ov.h4.limitations'})
        ], className="fw-bold mb-3 mt-4", style={'color': 'var(--z-color-text-primary)'}),

        info_box([
            html.Strong("ℹ Nota sobre las limitaciones: "),
            "Las limitaciones listadas corresponden al estado actual del software (v1.x). "
            "Muchas están planificadas para resolverse en versiones futuras. "
            "Las contribuciones de la comunidad son bienvenidas (ver sección Contribuir)."
        ], "info"),

        bl_row(
            "fas fa-microchip", "#ef4444",
            "Compatibilidad de hardware",
            [
                html.Span([html.Strong("Un único dispositivo soportado: "),
                 "ZORIA está diseñado exclusivamente para el EVAL-ADMX2001EBZ / ADMX2001B. "
                 "No soporta otros analizadores de impedancia o LCR meters."]),
                html.Span([html.Strong("Sin soporte USB nativo: "),
                 "la comunicación se realiza únicamente vía UART a través del cable FTDI incluido. "
                 "No hay driver USB HID propio."]),
                html.Span([html.Strong("Rango de frecuencia acotado: "),
                 "el ADMX2001B opera entre 1 Hz y 300 kHz. No cubre aplicaciones de RF "
                 "(MHz, GHz) ni frecuencias sub-Hz."]),
                html.Span([html.Strong("Una conexión a la vez: "),
                 "no es posible conectar múltiples dispositivos simultáneamente en la misma instancia."]),
            ]
        ),
        bl_row(
            "fas fa-server", "#f59e0b",
            "Despliegue y escalabilidad",
            [
                html.Span([html.Strong("Servidor local únicamente (recomendado): "),
                 "el servidor Dash corre en localhost. Para producción multi-usuario se requiere "
                 "configuración adicional (Gunicorn, Nginx, autenticación)."]),
                html.Span([html.Strong("Sin soporte cloud nativo: "),
                 "el dispositivo debe estar físicamente conectado al PC donde corre el servidor. "
                 "Remote-access requiere VPN o tunel SSH por parte del usuario."]),
                html.Span([html.Strong("Sin autenticación: "),
                 "en la versión actual no hay sistema de login ni control de acceso por usuario. "
                 "No usar expuesto directamente a internet."]),
            ]
        ),
        bl_row(
            "fas fa-chart-bar", "#8b5cf6",
            "Análisis y post-procesamiento",
            [
                html.Span([html.Strong("Sin ajuste de circuitos complejos: "),
                 "el fitting automático está limitado a modelos RC/RL simples (serie y paralelo). "
                 "No soporta modelos Warburg, CPE ni circuitos equivalentes Randles."]),
                html.Span([html.Strong("Sin análisis estadístico avanzado: "),
                 "no hay cálculo nativo de incertidumbre, intervalos de confianza ni "
                 "histogramas de dispersión sobre múltiples barridos."]),
                html.Span([html.Strong("Exportación limitada: "),
                 "sólo CSV. No exporta MATLAB (.mat), Touchstone (.s2p) ni formatos "
                 "propietarios de herramientas EDA."]),
            ]
        ),
        bl_row(
            "fas fa-mobile-alt", "#64748b",
            "Interfaz y UX",
            [
                html.Span([html.Strong("Diseño desktop-first: "),
                 "aunque responsive, la experiencia óptima es en pantalla ≥ 1080px. "
                 "El uso en móvil está limitado."]),
                html.Span([html.Strong("Sin modo oscuro completo: "),
                 "el dashboard principal tiene fondo blanco/gris. El sidebar y terminal tienen "
                 "tema oscuro pero el resto de la UI aún no."]),
            ]
        ),

        # ── Cuándo usar ZORIA ────────────────────────────────────────────────
        html.H4([
            html.I(className="fas fa-map-signs me-2", style={'color': 'var(--z-color-primary)'}),
            "¿Cuándo usar ZORIA?"
        ], className="fw-bold mb-3 mt-4", style={'color': 'var(--z-color-text-primary)'}),

        html.Div([
            html.Div([
                html.Div("ZORIA es ideal para...", className="fw-bold mb-3", style={'color': 'var(--z-color-success)', 'fontSize': '0.95rem'}),
                html.Ul([
                    html.Li("Laboratorios universitarios de electrónica analógica", style={'marginBottom': '8px', 'color': 'var(--z-color-text-secondary)'}),
                    html.Li("Caracterización de componentes pasivos (condensadores, inductores, filtros)", style={'marginBottom': '8px', 'color': 'var(--z-color-text-secondary)'}),
                    html.Li("Medición de impedancia de baterías y supercapacitores", style={'marginBottom': '8px', 'color': 'var(--z-color-text-secondary)'}),
                    html.Li("Investigación de materiales y sensores de impedancia", style={'marginBottom': '8px', 'color': 'var(--z-color-text-secondary)'}),
                    html.Li("Prototipado y verificación de diseños de filtros", style={'marginBottom': '8px', 'color': 'var(--z-color-text-secondary)'}),
                    html.Li("Equipos usando hardware ADMX2001 que buscan una GUI moderna", style={'marginBottom': '0', 'color': 'var(--z-color-text-secondary)'}),
                ], style={'paddingLeft': '20px', 'marginBottom': '0'})
            ], style={
                'background': 'var(--z-color-success-subtle)', 'border': '1px solid var(--z-color-success)',
                'borderRadius': '12px', 'padding': '20px', 'flex': '1',
            }),
            html.Div([
                html.Div("Considera alternativas si...", className="fw-bold mb-3", style={'color': 'var(--z-color-warning)', 'fontSize': '0.95rem'}),
                html.Ul([
                    html.Li("Necesitas rango de frecuencia > 300 kHz o RF", style={'marginBottom': '8px', 'color': 'var(--z-color-text-secondary)'}),
                    html.Li("Requieres soporte para múltiples dispositivos diferentes", style={'marginBottom': '8px', 'color': 'var(--z-color-text-secondary)'}),
                    html.Li("Necesitas modelos de circuito equivalente avanzados (Randles, Warburg)", style={'marginBottom': '8px', 'color': 'var(--z-color-text-secondary)'}),
                    html.Li("El entorno es producción industrial con requisitos de certificación", style={'marginBottom': '8px', 'color': 'var(--z-color-text-secondary)'}),
                    html.Li("Necesitas acceso multi-usuario simultáneo con control de sesión", style={'marginBottom': '0', 'color': 'var(--z-color-text-secondary)'}),
                ], style={'paddingLeft': '20px', 'marginBottom': '0'})
            ], style={
                'background': 'var(--z-color-warning-subtle)', 'border': '1px solid var(--z-color-warning)',
                'borderRadius': '12px', 'padding': '20px', 'flex': '1',
            }),
        ], style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap', 'marginBottom': '40px'}),

    ], style={'paddingTop': '20px'})


# ==================== CONTENIDO: CÓMO CONTRIBUIR ====================

def content_contribuir():
    """
    Guía completa de contribución al proyecto ZORIA.
    """

    def contrib_card(icon, color, title, body):
        return html.Div([
            html.Div([
                html.I(className=f"{icon} fa-lg me-3", style={'color': color}),
                html.Span(title, className="fw-bold", style={'color': 'var(--z-color-text-primary)', 'fontSize': '1rem'}),
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '12px'}),
            html.Div(body, style={'color': 'var(--z-color-text-secondary)', 'fontSize': '0.9rem', 'lineHeight': '1.7'}),
        ], style={
            'background': 'var(--z-color-bg-card)',
            'border': f'1px solid {color}50',
            'borderTop': f'3px solid {color}',
            'borderRadius': '10px',
            'padding': '20px',
            'boxShadow': '0 1px 4px rgba(0,0,0,0.05)',
        })

    def code_block(text, lang="bash"):
        return html.Pre(text, style={
            'background': 'var(--z-color-bg-card)',
            'color': 'var(--z-color-text-secondary)',
            'padding': '16px 20px',
            'borderRadius': '10px',
            'fontFamily': 'monospace',
            'fontSize': '0.82rem',
            'overflowX': 'auto',
            'lineHeight': '1.7',
            'marginBottom': '20px',
        })

    def badge(text, color):
        return html.Span(text, style={
            'background': color,
            'color': '#ffffff',
            'borderRadius': '20px',
            'padding': '3px 10px',
            'fontSize': '0.75rem',
            'fontWeight': '600',
            'marginRight': '6px',
            'display': 'inline-block',
            'marginBottom': '6px',
        })

    return html.Div([

        # ── Intro ─────────────────────────────────────────────────────────────
        html.Div([
            html.H3([
                html.I(className="fas fa-hands-helping me-3", style={'color': 'var(--z-footer-accent)'}),
                html.Span("Contribuir a ZORIA", **{'data-i18n': 'doc.section.contribute'})
            ], className="mb-3 fw-bold", style={'color': 'var(--z-color-text-primary)'}),
            html.P([
                "ZORIA es un proyecto de código abierto bajo licencia ", html.Strong("MIT"), ". "
                "¡Tu contribución, sin importar el tamaño, hace una diferencia! "
                "Ya sea reportando un bug, mejorando la documentación, traduciendo a un nuevo idioma, "
                "o añadiendo una nueva funcionalidad — todas las formas de participación son bienvenidas."
            ], style={'color': 'var(--z-color-text-secondary)', 'fontSize': '1.05rem', 'lineHeight': '1.8', 'marginBottom': '24px'}),

            # Links rápidos
            html.Div([
                html.A([html.I(className="fab fa-github me-2"), "GitHub Repository"],
                    href="https://github.com/mariomontero942/zoria", target="_blank",
                    className="btn me-3 mb-2",
                    style={'background': 'var(--z-color-bg-primary)', 'color': '#ffffff', 'textDecoration': 'none',
                           'padding': '10px 18px', 'borderRadius': '8px', 'display': 'inline-flex', 'alignItems': 'center'}),
                html.A([html.I(className="fas fa-bug me-2"), "Reportar un Bug"],
                    href="https://github.com/mariomontero942/zoria/issues/new?template=bug_report.md", target="_blank",
                    className="btn me-3 mb-2",
                    style={'background': 'var(--z-color-danger)', 'color': '#ffffff', 'textDecoration': 'none',
                           'padding': '10px 18px', 'borderRadius': '8px', 'display': 'inline-flex', 'alignItems': 'center'}),
                html.A([html.I(className="fas fa-lightbulb me-2"), "Proponer una Feature"],
                    href="https://github.com/mariomontero942/zoria/issues/new?template=feature_request.md", target="_blank",
                    className="btn mb-2",
                    style={'background': 'var(--z-footer-accent)', 'color': '#ffffff', 'textDecoration': 'none',
                           'padding': '10px 18px', 'borderRadius': '8px', 'display': 'inline-flex', 'alignItems': 'center'}),
            ], style={'marginBottom': '32px'}),
        ]),

        # ── Código de conducta ───────────────────────────────────────────────
        html.H4([
            html.I(className="fas fa-heart me-2", style={'color': 'var(--z-chart-phase)'}),
            html.Span("Código de conducta", **{'data-i18n': 'doc.contrib.h4.conduct'})
        ], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),

        info_box([
            html.Div([
                html.Strong("Nuestro compromiso: "),
                "En ZORIA nos comprometemos a que la participación en este proyecto sea una experiencia "
                "libre de acoso para todos, independientemente de edad, discapacidad, etnia, identidad "
                "de género, nivel de experiencia, nacionalidad, apariencia personal, raza, religión o "
                "identidad/orientación sexual."
            ], style={'marginBottom': '10px'}),
            html.Ul([
                html.Li("Usa lenguaje inclusivo y acogedor", style={'marginBottom': '5px'}),
                html.Li("Acepta las críticas constructivas con gracia", style={'marginBottom': '5px'}),
                html.Li("Enfócate en lo mejor para la comunidad", style={'marginBottom': '5px'}),
                html.Li("Muestra empatía hacia otros miembros de la comunidad", style={'marginBottom': '0'}),
            ], style={'paddingLeft': '20px', 'marginBottom': '0'})
        ], "info"),

        # ── Formas de contribuir ─────────────────────────────────────────────
        html.H4([
            html.I(className="fas fa-puzzle-piece me-2", style={'color': 'var(--z-color-primary)'}),
            html.Span("Formas de contribuir", **{'data-i18n': 'doc.contrib.h4.ways'})
        ], className="fw-bold mb-3 mt-4", style={'color': 'var(--z-color-text-primary)'}),

        html.Div([
            contrib_card(
                "fas fa-bug", "#ef4444", "Reportar bugs",
                [
                    html.P("Antes de crear un issue, busca si ya existe uno similar. "
                           "Un buen bug report incluye:", style={'marginBottom': '10px'}),
                    html.Ul([
                        html.Li("Descripción clara del comportamiento esperado vs. observado"),
                        html.Li("Pasos mínimos para reproducirlo"),
                        html.Li([html.Strong("Versión de ZORIA, Python y SO"), " (ej. ZORIA 1.2, Python 3.11, Ubuntu 22.04)"]),
                        html.Li("Logs del terminal o captura de pantalla del error"),
                        html.Li("El puerto COM / modelo USB-UART si es un bug de conexión"),
                    ], style={'paddingLeft': '20px', 'marginBottom': '0', 'lineHeight': '1.8'})
                ]
            ),
            contrib_card(
                "fas fa-lightbulb", "#f59e0b", "Proponer funcionalidades",
                [
                    html.P(["¿Tienes una idea para ZORIA? Abre un issue con la etiqueta ",
                           html.Code("enhancement", style={'background': 'var(--z-color-warning-subtle)', 'padding': '1px 6px', 'borderRadius': '4px'}),
                           ". Incluye:"], style={'marginBottom': '10px'}),
                    html.Ul([
                        html.Li("Descripción del problema que resuelve la feature"),
                        html.Li("Descripción detallada de la solución propuesta"),
                        html.Li("Alternativas que hayas considerado"),
                        html.Li("Si es nuevo hardware, modelos de dispositivos compatibles"),
                    ], style={'paddingLeft': '20px', 'marginBottom': '10px', 'lineHeight': '1.8'}),
                    html.Div([
                        badge("good first issue", "#22c55e"),
                        badge("help wanted", "#3b82f6"),
                        badge("enhancement", "#f59e0b"),
                        badge("documentation", "#8b5cf6"),
                    ])
                ]
            ),
            contrib_card(
                "fas fa-language", "#ec4899", "Añadir / mejorar traducciones",
                [
                    html.P(["El sistema i18n vive en ", html.Code("lib/i18n.py", style={'background': 'var(--z-color-danger-subtle)', 'padding': '1px 6px', 'borderRadius': '4px'}),
                            ". Para agregar o corregir un idioma:"], style={'marginBottom': '10px'}),
                    html.Ol([
                        html.Li(["Abre ", html.Code("lib/i18n.py")]),
                        html.Li("Para un idioma nuevo: añade su código al dict LANGUAGES y una columna a TRANSLATIONS"),
                        html.Li("Para corregir: edita directamente el valor en el diccionario existente"),
                        html.Li("Envía un PR con el título [i18n] Añadir/Corregir <idioma>"),
                    ], style={'paddingLeft': '20px', 'marginBottom': '0', 'lineHeight': '1.8'})
                ]
            ),
            contrib_card(
                "fas fa-book", "#8b5cf6", "Documentación",
                [
                    html.P(["La documentación vive en ", html.Code("pages/documentation/documentation_page.py"),
                            ". Para contribuir:"], style={'marginBottom': '10px'}),
                    html.Ul([
                        html.Li("Mejorar o corregir procediminetos existentes"),
                        html.Li("Añadir ejemplos de comandos CLI con resultados reales"),
                        html.Li("Agregar imágenes / diagramas aclaratorios"),
                        html.Li("Construir diagramas Mermaid adicionales en la sección §9"),
                        html.Li("Traducir contenido a otros idiomas"),
                    ], style={'paddingLeft': '20px', 'marginBottom': '0', 'lineHeight': '1.8'})
                ]
            ),
        ], style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(auto-fill, minmax(320px, 1fr))',
            'gap': '16px',
            'marginBottom': '40px',
        }),

        # ── Setup del entorno de desarrollo ──────────────────────────────────
        html.H4([
            html.I(className="fas fa-wrench me-2", style={'color': 'var(--z-color-success)'}),
            html.Span("Configurar el entorno de desarrollo", **{'data-i18n': 'doc.contrib.h4.setup'})
        ], className="fw-bold mb-3 mt-2", style={'color': 'var(--z-color-text-primary)'}),

        html.Div([
            html.Div([step_number(1), html.Span("Requisitos previos", className="fw-bold", style={'color': 'var(--z-color-text-primary)'})],
                     style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
            html.Ul([
                html.Li(["Python ", html.Strong("3.9+"), " (recomendado 3.11)"]),
                html.Li("Git 2.x"),
                html.Li("pip o conda"),
                html.Li(["(Opcional) Dispositivo EVAL-ADMX2001EBZ para tests de hardware"]),
            ], style={'color': 'var(--z-color-text-secondary)', 'paddingLeft': '20px', 'marginBottom': '20px'}),

            html.Div([step_number(2), html.Span("Clonar el repositorio", className="fw-bold", style={'color': 'var(--z-color-text-primary)'})],
                     style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
            code_block("""# Clona el repositorio (sustituye con tu fork si ya hiciste fork)
git clone https://github.com/mariomontero942/zoria.git
cd zoria"""),

            html.Div([step_number(3), html.Span("Crear entorno virtual e instalar dependencias", className="fw-bold", style={'color': 'var(--z-color-text-primary)'})],
                     style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
            code_block("""# Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\\Scripts\\activate           # Windows PowerShell

# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt   # herramientas de desarrollo"""),

            html.Div([step_number(4), html.Span("Ejecutar la aplicación en modo desarrollo", className="fw-bold", style={'color': 'var(--z-color-text-primary)'})],
                     style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
            code_block("""python app.py
# La app estará disponible en http://localhost:8050"""),

            html.Div([step_number(5), html.Span("Ejecutar los tests antes de hacer cambios", className="fw-bold", style={'color': 'var(--z-color-text-primary)'})],
                     style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
            code_block("""# Ejecutar suite de tests
python -m pytest test_*.py -v

# Tests específicos
python -m pytest test_calibration_parsing.py -v
python -m pytest test_fit_rc.py -v"""),

        ], style={'background': 'var(--z-color-bg-primary)', 'borderRadius': '12px', 'padding': '24px', 'marginBottom': '32px'}),

        # ── Guía de estilo de código ──────────────────────────────────────────
        html.H4([
            html.I(className="fas fa-paint-brush me-2", style={'color': 'var(--z-color-warning)'}),
            html.Span("Guía de estilo de código", **{'data-i18n': 'doc.contrib.h4.style'})
        ], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),

        html.Div([
            html.Div([
                html.Strong("Python", style={'color': 'var(--z-color-primary)', 'display': 'block', 'marginBottom': '10px', 'fontSize': '0.95rem'}),
                html.Ul([
                    html.Li(["Seguir ", html.Strong("PEP 8"), " — se recomienda usar ", html.Code("ruff"), " o ", html.Code("flake8")]),
                    html.Li([html.Strong("Tipo hints"), " en funciones nuevas: ", html.Code("def t(key: str, lang: str = 'es') -> str:")]),
                    html.Li(["Docstrings en Google style para funciones públicas"]),
                    html.Li(["Máximo ", html.Strong("120 caracteres"), " por línea"]),
                    html.Li(["Nombres en español para variables de dominio (ej. ", html.Code("frecuencia"), ", ", html.Code("calibracion"), "), inglés para lógica general"]),
                ], style={'color': 'var(--z-color-text-secondary)', 'paddingLeft': '20px', 'lineHeight': '1.8', 'marginBottom': '0'})
            ], style={'flex': '1', 'background': 'var(--z-color-info-subtle)', 'borderRadius': '10px', 'padding': '18px'}),

            html.Div([
                html.Strong("Dash / Componentes UI", style={'color': 'var(--z-color-primary)', 'display': 'block', 'marginBottom': '10px', 'fontSize': '0.95rem'}),
                html.Ul([
                    html.Li(["Cada página va en su propio directorio bajo ", html.Code("pages/<nombre>/")]),
                    html.Li(["Componentes reutilizables → ", html.Code("pages/common/")]),
                    html.Li(["IDs de componentes Dash: ", html.Code("kebab-case"), ", descriptivos y únicos globalmente"]),
                    html.Li(["Callbacks con ", html.Code("prevent_initial_call=True"), " salvo que el comportamiento inicial sea explícito"]),
                    html.Li(["Nuevos elementos de texto: añadir atributo ", html.Code("data-i18n"), " con la clave correspondiente"]),
                ], style={'color': 'var(--z-color-text-secondary)', 'paddingLeft': '20px', 'lineHeight': '1.8', 'marginBottom': '0'})
            ], style={'flex': '1', 'background': 'var(--z-color-info-subtle)', 'borderRadius': '10px', 'padding': '18px'}),

            html.Div([
                html.Strong("CSS", style={'color': 'var(--z-chart-phase)', 'display': 'block', 'marginBottom': '10px', 'fontSize': '0.95rem'}),
                html.Ul([
                    html.Li(["Un archivo CSS por sección/página: ", html.Code("assets/css/<nombre>.css")]),
                    html.Li(["Clases con prefijo del módulo: ", html.Code(".diagram-*"), ", ", html.Code(".lang-*"), ", ", html.Code(".calibration-*")]),
                    html.Li(["Variables CSS en ", html.Code(":root"), " para colores y tipografía reutilizables"]),
                    html.Li("Mobile-first: media queries desde 375px hacia arriba"),
                    html.Li("No usar estilos inline salvo en valores dinámicos imposibles de parametrizar"),
                ], style={'color': 'var(--z-color-text-secondary)', 'paddingLeft': '20px', 'lineHeight': '1.8', 'marginBottom': '0'})
            ], style={'flex': '1', 'background': 'var(--z-color-danger-subtle)', 'borderRadius': '10px', 'padding': '18px'}),

        ], style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap', 'marginBottom': '32px'}),

        # ── Proceso de Pull Request ───────────────────────────────────────────
        html.H4([
            html.I(className="fas fa-code-branch me-2", style={'color': 'var(--z-color-primary)'}),
            html.Span("Proceso de Pull Request", **{'data-i18n': 'doc.contrib.h4.pr'})
        ], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),

        html.Div([
            html.Div([
                html.Div([step_number(i+1, color), html.Span(title, className="fw-bold", style={'color': 'var(--z-color-text-primary)', 'fontSize': '0.9rem'})],
                         style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '8px'}),
                html.P(desc, style={'color': 'var(--z-color-text-secondary)', 'fontSize': '0.875rem', 'paddingLeft': '44px', 'marginBottom': '0'})
            ], style={'marginBottom': '20px'})
            for i, (title, desc, color) in enumerate([
                ("Fork + branch", "Haz fork del repo en GitHub. Crea una rama descriptiva: git checkout -b feature/nyquist-zoom o fix/calibration-load-empty-list.", "#3b82f6"),
                ("Desarrolla tus cambios", "Haz commits atómicos con mensajes claros en inglés y en tiempo presente: feat: add Portuguese translations, fix: prevent crash when no USB port detected, docs: add contributing guide.", "#10b981"),
                ("Tests", "Añade o actualiza tests para cubrir tu cambio. Todos los tests deben pasar (pytest test_*.py). Si tu cambio afecta hardware, documenta el resultado manual.", "#f59e0b"),
                ("Abre el Pull Request", "Abre el PR contra la rama main. Rellena la plantilla: descripción, tipo de cambio (feat/fix/docs/i18n/refactor), capturas de pantalla si es UI, y lista de tests ejecutados.", "#8b5cf6"),
                ("Code review", "Un maintainer revisará el PR. Pueden pedirte ajustes — responde con commits adicionales en la misma rama. Evita force-push salvo que se solicite explícitamente.", "#d4af37"),
                ("Merge", "Una vez aprobado y CIs en verde, el maintainer hará merge. ¡Tu contribución estará en ZORIA!", "#ec4899"),
            ])
        ], style={'background': 'var(--z-color-bg-primary)', 'borderRadius': '12px', 'padding': '24px', 'marginBottom': '32px'}),

        # ── Convención de commits ──────────────────────────────────────────────
        html.H4([
            html.I(className="fas fa-tags me-2", style={'color': 'var(--z-color-primary)'}),
            html.Span("Convención de commits (Conventional Commits)", **{'data-i18n': 'doc.contrib.h4.commits'})
        ], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),

        code_block("""# Formato
<tipo>(<scope>): <descripción breve en inglés>

# Ejemplos
feat(dashboard): add real-time Nyquist plot streaming
fix(calibration): prevent IndexError when calibration list is empty
docs(contributing): add pull request guide
i18n(ru): add Russian translations for calibration wizard
refactor(lib): extract serial timeout into config constant
test(rc_model): add fitting test for parallel RC above 100kHz
style(css): normalize diagram-card min-height across browsers
chore(deps): upgrade plotly to 5.18.0"""),

        html.Div([
            html.Div([badge(t, c) for t, c in [
                ("feat", "#22c55e"), ("fix", "#ef4444"), ("docs", "#8b5cf6"),
                ("i18n", "#ec4899"), ("refactor", "#f59e0b"), ("test", "#3b82f6"),
                ("style", "#06b6d4"), ("chore", "#64748b"), ("perf", "#d4af37"),
            ]]),
        ], style={'marginBottom': '32px'}),

        # ── Tests ─────────────────────────────────────────────────────────────
        html.H4([
            html.I(className="fas fa-vial me-2", style={'color': 'var(--z-color-success)'}),
            html.Span("Tests", **{'data-i18n': 'doc.contrib.h4.tests'})
        ], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),

        html.Div([
            html.Div([
                html.Strong("Estructura de tests", style={'color': 'var(--z-color-text-primary)', 'display': 'block', 'marginBottom': '10px'}),
                html.Ul([
                    html.Li([html.Code("test_calibration_*.py"), " — Tests de parseo y ejecución del flujo OSL"]),
                    html.Li([html.Code("test_fit_rc*.py"), " — Tests de ajuste de modelos RC/RL"]),
                    html.Li([html.Code("test_connection*.py"), " — Tests de comunicación serial (mock)"]),
                    html.Li([html.Code("test_sweep*.py"), " — Tests del flujo de barrido de frecuencia"]),
                ], style={'color': 'var(--z-color-text-secondary)', 'paddingLeft': '20px', 'lineHeight': '1.9', 'marginBottom': '0'})
            ], style={'flex': '1'}),
            html.Div([
                html.Strong("Guía para nuevos tests", style={'color': 'var(--z-color-text-primary)', 'display': 'block', 'marginBottom': '10px'}),
                html.Ul([
                    html.Li("Cada nuevo módulo en lib/ debe tener su archivo test_<modulo>.py"),
                    html.Li("Usa pytest fixtures para mock del dispositivo serial"),
                    html.Li("Tests de componentes UI: usa dash.testing.DashComposite cuando sea necesario"),
                    html.Li("Nombra tests descriptivamente: test_calibration_load_returns_list_when_empty()"),
                ], style={'color': 'var(--z-color-text-secondary)', 'paddingLeft': '20px', 'lineHeight': '1.9', 'marginBottom': '0'})
            ], style={'flex': '1'}),
        ], style={'display': 'flex', 'gap': '24px', 'flexWrap': 'wrap',
                  'background': 'var(--z-color-success-subtle)', 'borderRadius': '12px', 'padding': '24px', 'marginBottom': '32px'}),

        # ── Estructura del repo ───────────────────────────────────────────────
        html.H4([
            html.I(className="fas fa-folder-open me-2", style={'color': 'var(--z-footer-accent)'}),
            html.Span("Estructura del repositorio", **{'data-i18n': 'doc.contrib.h4.structure'})
        ], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),

        code_block("""zoria/
├── app.py                      # Punto de entrada, layout global, callbacks globales
├── themes.py                   # Tema VOLT + paleta de colores
├── requirements.txt            # Dependencias de producción
├── requirements-dev.txt        # Dependencias de desarrollo (pytest, ruff…)
│
├── lib/                        # Lógica de negocio (importable independientemente)
│   ├── admx2001.py             # Driver de comunicación serial con ADMX2001B
│   ├── calibration.py          # Lógica de calibración OSL
│   ├── calibration_parser.py   # Parsing de respuestas del dispositivo
│   ├── device_state.py         # Estado global del dispositivo (singleton)
│   ├── i18n.py                 # Sistema de traducciones (ES/EN/PT/ZH/RU/DE)
│   ├── rc_model.py             # Ajuste de modelos RC/RL
│   └── utils.py                # Utilidades comunes
│
├── pages/                      # Páginas de la SPA
│   ├── common/                 # Componentes compartidos (sidebar, footer, etc.)
│   ├── dashboard/              # Página principal de medición
│   ├── calibration/            # Wizard de calibración
│   ├── documentation/          # Esta documentación
│   ├── simulator/              # Simulador RLC
│   ├── about/                  # Acerca de
│   └── ...
│
├── assets/
│   ├── css/                    # Hojas de estilo por módulo
│   ├── js/                     # Scripts clientside (i18n, mermaid, shortcuts…)
│   └── vendor/                 # Dependencias JS/CSS locales (Bootstrap, Plotly…)
│
└── test_*.py                   # Tests (pytest)"""),

        # ── Contacto ──────────────────────────────────────────────────────────
        html.H4([
            html.I(className="fas fa-envelope me-2", style={'color': 'var(--z-color-danger)'}),
            html.Span("Contacto y comunidad", **{'data-i18n': 'doc.contrib.h4.contact'})
        ], className="fw-bold mb-3", style={'color': 'var(--z-color-text-primary)'}),

        html.Div([
            html.Div([
                html.I(className="fab fa-github fa-lg me-3", style={'color': 'var(--z-color-text-primary)'}),
                html.Div([
                    html.Strong("GitHub Issues", style={'display': 'block', 'color': 'var(--z-color-text-primary)'}),
                    html.Span("Para bugs, features y preguntas técnicas", style={'color': 'var(--z-color-text-tertiary)', 'fontSize': '0.875rem'}),
                ]),
            ], style={'display': 'flex', 'alignItems': 'center', 'padding': '16px',
                      'background': 'var(--z-color-bg-primary)', 'borderRadius': '10px', 'flex': '1'}),
            html.Div([
                html.I(className="fas fa-envelope fa-lg me-3", style={'color': 'var(--z-color-primary)'}),
                html.Div([
                    html.Strong("Email del mantenedor", style={'display': 'block', 'color': 'var(--z-color-text-primary)'}),
                    html.A("mariomontero942@gmail.com", href="mailto:mariomontero942@gmail.com",
                           style={'color': 'var(--z-color-primary)', 'fontSize': '0.875rem'}),
                ]),
            ], style={'display': 'flex', 'alignItems': 'center', 'padding': '16px',
                      'background': 'var(--z-color-bg-primary)', 'borderRadius': '10px', 'flex': '1'}),
            html.Div([
                html.I(className="fas fa-book-open fa-lg me-3", style={'color': 'var(--z-color-primary)'}),
                html.Div([
                    html.Strong("Wiki Analog Devices ADMX2001", style={'display': 'block', 'color': 'var(--z-color-text-primary)'}),
                    html.A("wiki.analog.com/resources/eval/eval-admx2001", href="https://wiki.analog.com/resources/eval/eval-admx2001",
                           target="_blank", style={'color': 'var(--z-color-primary)', 'fontSize': '0.875rem'}),
                ]),
            ], style={'display': 'flex', 'alignItems': 'center', 'padding': '16px',
                      'background': 'var(--z-color-bg-primary)', 'borderRadius': '10px', 'flex': '1'}),
        ], style={'display': 'flex', 'gap': '12px', 'flexWrap': 'wrap', 'marginBottom': '40px'}),

        info_box([
            html.Strong("¡Muchas gracias por querer contribuir! "),
            "Cada issue abierto, cada PR enviado, cada corrección de documentación — todo suma para "
            "hacer de ZORIA una herramienta mejor para la comunidad de análisis de impedancia."
        ], "success"),

    ], style={'paddingTop': '20px'})


# ==================== LAYOUT PRINCIPAL ====================
layout = html.Div([
    sideBar(),
    mobileNavBar(),
    
    html.Main([
        # Hero
        hero_section(),
        
        # Tabs con contenido
        html.Div([
            html.Div([
                dcc.Tabs([
                    dcc.Tab(
                        label=' Inicio Rápido',
                        value='inicio',
                        children=content_inicio_rapido(),
                        className='doc-tab',
                        selected_className='doc-tab-selected'
                    ),
                    dcc.Tab(
                        label=' Hardware',
                        value='hardware',
                        children=content_hardware(),
                        className='doc-tab',
                        selected_className='doc-tab-selected'
                    ),
                    dcc.Tab(
                        label=' Software',
                        value='software',
                        children=content_software(),
                        className='doc-tab',
                        selected_className='doc-tab-selected'
                    ),
                    dcc.Tab(
                        label=' Matemática',
                        value='matematica',
                        children=content_matematica_background(),
                        className='doc-tab',
                        selected_className='doc-tab-selected'
                    ),
                    dcc.Tab(
                        label=' Calibración',
                        value='calibracion',
                        children=content_calibracion(),
                        className='doc-tab',
                        selected_className='doc-tab-selected'
                    ),
                    dcc.Tab(
                        label='⌨ CLI',
                        value='cli',
                        children=content_cli(),
                        className='doc-tab',
                        selected_className='doc-tab-selected'
                    ),
                    dcc.Tab(
                        label=' Firmware',
                        value='firmware',
                        children=content_firmware(),
                        className='doc-tab',
                        selected_className='doc-tab-selected'
                    ),
                    dcc.Tab(
                        label=' ZORIA',
                        value='overview',
                        children=content_overview(),
                        className='doc-tab',
                        selected_className='doc-tab-selected'
                    ),
                    dcc.Tab(
                        label='Contribuir',
                        value='contribuir',
                        children=content_contribuir(),
                        className='doc-tab',
                        selected_className='doc-tab-selected'
                    )
                ], 
                id='doc-tabs',
                value='inicio',
                className='doc-tabs-container',
                parent_className='doc-tabs-parent',
                content_className='doc-tabs-content'
                )
            ], style={
                'maxWidth': '1200px',
                'margin': '0 auto',
                'padding': '0 40px 80px'
            })
        ])
    ], className="content", style={'background': 'var(--z-color-bg-card)'}),
    
    footer(),
    floating_terminal_button()
    
], className="sc-chart d-flex flex-column", style={
    'minHeight': '100vh',
    'background': 'var(--z-color-bg-card)'
})

# Store dummy para los callbacks i18n de esta página
layout.children.insert(0, dcc.Store(id='doc-i18n-dummy', storage_type='memory'))


def register_callbacks(app):
    from dash import Input, Output

    # Cuando llegan traducciones frescas (cambio de idioma o carga inicial),
    # reaplica con un pequeño retraso para asegurarse de que todo el DOM
    # de la página esté montado (especialmente con dcc.Tabs).
    app.clientside_callback(
        """
        function(translations) {
            if (!translations || !translations['_lang']) return window.dash_clientside.no_update;
            var lang = translations['_lang'];
            // Cancelar timers anteriores para evitar que un idioma viejo se reaplique tarde
            clearTimeout(window._zoriaDocApplyTimer1);
            clearTimeout(window._zoriaDocApplyTimer2);
            // Delay para que React termine de montar el DOM de los tabs
            window._zoriaDocApplyTimer1 = setTimeout(function() {
                if (window.ZORIA_I18N && window.ZORIA_I18N.current() === lang) {
                    window.ZORIA_I18N.apply(lang, translations);
                }
            }, 150);
            window._zoriaDocApplyTimer2 = setTimeout(function() {
                if (window.ZORIA_I18N && window.ZORIA_I18N.current() === lang) {
                    window.ZORIA_I18N.apply(lang);
                }
            }, 600);
            return window.dash_clientside.no_update;
        }
        """,
        Output('doc-i18n-dummy', 'data'),
        Input('lang-translations-store', 'data'),
        prevent_initial_call=False,
    )

    # También reaplica cuando el usuario cambia de pestaña,
    # por si Dash renderiza el contenido de la pestaña en ese momento.
    app.clientside_callback(
        """
        function(activeTab) {
            clearTimeout(window._zoriaDocTabTimer1);
            clearTimeout(window._zoriaDocTabTimer2);
            window._zoriaDocTabTimer1 = setTimeout(function() {
                if (window.ZORIA_I18N) window.ZORIA_I18N.apply(window.ZORIA_I18N.current());
            }, 100);
            window._zoriaDocTabTimer2 = setTimeout(function() {
                if (window.ZORIA_I18N) window.ZORIA_I18N.apply(window.ZORIA_I18N.current());
            }, 500);
            return window.dash_clientside.no_update;
        }
        """,
        Output('doc-i18n-dummy', 'data', allow_duplicate=True),
        Input('doc-tabs', 'value'),
        prevent_initial_call=True,
    )


def register_documentation_page(app):
    register_callbacks(app)
