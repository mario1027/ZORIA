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
    """Caja de información estilizada"""
    colors = {
        "info": ("#dbeafe", "#1e40af", "#3b82f6"),
        "warning": ("#fef3c7", "#92400e", "#f59e0b"),
        "danger": ("#fee2e2", "#991b1b", "#ef4444"),
        "success": ("#d1fae5", "#065f46", "#10b981"),
        "tip": ("#fffbeb", "#92400e", "#d4af37")
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


def step_number(number, color="#d4af37"):
    """Número de paso circular"""
    return html.Span(
        str(number),
        style={
            'display': 'inline-flex',
            'width': '32px',
            'height': '32px',
            'background': color,
            'color': '#ffffff',
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
                'border': '1px solid #e2e8f0',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.1)'
            }
        ),
        html.P(
            caption,
            style={
                'fontSize': '0.85rem',
                'color': '#64748b',
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
                html.I(className="fas fa-rocket me-3", style={'color': '#d4af37'}),
                "Inicio Rápido - Five Simple Steps"
            ], className="mb-3 fw-bold", style={'color': '#0f172a'}),
            html.P([
                "Esta guía te ayudará a configurar y comenzar a usar tu ",
                html.Strong("EVAL-ADMX2001", style={'color': '#d4af37'}),
                " en cinco simples pasos para realizar tus primeras mediciones."
            ], style={'color': '#475569', 'fontSize': '1.1rem', 'marginBottom': '30px'})
        ]),
        
        info_box([
            html.Strong("📦 Contenido del Kit:"),
            html.Ul([
                html.Li("Placa EVAL-ADMX2001EBZ"),
                html.Li("Cable UART a USB (TTL-232R-RPI)"),
                html.Li("Adaptador de corriente universal con salida de 9VDC"),
                html.Li("Pinzas de prueba para medidor LCR")
            ], style={'marginBottom': '0'}),
            html.Div([
                html.Strong("⚠️ IMPORTANTE: "), 
                "El módulo ADMX2001B se vende por separado. Es crítico comprar AMBOS componentes."
            ], style={'marginTop': '15px', 'padding': '10px', 'background': '#fef3c7', 'borderRadius': '6px'})
        ], "info"),
        
        # Paso 1
        html.Div([
            html.H5([step_number(1), "Instalación de Drivers FTDI VCP"], className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.P([
                "El ", html.Strong("EVAL-ADMX2001EBZ"), " se comunica con tu PC mediante UART. "
                "El cable USB-to-UART incluido requiere drivers ",
                html.Strong("Virtual COM Port (VCP)"), " de FTDI."
            ], style={'color': '#475569', 'marginBottom': '15px'}),
            html.Div([
                html.H6("Procedimiento:", className="fw-bold mt-3 mb-2", style={'color': '#0f172a'}),
                html.Ol([
                    html.Li([
                        "Descargar el setup executable del driver desde: ",
                        html.A("https://www.ftdichip.com/Drivers/VCP.htm", href="https://www.ftdichip.com/Drivers/VCP.htm", target="_blank", style={'color': '#3b82f6'})
                    ], style={'color': '#475569', 'marginBottom': '10px'}),
                    html.Li("Descomprimir y ejecutar el instalador", style={'color': '#475569', 'marginBottom': '10px'}),
                    html.Li([html.Strong("Conectar"), " el cable USB-UART al PC"], style={'color': '#475569', 'marginBottom': '10px'}),
                    html.Li("Abrir el Administrador de Dispositivos (Windows) / System Profiler (Mac)", style={'color': '#475569', 'marginBottom': '10px'}),
                    html.Li("Verificar que el Puerto Serial USB aparezca bajo 'Ports (COM & LPT)' con un identificador asignado (ej. COM3)", style={'color': '#475569'})
                ])
            ], style={'background': '#f8fafc', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '15px'}),
            info_box([
                html.Strong("💡 Verificación: "),
                "En Windows busca 'USB Serial Port (COMx)' bajo 'Ports (COM & LPT)'. Anota el número de puerto COM para el paso 4."
            ], "tip"),
            image_card(IMAGES.get('dev_mgr_vcp'), "Administrador de dispositivos Windows mostrando puerto COM")
        ], style={'marginBottom': '40px'}),
        
        # Paso 2
        html.Div([
            html.H5([step_number(2), "Instalación del Emulador de Terminal"], className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.P([
                "Para comunicarse con el ADMX2001B mediante su interfaz CLI y UART, se recomienda ",
                html.Strong("TeraTerm"), " (soporta códigos ANSI para colores y cursor)."
            ], style={'color': '#475569', 'marginBottom': '15px'}),
            html.A([
                html.I(className="fas fa-download me-2"),
                "Descargar TeraTerm"
            ], href="https://github.com/TeraTermProject/teraterm/releases", target="_blank",
               className="btn mb-3", style={'background': '#d4af37', 'color': '#ffffff', 'textDecoration': 'none', 'display': 'inline-block', 'padding': '10px 20px', 'borderRadius': '8px'}),
            html.P([
                html.Strong("Alternativas: "), "PuTTY, CoolTerm (pueden tener problemas con códigos ANSI)"
            ], style={'color': '#64748b', 'fontSize': '0.9rem', 'marginTop': '15px'}),
            html.Div([
                html.H6("Configuración de TeraTerm:", className="fw-bold mb-2", style={'color': '#0f172a'}),
                html.Ul([
                    html.Li([html.Strong("Speed: "), "115200"], style={'color': '#475569'}),
                    html.Li([html.Strong("Data: "), "8 bits"], style={'color': '#475569'}),
                    html.Li([html.Strong("Parity: "), "none"], style={'color': '#475569'}),
                    html.Li([html.Strong("Stop bits: "), "1 bits"], style={'color': '#475569'}),
                    html.Li([html.Strong("Flow control: "), "none"], style={'color': '#475569'})
                ])
            ], style={'background': '#f8fafc', 'padding': '15px', 'borderRadius': '8px', 'marginTop': '15px'})
        ], style={'marginBottom': '40px'}),
        
        # Paso 3
        html.Div([
            html.H5([step_number(3), "Configuración de Hardware"], className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.P("Sigue estos pasos para la configuración inicial:", style={'color': '#475569', 'marginBottom': '15px'}),
            html.Div([
                html.Div([
                    html.Strong("3.1 Ensamblaje del módulo", style={'color': '#0f172a', 'display': 'block', 'marginBottom': '8px'}),
                    html.Ul([
                        html.Li("Insertar el módulo ADMX2001B en la placa EVAL-ADMX2001EBZ"),
                        html.Li("Los conectores tienen guía - asegúrate de que esté completamente insertado")
                    ], style={'color': '#475569'})
                ], style={'background': '#f1f5f9', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '15px'}),
                html.Div([
                    html.Strong("3.2 Configuración de switches para self-test inicial", style={'color': '#0f172a', 'display': 'block', 'marginBottom': '8px'}),
                    html.Ul([
                        html.Li([html.Strong("S1"), " → Posición OPEN"]),
                        html.Li([html.Strong("S2"), " → Posición GND"])
                    ])
                ], style={'background': '#f1f5f9', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '15px'}),
                html.Div([
                    html.Strong("3.3 Alimentación:", style={'color': '#0f172a', 'display': 'block', 'marginBottom': '8px'}),
                    html.Ul([
                        html.Li("Conectar el adaptador de corriente al conector de alimentación y al tomacorriente"),
                        html.Li([html.Strong("Verificar: "), "El LED de self-test debe iluminarse en VERDE (parte inferior del módulo)"])
                    ])
                ], style={'background': '#f1f5f9', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '15px'}),
                html.Div([
                    html.Strong("3.4 Conexión UART:", style={'color': '#0f172a', 'display': 'block', 'marginBottom': '8px'}),
                    html.Ul([
                        html.Li("TX (naranja) → TX del evaluador"),
                        html.Li("RX (amarillo) → RX del evaluador"),
                        html.Li("GND (negro) → GND del evaluador")
                    ])
                ], style={'background': '#f1f5f9', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '15px'}),
                html.Div([
                    html.Strong("3.5 Verificaciones finales:", style={'color': '#0f172a', 'display': 'block', 'marginBottom': '8px'}),
                    html.Ul([
                        html.Li("Jumper CLK_SEL en posición INT (reloj interno)"),
                        html.Li("Cambiar switches a DUT y GND para mediciones"),
                        html.Li("Conectar pinzas de prueba: BNC rojos → HCUR/HPOT, BNC negros → LPOT/LCUR")
                    ])
                ], style={'background': '#f1f5f9', 'padding': '15px', 'borderRadius': '8px'})
            ]),
            info_box([
                html.Strong("⚠️ IMPORTANTE sobre pinzas: "),
                "Inspeccionar los conectores BNC de las pinzas. La carcasa puede aflojarse parcialmente. ",
                "Al usar en configuración 'open', cada pinza debe sujetar su propio trozo de alambre para asegurar conexión eléctrica."
            ], "warning"),
            image_card(IMAGES.get('basic_connections'), "Diagrama de conexiones básicas"),
            image_card(IMAGES.get('uart_connection'), "Detalle de conexión UART")
        ], style={'marginBottom': '40px'}),
        
        # Paso 4
        html.Div([
            html.H5([step_number(4), "Abrir Sesión con TeraTerm"], className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.Div([
                html.Strong("Configuración inicial:", style={'display': 'block', 'marginBottom': '10px'}),
                html.Ol([
                    html.Li("Abrir TeraTerm y elegir conexión Serial", style={'marginBottom': '8px'}),
                    html.Li("Seleccionar el puerto COM identificado en el Administrador de Dispositivos", style={'marginBottom': '8px'}),
                    html.Li("Ir a Setup → Serial port y configurar: 115200, 8, none, 1, none", style={'marginBottom': '8px'}),
                    html.Li("Click en 'New setting'", style={'marginBottom': '8px'}),
                    html.Li("(Opcional) Guardar configuración: Setup → Save setup", style={'marginBottom': '8px'})
                ], style={'color': '#475569'}),
                html.Strong("Verificar la conexión:", style={'display': 'block', 'marginTop': '20px', 'marginBottom': '10px'}),
                html.Ul([
                    html.Li([
                        "Presionar ", html.Code("ENTER", style={'background': '#1e293b', 'color': '#10b981', 'padding': '2px 8px', 'borderRadius': '4px'}),
                        " para mostrar el prompt ", html.Code("ADMX2001>")
                    ], style={'marginBottom': '8px'}),
                    html.Li([
                        "Escribir ", html.Code("*idn", style={'background': '#1e293b', 'color': '#10b981', 'padding': '2px 8px', 'borderRadius': '4px'}),
                        " y presionar ENTER para ver versión de firmware"
                    ], style={'marginBottom': '8px'}),
                    html.Li([
                        "Escribir ", html.Code("help", style={'background': '#1e293b', 'color': '#10b981', 'padding': '2px 8px', 'borderRadius': '4px'}),
                        " y presionar ENTER para ver lista de comandos disponibles"
                    ])
                ], style={'color': '#475569'})
            ], style={'background': '#f8fafc', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '15px'}),
            info_box([
                html.Strong("💡 Tip: "),
                "Cerrar la ventana de TeraTerm no resetea la configuración del ADMX2001B de la última sesión."
            ], "tip")
        ], style={'marginBottom': '40px'}),
        
        # Paso 5
        html.Div([
            html.H5([step_number(5), "Primeras Mediciones"], className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.P([
                "Al abrir una sesión, el ADMX2001B está listo para realizar mediciones de impedancia. ",
                html.Strong("⚠️ Las mediciones no serán precisas hasta calibrar el módulo (ver sección Calibración).")
            ], style={'color': '#475569', 'marginBottom': '15px'}),
            html.Div([
                html.Strong("Configuración por defecto:", style={'display': 'block', 'marginBottom': '10px'}),
                html.Ul([
                    html.Li("Mediciones de impedancia en coordenadas rectangulares (mode 6: R, X)"),
                    html.Li("Señal de 1V pk (magnitude = 1) a 1kHz"),
                    html.Li("Sin offset DC"),
                    html.Li("Auto-ranging habilitado")
                ], style={'color': '#475569'})
            ], style={'background': '#f8fafc', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '20px'}),
            html.H6("Ejemplo: Medición de Capacitancia", className="fw-bold mb-2", style={'color': '#0f172a'}),
            html.P("Realizar una medición Cp-Rp a 100kHz con amplitud de 1V, retornar 5 lecturas promediando 10 muestras:", style={'color': '#475569', 'marginBottom': '10px'}),
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
                'background': '#1e293b',
                'color': '#e2e8f0',
                'padding': '20px',
                'borderRadius': '12px',
                'fontFamily': 'monospace',
                'fontSize': '0.85rem',
                'overflowX': 'auto',
                'lineHeight': '1.6'
            }),
            info_box([
                html.Strong("✅ ¡Listo! "),
                "Tu EVAL-ADMX2001 está configurado. Para mediciones de precision, continúa con el procedimiento de calibración."
            ], "success")
        ])
    ])


# ==================== CONTENIDO: HARDWARE ====================

def content_hardware():
    return html.Div([
        html.Div([
            html.H3([
                html.I(className="fas fa-microchip me-3", style={'color': '#3b82f6'}),
                "Especificaciones de Hardware"
            ], className="mb-3 fw-bold", style={'color': '#0f172a'}),
            html.P([
                "El ", html.Strong("EVAL-ADMX2001 LCR Meter Demo", style={'color': '#3b82f6'}),
                " comprende el módulo ", html.Strong("ADMX2001B"), " y la placa de evaluación ",
                html.Strong("EVAL-ADMX2001EBZ"), "."
            ], style={'color': '#475569', 'fontSize': '1.1rem', 'marginBottom': '30px'})
        ]),
        
        info_box([
            html.Strong("⚠️ IMPORTANTE: "),
            "Es crítico comprar AMBOS el módulo ADMX2001B y la placa EVAL-ADMX2001EBZ. Se venden por separado."
        ], "warning"),
        
        # ADMX2001B Module
        html.Div([
            html.H5("ADMX2001B - Módulo Analizador de Impedancia", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.Div([
                html.Ul([
                    html.Li([html.Strong("Altamente compacto: "), "System-on-Module (SOM) de 1.5 × 2.5 pulgadas"]),
                    html.Li([html.Strong("Rango de frecuencia: "), "0.2 Hz a 10 MHz"]),
                    html.Li([html.Strong("Mediciones: "), "Resistencia DC o impedancia AC"]),
                    html.Li([html.Strong("Canales ADC: "), "18 bits de resolución"]),
                    html.Li([html.Strong("Alimentación: "), "Fuente única de 3.3V"]),
                    html.Li([html.Strong("Interfaces: "), "UART y SPI flexibles"]),
                    html.Li([html.Strong("Formatos: "), "18 modos de display en unidades SI"])
                ], style={'color': '#475569'})
            ], style={
                'background': '#ffffff',
                'borderRadius': '12px',
                'border': '1px solid #e2e8f0',
                'padding': '20px',
                'marginBottom': '30px'
            })
        ]),
        
        # EVAL-ADMX2001EBZ Board
        html.Div([
            html.H5("EVAL-ADMX2001EBZ - Placa de Evaluación", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.Div([
                html.Ul([
                    html.Li([html.Strong("Conectores BNC: "), "Para sondas y accesorios LCR estándar"]),
                    html.Li([html.Strong("Interfaz UART: "), "Cable USB-to-UART para conexión a PC"]),
                    html.Li([html.Strong("Triggers SMA: "), "Sincronización y triggers por hardware"]),
                    html.Li([html.Strong("Headers Arduino: "), "Para desarrollo embebido (ej. SDP-K1)"]),
                    html.Li([html.Strong("Alimentación: "), "Conector para adaptadores AC/DC de +5V a +12V"]),
                    html.Li([html.Strong("Headers PMOD: "), "Acceso a interfaz SPI"]),
                    html.Li([html.Strong("I/Os digitales: "), "8 salidas digitales configurables"])
                ], style={'color': '#475569'})
            ], style={
                'background': '#ffffff',
                'borderRadius': '12px',
                'border': '1px solid #e2e8f0',
                'padding': '20px',
                'marginBottom': '30px'
            })
        ]),
        
        # Descripción de Terminales
        html.Div([
            html.H5("Descripción de Terminales", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.Div([
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("Terminal", style={'color': '#0f172a', 'fontWeight': '600', 'padding': '12px', 'borderBottom': '2px solid #3b82f6'}),
                            html.Th("Descripción", style={'color': '#0f172a', 'fontWeight': '600', 'padding': '12px', 'borderBottom': '2px solid #3b82f6'})
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([
                            html.Td(html.Strong("H_CUR"), style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td("Terminal de fuente de señal. Genera la excitación requerida. Puede proveer hasta ±5V @ 50mA", style={'padding': '12px', 'color': '#475569', 'borderBottom': '1px solid #e2e8f0'})
                        ]),
                        html.Tr([
                            html.Td(html.Strong("H_POT"), style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td("Terminal de sensado de voltaje. Conectar a H_CUR en el DUT", style={'padding': '12px', 'color': '#475569', 'borderBottom': '1px solid #e2e8f0'})
                        ]),
                        html.Tr([
                            html.Td(html.Strong("L_POT"), style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td("Terminal de sensado de voltaje. Conectar a L_CUR en el DUT", style={'padding': '12px', 'color': '#475569', 'borderBottom': '1px solid #e2e8f0'})
                        ]),
                        html.Tr([
                            html.Td(html.Strong("L_CUR"), style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td("Terminal de sensado de corriente. Ruta de retorno para señal de excitación", style={'padding': '12px', 'color': '#475569', 'borderBottom': '1px solid #e2e8f0'})
                        ]),
                        html.Tr([
                            html.Td(html.Strong("UART TX/RX"), style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td("Pines de comunicación UART. Lógica 3.3V", style={'padding': '12px', 'color': '#475569', 'borderBottom': '1px solid #e2e8f0'})
                        ]),
                        html.Tr([
                            html.Td(html.Strong("TRIG_IN"), style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td("Entrada de trigger para adquisición sincronizada por hardware (3.3V, mín 15μs)", style={'padding': '12px', 'color': '#475569', 'borderBottom': '1px solid #e2e8f0'})
                        ]),
                        html.Tr([
                            html.Td(html.Strong("TRIG_OUT"), style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td("Salida de trigger al completar medición", style={'padding': '12px', 'color': '#475569', 'borderBottom': '1px solid #e2e8f0'})
                        ]),
                        html.Tr([
                            html.Td(html.Strong("CLK_IN/OUT"), style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td("Entrada/salida de reloj. Señal LVCMOS 50MHz", style={'padding': '12px', 'color': '#475569', 'borderBottom': '1px solid #e2e8f0'})
                        ])
                    ])
                ], style={'width': '100%', 'borderCollapse': 'collapse'})
            ], style={
                'background': '#ffffff',
                'borderRadius': '12px',
                'border': '1px solid #e2e8f0',
                'padding': '20px',
                'marginBottom': '30px',
                'overflowX': 'auto'
            })
        ]),
        
        # Self-Test
        html.Div([
            html.H5("Funcionalidad de Self-Test", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.P("Al encender, el ADMX2001B ejecuta automáticamente un self-test. El LED bicolor indica el estado:", style={'color': '#475569', 'marginBottom': '15px'}),
            html.Div([
                html.Div([
                    html.Span("●", style={'color': '#10b981', 'fontSize': '24px', 'marginRight': '12px'}),
                    html.Strong("Verde: ", style={'color': '#0f172a'}),
                    html.Span("Pasa el self-test", style={'color': '#475569'})
                ], style={'padding': '12px', 'marginBottom': '8px'}),
                html.Div([
                    html.Span("●", style={'color': '#f59e0b', 'fontSize': '24px', 'marginRight': '12px'}),
                    html.Strong("Verde/Rojo: ", style={'color': '#0f172a'}),
                    html.Span("Falla el self-test", style={'color': '#475569'})
                ], style={'padding': '12px', 'marginBottom': '8px'}),
                html.Div([
                    html.Span("●", style={'color': '#ef4444', 'fontSize': '24px', 'marginRight': '12px'}),
                    html.Strong("Rojo: ", style={'color': '#0f172a'}),
                    html.Span("Problema mayor (alimentación, firmware faltante)", style={'color': '#475569'})
                ], style={'padding': '12px'})
            ], style={'background': '#f8fafc', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '15px'}),
            html.P([
                html.Strong("Comandos del self-test:")
            ], style={'color': '#0f172a', 'marginTop': '20px', 'marginBottom': '10px'}),
            html.Ul([
                html.Li([html.Code("selftest", style={'background': '#1e293b', 'color': '#10b981', 'padding': '2px 8px', 'borderRadius': '4px'}), " - Ver estado del último self-test"]),
                html.Li([html.Code("selftest run", style={'background': '#1e293b', 'color': '#10b981', 'padding': '2px 8px', 'borderRadius': '4px'}), " - Reejecutar el self-test"])
            ], style={'color': '#475569'}),
            info_box([
                html.Strong("⚠️ Importante: "),
                "Para pasar el componente analógico del self-test, los switches S1 y S2 deben estar en OPEN y GND."
            ], "warning")
        ], style={'marginBottom': '40px'}),
        
        # Switches
        html.Div([
            html.H5("Configuración de Switches", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.P("Los switches S1 y S2 configuran el modo de operación:", style={'color': '#475569', 'marginBottom': '15px'}),
            html.Div([
                html.Div([
                    html.Strong("Self-Test Mode:"),
                    html.Ul([
                        html.Li("S1 → OPEN"),
                        html.Li("S2 → GND")
                    ])
                ], style={'background': '#f1f5f9', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '10px'}),
                html.Div([
                    html.Strong("Medición Normal (DUT):"),
                    html.Ul([
                        html.Li("S1 → LOAD"),
                        html.Li("S2 → GND")
                    ])
                ], style={'background': '#f1f5f9', 'padding': '15px', 'borderRadius': '8px'})
            ])
        ], style={'marginBottom': '40px'}),
        
        image_card(IMAGES.get('basic_connections'), "Diagrama de conexiones del evaluador")
    ])


# ==================== CONTENIDO: SOFTWARE ====================

def content_software():
    return html.Div([
        html.Div([
            html.H3([
                html.I(className="fas fa-laptop-code me-3", style={'color': '#10b981'}),
                "Guía de Software ZORIA"
            ], className="mb-3 fw-bold", style={'color': '#0f172a'}),
            html.P([
                "ZORIA es una plataforma web de código abierto que transforma el analizador de impedancia ",
                html.Strong("EVAL-ADMX2001"), " (Analog Devices) en un sistema de medición moderno con ",
                "visualización científica en tiempo real."
            ], style={'color': '#475569', 'fontSize': '1.1rem', 'marginBottom': '30px'})
        ]),
        
        # Arquitectura
        html.Div([
            html.H5("Arquitectura de ZORIA", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.P("ZORIA implementa una arquitectura modular de tres capas:", style={'color': '#475569', 'marginBottom': '15px'}),
            html.Div([
                html.Div([
                    html.H6("1. Capa de Hardware", className="fw-bold mb-2", style={'color': '#10b981'}),
                    html.Ul([
                        html.Li("Comunicación serial con EVAL-ADMX2001 via protocolo UART"),
                        html.Li("Parsing y validación de comandos"),
                        html.Li("Adquisición de datos y control de barridos"),
                        html.Li("Detección automática de dispositivo y manejo de conexión")
                    ], style={'color': '#475569'})
                ], style={'background': '#f0fdf4', 'padding': '20px', 'borderRadius': '12px', 'marginBottom': '15px', 'border': '2px solid #10b981'}),
                
                html.Div([
                    html.H6("2. Backend (Python)", className="fw-bold mb-2", style={'color': '#10b981'}),
                    html.Pre("""lib/
├── admx2001.py       # Clase principal de control del dispositivo (43 métodos)
├── calibration.py    # Gestión de calibración (open/short/load)
├── utils.py          # Utilidades de validación y procesamiento
├── enums.py          # Constantes, modos y configuraciones
└── exceptions.py     # Jerarquía de excepciones custom""", style={
                        'background': '#1e293b',
                        'color': '#10b981',
                        'padding': '15px',
                        'borderRadius': '8px',
                        'fontFamily': 'monospace',
                        'fontSize': '0.85rem',
                        'lineHeight': '1.5'
                    })
                ], style={'background': '#f0fdf4', 'padding': '20px', 'borderRadius': '12px', 'marginBottom': '15px', 'border': '2px solid #10b981'}),
                
                html.Div([
                    html.H6("3. Frontend (Dash-SPA)", className="fw-bold mb-2", style={'color': '#10b981'}),
                    html.Pre("""pages/
├── dashboard/        # Interfaz de medición en tiempo real
├── simulator/        # Calculadora de impedancia RLC
├── documentation/    # Documentación integrada de usuario
└── common/          # Componentes UI reutilizables""", style={
                        'background': '#1e293b',
                        'color': '#10b981',
                        'padding': '15px',
                        'borderRadius': '8px',
                        'fontFamily': 'monospace',
                        'fontSize': '0.85rem',
                        'lineHeight': '1.5'
                    })
                ], style={'background': '#f0fdf4', 'padding': '20px', 'borderRadius': '12px', 'border': '2px solid #10b981'})
            ])
        ], style={'marginBottom': '40px'}),
        
        # Biblioteca Python
        html.Div([
            html.H5("Biblioteca Python - lib/admx2001.py", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.P("La clase ADMX2001 proporciona 43 métodos para control completo del dispositivo:", style={'color': '#475569', 'marginBottom': '15px'}),
            html.Div([
                html.Div([
                    html.H6("Conexión y Comunicación:", className="fw-bold mb-2", style={'color': '#0f172a'}),
                    html.Ul([
                        html.Li([html.Code("connect()"), " - Establecer conexión serial"]),
                        html.Li([html.Code("disconnect()"), " - Cerrar conexión"]),
                        html.Li([html.Code("send_command(cmd)"), " - Enviar comando CLI"]),
                        html.Li([html.Code("check_connection()"), " - Verificar estado de conexión"]),
                        html.Li([html.Code("reconnect()"), " - Reconectar automáticamente"]),
                        html.Li([html.Code("get_idn()"), " - Obtener identificación del dispositivo"]),
                        html.Li([html.Code("get_version()"), " - Obtener versión de firmware"])
                    ], style={'color': '#475569', 'fontSize': '0.9rem'})
                ], style={'marginBottom': '20px'}),
                
                html.Div([
                    html.H6("Configuración de Medición:", className="fw-bold mb-2", style={'color': '#0f172a'}),
                    html.Ul([
                        html.Li([html.Code("set_frequency(freq)"), " - Configurar frecuencia (0.2 Hz - 10 MHz)"]),
                        html.Li([html.Code("set_magnitude(mag)"), " - Configurar amplitud de señal (0 - 2.5 V pk)"]),
                        html.Li([html.Code("set_offset(offset)"), " - Configurar offset DC (±2.5 V)"]),
                        html.Li([html.Code("set_average(avg)"), " - Configurar promediado (1-256 muestras)"]),
                        html.Li([html.Code("set_count(count)"), " - Número de lecturas por medición"]),
                        html.Li([html.Code("set_display_mode(mode)"), " - Modo de display (0-17)"])
                    ], style={'color': '#475569', 'fontSize': '0.9rem'})
                ], style={'marginBottom': '20px'}),
                
                html.Div([
                    html.H6("Control de Ganancia:", className="fw-bold mb-2", style={'color': '#0f172a'}),
                    html.Ul([
                        html.Li([html.Code("set_gain_auto()"), " - Activar auto-ranging"]),
                        html.Li([html.Code("set_gain_manual(ch0, ch1)"), " - Configurar ganancias manualmente"]),
                        html.Li([html.Code("set_gain(channel, gain)"), " - Configurar ganancia específica"]),
                        html.Li([html.Code("recommend_impedance_range(z)"), " - Recomendar ganancia para impedancia"])
                    ], style={'color': '#475569', 'fontSize': '0.9rem'})
                ], style={'marginBottom': '20px'}),
                
                html.Div([
                    html.H6("Mediciones:", className="fw-bold mb-2", style={'color': '#0f172a'}),
                    html.Ul([
                        html.Li([html.Code("measure_impedance()"), " - Medición de impedancia AC"]),
                        html.Li([html.Code("measure()"), " - Retorna tupla (valor1, valor2)"]),
                        html.Li([html.Code("measure_temperature()"), " - Medir temperatura interna"]),
                        html.Li([html.Code("measure_dcr()"), " - Medición de resistencia DC"]),
                        html.Li([html.Code("parse_impedance_response()"), " - Parsear respuesta del dispositivo"])
                    ], style={'color': '#475569', 'fontSize': '0.9rem'})
                ], style={'marginBottom': '20px'}),
                
                html.Div([
                    html.H6("Barridos:", className="fw-bold mb-2", style={'color': '#0f172a'}),
                    html.Ul([
                        html.Li([html.Code("configure_sweep(type, start, end, points, scale)"), " - Configurar barrido"]),
                        html.Li([html.Code("perform_sweep(timeout)"), " - Ejecutar barrido y retornar datos"]),
                        html.Li([html.Code("disable_sweep()"), " - Deshabilitar modo barrido"])
                    ], style={'color': '#475569', 'fontSize': '0.9rem'})
                ], style={'marginBottom': '20px'}),
                
                html.Div([
                    html.H6("Utilidades:", className="fw-bold mb-2", style={'color': '#0f172a'}),
                    html.Ul([
                        html.Li([html.Code("set_mdelay(ms)"), " - Retardo entre mediciones"]),
                        html.Li([html.Code("set_tdelay(ms)"), " - Retardo después de trigger"]),
                        html.Li([html.Code("selftest(run)"), " - Ejecutar/ver self-test"]),
                        html.Li([html.Code("reset()"), " - Reset del dispositivo"]),
                        html.Li([html.Code("get_help(cmd)"), " - Obtener ayuda de comando"]),
                        html.Li([html.Code("get_status()"), " - Obtener estado completo del dispositivo"])
                    ], style={'color': '#475569', 'fontSize': '0.9rem'})
                ])
            ], style={
                'background': '#ffffff',
                'borderRadius': '12px',
                'border': '1px solid #e2e8f0',
                'padding': '20px',
                'marginBottom': '20px'
            })
        ], style={'marginBottom': '40px'}),
        
        # Ejemplos de código
        html.Div([
            html.H5("Ejemplos de Código Python", className="fw-bold mb-3", style={'color': '#0f172a'}),
            
            html.H6("1. Conexión y Medición Simple:", className="fw-bold mb-2", style={'color': '#0f172a'}),
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
                'background': '#1e293b',
                'color': '#e2e8f0',
                'padding': '20px',
                'borderRadius': '12px',
                'fontFamily': 'monospace',
                'fontSize': '0.85rem',
                'overflowX': 'auto',
                'lineHeight': '1.5',
                'marginBottom': '20px'
            }),
            
            html.H6("2. Barrido de Frecuencia Logarítmico:", className="fw-bold mb-2", style={'color': '#0f172a'}),
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
                'background': '#1e293b',
                'color': '#e2e8f0',
                'padding': '20px',
                'borderRadius': '12px',
                'fontFamily': 'monospace',
                'fontSize': '0.85rem',
                'overflowX': 'auto',
                'lineHeight': '1.5',
                'marginBottom': '20px'
            }),
            
            html.H6("3. Uso del Simulador RLC:", className="fw-bold mb-2", style={'color': '#0f172a'}),
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
                'background': '#1e293b',
                'color': '#e2e8f0',
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
            html.H5("📊 Uso del Dashboard de Medición", className="fw-bold mb-3", style={'color': '#10b981'}),
            html.P("El Dashboard es la página principal de ZORIA donde se realizan mediciones en tiempo real y barridos de frecuencia.", style={'color': '#475569', 'marginBottom': '20px'}),
            
            # Conexión al dispositivo
            html.Div([
                html.H6("1. Conexión al Dispositivo", className="fw-bold mb-2", style={'color': '#0f172a'}),
                html.Ul([
                    html.Li([html.Strong("Botón \"Conectar ADMX2001\":"), " Hacer clic en el botón principal de conexión"]),
                    html.Li([html.Strong("Detección automática:"), " El sistema detecta puertos USB-Serial disponibles (FTDI, Silicon Labs, CH340)"]),
                    html.Li([html.Strong("Selección manual:"), " Elegir puerto específico si hay múltiples dispositivos"]),
                    html.Li([html.Strong("Verificación:"), " Al conectar exitosamente, aparece información del dispositivo (IDN, versión firmware)"]),
                    html.Li([html.Strong("LED de estado:"), " Indicador verde cuando la conexión está activa"])
                ], style={'color': '#475569'})
            ], style={'background': '#f0fdf4', 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid #10b981', 'marginBottom': '20px'}),
            
            # Medición simple
            html.Div([
                html.H6("2. Medición Simple (Punto Único)", className="fw-bold mb-2", style={'color': '#0f172a'}),
                html.Ul([
                    html.Li([html.Strong("Modo de Display:"), " Seleccionar uno de los 18 modos (Z-θ, R-X, Cp-D, Cs-D, Ls-Q, etc.)"]),
                    html.Li([html.Strong("Frecuencia:"), " Configurar frecuencia de medición (0.2 Hz - 10 MHz)"]),
                    html.Li([html.Strong("Magnitud:"), " Ajustar amplitud de señal (0 - 2.5 V pk) o usar auto"]),
                    html.Li([html.Strong("Promediado:"), " Configurar número de promedios (1-256) para reducir ruido"]),
                    html.Li([html.Strong("Botón \"Medir\":"), " Ejecutar medición única - resultados en display numérico grande"]),
                    html.Li([html.Strong("Visualización:"), " Valor principal y secundario según modo (ej: |Z| y θ)"])
                ], style={'color': '#475569'})
            ], style={'background': '#ffffff', 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid #e2e8f0', 'marginBottom': '20px'}),
            
            # Barrido de frecuencia
            html.Div([
                html.H6("3. Barrido de Frecuencia", className="fw-bold mb-2", style={'color': '#0f172a'}),
                html.Ul([
                    html.Li([html.Strong("Panel de configuración:"), " Tarjeta \"Configuración de Barrido\" en la parte inferior"]),
                    html.Li([html.Strong("Frecuencia inicial (Hz):"), " Punto de inicio del barrido"]),
                    html.Li([html.Strong("Frecuencia final (Hz):"), " Punto final del barrido"]),
                    html.Li([html.Strong("Número de puntos:"), " Resolución del barrido (10-1000 puntos)"]),
                    html.Li([html.Strong("Escala:"), " Lineal o Logarítmica (logarítmico recomendado para rangos amplios)"]),
                    html.Li([html.Strong("Botón \"Iniciar Barrido\":"), " Ejecutar barrido automático"]),
                    html.Li([html.Strong("Progreso en tiempo real:"), " Barra de progreso muestra avance (% completado)"]),
                    html.Li([html.Strong("Gráficos dinámicos:"), " Bode y Nyquist se actualizan durante el barrido"])
                ], style={'color': '#475569'})
            ], style={'background': '#fff7ed', 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid #fb923c', 'marginBottom': '20px'}),
            
            # Gráficos científicos
            html.Div([
                html.H6("4. Gráficos Científicos en Tiempo Real", className="fw-bold mb-2", style={'color': '#0f172a'}),
                
                html.Div([
                    html.Strong("📈 Diagrama de Bode:", style={'color': '#10b981'}),
                    html.Ul([
                        html.Li("Eje X: Frecuencia (escala logarítmica)"),
                        html.Li("Eje Y izquierdo: Magnitud |Z| en dB (línea cyan)"),
                        html.Li("Eje Y derecho: Fase θ en grados (línea rosa)"),
                        html.Li("Interactividad: Zoom, pan, hover para valores exactos"),
                        html.Li("Exportar imagen PNG desde menú del gráfico")
                    ], style={'color': '#475569', 'fontSize': '0.9rem'})
                ], className="mb-3"),
                
                html.Div([
                    html.Strong("🌀 Diagrama de Nyquist:", style={'color': '#10b981'}),
                    html.Ul([
                        html.Li("Eje X: Z' (parte real de impedancia en Ω)"),
                        html.Li("Eje Y: -Z'' (parte imaginaria negativa en Ω)"),
                        html.Li("Colormap: Gradiente de color según frecuencia (Viridis)"),
                        html.Li("Útil para: Identificar circuitos RC, RL, resonancia, EIS de baterías"),
                        html.Li("Exportar imagen PNG desde menú")
                    ], style={'color': '#475569', 'fontSize': '0.9rem'})
                ])
            ], style={'background': '#eff6ff', 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid #3b82f6', 'marginBottom': '20px'}),
            
            # Exportación de datos
            html.Div([
                html.H6("5. Exportación de Datos", className="fw-bold mb-2", style={'color': '#0f172a'}),
                html.Ul([
                    html.Li([html.Strong("Botón \"Exportar CSV\":"), " Descargar datos del último barrido"]),
                    html.Li([html.Strong("Formato:"), " CSV con columnas: Frecuencia(Hz), Z_real(Ω), Z_imag(Ω), |Z|(Ω), Phase(°)"]),
                    html.Li([html.Strong("Timestamp:"), " Nombre de archivo incluye fecha y hora (ej: sweep_20260209_143025.csv)"]),
                    html.Li([html.Strong("Compatible:"), " Importar en Excel, Python pandas, MATLAB, Origin"])
                ], style={'color': '#475569'})
            ], style={'background': '#f0fdf4', 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid #10b981', 'marginBottom': '20px'}),
            
            # Terminal flotante
            html.Div([
                html.H6("6. Terminal CLI Integrada", className="fw-bold mb-2", style={'color': '#0f172a'}),
                html.Ul([
                    html.Li([html.Strong("Acceso:"), " Presionar ", html.Kbd("Alt + T"), " o botón flotante inferior derecho"]),
                    html.Li([html.Strong("Comandos CLI:"), " Enviar comandos directos al ADMX2001"]),
                    html.Li([html.Strong("Historial:"), " Navegación con flechas arriba/abajo"]),
                    html.Li([html.Strong("Autocompletado:"), " Presionar Tab para sugerencias"]),
                    html.Li([html.Strong("Ejemplos:"), html.Code(" IDN? "), ", ", html.Code(" FREQ 1000 "), ", ", html.Code(" SWEEP? ")])
                ], style={'color': '#475569'})
            ], style={'background': '#fef3c7', 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid #f59e0b', 'marginBottom': '20px'}),
            
            # Características avanzadas
            html.Div([
                html.H6("✨ Características Avanzadas", className="fw-bold mb-2", style={'color': '#10b981'}),
                html.Div([
                    html.Div([
                        html.I(className="fas fa-database me-2", style={'color': '#10b981'}),
                        html.Strong("Persistencia de sesión: "),
                        html.Span("Configuración guardada automáticamente (puerto, frecuencia, modo)")
                    ], style={'padding': '10px 0', 'borderBottom': '1px solid #e2e8f0'}),
                    html.Div([
                        html.I(className="fas fa-sync-alt me-2", style={'color': '#10b981'}),
                        html.Strong("Reconexión automática: "),
                        html.Span("Al desconectar, reconecta con último puerto usado")
                    ], style={'padding': '10px 0', 'borderBottom': '1px solid #e2e8f0'}),
                    html.Div([
                        html.I(className="fas fa-moon me-2", style={'color': '#10b981'}),
                        html.Strong("Tema claro/oscuro: "),
                        html.Span("Botón para cambiar tema de gráficos (optimizado para publicaciones)")
                    ], style={'padding': '10px 0', 'borderBottom': '1px solid #e2e8f0'}),
                    html.Div([
                        html.I(className="fas fa-mobile-alt me-2", style={'color': '#10b981'}),
                        html.Strong("Responsive: "),
                        html.Span("Interfaz adaptable a tablets y móviles")
                    ], style={'padding': '10px 0'})
                ], style={'padding': '10px'})
            ], style={'background': '#ffffff', 'borderRadius': '12px', 'border': '1px solid #e2e8f0'})
        ], style={'marginBottom': '40px'}),
        
        # =============== SIMULADOR RLC ===============
        html.Div([
            html.H5("🔬 Simulador de Circuitos RLC", className="fw-bold mb-3", style={'color': '#10b981'}),
            html.P("El Simulador permite calcular y visualizar la respuesta en frecuencia de circuitos RLC antes de realizar mediciones físicas.", style={'color': '#475569', 'marginBottom': '20px'}),
            
            html.Div([
                html.H6("Uso del Simulador", className="fw-bold mb-2", style={'color': '#0f172a'}),
                html.Ol([
                    html.Li([html.Strong("Acceso:"), " Menú lateral → Simulador RLC"]),
                    html.Li([html.Strong("Seleccionar circuito:"), " Dropdown con 10 topologías (RC serie/paralelo, RL serie/paralelo, RLC serie/paralelo, etc.)"]),
                    html.Li([html.Strong("Configurar componentes:"), " Ingresar valores de R(Ω), L(H), C(F)"]),
                    html.Li([html.Strong("Rango de frecuencia:"), " Frecuencia inicial, final y número de puntos (10-10,000,000 Hz)"]),
                    html.Li([html.Strong("Calcular:"), " Presionar botón \"Calcular Impedancia\""]),
                    html.Li([html.Strong("Visualización:"), " Diagramas de Bode y Nyquist actualizados instantáneamente"]),
                    html.Li([html.Strong("Información:"), " Panel inferior muestra impedancia en frecuencias clave (mín, máx, resonancia)"])
                ], style={'color': '#475569'})
            ], style={'background': '#fef3c7', 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid #f59e0b', 'marginBottom': '20px'}),
            
            html.Div([
                html.H6("Circuitos Disponibles", className="fw-bold mb-2", style={'color': '#0f172a'}),
                html.Ul([
                    html.Li("RC Serie / RC Paralelo"),
                    html.Li("RL Serie / RL Paralelo"),
                    html.Li("RLC Serie / RLC Paralelo"),
                    html.Li("Solo R / Solo L / Solo C"),
                    html.Li("Circuitos personalizados con combinaciones")
                ], style={'color': '#475569'})
            ], style={'background': '#eff6ff', 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid #3b82f6', 'marginBottom': '20px'}),
            
            html.Div([
                html.H6("Aplicaciones del Simulador", className="fw-bold mb-2", style={'color': '#10b981'}),
                html.Ul([
                    html.Li("Predecir respuesta de circuitos antes de construirlos"),
                    html.Li("Comparar mediciones reales vs. teóricas para validación"),
                    html.Li("Diseñar filtros RC/RL con frecuencias de corte específicas"),
                    html.Li("Calcular frecuencia de resonancia de circuitos RLC"),
                    html.Li("Educación: Visualizar comportamiento de componentes pasivos")
                ], style={'color': '#475569'})
            ], style={'background': '#f0fdf4', 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid #10b981'})
        ], style={'marginBottom': '40px'}),
        
        # Casos de uso
        html.Div([
            html.H5("Casos de Uso", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.Div([
                html.Div([
                    html.H6("1. Caracterización de Resonadores RLC", className="fw-bold mb-2", style={'color': '#10b981'}),
                    html.P("Medir frecuencia de resonancia, factor de calidad (Q) y ancho de banda en circuitos resonantes para aplicaciones RF y diseño de filtros.", style={'color': '#475569', 'fontSize': '0.9rem'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.H6("2. Análisis de Baterías (EIS)", className="fw-bold mb-2", style={'color': '#10b981'}),
                    html.P("Espectroscopia de Impedancia Electroquímica para determinar State of Health (SOH) y State of Charge (SOC) en sistemas de gestión de baterías.", style={'color': '#475569', 'fontSize': '0.9rem'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.H6("3. Caracterización de Materiales", className="fw-bold mb-2", style={'color': '#10b981'}),
                    html.P("Medir propiedades dieléctricas, conductividad y tangente de pérdida de materiales en función de la frecuencia.", style={'color': '#475569', 'fontSize': '0.9rem'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.H6("4. Diseño de Filtros y Redes de Acoplamiento", className="fw-bold mb-2", style={'color': '#10b981'}),
                    html.P("Verificar impedancia característica, pérdida de inserción y parámetros S de filtros y redes de acoplamiento de impedancia.", style={'color': '#475569', 'fontSize': '0.9rem'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.H6("5. Desarrollo de Sensores", className="fw-bold mb-2", style={'color': '#10b981'}),
                    html.P("Caracterización de sensores impedimétricos para biosensores, sensores químicos y monitoreo ambiental.", style={'color': '#475569', 'fontSize': '0.9rem'})
                ])
            ], style={
                'background': '#f0fdf4',
                'borderRadius': '12px',
                'border': '1px solid #10b981',
                'padding': '20px'
            })
        ], style={'marginBottom': '40px'}),
        
        # Atajos de teclado
        html.Div([
            html.H5("Atajos de Teclado", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.Div([
                html.Div([
                    html.Kbd("Alt + T", style={
                        'background': '#f1f5f9',
                        'border': '1px solid #cbd5e1',
                        'borderRadius': '4px',
                        'padding': '4px 10px',
                        'fontSize': '0.85rem'
                    }),
                    html.Span(" Terminal flotante", style={'color': '#64748b', 'marginLeft': '12px'})
                ], style={'padding': '10px 0', 'borderBottom': '1px solid #e2e8f0'}),
                html.Div([
                    html.Kbd("Ctrl + L", style={
                        'background': '#f1f5f9',
                        'border': '1px solid #cbd5e1',
                        'borderRadius': '4px',
                        'padding': '4px 10px',
                        'fontSize': '0.85rem'
                    }),
                    html.Span(" Limpiar gráficos", style={'color': '#64748b', 'marginLeft': '12px'})
                ], style={'padding': '10px 0', 'borderBottom': '1px solid #e2e8f0'}),
                html.Div([
                    html.Kbd("Esc", style={
                        'background': '#f1f5f9',
                        'border': '1px solid #cbd5e1',
                        'borderRadius': '4px',
                        'padding': '4px 10px',
                        'fontSize': '0.85rem'
                    }),
                    html.Span(" Cerrar modal/ventana", style={'color': '#64748b', 'marginLeft': '12px'})
                ], style={'padding': '10px 0'})
            ], style={
                'background': '#ffffff',
                'borderRadius': '12px',
                'border': '1px solid #e2e8f0',
                'padding': '10px 25px'
            })
        ])
    ])


# ==================== CONTENIDO: CALIBRACIÓN ====================

def content_calibracion():
    return html.Div([
        html.Div([
            html.H3([
                html.I(className="fas fa-balance-scale me-3", style={'color': '#f59e0b'}),
                "Procedimiento de Calibración OSL"
            ], className="mb-3 fw-bold", style={'color': '#0f172a'}),
            html.P([
                "La calibración Open/Short/Load (OSL) es esencial para mediciones precisas. ",
                "Elimina los efectos de cables y conectores, proporcionando mediciones precisas del DUT."
            ], style={'color': '#475569', 'fontSize': '1.1rem', 'marginBottom': '30px'})
        ]),
        
        # ========== WIZARD DE CALIBRACIÓN EN ZORIA ==========
        html.Div([
            html.H4("🚀 Wizard de Calibración Automatizado en ZORIA", className="fw-bold mb-3", style={'color': '#10b981', 'fontSize': '1.5rem'}),
            html.P([
                "ZORIA incluye un ",
                html.Strong("Wizard de Calibración Automatizado"),
                " que simplifica el proceso completo de calibración OSL con ",
                "cálculo automático de ganancias óptimas, guía visual paso a paso y validación en tiempo real."
            ], style={'color': '#475569', 'marginBottom': '20px', 'fontSize': '1.05rem'}),
            
            # Acceso al Wizard
            html.Div([
                html.H6("📍 Acceso al Wizard", className="fw-bold mb-3", style={'color': '#0f172a'}),
                html.Ol([
                    html.Li("Navega a la página \"Calibración\" en el menú lateral izquierdo", style={'marginBottom': '8px'}),
                    html.Li("Haz clic en el botón \"⚖️ Iniciar Wizard de Calibración\"", style={'marginBottom': '8px'}),
                    html.Li("Se abre una ventana arrastrable con 5 pasos guiados")
                ], style={'color': '#475569', 'fontSize': '0.95rem'})
            ], style={'background': '#ecfdf5', 'padding': '20px', 'borderRadius': '12px', 'marginBottom': '25px', 'border': '2px solid #10b981'}),
            
            # Pasos del Wizard
            html.Div([
                html.H6("🔧 Pasos del Wizard de Calibración", className="fw-bold mb-3", style={'color': '#0f172a'}),
                
                # Paso 1: Configuración
                html.Div([
                    html.Div([
                        html.Span("1", className="badge bg-primary me-2", style={'fontSize': '1.1rem', 'padding': '8px 12px'}),
                        html.Strong("Configuración Automática", style={'fontSize': '1.05rem'})
                    ], className="mb-2"),
                    html.Ul([
                        html.Li([html.Strong("Resistencia de calibración (Ω): "), "Ingresar valor de resistencia patrón (ej: 1000Ω)"]),
                        html.Li([html.Strong("Frecuencia (Hz): "), "Frecuencia a la que se realizará la calibración (ej: 1000 Hz)"]),
                        html.Li([html.Strong("🎯 Cálculo automático de ganancia: "), "El wizard calcula automáticamente las ganancias óptimas CH0 y CH1 basándose en la impedancia ingresada"]),
                        html.Li([html.Strong("Indicador visual: "), "Muestra las ganancias calculadas (ej: CH0: 0, CH1: 1)"]),
                        html.Li("Presionar \"▶️ Iniciar Calibración\" para continuar al siguiente paso")
                    ], style={'color': '#475569', 'marginBottom': '0', 'fontSize': '0.9rem'})
                ], style={'background': '#eff6ff', 'padding': '18px', 'borderRadius': '10px', 'marginBottom': '15px', 'border': '1px solid #3b82f6'}),
                
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
                        html.Li("Presionar \"✅ Ejecutar Open\" → barra de progreso en tiempo real"),
                        html.Li([html.I(className="fas fa-check-circle me-1", style={'color': '#10b981'}), "Validación automática de resultados al completar"])
                    ], style={'color': '#475569', 'marginBottom': '0', 'fontSize': '0.9rem'})
                ], style={'background': '#f0fdfa', 'padding': '18px', 'borderRadius': '10px', 'marginBottom': '15px', 'border': '1px solid #14b8a6'}),
                
                # Paso 3: Short
                html.Div([
                    html.Div([
                        html.Span("3", className="badge bg-warning text-dark me-2", style={'fontSize': '1.1rem', 'padding': '8px 12px'}),
                        html.Strong("Short Calibration", style={'fontSize': '1.05rem'})
                    ], className="mb-2"),
                    html.Ul([
                        html.Li([html.Strong("Conexión: "), "Conectar ", html.Strong("TODOS los terminales juntos"), " con un cable (H_CUR, H_POT, L_POT, L_CUR)"]),
                        html.Li([html.Strong("⚡ Reducción automática: "), "El wizard reduce la magnitud a 0.2V ", html.Strong("automáticamente"), " para proteger el circuito"]),
                        html.Li([html.I(className="fas fa-eye me-1"), "Diagrama visual muestra cortocircuito entre todos los terminales"]),
                        html.Li("Presionar \"✅ Ejecutar Short\" → progreso con animación"),
                        html.Li([html.I(className="fas fa-info-circle me-1", style={'color': '#f59e0b'}), "Solo necesario para ganancias CH1 = 0 o 1"])
                    ], style={'color': '#475569', 'marginBottom': '0', 'fontSize': '0.9rem'})
                ], style={'background': '#fffbeb', 'padding': '18px', 'borderRadius': '10px', 'marginBottom': '15px', 'border': '1px solid #f59e0b'}),
                
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
                        html.Li([html.Strong("📊 Medición automática: "), "El sistema mide automáticamente R y X de la carga"]),
                        html.Li("Presionar \"✅ Ejecutar Load\" → resultados en tiempo real"),
                        html.Li([html.I(className="fas fa-check-circle me-1", style={'color': '#10b981'}), "Muestra valores medidos: R real, X reactiva"])
                    ], style={'color': '#475569', 'marginBottom': '0', 'fontSize': '0.9rem'})
                ], style={'background': '#f0fdf4', 'padding': '18px', 'borderRadius': '10px', 'marginBottom': '15px', 'border': '1px solid #10b981'}),
                
                # Paso 5: Guardar
                html.Div([
                    html.Div([
                        html.Span("5", className="badge bg-dark me-2", style={'fontSize': '1.1rem', 'padding': '8px 12px'}),
                        html.Strong("Guardar Calibración", style={'fontSize': '1.05rem'})
                    ], className="mb-2"),
                    html.Ul([
                        html.Li([html.Strong("Nombre descriptivo: "), "Asignar nombre (ej: \"Cal_1kHz_1kOhm_20260209\")"]),
                        html.Li([html.Strong("💾 Commit a Flash: "), "Guardar permanentemente en memoria no volátil del dispositivo"]),
                        html.Li([html.Strong("🔐 Password: "), "Por defecto ", html.Code("Analog123"), " (configurable en settings)"]),
                        html.Li([html.I(className="fas fa-history me-1"), "Historial de calibraciones guardadas en sesión"]),
                        html.Li([html.I(className="fas fa-file-export me-1"), "Botón para exportar calibración a archivo .txt para respaldo"]),
                        html.Li([html.Strong("Validación final: "), "El wizard verifica que todos los pasos se completaron exitosamente"])
                    ], style={'color': '#475569', 'marginBottom': '0', 'fontSize': '0.9rem'})
                ], style={'background': '#f8fafc', 'padding': '18px', 'borderRadius': '10px', 'marginBottom': '15px', 'border': '1px solid #64748b'})
            ], style={'background': '#ffffff', 'padding': '25px', 'borderRadius': '12px', 'border': '1px solid #e2e8f0', 'marginBottom': '25px'}),
            
            # Ventajas del Wizard
            html.Div([
                html.H6("✨ Ventajas del Wizard Automatizado", className="fw-bold mb-3", style={'color': '#10b981'}),
                html.Div([
                    html.Div([
                        html.I(className="fas fa-magic me-2", style={'color': '#10b981', 'fontSize': '1.2rem'}),
                        html.Strong("Cálculo automático de ganancias óptimas"),
                        html.Span(" según la impedancia del DUT", style={'color': '#64748b', 'fontSize': '0.9rem', 'marginLeft': '8px'})
                    ], style={'padding': '12px 0', 'borderBottom': '1px solid #e2e8f0'}),
                    html.Div([
                        html.I(className="fas fa-eye me-2", style={'color': '#10b981', 'fontSize': '1.2rem'}),
                        html.Strong("Diagramas visuales animados"),
                        html.Span(" para cada paso con conexiones claramente marcadas", style={'color': '#64748b', 'fontSize': '0.9rem', 'marginLeft': '8px'})
                    ], style={'padding': '12px 0', 'borderBottom': '1px solid #e2e8f0'}),
                    html.Div([
                        html.I(className="fas fa-check-double me-2", style={'color': '#10b981', 'fontSize': '1.2rem'}),
                        html.Strong("Validación automática de resultados"),
                        html.Span(" en cada paso con mensajes de error descriptivos", style={'color': '#64748b', 'fontSize': '0.9rem', 'marginLeft': '8px'})
                    ], style={'padding': '12px 0', 'borderBottom': '1px solid #e2e8f0'}),
                    html.Div([
                        html.I(className="fas fa-chart-line me-2", style={'color': '#10b981', 'fontSize': '1.2rem'}),
                        html.Strong("Progreso en tiempo real"),
                        html.Span(" con barra de progreso durante mediciones", style={'color': '#64748b', 'fontSize': '0.9rem', 'marginLeft': '8px'})
                    ], style={'padding': '12px 0', 'borderBottom': '1px solid #e2e8f0'}),
                    html.Div([
                        html.I(className="fas fa-save me-2", style={'color': '#10b981', 'fontSize': '1.2rem'}),
                        html.Strong("Guardado directo en flash"),
                        html.Span(" del dispositivo con un solo clic", style={'color': '#64748b', 'fontSize': '0.9rem', 'marginLeft': '8px'})
                    ], style={'padding': '12px 0', 'borderBottom': '1px solid #e2e8f0'}),
                    html.Div([
                        html.I(className="fas fa-history me-2", style={'color': '#10b981', 'fontSize': '1.2rem'}),
                        html.Strong("Historial persistente"),
                        html.Span(" de calibraciones en sesión del navegador", style={'color': '#64748b', 'fontSize': '0.9rem', 'marginLeft': '8px'})
                    ], style={'padding': '12px 0', 'borderBottom': '1px solid #e2e8f0'}),
                    html.Div([
                        html.I(className="fas fa-file-export me-2", style={'color': '#10b981', 'fontSize': '1.2rem'}),
                        html.Strong("Exportación a archivos"),
                        html.Span(" de respaldo (.txt) con todos los parámetros", style={'color': '#64748b', 'fontSize': '0.9rem', 'marginLeft': '8px'})
                    ], style={'padding': '12px 0'})
                ], style={'padding': '15px'})
            ], style={'background': '#ecfdf5', 'borderRadius': '12px', 'border': '2px solid #10b981', 'marginBottom': '40px'}),
            
            html.Hr(style={'margin': '40px 0', 'border': 'none', 'borderTop': '2px solid #e2e8f0'})
        ], style={'marginBottom': '50px'}),
        
        html.Div([
            html.H4("⌨️ Calibración Manual por CLI", className="fw-bold mb-3", style={'color': '#0f172a', 'fontSize': '1.5rem'}),
            html.P([
                "Para usuarios avanzados que prefieren control total, la calibración puede realizarse manualmente ",
                "usando comandos CLI directamente en el terminal del dispositivo."
            ], style={'color': '#475569', 'marginBottom': '30px', 'fontSize': '1.05rem'})
        ]),
        
        # Importancia
        info_box([
            html.Strong("⚠️ IMPORTANTE: "),
            "Realiza la calibración cada vez que cambies de rango de frecuencia o después de 30 minutos de inactividad. ",
            "Los pasos deben realizarse en orden: ", html.Strong("open → short → load")
        ], "warning"),
        
        # Configuraciones de calibración
        html.Div([
            html.H5("Configuraciones de Calibración", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.P([
                "Cada configuración de front-end (combinación de ganancia ch0 y ch1) necesita calibrarse por separado. ",
                "Hay ", html.Strong("16 combinaciones posibles"), " (4 ganancias ch0 × 4 ganancias ch1)."
            ], style={'color': '#475569', 'marginBottom': '15px'}),
            info_box([
                html.Strong("💡 Info: "),
                "Si usas autorange o solo las 7 combinaciones de ganancia estándar, las otras configuraciones no necesitan calibrarse."
            ], "tip"),
            info_box([
                html.Strong("⚠️ Frecuencia: "),
                "Cada punto de calibración es para una frecuencia específica. Siempre calibra lo más cerca posible de la frecuencia de prueba deseada."
            ], "warning")
        ], style={'marginBottom': '40px'}),
        
        # Pasos previos
        html.Div([
            html.H5("Preparación para Calibración", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.Ol([
                html.Li("Seleccionar la configuración de medición deseada (ganancia, frecuencia, magnitud, offset)", style={'color': '#475569', 'marginBottom': '10px'}),
                html.Li([html.Strong("⚠️ Deshabilitar autorange: "), "setgain ch0 <0-3> y setgain ch1 <0-3>"], style={'color': '#475569', 'marginBottom': '10px'}),
                html.Li("Configurar promediado a al menos 200 muestras: average 200", style={'color': '#475569', 'marginBottom': '10px'}),
                html.Li("Asegurar que los switches estén en posiciones DUT y GND", style={'color': '#475569'})
            ], style={'marginBottom': '20px'})
        ], style={'marginBottom': '40px'}),
        
        # Pasos de calibración
        html.Div([
            html.H5("Procedimiento Paso a Paso", className="fw-bold mb-3", style={'color': '#0f172a'}),
            
            # Paso 1: OPEN
            html.Div([
                html.H6([
                    html.Span("1", style={
                        'display': 'inline-block',
                        'width': '32px',
                        'height': '32px',
                        'background': '#f59e0b',
                        'color': '#ffffff',
                        'borderRadius': '50%',
                        'textAlign': 'center',
                        'lineHeight': '32px',
                        'fontSize': '1rem',
                        'marginRight': '12px',
                        'fontWeight': '700'
                    }),
                    "Calibración OPEN"
                ], className="fw-bold mb-3", style={'color': '#0f172a'}),
                html.Ol([
                    html.Li("Conectar terminales H_POT/H_CUR juntos y L_POT/L_CUR juntos (sin conectarlos entre sí)", style={'color': '#475569', 'marginBottom': '10px'}),
                    html.Li([
                        "Ejecutar: ",
                        html.Code("calibrate open", style={'background': '#1e293b', 'color': '#f59e0b', 'padding': '4px 10px', 'borderRadius': '4px', 'marginLeft': '8px'})
                    ], style={'color': '#475569', 'marginBottom': '10px'}),
                    html.Li("Esperar a que complete la medición", style={'color': '#475569', 'marginBottom': '10px'}),
                    html.Li("Verificar que muestre 'open:Done'", style={'color': '#475569'})
                ], style={'marginLeft': '44px'})
            ], style={'background': '#fff7ed', 'padding': '25px', 'borderRadius': '12px', 'border': '2px solid #f59e0b', 'marginBottom': '20px'}),
            
            image_card(IMAGES.get('open_load'), "Configuración OPEN: H_POT/H_CUR juntos, L_POT/L_CUR juntos"),
            
            # Paso 2: SHORT
            html.Div([
                html.H6([
                    html.Span("2", style={
                        'display': 'inline-block',
                        'width': '32px',
                        'height': '32px',
                        'background': '#f59e0b',
                        'color': '#ffffff',
                        'borderRadius': '50%',
                        'textAlign': 'center',
                        'lineHeight': '32px',
                        'fontSize': '1rem',
                        'marginRight': '12px',
                        'fontWeight': '700'
                    }),
                    "Calibración SHORT"
                ], className="fw-bold mb-3", style={'color': '#0f172a'}),
                html.Ol([
                    html.Li("Conectar TODAS las terminales juntas (H_CUR, H_POT, L_POT, L_CUR)", style={'color': '#475569', 'marginBottom': '10px'}),
                    html.Li([
                        html.Strong("⚠️ Solo cuando ganancia ch1 es 0 o 1"), " (omitir para ganancias 2 y 3)"
                    ], style={'color': '#ef4444', 'marginBottom': '10px'}),
                    html.Li([
                        "Reducir magnitude a 0.2: ",
                        html.Code("magnitude 0.2", style={'background': '#1e293b', 'color': '#f59e0b', 'padding': '4px 10px', 'borderRadius': '4px', 'marginLeft': '8px'})
                    ], style={'color': '#475569', 'marginBottom': '10px'}),
                    html.Li([
                        "Ejecutar: ",
                        html.Code("calibrate short", style={'background': '#1e293b', 'color': '#f59e0b', 'padding': '4px 10px', 'borderRadius': '4px', 'marginLeft': '8px'})
                    ], style={'color': '#475569', 'marginBottom': '10px'}),
                    html.Li("Verificar que muestre 'short:Done'", style={'color': '#475569'})
                ], style={'marginLeft': '44px'})
            ], style={'background': '#fff7ed', 'padding': '25px', 'borderRadius': '12px', 'border': '2px solid #f59e0b', 'marginBottom': '20px'}),
            
            # Paso 3: LOAD
            html.Div([
                html.H6([
                    html.Span("3", style={
                        'display': 'inline-block',
                        'width': '32px',
                        'height': '32px',
                        'background': '#f59e0b',
                        'color': '#ffffff',
                        'borderRadius': '50%',
                        'textAlign': 'center',
                        'lineHeight': '32px',
                        'fontSize': '1rem',
                        'marginRight': '12px',
                        'fontWeight': '700'
                    }),
                    "Calibración LOAD"
                ], className="fw-bold mb-3", style={'color': '#0f172a'}),
                html.Ol([
                    html.Li([
                        "Restaurar magnitude a 1: ",
                        html.Code("magnitude 1", style={'background': '#1e293b', 'color': '#f59e0b', 'padding': '4px 10px', 'borderRadius': '4px', 'marginLeft': '8px'})
                    ], style={'color': '#475569', 'marginBottom': '10px'}),
                    html.Li([
                        "Conectar impedancia conocida entre cables de medición. ",
                        html.Strong("Tip: "), "Usar resistor con impedancia cercana al DUT esperado"
                    ], style={'color': '#475569', 'marginBottom': '10px'}),
                    html.Li([
                        "Ejecutar: ",
                        html.Code("calibrate rt <R_ohms> xt <X_ohms>", style={'background': '#1e293b', 'color': '#f59e0b', 'padding': '4px 10px', 'borderRadius': '4px', 'marginLeft': '8px'}),
                        html.Br(),
                        html.Span("donde R es la componente resistiva y X la componente reactiva en Ohms", style={'fontSize': '0.9rem', 'color': '#64748b', 'marginLeft': '8px'})
                    ], style={'color': '#475569', 'marginBottom': '10px'}),
                    html.Li("Verificar que muestre 'load:Done'", style={'color': '#475569'})
                ], style={'marginLeft': '44px'})
            ], style={'background': '#fff7ed', 'padding': '25px', 'borderRadius': '12px', 'border': '2px solid #f59e0b', 'marginBottom': '20px'}),
            
            image_card(IMAGES.get('bnc_load'), "Resistor de calibración conectado entre terminales")
        ]),
        
        # Guardar calibración
        html.Div([
            html.H5("Guardar en Memoria No Volátil", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.P("Después de completar los pasos, los coeficientes se generan y almacenan en RAM. Para guardarlos en memoria flash:", style={'color': '#475569', 'marginBottom': '15px'}),
            html.Pre("""ADMX2001> calibrate commit
PASSWORD> Analog123
commit : success
""", style={
                'background': '#1e293b',
                'color': '#10b981',
                'padding': '20px',
                'borderRadius': '12px',
                'fontFamily': 'monospace',
                'fontSize': '0.9rem',
                'marginBottom': '20px'
            }),
            info_box([
                html.Strong("🔐 Password: "),
                "La contraseña por defecto es ", html.Code("Analog123", style={'background': '#1e293b', 'color': '#10b981', 'padding': '2px 8px', 'borderRadius': '4px'}),
                ". Puede cambiarse con ", html.Code("calibrate password")
            ], "info")
        ], style={'marginBottom': '40px'}),
        
        # ========== COMANDOS DE CALIBRACIÓN EN TERMINAL ==========
        html.Div([
            html.H5([
                html.I(className="fas fa-balance-scale me-2", style={'color': '#f59e0b'}),
                "Comandos de Calibración en Terminal"
            ], className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.P([
                "La calibración Open/Short/Load (OSL) puede realizarse directamente desde el terminal CLI. "
                "Esta sección describe todos los comandos disponibles para calibración manual."
            ], style={'color': '#475569', 'marginBottom': '20px'}),
            
            # Preparación
            html.Div([
                html.H6("Preparación para Calibración", className="fw-bold mb-2", style={'color': '#0f172a'}),
                html.Ol([
                    html.Li([
                        "Deshabilitar autorange y configurar ganancias manualmente:"
                    ], style={'color': '#475569', 'marginBottom': '8px'}),
                    html.Pre("""ADMX2001> setgain ch0 0
ADMX2001> setgain ch1 1""", style={
                        'background': '#1e293b',
                        'color': '#10b981',
                        'padding': '12px',
                        'borderRadius': '6px',
                        'fontFamily': 'monospace',
                        'fontSize': '0.85rem',
                        'marginBottom': '10px'
                    }),
                    html.Li([
                        "Configurar frecuencia de calibración (ej: 1kHz):"
                    ], style={'color': '#475569', 'marginBottom': '8px'}),
                    html.Pre("ADMX2001> frequency 1000", style={
                        'background': '#1e293b',
                        'color': '#10b981',
                        'padding': '8px 12px',
                        'borderRadius': '6px',
                        'fontFamily': 'monospace',
                        'fontSize': '0.85rem',
                        'marginBottom': '10px',
                        'display': 'inline-block'
                    }),
                    html.Li([
                        "Configurar promediado alto para mejor precisión:"
                    ], style={'color': '#475569', 'marginBottom': '8px'}),
                    html.Pre("ADMX2001> average 200", style={
                        'background': '#1e293b',
                        'color': '#10b981',
                        'padding': '8px 12px',
                        'borderRadius': '6px',
                        'fontFamily': 'monospace',
                        'fontSize': '0.85rem',
                        'marginBottom': '10px',
                        'display': 'inline-block'
                    }),
                    html.Li([
                        "Asegurar que los switches S1 y S2 estén en posición DUT/GND"
                    ], style={'color': '#475569'})
                ], style={'marginLeft': '20px'})
            ], style={'background': '#f8fafc', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '20px'}),
            
            # Comandos de calibración
            html.Div([
                html.H6("Comandos de Calibración OSL", className="fw-bold mb-3", style={'color': '#0f172a'}),
                
                # Calibrate Open
                html.Div([
                    html.Code("calibrate open", style={'background': '#1e293b', 'color': '#f59e0b', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P([
                        "Ejecuta calibración de circuito abierto. ",
                        html.Strong("Conexión: "), "H_POT/H_CUR juntos, L_POT/L_CUR juntos (sin conectar H con L)"
                    ], style={'color': '#64748b', 'marginTop': '8px', 'marginBottom': '15px'})
                ]),
                
                # Calibrate Short
                html.Div([
                    html.Code("calibrate short", style={'background': '#1e293b', 'color': '#f59e0b', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P([
                        "Ejecuta calibración de cortocircuito. ",
                        html.Strong("Conexión: "), "TODOS los terminales juntos (H_CUR, H_POT, L_POT, L_CUR)",
                        html.Br(),
                        html.Span("⚠️ Solo para ganancias CH1 = 0 o 1. Reducir magnitud a 0.2V antes.", style={'color': '#f59e0b', 'fontSize': '0.9rem'})
                    ], style={'color': '#64748b', 'marginTop': '8px', 'marginBottom': '15px'})
                ]),
                
                # Calibrate Load
                html.Div([
                    html.Code("calibrate rt <R> xt <X>", style={'background': '#1e293b', 'color': '#f59e0b', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P([
                        "Ejecuta calibración de carga. ",
                        html.Strong("Parámetros: "),
                        html.Br(),
                        html.Code("rt"), " = componente resistiva en Ohms",
                        html.Br(),
                        html.Code("xt"), " = componente reactiva en Ohms (0 para resistores puros)"
                    ], style={'color': '#64748b', 'marginTop': '8px', 'marginBottom': '15px'}),
                    html.P([
                        html.Strong("Ejemplo: "),
                        html.Code("calibrate rt 1e+3 xt 0", style={'background': '#f1f5f9', 'padding': '2px 6px', 'borderRadius': '4px'}),
                        " - Calibra con resistor de 1kΩ"
                    ], style={'color': '#475569', 'fontSize': '0.9rem', 'marginLeft': '20px'})
                ]),
                
                # Calibrate Commit
                html.Div([
                    html.Code("calibrate commit [timestamp]", style={'background': '#1e293b', 'color': '#f59e0b', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P([
                        "Guarda los coeficientes de calibración en memoria no volátil (flash).",
                        html.Br(),
                        "Solicitará password (por defecto: ", html.Code("Analog123"), ")"
                    ], style={'color': '#64748b', 'marginTop': '8px', 'marginBottom': '15px'}),
                    html.Pre("""ADMX2001> calibrate commit
PASSWORD> Analog123
commit : success""", style={
                        'background': '#1e293b',
                        'color': '#10b981',
                        'padding': '12px',
                        'borderRadius': '6px',
                        'fontFamily': 'monospace',
                        'fontSize': '0.85rem',
                        'marginTop': '10px'
                    })
                ]),
                
                info_box([
                    html.Strong("⚠️ Importante: "),
                    "Los pasos deben realizarse en orden: ", html.Strong("open → short → load → commit"), 
                    ". Cada punto de calibración es específico para la frecuencia y ganancias configuradas."
                ], "warning")
                
            ], style={'background': '#ffffff', 'borderRadius': '12px', 'border': '1px solid #e2e8f0', 'padding': '20px', 'marginBottom': '20px'}),
            
            # Comandos adicionales de calibración
            html.Div([
                html.H6("Comandos Adicionales de Calibración", className="fw-bold mb-3", style={'color': '#0f172a'}),
                
                html.Div([
                    html.Code("calibrate list", style={'background': '#1e293b', 'color': '#10b981', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Lista todas las frecuencias con datos de calibración guardados en flash", style={'color': '#64748b', 'marginTop': '8px', 'marginBottom': '15px'})
                ]),
                
                html.Div([
                    html.Code("calibrate list <freq>", style={'background': '#1e293b', 'color': '#10b981', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Muestra qué configuraciones de ganancia están calibradas para una frecuencia específica", style={'color': '#64748b', 'marginTop': '8px', 'marginBottom': '15px'})
                ]),
                
                html.Div([
                    html.Code("calibrate reload", style={'background': '#1e293b', 'color': '#10b981', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Carga los coeficientes de la frecuencia más cercana desde la memoria flash", style={'color': '#64748b', 'marginTop': '8px', 'marginBottom': '15px'})
                ]),
                
                html.Div([
                    html.Code("calibrate switch <evalkit|default>", style={'background': '#1e293b', 'color': '#10b981', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P([
                        "Cambia entre coeficientes precargados (evalkit) o coeficientes de usuario (default)",
                        html.Br(),
                        html.Span("⚠️ Los coeficientes precargados pueden no aplicar a tu configuración específica.", style={'color': '#64748b', 'fontSize': '0.85rem'})
                    ], style={'color': '#64748b', 'marginTop': '8px', 'marginBottom': '15px'})
                ]),
                
                html.Div([
                    html.Code("resetcal", style={'background': '#1e293b', 'color': '#ef4444', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Borra el conjunto de calibración cargado actualmente en RAM (no afecta flash)", style={'color': '#64748b', 'marginTop': '8px', 'marginBottom': '15px'})
                ]),
                
                html.Div([
                    html.Code("calibrate erase", style={'background': '#1e293b', 'color': '#ef4444', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P([
                        html.Strong("⚠️ ¡PELIGRO! "), "Elimina PERMANENTEMENTE todos los conjuntos de calibración de la flash. Requiere password.",
                        html.Br(),
                        html.Span("Use con extrema precaución.", style={'color': '#ef4444', 'fontWeight': 'bold'})
                    ], style={'color': '#64748b', 'marginTop': '8px'})
                ])
            ], style={'background': '#f8fafc', 'padding': '20px', 'borderRadius': '12px', 'border': '1px solid #e2e8f0', 'marginBottom': '20px'}),
            
            # Ejemplo completo de calibración en terminal
            html.Div([
                html.H6("Ejemplo Completo de Calibración en Terminal", className="fw-bold mb-3", style={'color': '#0f172a'}),
                html.P("Calibración a 1kHz con resistor de 1kΩ (configuración CH0=0, CH1=1):", style={'color': '#475569', 'marginBottom': '15px'}),
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
                    'background': '#1e293b',
                    'color': '#e2e8f0',
                    'padding': '20px',
                    'borderRadius': '12px',
                    'fontFamily': 'monospace',
                    'fontSize': '0.85rem',
                    'overflowX': 'auto',
                    'lineHeight': '1.5'
                })
            ], style={'marginBottom': '20px'}),
            
            info_box([
                html.Strong("💡 Consejo: "),
                "Usa el comando ", html.Code("calibrate list"), " después de guardar para verificar que la calibración se almacenó correctamente. "
                "La capacidad de almacenamiento es de 25 conjuntos (EEPROM) o 450 conjuntos (Flash) dependiendo del módulo."
            ], "tip")
            
        ], style={'marginBottom': '40px'}),
        
        # Ejemplo completo
        html.Div([
            html.H5("Ejemplo Completo de Calibración", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.P("Calibrar configuración de ganancia (ch0=0, ch1=1) a 100kHz con resistor de 1kΩ:", style={'color': '#475569', 'marginBottom': '15px'}),
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
                'background': '#1e293b',
                'color': '#e2e8f0',
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
            html.H5("Calibración sobre Frecuencia", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.P([
                "Desde firmware versión 1.2.2, se soporta calibración en múltiples puntos de frecuencia. ",
                "Esto permite calibrar todas las 16 configuraciones de ganancia en varias frecuencias."
            ], style={'color': '#475569', 'marginBottom': '15px'}),
            html.Div([
                html.H6("Comandos Adicionales:", className="fw-bold mb-2", style={'color': '#0f172a'}),
                html.Ul([
                    html.Li([
                        html.Code("calibrate list", style={'background': '#1e293b', 'color': '#f59e0b', 'padding': '2px 8px', 'borderRadius': '4px'}),
                        " - Reporta todas las frecuencias con datos guardados"
                    ]),
                    html.Li([
                        html.Code("calibrate reload", style={'background': '#1e293b', 'color': '#f59e0b', 'padding': '2px 8px', 'borderRadius': '4px'}),
                        " - Carga coeficientes de frecuencia más cercana desde flash"
                    ]),
                    html.Li([
                        html.Code("resetcal", style={'background': '#1e293b', 'color': '#f59e0b', 'padding': '2px 8px', 'borderRadius': '4px'}),
                        " - Borra solo el conjunto cargado en RAM"
                    ]),
                    html.Li([
                        html.Code("calibrate erase", style={'background': '#1e293b', 'color': '#f59e0b', 'padding': '2px 8px', 'borderRadius': '4px'}),
                        " - ⚠️ Elimina TODOS los conjuntos permanentemente (requiere password)"
                    ])
                ], style={'color': '#475569'})
            ], style={'background': '#f8fafc', 'padding': '20px', 'borderRadius': '8px', 'marginBottom': '15px'}),
            html.P([
                html.Strong("Capacidad de almacenamiento:"),
                html.Br(),
                "• Módulos con EEPROM: 25 conjuntos de calibración",
                html.Br(),
                "• Módulos con Flash: 450 conjuntos de calibración"
            ], style={'color': '#475569', 'marginTop': '15px'})
        ], style={'marginBottom': '40px'}),
        
        # Coeficientes precargados
        html.Div([
            html.H5("Conjuntos de Calibración Precargados", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.P("Algunos módulos envían con coeficientes de calibración precargados:", style={'color': '#475569', 'marginBottom': '15px'}),
            html.Pre("""ADMX2001> calibrate switch evalkit    # Usar coeficientes precargados
ADMX2001> calibrate switch default    # Usar coeficientes de usuario
""", style={
                'background': '#1e293b',
                'color': '#10b981',
                'padding': '15px',
                'borderRadius': '8px',
                'fontFamily': 'monospace',
                'fontSize': '0.9rem'
            }),
            info_box([
                html.Strong("⚠️ Advertencia: "),
                "Los coeficientes precargados pueden no aplicar a tu configuración de prueba específica y su precisión no está garantizada."
            ], "warning")
        ])
    ])


# ==================== CONTENIDO: CLI ====================

def content_cli():
    return html.Div([
        html.Div([
            html.H3([
                html.I(className="fas fa-terminal me-3", style={'color': '#8b5cf6'}),
                "Terminal CLI - Interfaz de Línea de Comandos"
            ], className="mb-3 fw-bold", style={'color': '#0f172a'}),
            html.P([
                "La interfaz de línea de comandos CLI permite control completo del sistema ADMX2001B. ",
                "Usa ", html.Code("help <comando>"), " para obtener ayuda sobre cualquier comando."
            ], style={'color': '#475569', 'fontSize': '1.1rem', 'marginBottom': '30px'})
        ]),
        
        # Modos de Display
        html.Div([
            html.H5("Modos de Display de Medición", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.P("El ADMX2001B retorna resultados en uno de 18 modos de display diferentes. El resultado siempre se reporta en la unidad SI base.", style={'color': '#475569', 'marginBottom': '15px'}),
            html.Div([
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("Modo", style={'color': '#0f172a', 'fontWeight': '600', 'padding': '10px', 'borderBottom': '2px solid #8b5cf6'}),
                            html.Th("Nombre", style={'color': '#0f172a', 'fontWeight': '600', 'padding': '10px', 'borderBottom': '2px solid #8b5cf6'}),
                            html.Th("Forma", style={'color': '#0f172a', 'fontWeight': '600', 'padding': '10px', 'borderBottom': '2px solid #8b5cf6'}),
                            html.Th("Unidad SI", style={'color': '#0f172a', 'fontWeight': '600', 'padding': '10px', 'borderBottom': '2px solid #8b5cf6'})
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([html.Td("0", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("Capacitancia serie y resistencia equivalente", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("Cs, Rs", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569', 'fontFamily': 'monospace'}), html.Td("Farads, Ohms", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("1", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("Capacitancia serie y factor de disipación", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("Cs, D", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569', 'fontFamily': 'monospace'}), html.Td("Farads, adimensional", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("2", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("Capacitancia serie y factor de calidad", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("Cs, Q", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569', 'fontFamily': 'monospace'}), html.Td("Farads, adimensional", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("3", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("Inductancia serie y resistencia equivalente", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("Ls, Rs", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569', 'fontFamily': 'monospace'}), html.Td("Henries, Ohms", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("4", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("Inductancia serie y factor de disipación", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("Ls, D", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569', 'fontFamily': 'monospace'}), html.Td("Henries, adimensional", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("5", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("Inductancia serie y factor de calidad", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("Ls, Q", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569', 'fontFamily': 'monospace'}), html.Td("Henries, adimensional", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("6", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'background': '#fef3c7'}), html.Td("Impedancia en coordenadas rectangulares (default)", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569', 'background': '#fef3c7'}), html.Td("R, X", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569', 'fontFamily': 'monospace', 'background': '#fef3c7'}), html.Td("Ohms, Ohms", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569', 'background': '#fef3c7'})]),
                        html.Tr([html.Td("7", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("Impedancia en magnitud y fase (grados)", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("Z, deg", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569', 'fontFamily': 'monospace'}), html.Td("Ohms, Grados", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("8", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("Impedancia en magnitud y fase (radianes)", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("Z, rad", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569', 'fontFamily': 'monospace'}), html.Td("Ohms, Radianes", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("9", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("Capacitancia paralela y resistencia equivalente", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("Cp, Rp", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569', 'fontFamily': 'monospace'}), html.Td("Farads, Ohms", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("10", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("Capacitancia paralela y factor de disipación", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("Cp, D", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569', 'fontFamily': 'monospace'}), html.Td("Farads, adimensional", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("11", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("Capacitancia paralela y factor de calidad", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("Cp, Q", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569', 'fontFamily': 'monospace'}), html.Td("Farads, adimensional", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("12", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("Inductancia paralela y resistencia equivalente", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("Lp, Rp", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569', 'fontFamily': 'monospace'}), html.Td("Henries, Ohms", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("13", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("Inductancia paralela y factor de disipación", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("Lp, D", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569', 'fontFamily': 'monospace'}), html.Td("Henries, adimensional", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("14", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("Inductancia paralela y factor de calidad", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("Lp, Q", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569', 'fontFamily': 'monospace'}), html.Td("Henries, adimensional", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("15", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("Admitancia en coordenadas rectangulares", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("G, B", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569', 'fontFamily': 'monospace'}), html.Td("Siemens, Siemens", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("16", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("Admitancia en magnitud y fase (grados)", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("Y, deg", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569', 'fontFamily': 'monospace'}), html.Td("Siemens, Grados", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("17", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("Admitancia en magnitud y fase (radianes)", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("Y, rad", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569', 'fontFamily': 'monospace'}), html.Td("Siemens, Radianes", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("18", style={'padding': '8px'}), html.Td("Apagado", style={'padding': '8px', 'color': '#475569'}), html.Td("None", style={'padding': '8px', 'color': '#475569', 'fontFamily': 'monospace'}), html.Td("None", style={'padding': '8px', 'color': '#475569'})])
                    ])
                ], style={'width': '100%', 'borderCollapse': 'collapse', 'fontSize': '0.9rem'})
            ], style={
                'background': '#ffffff',
                'borderRadius': '12px',
                'border': '1px solid #e2e8f0',
                'padding': '20px',
                'marginBottom': '30px',
                'overflowX': 'auto'
            })
        ]),
        
        # Selección de Ganancia
        html.Div([
            html.H5("Selección de Ganancia y Rango", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.P("Por defecto, el ADMX2001B está en modo auto-ranging. Para seleccionar manualmente:", style={'color': '#475569', 'marginBottom': '15px'}),
            html.Div([
                html.H6("Ganancias de Corriente (Ch1)", className="fw-bold mb-2", style={'color': '#0f172a'}),
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("Ganancia", style={'padding': '8px', 'borderBottom': '2px solid #8b5cf6'}),
                            html.Th("Corriente Máxima", style={'padding': '8px', 'borderBottom': '2px solid #8b5cf6'}),
                            html.Th("Transimpedancia", style={'padding': '8px', 'borderBottom': '2px solid #8b5cf6'})
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([html.Td("0", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("25mA", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("49.9Ω", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("1", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("2.5mA", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("499Ω", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("2", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("250μA", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("4.99kΩ", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("3", style={'padding': '8px'}), html.Td("25μA", style={'padding': '8px', 'color': '#475569'}), html.Td("49.9kΩ", style={'padding': '8px', 'color': '#475569'})])
                    ])
                ], style={'width': '100%', 'borderCollapse': 'collapse', 'marginBottom': '20px'}),
                
                html.H6("Ganancias de Voltaje (Ch0)", className="fw-bold mb-2", style={'color': '#0f172a'}),
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("Ganancia", style={'padding': '8px', 'borderBottom': '2px solid #8b5cf6'}),
                            html.Th("Rango Máximo", style={'padding': '8px', 'borderBottom': '2px solid #8b5cf6'}),
                            html.Th("Factor de Ganancia", style={'padding': '8px', 'borderBottom': '2px solid #8b5cf6'})
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([html.Td("0", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("±2.5V", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("1", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("1", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("±1.25V", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("2", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("2", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("±625mV", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'}), html.Td("4", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("3", style={'padding': '8px'}), html.Td("±312.5mV", style={'padding': '8px', 'color': '#475569'}), html.Td("8", style={'padding': '8px', 'color': '#475569'})])
                    ])
                ], style={'width': '100%', 'borderCollapse': 'collapse', 'marginBottom': '20px'}),
                
                html.H6("Rangos de Impedancia Recomendados", className="fw-bold mb-2", style={'color': '#0f172a'}),
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("Ganancia Ch0", style={'padding': '8px', 'borderBottom': '2px solid #8b5cf6'}),
                            html.Th("Ganancia Ch1", style={'padding': '8px', 'borderBottom': '2px solid #8b5cf6'}),
                            html.Th("Rango de Impedancia", style={'padding': '8px', 'borderBottom': '2px solid #8b5cf6'})
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([html.Td("3", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("0", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("< 10Ω", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("2", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("0", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("< 25Ω", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("1", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("0", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("< 50Ω", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("0", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("0", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("100Ω a 1kΩ", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("0", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("1", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("1kΩ a 10kΩ", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("0", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("2", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0'}), html.Td("10kΩ a 100kΩ", style={'padding': '8px', 'borderBottom': '1px solid #e2e8f0', 'color': '#475569'})]),
                        html.Tr([html.Td("0", style={'padding': '8px'}), html.Td("3", style={'padding': '8px'}), html.Td("> 100kΩ", style={'padding': '8px', 'color': '#475569'})])
                    ])
                ], style={'width': '100%', 'borderCollapse': 'collapse'})
            ], style={
                'background': '#ffffff',
                'borderRadius': '12px',
                'border': '1px solid #e2e8f0',
                'padding': '20px',
                'marginBottom': '30px',
                'overflowX': 'auto'
            })
        ]),
        
        # Comandos básicos
        html.Div([
            html.H5("Comandos Básicos", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.Div([
                html.Div([
                    html.Code("z", style={'background': '#1e293b', 'color': '#10b981', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Inicia una medición de impedancia", style={'color': '#64748b', 'marginTop': '8px'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.Code("frequency <Hz>", style={'background': '#1e293b', 'color': '#10b981', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Configura frecuencia de medición (0.2 Hz a 10 MHz, 0=DC)", style={'color': '#64748b', 'marginTop': '8px'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.Code("display <0-18>", style={'background': '#1e293b', 'color': '#10b981', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Selecciona modo de display de medición", style={'color': '#64748b', 'marginTop': '8px'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.Code("magnitude <V>", style={'background': '#1e293b', 'color': '#10b981', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Configura amplitud de señal de excitación (0 a 2.5V pk)", style={'color': '#64748b', 'marginTop': '8px'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.Code("offset <V>", style={'background': '#1e293b', 'color': '#10b981', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Configura offset DC (±2.5V)", style={'color': '#64748b', 'marginTop': '8px'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.Code("average <1-256>", style={'background': '#1e293b', 'color': '#10b981', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Número de muestras para promediar (reduce ruido)", style={'color': '#64748b', 'marginTop': '8px'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.Code("setgain ch0 <0-3>", style={'background': '#1e293b', 'color': '#10b981', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Configura ganancia de voltaje (canal 0)", style={'color': '#64748b', 'marginTop': '8px'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.Code("setgain ch1 <0-3>", style={'background': '#1e293b', 'color': '#10b981', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Configura ganancia de corriente (canal 1)", style={'color': '#64748b', 'marginTop': '8px'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.Code("setgain auto", style={'background': '#1e293b', 'color': '#10b981', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Activa auto-ranging de ganancia", style={'color': '#64748b', 'marginTop': '8px'})
                ])
            ], style={
                'background': '#ffffff',
                'borderRadius': '12px',
                'border': '1px solid #e2e8f0',
                'padding': '25px',
                'marginBottom': '30px'
            })
        ]),
        
        # Barridos
        html.Div([
            html.H5("Barridos Paramétricos (Sweeps)", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.P("El ADMX2001B puede realizar barridos automáticos:", style={'color': '#475569', 'marginBottom': '15px'}),
            html.Div([
                html.Div([
                    html.Code("sweep_type frequency <inicio> <fin>", style={'background': '#1e293b', 'color': '#10b981', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Barrido de frecuencia (común en EIS)", style={'color': '#64748b', 'marginTop': '8px'})
                ], style={'marginBottom': '15px'}),
                html.Div([
                    html.Code("sweep_type bias <inicio> <fin>", style={'background': '#1e293b', 'color': '#10b981', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Barrido de offset DC (mediciones C-V)", style={'color': '#64748b', 'marginTop': '8px'})
                ], style={'marginBottom': '15px'}),
                html.Div([
                    html.Code("sweep_scale <log|linear>", style={'background': '#1e293b', 'color': '#10b981', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Escala logarítmica o lineal", style={'color': '#64748b', 'marginTop': '8px'})
                ], style={'marginBottom': '15px'}),
                html.Div([
                    html.Code("count <puntos>", style={'background': '#1e293b', 'color': '#10b981', 'padding': '6px 12px', 'borderRadius': '4px', 'fontSize': '0.9rem'}),
                    html.P("Número de puntos en el barrido", style={'color': '#64748b', 'marginTop': '8px'})
                ])
            ], style={
                'background': '#ffffff',
                'borderRadius': '12px',
                'border': '1px solid #e2e8f0',
                'padding': '20px',
                'marginBottom': '30px'
            })
        ]),
        
        # Ejemplo
        html.Div([
            html.H5("Ejemplo de Uso Completo", className="fw-bold mb-3", style={'color': '#0f172a'}),
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
                'background': '#1e293b',
                'color': '#e2e8f0',
                'padding': '20px',
                'borderRadius': '12px',
                'fontFamily': 'monospace',
                'fontSize': '0.85rem',
                'overflowX': 'auto',
                'marginBottom': '20px'
            }),
            
            html.H6("Barrido Logarítmico:", className="fw-bold mb-2", style={'color': '#0f172a'}),
            html.Pre("""ADMX2001> count 11
ADMX2001> sweep_type frequency 100 1000
ADMX2001> sweep_scale log
ADMX2001> z
1.000000e+05,5.683433e-13,8.149236e+07
1.258925e+05,5.704062e-13,4.727518e+07
...
""", style={
                'background': '#1e293b',
                'color': '#e2e8f0',
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
                html.I(className="fas fa-code me-3", style={'color': '#ef4444'}),
               "Actualización de Firmware ADMX2001B"
            ], className="mb-3 fw-bold", style={'color': '#0f172a'}),
            html.P([
                "El firmware del módulo ADMX2001B es actualizable por el usuario. ",
                "Mantén tu dispositivo actualizado con la última versión para mejoras de rendimiento y correcciones."
            ], style={'color': '#475569', 'fontSize': '1.1rem', 'marginBottom': '30px'})
        ]),
        
        info_box([
            html.Strong("⚠️ ADVERTENCIA CRÍTICA: "),
            "Actualizar entre ciertas versiones de firmware puede causar pérdida de coeficientes de calibración guardados. ",
            "Respalda tu calibración antes de actualizar contactando admx-support@analog.com para asistencia."
        ], "danger"),
        
        # Versiones disponibles
        html.Div([
            html.H5("Versiones de Firmware Disponibles", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.Div([
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("Versión", style={'color': '#0f172a', 'fontWeight': '600', 'padding': '12px', 'borderBottom': '2px solid #ef4444'}),
                            html.Th("Estado", style={'color': '#0f172a', 'fontWeight': '600', 'padding': '12px', 'borderBottom': '2px solid #ef4444'}),
                            html.Th("Características Principales", style={'color': '#0f172a', 'fontWeight': '600', 'padding': '12px', 'borderBottom': '2px solid #ef4444'})
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([
                            html.Td(html.Span("1.3.2", style={'background': '#10b981', 'color': '#ffffff', 'padding': '4px 12px', 'borderRadius': '16px', 'fontSize': '0.9rem', 'fontWeight': '600'}), style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td(html.Span("Estable", style={'color': '#10b981', 'fontWeight': '600'}), style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td("Optimizaciones de tiempo de medición, GUI Python incluida, correcciones menores", style={'padding': '12px', 'color': '#475569', 'borderBottom': '1px solid #e2e8f0'})
                        ]),
                        html.Tr([
                            html.Td("1.3.1", style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td(html.Span("Estable", style={'color': '#10b981', 'fontWeight': '600'}), style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td("Mejoras sustanciales de ruido, correcciones y más", style={'padding': '12px', 'color': '#475569', 'borderBottom': '1px solid #e2e8f0'})
                        ]),
                        html.Tr([
                            html.Td("1.2.4", style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td(html.Span("Estable", style={'color': '#10b981', 'fontWeight': '600'}), style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td("Igual que 1.2.2, script de instalación Python añadido", style={'padding': '12px', 'color': '#475569', 'borderBottom': '1px solid #e2e8f0'})
                        ]),
                        html.Tr([
                            html.Td("1.2.2", style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td(html.Span("Estable", style={'color': '#10b981', 'fontWeight': '600'}), style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td("Calibración sobre frecuencia, salidas digitales configurables, soporte trigger externo", style={'padding': '12px', 'color': '#475569', 'borderBottom': '1px solid #e2e8f0'})
                        ]),
                        html.Tr([
                            html.Td("1.2.0", style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td(html.Span("Estable", style={'color': '#10b981', 'fontWeight': '600'}), style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td("Correcciones, mejoras de ruido y repetibilidad", style={'padding': '12px', 'color': '#475569', 'borderBottom': '1px solid #e2e8f0'})
                        ]),
                        html.Tr([
                            html.Td("1.1.1", style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td(html.Span("Legacy", style={'color': '#64748b', 'fontWeight': '600'}), style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td("Mismas correcciones que 1.2.0, no compatible con placas con flash", style={'padding': '12px', 'color': '#475569', 'borderBottom': '1px solid #e2e8f0'})
                        ]),
                        html.Tr([
                            html.Td("1.1.0", style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td(html.Span("Legacy", style={'color': '#64748b', 'fontWeight': '600'}), style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td("Interfaz SPI añadida, self test integrado", style={'padding': '12px', 'color': '#475569', 'borderBottom': '1px solid #e2e8f0'})
                        ]),
                        html.Tr([
                            html.Td("1.0.1", style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td(html.Span("Legacy", style={'color': '#64748b', 'fontWeight': '600'}), style={'padding': '12px', 'borderBottom': '1px solid #e2e8f0'}),
                            html.Td("Versión inicial", style={'padding': '12px', 'color': '#475569', 'borderBottom': '1px solid #e2e8f0'})
                        ]),
                        html.Tr([
                            html.Td("1.0.0", style={'padding': '12px'}),
                            html.Td(html.Span("Legacy", style={'color': '#64748b', 'fontWeight': '600'}), style={'padding': '12px'}),
                            html.Td("Primera versión de lanzamiento", style={'padding': '12px', 'color': '#475569'})
                        ])
                    ])
                ], style={'width': '100%', 'borderCollapse': 'collapse'})
            ], style={
                'background': '#ffffff',
                'borderRadius': '12px',
                'border': '1px solid #e2e8f0',
                'padding': '20px',
                'marginBottom': '30px',
                'overflowX': 'auto'
            })
        ]),
        
        # Equipo requerido
        html.Div([
            html.H5("Equipo y Software Requerido", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.Div([
                html.Div([
                    html.H6("Hardware:", className="fw-bold mb-2", style={'color': '#0f172a'}),
                    html.Ul([
                        html.Li("Placa EVAL-ADMX2001EBZ"),
                        html.Li("Módulo ADMX2001B"),
                        html.Li([html.Strong("Intel Altera USB Blaster"), " (programador JTAG)"]),
                        html.Li("Adaptador de corriente 9VDC"),
                        html.Li("Cable USB para USB Blaster")
                    ], style={'color': '#475569'})
                ], style={'marginBottom': '20px'}),
                html.Div([
                    html.H6("Software:", className="fw-bold mb-2", style={'color': '#0f172a'}),
                    html.Ul([
                        html.Li("Python 3.7 o superior"),
                        html.Li([html.Strong("Intel Quartus Prime Programmer And Tools"), " (última versión)"]),
                        html.Li("Drivers para Altera USB Blaster"),
                        html.Li("Carpeta de firmware conteniendo archivo *.pof")
                    ], style={'color': '#475569'})
                ], style={'marginBottom': '20px'})
            ], style={
                'background': '#f8fafc',
                'padding': '20px',
                'borderRadius': '12px',
                'border': '1px solid #e2e8f0',
                'marginBottom': '30px'
            })
        ]),
        
        # Método con script
        html.Div([
            html.H5("Método de Actualización con Script Python", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.P([
                html.Strong("Versiones 1.2.4+"), " incluyen un script de instalación Python que automatiza el proceso:"
            ], style={'color': '#475569', 'marginBottom': '15px'}),
            html.Pre("""python admx2001_flash_pof.py --pof "C:\\Analog Devices\\Admx2001Firmware-Relx.y.z\\Firmware\\admx_lcr_encrypted.pof"
""", style={
                'background': '#1e293b',
                'color': '#10b981',
                'padding': '20px',
                'borderRadius': '12px',
                'fontFamily': 'monospace',
                'fontSize': '0.9rem',
                'overflowX': 'auto',
                'marginBottom': '15px'
            }),
            info_box([
                html.Strong("⚠️ IMPORTANTE: "),
                "NO desconectar la placa ni interrumpir el proceso de programación. ",
                "El proceso toma entre 20-30 segundos. Una interrupción puede dañar permanentemente el módulo."
            ], "danger")
        ], style={'marginBottom': '40px'}),
        
        # Procedimiento manual
        html.Div([
            html.H5("Procedimiento Manual de Actualización", className="fw-bold mb-3", style={'color': '#0f172a'}),
            
            html.Div([
                html.H6([
                    html.Span("1", style={
                        'display': 'inline-block',
                        'width': '32px',
                        'height': '32px',
                        'background': '#ef4444',
                        'color': '#ffffff',
                        'borderRadius': '50%',
                        'textAlign': 'center',
                        'lineHeight': '32px',
                        'fontSize': '1rem',
                        'marginRight': '12px',
                        'fontWeight': '700'
                    }),
                    "Descargar Firmware"
                ], className="fw-bold mb-3", style={'color': '#0f172a'}),
                html.P([
                    "Contacta ", html.Strong("admx-support@analog.com"), " para obtener el archivo de programación (*.pof) más reciente."
                ], style={'color': '#475569', 'marginLeft': '44px'})
            ], style={'background': '#fee2e2', 'padding': '20px', 'borderRadius': '12px', 'border': '2px solid #ef4444', 'marginBottom': '20px'}),
            
            html.Div([
                html.H6([
                    html.Span("2", style={
                        'display': 'inline-block',
                        'width': '32px',
                        'height': '32px',
                        'background': '#ef4444',
                        'color': '#ffffff',
                        'borderRadius': '50%',
                        'textAlign': 'center',
                        'lineHeight': '32px',
                        'fontSize': '1rem',
                        'marginRight': '12px',
                        'fontWeight': '700'
                    }),
                    "Instalar Software"
                ], className="fw-bold mb-3", style={'color': '#0f172a'}),
                html.Ol([
                    html.Li("Descargar e instalar Intel Quartus Prime Programmer", style={'marginBottom': '8px'}),
                    html.Li("Instalar drivers para Altera USB Blaster", style={'marginBottom': '8px'}),
                    html.Li("Verificar Python 3.7+ instalado", style={'marginBottom': '8px'})
                ], style={'color': '#475569', 'marginLeft': '44px'})
            ], style={'background': '#fee2e2', 'padding': '20px', 'borderRadius': '12px', 'border': '2px solid #ef4444', 'marginBottom': '20px'}),
            
            html.Div([
                html.H6([
                    html.Span("3", style={
                        'display': 'inline-block',
                        'width': '32px',
                        'height': '32px',
                        'background': '#ef4444',
                        'color': '#ffffff',
                        'borderRadius': '50%',
                        'textAlign': 'center',
                        'lineHeight': '32px',
                        'fontSize': '1rem',
                        'marginRight': '12px',
                        'fontWeight': '700'
                    }),
                    "Conexión de Hardware"
                ], className="fw-bold mb-3", style={'color': '#0f172a'}),
                html.Ol([
                    html.Li("Conectar adaptador de corriente 9VDC a la placa EVAL-ADMX2001EBZ", style={'marginBottom': '8px'}),
                    html.Li("Conectar cable del Altera USB Blaster al conector JTAG de la placa", style={'marginBottom': '8px'}),
                    html.Li("Conectar USB Blaster a la PC", style={'marginBottom': '8px'}),
                    html.Li("Verificar que el LED de power esté encendido", style={'marginBottom': '8px'})
                ], style={'color': '#475569', 'marginLeft': '44px'})
            ], style={'background': '#fee2e2', 'padding': '20px', 'borderRadius': '12px', 'border': '2px solid #ef4444', 'marginBottom': '20px'}),
            
            html.Div([
                html.H6([
                    html.Span("4", style={
                        'display': 'inline-block',
                        'width': '32px',
                        'height': '32px',
                        'background': '#ef4444',
                        'color': '#ffffff',
                        'borderRadius': '50%',
                        'textAlign': 'center',
                        'lineHeight': '32px',
                        'fontSize': '1rem',
                        'marginRight': '12px',
                        'fontWeight': '700'
                    }),
                    "Programación"
                ], className="fw-bold mb-3", style={'color': '#0f172a'}),
                html.P("Ejecutar el script de programación:", style={'color': '#475569', 'marginLeft': '44px', 'marginBottom': '10px'}),
                html.Pre("""python admx2001_flash_pof.py --pof firmware.pof
""", style={
                    'background': '#1e293b',
                    'color': '#10b981',
                    'padding': '15px',
                    'borderRadius': '8px',
                    'fontFamily': 'monospace',
                    'fontSize': '0.9rem',
                    'marginLeft': '44px',
                    'marginBottom': '10px'
                }),
                html.P([
                    html.Strong("Duración esperada: "), "20-30 segundos"
                ], style={'color': '#475569', 'marginLeft': '44px'})
            ], style={'background': '#fee2e2', 'padding': '20px', 'borderRadius': '12px', 'border': '2px solid #ef4444', 'marginBottom': '20px'}),
            
            html.Div([
                html.H6([
                    html.Span("5", style={
                        'display': 'inline-block',
                        'width': '32px',
                        'height': '32px',
                        'background': '#ef4444',
                        'color': '#ffffff',
                        'borderRadius': '50%',
                        'textAlign': 'center',
                        'lineHeight': '32px',
                        'fontSize': '1rem',
                        'marginRight': '12px',
                        'fontWeight': '700'
                    }),
                    "Verificación"
                ], className="fw-bold mb-3", style={'color': '#0f172a'}),
                html.Ol([
                    html.Li("Desconectar el USB Blaster", style={'marginBottom': '8px'}),
                    html.Li("Conectar cable UART-USB", style={'marginBottom': '8px'}),
                    html.Li("Abrir terminal (TeraTerm, 115200 baud)", style={'marginBottom': '8px'}),
                    html.Li([
                        "Ejecutar comando: ",
                        html.Code("*idn", style={'background': '#1e293b', 'color': '#10b981', 'padding': '2px 8px', 'borderRadius': '4px'}),
                        " para verificar la nueva versión"
                    ], style={'marginBottom': '8px'}),
                    html.Li("Verificar self-test (LED verde)", style={'marginBottom': '8px'})
                ], style={'color': '#475569', 'marginLeft': '44px'})
            ], style={'background': '#fee2e2', 'padding': '20px', 'borderRadius': '12px', 'border': '2px solid #ef4444', 'marginBottom': '20px'})
        ]),
        
        # Obtener archivos
        html.Div([
            html.H5("Cómo Obtener Archivos de Firmware", className="fw-bold mb-3", style={'color': '#0f172a'}),
            html.P("Los archivos de programación deben solicitarse directamente a Analog Devices:", style={'color': '#475569', 'marginBottom': '15px'}),
            html.Div([
                html.Div([
                    html.I(className="fas fa-envelope", style={'color': '#ef4444', 'fontSize': '2rem', 'marginBottom': '15px'}),
                    html.Br(),
                    html.Strong("Email de Soporte:", style={'display': 'block', 'marginBottom': '8px'}),
                    html.A("admx-support@analog.com", href="mailto:admx-support@analog.com", style={'color': '#3b82f6', 'textDecoration': 'none', 'fontSize': '1.1rem'})
                ], style={'textAlign': 'center', 'padding': '30px'})
            ], style={
                'background': '#ffffff',
                'borderRadius': '12px',
                'border': '2px solid #ef4444',
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
                    'color': '#d4af37',
                    'fontSize': '8px',
                    'marginRight': '12px',
                    'animation': 'pulse 2s infinite'
                }),
                html.Span("DOCUMENTACIÓN OFICIAL", style={
                    'fontSize': '0.75rem',
                    'letterSpacing': '0.3em',
                    'fontWeight': '500',
                    'color': '#64748b'
                })
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
                    'color': '#0f172a',
                    'marginBottom': '10px'
                }),
                html.Span("EVAL-ADMX2001", style={
                    'display': 'block',
                    'fontSize': 'clamp(1rem, 2vw, 1.5rem)',
                    'fontWeight': '300',
                    'letterSpacing': '0.3em',
                    'color': '#d4af37',
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
                "Documentación completa del sistema de análisis de impedancia.",
                html.Br(),
                "Selecciona una sección para comenzar."
            ], style={
                'fontSize': 'clamp(1rem, 1.5vw, 1.25rem)',
                'fontWeight': '300',
                'color': '#475569',
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
        'background': 'linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)',
        'position': 'relative'
    })


# ==================== LAYOUT PRINCIPAL ====================
layout = html.Div([
    dcc.Location(id='url', refresh=False),
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
                        label='🚀 Inicio Rápido',
                        value='inicio',
                        children=content_inicio_rapido(),
                        className='doc-tab',
                        selected_className='doc-tab-selected'
                    ),
                    dcc.Tab(
                        label='🔧 Hardware',
                        value='hardware',
                        children=content_hardware(),
                        className='doc-tab',
                        selected_className='doc-tab-selected'
                    ),
                    dcc.Tab(
                        label='💻 Software',
                        value='software',
                        children=content_software(),
                        className='doc-tab',
                        selected_className='doc-tab-selected'
                    ),
                    dcc.Tab(
                        label='⚖️ Calibración',
                        value='calibracion',
                        children=content_calibracion(),
                        className='doc-tab',
                        selected_className='doc-tab-selected'
                    ),
                    dcc.Tab(
                        label='⌨️ CLI',
                        value='cli',
                        children=content_cli(),
                        className='doc-tab',
                        selected_className='doc-tab-selected'
                    ),
                    dcc.Tab(
                        label='🔌 Firmware',
                        value='firmware',
                        children=content_firmware(),
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
    ], className="content", style={'background': '#ffffff'}),
    
    footer(),
    floating_terminal_button()
    
], className="sc-chart d-flex flex-column", style={
    'minHeight': '100vh',
    'background': '#ffffff'
})


def register_callbacks(app):
    pass


def register_documentation_page(app):
    register_callbacks(app)
