#!/usr/bin/env python3
"""
Dashboard Profesional EVAL-ADMX2001 - COMPLETO
Analizador de Impedancia con Control Total del Sistema
Autor: Sistema basado en documentación oficial ADMX2001
"""

import dash
from dash import dcc, html, Input, Output, State, ctx, dash_table, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from datetime import datetime
import threading
import queue
import time
import serial.tools.list_ports
import math
import io
import base64

from lib import (
    ADMX2001, DisplayMode, SweepType, SweepScale, ImpedanceRange,
    ValidationError, ConnectionError as ADMX2001ConnectionError
)

# ==================== FUNCIONES DE UTILIDAD ====================

def format_value(value, unit=""):
    """
    Formatea un valor numérico de forma inteligente:
    - Notación científica si |value| < 0.01 o |value| > 100000
    - Formato decimal normal para valores intermedios
    
    Args:
        value: Valor numérico a formatear
        unit: Unidad opcional (Ω, H, F, etc.)
    
    Returns:
        String formateado
    """
    try:
        abs_val = abs(value)
        
        # Valores muy pequeños o muy grandes: notación científica
        if abs_val < 0.01 and abs_val != 0:
            formatted = f"{value:.3e}"
        elif abs_val > 100000:
            formatted = f"{value:.3e}"
        # Valores intermedios: formato decimal
        elif abs_val < 1:
            formatted = f"{value:.4f}"
        elif abs_val < 100:
            formatted = f"{value:.2f}"
        else:
            formatted = f"{value:.1f}"
        
        return f"{formatted} {unit}" if unit else formatted
    except:
        return "---"

# ==================== CONFIGURACIÓN GLOBAL ====================

# Variables globales
device = None
measurement_thread = None
sweep_thread = None
stop_measurement = threading.Event()
stop_sweep = threading.Event()
is_connected = threading.Event()

# Colas
data_queue = queue.Queue(maxsize=100)
sweep_queue = queue.Queue(maxsize=1000)

# Datos
realtime_data = {'time': [], 'value1': [], 'value2': [], 'z_magnitude': []}
sweep_data_global = {'param': [], 'z_real': [], 'z_imag': [], 'z_magnitude': [], 'phase': []}
sweep_data_last_hash = None  # Para detectar cambios en los datos y evitar regenerar gráficos
calibration_state = {'open': False, 'short': False, 'load': False, 'committed': False}

# ==================== WORKERS ====================

def measurement_worker():
    global device, is_connected
    consecutive_errors = 0
    max_consecutive_errors = 5
    last_alert_time = 0  # Para evitar spam de alertas
    
    while not stop_measurement.is_set():
        try:
            if device and is_connected.is_set():
                # Realizar medición (mdelay ya configurado en apply_config)
                # El mdelay se observa automáticamente antes de cada medición
                val1, val2 = device.measure()
                z_mag = math.sqrt(val1**2 + val2**2)
                
                data_queue.put({
                    'timestamp': datetime.now(),
                    'value1': val1,
                    'value2': val2,
                    'z_magnitude': z_mag
                })
                consecutive_errors = 0  # Reset en éxito
                
                # Pequeño delay para no saturar la CPU, pero la estabilización 
                # real la maneja mdelay del dispositivo
                time.sleep(0.1)
            else:
                time.sleep(0.5)
        except Exception as e:
            consecutive_errors += 1
            error_msg = str(e)
            current_time = time.time()
            
            # Solo imprimir cada 3 errores para no saturar
            if consecutive_errors % 3 == 1:
                print(f"⚠️ Error medición ({consecutive_errors}): {error_msg[:60]}")
            
            # Enviar alerta después de 3 errores (y no más de 1 alerta cada 10 segundos)
            if consecutive_errors == 3 and (current_time - last_alert_time) > 10:
                data_queue.put({
                    'error': True,
                    'error_count': consecutive_errors,
                    'error_msg': error_msg,
                    'alert_type': 'warning'
                })
                last_alert_time = current_time
            
            # Si hay muchos errores consecutivos, marcar como desconectado
            if consecutive_errors >= max_consecutive_errors:
                print(f"❌ Demasiados errores ({consecutive_errors}). Posible desconexión.")
                data_queue.put({
                    'error': True,
                    'error_count': consecutive_errors,
                    'error_msg': f"No se pudo obtener medición válida después de {max_consecutive_errors} intentos. Dispositivo posiblemente desconectado.",
                    'alert_type': 'error',
                    'disconnect': True
                })
                is_connected.clear()
                consecutive_errors = 0
                last_alert_time = current_time
                time.sleep(2)
            else:
                time.sleep(1.5)  # Esperar más antes de reintentar

def sweep_worker(config):
    """Worker thread para ejecutar barridos de frecuencia."""
    global device, sweep_data_global, is_connected
    try:
        if not device or not is_connected.is_set():
            print("❌ Error sweep: Dispositivo no conectado o desconectado")
            sweep_queue.put({'error': 'Dispositivo no conectado'})
            return
        
        sweep_type = config['type']
        start = float(config['start'])
        end = float(config['end'])
        points = int(config['points'])
        scale = config['scale']
        display_mode = config.get('display_mode', 6)  # Default: R_X
        mdelay = config.get('mdelay', -1)  # -1 = auto
        tdelay = config.get('tdelay', 0)
        
        # Formatear frecuencias para display
        def format_freq(f):
            if f >= 1e6: return f"{f/1e6:.2f} MHz"
            if f >= 1e3: return f"{f/1e3:.2f} kHz"
            return f"{f:.2f} Hz"
        
        # Nombres de los modos para el log
        mode_names = {
            0: "Cs, Rs", 1: "Cs, D", 2: "Cs, Q",
            3: "Ls, Rs", 4: "Ls, D", 5: "Ls, Q",
            6: "R, X", 7: "Z, θ°", 8: "Z, θ",
            9: "Cp, Rp", 10: "Cp, D", 11: "Cp, Q",
            12: "Lp, Rp", 13: "Lp, D", 14: "Lp, Q",
            15: "G, B", 16: "Y, θ°", 17: "Y, θ"
        }
        
        decades = abs(np.log10(end) - np.log10(start)) if end > start else 0
        print(f"🔄 Iniciando barrido: {format_freq(start)} → {format_freq(end)} ({decades:.2f} déc), {points} puntos")
        print(f"📊 Modo de medición: {mode_names.get(display_mode, f'Modo {display_mode}')}")
        sweep_data_global = {'param': [], 'z_real': [], 'z_imag': [], 'z_magnitude': [], 'phase': []}
        
        # Verificar conexión y configurar modo de medición
        try:
            # Configurar el modo de medición seleccionado
            device.set_display_mode(DisplayMode(display_mode))
            
            # Configurar mdelay (measurement delay)
            if mdelay == -1:
                # Modo automático según frecuencia
                if start >= 10000:  # > 10 kHz
                    actual_mdelay = 0
                    print("⚡ mdelay = 0 ms (auto: máxima velocidad)")
                elif start >= 1000:  # 1-10 kHz
                    actual_mdelay = 1
                    print("⚡ mdelay = 1 ms (auto: balance)")
                else:  # < 1 kHz
                    actual_mdelay = 2
                    print("⚡ mdelay = 2 ms (auto: estabilidad)")
                device.set_mdelay(actual_mdelay)
            else:
                # Modo manual
                device.set_mdelay(mdelay)
                print(f"⚡ mdelay = {mdelay} ms (manual)")
            
            # Configurar tdelay (trigger delay)
            device.set_tdelay(tdelay)
            if tdelay > 0:
                print(f"⏱️ tdelay = {tdelay} ms")
                
        except Exception as e:
            error_msg = f"Error configurando display/delays: {str(e)}"
            print(f"❌ {error_msg}")
            sweep_queue.put({
                'error': error_msg,
                'alert_type': 'error',
                'alert_title': 'Error de Configuración',
                'alert_text': f'No se pudo configurar el dispositivo: {str(e)}'
            })
            is_connected.clear()
            return
        
        sweep_type_map = {
            'frequency': SweepType.FREQUENCY,
            'offset': SweepType.DC_BIAS,
            'magnitude': SweepType.MAGNITUDE
        }
        
        sweep_scale_enum = SweepScale.LOG if scale == 'log' else SweepScale.LINEAR
        
        # IMPORTANTE: configure_sweep espera frecuencias en kHz, no en Hz
        # Convertir Hz a kHz antes de enviar
        start_khz = start / 1000.0
        end_khz = end / 1000.0
        
        device.configure_sweep(
            sweep_type=sweep_type_map[sweep_type],
            start=start_khz,
            end=end_khz,
            scale=sweep_scale_enum,
            count=points
        )
        
        results = device.perform_sweep()
        
        for i, result in enumerate(results):
            if stop_sweep.is_set():
                break
            
            param_val = result['sweep_value']
            r, x = result['measurement']
            z_mag = math.sqrt(r**2 + x**2)
            phase = math.degrees(math.atan2(x, r))
            
            sweep_data_global['param'].append(param_val)
            sweep_data_global['z_real'].append(r)
            sweep_data_global['z_imag'].append(x)
            sweep_data_global['z_magnitude'].append(z_mag)
            sweep_data_global['phase'].append(phase)
            
            sweep_queue.put({
                'current': i + 1,
                'total': points,
                'param': param_val,
                'z_real': r,
                'z_imag': x,
                'z_mag': z_mag,
                'phase': phase
            })
        
    except Exception as e:
        error_detail = str(e)
        print(f"❌ Error en sweep: {error_detail}")
        
        # Determinar tipo de error para mensaje apropiado
        if 'timeout' in error_detail.lower():
            alert_title = 'Timeout en Barrido'
            alert_text = f'El barrido tardó demasiado. Intenta con menos puntos o un rango más estrecho. Error: {error_detail}'
        elif 'serial' in error_detail.lower() or 'port' in error_detail.lower():
            alert_title = 'Error de Comunicación'
            alert_text = f'Se perdió la conexión con el dispositivo. Reconecta y vuelve a intentar. Error: {error_detail}'
        else:
            alert_title = 'Error en Barrido'
            alert_text = f'Ocurrió un error inesperado: {error_detail}'
        
        sweep_queue.put({
            'error': error_detail,
            'alert_type': 'error',
            'alert_title': alert_title,
            'alert_text': alert_text
        })
        is_connected.clear()

# ==================== DASH APP ====================

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css",
        "https://cdn.jsdelivr.net/npm/sweetalert2@11/dist/sweetalert2.min.css"
    ],
    external_scripts=[
        "https://cdn.jsdelivr.net/npm/sweetalert2@11/dist/sweetalert2.all.min.js"
    ],
    suppress_callback_exceptions=True
)

app.title = "EVAL-ADMX2001 Dashboard"

# ==================== LAYOUT ====================

app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("🔬 EVAL-ADMX2001 Dashboard", className="text-primary"),
            html.P("Analizador de Impedancia - Analog Devices", className="text-muted")
        ], width=8),
        dbc.Col([
            dbc.Badge("Desconectado", id="status-badge", color="danger", className="fs-5")
        ], width=4, className="text-end")
    ], className="mb-4"),
    
    # Tabs
    dbc.Tabs([
        # TAB 1: Control
        dbc.Tab(label="Control y Medición", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Conexión"),
                        dbc.CardBody([
                            dcc.Dropdown(id="port-dropdown", placeholder="Puerto..."),
                            dbc.Button("Actualizar", id="refresh-btn", size="sm", className="mt-2 w-100"),
                            dbc.Button("Conectar", id="connect-btn", color="success", className="mt-2 w-100"),
                            dbc.Button("Desconectar", id="disconnect-btn", color="danger", className="mt-2 w-100"),
                        ])
                    ], className="mb-3"),
                    dbc.Card([
                        dbc.CardHeader("Configuración"),
                        dbc.CardBody([
                            dbc.Label("Frecuencia (Hz):"),
                            dbc.Input(id="freq-input", type="number", value=1000),
                            dbc.Label("Magnitud (Vpk):", className="mt-2"),
                            dbc.Input(id="mag-input", type="number", value=0.5),
                            dbc.Label("Offset (V):", className="mt-2"),
                            dbc.Input(id="offset-input", type="number", value=0),
                            html.Hr(),
                            dbc.Label("Modo de Medición:", className="mt-2"),
                            dcc.Dropdown(
                                id="realtime-display-mode",
                                options=[
                                    # Series Capacitance
                                    {"label": "Cs, Rs - Capacitancia Serie", "value": 0},
                                    {"label": "Cs, D - Cap. Serie + Disipación", "value": 1},
                                    {"label": "Cs, Q - Cap. Serie + Calidad", "value": 2},
                                    # Series Inductance
                                    {"label": "Ls, Rs - Inductancia Serie", "value": 3},
                                    {"label": "Ls, D - Ind. Serie + Disipación", "value": 4},
                                    {"label": "Ls, Q - Ind. Serie + Calidad", "value": 5},
                                    # Impedance
                                    {"label": "R, X - Impedancia (Default)", "value": 6},
                                    {"label": "Z, θ° - Magnitud y Fase (deg)", "value": 7},
                                    {"label": "Z, θ - Magnitud y Fase (rad)", "value": 8},
                                    # Parallel Capacitance
                                    {"label": "Cp, Rp - Capacitancia Paralelo", "value": 9},
                                    {"label": "Cp, D - Cap. Paralelo + Disipación", "value": 10},
                                    {"label": "Cp, Q - Cap. Paralelo + Calidad", "value": 11},
                                    # Parallel Inductance
                                    {"label": "Lp, Rp - Inductancia Paralelo", "value": 12},
                                    {"label": "Lp, D - Ind. Paralelo + Disipación", "value": 13},
                                    {"label": "Lp, Q - Ind. Paralelo + Calidad", "value": 14},
                                    # Admittance
                                    {"label": "G, B - Admitancia", "value": 15},
                                    {"label": "Y, θ° - Admitancia + Fase (deg)", "value": 16},
                                    {"label": "Y, θ - Admitancia + Fase (rad)", "value": 17},
                                ],
                                value=6,  # Default: R_X
                                clearable=False,
                                style={'fontSize': '0.85em'}
                            ),
                            dbc.FormText(
                                id="realtime-mode-info",
                                children="R, X: Impedancia rectangular (Ohms)",
                                className="text-info small"
                            ),
                            html.Hr(),
                            dbc.Label("⏱️ Delays (ms):", className="mt-2"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("mdelay:", style={'fontSize': '0.9em'}),
                                    dbc.Input(
                                        id="realtime-mdelay",
                                        type="number",
                                        value=1,
                                        min=0,
                                        max=10000,
                                        step=1,
                                        size="sm"
                                    ),
                                    html.Small("0-10000", className="text-muted")
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("tdelay:", style={'fontSize': '0.9em'}),
                                    dbc.Input(
                                        id="realtime-tdelay",
                                        type="number",
                                        value=0,
                                        min=0,
                                        max=10000,
                                        step=1,
                                        size="sm"
                                    ),
                                    html.Small("0-10000", className="text-muted")
                                ], width=6)
                            ]),
                            dbc.FormText([
                                html.I(className="fas fa-info-circle me-1"),
                                "mdelay: delay antes de medición. ",
                                "tdelay: delay de trigger."
                            ], className="text-info small"),
                            html.Hr(),
                            dbc.Button("Aplicar Config", id="apply-btn", color="primary", className="mt-2 w-100"),
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Medición en Tiempo Real"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        html.H6(id="value1-label", children="Valor 1"),
                                        html.H3(id="value1-display", children="---", className="text-primary"),
                                    ]),
                                ], width=6),
                                dbc.Col([
                                    html.Div([
                                        html.H6(id="value2-label", children="Valor 2"),
                                        html.H3(id="value2-display", children="---", className="text-info"),
                                    ]),
                                ], width=6),
                            ]),
                            html.Div(id="connection-status-text", className="text-muted small mb-2"),
                            dbc.ButtonGroup([
                                dbc.Button("Iniciar", id="start-btn", color="success"),
                                dbc.Button("Detener", id="stop-btn", color="danger"),
                            ], className="mb-3"),
                            dcc.Graph(id="realtime-graph")
                        ])
                    ])
                ], width=9)
            ])
        ]),
        
        # TAB 2: Sweeps
        dbc.Tab(label="Barridos", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Config Barrido"),
                        dbc.CardBody([
                            dbc.Label("Inicio (Hz):"),
                            dcc.Input(id="sweep-start", type="number", value=100, min=0.2, max=10000000,
                                     style={'width': '100%', 'padding': '0.375rem 0.75rem', 
                                            'border': '1px solid #ced4da', 'border-radius': '0.25rem'}),
                            html.Small("Rango: 0.2 Hz - 10 MHz", className="text-muted"),
                            dbc.Label("Fin (Hz):", className="mt-2"),
                            dcc.Input(id="sweep-end", type="number", value=100000, min=0.2, max=10000000,
                                     style={'width': '100%', 'padding': '0.375rem 0.75rem', 
                                            'border': '1px solid #ced4da', 'border-radius': '0.25rem'}),
                            html.Small("Rango: 0.2 Hz - 10 MHz", className="text-muted"),
                            dbc.Label("Puntos:", className="mt-2"),
                            html.Div([
                                dcc.Input(
                                    id="sweep-points", 
                                    type="number", 
                                    value=50, 
                                    min=2, 
                                    max=1000,
                                    step=1,
                                    style={'width': '100%', 'padding': '0.375rem 0.75rem', 
                                           'border': '1px solid #ced4da', 'border-radius': '0.25rem'}
                                ),
                                dbc.FormText([
                                    html.Span(id="points-range-text", className="text-muted"),
                                    html.Br(),
                                    html.Small("⚡ Óptimo: 10-20 puntos/década. Max hardware: 1000 puntos", className="text-info"),
                                    html.Br(),
                                    html.Small("💡 Menos puntos = más rápido. Más puntos = más resolución", className="text-warning")
                                ])
                            ]),
                            dbc.Label("Escala:", className="mt-2"),
                            dbc.RadioItems(
                                id="sweep-scale",
                                options=[
                                    {"label": " Logarítmica (recomendado)", "value": "log"},
                                    {"label": " Lineal", "value": "linear"}
                                ],
                                value="log",
                                inline=False
                            ),
                            dbc.Label("Modo de Medición:", className="mt-3"),
                            dcc.Dropdown(
                                id="display-mode",
                                options=[
                                    # Series Capacitance
                                    {"label": "Cs, Rs - Series Capacitance & Resistance", "value": 0},
                                    {"label": "Cs, D - Series Capacitance & Dissipation", "value": 1},
                                    {"label": "Cs, Q - Series Capacitance & Quality Factor", "value": 2},
                                    # Series Inductance
                                    {"label": "Ls, Rs - Series Inductance & Resistance", "value": 3},
                                    {"label": "Ls, D - Series Inductance & Dissipation", "value": 4},
                                    {"label": "Ls, Q - Series Inductance & Quality Factor", "value": 5},
                                    # Impedance (default)
                                    {"label": "R, X - Impedance Rectangular (Default)", "value": 6},
                                    {"label": "Z, θ° - Impedance Magnitude & Phase (deg)", "value": 7},
                                    {"label": "Z, θ - Impedance Magnitude & Phase (rad)", "value": 8},
                                    # Parallel Capacitance
                                    {"label": "Cp, Rp - Parallel Capacitance & Resistance", "value": 9},
                                    {"label": "Cp, D - Parallel Capacitance & Dissipation", "value": 10},
                                    {"label": "Cp, Q - Parallel Capacitance & Quality Factor", "value": 11},
                                    # Parallel Inductance
                                    {"label": "Lp, Rp - Parallel Inductance & Resistance", "value": 12},
                                    {"label": "Lp, D - Parallel Inductance & Dissipation", "value": 13},
                                    {"label": "Lp, Q - Parallel Inductance & Quality Factor", "value": 14},
                                    # Admittance
                                    {"label": "G, B - Admittance Rectangular", "value": 15},
                                    {"label": "Y, θ° - Admittance Magnitude & Phase (deg)", "value": 16},
                                    {"label": "Y, θ - Admittance Magnitude & Phase (rad)", "value": 17},
                                ],
                                value=6,  # Default: R_X
                                clearable=False,
                                style={'fontSize': '0.9em'}
                            ),
                            dbc.FormText([
                                html.I(className="fas fa-info-circle me-1"),
                                html.Span(id="display-mode-info", children="Modo R, X: Impedancia en coordenadas rectangulares (Ohms)")
                            ], className="text-info small mt-1"),
                            html.Hr(),
                            dbc.Label("⏱️ Delays (ms):", className="mt-2"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("mdelay:", style={'fontSize': '0.9em'}),
                                    dbc.Input(
                                        id="sweep-mdelay",
                                        type="number",
                                        value=-1,
                                        min=-1,
                                        max=10000,
                                        step=1,
                                        size="sm"
                                    ),
                                    html.Small("-1 = auto", className="text-muted")
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("tdelay:", style={'fontSize': '0.9em'}),
                                    dbc.Input(
                                        id="sweep-tdelay",
                                        type="number",
                                        value=0,
                                        min=0,
                                        max=10000,
                                        step=1,
                                        size="sm"
                                    ),
                                    html.Small("0-10000", className="text-muted")
                                ], width=6)
                            ]),
                            dbc.FormText([
                                html.I(className="fas fa-info-circle me-1"),
                                "mdelay: delay antes de cada medición. ",
                                "tdelay: delay de trigger. ",
                                "Auto (-1) configura según frecuencia."
                            ], className="text-info small"),
                            html.Hr(),
                            dbc.Button(
                                [html.I(className="fas fa-play me-2"), "Iniciar Barrido"], 
                                id="sweep-btn", 
                                color="primary", 
                                className="w-100 mb-2",
                                size="lg"
                            ),
                            dbc.Button(
                                [html.I(className="fas fa-stop me-2"), "Detener"], 
                                id="stop-sweep-btn", 
                                color="danger", 
                                className="w-100 mb-3",
                                size="sm",
                                disabled=True
                            ),
                            html.Div([
                                dbc.Progress(
                                    id="sweep-progress-bar",
                                    value=0,
                                    striped=True,
                                    animated=True,
                                    className="mb-2",
                                    style={'height': '25px'}
                                ),
                                html.Div(id="sweep-progress-text", className="text-center small"),
                            ], id="sweep-progress-container", style={'display': 'none'}),
                            html.Div(id="sweep-error-text", className="text-danger text-center small mt-2"),
                            html.Div(id="sweep-success-text", className="text-success text-center small mt-2"),
                            html.Hr(),
                            dbc.Button(
                                [html.I(className="fas fa-download me-2"), "Exportar CSV"], 
                                id="export-csv-btn", 
                                color="success", 
                                className="w-100 mb-2",
                                size="sm",
                                outline=True
                            ),
                            dcc.Download(id="download-csv"),
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    html.Div([
                        dcc.Graph(
                            id="bode-plot",
                            style={'height': '650px', 'width': '100%'},
                            config={
                                'responsive': True,
                                'displayModeBar': True,
                                'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],
                                'modeBarButtonsToRemove': [],
                                'displaylogo': False,
                                'toImageButtonOptions': {
                                    'format': 'png',
                                    'filename': 'bode_plot',
                                    'height': 800,
                                    'width': 1200,
                                    'scale': 2
                                }
                            }
                        )
                    ], style={'marginBottom': '20px'}),
                    html.Div([
                        dcc.Graph(
                            id="nyquist-plot",
                            style={'height': '450px', 'width': '100%'},
                            config={
                                'responsive': True,
                                'displayModeBar': True,
                                'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],
                                'modeBarButtonsToRemove': [],
                                'displaylogo': False,
                                'toImageButtonOptions': {
                                    'format': 'png',
                                    'filename': 'nyquist_plot',
                                    'height': 600,
                                    'width': 800,
                                    'scale': 2
                                }
                            }
                        )
                    ])
                ], width=9)
            ])
        ]),
    ]),
    
    # Modal de progreso
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle([
            html.I(className="fas fa-sync fa-spin me-2"),
            "Realizando Barrido de Frecuencia..."
        ])),
        dbc.ModalBody([
            html.Div([
                html.H5("Analizando impedancia en múltiples frecuencias", className="text-center mb-3"),
                dbc.Progress(
                    id="modal-progress-bar",
                    value=0,
                    striped=True,
                    animated=True,
                    className="mb-3",
                    style={'height': '30px'}
                ),
                html.Div(id="modal-progress-text", className="text-center"),
                html.Hr(),
                html.Div([
                    html.Small([
                        html.I(className="fas fa-info-circle me-1"),
                        "El barrido puede tardar varios minutos dependiendo del número de puntos."
                    ], className="text-muted")
                ], className="text-center")
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button(
                [html.I(className="fas fa-times me-2"), "Cancelar"],
                id="modal-cancel-btn",
                color="secondary",
                size="sm"
            )
        ])
    ], id="sweep-modal", is_open=False, backdrop="static", keyboard=False, centered=True, size="lg"),
    
    # Intervalos
    dcc.Interval(id='interval-fast', interval=300, n_intervals=0),
    dcc.Interval(id='interval-slow', interval=1000, n_intervals=0),
    dcc.Interval(id='interval-sweep-progress', interval=500, n_intervals=0),
    
    # Store
    dcc.Store(id='connection-state', data={'connected': False}),
    dcc.Store(id='sweep-data-store', data={'param': [], 'z_real': [], 'z_imag': [], 'z_mag': [], 'phase': []}),
    dcc.Store(id='sweep-running', data={'running': False, 'total': 0}),
    
    # Script para SweetAlert
    html.Script(id='sweetalert-script', children=''),
    
], fluid=True)

# ==================== CALLBACKS ====================

# Callback para actualizar límites dinámicos de puntos
@app.callback(
    [Output('sweep-points', 'min'),
     Output('sweep-points', 'max'),
     Output('points-range-text', 'children')],
    [Input('sweep-start', 'value'),
     Input('sweep-end', 'value')],
    prevent_initial_call=False
)
def update_points_limits(start, end):
    """Actualiza límites de puntos basado en el rango de frecuencias.
    
    IMPORTANTE: El hardware ADMX2001 tiene límites que dependen del ANCHO DE BANDA.
    A MENOR ancho de banda (menos décadas) → MÁS puntos posibles.
    
    Límites realistas basados en observaciones empíricas del usuario:
    "De 1 al MAX solo deja 255 puntos pero disminuyendo el ancho aumenta"
    """
    if start is None or end is None or start >= end:
        return 2, 1000, "Rango: 2-1000 puntos"
    
    # Calcular décadas logarítmicas
    decades = abs(np.log10(end) - np.log10(start))
    
    # Límites realistas según ancho de banda
    # A MENOR ancho → MÁS puntos
    if decades <= 0.5:
        # Rango muy estrecho (< 0.5 década) - ej: 5-10 MHz
        min_points = 10
        max_points = 1000
        recommended = f"Ultra estrecho ({decades:.1f} déc)"
        time_est = "< 3 min"
    elif decades <= 1.0:
        # Rango estrecho (0.5-1.0 década) - ej: 1-10 MHz
        min_points = 10
        max_points = 500
        recommended = f"Estrecho ({decades:.1f} déc)"
        time_est = "< 2 min"
    elif decades <= 2.0:
        # Rango mediano (1-2 décadas) - ej: 100kHz-10MHz
        min_points = 10
        max_points = 300
        recommended = f"Mediano ({decades:.1f} déc)"
        time_est = "< 2 min"
    elif decades <= 3.0:
        # Rango grande (2-3 décadas) - ej: 10kHz-10MHz
        min_points = 15
        max_points = 255
        recommended = f"Grande ({decades:.1f} déc)"
        time_est = "< 3 min"
    elif decades <= 4.0:
        # Rango muy grande (3-4 décadas) - ej: 1kHz-10MHz
        min_points = 20
        max_points = 200
        recommended = f"Muy grande ({decades:.1f} déc)"
        time_est = "< 3 min"
    else:
        # Rango completo (> 4 décadas) - ej: 1Hz-10MHz
        # Límite conservador: 100 puntos máximo
        min_points = 20
        max_points = 100
        recommended = f"Rango completo ({decades:.1f} déc)"
        time_est = "2-5 min"
    
    info_text = f"Rango: {min_points}-{max_points} pts. {recommended}. Est: {time_est}"
    return min_points, max_points, info_text

@app.callback(
    Output('display-mode-info', 'children'),
    Input('display-mode', 'value'),
    prevent_initial_call=False
)
def update_display_mode_info(mode):
    """Actualiza la información del modo de medición seleccionado."""
    mode_info = {
        0: "Cs, Rs: Capacitancia e impedancia serie (Farads, Ohms)",
        1: "Cs, D: Capacitancia serie y factor de disipación (Farads, Adim.)",
        2: "Cs, Q: Capacitancia serie y factor de calidad (Farads, Adim.)",
        3: "Ls, Rs: Inductancia e impedancia serie (Henries, Ohms)",
        4: "Ls, D: Inductancia serie y factor de disipación (Henries, Adim.)",
        5: "Ls, Q: Inductancia serie y factor de calidad (Henries, Adim.)",
        6: "R, X: Impedancia en coordenadas rectangulares (Ohms, Ohms)",
        7: "Z, θ°: Impedancia en magnitud y fase en grados (Ohms, Grados)",
        8: "Z, θ: Impedancia en magnitud y fase en radianes (Ohms, Radianes)",
        9: "Cp, Rp: Capacitancia e impedancia paralelo (Farads, Ohms)",
        10: "Cp, D: Capacitancia paralelo y factor de disipación (Farads, Adim.)",
        11: "Cp, Q: Capacitancia paralelo y factor de calidad (Farads, Adim.)",
        12: "Lp, Rp: Inductancia e impedancia paralelo (Henries, Ohms)",
        13: "Lp, D: Inductancia paralelo y factor de disipación (Henries, Adim.)",
        14: "Lp, Q: Inductancia paralelo y factor de calidad (Henries, Adim.)",
        15: "G, B: Admitancia en coordenadas rectangulares (Siemens, Siemens)",
        16: "Y, θ°: Admitancia en magnitud y fase en grados (Siemens, Grados)",
        17: "Y, θ: Admitancia en magnitud y fase en radianes (Siemens, Radianes)",
    }
    return mode_info.get(mode, "Modo desconocido")

@app.callback(
    Output('realtime-mode-info', 'children'),
    Input('realtime-display-mode', 'value'),
    prevent_initial_call=False
)
def update_realtime_mode_info(mode):
    """Actualiza la información del modo de medición en tiempo real."""
    mode_info = {
        0: "Cs, Rs: Capacitancia e impedancia serie",
        1: "Cs, D: Capacitancia serie y disipación",
        2: "Cs, Q: Capacitancia serie y calidad",
        3: "Ls, Rs: Inductancia e impedancia serie",
        4: "Ls, D: Inductancia serie y disipación",
        5: "Ls, Q: Inductancia serie y calidad",
        6: "R, X: Impedancia rectangular (Ohms)",
        7: "Z, θ°: Magnitud y fase (grados)",
        8: "Z, θ: Magnitud y fase (radianes)",
        9: "Cp, Rp: Capacitancia e impedancia paralelo",
        10: "Cp, D: Capacitancia paralelo y disipación",
        11: "Cp, Q: Capacitancia paralelo y calidad",
        12: "Lp, Rp: Inductancia e impedancia paralelo",
        13: "Lp, D: Inductancia paralelo y disipación",
        14: "Lp, Q: Inductancia paralelo y calidad",
        15: "G, B: Admitancia rectangular",
        16: "Y, θ°: Admitancia y fase (grados)",
        17: "Y, θ: Admitancia y fase (radianes)",
    }
    return mode_info.get(mode, "Modo desconocido")

@app.callback(
    [Output('value1-label', 'children'),
     Output('value2-label', 'children')],
    Input('realtime-display-mode', 'value'),
    prevent_initial_call=False
)
def update_value_labels(mode):
    """Actualiza las etiquetas de los valores según el modo de medición."""
    labels = {
        0: ("Cs (Capacitancia)", "Rs (Resistencia)"),
        1: ("Cs (Capacitancia)", "D (Disipación)"),
        2: ("Cs (Capacitancia)", "Q (Calidad)"),
        3: ("Ls (Inductancia)", "Rs (Resistencia)"),
        4: ("Ls (Inductancia)", "D (Disipación)"),
        5: ("Ls (Inductancia)", "Q (Calidad)"),
        6: ("R (Resistencia)", "X (Reactancia)"),
        7: ("Z (Magnitud)", "θ (Fase °)"),
        8: ("Z (Magnitud)", "θ (Fase rad)"),
        9: ("Cp (Capacitancia)", "Rp (Resistencia)"),
        10: ("Cp (Capacitancia)", "D (Disipación)"),
        11: ("Cp (Capacitancia)", "Q (Calidad)"),
        12: ("Lp (Inductancia)", "Rp (Resistencia)"),
        13: ("Lp (Inductancia)", "D (Disipación)"),
        14: ("Lp (Inductancia)", "Q (Calidad)"),
        15: ("G (Conductancia)", "B (Susceptancia)"),
        16: ("Y (Admitancia)", "θ (Fase °)"),
        17: ("Y (Admitancia)", "θ (Fase rad)"),
    }
    return labels.get(mode, ("Valor 1", "Valor 2"))

def get_units_for_mode(mode):
    """Retorna las unidades apropiadas para cada modo de medición."""
    units = {
        0: ("F", "Ω"),      # Cs, Rs
        1: ("F", ""),        # Cs, D (sin unidad)
        2: ("F", ""),        # Cs, Q (sin unidad)
        3: ("H", "Ω"),      # Ls, Rs
        4: ("H", ""),        # Ls, D (sin unidad)
        5: ("H", ""),        # Ls, Q (sin unidad)
        6: ("Ω", "Ω"),      # R, X
        7: ("Ω", "°"),      # Z, θ°
        8: ("Ω", "rad"),    # Z, θ (radianes)
        9: ("F", "Ω"),      # Cp, Rp
        10: ("F", ""),       # Cp, D (sin unidad)
        11: ("F", ""),       # Cp, Q (sin unidad)
        12: ("H", "Ω"),     # Lp, Rp
        13: ("H", ""),       # Lp, D (sin unidad)
        14: ("H", ""),       # Lp, Q (sin unidad)
        15: ("S", "S"),     # G, B (Siemens)
        16: ("S", "°"),     # Y, θ°
        17: ("S", "rad"),   # Y, θ (radianes)
    }
    return units.get(mode, ("", ""))

@app.callback(
    Output('port-dropdown', 'options'),
    Input('refresh-btn', 'n_clicks'),
    prevent_initial_call=False
)
def refresh_ports(n):
    ports = serial.tools.list_ports.comports()
    return [{'label': f"{p.device} - {p.description}", 'value': p.device} for p in ports]

@app.callback(
    [Output('status-badge', 'children'),
     Output('status-badge', 'color'),
     Output('connection-state', 'data')],
    [Input('connect-btn', 'n_clicks'),
     Input('disconnect-btn', 'n_clicks')],
    [State('port-dropdown', 'value')],
    prevent_initial_call=True
)
def handle_connection(connect_n, disconnect_n, port):
    global device, is_connected
    
    triggered = ctx.triggered_id
    
    if triggered == 'connect-btn' and port:
        try:
            device = ADMX2001(port, timeout=5.0)  # Timeout aumentado
            is_connected.set()
            
            # Configurar delays iniciales del dispositivo
            # mdelay: 1ms por defecto (se puede ajustar desde la UI)
            # tdelay: 0ms por defecto (sin triggers externos)
            device.set_mdelay(1)
            device.set_tdelay(0)
            
            return "Conectado", "success", {'connected': True}
        except Exception as e:
            return f"Error: {str(e)[:20]}", "danger", {'connected': False}
    elif triggered == 'disconnect-btn':
        if device:
            device.close()
        is_connected.clear()
        return "Desconectado", "danger", {'connected': False}
    
    raise PreventUpdate

@app.callback(
    Output('apply-btn', 'children'),
    Input('apply-btn', 'n_clicks'),
    [State('freq-input', 'value'),
     State('mag-input', 'value'),
     State('offset-input', 'value'),
     State('realtime-display-mode', 'value'),
     State('realtime-mdelay', 'value'),
     State('realtime-tdelay', 'value')],
    prevent_initial_call=True
)
def apply_config(n, freq, mag, offset, display_mode, mdelay, tdelay):
    global device
    if device and is_connected.is_set():
        try:
            # Aplicar configuraciones
            device.set_frequency(freq)
            device.set_magnitude(mag)
            device.set_offset(offset)
            
            # Aplicar el modo de medición seleccionado
            device.set_display_mode(DisplayMode(display_mode if display_mode is not None else 6))
            
            # Configurar delays del dispositivo
            # mdelay: delay de medición (0-10000 ms)
            if mdelay is not None and 0 <= mdelay <= 10000:
                device.set_mdelay(mdelay)
            else:
                device.set_mdelay(1)  # Default 1ms
            
            # tdelay: delay de trigger (0-10000 ms)
            if tdelay is not None and 0 <= tdelay <= 10000:
                device.set_tdelay(tdelay)
            else:
                device.set_tdelay(0)  # Default 0ms
            
            # Nombres de los modos para feedback
            mode_names = {
                0: "Cs,Rs", 1: "Cs,D", 2: "Cs,Q",
                3: "Ls,Rs", 4: "Ls,D", 5: "Ls,Q",
                6: "R,X", 7: "Z,θ°", 8: "Z,θ",
                9: "Cp,Rp", 10: "Cp,D", 11: "Cp,Q",
                12: "Lp,Rp", 13: "Lp,D", 14: "Lp,Q",
                15: "G,B", 16: "Y,θ°", 17: "Y,θ"
            }
            mode_name = mode_names.get(display_mode, "R,X")
            return f"✓ Aplicado ({mode_name}, mdelay={mdelay}ms, tdelay={tdelay}ms)"
        except Exception as e:
            return f"Error: {str(e)[:20]}"
    return "❌ No conectado"


@app.callback(
    [Output('value1-display', 'children'),
     Output('value2-display', 'children'),
     Output('connection-status-text', 'children'),
     Output('realtime-graph', 'figure'),
     Output('sweetalert-script', 'children', allow_duplicate=True)],
    Input('interval-fast', 'n_intervals'),
    State('realtime-display-mode', 'value'),
    prevent_initial_call=True
)
def update_realtime(n, display_mode):
    global realtime_data, is_connected
    
    # Obtener unidades según el modo actual
    unit1, unit2 = get_units_for_mode(display_mode if display_mode is not None else 6)
    
    # Procesar cola
    new_data_count = 0
    error_alert = ""
    
    while not data_queue.empty():
        try:
            data = data_queue.get_nowait()
            
            # Verificar si es un error
            if data.get('error', False):
                error_count = data.get('error_count', 0)
                error_msg = data.get('error_msg', 'Error desconocido')
                alert_type = data.get('alert_type', 'error')
                
                if alert_type == 'warning':
                    error_alert = f"""
                        Swal.fire({{
                            icon: 'warning',
                            title: 'Errores de Medición',
                            html: '<b>{error_count} errores consecutivos</b><br><br>{error_msg[:80]}',
                            confirmButtonColor: '#ffc107',
                            timer: 5000,
                            timerProgressBar: true
                        }});
                    """
                else:  # error
                    error_alert = f"""
                        Swal.fire({{
                            icon: 'error',
                            title: 'Error Crítico de Medición',
                            html: '<b>Medición interrumpida</b><br><br>{error_msg}<br><br><small>Por favor verifica la conexión del dispositivo</small>',
                            confirmButtonColor: '#dc3545'
                        }});
                    """
                
                # Si hay orden de desconexión, actualizar estado
                if data.get('disconnect', False):
                    is_connected.clear()
            else:
                # Datos normales
                realtime_data['time'].append(data['timestamp'])
                realtime_data['value1'].append(data['value1'])
                realtime_data['value2'].append(data['value2'])
                new_data_count += 1
                
                # Mantener últimos 50
                if len(realtime_data['time']) > 50:
                    for key in realtime_data:
                        realtime_data[key] = realtime_data[key][-50:]
        except:
            break
    
    # Crear gráfico
    fig = go.Figure()
    if realtime_data['time']:
        fig.add_trace(go.Scatter(
            x=realtime_data['time'],
            y=realtime_data['value1'],
            name='R (Ω)',
            mode='lines+markers',
            line=dict(color='#0066cc')
        ))
        fig.add_trace(go.Scatter(
            x=realtime_data['time'],
            y=realtime_data['value2'],
            name='X (Ω)',
            mode='lines+markers',
            line=dict(color='#17a2b8')
        ))
    
    fig.update_layout(title='Impedancia en Tiempo Real', height=300, hovermode='x unified')
    
    # Textos con formato inteligente y unidades según el modo
    val1_text = format_value(realtime_data['value1'][-1], unit1) if realtime_data['value1'] else "---"
    val2_text = format_value(realtime_data['value2'][-1], unit2) if realtime_data['value2'] else "---"
    
    # Estado de conexión
    if is_connected.is_set() and new_data_count > 0:
        status_text = f"✅ Recibiendo datos ({new_data_count} nuevos)"
    elif is_connected.is_set():
        status_text = "⏸️ Conectado, esperando datos..."
    else:
        status_text = "❌ Sin conexión activa"
    
    return val1_text, val2_text, status_text, fig, error_alert

@app.callback(
    Output('start-btn', 'disabled'),
    [Input('start-btn', 'n_clicks'),
     Input('stop-btn', 'n_clicks')],
    prevent_initial_call=True
)
def control_measurement(start_n, stop_n):
    global measurement_thread, stop_measurement
    
    triggered = ctx.triggered_id
    
    if triggered == 'start-btn':
        stop_measurement.clear()
        if not measurement_thread or not measurement_thread.is_alive():
            measurement_thread = threading.Thread(target=measurement_worker, daemon=True)
            measurement_thread.start()
        return True
    elif triggered == 'stop-btn':
        stop_measurement.set()
        return False
    
    return False

@app.callback(
    [Output('bode-plot', 'figure'),
     Output('nyquist-plot', 'figure'),
     Output('sweep-progress-text', 'children'),
     Output('sweep-error-text', 'children'),
     Output('sweep-success-text', 'children'),
     Output('sweep-data-store', 'data'),
     Output('sweep-modal', 'is_open'),
     Output('modal-progress-bar', 'value'),
     Output('modal-progress-text', 'children'),
     Output('sweep-progress-bar', 'value'),
     Output('sweep-progress-container', 'style'),
     Output('sweep-btn', 'disabled'),
     Output('stop-sweep-btn', 'disabled'),
     Output('sweep-running', 'data'),
     Output('sweetalert-script', 'children')],
    [Input('interval-sweep-progress', 'n_intervals'),
     Input('sweep-btn', 'n_clicks'),
     Input('stop-sweep-btn', 'n_clicks'),
     Input('modal-cancel-btn', 'n_clicks')],
    [State('sweep-start', 'value'),
     State('sweep-end', 'value'),
     State('sweep-points', 'value'),
     State('sweep-scale', 'value'),
     State('display-mode', 'value'),
     State('sweep-mdelay', 'value'),
     State('sweep-tdelay', 'value'),
     State('sweep-data-store', 'data'),
     State('sweep-running', 'data'),
     State('sweep-modal', 'is_open')],
    prevent_initial_call=False
)
def update_sweep(n_intervals, sweep_n, stop_n, cancel_n, start, end, points, scale, 
                 display_mode, mdelay, tdelay, stored_data, sweep_state, modal_open):
    global sweep_thread, sweep_data_global, stop_sweep, sweep_data_last_hash
    
    triggered = ctx.triggered_id
    error_msg = ""
    success_msg = ""
    sweetalert_script = ""
    
    # Estado actual del sweep
    is_running = sweep_state.get('running', False)
    total_points = sweep_state.get('total', 0)
    
    # Crear un hash de los datos actuales para detectar cambios
    current_data_hash = (
        len(sweep_data_global['param']),
        len(sweep_data_global['z_real']),
        len(sweep_data_global['z_imag']),
        len(sweep_data_global['z_magnitude']),
        len(sweep_data_global['phase'])
    )
    
    # Verificar si los datos han cambiado
    data_changed = (sweep_data_last_hash != current_data_hash)
    
    # Procesar cola de sweep y obtener progreso
    current_point = 0
    error_from_sweep = None
    while not sweep_queue.empty():
        try:
            data = sweep_queue.get_nowait()
            if 'error' in data:
                # Error detectado desde el sweep worker
                error_from_sweep = data
            else:
                current_point = data.get('current', 0)
                total_points = data.get('total', total_points)
        except:
            break
    
    # Si hay error desde el sweep, mostrarlo inmediatamente
    if error_from_sweep:
        sweetalert_script = f"""
            Swal.fire({{
                icon: '{error_from_sweep.get('alert_type', 'error')}',
                title: '{error_from_sweep.get('alert_title', 'Error')}',
                text: '{error_from_sweep.get('alert_text', error_from_sweep.get('error', 'Error desconocido'))}',
                confirmButtonColor: '#0d6efd'
            }});
        """
        return (go.Figure(), go.Figure(), "", "", "", stored_data,
                False, 0, "", 0, {'display': 'none'}, False, True,
                {'running': False, 'total': 0}, sweetalert_script)
    
    # Calcular progreso
    if total_points > 0 and current_point > 0:
        progress_percent = int((current_point / total_points) * 100)
    else:
        progress_percent = 0
    
    # Si se clickeó el botón de iniciar sweep
    if triggered == 'sweep-btn':
        # Debug ANTES de conversión
        print(f"DEBUG RAW - Valores crudos: start={start} (type={type(start).__name__}), end={end} (type={type(end).__name__}), points={points} (type={type(points).__name__})")
        
        # Convertir valores a números y manejar None
        try:
            start = float(start) if start is not None and start != '' else None
            end = float(end) if end is not None and end != '' else None
            points = int(points) if points is not None and points != '' else None
        except (ValueError, TypeError) as e:
            print(f"ERROR en conversión: {e}")
            pass
        
        # Debug: Imprimir valores recibidos
        print(f"DEBUG CONVERTED - Valores convertidos: start={start}, end={end}, points={points}")
        
        # Validaciones
        if start is None or end is None or points is None:
            print(f"WARNING - Valores None detectados: start={start}, end={end}, points={points}")
            
            # Identificar qué campo falta
            missing_fields = []
            if start is None:
                missing_fields.append("Inicio")
            if end is None:
                missing_fields.append("Fin")
            if points is None:
                missing_fields.append("Puntos")
            
            missing_text = ", ".join(missing_fields)
            
            sweetalert_script = f"""
                Swal.fire({{
                    icon: 'warning',
                    title: 'Datos Incompletos',
                    html: 'Por favor complete: <b>{missing_text}</b><br><br><small>Valores actuales: start={start}, end={end}, points={points}</small>',
                    confirmButtonColor: '#0d6efd'
                }});
            """
            return (go.Figure(), go.Figure(), "", error_msg, "", stored_data, 
                    False, 0, "", 0, {'display': 'none'}, False, True, 
                    {'running': False, 'total': 0}, sweetalert_script)
        
        elif start < 0.2 or start > 10000000:
            sweetalert_script = f"""
                Swal.fire({{
                    icon: 'error',
                    title: 'Frecuencia Inválida',
                    text: 'Inicio fuera de rango (0.2 Hz - 10 MHz): {start} Hz',
                    confirmButtonColor: '#0d6efd'
                }});
            """
            return (go.Figure(), go.Figure(), "", error_msg, "", stored_data,
                    False, 0, "", 0, {'display': 'none'}, False, True,
                    {'running': False, 'total': 0}, sweetalert_script)
        
        elif end < 0.2 or end > 10000000:
            sweetalert_script = f"""
                Swal.fire({{
                    icon: 'error',
                    title: 'Frecuencia Inválida',
                    text: 'Fin fuera de rango (0.2 Hz - 10 MHz): {end} Hz',
                    confirmButtonColor: '#0d6efd'
                }});
            """
            return (go.Figure(), go.Figure(), "", error_msg, "", stored_data,
                    False, 0, "", 0, {'display': 'none'}, False, True,
                    {'running': False, 'total': 0}, sweetalert_script)
        
        elif start >= end:
            sweetalert_script = """
                Swal.fire({
                    icon: 'warning',
                    title: 'Rango Inválido',
                    text: 'La frecuencia inicial debe ser menor que la final',
                    confirmButtonColor: '#0d6efd'
                });
            """
            return (go.Figure(), go.Figure(), "", error_msg, "", stored_data,
                    False, 0, "", 0, {'display': 'none'}, False, True,
                    {'running': False, 'total': 0}, sweetalert_script)
        
        # Validar puntos según ancho de banda
        decades = abs(np.log10(end) - np.log10(start)) if end > start else 0
        # Determinar límite máximo realista según ancho de banda
        if decades < 0.5:
            max_allowed = 1000
        elif decades < 1.0:
            max_allowed = 500
        elif decades < 2.0:
            max_allowed = 300
        elif decades < 3.0:
            max_allowed = 255
        elif decades < 4.0:
            max_allowed = 200
        else:
            max_allowed = 100
        
        if points < 2 or points > max_allowed:
            sweetalert_script = f"""
                Swal.fire({{
                    icon: 'error',
                    title: 'Número de Puntos Inválido',
                    text: 'Para este rango ({decades:.1f} décadas), máximo {max_allowed} puntos (recibido: {points}). A menor ancho → más puntos.',
                    confirmButtonColor: '#0d6efd'
                }});
            """
            return (go.Figure(), go.Figure(), "", error_msg, "", stored_data,
                    False, 0, "", 0, {'display': 'none'}, False, True,
                    {'running': False, 'total': 0}, sweetalert_script)
        
        elif not device or not is_connected.is_set():
            sweetalert_script = """
                Swal.fire({
                    icon: 'error',
                    title: 'Dispositivo No Conectado',
                    text: 'Por favor conecte el dispositivo antes de iniciar el barrido',
                    confirmButtonColor: '#0d6efd'
                });
            """
            return (go.Figure(), go.Figure(), "", error_msg, "", stored_data,
                    False, 0, "", 0, {'display': 'none'}, False, True,
                    {'running': False, 'total': 0}, sweetalert_script)
        
        # Todo válido - iniciar sweep
        else:
            stop_sweep.clear()
            config = {
                'type': 'frequency',
                'start': start,
                'end': end,
                'points': points,
                'scale': scale,
                'display_mode': display_mode if display_mode is not None else 6,  # Default: R_X
                'mdelay': mdelay if mdelay is not None else -1,
                'tdelay': tdelay if tdelay is not None else 0
            }
            if not sweep_thread or not sweep_thread.is_alive():
                sweep_thread = threading.Thread(target=sweep_worker, args=(config,), daemon=True)
                sweep_thread.start()
                
                sweetalert_script = """
                    Swal.fire({
                        icon: 'success',
                        title: 'Barrido Iniciado',
                        text: 'Analizando impedancia en múltiples frecuencias...',
                        timer: 2000,
                        showConfirmButton: false
                    });
                """
                
                is_running = True
                total_points = points
    
    # Si se clickeó detener o cancelar
    elif triggered in ['stop-sweep-btn', 'modal-cancel-btn']:
        stop_sweep.set()
        is_running = False
        
        sweetalert_script = """
            Swal.fire({
                icon: 'info',
                title: 'Barrido Detenido',
                text: 'El barrido fue cancelado por el usuario',
                confirmButtonColor: '#0d6efd'
            });
        """
    
    # Verificar si el sweep terminó
    if is_running and sweep_thread and not sweep_thread.is_alive():
        is_running = False
        if len(sweep_data_global['param']) == total_points:
            success_msg = f"✓ Barrido completado: {len(sweep_data_global['param'])} puntos"
            sweetalert_script = f"""
                Swal.fire({{
                    icon: 'success',
                    title: '¡Barrido Completado!',
                    text: 'Se obtuvieron {len(sweep_data_global['param'])} puntos de datos',
                    confirmButtonColor: '#0d6efd'
                }});
            """
        else:
            error_msg = f"⚠ Barrido incompleto: {len(sweep_data_global['param'])}/{total_points} puntos"
    
    # Si el trigger es el intervalo y los datos NO han cambiado, 
    # usar no_update para las figuras para preservar el zoom
    if triggered == 'interval-sweep-progress' and not data_changed:
        # Actualizar el hash para la próxima vez
        sweep_data_last_hash = current_data_hash
        
        # Calcular valores de progreso
        if total_points > 0 and current_point > 0:
            progress_percent = int((current_point / total_points) * 100)
        else:
            progress_percent = 0
        
        # Textos de progreso
        if is_running and current_point > 0:
            progress_text = f"📊 Punto {current_point}/{total_points}"
            modal_text = f"Analizando punto {current_point} de {total_points}"
        elif is_running:
            progress_text = "🔄 Iniciando barrido..."
            modal_text = "Preparando análisis..."
        else:
            progress_text = ""
            modal_text = ""
        
        # Configuración del modal y controles
        modal_is_open = is_running
        progress_style = {'display': 'block'} if is_running else {'display': 'none'}
        sweep_btn_disabled = is_running
        stop_btn_disabled = not is_running
        
        # Retornar con no_update para las figuras (preservar zoom)
        return (no_update, no_update, progress_text, error_msg, success_msg,
                no_update,  # sweep-data-store también se preserva
                modal_is_open, progress_percent, modal_text, progress_percent, progress_style,
                sweep_btn_disabled, stop_btn_disabled,
                {'running': is_running, 'total': total_points},
                sweetalert_script)
    
    # Si llegamos aquí, los datos cambiaron o el trigger fue un botón
    # Actualizar el hash
    sweep_data_last_hash = current_data_hash
    
    # Crear gráficos
    param = sweep_data_global['param']
    z_real = sweep_data_global['z_real']
    z_imag = sweep_data_global['z_imag']
    z_mag = sweep_data_global['z_magnitude']
    phase = sweep_data_global['phase']
    
    # Bode plot - Un solo gráfico con dos ejes Y (magnitud y fase)
    bode_fig = go.Figure()
    if param:
        # Traza de magnitud en eje Y principal (izquierdo)
        bode_fig.add_trace(
            go.Scatter(
                x=param, 
                y=z_mag, 
                mode='lines+markers', 
                name='|Z|',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=6),
                yaxis='y1'
            )
        )
        
        # Traza de fase en eje Y secundario (derecho)
        bode_fig.add_trace(
            go.Scatter(
                x=param, 
                y=[-p for p in phase],  # Negativo para convención Bode
                mode='lines+markers', 
                name='Fase (θ)',
                line=dict(color='#ff7f0e', width=2),
                marker=dict(size=6),
                yaxis='y2'
            )
        )
        
        # Configurar layout con dos ejes Y
        bode_fig.update_layout(
            title={
                'text': "Diagrama de Bode - Respuesta en Frecuencia",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#1f77b4'}
            },
            xaxis=dict(
                title="Frecuencia (Hz)",
                type="log",
                domain=[0, 1],
                fixedrange=False  # Permite zoom en X
            ),
            yaxis=dict(
                title=dict(text="|Z| (Ω)", font=dict(color='#1f77b4')),
                type="log",
                side="left",
                tickfont=dict(color='#1f77b4'),
                fixedrange=False  # Permite zoom en Y1
            ),
            yaxis2=dict(
                title=dict(text="Fase (°)", font=dict(color='#ff7f0e')),
                side="right",
                overlaying="y",
                tickfont=dict(color='#ff7f0e'),
                fixedrange=False  # Permite zoom en Y2
            ),
            height=500,
            showlegend=True,
            legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.8)'),
            margin=dict(l=60, r=60, t=80, b=60),
            autosize=True,
            hovermode='x unified',
            dragmode='zoom'  # Modo de arrastre por defecto: zoom
        )
    
    # Nyquist plot
    nyquist_fig = go.Figure()
    if z_real and z_imag:
        # Crear texto personalizado para hover con frecuencia
        hover_text = [
            f"Frecuencia: {f:.2f} Hz<br>Z': {r:.2f} Ω<br>-Z'': {-i:.2f} Ω"
            for f, r, i in zip(param, z_real, z_imag)
        ]
        
        nyquist_fig.add_trace(go.Scatter(
            x=z_real,
            y=[-z for z in z_imag],  # -Z'' para formato estándar
            mode='lines+markers',
            name='Nyquist',
            text=hover_text,
            hovertemplate='%{text}<extra></extra>',
            marker=dict(size=8, color=param, colorscale='Viridis', 
                       showscale=True, colorbar=dict(title="Freq (Hz)"))
        ))
        nyquist_fig.update_layout(
            title="Diagrama de Nyquist",
            xaxis=dict(
                title="Z' (Ω)",
                fixedrange=False  # Permite zoom en X
            ),
            yaxis=dict(
                title="-Z'' (Ω)",
                scaleanchor="x",
                scaleratio=1,
                fixedrange=False  # Permite zoom en Y
            ),
            height=450,
            width=None,
            autosize=True,
            margin=dict(l=60, r=40, t=60, b=60),
            dragmode='zoom',  # Modo de arrastre por defecto: zoom
            hovermode='closest'
        )
    
    # Textos de progreso
    if is_running and current_point > 0:
        progress_text = f"📊 Punto {current_point}/{total_points}"
        modal_text = f"Analizando punto {current_point} de {total_points}"
    elif is_running:
        progress_text = "🔄 Iniciando barrido..."
        modal_text = "Preparando análisis..."
    else:
        progress_text = ""
        modal_text = ""
    
    # Configuración del modal y controles
    modal_is_open = is_running
    progress_style = {'display': 'block'} if is_running else {'display': 'none'}
    sweep_btn_disabled = is_running
    stop_btn_disabled = not is_running
    
    return (bode_fig, nyquist_fig, progress_text, error_msg, success_msg,
            {'param': param, 'z_real': z_real, 'z_imag': z_imag, 'z_mag': z_mag, 'phase': phase},
            modal_is_open, progress_percent, modal_text, progress_percent, progress_style,
            sweep_btn_disabled, stop_btn_disabled,
            {'running': is_running, 'total': total_points},
            sweetalert_script)

# Callback para ejecutar SweetAlert
app.clientside_callback(
    """
    function(script) {
        if (script && script.length > 0) {
            eval(script);
        }
        return '';
    }
    """,
    Output('sweetalert-script', 'children', allow_duplicate=True),
    Input('sweetalert-script', 'children'),
    prevent_initial_call=True
)

# Callback para exportar datos a CSV
@app.callback(
    Output('download-csv', 'data'),
    Input('export-csv-btn', 'n_clicks'),
    State('sweep-data-store', 'data'),
    prevent_initial_call=True
)
def export_csv(n_clicks, data):
    """Exporta los datos del barrido a un archivo CSV compatible con Origin y pandas."""
    if not data or not data.get('param'):
        raise PreventUpdate
    
    import pandas as pd
    from io import StringIO
    
    # Crear DataFrame con todos los datos
    df = pd.DataFrame({
        'Frecuencia_Hz': data['param'],
        'Z_Real_Ohm': data['z_real'],
        'Z_Imag_Ohm': data['z_imag'],
        'Z_Magnitud_Ohm': data['z_mag'],
        'Fase_Grados': data['phase']
    })
    
    # Agregar columnas calculadas útiles
    df['Frecuencia_kHz'] = df['Frecuencia_Hz'] / 1000
    df['Frecuencia_MHz'] = df['Frecuencia_Hz'] / 1e6
    df['Z_Imag_Neg_Ohm'] = -df['Z_Imag_Ohm']  # -Z'' para Nyquist
    df['Fase_Radianes'] = np.radians(df['Fase_Grados'])
    
    # Reordenar columnas para mejor legibilidad
    column_order = [
        'Frecuencia_Hz', 'Frecuencia_kHz', 'Frecuencia_MHz',
        'Z_Real_Ohm', 'Z_Imag_Ohm', 'Z_Imag_Neg_Ohm',
        'Z_Magnitud_Ohm', 'Fase_Grados', 'Fase_Radianes'
    ]
    df = df[column_order]
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"impedance_sweep_{timestamp}.csv"
    
    # Convertir a CSV con configuración compatible con Origin
    csv_string = df.to_csv(index=False, float_format='%.6e', sep=',')
    
    return dict(content=csv_string, filename=filename)

# ==================== MAIN ====================

if __name__ == '__main__':
    print("="*80)
    print("  🔬 DASHBOARD EVAL-ADMX2001")
    print("  📡 Puerto: http://127.0.0.1:8050")
    print("  📊 Dash + Bootstrap + Plotly")
    print("="*80)
    app.run(debug=True, host='127.0.0.1', port=8050)
