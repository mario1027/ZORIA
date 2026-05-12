"""
Página de Calibración para ADMX2001 - Wizard Automatizado
Sistema completo de calibración Open/Short/Load con interfaz guiada,
animaciones profesionales y ganancia automática.
"""
from dash import html, dcc, Input, Output, State, ctx
from dash.exceptions import PreventUpdate
from dash_spa import register_page
from datetime import datetime
import json
import logging
import re

# Logger
logger = logging.getLogger(__name__)

# Importar componentes comunes
from pages.common.sidebar import sideBar
from pages.common.mobile_nav import mobileNavBar
from pages.common.footer import footer
from pages.common.floating_terminal_button import floating_terminal_button

# Registrar la página
register_page(
    __name__,
    path='/calibration',
    title='Calibración - ZORIA',
    name='Calibración ADMX2001'
)


def calibration_wizard_modal():
    """
    Wizard de Calibración - Ventana arrastrable tipo escritorio.
    Sistema moderno de ventanas con capacidad de mover, minimizar, maximizar.
    """
    return html.Div([
        # Stores para el estado del wizard
        dcc.Store(id='cal-wizard-state', data={
            'step': 0,
            'config': {'r_load': 1000.0, 'freq': 1000, 'ch0': 0, 'ch1': 0},
            'results': {'open': None, 'short': None, 'load': None}
        }),
        dcc.Store(id='cal-saved-calibrations', data=[], storage_type='session'),
        dcc.Store(id='cal-wizard-initialized', data=False),
        dcc.Interval(id='cal-wizard-interval', interval=500),
        
        # Ventana arrastrable
        html.Div([
            # Header - estructura estandarizada
            html.Div([
                # Título
                html.Div([
                    html.I(className="fas fa-balance-scale me-2"),
                    html.Span('', **{'data-i18n': 'cal.wizard_title'}),
                ], className="window-title"),
                
                # Controles
                html.Div([
                    html.Button(
                        html.I(className="fas fa-minus"),
                        id="cal-wizard-minimize",
                        className="window-control-btn window-btn-minimize",
                        title="Minimizar"
                    ),
                    html.Button(
                        html.I(className="fas fa-expand"),
                        id="cal-wizard-maximize",
                        className="window-control-btn window-btn-maximize",
                        title="Maximizar"
                    ),
                    html.Button(
                        html.I(className="fas fa-times"),
                        id="cal-wizard-close",
                        className="window-control-btn window-btn-close",
                        title="Cerrar"
                    ),
                ], className="window-controls")
            ], className="window-header", id="cal-wizard-header"),
            
            # Contenido del wizard
            html.Div([
                # Barra de progreso con pasos numerados
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div("1", className="wizard-step-indicator", id="cal-step-icon-1"),
                            html.Span("Config", className="wizard-step-label")
                        ], className="wizard-step", id="cal-step-1"),
                        html.Div(className="wizard-step-connector", id="cal-connector-1"),
                        html.Div([
                            html.Div("2", className="wizard-step-indicator", id="cal-step-icon-2"),
                            html.Span("Open", className="wizard-step-label")
                        ], className="wizard-step", id="cal-step-2"),
                        html.Div(className="wizard-step-connector", id="cal-connector-2"),
                        html.Div([
                            html.Div("3", className="wizard-step-indicator", id="cal-step-icon-3"),
                            html.Span("Short", className="wizard-step-label")
                        ], className="wizard-step", id="cal-step-3"),
                        html.Div(className="wizard-step-connector", id="cal-connector-3"),
                        html.Div([
                            html.Div("4", className="wizard-step-indicator", id="cal-step-icon-4"),
                            html.Span("Load", className="wizard-step-label")
                        ], className="wizard-step", id="cal-step-4"),
                        html.Div(className="wizard-step-connector", id="cal-connector-4"),
                        html.Div([
                            html.Div("5", className="wizard-step-indicator", id="cal-step-icon-5"),
                            html.Span("Guardar", className="wizard-step-label")
                        ], className="wizard-step", id="cal-step-5"),
                    ], className="wizard-steps")
                ], className="wizard-progress"),
                
                # Área de contenido dinámico (scrollable)
                html.Div(className="wizard-content", children=[
                    # Paso 0: Bienvenida/Configuración
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-magic fa-3x text-primary mb-3"),
                            html.H4("Wizard de Calibración Automatizado", className="mb-3"),
                            html.P("Este wizard te guiará paso a paso en el proceso de calibración Open/Short/Load.", className="text-muted mb-4"),
                            
                            # Configuración automática
                            html.Div([
                                html.H6("Configuración Automática", className="mb-3 text-start"),
                                
                                # Input de Resistencia
                                html.Div([
                                    html.Label([
                                        html.I(className="fas fa-resistor me-2"),
                                        "Resistencia de Calibración (Ω)"
                                    ], className="form-label text-start d-block"),
                                    dcc.Input(
                                        id='cal-wizard-r-load',
                                        type='number',
                                        value=1000,
                                        min=0.1,
                                        max=10000000,
                                        className="form-control",
                                        placeholder="Ej: 1000"
                                    ),
                                    html.Small("Rango típico: 100Ω - 100kΩ. El sistema calculará las ganancias óptimas automáticamente.", 
                                              className="text-muted d-block text-start mt-1")
                                ], className="mb-3"),
                                
                                # Input de Frecuencia
                                html.Div([
                                    html.Label([
                                        html.I(className="fas fa-wave-square me-2"),
                                        "Frecuencia de Calibración (Hz)"
                                    ], className="form-label text-start d-block"),
                                    dcc.Input(
                                        id='cal-wizard-freq',
                                        type='number',
                                        value=1000,
                                        min=0.2,
                                        max=10000000,
                                        className="form-control",
                                        placeholder="Ej: 1000"
                                    ),
                                    html.Small("Frecuencia a la que se realizará la calibración.", 
                                              className="text-muted d-block text-start mt-1")
                                ], className="mb-3"),
                                
                                # Indicador de ganancia calculada
                                html.Div([
                                    html.Div([
                                        html.I(className="fas fa-calculator me-2"),
                                        html.Span("Ganancia calculada:", className="me-2"),
                                        html.Span(id='cal-wizard-gain-display', children=[
                                            html.Span("CH0: 0", className="badge bg-info me-2"),
                                            html.Span("CH1: 0", className="badge bg-info")
                                        ])
                                    ], className="alert alert-dark border-0"),
                                ], id='cal-wizard-gain-panel', className="mb-3"),
                                
                                html.Button([
                                    html.I(className="fas fa-play me-2"),
                                    html.Span('Iniciar Calibración', **{'data-i18n': 'cal.start_wizard'}),
                                ], id='cal-wizard-start', className="btn btn-primary btn-lg w-100")
                            ], className="p-4 border rounded bg-light")
                        ], className="text-center py-4")
                    ], id='cal-wizard-step-0', className="wizard-step-content"),
                    
                    # Paso 1: Open Calibration
                    html.Div([
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-circle-notch fa-spin fa-3x text-primary mb-3"),
                                html.H4("Open Calibration", className="mb-3"),
                                html.P("Conecta los terminales según el diagrama:", className="text-muted mb-4")
                            ], className="text-center mb-4"),
                            
                            # Diagrama visual interactivo
                            html.Div([
                                html.Div([
                                    # Diagrama de conexión Open
                                    html.Div([
                                        html.Div([
                                            html.Div("H_CUR", className="cal-terminal cal-terminal-hcur"),
                                            html.Div(className="cal-wire cal-wire-open-h"),
                                            html.Div("H_POT", className="cal-terminal cal-terminal-hpot")
                                        ], className="cal-diagram-row"),
                                        html.Div([
                                            html.Div("L_CUR", className="cal-terminal cal-terminal-lcur"),
                                            html.Div(className="cal-wire cal-wire-open-l"),
                                            html.Div("L_POT", className="cal-terminal cal-terminal-lpot")
                                        ], className="cal-diagram-row"),
                                        html.Div([
                                            html.Div("OPEN", className="cal-indicator cal-indicator-open cal-anim-blink")
                                        ], className="cal-diagram-indicator")
                                    ], className="cal-diagram")
                                ], className="cal-diagram-container mb-4")
                            ]),
                            
                            # Instrucciones detalladas
                            html.Div([
                                html.H6("Instrucciones:", className="mb-2"),
                                html.Ol([
                                    html.Li("Conecta H_CUR con H_POT (cable corto)"),
                                    html.Li("Conecta L_CUR con L_POT (cable corto)"),
                                    html.Li("Deja separados los pares H y L (circuito abierto)")
                                ], className="text-start")
                            ], className="alert alert-info border-0 mb-4"),
                            
                            # Barra de progreso de la operación
                            html.Div([
                                html.Div(id="cal-open-progress", className="progress-bar progress-bar-striped progress-bar-animated", style={'width': '0%'})
                            ], className="progress mb-3", style={'height': '8px'}),
                            
                            html.Div(id="cal-open-status", className="text-center text-muted small mb-3"),
                            
                            html.Button([
                                html.I(className="fas fa-check-circle me-2"),
                                "Ejecutar Open"
                            ], id='cal-wizard-run-open', className="btn btn-primary w-100")
                        ], className="py-3")
                    ], id='cal-wizard-step-1', className="wizard-step-content", style={'display': 'none'}),
                    
                    # Paso 2: Short Calibration
                    html.Div([
                        html.Div([
                            html.Div([
                                html.H4("Short Calibration", className="mb-3"),
                                html.P("Conecta TODOS los terminales juntos:", className="text-muted mb-4")
                            ], className="text-center mb-4"),
                            
                            # Diagrama visual
                            html.Div([
                                html.Div([
                                    html.Div([
                                        html.Div("H_CUR", className="cal-terminal cal-terminal-hcur cal-terminal-active"),
                                        html.Div(className="cal-wire cal-wire-short"),
                                        html.Div("H_POT", className="cal-terminal cal-terminal-hpot cal-terminal-active")
                                    ], className="cal-diagram-row"),
                                    html.Div([
                                        html.Div("L_CUR", className="cal-terminal cal-terminal-lcur cal-terminal-active"),
                                        html.Div(className="cal-wire cal-wire-short"),
                                        html.Div("L_POT", className="cal-terminal cal-terminal-lpot cal-terminal-active")
                                    ], className="cal-diagram-row"),
                                    html.Div([
                                        html.Div("SHORT", className="cal-indicator cal-indicator-short cal-anim-blink")
                                    ], className="cal-diagram-indicator")
                                ], className="cal-diagram cal-diagram-short")
                            ], className="cal-diagram-container mb-4"),
                            
                            html.Div([
                                html.H6("Importante:", className="mb-2"),
                                html.Ul([
                                    html.Li("Conecta todos los terminales juntos con un cable"),
                                    html.Li("Asegúrate de que la conexión sea firme"),
                                    html.Li(html.Span("Magnitud reducida automáticamente a 0.2V", className="text-warning"))
                                ], className="text-start")
                            ], className="alert alert-warning border-0 mb-4"),
                            
                            html.Div([
                                html.Div(id="cal-short-progress", className="progress-bar progress-bar-striped progress-bar-animated bg-warning", style={'width': '0%'})
                            ], className="progress mb-3", style={'height': '8px'}),
                            
                            html.Div(id="cal-short-status", className="text-center text-muted small mb-3"),
                            
                            html.Button([
                                html.I(className="fas fa-check-circle me-2"),
                                "Ejecutar Short"
                            ], id='cal-wizard-run-short', className="btn btn-warning w-100 text-dark")
                        ], className="py-3")
                    ], id='cal-wizard-step-2', className="wizard-step-content", style={'display': 'none'}),
                    
                    # Paso 3: Load Calibration
                    html.Div([
                        html.Div([
                            html.Div([
                                html.H4("Load Calibration", className="mb-3"),
                                html.P(f"Conecta la resistencia de calibración:", className="text-muted mb-2"),
                                html.H3(id="cal-wizard-load-value-display", children="1000 Ω", className="text-success mb-4")
                            ], className="text-center mb-4"),
                            
                            # Diagrama visual
                            html.Div([
                                html.Div([
                                    html.Div([
                                        html.Div("H", className="cal-terminal cal-terminal-hcur cal-terminal-active"),
                                        html.Div(className="cal-wire cal-wire-load"),
                                        html.Div("L", className="cal-terminal cal-terminal-lpot cal-terminal-active")
                                    ], className="cal-diagram-row"),
                                    html.Div([
                                        html.Div("LOAD", className="cal-indicator cal-indicator-load cal-anim-blink")
                                    ], className="cal-diagram-indicator")
                                ], className="cal-diagram cal-diagram-load")
                            ], className="cal-diagram-container mb-4"),
                            
                            html.Div([
                                html.H6("Instrucciones:", className="mb-2"),
                                html.Ol([
                                    html.Li("Conecta la resistencia de precisión entre H_CUR y L_POT"),
                                    html.Li(["Valor nominal: ", html.Strong(id="cal-wizard-load-instruction-value", children="1000 Ω")]),
                                    html.Li("Asegúrate de que las conexiones sean firmes y limpias")
                                ], className="text-start")
                            ], className="alert alert-success border-0 mb-4"),
                            
                            html.Div([
                                html.Div(id="cal-load-progress", className="progress-bar progress-bar-striped progress-bar-animated bg-success", style={'width': '0%'})
                            ], className="progress mb-3", style={'height': '8px'}),
                            
                            html.Div(id="cal-load-status", className="text-center text-muted small mb-3"),
                            
                            html.Button([
                                html.I(className="fas fa-check-circle me-2"),
                                "Ejecutar Load"
                            ], id='cal-wizard-run-load', className="btn btn-success w-100")
                        ], className="py-3")
                    ], id='cal-wizard-step-3', className="wizard-step-content", style={'display': 'none'}),
                    
                    # Paso 4: Commit
                    html.Div([
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-save fa-3x text-info mb-3"),
                                html.H4("Guardar Calibración", className="mb-3"),
                                html.P("Guarda los coeficientes en memoria no volátil", className="text-muted mb-4")
                            ], className="text-center mb-4"),
                            
                            # Resumen de la calibración
                            html.Div([
                                html.H6("Resumen de Calibración:", className="mb-3"),
                                html.Div([
                                    html.Div([
                                        html.Span("", className="text-success me-2"),
                                        html.Span("Open: "),
                                        html.Span(id="cal-summary-open", children="Completado", className="text-success")
                                    ], className="mb-2"),
                                    html.Div([
                                        html.Span("", className="text-success me-2"),
                                        html.Span("Short: "),
                                        html.Span(id="cal-summary-short", children="Completado", className="text-success")
                                    ], className="mb-2"),
                                    html.Div([
                                        html.Span("", className="text-success me-2"),
                                        html.Span("Load: "),
                                        html.Span(id="cal-summary-load", children="Completado", className="text-success")
                                    ], className="mb-2"),
                                    html.Hr(),
                                    html.Div([
                                        html.Span("Resistencia: ", className="text-muted"),
                                        html.Strong(id="cal-summary-r", children="1000 Ω")
                                    ], className="mb-1"),
                                    html.Div([
                                        html.Span("Frecuencia: ", className="text-muted"),
                                        html.Strong(id="cal-summary-freq", children="1000 Hz")
                                    ], className="mb-1"),
                                    html.Div([
                                        html.Span("Ganancia: ", className="text-muted"),
                                        html.Strong(id="cal-summary-gain", children="CH0=0, CH1=0")
                                    ])
                                ], className="p-3 bg-dark rounded mb-4")
                            ]),
                            
                            html.Div([
                                html.I(className="fas fa-lock me-2"),
                                html.Span("Contraseña: ", className="me-2"),
                                html.Code("Analog123", className="bg-light text-dark px-2 py-1 rounded")
                            ], className="alert alert-secondary border-0 mb-4"),
                            
                            html.Div([
                                html.Div(id="cal-commit-progress", className="progress-bar progress-bar-striped progress-bar-animated bg-info", style={'width': '0%'})
                            ], className="progress mb-3", style={'height': '8px'}),
                            
                            html.Div(id="cal-commit-status", className="text-center text-muted small mb-3"),
                            
                            html.Button([
                                html.I(className="fas fa-save me-2"),
                                "Guardar en Flash"
                            ], id='cal-wizard-run-commit', className="btn btn-info w-100 text-white")
                        ], className="py-3")
                    ], id='cal-wizard-step-4', className="wizard-step-content", style={'display': 'none'}),
                    
                    # Paso 5: Completado
                    html.Div([
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-check-circle fa-4x text-success mb-3 cal-anim-bounce"),
                                html.H3("¡Calibración Completada!", className="mb-3 text-success"),
                                html.P("Los coeficientes han sido guardados exitosamente.", className="text-muted mb-4")
                            ], className="text-center mb-4"),
                            
                            html.Div([
                                html.H6("Detalles:", className="mb-3"),
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            html.Span("Timestamp: ", className="text-muted"),
                                            html.Span(id="cal-complete-timestamp", children=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                                        ], className="mb-2"),
                                        html.Div([
                                            html.Span("Resistencia: ", className="text-muted"),
                                            html.Strong(id="cal-complete-r", children="1000 Ω")
                                        ], className="mb-2"),
                                        html.Div([
                                            html.Span("Frecuencia: ", className="text-muted"),
                                            html.Strong(id="cal-complete-freq", children="1000 Hz")
                                        ], className="mb-2")
                                    ], className="p-3 bg-light rounded")
                                ])
                            ], className="mb-4"),
                            
                            html.Div([
                                html.Button([
                                    html.I(className="fas fa-redo me-2"),
                                    "Nueva Calibración"
                                ], id='cal-wizard-restart', className="btn btn-outline-primary me-2"),
                                html.Button([
                                    html.I(className="fas fa-times me-2"),
                                    "Cerrar"
                                ], id='cal-wizard-finish', className="btn btn-primary")
                            ], className="text-center")
                        ], className="py-4")
                    ], id='cal-wizard-step-5', className="wizard-step-content", style={'display': 'none'}),
                    
                ])
            ], className="window-body"),
            
        ], id="cal-wizard-modal", className='draggable-window calibration-window', style={'display': 'none'})
    ])


def calibration_page_layout():
    """Layout principal de la página de calibración"""
    return html.Div([
        # Mobile Navbar
        mobileNavBar(),
        
        # Botón flotante del terminal
        floating_terminal_button(),
        
        # Wizard de calibración (modal movible)
        calibration_wizard_modal(),
        
        # Stores
        dcc.Store(id='calibration-state', data={
            'is_calibrating': False,
            'current_step': 0,
            'config': {}
        }),
        dcc.Interval(id='calibration-status-interval', interval=1000),
        
        # Contenedor principal
        html.Div([
            sideBar(),
            
            html.Main([
                html.Div([
                    # Header
                    html.Div([
                        html.Div([
                            html.H2([
                                html.I(className="fas fa-balance-scale me-3"),
                                html.Span('', **{'data-i18n': 'cal.title'}),
                            ], className="h3 mb-1"),
                            html.P("Sistema de calibración Open/Short/Load para ADMX2001",
                                   className="text-muted mb-0 small")
                        ], className="col-12 col-md-8 mb-3 mb-md-0"),
                        html.Div([
                            html.Span(id="cal-device-status", children=[
                                html.I(className="fas fa-circle text-success me-2"),
                                "Listo"
                            ], className="badge bg-dark px-3 py-2")
                        ], className="col-12 col-md-4 d-flex justify-content-md-end align-items-center")
                    ], className="row align-items-center py-4 mb-4 border-bottom"),
                    
                    # Grid de acciones
                    html.Div([
                        # Card: Nueva Calibración
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.I(className="fas fa-magic fa-3x text-primary mb-3"),
                                    html.H5(html.Span('', **{'data-i18n': 'cal.wizard_title'}), className="card-title"),
                                    html.P("Inicia el wizard de calibración automatizado con ganancia inteligente.", className="card-text text-muted small"),
                                    html.Button([
                                        html.I(className="fas fa-play me-2"),
                                        html.Span('', **{'data-i18n': 'cal.start_wizard'}),
                                    ], id="btn-start-calibration", className="btn btn-primary w-100")
                                ], className="card-body text-center")
                            ], className="card h-100 shadow-sm border-0")
                        ], className="col-lg-4 col-md-6 mb-4"),
                        
                        # Card: Ver Calibraciones
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.I(className="fas fa-list fa-3x text-info mb-3"),
                                    html.H5(html.Span('', **{'data-i18n': 'cal.list_title'}), className="card-title"),
                                    html.P("Visualiza y gestiona las calibraciones almacenadas en el dispositivo.", className="card-text text-muted small"),
                                    html.Button([
                                        html.I(className="fas fa-eye me-2"),
                                        "Ver Lista"
                                    ], id="btn-view-calibrations", className="btn btn-info w-100 text-white")
                                ], className="card-body text-center")
                            ], className="card h-100 shadow-sm border-0")
                        ], className="col-lg-4 col-md-6 mb-4"),
                        
                        # Card: Eliminar Calibraciones
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.I(className="fas fa-trash-alt fa-3x text-danger mb-3"),
                                    html.H5("Eliminar Calibraciones", className="card-title"),
                                    html.P("Borra todas las calibraciones guardadas en la memoria flash.", className="card-text text-muted small"),
                                    html.Button([
                                        html.I(className="fas fa-exclamation-triangle me-2"),
                                        "Eliminar Todo"
                                    ], id="btn-delete-calibrations", className="btn btn-outline-danger w-100")
                                ], className="card-body text-center")
                            ], className="card h-100 shadow-sm border-0")
                        ], className="col-lg-4 col-md-6 mb-4"),
                        
                    ], className="row mb-4"),
                    
                    # Panel de Calibraciones Guardadas
                    html.Div([
                        html.Div([
                            html.Div([
                                html.H5([
                                    html.I(className="fas fa-database me-2"),
                                    "Calibraciones Almacenadas"
                                ]),
                                html.Button([
                                    html.I(className="fas fa-sync-alt me-1"),
                                    "Actualizar"
                                ], id="btn-refresh-calibrations", className="btn btn-sm btn-outline-secondary")
                            ], className="d-flex justify-content-between align-items-center mb-3"),
                            
                            html.Div([
                                html.Table([
                                    html.Thead([
                                        html.Tr([
                                            html.Th("#", className="text-center"),
                                            html.Th("Fecha/Hora"),
                                            html.Th("Resistencia"),
                                            html.Th("Frecuencia"),
                                            html.Th("Ganancia"),
                                            html.Th("Estado", className="text-center"),
                                            html.Th("Acciones", className="text-center")
                                        ])
                                    ]),
                                    html.Tbody(id="calibrations-table-body", children=[
                                        html.Tr([
                                            html.Td("1", className="text-center"),
                                            html.Td("2025-02-07 14:30:00"),
                                            html.Td("1000 Ω"),
                                            html.Td("1000 Hz"),
                                            html.Td("CH0:0, CH1:0"),
                                            html.Td([
                                                html.Span("", className="text-success")
                                            ], className="text-center"),
                                            html.Td([
                                                html.Button([
                                                    html.I(className="fas fa-info-circle")
                                                ], className="btn btn-sm btn-outline-info me-1"),
                                                html.Button([
                                                    html.I(className="fas fa-trash")
                                                ], className="btn btn-sm btn-outline-danger")
                                            ], className="text-center")
                                        ])
                                    ])
                                ], className="table table-hover")
                            ], className="table-responsive")
                        ], className="card-body")
                    ], id="calibrations-panel", className="card shadow-sm"),
                    
                    # Guía rápida
                    html.Div([
                        html.Div([
                            html.H5([
                                html.I(className="fas fa-book me-2"),
                                "Guía de Calibración"
                            ], className="mb-3"),
                            html.Div([
                                html.Div([
                                    html.Div([
                                        html.Span("1", className="cal-guide-number"),
                                        html.Div([
                                            html.H6("Configuración", className="mb-1"),
                                            html.Small("Ingresa el valor de tu resistencia de calibración", className="text-muted")
                                        ])
                                    ], className="cal-guide-item")
                                ], className="col-md-6 mb-3"),
                                html.Div([
                                    html.Div([
                                        html.Span("2", className="cal-guide-number"),
                                        html.Div([
                                            html.H6("Open", className="mb-1"),
                                            html.Small("Conecta H_CUR-H_POT y L_CUR-L_POT separados", className="text-muted")
                                        ])
                                    ], className="cal-guide-item")
                                ], className="col-md-6 mb-3"),
                                html.Div([
                                    html.Div([
                                        html.Span("3", className="cal-guide-number"),
                                        html.Div([
                                            html.H6("Short", className="mb-1"),
                                            html.Small("Conecta todos los terminales juntos", className="text-muted")
                                        ])
                                    ], className="cal-guide-item")
                                ], className="col-md-6 mb-3"),
                                html.Div([
                                    html.Div([
                                        html.Span("4", className="cal-guide-number"),
                                        html.Div([
                                            html.H6("Load", className="mb-1"),
                                            html.Small("Conecta la resistencia de calibración", className="text-muted")
                                        ])
                                    ], className="cal-guide-item")
                                ], className="col-md-6 mb-3"),
                            ], className="row")
                        ], className="card-body")
                    ], className="card shadow-sm mt-4")
                    
                ], className="container-fluid py-4")
            ], className="main-content w-100")
        ], className="d-flex flex-grow-1"),
        
        footer()
    ], className="d-flex flex-column min-vh-100")


layout = calibration_page_layout()


def register_calibration_callbacks(app):
    """Registra los callbacks para la página de calibración"""
    
    # Clientside callback para inicializar el wizard
    app.clientside_callback(
        """
        function(trigger) {
            // Inicializar sistema de ventanas cuando se abra
            setTimeout(function() {
                if (window.DraggableWindows) {
                    window.DraggableWindows.init('cal-wizard-modal', 'cal-wizard-header', {
                        width: 750,
                        height: 600
                    });
                }
            }, 300);
            return window.dash_clientside.no_update;
        }
        """,
        Output('cal-wizard-initialized', 'data'),
        Input('cal-wizard-modal', 'style'),
        prevent_initial_call=True
    )
    
    # Los controles de ventana (maximizar, minimizar, cerrar) son manejados
    # automáticamente por draggable_windows.js a través de setupWindowControls()
    # No se requieren callbacks adicionales
    
    # Callback para calcular ganancia automáticamente
    @app.callback(
        Output('cal-wizard-gain-display', 'children'),
        Output('cal-wizard-gain-panel', 'className'),
        Input('cal-wizard-r-load', 'value')
    )
    def calculate_auto_gain(r_load):
        """Calcula automáticamente las ganancias según el valor de resistencia"""
        if not r_load or r_load <= 0:
            return [
                html.Span("CH0: -", className="badge bg-secondary me-2"),
                html.Span("CH1: -", className="badge bg-secondary")
            ], "mb-3 opacity-50"
        
        # Lógica de ganancia según documentación
        # CH0 (voltaje): determina rango de impedancia
        # CH1 (corriente): valores más altos para impedancias más altas
        
        if r_load < 10:
            ch0, ch1 = 3, 0
        elif r_load < 25:
            ch0, ch1 = 2, 0
        elif r_load < 50:
            ch0, ch1 = 1, 0
        elif r_load <= 1000:
            ch0, ch1 = 0, 0
        elif r_load <= 10000:
            ch0, ch1 = 0, 1
        elif r_load <= 100000:
            ch0, ch1 = 0, 2
        else:
            ch0, ch1 = 0, 3
        
        return [
            html.Span(f"CH0: {ch0}", className="badge bg-info me-2"),
            html.Span(f"CH1: {ch1}", className="badge bg-info")
        ], "mb-3"
    
    # Callback para abrir/cerrar wizard
    @app.callback(
        Output('cal-wizard-modal', 'style'),
        Output('cal-wizard-state', 'data'),
        Input('btn-start-calibration', 'n_clicks'),
        Input('cal-wizard-close', 'n_clicks'),
        Input('cal-wizard-finish', 'n_clicks'),
        State('cal-wizard-state', 'data'),
        prevent_initial_call=True
    )
    def toggle_wizard(start_clicks, close_clicks, finish_clicks, wizard_state):
        """Controla la visibilidad del wizard"""
        if not ctx.triggered:
            raise PreventUpdate
        
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if triggered_id == 'btn-start-calibration':
            wizard_state['step'] = 0
            return {'display': 'block'}, wizard_state
        
        if triggered_id in ['cal-wizard-close', 'cal-wizard-finish']:
            return {'display': 'none'}, wizard_state
        
        raise PreventUpdate
    
    # Callback para navegación del wizard
    @app.callback(
        Output('cal-wizard-step-0', 'style'),
        Output('cal-wizard-step-1', 'style'),
        Output('cal-wizard-step-2', 'style'),
        Output('cal-wizard-step-3', 'style'),
        Output('cal-wizard-step-4', 'style'),
        Output('cal-wizard-step-5', 'style'),
        Output('cal-step-1', 'className'),
        Output('cal-step-2', 'className'),
        Output('cal-step-3', 'className'),
        Output('cal-step-4', 'className'),
        Output('cal-step-5', 'className'),
        Output('cal-connector-1', 'className'),
        Output('cal-connector-2', 'className'),
        Output('cal-connector-3', 'className'),
        Output('cal-connector-4', 'className'),
        Output('cal-wizard-load-value-display', 'children'),
        Output('cal-wizard-load-instruction-value', 'children'),
        Output('cal-summary-r', 'children'),
        Output('cal-summary-freq', 'children'),
        Output('cal-summary-gain', 'children'),
        Output('cal-complete-r', 'children'),
        Output('cal-complete-freq', 'children'),
        Input('cal-wizard-start', 'n_clicks'),
        Input('cal-wizard-run-open', 'n_clicks'),
        Input('cal-wizard-run-short', 'n_clicks'),
        Input('cal-wizard-run-load', 'n_clicks'),
        Input('cal-wizard-run-commit', 'n_clicks'),
        Input('cal-wizard-restart', 'n_clicks'),
        State('cal-wizard-state', 'data'),
        State('cal-wizard-r-load', 'value'),
        State('cal-wizard-freq', 'value'),
        prevent_initial_call=True
    )
    def navigate_wizard(start, open_clk, short_clk, load_clk, commit_clk, restart, state, r_load, freq):
        """Navega entre los pasos del wizard"""
        if not ctx.triggered:
            raise PreventUpdate
        
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Determinar paso actual
        if triggered_id == 'cal-wizard-start':
            state['step'] = 1
        elif triggered_id == 'cal-wizard-run-open':
            state['step'] = 2
        elif triggered_id == 'cal-wizard-run-short':
            state['step'] = 3
        elif triggered_id == 'cal-wizard-run-load':
            state['step'] = 4
        elif triggered_id == 'cal-wizard-run-commit':
            state['step'] = 5
        elif triggered_id == 'cal-wizard-restart':
            state['step'] = 0
        
        step = state['step']
        
        # Construir estilos de pasos
        def step_style(n):
            return {'display': 'block'} if step == n else {'display': 'none'}
        
        # Clases de pasos
        def step_class(n):
            base = "wizard-step"
            if step > n:
                return f"{base} completed"
            elif step == n:
                return f"{base} active"
            return base
        
        # Clases de conectores
        def connector_class(n):
            base = "wizard-step-connector"
            if step > n:
                return f"{base} completed"
            return base
        
        # Valores de configuración
        r_display = f"{r_load or 1000} Ω"
        f_display = f"{freq or 1000} Hz"
        
        # Calcular ganancia para resumen
        r_val = r_load or 1000
        if r_val < 10:
            ch0, ch1 = 3, 0
        elif r_val < 25:
            ch0, ch1 = 2, 0
        elif r_val < 50:
            ch0, ch1 = 1, 0
        elif r_val <= 1000:
            ch0, ch1 = 0, 0
        elif r_val <= 10000:
            ch0, ch1 = 0, 1
        elif r_val <= 100000:
            ch0, ch1 = 0, 2
        else:
            ch0, ch1 = 0, 3
        
        gain_display = f"CH0={ch0}, CH1={ch1}"
        
        return (
            step_style(0), step_style(1), step_style(2), step_style(3), step_style(4), step_style(5),
            step_class(1), step_class(2), step_class(3), step_class(4), step_class(5),
            connector_class(1), connector_class(2), connector_class(3), connector_class(4),
            r_display, r_display, r_display, f_display, gain_display, r_display, f_display
        )


    # Callback para actualizar tabla de calibraciones
    @app.callback(
        Output('calibrations-table-body', 'children'),
        Input('btn-refresh-calibrations', 'n_clicks'),
        prevent_initial_call=False
    )
    def refresh_calibrations_table(n_clicks):
        """Actualiza la tabla de calibraciones almacenadas desde el dispositivo"""
        
        from lib.device_state import device_state
        from lib.calibration_parser import parse_calibrate_list_lines
        
        try:
            # Obtener dispositivo desde device_state global
            device = device_state.device
            
            if device is None or not device_state.is_connected or not hasattr(device, 'calibration'):
                return [
                    html.Tr([
                        html.Td(colSpan="7", className="text-center text-muted", children=[
                            html.I(className="fas fa-exclamation-triangle me-2"),
                            "Dispositivo no conectado. Conecta el ADMX2001 desde el Dashboard."
                        ])
                    ])
                ]
            
            # Obtener calibraciones del dispositivo
            calibrations_raw = device.calibration.list_calibrations()
            
            # Log debug MUY DETALLADO para ver qué se recibe
            logger.info(f"[Cal] '==== DEBUG calibrate list ===='")
            logger.info(f"[Cal] Recibido {len(calibrations_raw) if calibrations_raw else 0} líneas de 'calibrate list'")
            logger.info(f"[Cal] Tipo: {type(calibrations_raw)}")
            
            if calibrations_raw:
                logger.info(f"[Cal] '==== TODAS LAS LÍNEAS CRUDAS ===='")
                for idx, line in enumerate(calibrations_raw):
                    logger.info(f"[Cal] RAW[{idx:2d}]: {repr(line)}")
                logger.info(f"[Cal] '==== FIN LÍNEAS CRUDAS ===='")
            
            # Verificar si hay errores en la respuesta
            if calibrations_raw:
                has_error = any('error' in line.lower() or 'failed' in line.lower() for line in calibrations_raw)
                if has_error:
                    error_msg = next((line for line in calibrations_raw if 'error' in line.lower() or 'failed' in line.lower()), 'Error desconocido')
                    return [
                        html.Tr([
                            html.Td(colSpan="7", className="text-center text-warning", children=[
                                html.I(className="fas fa-exclamation-triangle me-2"),
                                html.Div([
                                    html.P("El dispositivo reportó un error al listar calibraciones:", className="mb-2"),
                                    html.Code(error_msg, className="d-block bg-dark text-warning p-2 rounded mb-2"),
                                    html.Small([
                                        "Esto puede ocurrir si:",
                                        html.Ul([
                                            html.Li("No hay calibraciones guardadas en el dispositivo"),
                                            html.Li("La calibración está corrupta o incompleta"),
                                            html.Li("El ADC está saturado (desconecta la carga y reinicia)")
                                        ], className="text-start mt-2")
                                    ], className="text-muted")
                                ])
                            ])
                        ])
                    ]
            
            if not calibrations_raw or len(calibrations_raw) == 0:
                return [
                    html.Tr([
                        html.Td(colSpan="7", className="text-center text-muted", children=[
                            html.I(className="fas fa-info-circle me-2"),
                            "No hay calibraciones almacenadas en el dispositivo."
                        ])
                    ])
                ]
            
            # Parsear y crear filas de tabla con parseo robusto
            rows = []
            frequencies_with_configs = parse_calibrate_list_lines(calibrations_raw)
            
            # Log detallado del resultado del parseo
            logger.info(f"[Cal] '==== RESULTADO DEL PARSEO ===='")
            logger.info(f"[Cal] Frecuencias parseadas: {len(frequencies_with_configs)}")
            for freq_key in sorted(frequencies_with_configs.keys(), key=lambda x: float(x) if x.isdigit() else 0):
                configs = frequencies_with_configs[freq_key]
                logger.info(f"[Cal] FREQ={freq_key} Hz: {len(configs)} configs")
                for idx, cfg in enumerate(configs):
                    if cfg.get('placeholder'):
                        logger.info(f"[Cal]   [{idx}] PLACEHOLDER")
                    else:
                        logger.info(f"[Cal]   [{idx}] CH0={cfg.get('ch0')}, CH1={cfg.get('ch1')}, RES={cfg.get('res')}")
            logger.info(f"[Cal] '==== FIN PARSEO ===='")
            
            # Crear filas organizadas por frecuencia
            row_num = 1
            for freq, configs in sorted(frequencies_with_configs.items(), 
                                       key=lambda x: float(x[0]) if x[0].isdigit() else 0):
                
                if configs and configs[0].get('placeholder'):
                    # Solo frecuencia, sin configuraciones
                    rows.append(
                        html.Tr([
                            html.Td(str(row_num), className="text-center"),
                            html.Td(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                                   className="small text-muted"),
                            html.Td("N/A"),
                            html.Td(f"{freq} Hz", className="fw-bold"),
                            html.Td("Usar 'calibrate list " + freq + "' para detalles", 
                                   className="text-muted small"),
                            html.Td([
                                html.Span("○", className="text-info", 
                                         title="Frecuencia calibrada")
                            ], className="text-center"),
                            html.Td([
                                html.Button([
                                    html.I(className="fas fa-search")
                                ], className="btn btn-sm btn-outline-secondary", 
                                   title="Ver configuraciones")
                            ], className="text-center")
                        ])
                    )
                    row_num += 1
                else:
                    # Frecuencia con configuraciones
                    for config in configs:
                        ch0 = config.get('ch0', '?')
                        ch1 = config.get('ch1', '?')
                        res = config.get('res', '?')
                        
                        rows.append(
                            html.Tr([
                                html.Td(str(row_num), className="text-center"),
                                html.Td(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                       className="small text-muted"),
                                html.Td(f"{res} Ω" if res != '?' else 'N/A'),
                                html.Td(f"{freq} Hz", className="fw-bold"),
                                html.Td(f"CH0={ch0}, CH1={ch1}"),
                                html.Td([
                                    html.Span("", className="text-success")
                                ], className="text-center"),
                                html.Td([
                                    html.Button([
                                        html.I(className="fas fa-info-circle")
                                    ], className="btn btn-sm btn-outline-info me-1", 
                                       title="Ver detalles"),
                                    html.Button([
                                        html.I(className="fas fa-trash")
                                    ], className="btn btn-sm btn-outline-danger",
                                       title="Eliminar")
                                ], className="text-center")
                            ])
                        )
                        row_num += 1
            
            # Verificar si encontramos calibraciones válidas
            if not rows:
                logger.info(f"[Cal] No se encontraron calibraciones válidas después del filtrado. Total líneas recibidas: {len(calibrations_raw)}")
            else:
                logger.info(f"[Cal] '==== RETORNANDO {len(rows)} FILAS A LA TABLA ===='")
                for idx, row in enumerate(rows[:3]):  # solo primeras 3
                    logger.info(f"[Cal] Fila {idx}: {type(row)}")
            
            return rows if rows else [
                html.Tr([
                    html.Td(colSpan="7", className="text-center text-muted", children=[
                        html.I(className="fas fa-info-circle me-2"),
                        html.Div([
                            html.P("No hay calibraciones válidas almacenadas.", className="mb-1"),
                            html.Small([
                                "El dispositivo devolvió ",
                                html.Code(f"{len(calibrations_raw)} líneas", className="text-warning"),
                                " pero ninguna coincide con el formato esperado de calibración."
                            ], className="text-muted")
                        ])
                    ])
                ])
            ]
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            return [
                html.Tr([
                    html.Td(colSpan="7", className="text-center text-danger", children=[
                        html.I(className="fas fa-exclamation-circle me-2"),
                        html.Div([
                            html.P(f"Error al obtener calibraciones: {str(e)}"),
                            html.Details([
                                html.Summary("Ver detalles técnicos", className="btn btn-sm btn-link"),
                                html.Pre(error_detail, className="small mt-2 text-start")
                            ])
                        ])
                    ])
                ])
            ]


def register_calibration_page(app):
    """Registra la página de calibración"""
    register_calibration_callbacks(app)
