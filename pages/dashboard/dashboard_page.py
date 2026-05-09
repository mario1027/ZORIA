"""
ZORIA Dashboard - Analizador de Impedancia
Refactorizado 100% según patrón dash-plantilla VOLT Bootstrap 5
"""
from dash import html, Input, Output, State, ctx, register_page, dcc, dash_table
import dash
from dash.exceptions import PreventUpdate
from dash import no_update as NOUPDATE
from dash_spa.components import Alert, SPA_ALERT, Notyf, SPA_NOTIFY
import plotly.graph_objs as go
import numpy as np
from datetime import datetime
import threading
import queue
import time
import serial.tools.list_ports
import logging
import base64
import io
import pandas as pd

from lib import (
    ADMX2001, DisplayMode, SweepType, SweepScale, ImpedanceRange,
    ValidationError, ConnectionError as ADMX2001ConnectionError
)
from lib.utils import (
    clean_response_line,
    get_preferred_usb_serial_ports,
    is_likely_admx_port,
)

# Importar componentes comunes compartidos
from pages.common.sidebar import sideBar
from pages.common.mobile_nav import mobileNavBar
from pages.common.footer import footer
from pages.common.floating_terminal_button import floating_terminal_button

# Importar estado global del dispositivo
from lib.device_state import device_state

# ==================== CONFIGURACIÓN GLOBAL ====================

# Logger
logger = logging.getLogger(__name__)

# Timestamp de inicio de la aplicación (para evitar errores prematuros)
APP_START_TIME = time.time()

# Variables globales para el estado del sistema
# NOTA: 'device' e 'is_connected' locales están obsoletas - usar device_state global
# device = None  # OBSOLETO - usar device_state.device
# is_connected = threading.Event()  # OBSOLETO - usar device_state.is_connected
measurement_thread = None
stop_measurement = threading.Event()
sweep_thread = None
stop_sweep = threading.Event()

# Colas para comunicación entre threads
measurement_queue = queue.Queue()
sweep_queue = queue.Queue()

# Datos globales
measurement_data = {'timestamp': [], 'value1': [], 'value2': []}
sweep_data = {'param': [], 'z_real': [], 'z_imag': [], 'z_mag': [], 'phase': []}

# Estado del progreso del sweep
sweep_progress = 0
sweep_completed_successfully = False

# Variables para detectar sweeps "abandonados" (sin actualizaciones)
last_sweep_point_count = 0
intervals_without_new_points = 0
MAX_INTERVALS_WITHOUT_DATA = 300  # 30 segundos @ 100ms por interval

# Configuración de medición
measurement_config = {
    'display_mode': 6,
    'frequency': 1000,
    'average': 1,
    'mdelay': -1,
    'tdelay': 0,
    'magnitude': 'auto'
}

# Función helper para prints seguros (maneja BrokenPipeError)
def safe_print(message):
    """Imprime un mensaje manejando errores de pipe roto"""
    try:
        print(message)
    except (BrokenPipeError, IOError):
        pass  # Ignorar si el terminal está cerrado

def detect_admx2001_ports():
    """Detecta puertos que podrían ser el dispositivo ADMX2001"""
    try:
        return [
            port for port in get_preferred_usb_serial_ports()
            if is_likely_admx_port(port)
        ]
    except Exception as e:
        print(f"Error detectando puertos ADMX2001: {e}")
        return []

def create_empty_figure(title="Sin datos", theme='dark'):
    """Crea una figura vacía con mensaje"""
    # Definir colores basados en el tema
    if theme == 'light':
        bg_color = '#FFFFFF'
        text_color = '#333333'
        annotation_color = '#333333'
    else:  # dark theme
        bg_color = '#0D213A'
        text_color = '#6495ED'
        annotation_color = '#6495ED'
    
    fig = go.Figure()
    fig.update_layout(
        title=title,
        annotations=[dict(
            text="No hay datos disponibles",
            showarrow=False,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            font=dict(size=16, color=annotation_color)
        )],
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=text_color, size=14, family="Arial, sans-serif"),
        title_font=dict(color=text_color, size=18)
    )
    return fig

def create_bode_plot(param, z_mag, phase, negative_phase=False, theme='dark'):
    """Crea el diagrama de Bode"""
    print(f"create_bode_plot llamado con: param={len(param) if param else 0}, z_mag={len(z_mag) if z_mag else 0}, phase={len(phase) if phase else 0}, negative_phase={negative_phase}, theme={theme}")
    
    # Definir colores basados en el tema
    if theme == 'light':
        mag_color = '#00BFFF'  # Cyan más oscuro para light theme
        phase_color = '#FF1493'  # Pink más oscuro para light theme
        bg_color = '#FFFFFF'
        grid_color = '#E0E0E0'
        text_color = '#333333'
    else:  # dark theme
        mag_color = '#00FFFF'  # Cyan brillante para dark theme
        phase_color = '#FF69B4'  # Pink para dark theme
        bg_color = '#0D213A'
        grid_color = '#1F3D68'
        text_color = '#6495ED'
    
    if not param or not z_mag or len(param) == 0 or len(z_mag) == 0:
        print("No hay datos suficientes para crear diagrama de Bode")
        return create_empty_figure("Diagrama de Bode - Sin datos", theme)

    print(f"Primeros valores param: {param[:3] if len(param) > 3 else param}")
    print(f"Primeros valores z_mag: {z_mag[:3] if len(z_mag) > 3 else z_mag}")
    print(f"Primeros valores phase: {phase[:3] if phase and len(phase) > 3 else phase}")

    fig = go.Figure()

    # Si todos los puntos pertenecen a una misma frecuencia fija, tratarlo como
    # una secuencia de triggers/mediciones repetidas para que el eje X sea útil.
    fixed_frequency_mode = False
    fixed_frequency_hz = None
    x_values = param
    xaxis_title = "Frecuencia (Hz)"
    xaxis_type = "log"

    if len(param) > 1:
        try:
            first_freq = float(param[0])
            fixed_frequency_mode = all(abs(float(p) - first_freq) < 1e-9 for p in param)
            if fixed_frequency_mode:
                fixed_frequency_hz = first_freq
                x_values = list(range(1, len(param) + 1))
                xaxis_title = "Trigger #"
                xaxis_type = "linear"
        except Exception:
            fixed_frequency_mode = False

    # Magnitud - asegurar valores positivos para log
    mag_db = [20 * np.log10(max(z, 1e-12)) for z in z_mag]
    print(f"Magnitud en dB: primeros valores {mag_db[:3]}")

    mag_hover = '<b>Frecuencia:</b> %{x:.2f} Hz<br><b>|Z|:</b> %{y:.2f} dB<extra></extra>'
    phase_hover = '<b>Frecuencia:</b> %{x:.2f} Hz<br><b>Fase:</b> %{y:.2f}°<extra></extra>'
    if fixed_frequency_mode and fixed_frequency_hz is not None:
        mag_hover = (
            f'<b>Trigger:</b> %{{x}}<br><b>Frecuencia fija:</b> {fixed_frequency_hz:.2f} Hz'
            '<br><b>|Z|:</b> %{y:.2f} dB<extra></extra>'
        )
        phase_hover = (
            f'<b>Trigger:</b> %{{x}}<br><b>Frecuencia fija:</b> {fixed_frequency_hz:.2f} Hz'
            '<br><b>Fase:</b> %{y:.2f}°<extra></extra>'
        )

    fig.add_trace(go.Scatter(
        x=x_values,
        y=mag_db,  # Convertir a dB
        mode='lines+markers',
        name='|Z| (dB)',
        line=dict(color=mag_color, width=2),
        marker=dict(size=4, color=mag_color),
        yaxis="y1",
        hovertemplate=mag_hover
    ))

    # Fase - aplicar signo según configuración del checkbox
    if phase and len(phase) > 0:
        # Si negative_phase=True, usar fase negativa; si False, usar fase positiva
        phase_deg = [-np.degrees(p) if negative_phase else np.degrees(p) for p in phase]
        print(f"Fase ({'negativa' if negative_phase else 'positiva'}): primeros valores {phase_deg[:3]}")
        fig.add_trace(go.Scatter(
            x=x_values,
            y=phase_deg,
            mode='lines+markers',
            name='Fase (°)',
            line=dict(color=phase_color, width=2),
            marker=dict(size=4, color=phase_color),
            yaxis="y2",
            hovertemplate=phase_hover
        ))

    fig.update_layout(
        title=f"Diagrama de Bode",
        xaxis=dict(
            title=xaxis_title,
            type=xaxis_type,
            autorange=True,
            showgrid=True,
            gridcolor=grid_color,
            linecolor=text_color,
            tickcolor=text_color,
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color),
            # Etiquetas legibles para el rango completo 0.2 Hz–10 MHz
            tickvals=[0.2, 1, 10, 100, 1e3, 1e4, 1e5, 1e6, 1e7] if xaxis_type == "log" else None,
            ticktext=["0.2", "1", "10", "100", "1k", "10k", "100k", "1M", "10M"] if xaxis_type == "log" else None,
        ),
        yaxis=dict(
            title="|Z| (dB)",
            color=mag_color,
            autorange=True,
            showgrid=True,
            gridcolor=grid_color,
            linecolor=text_color,
            tickcolor=text_color,
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color)
        ),
        yaxis2=dict(
            title="Fase (°)",
            color=phase_color,
            overlaying="y",
            side="right",
            autorange=True,
            showgrid=False,
            linecolor=text_color,
            tickcolor=text_color,
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color)
        ),
        height=500,
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=text_color, size=14, family="Arial, sans-serif"),
        title_font=dict(color=text_color, size=18),
        showlegend=True,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=bg_color,
            bordercolor=text_color,
            font=dict(color=text_color)
        )
    )

    return fig

def create_nyquist_plot(z_real, z_imag, freq=None, theme='dark'):
    """Crea el diagrama de Nyquist"""
    print(f"create_nyquist_plot llamado con: z_real={len(z_real) if z_real else 0}, z_imag={len(z_imag) if z_imag else 0}, freq={len(freq) if freq else 0}, theme={theme}")
    
    # Definir colores basados en el tema
    if theme == 'light':
        nyquist_color = '#FF8C00'  # Orange más oscuro para light theme
        bg_color = '#FFFFFF'
        grid_color = '#E0E0E0'
        text_color = '#333333'
    else:  # dark theme
        nyquist_color = '#FFA500'  # Orange para dark theme
        bg_color = '#0D213A'
        grid_color = '#1F3D68'
        text_color = '#6495ED'
    
    if not z_real or not z_imag or len(z_real) == 0 or len(z_imag) == 0:
        print("No hay datos suficientes para crear diagrama de Nyquist")
        return create_empty_figure("Diagrama de Nyquist - Sin datos", theme)

    print(f"Primeros valores z_real: {z_real[:3] if len(z_real) > 3 else z_real}")
    print(f"Primeros valores z_imag: {z_imag[:3] if len(z_imag) > 3 else z_imag}")

    fig = go.Figure()

    # Preparar datos para el gráfico - FORMATO ESTÁNDAR DE NYQUIST
    # Eje X = Z' (parte real) - horizontal
    # Eje Y = -Z'' (parte imaginaria negativa) - vertical
    x_data = z_real  # Z' en eje X (horizontal)
    y_data = [-z for z in z_imag]  # -Z'' en eje Y (vertical)
    print(f"Datos X (z_real): {x_data[:3]}...")
    print(f"Datos Y (-z_imag): {y_data[:3]}...")

    # Crear colormap basado en frecuencia si está disponible
    if freq and len(freq) == len(z_real):
        # Usar escala logarítmica de frecuencia para el color
        import numpy as np
        freq_log = np.log10(freq)
        
        # Crear texto personalizado para hover
        hover_text = [
            f'Frecuencia: {f:.2f} Hz<br>Z\': {zr:.2f} Ω<br>-Z\'\': {-zi:.2f} Ω'
            for f, zr, zi in zip(freq, z_real, z_imag)
        ]
        
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines+markers',
            name='Impedancia',
            line=dict(width=2),
            marker=dict(
                size=8,
                color=freq_log,  # Color basado en log(frecuencia)
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(
                    title="log₁₀(f) [Hz]",
                    thickness=15,
                    len=0.7
                )
            ),
            text=hover_text,
            hovertemplate='%{text}<extra></extra>'
        ))
    else:
        # Sin información de frecuencia, usar colores fijos
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines+markers',
            name='Impedancia',
            line=dict(color=nyquist_color, width=2),
            marker=dict(size=6, color=nyquist_color),
            hovertemplate='Z\': %{x:.2f} Ω<br>-Z\'\': %{y:.2f} Ω<extra></extra>'
        ))

    fig.update_layout(
        title=f"Diagrama de Nyquist",
        xaxis=dict(
            title="Z' (Ω)",
            showgrid=True,
            zeroline=True,
            autorange=True,
            gridcolor=grid_color,
            linecolor=text_color,
            tickcolor=text_color,
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color)
        ),
        yaxis=dict(
            title="-Z'' (Ω)",
            showgrid=True,
            zeroline=True,
            autorange=True,
            gridcolor=grid_color,
            linecolor=text_color,
            tickcolor=text_color,
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color)
        ),
        height=500,
        width=None,
        showlegend=True,
        autosize=True,
        margin=dict(l=60, r=60, t=60, b=60),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=text_color, size=14, family="Arial, sans-serif"),
        title_font=dict(color=text_color, size=18),
        hovermode="closest",
        hoverlabel=dict(
            bgcolor=bg_color,
            bordercolor=text_color,
            font=dict(color=text_color)
        )
    )

    print(f"Nyquist plot creado con {len(fig.data)} traces")
    return fig


def _get_trigger_plot_palette(theme='dark'):
    """Paleta de colores para superponer múltiples barridos trigger."""
    if theme == 'light':
        return ['#2563eb', '#dc2626', '#059669', '#d97706', '#7c3aed', '#0891b2']
    return ['#60a5fa', '#f87171', '#34d399', '#fbbf24', '#a78bfa', '#22d3ee']


def create_bode_plot_from_dataset(dataset, negative_phase=False, theme='dark'):
    """Genera Bode desde el store, soportando overlays para Trigger 1..N."""
    if not dataset or len(dataset.get('param', [])) == 0:
        return create_empty_figure("Diagrama de Bode - Sin datos", theme)

    runs = dataset.get('runs') or []
    if len(runs) <= 1:
        return create_bode_plot(dataset['param'], dataset['z_mag'], dataset['phase'], negative_phase, theme)

    if theme == 'light':
        bg_color = '#FFFFFF'
        grid_color = '#E0E0E0'
        text_color = '#333333'
    else:
        bg_color = '#0D213A'
        grid_color = '#1F3D68'
        text_color = '#6495ED'

    colors = _get_trigger_plot_palette(theme)
    fig = go.Figure()

    for idx, run in enumerate(runs, start=1):
        freq = run.get('param', [])
        z_mag = run.get('z_mag', [])
        phase = run.get('phase', [])
        if not freq or not z_mag:
            continue

        color = colors[(idx - 1) % len(colors)]
        mag_db = [20 * np.log10(max(z, 1e-12)) for z in z_mag]
        phase_deg = [-np.degrees(p) if negative_phase else np.degrees(p) for p in phase]
        run_label = f"Trigger {run.get('run_index', idx)}"

        fig.add_trace(go.Scatter(
            x=freq,
            y=mag_db,
            mode='lines+markers',
            name=f"{run_label} |Z|",
            line=dict(color=color, width=2),
            marker=dict(size=4, color=color),
            yaxis='y1',
            legendgroup=run_label,
            hovertemplate=f'<b>{run_label}</b><br><b>Frecuencia:</b> %{{x:.2f}} Hz<br><b>|Z|:</b> %{{y:.2f}} dB<extra></extra>'
        ))

        if phase:
            fig.add_trace(go.Scatter(
                x=freq,
                y=phase_deg,
                mode='lines+markers',
                name=f"{run_label} fase",
                line=dict(color=color, width=1.5, dash='dot'),
                marker=dict(size=3, color=color),
                yaxis='y2',
                legendgroup=run_label,
                hovertemplate=f'<b>{run_label}</b><br><b>Frecuencia:</b> %{{x:.2f}} Hz<br><b>Fase:</b> %{{y:.2f}}°<extra></extra>'
            ))

    fig.update_layout(
        title="Diagrama de Bode",
        xaxis=dict(
            title="Frecuencia (Hz)",
            type="log",
            autorange=True,
            showgrid=True,
            gridcolor=grid_color,
            linecolor=text_color,
            tickcolor=text_color,
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color),
            tickvals=[0.2, 1, 10, 100, 1e3, 1e4, 1e5, 1e6, 1e7],
            ticktext=["0.2", "1", "10", "100", "1k", "10k", "100k", "1M", "10M"],
        ),
        yaxis=dict(
            title="|Z| (dB)",
            autorange=True,
            showgrid=True,
            gridcolor=grid_color,
            linecolor=text_color,
            tickcolor=text_color,
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color)
        ),
        yaxis2=dict(
            title="Fase (°)",
            overlaying="y",
            side="right",
            autorange=True,
            showgrid=False,
            linecolor=text_color,
            tickcolor=text_color,
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color)
        ),
        height=500,
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=text_color, size=14, family="Arial, sans-serif"),
        title_font=dict(color=text_color, size=18),
        showlegend=True,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=bg_color,
            bordercolor=text_color,
            font=dict(color=text_color)
        )
    )
    return fig


def create_nyquist_plot_from_dataset(dataset, theme='dark'):
    """Genera Nyquist desde el store, soportando overlays para Trigger 1..N."""
    if not dataset or len(dataset.get('param', [])) == 0:
        return create_empty_figure("Diagrama de Nyquist - Sin datos", theme)

    runs = dataset.get('runs') or []
    if len(runs) <= 1:
        return create_nyquist_plot(dataset['z_real'], dataset['z_imag'], dataset['param'], theme)

    if theme == 'light':
        bg_color = '#FFFFFF'
        grid_color = '#E0E0E0'
        text_color = '#333333'
    else:
        bg_color = '#0D213A'
        grid_color = '#1F3D68'
        text_color = '#6495ED'

    colors = _get_trigger_plot_palette(theme)
    fig = go.Figure()

    for idx, run in enumerate(runs, start=1):
        freq = run.get('param', [])
        z_real = run.get('z_real', [])
        z_imag = run.get('z_imag', [])
        if not z_real or not z_imag:
            continue

        color = colors[(idx - 1) % len(colors)]
        run_label = f"Trigger {run.get('run_index', idx)}"
        hover_text = [
            f'{run_label}<br>Frecuencia: {f:.2f} Hz<br>Z\': {zr:.2f} Ω<br>-Z\'\': {-zi:.2f} Ω'
            for f, zr, zi in zip(freq, z_real, z_imag)
        ]

        fig.add_trace(go.Scatter(
            x=z_real,
            y=[-z for z in z_imag],
            mode='lines+markers',
            name=run_label,
            line=dict(color=color, width=2),
            marker=dict(size=5, color=color),
            text=hover_text,
            hovertemplate='%{text}<extra></extra>'
        ))

    fig.update_layout(
        title="Diagrama de Nyquist",
        xaxis=dict(
            title="Z' (Ω)",
            showgrid=True,
            zeroline=True,
            autorange=True,
            gridcolor=grid_color,
            linecolor=text_color,
            tickcolor=text_color,
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color)
        ),
        yaxis=dict(
            title="-Z'' (Ω)",
            showgrid=True,
            zeroline=True,
            autorange=True,
            gridcolor=grid_color,
            linecolor=text_color,
            tickcolor=text_color,
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color)
        ),
        height=500,
        width=None,
        showlegend=True,
        autosize=True,
        margin=dict(l=60, r=60, t=60, b=60),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=text_color, size=14, family="Arial, sans-serif"),
        title_font=dict(color=text_color, size=18),
        hovermode="closest",
        hoverlabel=dict(
            bgcolor=bg_color,
            bordercolor=text_color,
            font=dict(color=text_color)
        )
    )
    return fig

# ==================== WORKERS ====================

def measurement_worker(config):
    """Worker para mediciones continuas"""
    global measurement_data

    try:
        display_mode = config['display_mode']
        frequency = config['frequency']
        mdelay = config['mdelay']
        tdelay = config['tdelay']
        magnitude = config['magnitude']

        while not stop_measurement.is_set():
            if device_state.device and device_state.is_connected:
                try:
                    # Configurar medición
                    device_state.device.set_display_mode(display_mode)
                    device_state.device.set_frequency(frequency)
                    if mdelay >= 0:
                        device_state.device.set_measurement_delay(mdelay)
                    if tdelay >= 0:
                        device_state.device.set_trigger_delay(tdelay)
                    if magnitude and magnitude != 'auto':
                        # Convertir a float si es string
                        mag_value = float(magnitude) if isinstance(magnitude, str) else magnitude
                        device_state.device.set_magnitude(mag_value)

                    # Realizar medición
                    measurement = device_state.device.measure()

                    # Procesar resultado
                    timestamp = datetime.now()
                    value1 = measurement[0] if len(measurement) > 0 else 0
                    value2 = measurement[1] if len(measurement) > 1 else 0

                    # Agregar a datos
                    measurement_data['timestamp'].append(timestamp)
                    measurement_data['value1'].append(value1)
                    measurement_data['value2'].append(value2)

                    # Mantener solo los últimos 100 puntos
                    if len(measurement_data['timestamp']) > 100:
                        measurement_data['timestamp'] = measurement_data['timestamp'][-100:]
                        measurement_data['value1'] = measurement_data['value1'][-100:]
                        measurement_data['value2'] = measurement_data['value2'][-100:]

                    # Enviar actualización
                    measurement_queue.put({
                        'timestamp': timestamp,
                        'value1': value1,
                        'value2': value2
                    })

                except Exception as e:
                    print(f"Error en medición: {e}")
                    measurement_queue.put({'error': True, 'message': str(e)})

            time.sleep(0.1)  # 100ms entre mediciones

    except Exception as e:
        print(f"Error en measurement worker: {e}")
        measurement_queue.put({'error': True, 'message': str(e)})

def sweep_worker(config):
    """Worker para barridos de frecuencia"""
    global sweep_data
    sweep_phase = 'init'

    # Adquirir lock para operaciones exclusivas con el dispositivo
    device_state._operation_lock.acquire()
    
    try:
        sweep_phase = 'config'
        # Extraer parámetros de la configuración recibida
        start = config['start']
        end = config['end']
        points = config['points']
        scale = config['scale']
        display_mode = config['display_mode']
        trigger_enabled = bool(config.get('trigger_enabled'))
        trigger_count_raw = config.get('trigger_count')
        trigger_count = int(trigger_count_raw) if trigger_count_raw is not None else int(points or 1)
        average = config.get('average', 1)
        mdelay = config['mdelay']
        tdelay = config['tdelay']
        magnitude = config.get('magnitude', 1.0)  # Valor por defecto 1.0V
        configured_magnitude = None
        total_stream_points = points * trigger_count if trigger_enabled else points

        # OPTIMIZACIÓN: evitar heredar delays lentos de operaciones previas (p.ej. calibración)
        # Si UI envía -1 (auto/no cambiar), usar 0 ms para barridos rápidos.
        effective_mdelay = 0 if mdelay is None or mdelay < 0 else mdelay
        effective_tdelay = 0 if tdelay is None or tdelay < 0 else tdelay
        effective_average = 1 if average is None or average < 1 else int(average)
        
        print(f"🔄 WORKER INICIADO - Configuración recibida:")
        print(f"   - Start: {start} Hz, End: {end} Hz")
        print(f"   - Puntos: {points}, Escala: {scale}")
        print(f"   - Trigger habilitado: {trigger_enabled}")
        print(f"   - Trigger count: {trigger_count}")
        print(f"   - Display Mode: {display_mode}, Average: {average} (efectivo {effective_average}), MDelay: {mdelay} (efectivo {effective_mdelay}), TDelay: {tdelay} (efectivo {effective_tdelay})")
        print(f"   - Magnitud: {magnitude} V")

        # Resetear datos
        global sweep_data
        sweep_data = {'param': [], 'z_real': [], 'z_imag': [], 'z_mag': [], 'phase': []}

        # === INICIAR STREAMING DEL SWEEP ===
        # Limpiar buffer de streaming antes de iniciar
        device_state.clear_sweep_buffer()
        device_state.start_sweep_streaming(total_stream_points)
        print(f"📡 Streaming iniciado para {total_stream_points} puntos - buffer limpio")

        # Configurar dispositivo para barrido
        if device_state.device:
            from lib.enums import SweepType, SweepScale
            import numpy as np

            # Configurar display mode PRIMERO (modo 6 = R, X coordenadas rectangulares)
            try:
                # Convertir display_mode a entero si viene como string
                display_mode_int = int(display_mode) if isinstance(display_mode, str) else display_mode
                print(f"🔧 Configurando display mode: {display_mode_int} (R-X)")
                device_state.device.set_display_mode(display_mode_int)
            except Exception as e:
                print(f"⚠️ Error configurando display mode: {e}")

            # Forzar autorange para minimizar riesgo de saturación durante sweep
            try:
                print("🔧 Habilitando autorange (setgain auto)")
                device_state.device.set_gain_auto()
            except Exception as e:
                print(f"⚠️ Error habilitando autorange: {e}")

            # Configurar average para velocidad de sweep (evita heredar average=200 de calibración)
            try:
                print(f"🔧 Configurando average efectivo: {effective_average}")
                device_state.device.send_command(f"average {effective_average}")
            except Exception as e:
                print(f"⚠️ Error configurando average: {e}")

            # Configurar delays ANTES del sweep
            try:
                print(f"🔧 Configurando measurement delay efectivo: {effective_mdelay} ms")
                device_state.device.set_measurement_delay(effective_mdelay)
                time.sleep(0.0005)  # Esperar 0.5ms para estabilización del delay
                print(f"🔧 Configurando trigger delay efectivo: {effective_tdelay} ms")
                device_state.device.set_trigger_delay(effective_tdelay)
            except Exception as e:
                print(f"⚠️ Error configurando delays: {e}")

            # Configurar magnitud ANTES del sweep
            if magnitude and magnitude != 'auto':
                try:
                    configured_magnitude = float(magnitude) if isinstance(magnitude, str) else float(magnitude)
                    print(f"🔧 Configurando magnitud: {configured_magnitude} V")
                    device_state.device.set_magnitude(configured_magnitude)
                except Exception as e:
                    print(f"⚠️ Error configurando magnitud: {e}")

            # Convertir escala
            sweep_scale = SweepScale.LOG if scale == 'log' else SweepScale.LINEAR
            def execute_frequency_sweep_once(run_index=1, total_runs=1):
                nonlocal configured_magnitude, sweep_phase

                from lib.utils import estimate_sweep_time, max_points_per_segment

                # SEGMENTACIÓN DINÁMICA: el tamaño máximo de segmento depende de la
                # frecuencia más baja del rango para evitar timeouts a bajas frecuencias.
                BASE_MAX_SEG = max_points_per_segment(start)

                if points <= BASE_MAX_SEG:
                    print(f"📊 Barrido simple: {points} puntos")
                    segments = [(start, end, points)]
                else:
                    num_segments = (points + BASE_MAX_SEG - 1) // BASE_MAX_SEG
                    print(f"📊 Barrido segmentado: {points} pts → {num_segments} segmentos (máx {BASE_MAX_SEG} pts/seg)")

                    if scale == 'log':
                        all_freqs = np.logspace(np.log10(start), np.log10(end), points)
                    else:
                        all_freqs = np.linspace(start, end, points)

                    segments = []
                    for i in range(num_segments):
                        seg_start_idx = i * BASE_MAX_SEG
                        seg_end_idx   = min((i + 1) * BASE_MAX_SEG, points)
                        seg_points    = seg_end_idx - seg_start_idx
                        seg_start_freq = float(all_freqs[seg_start_idx])
                        seg_end_freq   = float(all_freqs[seg_end_idx - 1])
                        segments.append((seg_start_freq, seg_end_freq, seg_points))
                        print(f"  Seg {i+1}/{num_segments}: {seg_start_freq:.4g} Hz – {seg_end_freq:.4g} Hz ({seg_points} pts)")

                all_results = []
                for seg_idx, (seg_start, seg_end, seg_points) in enumerate(segments):
                    sweep_phase = 'acquisition'
                    if stop_sweep.is_set():
                        raise RuntimeError("Sweep cancelado por el usuario")

                    if total_runs > 1:
                        print(f"🔁 Trigger barrido {run_index}/{total_runs}")
                    if len(segments) > 1:
                        print(f"🔄 Ejecutando segmento {seg_idx+1}/{len(segments)}: {seg_start:.1f}-{seg_end:.1f} Hz, {seg_points} puntos")

                    print(f"📋 CONFIGURANDO SWEEP:")
                    print(f"   Tipo: FREQUENCY")
                    print(f"   Start: {seg_start:.1f} Hz ({seg_start/1000:.3f} kHz)")
                    print(f"   End: {seg_end:.1f} Hz ({seg_end/1000:.3f} kHz)")
                    print(f"   Scale: {sweep_scale}")
                    print(f"   Count: {seg_points} puntos ← IMPORTANTE")

                    device_state.device.configure_sweep(
                        SweepType.FREQUENCY,
                        seg_start / 1000,
                        seg_end / 1000,
                        sweep_scale,
                        seg_points
                    )

                    print(f"✅ Sweep configurado - esperando {seg_points} puntos")

                    # Timeout basado en tiempo real de adquisición por frecuencia
                    seg_time = estimate_sweep_time(
                        seg_start, seg_end, seg_points,
                        scale=scale,
                        average=effective_average,
                        mdelay=effective_mdelay,
                        tdelay=effective_tdelay
                    )
                    # Margen de seguridad: 3× el tiempo estimado + 60 s overhead mínimo
                    sweep_timeout = max(120, int(seg_time['total_seconds'] * 3) + 60)
                    print(f"  ⏱ Timeout segmento: {sweep_timeout}s  "
                          f"(estimado={seg_time['human_readable']}, "
                          f"cuello botella={seg_time['bottleneck_freq']:.4g} Hz "
                          f"→ {seg_time['bottleneck_ms']:.0f} ms/pto)")

                    segment_start_point = sum(seg[2] for seg in segments[:seg_idx]) + ((run_index - 1) * points)

                    point_counter = [0]
                    def process_point_realtime(point):
                        try:
                            freq_hz = point['sweep_value']
                            measurement = point['measurement']

                            if len(measurement) >= 2:
                                z_real = measurement[0]
                                z_imag = measurement[1]
                                z_mag = np.sqrt(z_real**2 + z_imag**2)
                                phase = np.arctan2(z_imag, z_real)
                                device_state.add_sweep_point(freq_hz, z_real, z_imag, z_mag, phase)

                                point_counter[0] += 1
                                if point_counter[0] % 10 == 0 or point_counter[0] == 1:
                                    print(f"[Real-time Callback] ✅ Punto {point_counter[0]} procesado y enviado al buffer")
                        except Exception as e:
                            print(f"⚠️ Error procesando punto en tiempo real: {e}")

                    import time
                    import threading

                    segment_results = None
                    acquisition_complete = threading.Event()
                    segment_exception = [None]

                    def acquire_segment():
                        nonlocal segment_results
                        try:
                            segment_results = device_state.device.perform_sweep(
                                timeout=sweep_timeout,
                                point_callback=process_point_realtime
                            )
                        except Exception as e:
                            segment_exception[0] = e
                        finally:
                            acquisition_complete.set()

                    acq_thread = threading.Thread(target=acquire_segment, daemon=True)
                    acq_thread.start()
                    acq_thread.join()

                    if segment_exception[0] is not None:
                        error_text = str(segment_exception[0]).lower()
                        can_retry = (configured_magnitude is not None and configured_magnitude > 0.01)
                        is_saturation_error = ('saturat' in error_text) or ('measurement failed' in error_text)

                        if is_saturation_error and can_retry:
                            retry_magnitude = max(0.01, configured_magnitude * 0.5)
                            print(f"⚠️ Saturación detectada en segmento {seg_idx+1}. Reintentando con magnitud {configured_magnitude}V → {retry_magnitude}V")
                            configured_magnitude = retry_magnitude
                            try:
                                device_state.device.set_gain_auto()
                                device_state.device.set_magnitude(configured_magnitude)
                            except Exception as e:
                                print(f"⚠️ Error aplicando recuperación por saturación: {e}")

                            device_state.device.configure_sweep(
                                SweepType.FREQUENCY,
                                seg_start / 1000,
                                seg_end / 1000,
                                sweep_scale,
                                seg_points
                            )

                            segment_results = device_state.device.perform_sweep(
                                timeout=sweep_timeout,
                                point_callback=process_point_realtime
                            )
                        else:
                            raise segment_exception[0]

                    if segment_results:
                        all_results.extend(segment_results)
                        print(f"  ✅ Segmento completado: {len(segment_results)} puntos obtenidos")
                        if len(segment_results) != seg_points:
                            raise RuntimeError(
                                f"Sweep incompleto en segmento {seg_idx+1}: esperados {seg_points}, recibidos {len(segment_results)}"
                            )

                        segment_end_point = segment_start_point + seg_points
                        final_progress_pct = int((segment_end_point / total_stream_points) * 100)
                        print(f"  📊 Progreso automático vía streaming: {final_progress_pct}% ({segment_end_point}/{total_stream_points} puntos)")
                    else:
                        print(f"  ⚠️ Segmento sin resultados")

                return all_results

            batch_runs = []
            if trigger_enabled:
                if trigger_count < 1:
                    raise ValueError("El número de triggers debe ser al menos 1")

                print(f"🎯 MODO TRIGGER: {trigger_count} barridos usando Start={start} Hz, End={end} Hz, Points={points}")
                for run_index in range(1, trigger_count + 1):
                    if stop_sweep.is_set():
                        print("🛑 Trigger cancelado por el usuario")
                        device_state.end_sweep_streaming()
                        return

                    run_results = execute_frequency_sweep_once(run_index, trigger_count)
                    run_data = {'param': [], 'z_real': [], 'z_imag': [], 'z_mag': [], 'phase': []}
                    for point in run_results:
                        freq_hz = point['sweep_value']
                        measurement = point['measurement']
                        if len(measurement) >= 2:
                            z_real = measurement[0]
                            z_imag = measurement[1]
                            z_mag = np.sqrt(z_real**2 + z_imag**2)
                            phase = np.arctan2(z_imag, z_real)
                            run_data['param'].append(freq_hz)
                            run_data['z_real'].append(z_real)
                            run_data['z_imag'].append(z_imag)
                            run_data['z_mag'].append(z_mag)
                            run_data['phase'].append(phase)

                    batch_runs.append({
                        'run_index': run_index,
                        'param': run_data['param'].copy(),
                        'z_real': run_data['z_real'].copy(),
                        'z_imag': run_data['z_imag'].copy(),
                        'z_mag': run_data['z_mag'].copy(),
                        'phase': run_data['phase'].copy(),
                    })
                    print(f"[Trigger Sweep] ✅ Barrido {run_index}/{trigger_count} guardado con {len(run_data['param'])} puntos")

                results = batch_runs[-1] if batch_runs else {'param': [], 'z_real': [], 'z_imag': [], 'z_mag': [], 'phase': []}
                print(f"✅ Trigger completo: {len(batch_runs)} barridos obtenidos")
            else:
                results = execute_frequency_sweep_once()
                print(f"✅ Barrido completo: {len(results)} puntos totales obtenidos")

            # Consolidar resultados finales en sweep_data (ya se enviaron al streaming en tiempo real)
            sweep_phase = 'postprocess'
            print(f"📊 Consolidando {'trigger' if trigger_enabled else 'sweep'} en datos finales...")
            try:
                if trigger_enabled:
                    if batch_runs:
                        last_run = batch_runs[-1]
                        sweep_data = {
                            'param': last_run['param'].copy(),
                            'z_real': last_run['z_real'].copy(),
                            'z_imag': last_run['z_imag'].copy(),
                            'z_mag': last_run['z_mag'].copy(),
                            'phase': last_run['phase'].copy(),
                            'runs': [dict(run) for run in batch_runs],
                            'trigger_enabled': True,
                        }
                        print(f"✅ Consolidación trigger completada: {len(batch_runs)} barridos, {len(sweep_data['param'])} puntos en el último barrido")
                    else:
                        sweep_data = {'param': [], 'z_real': [], 'z_imag': [], 'z_mag': [], 'phase': [], 'runs': [], 'trigger_enabled': True}
                else:
                    for i, point in enumerate(results):
                        freq_hz = point['sweep_value']
                        measurement = point['measurement']

                        if len(measurement) >= 2:
                            z_real = measurement[0]
                            z_imag = measurement[1]
                            z_mag = np.sqrt(z_real**2 + z_imag**2)
                            phase = np.arctan2(z_imag, z_real)

                            sweep_data['param'].append(freq_hz)
                            sweep_data['z_real'].append(z_real)
                            sweep_data['z_imag'].append(z_imag)
                            sweep_data['z_mag'].append(z_mag)
                            sweep_data['phase'].append(phase)

                    print(f"✅ Consolidación completada: {len(sweep_data['param'])} puntos finales")

                print(f"📊 Progreso final confirmado por streaming: 100% ({total_stream_points}/{total_stream_points} puntos)")
                
            except Exception as e:
                print(f"❌ ERROR en procesamiento: {e}")
                import traceback
                traceback.print_exc()
                sweep_queue.put({'error': True, 'message': f'Error procesando datos: {str(e)}'})
                return        # Barrido completado
        final_points = len(sweep_data['param'])
        print(f"WORKER: Barrido completado exitosamente con {final_points} puntos - enviando mensaje completed")
        
        # === FINALIZAR STREAMING ===
        device_state.end_sweep_streaming()
        print(f"📡 Streaming finalizado")
        
        sweep_queue.put({
            'completed': True,
            'points': final_points,
            'mode': 'trigger' if trigger_enabled else 'sweep',
            'runs': trigger_count if trigger_enabled else 1,
        })
        print(f"WORKER: Mensaje completed enviado a la cola")

    except Exception as e:
        print(f"WORKER ERROR [{sweep_phase}]: Error en sweep worker: {e}")
        import traceback
        traceback.print_exc()
        sweep_queue.put({'error': True, 'message': str(e), 'phase': sweep_phase})
    
    finally:
        # Liberar lock de operación
        device_state._operation_lock.release()
        print("🔓 Lock de operación liberado")

# ==================== COMPONENTES DE UI ====================
# NOTA: El terminal CLI ahora es global (ver terminal_component.py)
# Se eliminó command_prompt_modal() para evitar IDs duplicados

def connect_modal():
    """Ventana de conexión arrastrable tipo escritorio para ADMX2001"""
    MODAL_ID = 'connect-modal'
    
    return html.Div([
        # Ventana arrastrable tipo escritorio
        html.Div([
            # Header arrastrable
            html.Div([
                html.Div([
                    html.I(className="fas fa-microchip"),
                ], className="window-title-icon"),
                html.Span('', **{'data-i18n': 'dash.connect_modal_title'}, className="window-title-text"),
                
                html.Div([
                    html.Button(
                        html.I(className="fas fa-minus"),
                        id="connect-modal-minimize",
                        className="window-control-btn window-btn-minimize",
                        title="Minimizar"
                    ),
                    html.Button(
                        html.I(className="fas fa-times"),
                        id="connect-modal-close",
                        className="window-control-btn window-btn-close",
                        title="Cerrar"
                    ),
                ], className="window-controls")
            ], className="window-header", id="connect-modal-header"),
            
            # Body
            html.Div([
                # Estado y progreso
                html.Div([
                    html.Div([
                        html.Div(id="auto-connect-spinner", className="spinner-border spinner-border-sm text-primary me-2", style={'display': 'none'}),
                        html.Span(id="auto-connect-status", className="fw-semibold text-primary", children="Buscando dispositivo...")
                    ], className="d-flex align-items-center justify-content-center mb-3"),
                    
                    # Barra de progreso
                    html.Div([
                        html.Div(
                            id="auto-connect-progress",
                            className="progress-bar progress-bar-striped progress-bar-animated",
                            style={'width': '0%'}
                        )
                    ], className="progress mb-3", style={'height': '8px'}),
                    
                    # Puerto detectado
                    html.Div([
                        html.Small("", className="text-muted", **{'data-i18n': 'ui.port_prefix'}),
                        html.Code(id="detected-port", className="text-dark ms-1", children="--")
                    ], className="text-center mb-2"),
                    
                    # Resultado del test
                    html.Div(id="connection-test-result", className="text-center small mt-2")
                    
                ], className="p-3 bg-light rounded mb-3"),
                
                # Selector manual
                html.Div([
                    html.Label([html.I(className="fas fa-usb me-2"), html.Span('', **{'data-i18n': 'ui.manual_port'})], className="form-label fw-semibold small"),
                    dcc.Dropdown(
                        id='serial-ports',
                        options=[],
                        value='',
                        placeholder="Seleccionar puerto...",
                        className="mb-2"
                    ),
                    html.Button([
                        html.I(className="fas fa-sync-alt me-1"),
                        "Actualizar"
                    ], id="refresh-ports-btn", className="btn btn-sm btn-outline-secondary w-100 mb-3", n_clicks=0)
                ]),
                
                # Botones de acción
                html.Div([
                    html.Button([
                        html.I(className="fas fa-bolt me-2"),
                        "Conectar"
                    ], id="connect-btn", className="btn btn-success w-100 mb-2"),
                    html.Button([
                        html.I(className="fas fa-power-off me-2"),
                        "Desconectar"
                    ], id="disconnect-modal-btn", className="btn btn-outline-danger w-100 mb-2"),
                ], className='action-buttons')
                
            ], className='window-body p-3')
            
        ], id=MODAL_ID, className='draggable-window connection-window', style={'display': 'none', 'width': '380px', 'height': 'auto'})
    ])

def csv_modal():
    """Modal para cargar archivos CSV"""
    MODAL_ID = 'csv-modal'
    DISMISS = {"data-bs-dismiss": "modal"}
    
    return html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        # Botón close (esquina superior derecha)
                        html.Button(type='button', className='btn-close ms-auto', **DISMISS),
                        
                        # Título centrado
                        html.Div([
                            html.H1([
                                html.I(className="fas fa-file-csv me-2"),
                                "Cargar Datos CSV"
                            ], className='mb-0 h4')
                        ], className='text-center mb-4 mt-md-0'),
                        
                        # Contenido del modal
                        html.Div([
                            # Información sobre el formato CSV
                            html.Div([
                                html.H6("", className="fw-bold mb-3", **{'data-i18n': 'dash.csv_format_title'}),
                                html.P([
                                    html.I(className="fas fa-info-circle me-2"),
                                    "El archivo CSV debe contener las siguientes columnas:"
                                ], className="text-muted small mb-2"),
                                html.Ul([
                                    html.Li("", className="small", **{'data-i18n': 'dash.csv_col_freq'}),
                                    html.Li("", className="small", **{'data-i18n': 'dash.csv_col_zreal'}),
                                    html.Li("", className="small", **{'data-i18n': 'dash.csv_col_zimag'}),
                                    html.Li("", className="small", **{'data-i18n': 'dash.csv_col_zmag'}),
                                    html.Li("", className="small", **{'data-i18n': 'dash.csv_col_phase_rad'}),
                                    html.Li("", className="small", **{'data-i18n': 'dash.csv_col_phase_deg'})
                                ], className="text-muted small mb-3")
                            ], className="mb-4"),
                            
                            # Componente de subida de archivos
                            html.Div([
                                html.Label("", className="form-label fw-bold", **{'data-i18n': 'dash.csv_select_file'}),
                                dcc.Upload(
                                    id='upload-csv',
                                    children=html.Div([
                                        html.I(className="fas fa-cloud-upload-alt me-2"),
                                        'Arrastra y suelta o ',
                                        html.A('selecciona un archivo', className="text-primary")
                                    ]),
                                    style={
                                        'width': '100%',
                                        'height': '60px',
                                        'lineHeight': '60px',
                                        'borderWidth': '1px',
                                        'borderStyle': 'dashed',
                                        'borderRadius': '5px',
                                        'textAlign': 'center',
                                        'margin': '10px 0'
                                    },
                                    multiple=False
                                )
                            ], className="mb-4"),
                            
                            # Estado de carga
                            html.Div([
                                html.Span("", id="csv-upload-status", className="text-muted small")
                            ], className="mb-3"),
                            
                            # Lista de archivos CSV disponibles
                            html.Div([
                                html.H6("", className="fw-bold mb-3", **{'data-i18n': 'dash.csv_available'}),
                                html.Div(id="csv-files-list", className="small")
                            ], className="mb-4"),
                            
                            # Botones de acción
                            html.Div([
                                html.Button([
                                    html.I(className="fas fa-times me-2"),
                                    "Cancelar"
                                ], type="button", className="btn btn-secondary me-2", **DISMISS),
                                html.Button([
                                    html.I(className="fas fa-upload me-2"),
                                    "Cargar Datos"
                                ], id="confirm-load-csv-btn", className="btn btn-primary")
                            ], className='d-flex gap-2 flex-wrap')
                        ])
                    ], className='card p-3 p-lg-4')
                ], className='modal-body p-0')
            ], className='modal-content')
        ], className='modal-dialog modal-dialog-centered modal-lg d-flex align-items-center min-vh-100 w-100 mx-auto', role='document')
    ], className='modal fade', id=MODAL_ID, tabIndex='-1', role='dialog', **{"aria-hidden": "true"})

def sweep_config_card_compact():
    """Tarjeta de configuración de barrido - Layout horizontal compacto"""
    return html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.H5([
                        html.I(className="fas fa-sliders-h me-2"),
                        html.Span('', **{'data-i18n': 'dash.sweep_config'})
                    ], className="mb-0")
                ], className="card-header border-bottom border-gray-300 p-3"),
                html.Div([
                    # Primera fila: Frecuencias y puntos
                    html.Div([
                        html.Div([
                            html.Label(html.Span('', **{'data-i18n': 'dash.freq_start'}), className="form-label fw-bold small mb-1"),
                            dcc.Input(id='sweep-start', type='number', value=100, min=0.2, max=10000000, step='any',
                                      placeholder="ej: 0.2",
                                      className="form-control form-control-sm"),
                            html.Small("0.2 Hz – 10 MHz", className="form-text text-muted")
                        ], className="col-6 col-md-2"),
                        html.Div([
                            html.Label(html.Span('', **{'data-i18n': 'dash.freq_end'}), className="form-label fw-bold small mb-1"),
                            dcc.Input(id='sweep-end', type='number', value=100000, min=0.2, max=10000000, step='any',
                                      placeholder="ej: 10000000",
                                      className="form-control form-control-sm"),
                            html.Small("0.2 Hz – 10 MHz", className="form-text text-muted")
                        ], className="col-6 col-md-2"),
                        html.Div([
                            html.Label(html.Span('', **{'data-i18n': 'dash.points'}), className="form-label fw-bold small mb-1"),
                            dcc.Input(id='sweep-points', type='number', value=50, min=2, step=1,
                                      className="form-control form-control-sm"),
                            html.Small("Puntos por barrido", className="form-text text-muted")
                        ], className="col-6 col-md-2"),
                        html.Div([
                            html.Label(html.Span('', **{'data-i18n': 'dash.scale'}), className="form-label fw-bold small mb-1"),
                            dcc.Dropdown(id="sweep-scale", options=[
                                {'label': 'Log', 'value': 'log'},
                                {'label': 'Lineal', 'value': 'linear'}
                            ], value="log", clearable=False, className="mb-0")
                        ], className="col-6 col-md-2"),
                        html.Div([
                            html.Label(html.Span('', **{'data-i18n': 'dash.mode'}), className="form-label fw-bold small mb-1"),
                            dcc.Dropdown(id="sweep-display-mode", options=[
                                {'label': 'R-X', 'value': '6'},
                                {'label': 'Z-θ', 'value': '1'},
                                {'label': 'Y-θ', 'value': '2'}
                            ], value="6", clearable=False, className="mb-0")
                        ], className="col-6 col-md-2"),
                        html.Div([
                            html.Label(html.Span('', **{'data-i18n': 'dash.magnitude_v'}), className="form-label fw-bold small mb-1"),
                            dcc.Input(
                                id="sweep-magnitude", 
                                type='number', 
                                value=1.0,
                                min=0.001,
                                max=10,
                                step=0.001,
                                placeholder="Ej: 0.2, 1.0",
                                className="form-control form-control-sm"
                            )
                        ], className="col-6 col-md-2")
                    ], className="row g-2 mb-2"),
                    
                    # Segunda fila: Delays y botones
                    html.Div([
                        html.Div([
                            html.Label(html.Span('', **{'data-i18n': 'dash.mdelay'}), className="form-label fw-bold small mb-1"),
                            dcc.Input(id='sweep-mdelay', type='number', value=-1, placeholder="Auto", className="form-control form-control-sm")
                        ], className="col-6 col-md-2"),
                        html.Div([
                            html.Label(html.Span('', **{'data-i18n': 'dash.tdelay'}), className="form-label fw-bold small mb-1"),
                            dcc.Input(id='sweep-tdelay', type='number', value=0, className="form-control form-control-sm")
                        ], className="col-6 col-md-2"),
                        html.Div([
                            html.Label(html.Span('', **{'data-i18n': 'dash.options'}), className="form-label fw-bold small mb-1 d-block"),
                            dcc.Checklist(
                                id='phase-negative-check',
                                options=[{'label': html.Span('', **{'data-i18n': 'dash.phase_neg'}), 'value': 'negative'}],
                                value=[],
                                className="form-check-inline small",
                                inputClassName="form-check-input",
                                labelClassName="form-check-label"
                            )
                        ], className="col-6 col-md-2"),
                        # Botones de acción — bloque rediseñado con etiquetas visibles
                        html.Div([
                            html.Label(
                                html.Span('', **{'data-i18n': 'dash.actions'}),
                                className="form-label fw-bold small mb-1 d-block"
                            ),
                            html.Div([
                                # Iniciar barrido
                                html.Button([
                                    html.I(className="fas fa-play"),
                                    html.Span("Iniciar", className="btn-label ms-1")
                                ], id="sweep-btn",
                                   className="btn btn-primary sweep-action-btn",
                                   title="Iniciar barrido de frecuencias"),
                                # Detener
                                html.Button([
                                    html.I(className="fas fa-stop"),
                                    html.Span("Detener", className="btn-label ms-1")
                                ], id="cancel-sweep-btn",
                                   className="btn btn-danger sweep-action-btn",
                                   title="Detener barrido en curso"),
                                # Guardar CSV
                                html.Button([
                                    html.I(className="fas fa-floppy-disk"),
                                    html.Span("Guardar", className="btn-label ms-1")
                                ], id="save-csv-btn",
                                   className="btn btn-success sweep-action-btn",
                                   title="Exportar datos a CSV"),
                                # Importar CSV
                                html.Button([
                                    html.I(className="fas fa-folder-open"),
                                    html.Span("Cargar", className="btn-label ms-1")
                                ], id="load-csv-btn",
                                   className="btn btn-outline-secondary sweep-action-btn",
                                   title="Importar datos desde CSV"),
                            ], className="d-flex flex-wrap gap-2 align-items-center")
                        ], className="col-12 col-md-6"),
                    ], className="row g-2"),

                    # Trigger + estado del barrido
                    html.Div([
                        html.Div([
                            html.Label("Trigger", className="form-label fw-bold small mb-1 d-block"),
                            dcc.Checklist(
                                id='sweep-trigger-check',
                                options=[{'label': 'Modo trigger', 'value': 'trigger'}],
                                value=[],
                                className="form-check-inline small",
                                inputClassName="form-check-input",
                                labelClassName="form-check-label"
                            )
                        ], className="col-12 col-md-2"),
                        html.Div([
                            html.Label("Rango del Trigger", className="form-label fw-bold small mb-1"),
                            html.Small(
                                "Usa Start / End / Points del barrido actual.",
                                className="text-muted d-block mb-1"
                            ),
                            dcc.Input(
                                id='sweep-trigger-frequency',
                                type='number',
                                value=1000,
                                min=0.2,
                                max=10000000,
                                disabled=True,
                                className="form-control form-control-sm d-none"
                            )
                        ], className="col-6 col-md-2"),
                        html.Div([
                            html.Label("# Triggers", className="form-label fw-bold small mb-1"),
                            dcc.Input(
                                id='sweep-trigger-count',
                                type='number',
                                value=10,
                                min=1,
                                step=1,
                                disabled=True,
                                className="form-control form-control-sm"
                            )
                        ], className="col-6 col-md-2"),
                        html.Div([
                            html.Small(
                                "Si activa Trigger, se harán N mediciones consecutivas en una frecuencia fija y se guardará cada resultado.",
                                className="text-muted d-block pt-md-4"
                            )
                        ], className="col-12 col-md-8")
                    ], className="row g-2 mt-1"),

                    # Barra de estado rediseñada — pill con icono + texto + tiempo estimado
                    html.Div([
                        html.Div([
                            html.I(id="sweep-status-icon", className="fas fa-circle-info me-1 text-secondary"),
                            html.Span("", id="sweep-status", className="small"),
                        ], className="d-flex align-items-center gap-1"),
                        html.Div([
                            html.I(className="fas fa-clock me-1 text-muted"),
                            html.Span(id="sweep-time-estimate", className="small fw-semibold text-muted"),
                        ], id="sweep-time-badge", className="d-flex align-items-center gap-1"),
                    ], className="sweep-status-bar mt-3 d-flex flex-wrap align-items-center gap-3",
                       id="sweep-status-bar")
                ], className="card-body p-3")
            ], className="card border-0 shadow")
        ], className="col-12")
    ], className="row mb-4")

# ==================== LAYOUT ====================

layout = html.Div([
    # Mobile Navbar (solo visible en móvil)
    mobileNavBar(),
    
    # Botón flotante del terminal
    floating_terminal_button(),
    
    # Contenedor flex para sidebar y contenido principal
    html.Div([
        # Sidebar (navegación izquierda)
        sideBar(),
        
        # Contenido principal - aprovecha todo el espacio horizontal disponible
        html.Main([
            dcc.Location(id='url', refresh=False),
            
            # Contenedor principal con fondo
            html.Div([
                # Header limpio - controles de conexión movidos al sidebar
                html.Div([
                    html.Div([
                        html.H2(html.Span('', **{'data-i18n': 'dash.title'}), className="h3 mb-0")
                ], className="col-12 col-md-6 mb-2 mb-md-0"),
                html.Div([
                    # Solo botón de tema
                    html.Button([
                        html.I(className="fas fa-moon", id="theme-icon")
                    ], id="theme-toggle-btn", className="btn btn-outline-secondary", title="Cambiar tema"),
                ], className="col-12 col-md-6 d-flex justify-content-md-end align-items-center")
            ], className="row align-items-center py-4"),

            # Intervalos de actualización y stores (solo específicos del dashboard)
            # ports-interval y connection-monitor-interval están definidos globalmente en app.py
            dcc.Interval(id='measurement-interval', interval=500, n_intervals=0, disabled=True),
            dcc.Interval(id='sweep-interval', interval=1000, n_intervals=0, disabled=True),  # Deshabilitado por defecto - se activa solo durante barrido
            dcc.Interval(id='sweep-streaming-interval', interval=100, n_intervals=0, disabled=True),  # Para polling de puntos en streaming (100ms)
            dcc.Interval(id='connection-status-interval', interval=1000, n_intervals=0, disabled=True),  # Deshabilitado por defecto - solo activo cuando el modal está abierto
            dcc.Interval(id='modal-close-interval', interval=1000, n_intervals=0, disabled=True),  # Para cerrar modal con delay
            dcc.Store(id='sweep-data-store', storage_type='session', data={'param': [], 'z_real': [], 'z_imag': [], 'z_mag': [], 'phase': []}),  # Persistir datos entre páginas
            dcc.Store(id='sweep-streaming-state', data={'active': False}),  # Estado del streaming de sweep
            dcc.Store(id='phase-negative-store', storage_type='session', data=False),  # Persistir configuración de fase entre páginas
            dcc.Store(id='sweep-completed-trigger', data=False),  # Store para activar alerta de sweep completado
            dcc.Store(id='ports-cache-store', data=[]),  # Cache de puertos para evitar recargas innecesarias
            # connection-error-trigger y connection-success-trigger están definidos globalmente en app.py
            dcc.Store(id='modal-close-trigger', data=False),  # Store para controlar cierre del modal con delay
            # theme-store se define globalmente en app.py
            dcc.Download(id='download-csv'),  # Componente para descargar archivos CSV
            dcc.Store(id='csv-upload-store', data=None),  # Store temporal para datos CSV cargados
            # auto-connect-on-start está definido globalmente en app.py
            dcc.Store(id='connect-modal-dummy', data=None),  # Dummy store para callbacks clientside
            dcc.Store(id='chart-modal-dummy', data=None),  # Dummy store para ventana de gráfico

            # ✅ PRIORIDAD #1: GRÁFICOS PRIMERO (70% altura visual)
            html.Div([
                # Diagrama de Bode
                html.Div([
                    html.Div([
                        html.Div([
                            html.H5([
                                html.I(className="fas fa-chart-line me-2"),
                                html.Span('', **{'data-i18n': 'dash.bode_title'})
                            ], className="mb-0"),
                            html.Button(
                                html.I(className="fas fa-expand"),
                                id='maximize-bode-btn',
                                className='btn btn-outline-secondary btn-sm ms-2',
                                title='',
                                **{'data-i18n-title': 'dash.maximize_bode'}
                            )
                        ], className="d-flex justify-content-between align-items-center card-header border-bottom border-gray-300 p-3"),
                        html.Div([
                            dcc.Graph(id='bode-plot', figure={}, style={'height': '500px'})
                        ], className="card-body p-2")
                    ], className="card border-0 shadow h-100")
                ], className="col-12 col-lg-6 mb-4"),

                # Diagrama de Nyquist
                html.Div([
                    html.Div([
                        html.Div([
                            html.H5([
                                html.I(className="fas fa-circle-notch me-2"),
                                html.Span('', **{'data-i18n': 'dash.nyquist_title'})
                            ], className="mb-0"),
                            html.Button(
                                html.I(className="fas fa-expand"),
                                id='maximize-nyquist-btn',
                                className='btn btn-outline-secondary btn-sm ms-2',
                                title='',
                                **{'data-i18n-title': 'dash.maximize_nyq'}
                            )
                        ], className="d-flex justify-content-between align-items-center card-header border-bottom border-gray-300 p-3"),
                        html.Div([
                            dcc.Graph(id='nyquist-plot', figure={}, style={'height': '500px'})
                        ], className="card-body p-2")
                    ], className="card border-0 shadow h-100")
                ], className="col-12 col-lg-6 mb-4")
            ], className="row"),
            
            # ✅ PRIORIDAD #2: CONFIGURACIÓN COMPACTA (30% altura visual)
            sweep_config_card_compact(),

            # Modales
            connect_modal(),
            csv_modal(),
            # Nota: Terminal CLI es global, no se incluye aquí
            
            # Modal de progreso del barrido (estilo Volt Bootstrap 5)
            html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div([
                                # Botón close (esquina superior derecha)
                                html.Button(type='button', className='btn-close ms-auto', **{"data-bs-dismiss": "modal"}),
                                
                                # Título centrado
                                html.Div([
                                    html.H1([
                                        html.I(className="fas fa-chart-line me-2"),
                                        "Barrido en Progreso"
                                    ], className='mb-0 h4')
                                ], className='text-center mb-4 mt-md-0'),
                                
                                # Contenido del progreso
                                html.Div([
                                    html.P("", className="mb-3 text-center", **{'data-i18n': 'dash.running_sweep_short'}),
                                    html.Div([
                                        html.Div("0%", id="sweep-progress-bar", className="progress-bar progress-bar-striped progress-bar-animated bg-info", 
                                                 role="progressbar", style={'width': '0%'}, **{"aria-valuenow": "0", "aria-valuemin": "0", "aria-valuemax": "100"})
                                    ], className="progress mb-3", style={'height': '25px'}),
                                    html.P("", id="sweep-status-modal", className="text-muted text-center mb-4", **{'data-i18n': 'dash.starting'})
                                ]),
                                
                                # Botón de cancelar
                                html.Div([
                                    html.Button([
                                        html.I(className="fas fa-times me-2"), 
                                        "Cancelar Barrido"
                                    ], id="cancel-sweep-modal-btn", className="btn btn-danger")
                                ], className='d-grid')
                            ], className='card p-3 p-lg-4')
                        ], className='modal-body p-0')
                    ], className='modal-content')
                ], className='modal-dialog modal-dialog-centered modal-lg d-flex align-items-center min-vh-100 w-100 mx-auto', role='document')
            ], id="sweep-modal", className='modal fade', tabIndex='-1', role='dialog', **{"aria-hidden": "true"})

        ], className="container-fluid py-4")
        ], className="main-content w-100")
    
    ], className="d-flex flex-grow-1"),
    
    # Footer al final, fuera del flex sidebar-content
    footer(),
    
    # Ventana de gráfico maximizado - Estilo ventana arrastrable moderna
    html.Div([
        # Header - estructura estandarizada
        html.Div([
            # Título
            html.Div([
                html.I(className="fas fa-chart-line me-2"),
                html.Span("", id="chart-modal-title", **{'data-i18n': 'dash.chart_maximized'}),
            ], className="window-title"),
            
            # Controles
            html.Div([
                html.Button(
                    html.I(className="fas fa-minus"),
                    id="modal-minimize-btn",
                    className="window-control-btn window-btn-minimize",
                    title="Minimizar"
                ),
                html.Button(
                    html.I(className="fas fa-expand"),
                    id="modal-maximize-btn",
                    className="window-control-btn window-btn-maximize",
                    title="Maximizar/Restaurar"
                ),
                html.Button(
                    html.I(className="fas fa-times"),
                    id="modal-close-btn",
                    className="window-control-btn window-btn-close",
                    title="Cerrar (Esc)"
                )
            ], className="window-controls")
        ], className="window-header", id="chart-modal-header-drag"),
        
        # Body con gráfico
        html.Div([
            dcc.Graph(
                id='modal-chart',
                style={'height': '100%'},
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'scrollZoom': True,
                    'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': 'zoria_chart',
                        'height': 800,
                        'width': 1200,
                        'scale': 2
                    }
                }
            )
        ], className="window-body"),
        
        # Info bar en la parte inferior
        html.Div([
            html.Div([
                html.Small([
                    html.I(className="fas fa-info-circle me-1"),
                    " Use la rueda del ratón para zoom • Doble clic para resetear • Arrastre para pan"
                ], className="text-muted")
            ], className="d-flex align-items-center"),
            html.Div([
                html.Button(
                    [html.I(className="fas fa-download me-1"), " PNG"],
                    id="modal-export-png-btn",
                    className="btn btn-sm btn-outline-secondary me-2"
                ),
                html.Button(
                    [html.I(className="fas fa-file-csv me-1"), " CSV"],
                    id="modal-export-csv-btn",
                    className="btn btn-sm btn-outline-secondary"
                )
            ], className="d-flex align-items-center")
        ], className="chart-footer")
    ], 
    id="chart-modal",
    className="draggable-window chart-window",
    style={'display': 'none'}
    )

], className="sc-chart sc-theme-dark d-flex flex-column min-vh-100", id="main-layout")

# ==================== CALLBACKS ====================

def register_callbacks(app):
    # Callback para actualizar puertos seriales (solo si hay cambios)
    @app.callback(
        Output('serial-ports', 'options'),
        Output('serial-ports', 'value', allow_duplicate=True),
        Output('ports-cache-store', 'data'),
        [Input('ports-interval', 'n_intervals'),
         Input('refresh-ports-btn', 'n_clicks')],
        State('serial-ports', 'value'),
        State('ports-cache-store', 'data'),
        prevent_initial_call=True
    )
    def update_serial_ports(interval_n, refresh_clicks, current_value, cached_ports):
        """
        Actualiza la lista de puertos seriales disponibles.
        Solo actualiza si detecta cambios reales (puertos conectados/desconectados).
        """
        try:
            # Detectar puertos actuales
            admx_ports = detect_admx2001_ports()
            usb_ports = get_preferred_usb_serial_ports()

            # Crear lista actual de dispositivos
            current_ports = []
            options = []

            # Agregar puertos ADMX2001 primero
            for port in admx_ports:
                port_info = {
                    'device': port.device,
                    'description': port.description[:30] if port.description else '',
                    'is_admx': True
                }
                current_ports.append(port_info)
                options.append({
                    'label': f"✓ {port.device} - {port_info['description']}",
                    'value': port.device
                })

            # Agregar otros puertos USB compatibles, excluyendo ttyS* y similares
            for port in usb_ports:
                if port not in admx_ports:
                    port_info = {
                        'device': port.device,
                        'description': port.description if port.description else '',
                        'is_admx': False
                    }
                    current_ports.append(port_info)
                    options.append({
                        'label': f"{port.device} - {port_info['description']}",
                        'value': port.device
                    })

            # Comparar con caché - solo actualizar si hay cambios
            # Verificar si fue clic en refresh (siempre actualizar)
            triggered = ctx.triggered_id
            force_update = (triggered == 'refresh-ports-btn')
            
            if not force_update and cached_ports:
                # Comparar las listas de dispositivos
                cached_devices = [p['device'] for p in cached_ports]
                current_devices = [p['device'] for p in current_ports]
                
                # Si los dispositivos son los mismos, no actualizar
                if set(cached_devices) == set(current_devices):
                    raise PreventUpdate

            # Si no hay puertos, mostrar mensaje
            if not options:
                options = [{'label': '❌ No se encontraron puertos USB', 'value': '', 'disabled': True}]
                return options, '', []
            
            # Determinar valor a seleccionar
            available_devices = [p['device'] for p in current_ports]
            
            # Mantener el valor actual si sigue disponible
            if current_value and current_value in available_devices:
                new_value = current_value
            else:
                # Si el valor actual ya no está disponible, seleccionar el primero
                new_value = available_devices[0] if available_devices else ''

            return options, new_value, current_ports

        except PreventUpdate:
            raise
        except Exception as e:
            logger.error(f"Error al detectar puertos seriales: {e}")
            return [{'label': f'❌ Error: {str(e)[:40]}', 'value': '', 'disabled': True}], '', []

    # Callback para sincronizar checkbox de fase negativa con Store
    @app.callback(
        Output('phase-negative-store', 'data'),
        Input('phase-negative-check', 'value'),
        prevent_initial_call=False
    )
    def update_phase_negative_store(checkbox_value):
        """Actualiza el store cuando cambia el checkbox de fase negativa"""
        is_negative = 'negative' in checkbox_value if checkbox_value else False
        safe_print(f"📐 Fase negativa: {is_negative}")
        return is_negative

    # ── Callback: Estimador de tiempo de barrido en tiempo real ──────────────
    @app.callback(
        Output('sweep-time-estimate', 'children'),
        [Input('sweep-start',  'value'),
         Input('sweep-end',    'value'),
         Input('sweep-points', 'value'),
         Input('sweep-scale',  'value'),
         Input('sweep-mdelay', 'value'),
         Input('sweep-tdelay', 'value')],
        prevent_initial_call=False
    )
    def update_sweep_time_estimate(f_start, f_end, n_pts, scale, mdelay, tdelay):
        """Calcula y muestra el tiempo estimado del barrido en la UI."""
        from lib.utils import estimate_sweep_time, max_points_per_segment
        try:
            f_start  = float(f_start  or 100)
            f_end    = float(f_end    or 100000)
            n_pts    = int(n_pts      or 50)
            scale    = scale  or 'log'
            mdelay_v = float(mdelay   or 0) if (mdelay is not None and float(mdelay) >= 0) else 0.0
            tdelay_v = float(tdelay   or 0) if tdelay is not None else 0.0

            if f_start <= 0 or f_end <= 0 or f_start >= f_end or n_pts < 2:
                return ""

            info = estimate_sweep_time(f_start, f_end, n_pts,
                                       scale=scale,
                                       mdelay=mdelay_v,
                                       tdelay=tdelay_v)
            seg_rec = info['recommended_segments']
            seg_label = f"{seg_rec} seg." if seg_rec > 1 else "1 seg."

            # Advertencia si el barrido es muy largo
            total_s = info['total_seconds']
            if total_s > 3600:
                color = "text-danger"
                icon  = "⚠️"
            elif total_s > 300:
                color = "text-warning"
                icon  = "⏳"
            else:
                color = "text-success"
                icon  = "⏱"

            return html.Span(
                [f"{icon} ~{info['human_readable']}  ({seg_label})"],
                className=color,
                title=(f"Estimación basada en {n_pts} puntos. "
                       f"Punto más lento: {info['bottleneck_freq']:.4g} Hz "
                       f"→ {info['bottleneck_ms']:.0f} ms. "
                       f"Segmentos recomendados: {seg_rec}.")
            )
        except Exception:
            return ""
    # ─────────────────────────────────────────────────────────────────────────
    
    # Callback dedicado para actualizar gráficas cuando cambia la fase negativa
    @app.callback(
        [Output('bode-plot', 'figure', allow_duplicate=True),
         Output('nyquist-plot', 'figure', allow_duplicate=True)],
        Input('phase-negative-store', 'data'),
        State('sweep-data-store', 'data'),
        State('theme-store', 'data'),
        prevent_initial_call=True
    )
    def update_graphs_on_phase_change(negative_phase, stored_data, theme):
        """Actualiza SOLO las gráficas cuando cambia el checkbox de fase negativa"""
        safe_print(f"🔄 Actualizando gráficas por cambio de fase - negativa: {negative_phase}")
        
        if stored_data and len(stored_data.get('param', [])) > 0:
            safe_print(f"📊 Regenerando gráficas con fase {'negativa' if negative_phase else 'positiva'}")
            bode_fig = create_bode_plot_from_dataset(stored_data, negative_phase, theme)
            nyquist_fig = create_nyquist_plot_from_dataset(stored_data, theme)
            return bode_fig, nyquist_fig
        else:
            safe_print(f"⚠️ No hay datos para actualizar gráficas")
            raise PreventUpdate
    
    # Callback para cargar datos persistentes al navegar a la página
    @app.callback(
        [Output('bode-plot', 'figure', allow_duplicate=True),
         Output('nyquist-plot', 'figure', allow_duplicate=True)],
        Input('url', 'pathname'),
        [State('sweep-data-store', 'data'),
         State('phase-negative-store', 'data'),
         State('theme-store', 'data')],
        prevent_initial_call=False
    )
    def load_persistent_data(pathname, stored_data, phase_negative, theme):
        """Carga datos del Store al cargar/navegar a la página del dashboard SOLO al navegar"""
        safe_print(f"🔄 Callback load_persistent_data - pathname: {pathname}")
        
        # Si hay datos guardados, regenerar gráficas
        if stored_data and len(stored_data.get('param', [])) > 0:
            safe_print(f"📊 Restaurando gráficas con {len(stored_data['param'])} puntos del Store")
            bode_fig = create_bode_plot_from_dataset(stored_data, phase_negative, theme)
            nyquist_fig = create_nyquist_plot_from_dataset(stored_data, theme)
            return bode_fig, nyquist_fig
        else:
            safe_print(f"📊 No hay datos en Store - mostrando gráficas vacías")
            empty_bode = create_empty_figure("Sin datos - Ejecute un barrido", theme)
            empty_nyquist = create_empty_figure("Sin datos - Ejecute un barrido", theme)
            return empty_bode, empty_nyquist
    
    # Callback separado para sincronizar checkbox con Store al cargar página
    @app.callback(
        Output('phase-negative-check', 'value'),
        Input('url', 'pathname'),
        State('phase-negative-store', 'data'),
        prevent_initial_call=False
    )
    def sync_checkbox_from_store(pathname, phase_negative):
        """Sincroniza el checkbox con el valor del Store SOLO al navegar a la página"""
        checkbox_value = ['negative'] if phase_negative else []
        safe_print(f"🔄 Sincronizando checkbox desde Store: {checkbox_value} (pathname: {pathname})")
        return checkbox_value

    @app.callback(
        [Output('sweep-start', 'disabled'),
         Output('sweep-end', 'disabled'),
         Output('sweep-points', 'disabled'),
         Output('sweep-scale', 'disabled'),
         Output('sweep-trigger-frequency', 'disabled'),
         Output('sweep-trigger-count', 'disabled')],
        Input('sweep-trigger-check', 'value'),
        prevent_initial_call=False
    )
    def toggle_trigger_mode_controls(trigger_options):
        """Alterna controles entre barrido clásico y trigger de frecuencia fija."""
        trigger_enabled = 'trigger' in (trigger_options or [])
        return (
            False,
            False,
            False,
            False,
            True,
            not trigger_enabled,
        )
    
    # Callback para cerrar modal con delay de 1 segundo después de completarse el sweep
    @app.callback(
        [Output('sweep-modal', 'style', allow_duplicate=True),
         Output('sweep-modal', 'className', allow_duplicate=True),
         Output('modal-close-interval', 'disabled', allow_duplicate=True)],
        Input('modal-close-interval', 'n_intervals'),
        prevent_initial_call=True
    )
    def close_modal_after_delay(n):
        """Cierra el modal 1 segundo después de completarse el barrido al 100%"""
        safe_print(f"⏱️ Modal close interval fired: n_intervals = {n}")
        
        if n and n > 0:
            # El intervalo se disparó, cerrar modal
            safe_print("✅ Cerrando modal después de 1 segundo de delay")
            return {'display': 'none'}, 'modal fade', True  # Cerrar modal y deshabilitar intervalo
        
        # No cerrar aún
        raise PreventUpdate

    # =========================================================================
    # CALLBACKS DE CONEXIÓN DEL SIDEBAR
    # =========================================================================
    # Los callbacks de conexión del sidebar (sidebar_connection_handler,
    # monitor_connection_health, trigger_auto_connect) ahora están registrados
    # globalmente en app.py para estar disponibles en todas las páginas.

    # Callback para ventana de conexión (abrir/cerrar) - solo controles internos del modal
    @app.callback(
        Output('connect-modal', 'style', allow_duplicate=True),
        Input('connect-modal-close', 'n_clicks'),
        prevent_initial_call=True
    )
    def toggle_connect_modal(close_clicks):
        """Controla el cierre del modal de conexión ADMX2001"""
        if close_clicks and close_clicks > 0:
            return {'display': 'none'}
        raise PreventUpdate
    
    # Abrir modal desde botón del sidebar (clientside) - CRÍTICO: actualiza el prop de React
    # para que el cierre funcione. La apertura directa con JS baja bypassea React y rompe el close.
    app.clientside_callback(
        """
        function(n) {
            if (!n || n <= 0) return window.dash_clientside.no_update;
            if (window.location.pathname !== '/') return window.dash_clientside.no_update;
            return {'display': 'flex', 'width': '380px', 'height': 'auto'};
        }
        """,
        Output('connect-modal', 'style', allow_duplicate=True),
        Input('sidebar-config-btn', 'n_clicks'),
        prevent_initial_call=True
    )

    # Inicializar ventana arrastrable de conexión (clientside)
    app.clientside_callback(
        """
        function(style) {
            if (style && (style.display === 'flex' || style.display === 'block')) {
                // Dar tiempo a que el DOM se actualice
                setTimeout(function() {
                    if (window.DraggableWindows && !window.DraggableWindows.isInitialized('connect-modal')) {
                        window.DraggableWindows.init('connect-modal', 'connect-modal-header', {width: 380, height: 420});
                        window.DraggableWindows.show('connect-modal');
                    } else if (window.DraggableWindows) {
                        window.DraggableWindows.show('connect-modal');
                    }
                }, 100);
            }
            return 1;
        }
        """,
        Output('connect-modal-dummy', 'data'),
        Input('connect-modal', 'style'),
        prevent_initial_call=True
    )
    
    # Callback para conectar desde el modal (solo disponible en Dashboard)
    @app.callback(
        [Output('sidebar-connection-text', 'children', allow_duplicate=True),
         Output('sidebar-connection-dot', 'className', allow_duplicate=True),
         Output('sidebar-device-port', 'children', allow_duplicate=True),
         Output('sidebar-disconnect-btn', 'disabled', allow_duplicate=True),
         Output('connection-error-trigger', 'data', allow_duplicate=True),
         Output('connection-success-trigger', 'data', allow_duplicate=True),
         Output('connect-modal', 'style', allow_duplicate=True)],
        [Input('connect-btn', 'n_clicks'),
         Input('disconnect-modal-btn', 'n_clicks')],
        State('serial-ports', 'value'),
        prevent_initial_call=True
    )
    def modal_connection_handler(connect_clicks, disconnect_clicks, port):
        """
        Callback de conexión desde el modal (solo disponible en Dashboard):
        - Conexión manual desde modal (connect-btn)
        - Desconexión desde modal (disconnect-modal-btn)
        """
        
        triggered = ctx.triggered_id
        logger.info(f"Modal connection handler triggered by: {triggered}")
        
        # Verificar que el trigger sea válido
        if not triggered or triggered not in ['connect-btn', 'disconnect-modal-btn']:
            logger.warning(f"Modal connection handler: trigger inválido {triggered}")
            raise PreventUpdate
        
        # CRÍTICO: Ignorar disparos por re-montaje SPA (n_clicks=0 al navegar a la página).
        # prevent_initial_call=True solo protege el arranque inicial de la app, NO la
        # navegación SPA donde los componentes se remontan con n_clicks=0 pero Dash
        # igual dispara el callback porque los componentes son "nuevos" para React.
        if triggered == 'connect-btn' and (not connect_clicks or connect_clicks <= 0):
            raise PreventUpdate
        if triggered == 'disconnect-modal-btn' and (not disconnect_clicks or disconnect_clicks <= 0):
            raise PreventUpdate
        
        # ===== DESCONEXIÓN =====
        if triggered == 'disconnect-modal-btn':
            try:
                if device_state.device:
                    device_state.device.close()
                device_state.set_device(None, False)
                logger.info("Dispositivo desconectado desde modal")
                return ("Desconectado", "connection-pulse disconnected",
                        "ADMX2001", True, False, False, {'display': 'none'})
            except Exception as e:
                logger.error(f"Error desconectando: {e}")
                # NO activar error modal - desconexión fallida no es crítica
                return ("Error", "connection-pulse error",
                        "ADMX2001", True, False, False, {'display': 'none'})
        
        # ===== CONEXIÓN MANUAL =====
        if triggered == 'connect-btn':
            if not port or port == '':
                logger.warning("Intento de conexión sin puerto seleccionado")
                # NO activar error modal - solo es una validación de formulario
                return ("Seleccione puerto", "connection-pulse disconnected",
                        "ADMX2001", True, False, False, {'display': 'flex'})
            
            # Adquirir lock para evitar conexiones simultáneas
            if not device_state._operation_lock.acquire(blocking=False):
                logger.warning("Otra operación en curso, saltando conexión manual")
                return ("Ocupado", "connection-pulse disconnected",
                        "ADMX2001", True, False, False, {'display': 'flex'})
            
            try:
                logger.info(f"Conectando manualmente a {port}...")
                new_device = ADMX2001(port, baudrate=115200, timeout=5.0)
                device_state.set_device(new_device, True)
                new_device.set_mdelay(1)
                new_device.set_tdelay(0)
                logger.info(f"✅ Conectado a {port}")
                return ("Conectado", "connection-pulse connected",
                    port, False, False, True, {'display': 'none'})
            except Exception as e:
                logger.error(f"Error conectando manualmente: {e}")
                # SÍ activar error modal - falló una conexión manual explícita
                return ("Error", "connection-pulse error",
                    "ADMX2001", True, True, False, {'display': 'flex'})
            finally:
                # Liberar lock de operación
                device_state._operation_lock.release()
        
        raise PreventUpdate
    
    # Callback para controlar el interval de autoconexión según visibilidad del modal
    @app.callback(
        Output('connection-status-interval', 'disabled', allow_duplicate=True),
        Input('connect-modal', 'style'),
        State('connection-status-interval', 'disabled'),
        prevent_initial_call=True
    )
    def control_connection_interval(modal_style, current_disabled):
        """
        Controla el interval de autoconexión:
        - Habilitado solo cuando el modal está visible
        - Deshabilitado cuando el modal está cerrado (para evitar bucles)
        """
        if not modal_style:
            return True  # Deshabilitar si no hay estilo
        
        is_visible = modal_style.get('display') != 'none'
        
        # Habilitar interval solo si el modal está visible
        should_be_disabled = not is_visible
        
        # Solo actualizar si cambió el estado
        if should_be_disabled != current_disabled:
            return should_be_disabled
        
        raise PreventUpdate

    # Callback para gestionar barrido y actualizar gráficos
    @app.callback(
        [Output('bode-plot', 'figure'),
         Output('nyquist-plot', 'figure'),
         Output('sweep-modal', 'style'),
         Output('sweep-modal', 'className'),
         Output('sweep-progress-bar', 'style'),
         Output('sweep-progress-bar', 'children'),
         Output('sweep-progress-bar', 'aria-valuenow'),
         Output('sweep-status', 'children'),
         Output('sweep-status-modal', 'children'),
         Output('sweep-data-store', 'data'),
         Output('sweep-completed-trigger', 'data'),
         Output('sweep-interval', 'disabled'),  # Control del interval - solo activo durante barrido
         Output('modal-close-interval', 'disabled'),  # Control del cierre retardado del modal
         Output('sweep-streaming-interval', 'disabled')],  # Control del interval de streaming
        [Input('sweep-interval', 'n_intervals'),
         Input('sweep-btn', 'n_clicks'),
         Input('cancel-sweep-btn', 'n_clicks'),
         Input('cancel-sweep-modal-btn', 'n_clicks')],  # 4 inputs - phase NO es Input
        [State('sweep-start', 'value'),
         State('sweep-end', 'value'),
         State('sweep-points', 'value'),
         State('sweep-scale', 'value'),
         State('sweep-display-mode', 'value'),
         State('sweep-mdelay', 'value'),
         State('sweep-tdelay', 'value'),
         State('sweep-magnitude', 'value'),
         State('sweep-trigger-check', 'value'),
         State('sweep-trigger-frequency', 'value'),
         State('sweep-trigger-count', 'value'),
         State('phase-negative-store', 'data'),  # Ahora es State - solo lee valor
         State('sweep-data-store', 'data'),
         State('theme-store', 'data')],
        prevent_initial_call=True
    )
    def manage_sweep(n_intervals, sweep_clicks, cancel_clicks, cancel_modal_clicks,
                     start, end, points, scale, display_mode, mdelay, tdelay, magnitude,
                     trigger_options, trigger_frequency, trigger_count,
                     negative_phase, stored_data, theme):
        """Gestiona el barrido de frecuencia y actualización de gráficos"""
        global sweep_thread, sweep_data, sweep_progress, sweep_completed_successfully

        safe_print(f"Callback manage_sweep ejecutado - interval: {n_intervals}, triggered: {ctx.triggered_id}, negative_phase: {negative_phase}")

        # Obtener el ID del elemento que disparó el callback
        triggered = ctx.triggered_id

        # Inicializar variables básicas
        sweep_completed_trigger = False
        has_new_data = False  # CRÍTICO: Inicializar antes de cualquier uso
        # Inicializar gráficas con stored_data si existe, sino gráficas vacías
        # Estas se regenerarán durante el procesamiento si hay nuevos datos
        if stored_data and len(stored_data.get('param', [])) > 0:
            bode_fig = create_bode_plot_from_dataset(stored_data, negative_phase, theme)
            nyquist_fig = create_nyquist_plot_from_dataset(stored_data, theme)
        else:
            bode_fig = create_empty_figure("Sin datos", theme)
            nyquist_fig = create_empty_figure("Sin datos", theme)
        
        stored_data = stored_data or {'param': [], 'z_real': [], 'z_imag': [], 'z_mag': [], 'phase': []}
        total_points = points or 50
        sweep_completed = False
        graphs_updated = False  # Bandera para saber si se actualizaron las gráficas durante procesamiento
        
        # NO inicializar progress/status/modal aquí - se establecerán según el estado del sweep
        # Esto evita sobrescribir valores actualizados durante el procesamiento de mensajes
        
        # Control del interval: Determinar estado basándose en thread y cola
        # El interval debe estar habilitado si hay un sweep activo O mensajes pendientes
        thread_alive = sweep_thread and sweep_thread.is_alive()
        queue_has_messages = not sweep_queue.empty()
        has_active_sweep = thread_alive or queue_has_messages
        interval_disabled = not has_active_sweep  # Disabled = True cuando NO hay sweep activo
        
        print(f"📊 Estado: Thread alive={thread_alive}, Queue has msgs={queue_has_messages}, Active sweep={has_active_sweep}, Interval disabled={interval_disabled}")

        # CRÍTICO: Mantener modal CERRADO hasta que haya mensajes en la cola
        # Esto evita que el usuario vea el modal durante la fase de adquisición del hardware
        # El modal solo se abre cuando hay progreso real que mostrar (mensajes en cola)

        # Procesar mensajes de la cola si hay un sweep activo o mensajes pendientes
        if has_active_sweep:
            try:
                # Inicializar TODAS las variables necesarias para el return
                modal_style = {'display': 'flex'}
                modal_class = 'modal fade show'
                progress_style = {'width': f'{sweep_progress}%'}
                progress_text = f"{sweep_progress}%"
                status_text = "Procesando..."
                sweep_completed = False  # Flag local para detectar completado en ESTA ejecución
                
                # Usar progreso anterior
                progress_value = sweep_progress
                print(f"Progreso actual: {progress_value}%")
                print(f"  Thread alive: {sweep_thread and sweep_thread.is_alive()}, Queue size: {sweep_queue.qsize()}")

                # Procesar cola de sweep para actualizar progreso
                current_point = 0
                has_new_data = False

                # ELIMINADO: Procesamiento de mensajes 'current' - el progreso ahora se maneja 100% por streaming
                # Solo procesamos 'completed' y 'error' de la cola
                if not sweep_queue.empty():
                    try:
                        data = sweep_queue.get_nowait()
                        print(f"CALLBACK: Recibido mensaje de cola: {list(data.keys())}")
                        has_new_data = True
                        
                        # SOLO procesar 'completed' y 'error', ignorar 'current'
                        if 'current' in data:
                            # IGNORAR - el progreso lo maneja poll_sweep_streaming
                            print(f"[manage_sweep] Mensaje 'current' ignorado - progreso manejado por streaming")
                            pass

                        elif 'completed' in data:
                            # CRÍTICO: Actualizar TODAS las variables de progreso al 100%
                            progress_value = 100  # aria-valuenow
                            sweep_progress = 100  # variable global
                            progress_style = {'width': '100%'}  # ancho visual
                            progress_text = "100%"  # texto mostrado
                            
                            if data.get('mode') == 'trigger':
                                status_text = f"✅ Trigger completado: {data.get('runs', 1)} barridos ({data['points']} puntos en el último)"
                            else:
                                status_text = f"✅ Barrido completado: {data['points']} puntos"
                            sweep_completed = True  # Marcar que el sweep se completó
                            sweep_completed_successfully = True  # Marcar que se completó exitosamente
                            
                            # CERRAR MODAL INMEDIATAMENTE (no esperar 1s)
                            modal_style = {'display': 'none'}
                            modal_class = 'modal fade'
                            modal_close_interval_disabled = True  # Ya cerrado, no necesita interval
                            
                            # CRÍTICO: Marcar sweep como NO en progreso para detener polling
                            device_state.end_sweep_streaming()
                            print(f"📡 Sweep streaming finalizado desde callback (redundancia)")
                            
                            print(f"🎉 BARRIDO COMPLETADO: 100% - cerrando modal inmediatamente")
                            # Forzar actualización inmediata de gráficos cuando se completa el sweep
                            if sweep_data and sweep_data.get('param') and len(sweep_data['param']) > 0:
                                try:
                                    print(f"📊 ACTUALIZANDO GRÁFICAS FINALES: {len(sweep_data['param'])} puntos")
                                    bode_fig = create_bode_plot_from_dataset(sweep_data, negative_phase, theme)
                                    nyquist_fig = create_nyquist_plot_from_dataset(sweep_data, theme)
                                    graphs_updated = True  # Marcar que las gráficas se actualizaron
                                    # CRÍTICO: Actualizar el store INMEDIATAMENTE con los datos completos del sweep
                                    stored_data = {
                                        'param': sweep_data['param'].copy(),
                                        'z_real': sweep_data['z_real'].copy(),
                                        'z_imag': sweep_data['z_imag'].copy(),
                                        'z_mag': sweep_data['z_mag'].copy(),
                                        'phase': sweep_data['phase'].copy(),
                                        'runs': [dict(run) for run in sweep_data.get('runs', [])],
                                        'trigger_enabled': sweep_data.get('trigger_enabled', False),
                                    }
                                    print(f"✅ STORED_DATA ACTUALIZADO: {len(stored_data['param'])} puntos")
                                    # Activar trigger para mostrar alerta de sweep completado
                                    sweep_completed_trigger = True
                                except Exception as e:
                                    print(f"❌ ERROR actualizando gráficas: {e}")
                                    bode_fig = create_empty_figure("Error en gráfico de Bode", theme)
                                    nyquist_fig = create_empty_figure("Error en gráfico de Nyquist", theme)
                                    sweep_completed_trigger = False
                            
                            # RETORNAR INMEDIATAMENTE con modal cerrado
                            interval_disabled = True  # Detener interval
                            streaming_interval_disabled = True  # Detener streaming
                            print(f"🔒 RETORNANDO: Modal cerrado, intervals detenidos, {len(stored_data['param'])} puntos guardados")
                            return (bode_fig, nyquist_fig, modal_style, modal_class, progress_style, progress_text, str(progress_value), status_text, status_text, stored_data, sweep_completed_trigger, interval_disabled, modal_close_interval_disabled, streaming_interval_disabled)

                        elif 'error' in data:
                            error_phase = data.get('phase', 'unknown')
                            if error_phase == 'config':
                                print(f"❌ Error durante CONFIGURACIÓN de sweep: {data.get('message', '')}")
                            elif error_phase == 'acquisition':
                                print(f"❌ Error durante ADQUISICIÓN de sweep: {data.get('message', '')}")
                            elif error_phase == 'postprocess':
                                print(f"❌ Error durante POSTPROCESADO de sweep: {data.get('message', '')}")
                            else:
                                print(f"❌ Error en sweep (fase no clasificada): {data.get('message', '')}")

                            # CERRAR MODAL Y DETENER TODO cuando hay error
                            modal_style = {'display': 'none'}
                            modal_class = 'modal fade'
                            sweep_progress = 0  # Reiniciar progreso en caso de error
                            progress_value = 0
                            progress_style = {'width': '0%'}
                            progress_text = "0%"
                            status_text = f"❌ Error ({error_phase}): {data['message']}"
                            interval_disabled = True  # Detener interval
                            streaming_interval_disabled = True  # Detener streaming
                            modal_close_interval_disabled = True  # No necesita cerrar (ya cerrado)
                            
                            # Detener sweep streaming
                            device_state.end_sweep_streaming()
                            print(f"❌ Error en sweep - modal cerrado, intervals detenidos")

                    except Exception as e:
                        # Si hay error procesando el mensaje, simplemente mantener estado actual
                        pass

            except (BrokenPipeError, IOError):
                # Ignorar errores de pipe roto (terminal cerrado)
                pass
            except Exception as e:
                try:
                    print(f"Error en callback manage_sweep (mantenimiento estado): {e}")
                    import traceback
                    traceback.print_exc()
                except (BrokenPipeError, IOError):
                    pass  # Ignorar si no se puede imprimir
                empty_bode = create_empty_figure("Error")
                empty_nyquist = create_empty_figure("Error")
                return (empty_bode, empty_nyquist, {'display': 'none'}, 'modal fade', {'width': '0%'}, "0%", "0",
                        f"❌ Error interno: {str(e)}", f"❌ Error interno: {str(e)}",
                        {'param': [], 'z_real': [], 'z_imag': [], 'z_mag': [], 'phase': []}, False)

        try:
            triggered = ctx.triggered_id

            # Iniciar sweep
            if triggered == 'sweep-btn':
                # Usar device_state global en lugar de variables locales
                if not device_state.device or not device_state.is_connected:
                    status_text = "❌ Dispositivo no conectado"
                    progress_style = {'width': '0%'}
                    progress_text = "0%"
                    modal_style = {'display': 'none'}
                    modal_class = 'modal fade'
                    return (bode_fig, nyquist_fig, modal_style, modal_class, progress_style, progress_text, "0", status_text, status_text, stored_data, False, True, True, True)  # interval disabled, modal-close-interval disabled, streaming-interval disabled

                try:
                    # Tomar valores ACTUALES de los inputs, con fallback a valores por defecto
                    start = float(start or 100)
                    end = float(end or 100000)
                    points = int(points or 50)
                    scale = scale or 'log'
                    trigger_enabled = 'trigger' in (trigger_options or [])
                    trigger_count = int(trigger_count) if trigger_count is not None else 1
                    
                    # Log de los parámetros que se van a usar
                    print(f"🔧 PARÁMETROS DEL BARRIDO:")
                    print(f"   - Frecuencia inicial: {start} Hz")
                    print(f"   - Frecuencia final: {end} Hz")
                    print(f"   - Número de puntos: {points}")
                    print(f"   - Escala: {scale}")
                    print(f"   - Trigger habilitado: {trigger_enabled}")
                    print(f"   - Conteo trigger: {trigger_count}")
                    print(f"   - Modo de visualización: {display_mode}")
                    print(f"   - Magnitud: {magnitude}")
                    print(f"   - Retardo medición: {mdelay}")
                    print(f"   - Retardo trigger: {tdelay}")

                    # Validar límites del equipo ADMX2001: 0.2 Hz - 10 MHz
                    min_freq = 0.2
                    max_freq = 10000000

                    if start < min_freq or start > max_freq:
                        status_text = f"❌ Frecuencia inicial debe estar entre {min_freq} Hz y {max_freq/1000000} MHz"
                        progress_style = {'width': '0%'}
                        progress_text = "0%"
                        modal_style = {'display': 'none'}
                        modal_class = 'modal fade'
                        return (bode_fig, nyquist_fig, modal_style, modal_class, progress_style, progress_text, "0", status_text, status_text, stored_data, False, True, True, True)  # interval disabled, modal-close-interval disabled, streaming disabled

                    if end < min_freq or end > max_freq:
                        status_text = f"❌ Frecuencia final debe estar entre {min_freq} Hz y {max_freq/1000000} MHz"
                        progress_style = {'width': '0%'}
                        progress_text = "0%"
                        modal_style = {'display': 'none'}
                        modal_class = 'modal fade'
                        return (bode_fig, nyquist_fig, modal_style, modal_class, progress_style, progress_text, "0", status_text, status_text, stored_data, False, True, True, True)  # interval disabled, modal-close-interval disabled, streaming disabled

                    if trigger_enabled:
                        if trigger_count < 1:
                            status_text = "❌ El número de triggers debe ser mayor o igual a 1"
                            progress_style = {'width': '0%'}
                            progress_text = "0%"
                            modal_style = {'display': 'none'}
                            modal_class = 'modal fade'
                            return (bode_fig, nyquist_fig, modal_style, modal_class, progress_style, progress_text, "0", status_text, status_text, stored_data, False, True, True, True)

                    if not trigger_enabled and (start >= end or points < 2):
                        status_text = "❌ Parámetros inválidos"
                        progress_style = {'width': '0%'}
                        progress_text = "0%"
                        modal_style = {'display': 'none'}
                        modal_class = 'modal fade'
                        return (bode_fig, nyquist_fig, modal_style, modal_class, progress_style, progress_text, "0", status_text, status_text, stored_data, False, True, True, True)  # interval disabled, modal-close-interval disabled, streaming disabled

                    # Crear configuración con los valores actuales
                    config = {
                        'start': start,
                        'end': end,
                        'points': points,
                        'scale': scale,
                        'display_mode': display_mode or 6,
                        'average': measurement_config.get('average', 1),
                        'mdelay': mdelay if mdelay is not None else -1,
                        'tdelay': tdelay if tdelay is not None else 0,
                        'magnitude': magnitude or 'auto',
                        'trigger_enabled': trigger_enabled,
                        'trigger_count': trigger_count,
                    }

                    # Prevenir inicio de barrido si ya hay uno activo
                    if sweep_thread and sweep_thread.is_alive():
                        print(f"⚠️ BARRIDO YA EN PROGRESO - Ignorando solicitud duplicada")
                        status_text = "⚠️ Barrido ya en progreso..."
                        # Retornar estado actual sin cambios - mantener streaming activo
                        return (bode_fig, nyquist_fig, modal_style, modal_class, progress_style, progress_text, str(progress_value), status_text, status_text, stored_data, False, False, True, False)  # interval enabled, modal-close disabled, streaming ENABLED
                    
                    # Iniciar nuevo barrido
                    stop_sweep.clear()

                    # Limpiar datos previos para que el nuevo sweep inicie con gráficas vacías
                    stored_data = {'param': [], 'z_real': [], 'z_imag': [], 'z_mag': [], 'phase': []}
                    bode_fig = create_empty_figure("Sin datos", theme)
                    nyquist_fig = create_empty_figure("Sin datos", theme)
                    
                    # Mantener stored_data para que los gráficos NO desaparezcan
                    # Los nuevos puntos llegarán vía poll_sweep_streaming
                    print(f"✅ Iniciando thread de barrido con configuración:")
                    print(f"   Config completa: {config}")
                    sweep_thread = threading.Thread(target=sweep_worker, args=(config,), daemon=True)
                    sweep_progress = 0  # Reiniciar progreso solo cuando se inicia un nuevo thread
                    sweep_completed_successfully = False  # Resetear estado de completado
                    sweep_thread.start()
                    print(f"🚀 Thread de barrido iniciado correctamente")

                    modal_style = {'display': 'block'}
                    modal_class = 'modal fade show'
                    progress_value = sweep_progress  # Usar el progreso actual (0 si es nuevo)
                    progress_style = {'width': '0%'}  # Inicializar estilo de progreso
                    progress_text = "0%"  # Inicializar texto de progreso
                    if trigger_enabled:
                        status_text = f"Iniciando trigger: {trigger_count} barridos sobre el rango configurado..."
                    else:
                        status_text = "Iniciando barrido..."
                    interval_disabled = False  # HABILITAR interval durante el barrido
                    streaming_interval_disabled = False  # HABILITAR interval de streaming durante el barrido
                    modal_close_interval_disabled = True  # Deshabilitar modal-close al inicio
                    
                    # RETORNAR INMEDIATAMENTE después de iniciar el sweep
                    # Mantener stored_data para preservar gráficos anteriores
                    return (bode_fig, nyquist_fig, modal_style, modal_class, progress_style, progress_text, str(progress_value), status_text, status_text, stored_data, False, interval_disabled, modal_close_interval_disabled, streaming_interval_disabled)

                except Exception as e:
                    status_text = f"❌ Error: {str(e)}"
                    progress_style = {'width': '0%'}
                    progress_text = "0%"
                    modal_style = {'display': 'none'}
                    modal_class = 'modal fade'
                    return (bode_fig, nyquist_fig, modal_style, modal_class, progress_style, progress_text, "0", status_text, status_text, stored_data, False, True, True, True)  # interval disabled, modal-close disabled, streaming disabled

            # Detener sweep
            elif triggered in ['cancel-sweep-btn', 'cancel-sweep-modal-btn']:
                stop_sweep.set()
                modal_style = {'display': 'none'}
                modal_class = 'modal fade'
                progress_style = {'width': '0%'}
                progress_text = "0%"
                sweep_progress = 0  # Reiniciar progreso al cancelar
                interval_disabled = True  # DESHABILITAR interval cuando se cancela
                streaming_interval_disabled = True  # DESHABILITAR interval de streaming cuando se cancela
                modal_close_interval_disabled = True  # Deshabilitar modal-close al cancelar
                progress_value = 0
                progress_text = "0%"
                status_text = "Barrido cancelado"
                sweep_completed_successfully = False  # Resetear estado de completado
                
                # RETORNAR INMEDIATAMENTE después de cancelar
                return (bode_fig, nyquist_fig, modal_style, modal_class, progress_style, progress_text, str(progress_value), status_text, status_text, stored_data, False, interval_disabled, modal_close_interval_disabled, streaming_interval_disabled)

            # Establecer valores por defecto SOLO si no fueron actualizados durante el procesamiento
            # Esto preserva los valores establecidos al procesar mensajes de la cola
            if 'progress_value' not in locals():
                progress_value = sweep_progress  # Usar progreso global
            if 'progress_style' not in locals():
                progress_style = {'width': f'{sweep_progress}%'}
            if 'progress_text' not in locals():
                progress_text = f"{sweep_progress}%"
            if 'modal_style' not in locals():
                modal_style = {'display': 'flex'}
            if 'modal_class' not in locals():
                modal_class = 'modal fade show'
            if 'status_text' not in locals():
                status_text = "Procesando..."
            if 'status_text' not in locals():
                status_text = "Procesando..." if has_active_sweep else "Listo"
            if 'modal_style' not in locals():
                modal_style = {'display': 'block'} if has_active_sweep else {'display': 'none'}
            if 'modal_class' not in locals():
                modal_class = 'modal fade show' if has_active_sweep else 'modal fade'
            
            # Establecer streaming_interval_disabled basándose en el estado del sweep
            if 'streaming_interval_disabled' not in locals():
                # Habilitar streaming solo si hay un sweep activo
                streaming_interval_disabled = not has_active_sweep
            
            print(f"🔍 Valores finales - Progress: {progress_value}%, Style width: {progress_style.get('width')}, Text: {progress_text}")
            
            # Actualizar gráficos con la mejor fuente de datos disponible
            # PRIORIDAD: stored_data > sweep_data (stored_data es persistente después del sweep)
            stored_points = len(stored_data.get('param', [])) if stored_data else 0
            sweep_points = len(sweep_data.get('param', [])) if sweep_data else 0
            
            # Si NO tenemos gráficos actualizados O el sweep ya terminó, regenerar con los datos disponibles
            if not graphs_updated or not has_active_sweep:
                # Priorizar stored_data si tiene datos (es la fuente persistente post-sweep)
                if stored_points > 0:
                    data_source = stored_data
                    source_name = 'stored_data (persistente)'
                elif sweep_points > 0:
                    data_source = sweep_data
                    source_name = 'sweep_data (activo)'
                else:
                    data_source = None
                    source_name = 'ninguna'
                
                if data_source and len(data_source.get('param', [])) > 0:
                    print(f"📊 Generando gráficas con {len(data_source['param'])} puntos (fuente: {source_name})")
                    bode_fig = create_bode_plot_from_dataset(data_source, negative_phase, theme)
                    nyquist_fig = create_nyquist_plot_from_dataset(data_source, theme)
                else:
                    safe_print(f"⚠️ No hay datos disponibles - manteniendo gráficas actuales")
            else:
                safe_print(f"📊 Gráficas ya actualizadas durante procesamiento - mantener")
            
            # Log de control del interval para debugging
            safe_print(f"🔄 Return interval state - Thread alive: {sweep_thread and sweep_thread.is_alive()}, Queue empty: {sweep_queue.empty()}, Interval disabled: {interval_disabled}")
            
            # Determinar si debe activarse el intervalo de cierre del modal
            # Solo se activa cuando el sweep se completa exitosamente (100%)
            # Si ya fue establecido en el bloque 'completed', no sobrescribir
            if 'modal_close_interval_disabled' not in locals():
                modal_close_interval_disabled = not sweep_completed  # False cuando sweep completo (habilitar intervalo)
            
            print(f"🔔 Modal close interval: disabled={modal_close_interval_disabled}, sweep_completed={sweep_completed}")
            
            # CRÍTICO: Si no hay mensaje en la cola Y el sweep está en progreso, NO actualizar progreso
            # Dejar que poll_sweep_streaming sea el ÚNICO que actualice durante el sweep
            if not has_new_data and sweep_thread and sweep_thread.is_alive():
                # Sweep en progreso pero sin mensaje - NO actualizar progreso
                return (bode_fig, nyquist_fig, modal_style, modal_class, 
                       dash.no_update, dash.no_update, dash.no_update,  # NO actualizar progreso
                       status_text, status_text, stored_data, sweep_completed_trigger, 
                       interval_disabled, modal_close_interval_disabled, streaming_interval_disabled)
            
            # Si hay mensaje o el sweep no está en progreso, actualizar normalmente
            return (bode_fig, nyquist_fig, modal_style, modal_class, progress_style, progress_text, str(progress_value), status_text, status_text, stored_data, sweep_completed_trigger, interval_disabled, modal_close_interval_disabled, streaming_interval_disabled)

        except (BrokenPipeError, IOError):
            # Ignorar errores de pipe roto (terminal cerrado)
            empty_bode = create_empty_figure("Error")
            empty_nyquist = create_empty_figure("Error")
            return (empty_bode, empty_nyquist, {'display': 'none'}, 'modal fade', {'width': '0%'}, "0%", "0",
                    "❌ Error de comunicación", "❌ Error de comunicación",
                    {'param': [], 'z_real': [], 'z_imag': [], 'z_mag': [], 'phase': []}, False, True, True, True)  # all intervals disabled
        except Exception as e:
            try:
                print(f"Error en callback manage_sweep: {e}")
                import traceback
                traceback.print_exc()
            except (BrokenPipeError, IOError):
                pass  # Ignorar si no se puede imprimir
            empty_bode = create_empty_figure("Error")
            empty_nyquist = create_empty_figure("Error")
            return (empty_bode, empty_nyquist, {'display': 'none'}, 'modal fade', {'width': '0%'}, "0%", "0",
                    f"❌ Error interno: {str(e)}", f"❌ Error interno: {str(e)}",
                    {'param': [], 'z_real': [], 'z_imag': [], 'z_mag': [], 'phase': []}, False, True, True, True)  # all inte rvals disabled

    # Callback para alternar tema de gráficos
    @app.callback(
        [Output('theme-store', 'data'),
         Output('theme-icon', 'className'),
         Output('bode-plot', 'figure', allow_duplicate=True),
         Output('nyquist-plot', 'figure', allow_duplicate=True)],
        Input('theme-toggle-btn', 'n_clicks'),
        [State('theme-store', 'data'),
         State('sweep-data-store', 'data'),
         State('phase-negative-store', 'data')],
        prevent_initial_call=True
    )
    def toggle_chart_theme(n_clicks, current_theme, stored_data, negative_phase):
        """Alterna entre tema oscuro y claro para los gráficos"""
        if current_theme == 'dark':
            new_theme = 'light'
            icon_class = 'fas fa-sun'
        else:
            new_theme = 'dark'
            icon_class = 'fas fa-moon'
        
        print(f"🎨 Cambiando tema de gráficos: {current_theme} → {new_theme}")
        
        # Actualizar gráficos con el nuevo tema si hay datos
        if stored_data and len(stored_data.get('param', [])) > 0:
            bode_fig = create_bode_plot_from_dataset(stored_data, negative_phase, new_theme)
            nyquist_fig = create_nyquist_plot_from_dataset(stored_data, new_theme)
        else:
            bode_fig = create_empty_figure("Sin datos - Ejecute un barrido", new_theme)
            nyquist_fig = create_empty_figure("Sin datos - Ejecute un barrido", new_theme)
        
        return new_theme, icon_class, bode_fig, nyquist_fig
    
    # Callback para actualizar icono del tema al cargar página
    @app.callback(
        Output('theme-icon', 'className', allow_duplicate=True),
        Input('url', 'pathname'),
        State('theme-store', 'data'),
        prevent_initial_call=False
    )
    def update_theme_icon_on_load(pathname, theme):
        """Actualiza el icono del botón de tema al cargar la página"""
        if theme == 'light':
            return 'fas fa-sun'
        else:
            return 'fas fa-moon'
    
    # Callback para resetear trigger de conexión exitosa después de mostrar la notificación
    @app.callback(
        Output('connection-success-trigger', 'data', allow_duplicate=True),
        Input('connection-success-trigger', 'data'),
        prevent_initial_call=True
    )
    def reset_connection_success_trigger(trigger):
        """Resetea el trigger después de mostrarse para permitir futuras notificaciones"""
        if trigger is True:
            return False
        raise PreventUpdate

    # Callback para resetear trigger de error de conexión después de mostrar la alerta
    @app.callback(
        Output('connection-error-trigger', 'data', allow_duplicate=True),
        Input('connection-error-trigger', 'data'),
        prevent_initial_call=True
    )
    def reset_connection_error_trigger(trigger):
        """Resetea el trigger después de mostrarse para evitar alertas repetidas."""
        if trigger is True:
            return False
        raise PreventUpdate
    
    # Callback para notificación de conexión exitosa (Toast)
    @SPA_NOTIFY.update(
        Input('connection-success-trigger', 'data'),
        prevent_initial_call=True
    )
    def notify_connection_success(trigger, store):
        """Muestra toast de éxito cuando el dispositivo se conecta"""
        print(f"notify_connection_success ejecutado - trigger: {trigger}")
        # Solo mostrar notificación si el trigger es explícitamente True
        if trigger is True:
            notyf = Notyf(
                message='✅ Dispositivo Conectado - ADMX2001 listo para usar',
                type='success'
            )
            print("Retornando notificación de conexión exitosa")
            return notyf.report()
        return NOUPDATE
    
    # Callback para alerta de error de conexión (SweetAlert)
    @SPA_ALERT.update(Input('connection-error-trigger', 'data'))
    def alert_connection_error(trigger, store):
        """
        Muestra alerta de error cuando falla la conexión.
        Solo se activa si el trigger es True (conexión manual fallida).
        """
        logger.info(f"[DEBUG] alert_connection_error ejecutado con trigger={trigger}, type={type(trigger)}")
        
        # Protección temporal: no mostrar errores en los primeros 3 segundos
        time_since_start = time.time() - APP_START_TIME
        if time_since_start < 3:
            logger.info(f"[DEBUG] Ignorando error - app inicio hace {time_since_start:.1f}s (< 3s)")
            return NOUPDATE
        
        # Solo mostrar alerta si es explícitamente True (no False inicial, no None)
        if trigger is True:
            logger.warning("Mostrando modal de error de conexión")
            alert = Alert(
                '❌ Error de Conexión',
                'No se pudo conectar al dispositivo ADMX2001. Verifique que el cable esté conectado y el puerto sea correcto.',
                icon='error'
            )
            return alert.report()
        
        logger.debug(f"No se muestra alert de error (trigger={trigger})")
        return NOUPDATE
    
    # Callback para alerta de barrido completado (SweetAlert con timer)
    @SPA_ALERT.update(Input('sweep-completed-trigger', 'data'))
    def alert_sweep_completed(trigger, store):
        """Muestra alerta cuando el barrido se completa exitosamente"""
        if trigger:
            alert = Alert(
                '🎉 ¡Barrido Completado!',
                'Se adquirieron exitosamente todos los puntos de medición',
                icon='success',
                timer=3000,
                showConfirmButton=False
            )
            return alert.report()
        return NOUPDATE

    # Callbacks para ventana de gráfico maximizado
    @app.callback(
        [Output('chart-modal', 'style', allow_duplicate=True),
         Output('modal-chart', 'figure'),
         Output('chart-modal-title', 'children')],
        [Input('maximize-bode-btn', 'n_clicks'),
         Input('maximize-nyquist-btn', 'n_clicks')],
        [State('sweep-data-store', 'data'),
         State('phase-negative-store', 'data'),
         State('theme-store', 'data')],
        prevent_initial_call=True
    )
    def show_chart_modal(bode_clicks, nyquist_clicks, stored_data, negative_phase, theme):
        """Muestra la ventana con el gráfico maximizado"""
        if not ctx.triggered:
            raise PreventUpdate
        
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Determinar qué gráfico mostrar
        if triggered_id == 'maximize-bode-btn':
            chart_type = 'bode'
            title_text = "Diagrama de Bode"
        elif triggered_id == 'maximize-nyquist-btn':
            chart_type = 'nyquist'
            title_text = "Diagrama de Nyquist"
        else:
            raise PreventUpdate
        
        # Crear el gráfico maximizado
        if stored_data and len(stored_data.get('param', [])) > 0:
            if chart_type == 'bode':
                fig = create_bode_plot_from_dataset(stored_data, negative_phase, theme)
            else:  # nyquist
                fig = create_nyquist_plot_from_dataset(stored_data, theme)
            
            # Actualizar el layout para la vista maximizada
            fig.update_layout(
                title=None,  # Sin título interno, usamos el del header
                margin=dict(l=60, r=40, t=40, b=60)
            )
        else:
            # Gráfico vacío si no hay datos
            fig = create_empty_figure(f"{title_text} - Sin datos disponibles", theme)
            fig.update_layout(margin=dict(l=60, r=40, t=60, b=60))
        
        return {'display': 'flex'}, fig, title_text

    # Callback para cerrar la ventana de gráfico
    @app.callback(
        Output('chart-modal', 'style', allow_duplicate=True),
        Input('modal-close-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def close_chart_modal(close_clicks):
        """Cierra la ventana de gráfico"""
        return {'display': 'none'}

    # Inicializar ventana arrastrable del gráfico (clientside)
    app.clientside_callback(
        """
        function(style) {
            if (!style || style.display !== 'flex') return window.dash_clientside.no_update;
            
            setTimeout(function() {
                if (!window.DraggableWindows) {
                    console.error('[ChartModal] DraggableWindows no disponible');
                    return;
                }
                
                var win = document.getElementById('chart-modal');
                var header = document.getElementById('chart-modal-header-drag');
                
                if (!win || !header) {
                    console.error('[ChartModal] Elementos no encontrados');
                    return;
                }
                
                // Inicializar si no existe
                if (!window.DraggableWindows.isInitialized('chart-modal')) {
                    console.log('[ChartModal] Inicializando ventana');
                    window.DraggableWindows.init('chart-modal', 'chart-modal-header-drag', {
                        width: 900,
                        height: 650,
                        x: (window.innerWidth - 900) / 2,
                        y: (window.innerHeight - 650) / 2
                    });
                }
                
                // Mostrar ventana
                console.log('[ChartModal] Mostrando ventana');
                window.DraggableWindows.show('chart-modal');
            }, 300);
            
            return window.dash_clientside.no_update;
        }
        """,
        Output('chart-modal-dummy', 'data', allow_duplicate=True),
        Input('chart-modal', 'style'),
        prevent_initial_call=True
    )

    # =========================================================================
    # AUTOCONEXIÓN INTELIGENTE - Callbacks del modal compacto
    # =========================================================================
    
    # Callback de autoconexión inteligente
    @app.callback(
        Output('serial-ports', 'options', allow_duplicate=True),
        Output('serial-ports', 'value', allow_duplicate=True),
        Output('detected-port', 'children'),
        Output('detected-port', 'className'),
        Output('auto-connect-status', 'children'),
        Output('auto-connect-status', 'className'),
        Output('auto-connect-progress', 'style'),
        Output('auto-connect-spinner', 'style'),
        Output('connection-test-result', 'children'),
        Output('connect-btn', 'disabled'),
        Output('connect-btn', 'children'),
        Output('connection-success-trigger', 'data', allow_duplicate=True),
        Output('connection-status-interval', 'disabled', allow_duplicate=True),
        Input('connect-modal', 'style'),
        Input('refresh-ports-btn', 'n_clicks'),
        Input('connection-status-interval', 'n_intervals'),
        State('serial-ports', 'options'),
        prevent_initial_call=True
    )
    def auto_detect_and_connect(modal_style, refresh_clicks, interval_n, current_options):
        """
        Autodetección y AUTOCONEXIÓN inteligente de ADMX2001:
        1. Escanea puertos USB
        2. Identifica candidatos (FTDI, CP210x, etc.)
        3. Testea conexión con *idn
        4. Si responde correctamente, SE CONECTA AUTOMÁTICAMENTE
        """
        
        if ctx.triggered_id is None:
            raise PreventUpdate
        
        # Solo ejecutar si el modal está visible o si se presionó refresh
        modal_visible = modal_style and modal_style.get('display') != 'none'
        is_refresh = ctx.triggered_id == 'refresh-ports-btn'
        
        if not modal_visible and not is_refresh:
            raise PreventUpdate
        
        # Si ya hay dispositivo conectado, deshabilitar interval y retornar estado actual
        if device_state.is_connected and device_state.device is not None:
            return (
                current_options or [], NOUPDATE,
                'Ya conectado', 'has-device',
                "✓ Conectado", "fw-semibold text-success",
                {'width': '100%'}, {'display': 'none'},
                html.Small("", **{'data-i18n': 'dash.device_connected_already'}),
                True, [html.I(className="fas fa-check me-2"), "Conectado"],
                False,
                True  # Deshabilitar interval
            )
        
        try:
            # Detectar puertos
            usb_ports = get_preferred_usb_serial_ports()
            
            if not usb_ports:
                return (
                    [{'label': '❌ No hay puertos USB', 'value': '', 'disabled': True}], '',
                    'Ninguno', '',
                    "❌ Sin dispositivos", "fw-semibold text-danger",
                    {'width': '0%'}, {'display': 'none'},
                    "Conecte el cable USB del ADMX2001",
                    True, [html.I(className="fas fa-plug me-2"), "Conectar"],
                    False,
                    False  # Mantener interval activo para detectar cuando conectan
                )
            
            # Crear opciones para dropdown
            options = []
            candidate_ports = []

            for port in usb_ports:
                is_candidate = is_likely_admx_port(port)
                description = (port.description or 'USB Serial')[:40]
                prefix = '✓' if is_candidate else '○'
                label = f"{prefix} {port.device} - {description}"
                options.append({'label': label, 'value': port.device, 'disabled': False})
                
                if is_candidate:
                    candidate_ports.append(port)

            if not candidate_ports and usb_ports:
                candidate_ports = usb_ports[:1]
            
            # Si las opciones no cambiaron y no es un refresh manual, no actualizar
            if not is_refresh and current_options:
                current_values = {opt.get('value') for opt in current_options if isinstance(opt, dict)}
                new_values = {opt['value'] for opt in options}
                if current_values == new_values:
                    # Opciones no cambiaron, no actualizar
                    options = NOUPDATE
            
            # Probar candidatos y conectar automáticamente al primero válido
            connected_port = None
            test_result = ""
            
            if candidate_ports:
                # Probar primero el TTL esperado; si no aparece exacto, usar el mejor USB disponible.
                for port in candidate_ports[:2]:
                    try:
                        test_result += f"Probando {port.device}... "
                        
                        # Intentar conexión
                        test_device = ADMX2001(port.device, baudrate=115200, timeout=1.2)
                        
                        # Test con *idn
                        response = test_device.send_command('*idn')
                        
                        if response and any(x in str(response).upper() for x in ['ADMX', '2001', 'ANALOG']):
                            # ¡ÉXITO! Conectar permanentemente
                            test_device.set_mdelay(1)
                            test_device.set_tdelay(0)
                            
                            # Registrar en estado global
                            device_state.set_device(test_device, True)
                            
                            connected_port = port.device
                            test_result += "✓ Conectado!"
                            logger.info(f"Auto-conexión exitosa en {port.device}")
                            break
                        else:
                            test_device.close()
                            test_result += "✗ No responde; "
                            
                    except Exception as e:
                        test_result += f"✗ {str(e)[:20]}; "
                        continue
            
            # Si se conectó exitosamente
            if connected_port:
                return (
                    options if options != NOUPDATE else current_options, connected_port,
                    connected_port, 'has-device',
                    "✓ Conectado", "fw-semibold text-success",
                    {'width': '100%'}, {'display': 'none'},
                    html.Small(test_result, className="text-muted"),
                    True, [html.I(className="fas fa-check-circle me-2"), "Conectado"],
                    True,  # Trigger notificación
                    True  # Deshabilitar interval al conectar
                )
            
            # Si no se pudo conectar a ninguno
            return (
                options if options != NOUPDATE else current_options, '',
                'Sin respuesta', '',
                "⚠ No detectado", "fw-semibold text-warning",
                {'width': '100%'}, {'display': 'none'},
                html.Small(test_result or "No se detectó USB TTL232R-3V3"),
                False, [html.I(className="fas fa-plug me-2"), "Conectar Manual"],
                False,
                False  # Mantener interval activo para seguir buscando
            )
            
        except Exception as e:
            logger.error(f"Error en autoconexión: {e}")
            return (
                [{'label': f'❌ Error: {str(e)[:20]}', 'value': '', 'disabled': True}], '',
                'Error', '',
                "❌ Error de escaneo", "fw-semibold text-danger",
                {'width': '0%'}, {'display': 'none'},
                str(e)[:50],
                False, [html.I(className="fas fa-times me-2"), "Reintentar"],
                False,
                False  # Mantener interval activo
            )
    
    # =============================================================================
    # NOTA: Callbacks del terminal movidos a app.py (global)
    # =============================================================================
    
    # Callback para abrir modal de CSV
    @app.callback(
        Output('csv-modal', 'style', allow_duplicate=True),
        Output('csv-modal', 'className', allow_duplicate=True),
        Input('load-csv-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def open_csv_modal(n_clicks):
        """Abre el modal para cargar archivos CSV"""
        return {'display': 'block'}, 'modal fade show'

    # Callback para guardar datos del barrido en CSV
    @app.callback(
        Output('download-csv', 'data'),
        Input('save-csv-btn', 'n_clicks'),
        State('sweep-data-store', 'data'),
        prevent_initial_call=True
    )
    def save_csv(n_clicks, stored_data):
        """Guarda los datos del barrido actual en un archivo CSV"""
        if not stored_data or len(stored_data.get('param', [])) == 0:
            # No hay datos para guardar
            raise PreventUpdate
        
        try:
            import csv
            import os
            from io import StringIO

            trigger_runs = stored_data.get('runs') or []

            # Si hay múltiples barridos guardados por trigger, exportar todo en un solo CSV
            if trigger_runs:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"trigger_sweeps_{timestamp}.csv"
                os.makedirs('data', exist_ok=True)
                filepath = os.path.join('data', filename)

                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['run_index', 'frequency_hz', 'z_real_ohm', 'z_imag_ohm', 'z_magnitude_ohm', 'phase_rad', 'phase_deg']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()

                    for run in trigger_runs:
                        run_index = run.get('run_index', 1)
                        run_len = len(run.get('param', []))
                        for i in range(run_len):
                            phase_rad = run['phase'][i]
                            writer.writerow({
                                'run_index': run_index,
                                'frequency_hz': run['param'][i],
                                'z_real_ohm': run['z_real'][i],
                                'z_imag_ohm': run['z_imag'][i],
                                'z_magnitude_ohm': run['z_mag'][i],
                                'phase_rad': phase_rad,
                                'phase_deg': np.degrees(phase_rad),
                            })

                with open(filepath, 'r', encoding='utf-8') as f:
                    csv_content = f.read()

                return dict(content=csv_content, filename=filename, type='text/csv')

            # Usar la función de utils para guardar CSV
            from lib.utils import save_sweep_data_to_csv
            
            # Crear datos en el formato esperado por la función
            sweep_data = {
                'param': stored_data['param'],
                'z_real': stored_data['z_real'],
                'z_imag': stored_data['z_imag'],
                'z_mag': stored_data['z_mag'],
                'phase': stored_data['phase']
            }
            
            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sweep_data_{timestamp}.csv"
            
            # Guardar CSV y obtener el nombre del archivo
            saved_filename = save_sweep_data_to_csv(sweep_data, filename)
            
            # Leer el contenido del archivo para la descarga
            filepath = os.path.join('data', saved_filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                csv_content = f.read()
            
            # Retornar datos para descarga
            return dict(content=csv_content, filename=saved_filename, type='text/csv')
            
        except Exception as e:
            print(f"Error guardando CSV: {e}")
            raise PreventUpdate

    # Callback para actualizar lista de archivos CSV disponibles
    @app.callback(
        Output('csv-files-list', 'children'),
        Input('csv-modal', 'style'),
        prevent_initial_call=True
    )
    def update_csv_files_list(modal_style):
        """Actualiza la lista de archivos CSV disponibles cuando se abre el modal"""
        if modal_style and modal_style.get('display') == 'block':
            try:
                from lib.utils import list_csv_files
                csv_files = list_csv_files()
                
                if not csv_files:
                    return html.P("", className="text-muted", **{'data-i18n': 'dash.no_csv_files'})
                
                # Crear lista de archivos
                file_list = []
                for filename in csv_files:
                    file_list.append(
                        html.Div([
                            html.I(className="fas fa-file-csv me-2 text-success"),
                            html.Span(filename, className="me-2"),
                            html.Small("", className="text-muted", **{'data-i18n': 'dash.csv_tag'})
                        ], className="d-flex align-items-center mb-1")
                    )
                
                return html.Div(file_list)
                
            except Exception as e:
                return html.P(f"Error al listar archivos CSV: {str(e)}", className="text-danger")
        
        return ""

    # Callback para manejar subida de archivos CSV
    @app.callback(
        [Output('csv-upload-status', 'children'),
         Output('csv-upload-store', 'data'),
         Output('csv-modal', 'style', allow_duplicate=True),
         Output('csv-modal', 'className', allow_duplicate=True)],
        Input('upload-csv', 'contents'),
        State('upload-csv', 'filename'),
        prevent_initial_call=True
    )
    def handle_csv_upload(contents, filename):
        """Maneja la subida de archivos CSV"""
        if contents is None:
            raise PreventUpdate
        
        try:
            # Decodificar contenido del archivo
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            # Leer como CSV
            csv_data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            
            # Validar columnas requeridas
            required_columns = ['frequency_hz', 'z_real_ohm', 'z_imag_ohm', 'z_magnitude_ohm', 'phase_rad', 'phase_deg']
            missing_columns = [col for col in required_columns if col not in csv_data.columns]
            
            if missing_columns:
                status = f"❌ Columnas faltantes: {', '.join(missing_columns)}"
                return status, None, {'display': 'block'}, 'modal fade show'
            
            # Validar que hay datos
            if len(csv_data) == 0:
                status = "❌ El archivo CSV está vacío"
                return status, None, {'display': 'block'}, 'modal fade show'
            
            # Convertir a formato interno
            loaded_data = {
                'param': csv_data['frequency_hz'].tolist(),
                'z_real': csv_data['z_real_ohm'].tolist(),
                'z_imag': csv_data['z_imag_ohm'].tolist(),
                'z_mag': csv_data['z_magnitude_ohm'].tolist(),
                'phase': csv_data['phase_rad'].tolist()  # Usar radianes para consistencia interna
            }
            
            # Guardar en store temporal (esto se manejará en el callback de confirmación)
            # Por ahora solo mostrar éxito
            status = f"✅ Archivo '{filename}' cargado exitosamente ({len(csv_data)} puntos). Haz clic en 'Cargar Datos' para mostrar los gráficos."
            
            return status, loaded_data, {'display': 'block'}, 'modal fade show'
            
        except Exception as e:
            status = f"❌ Error al procesar archivo CSV: {str(e)}"
            return status, None, {'display': 'block'}, 'modal fade show'

    # Callback para confirmar carga de datos CSV
    @app.callback(
        [Output('sweep-data-store', 'data', allow_duplicate=True),
         Output('bode-plot', 'figure', allow_duplicate=True),
         Output('nyquist-plot', 'figure', allow_duplicate=True),
         Output('csv-modal', 'style', allow_duplicate=True),
         Output('csv-modal', 'className', allow_duplicate=True)],
        Input('confirm-load-csv-btn', 'n_clicks'),
        State('csv-upload-store', 'data'),
        State('phase-negative-store', 'data'),
        State('theme-store', 'data'),
        prevent_initial_call=True
    )
    def confirm_load_csv(n_clicks, csv_data, negative_phase, theme):
        """Confirma la carga de datos CSV y actualiza las gráficas"""
        if not csv_data:
            raise PreventUpdate
        
        try:
            # Actualizar gráficas con los datos cargados
            bode_fig = create_bode_plot_from_dataset(csv_data, negative_phase, theme)
            nyquist_fig = create_nyquist_plot_from_dataset(csv_data, theme)
            
            # Cerrar modal
            return csv_data, bode_fig, nyquist_fig, {'display': 'none'}, 'modal fade'
            
        except Exception as e:
            print(f"Error cargando datos CSV: {e}")
            raise PreventUpdate

    # ========== CALLBACK PARA STREAMING DE SWEEP EN TIEMPO REAL ==========
    @app.callback(
        [Output('bode-plot', 'figure', allow_duplicate=True),
         Output('nyquist-plot', 'figure', allow_duplicate=True),
         Output('sweep-data-store', 'data', allow_duplicate=True),
         Output('sweep-progress-bar', 'style', allow_duplicate=True),
         Output('sweep-progress-bar', 'children', allow_duplicate=True),
         Output('sweep-progress-bar', 'aria-valuenow', allow_duplicate=True),
         Output('sweep-streaming-interval', 'disabled', allow_duplicate=True)],
        Input('sweep-streaming-interval', 'n_intervals'),
        [State('sweep-data-store', 'data'),
         State('phase-negative-store', 'data'),
         State('theme-store', 'data'),
         State('bode-plot', 'figure'),
         State('nyquist-plot', 'figure')],
        prevent_initial_call=True
    )
    def poll_sweep_streaming(n_intervals, current_data, negative_phase, theme, bode_fig, nyquist_fig):
        """Poll para obtener nuevos puntos del sweep y actualizar gráficos en tiempo real"""
        import numpy as np
        
        global last_sweep_point_count, intervals_without_new_points
        
        # Inicializar current_data si es None o vacío
        if not current_data:
            current_data = {'param': [], 'z_real': [], 'z_imag': [], 'z_mag': [], 'phase': []}
        
        current_point_count = len(current_data.get('param', []))
        
        print(f"[Sweep Poll] n_intervals={n_intervals}, sweep_in_progress={device_state.is_sweep_in_progress()}, puntos_actuales={current_point_count}")
        
        # Verificar si hay sweep en progreso
        if not device_state.is_sweep_in_progress():
            # No hay sweep, desactivar interval y resetear contadores
            print(f"[Sweep Poll] Sweep no en progreso - desactivando interval y limpiando buffer")
            last_sweep_point_count = 0
            intervals_without_new_points = 0
            # Limpiar current_data para el próximo sweep
            current_data = {'param': [], 'z_real': [], 'z_imag': [], 'z_mag': [], 'phase': []}
            return bode_fig, nyquist_fig, current_data, dash.no_update, dash.no_update, dash.no_update, True
        
        # Detectar sweeps "abandonados" (sin nuevos puntos por tiempo prolongado)
        if current_point_count == last_sweep_point_count:
            intervals_without_new_points += 1
            
            # Si han pasado muchos intervalos sin nuevos datos Y hay progreso significativo
            if intervals_without_new_points > MAX_INTERVALS_WITHOUT_DATA:
                current, total, pct = device_state.get_sweep_progress()
                if pct >= 90 and current_point_count > 0:
                    print(f"[Sweep Poll] ⚠️ Sweep abandonado detectado - {intervals_without_new_points} intervalos sin datos, progreso={pct}%")
                    print(f"[Sweep Poll] Finalizando sweep automáticamente...")
                    device_state.end_sweep_streaming()
                    intervals_without_new_points = 0
                    last_sweep_point_count = 0
                    return bode_fig, nyquist_fig, dash.no_update, dash.no_update, dash.no_update, dash.no_update, True
        else:
            # Hay nuevos puntos, resetear contador
            intervals_without_new_points = 0
            last_sweep_point_count = current_point_count
        
        # Obtener nuevos puntos del buffer
        new_points = device_state.get_sweep_points()
        
        if not new_points:
            # No hay puntos nuevos, mantener estado actual
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, False
        
        print(f"[Sweep Poll] ✅ Actualizando gráficos con {len(new_points)} nuevos puntos")

        # Limpiar datos previos EXACTAMENTE al entrar el primer punto del nuevo sweep
        # El primer punto siempre llega con index == 0 (reseteado en start_sweep_streaming)
        first_point_of_new_sweep = any(point.get('index') == 0 for point in new_points)
        if first_point_of_new_sweep and len(current_data.get('param', [])) > 0:
            print(f"[Sweep Poll] 🧹 Primer punto detectado (index=0) - limpiando {len(current_data['param'])} datos previos")
            current_data = {'param': [], 'z_real': [], 'z_imag': [], 'z_mag': [], 'phase': []}
        
        # Agregar nuevos puntos a los datos actuales
        for point in new_points:
            current_data['param'].append(point['freq'])
            current_data['z_real'].append(point['z_real'])
            current_data['z_imag'].append(point['z_imag'])
            current_data['z_mag'].append(point['z_mag'])
            current_data['phase'].append(point['phase'])
        
        print(f"[Sweep Poll] Total de puntos en gráficos: {len(current_data['param'])}")
        
        # Actualizar gráficos con todos los datos (incluidos los nuevos)
        if len(current_data['param']) > 0:
            bode_fig = create_bode_plot_from_dataset(current_data, negative_phase, theme)
            nyquist_fig = create_nyquist_plot_from_dataset(current_data, theme)
        
        # Actualizar progreso
        current, total, pct = device_state.get_sweep_progress()
        progress_style = {'width': f'{pct}%'}
        progress_text = f"{pct}%"
        
        # IMPORTANTE: Retornar current_data actualizado para que persista entre polls
        return bode_fig, nyquist_fig, current_data, progress_style, progress_text, str(pct), False

    # ── Clientside: actualizar ícono y clase de la barra de estado del sweep ──
    app.clientside_callback(
        """
        function(statusText) {
            if (!statusText) {
                return [
                    'fas fa-circle-info me-1 text-secondary',
                    'sweep-status-bar mt-3 d-flex flex-wrap align-items-center gap-3'
                ];
            }
            var t = statusText.toString();
            if (t.indexOf('✅') !== -1 || t.indexOf('completado') !== -1) {
                return [
                    'fas fa-circle-check me-1 text-success',
                    'sweep-status-bar completed mt-3 d-flex flex-wrap align-items-center gap-3'
                ];
            }
            if (t.indexOf('❌') !== -1 || t.indexOf('Error') !== -1) {
                return [
                    'fas fa-circle-xmark me-1 text-danger',
                    'sweep-status-bar error mt-3 d-flex flex-wrap align-items-center gap-3'
                ];
            }
            if (t.length > 0) {
                return [
                    'fas fa-circle-notch fa-spin me-1 text-primary',
                    'sweep-status-bar running mt-3 d-flex flex-wrap align-items-center gap-3'
                ];
            }
            return [
                'fas fa-circle-info me-1 text-secondary',
                'sweep-status-bar mt-3 d-flex flex-wrap align-items-center gap-3'
            ];
        }
        """,
        [Output('sweep-status-icon', 'className'),
         Output('sweep-status-bar', 'className', allow_duplicate=True)],
        Input('sweep-status', 'children'),
        prevent_initial_call=True
    )

# ==================== FUNCIONES AUXILIARES ====================

def create_dashboard_page():
    """Crea la página del dashboard ZORIA"""
    return layout

def register_dashboard_page(app):
    """Registra la página del dashboard en la aplicación DashSPA"""
    register_page(
        __name__,
        path="/",
        title="ZORIA Dashboard",
        name="Dashboard",
        layout=layout
    )
    # Registrar los callbacks
    register_callbacks(app)
