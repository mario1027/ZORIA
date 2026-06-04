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
from pages.common.sidebar import sideBar
from pages.common.mobile_nav import mobileNavBar
from pages.common.footer import footer
from pages.common.floating_terminal_button import floating_terminal_button
from lib.device_state import device_state


logger = logging.getLogger(__name__)


register_page(
    __name__,
    path='/calibration',
    title='Calibración - ZORIA',
    name='Calibración ADMX2001'
)


def _build_status(message, tone='info'):
    return {'message': message, 'tone': tone}


def _default_wizard_state():
    return {
        'step': 0,
        'config': {'r_load': 1000.0, 'freq': 1000.0, 'ch0': 0, 'ch1': 0},
        'results': {'open': None, 'short': None, 'load': None, 'commit': None},
        'progress': {'open': 0, 'short': 0, 'load': 0, 'commit': 0},
        'status': {
            'start': _build_status('Configura el patrón y pulsa Iniciar Calibración.', 'info'),
            'open': _build_status('Pendiente.', 'secondary'),
            'short': _build_status('Pendiente.', 'secondary'),
            'load': _build_status('Pendiente.', 'secondary'),
            'commit': _build_status('Pendiente.', 'secondary'),
        }
    }


def _merge_wizard_state(state):
    merged = _default_wizard_state()
    if not isinstance(state, dict):
        return merged

    for key, value in state.items():
        if key in ('config', 'results', 'progress', 'status') and isinstance(value, dict):
            merged[key] = {**merged[key], **value}
        else:
            merged[key] = value

    return merged


def _calculate_gain_values(r_load):
    from lib.utils import gain_settings_from_impedance_table

    try:
        resistance = max(float(r_load or 1000.0), 0.1)
    except (TypeError, ValueError):
        resistance = 1000.0

    return gain_settings_from_impedance_table(resistance)


def _format_success_message(prefix, result):
    if not isinstance(result, dict) or not result:
        return prefix

    fragments = []
    for key in ('message', 'timestamp', 'saved_at'):
        value = result.get(key)
        if value:
            fragments.append(str(value))

    if not fragments:
        return prefix

    return f"{prefix} {' | '.join(fragments)}"


def _status_with_error(state, key, error):
    merged = _merge_wizard_state(state)
    merged['status'][key] = _build_status(str(error), 'danger')
    return merged


def _format_status(status):
    status_data = status if isinstance(status, dict) else _build_status(str(status), 'secondary')
    icon_by_tone = {
        'success': 'fa-check-circle',
        'warning': 'fa-triangle-exclamation',
        'danger': 'fa-circle-xmark',
        'info': 'fa-circle-info',
        'secondary': 'fa-clock'
    }
    color_by_tone = {
        'success': 'text-success',
        'warning': 'text-warning',
        'danger': 'text-danger',
        'info': 'text-info',
        'secondary': 'text-muted'
    }
    tone = status_data.get('tone', 'info')
    icon = icon_by_tone.get(tone, 'fa-circle-info')
    color = color_by_tone.get(tone, 'text-info')
    return [
        html.I(className=f"fas {icon} me-2 {color}"),
        html.Span(status_data.get('message', ''), className=color)
    ]


def _progress_style(value):
    try:
        progress = int(value or 0)
    except (TypeError, ValueError):
        progress = 0

    progress = max(0, min(progress, 100))
    return {'width': f'{progress}%'}


def _summary_label(state, key):
    merged = _merge_wizard_state(state)
    step_by_key = {'open': 1, 'short': 2, 'load': 3}
    if merged['results'].get(key):
        return html.Span('Completado', className='text-success')
    if merged['step'] == step_by_key.get(key):
        return html.Span('En curso', className='text-warning')
    return html.Span('Pendiente', className='text-muted')


def _looks_like_empty_calibration_noise(lines):
    if not lines:
        return True

    normalized = [str(line).strip() for line in lines if str(line).strip()]
    if not normalized:
        return True

    from lib.calibration_parser import INVALID_KEYWORDS

    meaningful_tokens = ('freq', 'frequency', 'ch0', 'ch1', 'res', 'resistance', '=', 'hz')
    for line in normalized:
        lowered = line.lower()
        if lowered == 'calibrate list' or lowered.startswith('calibrate list '):
            continue
        if any(keyword in lowered for keyword in INVALID_KEYWORDS):
            continue
        if any(token in lowered for token in meaningful_tokens):
            return False
    return True


def calibration_wizard_modal():
    """
    Wizard de Calibración - Ventana arrastrable tipo escritorio.
    Sistema moderno de ventanas con capacidad de mover, minimizar, maximizar.
    """
    progress_section = html.Div([
        html.Div([
            html.Div([
                html.Span("Calibration cockpit", className="cal-wizard-kicker"),
                html.H4(
                    "Una secuencia clara, rápida y verificable",
                    className="cal-wizard-progress-title"
                ),
                html.P(
                    "Cada paso muestra conexion, criterio de ejecucion y estado del equipo "
                    "sin perder el contexto del proceso.",
                    className="cal-wizard-progress-copy"
                )
            ], className="cal-wizard-progress-copyblock"),
            html.Div([
                html.Span("OPEN", className="cal-wizard-chip"),
                html.Span("SHORT", className="cal-wizard-chip"),
                html.Span("LOAD", className="cal-wizard-chip")
            ], className="cal-wizard-chip-row")
        ], className="cal-wizard-progress-hero"),
        html.Div([
            html.Div([
                html.Div("1", className="wizard-step-indicator", id="cal-step-icon-1"),
                html.Div([
                    html.Span("Config", className="wizard-step-label"),
                    html.Small("Setup", className="cal-wizard-step-meta")
                ], className="cal-wizard-step-copy")
            ], className="wizard-step", id="cal-step-1"),
            html.Div(className="wizard-step-connector", id="cal-connector-1"),
            html.Div([
                html.Div("2", className="wizard-step-indicator", id="cal-step-icon-2"),
                html.Div([
                    html.Span("Open", className="wizard-step-label"),
                    html.Small("Circuito abierto", className="cal-wizard-step-meta")
                ], className="cal-wizard-step-copy")
            ], className="wizard-step", id="cal-step-2"),
            html.Div(className="wizard-step-connector", id="cal-connector-2"),
            html.Div([
                html.Div("3", className="wizard-step-indicator", id="cal-step-icon-3"),
                html.Div([
                    html.Span("Short", className="wizard-step-label"),
                    html.Small("Cierre total", className="cal-wizard-step-meta")
                ], className="cal-wizard-step-copy")
            ], className="wizard-step", id="cal-step-3"),
            html.Div(className="wizard-step-connector", id="cal-connector-3"),
            html.Div([
                html.Div("4", className="wizard-step-indicator", id="cal-step-icon-4"),
                html.Div([
                    html.Span("Load", className="wizard-step-label"),
                    html.Small("Patron de referencia", className="cal-wizard-step-meta")
                ], className="cal-wizard-step-copy")
            ], className="wizard-step", id="cal-step-4"),
            html.Div(className="wizard-step-connector", id="cal-connector-4"),
            html.Div([
                html.Div("5", className="wizard-step-indicator", id="cal-step-icon-5"),
                html.Div([
                    html.Span("Guardar", className="wizard-step-label"),
                    html.Small("Persistencia", className="cal-wizard-step-meta")
                ], className="cal-wizard-step-copy")
            ], className="wizard-step", id="cal-step-5")
        ], className="wizard-steps")
    ], className="wizard-progress")

    intro_step = html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.I(className="fas fa-magic fa-3x mb-3"),
                    html.Span("Preparacion", className="cal-wizard-kicker"),
                    html.H4("Configura el patron antes de tocar el hardware", className="mb-3"),
                    html.P(
                        "Define resistencia y frecuencia. El wizard ajusta la ganancia, "
                        "configura average 200 y tdelay 200 ms, y deja la secuencia lista.",
                        className="cal-wizard-lead mb-4"
                    ),
                    html.Div([
                        html.Div([
                            html.Span("Patron de referencia", className="cal-wizard-metric-label"),
                            html.Strong("Open / Short / Load", className="cal-wizard-metric-value")
                        ], className="cal-wizard-metric"),
                        html.Div([
                            html.Span("Modo", className="cal-wizard-metric-label"),
                            html.Strong("Guiado", className="cal-wizard-metric-value")
                        ], className="cal-wizard-metric"),
                        html.Div([
                            html.Span("Objetivo", className="cal-wizard-metric-label"),
                            html.Strong("Persistir en flash", className="cal-wizard-metric-value")
                        ], className="cal-wizard-metric")
                    ], className="cal-wizard-metrics")
                ], className="cal-wizard-intro-copy"),
                html.Div([
                    html.Div([
                        html.H6("Configuracion automatica", className="cal-wizard-panel-title"),
                        html.P(
                            "Introduce el patron fisico que vas a montar. Al iniciar y antes de "
                            "cada paso OPEN/SHORT/LOAD se envia average 200 al dispositivo.",
                            className="cal-wizard-panel-copy"
                        )
                    ], className="cal-wizard-panel-header"),
                    html.Div([
                        html.Label([
                            html.I(className="fas fa-resistor me-2"),
                            "Resistencia de calibracion (Ohm)"
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
                        html.Small(
                            "Rango habitual: 100 Ohm a 100 kOhm.",
                            className="text-muted d-block text-start mt-1"
                        )
                    ], className="mb-3"),
                    html.Div([
                        html.Label([
                            html.I(className="fas fa-wave-square me-2"),
                            "Frecuencia de calibracion (Hz)"
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
                        html.Small(
                            "Usa la frecuencia donde quieras maximizar la fidelidad.",
                            className="text-muted d-block text-start mt-1"
                        )
                    ], className="mb-3"),
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-calculator me-2"),
                            html.Span("Ganancia calculada", className="me-2"),
                            html.Span(id='cal-wizard-gain-display', children=[
                                html.Span("CH0: 0", className="badge bg-info me-2"),
                                html.Span("CH1: 0", className="badge bg-info")
                            ])
                        ], className="cal-wizard-gain-inner")
                    ], id='cal-wizard-gain-panel', className="mb-4"),
                    html.Button([
                        html.I(className="fas fa-play me-2"),
                        html.Span('Iniciar Calibración', **{'data-i18n': 'cal.start_wizard'}),
                    ], id='cal-wizard-start', className="btn btn-primary btn-lg w-100 wizard-action-btn"),
                    html.Div(
                        id='cal-wizard-start-status',
                        className="text-center small mt-3 cal-wizard-inline-status"
                    )
                ], className="cal-wizard-control-card")
            ], className="cal-wizard-intro-grid")
        ], className="cal-wizard-stage cal-wizard-stage-intro")
    ], id='cal-wizard-step-0', className="wizard-step-content")

    open_step = html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Span("Paso 2", className="cal-wizard-kicker"),
                    html.H4("Open Calibration", className="mb-2"),
                    html.P(
                        "Verifica el circuito abierto con una conexion limpia entre cada par.",
                        className="cal-wizard-lead"
                    )
                ], className="cal-wizard-stage-header"),
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
                ], className="cal-diagram cal-diagram-container mb-4 cal-wizard-stage-main"),
                html.Div([
                    html.Div([
                        html.H6("Checklist", className="mb-2"),
                        html.Ol([
                            html.Li("Une H_CUR con H_POT usando el tramo mas corto posible."),
                            html.Li("Une L_CUR con L_POT con el mismo criterio."),
                            html.Li("Mantén separados ambos pares para conservar el circuito abierto.")
                        ], className="text-start mb-0")
                    ], className="alert alert-info border-0 mb-4 cal-wizard-callout"),
                    html.Div([
                        html.Span("Estado del paso", className="cal-wizard-status-label"),
                        html.Div(id="cal-open-status", className="text-start text-muted small mb-3 cal-wizard-inline-status"),
                        html.Div([
                            html.Div(
                                id="cal-open-progress",
                                className="progress-bar progress-bar-striped progress-bar-animated",
                                style={'width': '0%'}
                            )
                        ], className="progress mb-4 cal-wizard-progressbar", style={'height': '8px'}),
                        html.Button([
                            html.I(className="fas fa-check-circle me-2"),
                            "Ejecutar Open"
                        ], id='cal-wizard-run-open', className="btn btn-primary w-100 wizard-action-btn")
                    ], className="cal-wizard-action-card")
                ], className="cal-wizard-stage-aside")
            ], className="cal-wizard-stage-grid")
        ], className="py-3 cal-wizard-stage cal-wizard-stage-open")
    ], id='cal-wizard-step-1', className="wizard-step-content", style={'display': 'none'})

    short_step = html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Span("Paso 3", className="cal-wizard-kicker"),
                    html.H4("Short Calibration", className="mb-2"),
                    html.P(
                        "Cierra todos los nodos para medir el offset del montaje real.",
                        className="cal-wizard-lead"
                    )
                ], className="cal-wizard-stage-header"),
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
                ], className="cal-diagram cal-diagram-short cal-wizard-stage-main"),
                html.Div([
                    html.Div([
                        html.H6("Importante", className="mb-2"),
                        html.Ul([
                            html.Li("Conecta todos los terminales con un unico punto comun."),
                            html.Li("Evita bucles y contactos flojos."),
                            html.Li(html.Span("La magnitud se reduce automaticamente a 0.2 V.", className="text-warning"))
                        ], className="text-start mb-0")
                    ], className="alert alert-warning border-0 mb-4 cal-wizard-callout"),
                    html.Div([
                        html.Span("Estado del paso", className="cal-wizard-status-label"),
                        html.Div(id="cal-short-status", className="text-start text-muted small mb-3 cal-wizard-inline-status"),
                        html.Div([
                            html.Div(
                                id="cal-short-progress",
                                className="progress-bar progress-bar-striped progress-bar-animated bg-warning",
                                style={'width': '0%'}
                            )
                        ], className="progress mb-4 cal-wizard-progressbar", style={'height': '8px'}),
                        html.Button([
                            html.I(className="fas fa-check-circle me-2"),
                            "Ejecutar Short"
                        ], id='cal-wizard-run-short', className="btn btn-warning w-100 text-dark wizard-action-btn")
                    ], className="cal-wizard-action-card")
                ], className="cal-wizard-stage-aside")
            ], className="cal-wizard-stage-grid")
        ], className="py-3 cal-wizard-stage cal-wizard-stage-short")
    ], id='cal-wizard-step-2', className="wizard-step-content", style={'display': 'none'})

    load_step = html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Span("Paso 4", className="cal-wizard-kicker"),
                    html.H4("Load Calibration", className="mb-2"),
                    html.P(
                        "Monta la resistencia patron y captura la referencia absoluta del sistema.",
                        className="cal-wizard-lead mb-2"
                    ),
                    html.H3(id="cal-wizard-load-value-display", children="1000 Ω", className="text-success mb-0")
                ], className="cal-wizard-stage-header"),
                html.Div([
                    html.Div([
                        html.Div("H", className="cal-terminal cal-terminal-hcur cal-terminal-active"),
                        html.Div(className="cal-wire cal-wire-load"),
                        html.Div("L", className="cal-terminal cal-terminal-lpot cal-terminal-active")
                    ], className="cal-diagram-row"),
                    html.Div([
                        html.Div("LOAD", className="cal-indicator cal-indicator-load cal-anim-blink")
                    ], className="cal-diagram-indicator")
                ], className="cal-diagram cal-diagram-load cal-wizard-stage-main"),
                html.Div([
                    html.Div([
                        html.H6("Instrucciones", className="mb-2"),
                        html.Ol([
                            html.Li("Conecta la resistencia de precision entre H_CUR y L_POT."),
                            html.Li(["Valor nominal: ", html.Strong(id="cal-wizard-load-instruction-value", children="1000 Ω")]),
                            html.Li("Mantén el contacto limpio y la longitud de conexion al minimo.")
                        ], className="text-start mb-0")
                    ], className="alert alert-success border-0 mb-4 cal-wizard-callout"),
                    html.Div([
                        html.Span("Estado del paso", className="cal-wizard-status-label"),
                        html.Div(id="cal-load-status", className="text-start text-muted small mb-3 cal-wizard-inline-status"),
                        html.Div([
                            html.Div(
                                id="cal-load-progress",
                                className="progress-bar progress-bar-striped progress-bar-animated bg-success",
                                style={'width': '0%'}
                            )
                        ], className="progress mb-4 cal-wizard-progressbar", style={'height': '8px'}),
                        html.Button([
                            html.I(className="fas fa-check-circle me-2"),
                            "Ejecutar Load"
                        ], id='cal-wizard-run-load', className="btn btn-success w-100 wizard-action-btn")
                    ], className="cal-wizard-action-card")
                ], className="cal-wizard-stage-aside")
            ], className="cal-wizard-stage-grid cal-wizard-stage-grid-load")
        ], className="py-3 cal-wizard-stage cal-wizard-stage-load")
    ], id='cal-wizard-step-3', className="wizard-step-content", style={'display': 'none'})

    commit_step = html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Span("Paso 5", className="cal-wizard-kicker"),
                    html.H4("Guardar Calibración", className="mb-2"),
                    html.P(
                        "Revisa el resultado y persiste los coeficientes en memoria no volatil.",
                        className="cal-wizard-lead"
                    )
                ], className="cal-wizard-stage-header"),
                html.Div([
                    html.H6("Resumen de calibracion", className="mb-3"),
                    html.Div([
                        html.Div([
                            html.Span("Open", className="cal-wizard-summary-label"),
                            html.Span(id="cal-summary-open", children="Completado", className="text-success")
                        ], className="cal-wizard-summary-row"),
                        html.Div([
                            html.Span("Short", className="cal-wizard-summary-label"),
                            html.Span(id="cal-summary-short", children="Completado", className="text-success")
                        ], className="cal-wizard-summary-row"),
                        html.Div([
                            html.Span("Load", className="cal-wizard-summary-label"),
                            html.Span(id="cal-summary-load", children="Completado", className="text-success")
                        ], className="cal-wizard-summary-row"),
                        html.Hr(),
                        html.Div([
                            html.Span("Resistencia", className="cal-wizard-summary-label"),
                            html.Strong(id="cal-summary-r", children="1000 Ω")
                        ], className="cal-wizard-summary-row"),
                        html.Div([
                            html.Span("Frecuencia", className="cal-wizard-summary-label"),
                            html.Strong(id="cal-summary-freq", children="1000 Hz")
                        ], className="cal-wizard-summary-row"),
                        html.Div([
                            html.Span("Ganancia", className="cal-wizard-summary-label"),
                            html.Strong(id="cal-summary-gain", children="CH0=0, CH1=0")
                        ], className="cal-wizard-summary-row")
                    ], className="cal-wizard-summary-card")
                ], className="cal-wizard-stage-main"),
                html.Div([
                    html.Div([
                        html.I(className="fas fa-lock me-2"),
                        html.Span("Clave de escritura", className="me-2"),
                        html.Code("Analog123", className="bg-light text-dark px-2 py-1 rounded")
                    ], className="alert alert-secondary border-0 mb-4 cal-wizard-callout"),
                    html.Div([
                        html.Span("Estado del guardado", className="cal-wizard-status-label"),
                        html.Div(id="cal-commit-status", className="text-start text-muted small mb-3 cal-wizard-inline-status"),
                        html.Div([
                            html.Div(
                                id="cal-commit-progress",
                                className="progress-bar progress-bar-striped progress-bar-animated bg-info",
                                style={'width': '0%'}
                            )
                        ], className="progress mb-4 cal-wizard-progressbar", style={'height': '8px'}),
                        html.Button([
                            html.I(className="fas fa-save me-2"),
                            "Guardar en Flash"
                        ], id='cal-wizard-run-commit', className="btn btn-info w-100 text-white wizard-action-btn")
                    ], className="cal-wizard-action-card")
                ], className="cal-wizard-stage-aside")
            ], className="cal-wizard-stage-grid")
        ], className="py-3 cal-wizard-stage cal-wizard-stage-commit")
    ], id='cal-wizard-step-4', className="wizard-step-content", style={'display': 'none'})

    complete_step = html.Div([
        html.Div([
            html.Div([
                html.I(className="fas fa-check-circle fa-4x text-success mb-3 cal-anim-bounce"),
                html.Span("Secuencia completa", className="cal-wizard-kicker"),
                html.H3("Calibracion completada", className="mb-3 text-success"),
                html.P(
                    "Los coeficientes quedaron guardados y el instrumento ya puede trabajar con la "
                    "nueva referencia.",
                    className="cal-wizard-lead mb-4"
                )
            ], className="text-center mb-4"),
            html.Div([
                html.H6("Detalles", className="mb-3"),
                html.Div([
                    html.Div([
                        html.Span("Timestamp", className="cal-wizard-summary-label"),
                        html.Span(id="cal-complete-timestamp", children=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    ], className="cal-wizard-summary-row"),
                    html.Div([
                        html.Span("Resistencia", className="cal-wizard-summary-label"),
                        html.Strong(id="cal-complete-r", children="1000 Ω")
                    ], className="cal-wizard-summary-row"),
                    html.Div([
                        html.Span("Frecuencia", className="cal-wizard-summary-label"),
                        html.Strong(id="cal-complete-freq", children="1000 Hz")
                    ], className="cal-wizard-summary-row")
                ], className="cal-wizard-summary-card")
            ], className="mb-4"),
            html.Div([
                html.Button([
                    html.I(className="fas fa-redo me-2"),
                    "Nueva Calibración"
                ], id='cal-wizard-restart', className="btn btn-outline-primary me-2 wizard-action-btn"),
                html.Button([
                    html.I(className="fas fa-times me-2"),
                    "Cerrar"
                ], id='cal-wizard-finish', className="btn btn-primary wizard-action-btn")
            ], className="text-center")
        ], className="py-4 cal-wizard-stage cal-wizard-stage-complete")
    ], id='cal-wizard-step-5', className="wizard-step-content", style={'display': 'none'})

    return html.Div([
        dcc.Store(id='cal-wizard-state', data={**_default_wizard_state()}),
        dcc.Store(id='cal-saved-calibrations', data=[], storage_type='session'),
        dcc.Store(id='cal-wizard-initialized', data=False),
        dcc.Interval(id='cal-wizard-interval', interval=500),
        html.Div([
            html.Div([
                html.Div([
                    html.Span(html.I(className="fas fa-balance-scale"), className="cal-wizard-title-icon"),
                    html.Div([
                        html.Span('', **{'data-i18n': 'cal.wizard_title'}),
                        html.Small("Flujo guiado para Open, Short y Load", className="cal-wizard-title-subtitle")
                    ], className="cal-wizard-title-copy")
                ], className="window-title"),
                html.Div([
                    html.Button(html.I(className="fas fa-minus"), id="cal-wizard-minimize", className="window-control-btn window-btn-minimize", title="Minimizar"),
                    html.Button(html.I(className="fas fa-expand"), id="cal-wizard-maximize", className="window-control-btn window-btn-maximize", title="Maximizar"),
                    html.Button(html.I(className="fas fa-times"), id="cal-wizard-close", className="window-control-btn window-btn-close", title="Cerrar")
                ], className="window-controls")
            ], className="window-header", id="cal-wizard-header"),
            html.Div([
                progress_section,
                html.Div([
                    intro_step,
                    open_step,
                    short_step,
                    load_step,
                    commit_step,
                    complete_step
                ], className="wizard-content")
            ], className="window-body")
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
                ], id="btn-refresh-calibrations", className="btn btn-sm btn-outline-secondary", type="button")
                            ], className="d-flex justify-content-between align-items-center mb-3"),
                            html.Div(id="cal-delete-status", className="mb-2"),
                            html.Div(id="cal-refresh-status", className="mb-2 small text-muted"),
                            dcc.Loading(
                                id="cal-table-loading",
                                type="default",
                                children=html.Div([
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
                                                html.Td(
                                                    colSpan="7",
                                                    className="text-center text-muted",
                                                    children=[
                                                        html.I(className="fas fa-info-circle me-2"),
                                                        "Conecta el ADMX2001 y pulsa Actualizar para cargar calibraciones."
                                                    ]
                                                )
                                            ])
                                        ])
                                    ], className="table table-hover")
                                ], className="table-responsive"),
                            ),
                        ], className="card-body")
                    ], id="calibrations-panel", className="card shadow-sm"),

                    # Modal confirmación borrado
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.H5([
                                        html.I(className="fas fa-exclamation-triangle text-danger me-2"),
                                        "Eliminar todas las calibraciones"
                                    ], className="modal-title"),
                                    html.Button("×", id="cal-delete-modal-close", className="btn-close", **{"aria-label": "Cerrar"}),
                                ], className="modal-header"),
                                html.Div([
                                    html.P(
                                        "Esta acción borra permanentemente todas las calibraciones "
                                        "guardadas en la memoria flash del ADMX2001. No se puede deshacer.",
                                        className="mb-3"
                                    ),
                                    html.P([
                                        "Contraseña predeterminada: ",
                                        html.Code("Analog123")
                                    ], className="text-muted small mb-0"),
                                ], className="modal-body"),
                                html.Div([
                                    html.Button("Cancelar", id="cal-delete-modal-cancel", className="btn btn-secondary me-2"),
                                    html.Button([
                                        html.I(className="fas fa-trash me-1"),
                                        "Eliminar todo"
                                    ], id="cal-delete-modal-confirm", className="btn btn-danger"),
                                ], className="modal-footer"),
                            ], className="modal-content")
                        ], className="modal-dialog modal-dialog-centered")
                    ], id="cal-delete-modal", className="modal fade", style={
                        "display": "none",
                        "position": "fixed",
                        "top": "0",
                        "left": "0",
                        "width": "100%",
                        "height": "100%",
                        "zIndex": "1050",
                        "backgroundColor": "rgba(0,0,0,0.5)",
                        "alignItems": "center",
                        "justifyContent": "center",
                    }, tabIndex="-1"),
                    
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
        
        ch0, ch1 = _calculate_gain_values(r_load)

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
        State('command-modal', 'style'),
        prevent_initial_call=True
    )
    def toggle_wizard(start_clicks, close_clicks, finish_clicks, wizard_state, terminal_style):
        """Controla la visibilidad del wizard"""
        if not ctx.triggered:
            raise PreventUpdate
        
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if triggered_id == 'btn-start-calibration':
            device_state.force_exclusive_session('calibration_wizard')
            return {'display': 'flex'}, _default_wizard_state()
        
        if triggered_id in ['cal-wizard-close', 'cal-wizard-finish']:
            device_state.release_exclusive_session('calibration_wizard')
            terminal_open = (
                terminal_style
                and terminal_style.get('display') in ('flex', 'block')
            )
            if terminal_open:
                device_state.force_exclusive_session('terminal')
            return {'display': 'none'}, _merge_wizard_state(wizard_state)
        
        raise PreventUpdate

    @app.callback(
        Output('cal-wizard-state', 'data', allow_duplicate=True),
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
    def execute_wizard_step(
        start_clicks,
        open_clicks,
        short_clicks,
        load_clicks,
        commit_clicks,
        restart_clicks,
        wizard_state,
        r_load,
        freq,
    ):
        """Ejecuta el paso activo del wizard contra el dispositivo conectado."""
        if not ctx.triggered:
            raise PreventUpdate

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if triggered_id == 'cal-wizard-restart':
            return _default_wizard_state()

        session = device_state.get_exclusive_session()
        if session == 'terminal':
            state = _merge_wizard_state(wizard_state)
            step_key = (
                'start' if triggered_id == 'cal-wizard-start'
                else triggered_id.rsplit('-', 1)[-1]
            )
            state['status'][step_key] = _build_status(
                'Cierra el terminal CLI antes de ejecutar pasos del wizard.',
                'danger'
            )
            return state
        if session != 'calibration_wizard':
            device_state.force_exclusive_session('calibration_wizard')

        state = _merge_wizard_state(wizard_state)
        state['config']['r_load'] = float(r_load or 1000.0)
        state['config']['freq'] = float(freq or 1000.0)
        ch0, ch1 = _calculate_gain_values(state['config']['r_load'])
        state['config']['ch0'] = ch0
        state['config']['ch1'] = ch1

        from lib.device_state import device_state

        device = device_state.device
        if device is None or not device_state.is_connected or not hasattr(device, 'calibration'):
            status_key = 'start' if triggered_id == 'cal-wizard-start' else triggered_id.rsplit('-', 1)[-1]
            state['status'][status_key] = _build_status(
                'Dispositivo no conectado. Conecta el ADMX2001 desde el Dashboard.',
                'danger'
            )
            return state

        calibration = device.calibration

        # Adquirir lock de operación para bloquear verify_connection durante calibración
        lock_acquired = device_state._operation_lock.acquire(timeout=90.0)
        if lock_acquired:
            device_state._operation_lock_owner = 'calibration_wizard'
        if not lock_acquired:
            state['status']['start' if triggered_id == 'cal-wizard-start' else triggered_id.rsplit('-', 1)[-1]] = _build_status(
                'Dispositivo ocupado (terminal CLI, barrido u otra operación en curso). '
                'Espere a que termine e intente de nuevo.',
                'danger'
            )
            return state
        try:
            if triggered_id == 'cal-wizard-start':
                state = _default_wizard_state()
                state['config']['r_load'] = float(r_load or 1000.0)
                state['config']['freq'] = float(freq or 1000.0)
                state['config']['ch0'] = ch0
                state['config']['ch1'] = ch1
                calibration.start_calibration_sequence(
                    ch0_gain=ch0,
                    ch1_gain=ch1,
                    frequency=state['config']['freq']
                )
                state['step'] = 1
                state['status']['start'] = _build_status(
                    f'Secuencia inicializada (CH0={ch0}, CH1={ch1}, average=200, tdelay=200 ms).',
                    'success'
                )
                state['status']['open'] = _build_status(
                    'Preparado para OPEN. Configure las puntas y pulse Ejecutar Open.',
                    'info'
                )
                return state

            if triggered_id == 'cal-wizard-run-open':
                result = calibration.calibrate_open()
                state['results']['open'] = result
                state['progress']['open'] = 100
                state['status']['open'] = _build_status(
                    _format_success_message('Calibración OPEN completada.', result),
                    'success'
                )
                state['step'] = 2
                state['status']['short'] = _build_status(
                    'Configure SHORT y pulse Ejecutar Short.',
                    'info'
                )
                return state

            if triggered_id == 'cal-wizard-run-short':
                result = calibration.calibrate_short()
                state['results']['short'] = result
                state['progress']['short'] = 100
                state['status']['short'] = _build_status(
                    _format_success_message('Calibración SHORT completada.', result),
                    'success'
                )
                state['step'] = 3
                state['status']['load'] = _build_status(
                    'Conecte la carga conocida y pulse Ejecutar Load.',
                    'info'
                )
                return state

            if triggered_id == 'cal-wizard-run-load':
                result = calibration.calibrate_load(state['config']['r_load'], 0.0)
                state['results']['load'] = result
                state['progress']['load'] = 100
                state['status']['load'] = _build_status(
                    _format_success_message('Calibración LOAD completada.', result),
                    'success'
                )
                state['step'] = 4
                state['status']['commit'] = _build_status(
                    'Listo para guardar en flash. Pulse Guardar en Flash.',
                    'info'
                )
                return state

            if triggered_id == 'cal-wizard-run-commit':
                calibration.commit()
                commit_timestamp = getattr(calibration.current_state, 'timestamp', None)
                state['results']['commit'] = {
                    'timestamp': commit_timestamp,
                    'saved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                state['progress']['commit'] = 100
                state['status']['commit'] = _build_status(
                    'Calibración guardada en flash correctamente.',
                    'success'
                )
                state['step'] = 5
                return state

        except Exception as error:
            if triggered_id == 'cal-wizard-start':
                return _status_with_error(state, 'start', error)
            return _status_with_error(state, triggered_id.rsplit('-', 1)[-1], error)
        finally:
            if lock_acquired:
                device_state._operation_lock_owner = None
                device_state._operation_lock.release()

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
        Input('cal-wizard-state', 'data'),
        Input('cal-wizard-r-load', 'value'),
        Input('cal-wizard-freq', 'value')
    )
    def navigate_wizard(state, r_load, freq):
        """Navega entre los pasos del wizard"""
        state = _merge_wizard_state(state)
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
        ch0, ch1 = _calculate_gain_values(r_val)
        
        gain_display = f"CH0={ch0}, CH1={ch1}"
        
        return (
            step_style(0), step_style(1), step_style(2), step_style(3), step_style(4), step_style(5),
            step_class(1), step_class(2), step_class(3), step_class(4), step_class(5),
            connector_class(1), connector_class(2), connector_class(3), connector_class(4),
            r_display, r_display, r_display, f_display, gain_display, r_display, f_display
        )

    @app.callback(
        Output('cal-wizard-start-status', 'children'),
        Output('cal-open-progress', 'style'),
        Output('cal-open-status', 'children'),
        Output('cal-short-progress', 'style'),
        Output('cal-short-status', 'children'),
        Output('cal-load-progress', 'style'),
        Output('cal-load-status', 'children'),
        Output('cal-commit-progress', 'style'),
        Output('cal-commit-status', 'children'),
        Output('cal-summary-open', 'children'),
        Output('cal-summary-short', 'children'),
        Output('cal-summary-load', 'children'),
        Output('cal-complete-timestamp', 'children'),
        Input('cal-wizard-state', 'data')
    )
    def render_wizard_status(state):
        """Renderiza el estado persistido del wizard en la UI."""
        state = _merge_wizard_state(state)
        commit_result = state['results'].get('commit') or {}
        complete_timestamp = commit_result.get(
            'saved_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        return (
            _format_status(state['status']['start']),
            _progress_style(state['progress']['open']),
            _format_status(state['status']['open']),
            _progress_style(state['progress']['short']),
            _format_status(state['status']['short']),
            _progress_style(state['progress']['load']),
            _format_status(state['status']['load']),
            _progress_style(state['progress']['commit']),
            _format_status(state['status']['commit']),
            _summary_label(state, 'open'),
            _summary_label(state, 'short'),
            _summary_label(state, 'load'),
            complete_timestamp,
        )


    # Callback: borrar calibraciones (separado del refresco)
    @app.callback(
        Output('calibrations-table-body', 'children', allow_duplicate=True),
        Output('cal-delete-status', 'children', allow_duplicate=True),
        Input('cal-delete-modal-confirm', 'n_clicks'),
        prevent_initial_call=True,
    )
    def delete_calibrations_and_refresh(confirm_clicks):
        from lib.device_state import device_state

        if not confirm_clicks:
            raise PreventUpdate
        try:
            device = device_state.device
            if not device or not device_state.is_connected or not hasattr(device, 'calibration'):
                return [
                    html.Tr([
                        html.Td(colSpan="7", className="text-center text-warning", children=[
                            html.I(className="fas fa-exclamation-triangle me-2"),
                            "Dispositivo no conectado. No se pudo borrar."
                        ])
                    ])
                ], html.Div(className="text-warning small", children="Sin conexión.")
            device.calibration.erase_all_calibrations()
            logger.info("[Cal] Calibraciones borradas desde UI")
            status = html.Div([
                html.I(className="fas fa-check-circle me-2 text-success"),
                "Calibraciones eliminadas. Pulsa Actualizar para verificar."
            ], className="alert alert-success py-2 mb-0 small")
            return [
                html.Tr([
                    html.Td(colSpan="7", className="text-center text-muted", children=[
                        html.I(className="fas fa-info-circle me-2"),
                        "Lista vacía tras borrado. Pulsa Actualizar para confirmar."
                    ])
                ])
            ], status
        except Exception as e:
            logger.error(f"[Cal] Error borrando: {e}")
            return [
                html.Tr([
                    html.Td(colSpan="7", className="text-center text-danger", children=str(e))
                ])
            ], html.Div(className="text-danger small", children=str(e))

    # Callback: actualizar tabla de calibraciones
    @app.callback(
        Output('calibrations-table-body', 'children'),
        Output('cal-refresh-status', 'children'),
        Input('btn-refresh-calibrations', 'n_clicks'),
        Input('btn-view-calibrations', 'n_clicks'),
        prevent_initial_call=True,
    )
    def refresh_calibrations_table(refresh_clicks, view_clicks):
        """Actualiza la tabla de calibraciones almacenadas desde el dispositivo"""
        
        from lib.device_state import device_state
        from lib.calibration_parser import (
            parse_calibrate_list_lines,
            parse_calibrate_list_detail_lines,
            line_looks_like_firmware_error,
            format_freq_label_from_khz,
            format_calibrate_list_khz,
            format_calibrate_gain_cell,
            format_calibrate_steps_cell,
            format_calibrate_resistance_cell,
            calibrate_config_is_complete,
        )
        import time as _time

        triggered = ctx.triggered_id if ctx.triggered else None
        stamp = datetime.now().strftime('%H:%M:%S')
        status_ok = html.Span([
            html.I(className="fas fa-sync me-1"),
            f"Actualizado a las {stamp}",
        ], className="text-success")

        def _finish(rows, css_class="text-success", note=None):
            msg = html.Span([
                html.I(className="fas fa-sync me-1"),
                note or f"Actualizado a las {stamp}",
            ], className=css_class)
            return rows, msg

        try:
            # Obtener dispositivo desde device_state global
            device = device_state.device
            
            if device is None or not device_state.is_connected or not hasattr(device, 'calibration'):
                return _finish([
                    html.Tr([
                        html.Td(colSpan="7", className="text-center text-muted", children=[
                            html.I(className="fas fa-exclamation-triangle me-2"),
                            "Dispositivo no conectado. Conecta el ADMX2001 desde el Dashboard."
                        ])
                    ])
                ], "text-warning", "Sin conexión — conecta desde el Dashboard.")
            
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
            
            # Verificar si hay errores reales en la respuesta
            if calibrations_raw:
                error_lines = [
                    line for line in calibrations_raw
                    if line_looks_like_firmware_error(line)
                ]
                if error_lines:
                    error_msg = error_lines[0]
                    return _finish([
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
                    ], "text-warning", f"Error del dispositivo ({stamp}).")
            
            if not calibrations_raw or len(calibrations_raw) == 0:
                return _finish([
                    html.Tr([
                        html.Td(colSpan="7", className="text-center text-muted", children=[
                            html.I(className="fas fa-info-circle me-2"),
                            "No hay calibraciones almacenadas en el dispositivo."
                        ])
                    ])
                ], "text-muted", "Flash vacío — sin calibraciones.")

            rows = []
            frequencies_with_configs = parse_calibrate_list_lines(calibrations_raw)

            # Enriquecer cada frecuencia con calibrate list <kHz> (Vg/Ig + open/short/load)
            for idx, (freq, configs) in enumerate(list(frequencies_with_configs.items())):
                if freq == '?':
                    continue
                if idx > 0:
                    _time.sleep(0.2)
                try:
                    freq_arg = format_calibrate_list_khz(freq)
                    detail_raw = device.calibration.list_calibrations_at_frequency(freq_arg)
                    logger.info(
                        f"[Cal] detail calibrate list {freq_arg}: "
                        f"{len(detail_raw or [])} líneas"
                    )
                    if detail_raw:
                        for d_idx, d_line in enumerate(detail_raw[:8]):
                            logger.info(f"[Cal]   detail[{d_idx}]: {repr(d_line)}")
                    detail_configs = parse_calibrate_list_detail_lines(
                        detail_raw or [], context_freq_khz=freq,
                    )
                    if not detail_configs:
                        detail_parsed = parse_calibrate_list_lines(
                            detail_raw or [], context_freq_khz=freq,
                        )
                        detail_configs = [
                            c for c in (detail_parsed.get(freq) or detail_parsed.get('?', []))
                            if not c.get('placeholder')
                        ]
                    if detail_configs:
                        frequencies_with_configs[freq] = detail_configs
                    else:
                        logger.warning(
                            f"[Cal] Sin detalle parseable para {freq_arg} kHz "
                            f"(raw={detail_raw!r})"
                        )
                except Exception as detail_err:
                    logger.warning(f"[Cal] No se pudo detallar freq {freq} kHz: {detail_err}")
            
            # Log detallado del resultado del parseo
            logger.info(f"[Cal] '==== RESULTADO DEL PARSEO ===='")
            logger.info(f"[Cal] Frecuencias parseadas: {len(frequencies_with_configs)}")
            for freq_key in sorted(frequencies_with_configs.keys(), key=lambda x: float(x) if x.isdigit() else 0):
                configs = frequencies_with_configs[freq_key]
                logger.info(f"[Cal] FREQ={freq_key} kHz: {len(configs)} configs")
                for idx, cfg in enumerate(configs):
                    if cfg.get('placeholder'):
                        logger.info(f"[Cal]   [{idx}] PLACEHOLDER")
                    else:
                        logger.info(
                            f"[Cal]   [{idx}] Vg={cfg.get('vg')}, Ig={cfg.get('ig')}, "
                            f"open={cfg.get('open')}, short={cfg.get('short')}, load={cfg.get('load')}"
                        )
            logger.info(f"[Cal] '==== FIN PARSEO ===='")
            
            # Crear filas organizadas por frecuencia
            row_num = 1
            for freq, configs in sorted(
                frequencies_with_configs.items(),
                key=lambda x: float(x[0]) if str(x[0]).replace('.', '', 1).isdigit() else 0,
            ):
                if freq == '?':
                    continue

                usable = [c for c in configs if not c.get('placeholder')]
                if not usable:
                    freq_hint = format_calibrate_list_khz(freq)
                    rows.append(
                        html.Tr([
                            html.Td(str(row_num), className="text-center"),
                            html.Td(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                   className="small text-muted"),
                            html.Td("N/A"),
                            html.Td(format_freq_label_from_khz(freq), className="fw-bold"),
                            html.Td(
                                html.Span(
                                    f"— (calibrate list {freq_hint})",
                                    className="text-muted small",
                                ),
                            ),
                            html.Td([
                                html.Span("○", className="text-warning",
                                         title="Sin detalle — pulsa Actualizar de nuevo")
                            ], className="text-center"),
                            html.Td([
                                html.Button([
                                    html.I(className="fas fa-search")
                                ], className="btn btn-sm btn-outline-secondary",
                                   title=f"Detalle: calibrate list {freq_hint}")
                            ], className="text-center")
                        ])
                    )
                    row_num += 1
                    continue

                for config in usable:
                    complete = calibrate_config_is_complete(config)
                    res_text, res_title = format_calibrate_resistance_cell(config)
                    rows.append(
                        html.Tr([
                            html.Td(str(row_num), className="text-center"),
                            html.Td(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                   className="small text-muted"),
                            html.Td(
                                html.Span(res_text, title=res_title, className="small"),
                            ),
                            html.Td(format_freq_label_from_khz(freq), className="fw-bold"),
                            html.Td(format_calibrate_gain_cell(config), className="small"),
                            html.Td([
                                html.Span(
                                    "✓" if complete else "○",
                                    className="text-success" if complete else "text-warning",
                                    title=format_calibrate_steps_cell(config),
                                )
                            ], className="text-center"),
                            html.Td([
                                html.Button([
                                    html.I(className="fas fa-info-circle")
                                ], className="btn btn-sm btn-outline-info me-1",
                                   title=format_calibrate_steps_cell(config)),
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
            
            if rows:
                return _finish(rows)

            if _looks_like_empty_calibration_noise(calibrations_raw):
                return _finish([
                    html.Tr([
                        html.Td(colSpan="7", className="text-center text-muted", children=[
                            html.I(className="fas fa-info-circle me-2"),
                            "No hay calibraciones almacenadas en el dispositivo."
                        ])
                    ])
                ], "text-muted", "Sin calibraciones en flash.")

            return _finish([
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
            ], "text-warning", "Formato de respuesta no reconocido.")

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            return _finish([
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
            ], "text-danger", f"Error: {e}")

    @app.callback(
        Output('cal-delete-modal', 'style'),
        Input('btn-delete-calibrations', 'n_clicks'),
        Input('cal-delete-modal-close', 'n_clicks'),
        Input('cal-delete-modal-cancel', 'n_clicks'),
        Input('cal-delete-modal-confirm', 'n_clicks'),
        prevent_initial_call=True,
    )
    def toggle_cal_delete_modal(delete_clicks, close_clicks, cancel_clicks, confirm_clicks):
        """Abre/cierra el modal de confirmación de borrado."""
        triggered = ctx.triggered_id if ctx.triggered else None
        if triggered == 'btn-delete-calibrations':
            return {
                'display': 'flex',
                'position': 'fixed',
                'top': '0',
                'left': '0',
                'width': '100%',
                'height': '100%',
                'zIndex': '1050',
                'backgroundColor': 'rgba(0,0,0,0.5)',
                'alignItems': 'center',
                'justifyContent': 'center',
            }
        return {'display': 'none'}

    app.clientside_callback(
        """
        function(viewClicks) {
            if (!viewClicks) {
                return window.dash_clientside.no_update;
            }
            var panel = document.getElementById('calibrations-panel');
            if (panel) {
                panel.scrollIntoView({behavior: 'smooth', block: 'start'});
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output('cal-saved-calibrations', 'data'),
        Input('btn-view-calibrations', 'n_clicks'),
        prevent_initial_call=True,
    )


def register_calibration_page(app):
    """Registra la página de calibración"""
    register_calibration_callbacks(app)
