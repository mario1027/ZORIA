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
from lib.utils import clean_response_line

# Importar componentes comunes compartidos
from pages.common.sidebar import sideBar
from pages.common.mobile_nav import mobileNavBar
from pages.common.footer import footer

# ==================== CONFIGURACIÓN GLOBAL ====================

# Logger
logger = logging.getLogger(__name__)

# Variables globales para el estado del sistema
device = None
is_connected = threading.Event()
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

# Configuración de medición
measurement_config = {
    'display_mode': 6,
    'frequency': 1000,
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
        ports = serial.tools.list_ports.comports()
        admx_ports = []

        for port in ports:
            # Buscar puertos que podrían ser el ADMX2001
            description = port.description.upper()
            manufacturer = (port.manufacturer or '').upper()
            device_name = port.device.upper()

            # Criterios más amplios para identificar dispositivos seriales USB
            if ('USB' in description or 'SERIAL' in description or
                'FTDI' in manufacturer or 'SILICON' in manufacturer or
                'CP210' in description or 'CH340' in description or
                'TTL232' in description or 'PL2303' in description or
                'FT232' in description or device_name.startswith('/DEV/TTYUSB') or
                device_name.startswith('/DEV/TTYACM')):
                admx_ports.append(port)

        return admx_ports
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
            font=dict(size=14, color=annotation_color)
        )],
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=text_color, size=12, family="Arial, sans-serif"),
        title_font=dict(color=text_color, size=16)
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

    # Magnitud - asegurar valores positivos para log
    mag_db = [20 * np.log10(max(z, 1e-12)) for z in z_mag]
    print(f"Magnitud en dB: primeros valores {mag_db[:3]}")

    fig.add_trace(go.Scatter(
        x=param,
        y=mag_db,  # Convertir a dB
        mode='lines+markers',
        name='|Z| (dB)',
        line=dict(color=mag_color, width=2),
        marker=dict(size=4, color=mag_color),
        yaxis="y1",
        hovertemplate='<b>Frecuencia:</b> %{x:.2f} Hz<br><b>|Z|:</b> %{y:.2f} dB<extra></extra>'
    ))

    # Fase - aplicar signo según configuración del checkbox
    if phase and len(phase) > 0:
        # Si negative_phase=True, usar fase negativa; si False, usar fase positiva
        phase_deg = [-np.degrees(p) if negative_phase else np.degrees(p) for p in phase]
        print(f"Fase ({'negativa' if negative_phase else 'positiva'}): primeros valores {phase_deg[:3]}")
        fig.add_trace(go.Scatter(
            x=param,
            y=phase_deg,
            mode='lines+markers',
            name='Fase (°)',
            line=dict(color=phase_color, width=2),
            marker=dict(size=4, color=phase_color),
            yaxis="y2",
            hovertemplate='<b>Frecuencia:</b> %{x:.2f} Hz<br><b>Fase:</b> %{y:.2f}°<extra></extra>'
        ))

    fig.update_layout(
        title=f"Diagrama de Bode",
        xaxis=dict(
            title="Frecuencia (Hz)",
            type="log",
            autorange=True,
            showgrid=True,
            gridcolor=grid_color,
            linecolor=text_color,
            tickcolor=text_color,
            tickfont=dict(color=text_color),
            title_font=dict(color=text_color)
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
        font=dict(color=text_color, size=12, family="Arial, sans-serif"),
        title_font=dict(color=text_color, size=16),
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

    # Preparar datos para el gráfico - formato estándar de Nyquist
    y_data = [-z for z in z_imag]  # -Z'' para formato estándar
    print(f"Datos Y calculados (-z_imag): {y_data[:3]}...")

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
            x=z_real,
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
            x=z_real,
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
        font=dict(color=text_color, size=12, family="Arial, sans-serif"),
        title_font=dict(color=text_color, size=16),
        hovermode="closest",
        hoverlabel=dict(
            bgcolor=bg_color,
            bordercolor=text_color,
            font=dict(color=text_color)
        )
    )

    print(f"Nyquist plot creado con {len(fig.data)} traces")
    return fig

# ==================== WORKERS ====================

def measurement_worker(config):
    """Worker para mediciones continuas"""
    global device, measurement_data

    try:
        display_mode = config['display_mode']
        frequency = config['frequency']
        mdelay = config['mdelay']
        tdelay = config['tdelay']
        magnitude = config['magnitude']

        while not stop_measurement.is_set():
            if device and is_connected.is_set():
                try:
                    # Configurar medición
                    device.set_display_mode(display_mode)
                    device.set_frequency(frequency)
                    if mdelay >= 0:
                        device.set_measurement_delay(mdelay)
                    if tdelay >= 0:
                        device.set_trigger_delay(tdelay)
                    if magnitude and magnitude != 'auto':
                        # Convertir a float si es string
                        mag_value = float(magnitude) if isinstance(magnitude, str) else magnitude
                        device.set_magnitude(mag_value)

                    # Realizar medición
                    measurement = device.measure()

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
    global device, sweep_data

    try:
        # Extraer parámetros de la configuración recibida
        start = config['start']
        end = config['end']
        points = config['points']
        scale = config['scale']
        display_mode = config['display_mode']
        mdelay = config['mdelay']
        tdelay = config['tdelay']
        magnitude = config.get('magnitude', 1.0)  # Valor por defecto 1.0V
        
        print(f"🔄 WORKER INICIADO - Configuración recibida:")
        print(f"   - Start: {start} Hz, End: {end} Hz")
        print(f"   - Puntos: {points}, Escala: {scale}")
        print(f"   - Display Mode: {display_mode}, MDelay: {mdelay}, TDelay: {tdelay}")
        print(f"   - Magnitud: {magnitude} V")

        # Resetear datos
        global sweep_data
        sweep_data = {'param': [], 'z_real': [], 'z_imag': [], 'z_mag': [], 'phase': []}

        # Configurar dispositivo para barrido
        if device:
            from lib.enums import SweepType, SweepScale
            import numpy as np

            # Configurar delays ANTES del sweep (PRIMERO)
            try:
                if mdelay >= 0:
                    print(f"🔧 Configurando measurement delay: {mdelay} ms")
                    device.set_measurement_delay(mdelay)
                    time.sleep(0.0005)  # Esperar 0.5ms para estabilización del delay
                if tdelay >= 0:
                    print(f"🔧 Configurando trigger delay: {tdelay} ms")
                    device.set_trigger_delay(tdelay)
            except Exception as e:
                print(f"⚠️ Error configurando delays: {e}")

            # Configurar magnitud ANTES del sweep
            if magnitude and magnitude != 'auto':
                try:
                    mag_value = float(magnitude) if isinstance(magnitude, str) else magnitude
                    print(f"🔧 Configurando magnitud: {mag_value} V")
                    device.set_magnitude(mag_value)
                except Exception as e:
                    print(f"⚠️ Error configurando magnitud: {e}")

            # Convertir escala
            sweep_scale = SweepScale.LOG if scale == 'log' else SweepScale.LINEAR

            # SEGMENTACIÓN: El ADMX2001 tiene límite de 255 puntos por barrido
            MAX_POINTS_PER_SEGMENT = 255
            
            if points <= MAX_POINTS_PER_SEGMENT:
                # Barrido simple - sin segmentación
                print(f"📊 Barrido simple: {points} puntos")
                segments = [(start, end, points)]
            else:
                # Barrido segmentado - dividir en múltiples barridos de hasta 255 puntos
                num_segments = (points + MAX_POINTS_PER_SEGMENT - 1) // MAX_POINTS_PER_SEGMENT
                print(f"📊 Barrido segmentado: {points} puntos divididos en {num_segments} segmentos de máximo {MAX_POINTS_PER_SEGMENT} puntos")
                
                # Generar frecuencias para el barrido completo
                if scale == 'log':
                    all_freqs = np.logspace(np.log10(start), np.log10(end), points)
                else:
                    all_freqs = np.linspace(start, end, points)
                
                # Dividir en segmentos
                segments = []
                for i in range(num_segments):
                    seg_start_idx = i * MAX_POINTS_PER_SEGMENT
                    seg_end_idx = min((i + 1) * MAX_POINTS_PER_SEGMENT, points)
                    seg_points = seg_end_idx - seg_start_idx
                    seg_start_freq = all_freqs[seg_start_idx]
                    seg_end_freq = all_freqs[seg_end_idx - 1]
                    segments.append((seg_start_freq, seg_end_freq, seg_points))
                    print(f"  Segmento {i+1}/{num_segments}: {seg_start_freq:.1f} Hz - {seg_end_freq:.1f} Hz ({seg_points} puntos)")

            # Ejecutar barrido(s) - uno o múltiples segmentos
            all_results = []
            for seg_idx, (seg_start, seg_end, seg_points) in enumerate(segments):
                if len(segments) > 1:
                    print(f"🔄 Ejecutando segmento {seg_idx+1}/{len(segments)}: {seg_start:.1f}-{seg_end:.1f} Hz, {seg_points} puntos")
                
                # Configurar barrido para este segmento (valores en kHz)
                print(f"📋 CONFIGURANDO SWEEP:")
                print(f"   Tipo: FREQUENCY")
                print(f"   Start: {seg_start:.1f} Hz ({seg_start/1000:.3f} kHz)")
                print(f"   End: {seg_end:.1f} Hz ({seg_end/1000:.3f} kHz)")
                print(f"   Scale: {sweep_scale}")
                print(f"   Count: {seg_points} puntos ← IMPORTANTE")
                
                device.configure_sweep(
                    SweepType.FREQUENCY,
                    seg_start / 1000,  # Convertir Hz a kHz
                    seg_end / 1000,    # Convertir Hz a kHz
                    sweep_scale,
                    seg_points
                )
                
                print(f"✅ Sweep configurado - esperando {seg_points} puntos")

                # Ejecutar barrido del segmento
                # Ajustar timeout para coincidir con el timeout del dispositivo (3s por punto)
                if seg_points > 100:
                    sweep_timeout = max(180, 120 + seg_points * 3)  # Para segmentos grandes
                else:
                    sweep_timeout = max(120, 60 + seg_points * 3)   # 3s por punto
                print(f"  Iniciando segmento con timeout: {sweep_timeout}s ({sweep_timeout/seg_points:.1f}s por punto)")
                
                # Enviar progreso inicial para este segmento
                segment_start_point = sum(seg[2] for seg in segments[:seg_idx])
                sweep_queue.put({
                    'current': segment_start_point,
                    'total': points,
                    'freq': seg_start,
                    'z_real': 0,
                    'z_imag': 0,
                    'update_graphs': False
                })
                
                # Ejecutar barrido (bloqueante)
                import time
                import threading
                
                segment_results = None
                acquisition_complete = threading.Event()
                
                def acquire_segment():
                    nonlocal segment_results
                    segment_results = device.perform_sweep(timeout=sweep_timeout)
                    acquisition_complete.set()
                
                # Iniciar adquisición en thread separado
                acq_thread = threading.Thread(target=acquire_segment, daemon=True)
                acq_thread.start()
                
                # Simular progreso mientras se adquiere
                start_time = time.time()
                estimated_duration = seg_points * 0.15  # ~150ms por punto estimado
                last_progress = 0
                
                while not acquisition_complete.is_set():
                    elapsed = time.time() - start_time
                    # Progreso estimado basado en tiempo (máximo 95% hasta que termine realmente)
                    estimated_progress = min(0.95, elapsed / estimated_duration)
                    current_estimated_point = segment_start_point + int(seg_points * estimated_progress)
                    
                    # Enviar actualización de progreso cada 5%
                    progress_pct = int((current_estimated_point / points) * 100)
                    if progress_pct > last_progress and progress_pct % 5 == 0:
                        sweep_queue.put({
                            'current': current_estimated_point,
                            'total': points,
                            'freq': seg_start + (seg_end - seg_start) * estimated_progress,
                            'z_real': 0,
                            'z_imag': 0,
                            'update_graphs': False
                        })
                        last_progress = progress_pct
                        print(f"  Progreso estimado: {progress_pct}%")
                    
                    time.sleep(0.5)  # Actualizar cada 500ms
                
                # Esperar a que termine
                acq_thread.join()
                
                if segment_results:
                    all_results.extend(segment_results)
                    print(f"  ✅ Segmento completado: {len(segment_results)} puntos obtenidos")
                    if len(segment_results) != seg_points:
                        print(f"  ⚠️⚠️⚠️ PROBLEMA: Esperábamos {seg_points} puntos pero obtuvimos {len(segment_results)}")
                        print(f"  ⚠️⚠️⚠️ Faltan {seg_points - len(segment_results)} puntos!")
                    
                    # IMPORTANTE: Enviar progreso al 100% para este segmento
                    segment_end_point = segment_start_point + seg_points
                    final_progress_pct = int((segment_end_point / points) * 100)
                    sweep_queue.put({
                        'current': segment_end_point,
                        'total': points,
                        'freq': seg_end,
                        'z_real': 0,
                        'z_imag': 0,
                        'update_graphs': False
                    })
                    print(f"  📊 Progreso actualizado a {final_progress_pct}% ({segment_end_point}/{points} puntos)")
                else:
                    print(f"  ⚠️ Segmento sin resultados")
            
            results = all_results
            print(f"✅ Barrido completo: {len(results)} puntos totales obtenidos")

            # Procesar resultados DE UNA SOLA VEZ (sin enviar mensajes individuales)
            print(f"📊 Procesando {len(results)} puntos de una sola vez...")
            try:
                for i, point in enumerate(results):
                    # sweep_value viene directamente en Hz (no en kHz)
                    freq_hz = point['sweep_value']
                    measurement = point['measurement']  # Tupla con valores medidos

                    # Los valores medidos dependen del display_mode
                    # Para display_mode=6 (R_X), measurement contiene (Z_real, Z_imag)
                    if len(measurement) >= 2:
                        z_real = measurement[0]
                        z_imag = measurement[1]

                        # Calcular magnitud y fase
                        z_mag = np.sqrt(z_real**2 + z_imag**2)
                        phase = np.arctan2(z_imag, z_real)

                        # Agregar a datos
                        sweep_data['param'].append(freq_hz)
                        sweep_data['z_real'].append(z_real)
                        sweep_data['z_imag'].append(z_imag)
                        sweep_data['z_mag'].append(z_mag)
                        sweep_data['phase'].append(phase)

                print(f"✅ Procesamiento completado: {len(sweep_data['param'])} puntos listos")
                
                # IMPORTANTE: Enviar progreso final al 100% antes del mensaje 'completed'
                sweep_queue.put({
                    'current': points,
                    'total': points,
                    'freq': sweep_data['param'][-1] if sweep_data['param'] else 0,
                    'z_real': sweep_data['z_real'][-1] if sweep_data['z_real'] else 0,
                    'z_imag': sweep_data['z_imag'][-1] if sweep_data['z_imag'] else 0,
                    'update_graphs': False
                })
                print(f"📊 Progreso final: 100% ({points}/{points} puntos)")
                
            except Exception as e:
                print(f"❌ ERROR en procesamiento: {e}")
                import traceback
                traceback.print_exc()
                sweep_queue.put({'error': True, 'message': f'Error procesando datos: {str(e)}'})
                return        # Barrido completado
        final_points = len(sweep_data['param'])
        print(f"WORKER: Barrido completado exitosamente con {final_points} puntos - enviando mensaje completed")
        sweep_queue.put({'completed': True, 'points': final_points})
        print(f"WORKER: Mensaje completed enviado a la cola")

    except Exception as e:
        print(f"WORKER ERROR: Error en sweep worker: {e}")
        import traceback
        traceback.print_exc()
        sweep_queue.put({'error': True, 'message': str(e)})

# ==================== COMPONENTES DE UI ====================

def command_prompt_modal():
    """Modal de command prompt para comunicación directa con ADMX2001"""
    MODAL_ID = 'command-modal'
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
                                html.I(className="fas fa-terminal me-2"),
                                "Command Prompt ADMX2001"
                            ], className='mb-0 h4')
                        ], className='text-center mb-4 mt-md-0'),
                        
                        # Área de terminal/output
                        html.Div([
                            html.Div([
                                html.Pre("", id="command-output", className="bg-dark text-light p-3 rounded", 
                                        style={'height': '300px', 'overflow-y': 'auto', 'font-family': 'monospace', 'font-size': '12px'})
                            ], className="mb-3"),
                            
                            # Input de comando
                            html.Div([
                                html.Div([
                                    html.Span("ADMX2001> ", className="text-primary fw-bold"),
                                    dcc.Input(
                                        id="command-input",
                                        type="text",
                                        placeholder="Escriba comando CLI (ej: 'z', 'frequency 1000', 'help')",
                                        className="form-control d-inline-block",
                                        style={'width': 'calc(100% - 100px)', 'border-radius': '0.375rem 0 0 0.375rem'}
                                    ),
                                    html.Button([
                                        html.I(className="fas fa-paper-plane")
                                    ], id="send-command-btn", className="btn btn-primary", 
                                       style={'border-radius': '0 0.375rem 0.375rem 0'})
                                ], className="input-group")
                            ], className="mb-3"),
                            
                            # Botones de acción
                            html.Div([
                                html.Button("Limpiar Terminal", id="clear-terminal-btn", className="btn btn-warning me-2"),
                                html.Button("Ejecutar 'z'", id="quick-measure-btn", className="btn btn-success me-2"),
                                html.Button("Ejecutar 'help'", id="quick-help-btn", className="btn btn-info me-2"),
                                html.Button("Cerrar", type="button", className="btn btn-secondary", **DISMISS)
                            ], className='d-flex gap-2 flex-wrap')
                        ])
                    ], className='card p-3 p-lg-4')
                ], className='modal-body p-0')
            ], className='modal-content')
        ], className='modal-dialog modal-dialog-centered modal-xl d-flex align-items-center min-vh-100 w-100 mx-auto', role='document')
    ], className='modal fade', id=MODAL_ID, tabIndex='-1', role='dialog', **{"aria-hidden": "true"})

def connect_modal():
    """Modal para conexión/desconexión del dispositivo ADMX2001"""
    MODAL_ID = 'connect-modal'
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
                                html.I(className="fas fa-plug me-2"),
                                "Conectar ADMX2001"
                            ], className='mb-0 h4')
                        ], className='text-center mb-4 mt-md-0'),
                        
                        # Contenido del modal
                        html.Div([
                            # Selector de puerto serial
                            html.Div([
                                html.Label("Puerto Serial", className="form-label fw-bold"),
                                dcc.Dropdown(
                                    id='serial-ports',
                                    options=[{'label': 'Buscando puertos...', 'value': '', 'disabled': True}],
                                    value='',
                                    placeholder="Seleccione un puerto serial",
                                    className="mb-3"
                                )
                            ], className="mb-4"),
                            
                            # Información del dispositivo
                            html.Div([
                                html.H6("Información del Dispositivo", className="fw-bold mb-3"),
                                html.P([
                                    html.I(className="fas fa-info-circle me-2"),
                                    "El ADMX2001 es un analizador de impedancia que se conecta vía puerto serial USB."
                                ], className="text-muted small mb-2"),
                                html.P([
                                    html.I(className="fas fa-cogs me-2"),
                                    "Asegúrese de que el dispositivo esté encendido y conectado correctamente."
                                ], className="text-muted small mb-0")
                            ], className="mb-4"),
                            
                            # Estado de conexión
                            html.Div([
                                html.Span("", id="connect-status", className="text-muted small")
                            ], className="mb-3"),
                            
                            # Botones de acción
                            html.Div([
                                html.Button([
                                    html.I(className="fas fa-plug me-2"),
                                    "Conectar"
                                ], id="connect-btn", className="btn btn-success me-2"),
                                html.Button([
                                    html.I(className="fas fa-power-off me-2"),
                                    "Desconectar"
                                ], id="disconnect-modal-btn", className="btn btn-outline-danger me-2"),
                                html.Button("Cancelar", type="button", className="btn btn-secondary", **DISMISS)
                            ], className='d-flex gap-2 flex-wrap')
                        ])
                    ], className='card p-3 p-lg-4')
                ], className='modal-body p-0')
            ], className='modal-content')
        ], className='modal-dialog modal-dialog-centered modal-lg d-flex align-items-center min-vh-100 w-100 mx-auto', role='document')
    ], className='modal fade', id=MODAL_ID, tabIndex='-1', role='dialog', **{"aria-hidden": "true"})

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
                                html.H6("Formato de Archivo CSV", className="fw-bold mb-3"),
                                html.P([
                                    html.I(className="fas fa-info-circle me-2"),
                                    "El archivo CSV debe contener las siguientes columnas:"
                                ], className="text-muted small mb-2"),
                                html.Ul([
                                    html.Li("frequency_hz: Frecuencia en Hz", className="small"),
                                    html.Li("z_real_ohm: Parte real de la impedancia en Ohm", className="small"),
                                    html.Li("z_imag_ohm: Parte imaginaria de la impedancia en Ohm", className="small"),
                                    html.Li("z_magnitude_ohm: Magnitud de la impedancia en Ohm", className="small"),
                                    html.Li("phase_rad: Fase en radianes", className="small"),
                                    html.Li("phase_deg: Fase en grados", className="small")
                                ], className="text-muted small mb-3")
                            ], className="mb-4"),
                            
                            # Componente de subida de archivos
                            html.Div([
                                html.Label("Seleccionar archivo CSV", className="form-label fw-bold"),
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
                                html.H6("Archivos CSV Disponibles", className="fw-bold mb-3"),
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
                        "Configuración de Barrido"
                    ], className="mb-0")
                ], className="card-header border-bottom border-gray-300 p-3"),
                html.Div([
                    # Primera fila: Frecuencias y puntos
                    html.Div([
                        html.Div([
                            html.Label("Frec. Inicial (Hz)", className="form-label fw-bold small mb-1"),
                            dcc.Input(id='sweep-start', type='number', value=100, min=0.2, max=10000000, className="form-control form-control-sm")
                        ], className="col-6 col-md-2"),
                        html.Div([
                            html.Label("Frec. Final (Hz)", className="form-label fw-bold small mb-1"),
                            dcc.Input(id='sweep-end', type='number', value=100000, min=0.2, max=10000000, className="form-control form-control-sm")
                        ], className="col-6 col-md-2"),
                        html.Div([
                            html.Label("Puntos", className="form-label fw-bold small mb-1"),
                            dcc.Input(id='sweep-points', type='number', value=50, min=2, max=1000, className="form-control form-control-sm")
                        ], className="col-6 col-md-2"),
                        html.Div([
                            html.Label("Escala", className="form-label fw-bold small mb-1"),
                            dcc.Dropdown(id="sweep-scale", options=[
                                {'label': 'Log', 'value': 'log'},
                                {'label': 'Lineal', 'value': 'linear'}
                            ], value="log", clearable=False, className="mb-0")
                        ], className="col-6 col-md-2"),
                        html.Div([
                            html.Label("Modo", className="form-label fw-bold small mb-1"),
                            dcc.Dropdown(id="sweep-display-mode", options=[
                                {'label': 'R-X', 'value': '6'},
                                {'label': 'Z-θ', 'value': '1'},
                                {'label': 'Y-θ', 'value': '2'}
                            ], value="6", clearable=False, className="mb-0")
                        ], className="col-6 col-md-2"),
                        html.Div([
                            html.Label("Magnitud (V)", className="form-label fw-bold small mb-1"),
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
                            html.Label("M.Delay (ms)", className="form-label fw-bold small mb-1"),
                            dcc.Input(id='sweep-mdelay', type='number', value=-1, placeholder="Auto", className="form-control form-control-sm")
                        ], className="col-6 col-md-2"),
                        html.Div([
                            html.Label("T.Delay (ms)", className="form-label fw-bold small mb-1"),
                            dcc.Input(id='sweep-tdelay', type='number', value=0, className="form-control form-control-sm")
                        ], className="col-6 col-md-2"),
                        html.Div([
                            html.Label("Opciones", className="form-label fw-bold small mb-1 d-block"),
                            dcc.Checklist(
                                id='phase-negative-check',
                                options=[{'label': ' Fase negativa', 'value': 'negative'}],
                                value=[],
                                className="form-check-inline small",
                                inputClassName="form-check-input",
                                labelClassName="form-check-label"
                            )
                        ], className="col-6 col-md-2"),
                        html.Div([
                            html.Label("Acciones", className="form-label fw-bold small mb-1 d-block"),
                            html.Button([html.I(className="fas fa-play me-1"), "Ejecutar"], id="sweep-btn", className="btn btn-gray-800 btn-sm me-1"),
                            html.Button([html.I(className="fas fa-stop me-1"), "Cancelar"], id="cancel-sweep-btn", className="btn btn-danger btn-sm me-1"),
                            html.Button([html.I(className="fas fa-save me-1"), "Guardar CSV"], id="save-csv-btn", className="btn btn-success btn-sm me-1"),
                            html.Button([html.I(className="fas fa-upload me-1"), "Cargar CSV"], id="load-csv-btn", className="btn btn-info btn-sm")
                        ], className="col-12 col-md-6"),
                    ], className="row g-2"),
                    
                    # Estado
                    html.Div([
                        html.Span("", id="sweep-status", className="text-muted small")
                    ], className="mt-2")
                ], className="card-body p-3")
            ], className="card border-0 shadow")
        ], className="col-12")
    ], className="row mb-4")

# ==================== LAYOUT ====================

layout = html.Div([
    # Mobile Navbar (solo visible en móvil)
    mobileNavBar(),
    
    # Contenedor flex para sidebar y contenido principal
    html.Div([
        # Sidebar (navegación izquierda)
        sideBar(),
        
        # Contenido principal - aprovecha todo el espacio horizontal disponible
        html.Main([
            dcc.Location(id='url', refresh=False),
            
            # Contenedor principal con fondo
            html.Div([
                # Header optimizado con botón de conexión
                html.Div([
                    html.Div([
                        html.H2("ZORIA Dashboard", className="h3 mb-0")
                ], className="col-12 col-md-6 mb-2 mb-md-0"),
                html.Div([
                    # Botón de alternancia de tema
                    html.Button([
                        html.I(className="fas fa-moon", id="theme-icon")
                    ], id="theme-toggle-btn", className="btn btn-outline-secondary me-2", title="Cambiar tema"),
                    html.Button([
                        html.I(className="fas fa-plug me-2"),
                        "Conectar Dispositivo"
                    ], id="open-connect-modal", className="btn btn-gray-800 me-2", **{"data-bs-toggle": "modal", "data-bs-target": "#connect-modal"}),
                    html.Span("🔌 Desconectado", id="connection-badge", className="badge bg-secondary px-3 py-2"),
                    html.Button([
                        html.I(className="fas fa-power-off me-2"),
                        "Desconectar"
                    ], id="disconnect-btn", className="btn btn-outline-danger ms-2", title="Desconectar dispositivo")
                ], className="col-12 col-md-6 d-flex justify-content-md-end align-items-center gap-2")
            ], className="row align-items-center py-4"),

            # Intervalos de actualización y stores
            dcc.Interval(id='ports-interval', interval=2000, n_intervals=0),
            dcc.Interval(id='measurement-interval', interval=500, n_intervals=0, disabled=True),
            dcc.Interval(id='sweep-interval', interval=1000, n_intervals=0, disabled=True),  # Deshabilitado por defecto - se activa solo durante barrido
            dcc.Interval(id='connection-status-interval', interval=1000, n_intervals=0),
            dcc.Interval(id='modal-close-interval', interval=1000, n_intervals=0, disabled=True),  # Para cerrar modal con delay
            dcc.Store(id='sweep-data-store', storage_type='session', data={'param': [], 'z_real': [], 'z_imag': [], 'z_mag': [], 'phase': []}),  # Persistir datos entre páginas
            dcc.Store(id='phase-negative-store', storage_type='session', data=False),  # Persistir configuración de fase entre páginas
            dcc.Store(id='sweep-completed-trigger', data=False),  # Store para activar alerta de sweep completado
            dcc.Store(id='connection-error-trigger', data=False),  # Store para activar alerta de error de conexión
            dcc.Store(id='connection-success-trigger', data=False),  # Store para activar notificación de conexión exitosa
            dcc.Store(id='modal-close-trigger', data=False),  # Store para controlar cierre del modal con delay
            dcc.Store(id='theme-store', storage_type='local', data='dark'),  # Store para mantener el tema seleccionado
            dcc.Download(id='download-csv'),  # Componente para descargar archivos CSV
            dcc.Store(id='csv-upload-store', data=None),  # Store temporal para datos CSV cargados

            # ✅ PRIORIDAD #1: GRÁFICOS PRIMERO (70% altura visual)
            html.Div([
                # Diagrama de Bode
                html.Div([
                    html.Div([
                        html.Div([
                            html.H5([
                                html.I(className="fas fa-chart-line me-2"),
                                "📊 Diagrama de Bode"
                            ], className="mb-0"),
                            html.Button(
                                html.I(className="fas fa-expand"),
                                id='maximize-bode-btn',
                                className='btn btn-outline-secondary btn-sm ms-2',
                                title='Maximizar gráfico de Bode'
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
                                "📊 Diagrama de Nyquist"
                            ], className="mb-0"),
                            html.Button(
                                html.I(className="fas fa-expand"),
                                id='maximize-nyquist-btn',
                                className='btn btn-outline-secondary btn-sm ms-2',
                                title='Maximizar gráfico de Nyquist'
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
            
            # Modal de command prompt
            command_prompt_modal(),
            
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
                                    html.P("Ejecutando barrido de frecuencia...", className="mb-3 text-center"),
                                    html.Div([
                                        html.Div("0%", id="sweep-progress-bar", className="progress-bar progress-bar-striped progress-bar-animated bg-info", 
                                                 role="progressbar", style={'width': '0%'}, **{"aria-valuenow": "0", "aria-valuemin": "0", "aria-valuemax": "100"})
                                    ], className="progress mb-3", style={'height': '25px'}),
                                    html.P("Iniciando...", id="sweep-status-modal", className="text-muted text-center mb-4")
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
    
    # Modal para gráfico maximizado (usando Bootstrap modal con control híbrido)
    html.Div([
        html.Div([
            html.Div([
                # Header del modal
                html.Div([
                    html.H5("Gráfico Maximizado", className="modal-title"),
                    html.Button(
                        type="button",
                        className="btn-close",
                        id="modal-close-btn",
                        **{"data-bs-dismiss": "modal", "aria-label": "Close"}
                    )
                ], className="modal-header"),
                # Body del modal
                html.Div([
                    dcc.Graph(
                        id='modal-chart',
                        style={'height': '75vh'},
                        config={
                            'displayModeBar': True,
                            'displaylogo': False,
                            'scrollZoom': True,
                            'modeBarButtonsToRemove': ['pan2d', 'lasso2d']
                        }
                    )
                ], className="modal-body p-0"),
                # Footer del modal con botón de cerrar
                html.Div([
                    html.Button(
                        "Cerrar",
                        id="modal-close-footer-btn",
                        className="btn btn-secondary",
                        type="button"
                    )
                ], className="modal-footer")
            ], className="modal-content")
        ], className="modal-dialog modal-fullscreen"),
    ], className="modal fade", id="chart-modal", tabIndex="-1", 
       style={'display': 'none'},  # Inicialmente oculto
       role="dialog",
       **{"aria-labelledby": "chart-modal-label", "aria-hidden": "true"}),
    
    # Componente SPA_ALERT para notificaciones
    SPA_ALERT,
    # Componente SPA_NOTIFY para toasts
    SPA_NOTIFY

], className="sc-chart sc-theme-dark d-flex flex-column min-vh-100", id="main-layout")

# ==================== CALLBACKS ====================

def register_callbacks(app):
    # Callback para actualizar puertos seriales
    @app.callback(
        Output('serial-ports', 'options'),
        [Input('connect-btn', 'n_clicks'),
         Input('ports-interval', 'n_intervals')]
    )
    def update_serial_ports(connect_clicks, interval_n):
        """Actualiza la lista de puertos seriales disponibles"""
        try:
            # Primero intentar detectar puertos ADMX2001
            admx_ports = detect_admx2001_ports()
            all_ports = serial.tools.list_ports.comports()

            options = []

            # Agregar puertos ADMX2001 primero
            for port in admx_ports:
                options.append({
                    'label': f"🔌 {port.device} - {port.description} (Posible ADMX2001)",
                    'value': port.device
                })

            # Agregar otros puertos
            for port in all_ports:
                if port not in admx_ports:
                    options.append({
                        'label': f"{port.device} - {port.description}",
                        'value': port.device
                    })

            # Si no hay puertos, mostrar mensaje
            if not options:
                options = [{'label': 'No se encontraron puertos seriales', 'value': '', 'disabled': True}]

            return options

        except Exception as e:
            print(f"Error al detectar puertos seriales: {e}")
            return [{'label': f'Error: {str(e)}', 'value': '', 'disabled': True}]

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
            bode_fig = create_bode_plot(
                stored_data['param'], 
                stored_data['z_mag'], 
                stored_data['phase'],
                negative_phase,
                theme
            )
            nyquist_fig = create_nyquist_plot(
                stored_data['z_real'], 
                stored_data['z_imag'], 
                stored_data['param'],
                theme
            )
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
            bode_fig = create_bode_plot(
                stored_data['param'], 
                stored_data['z_mag'], 
                stored_data['phase'],
                phase_negative,
                theme
            )
            nyquist_fig = create_nyquist_plot(
                stored_data['z_real'], 
                stored_data['z_imag'], 
                stored_data['param'],
                theme
            )
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

    # Callback para gestionar conexión
    @app.callback(
        [Output('connection-badge', 'children'),
         Output('connection-badge', 'className'),
         Output('connection-error-trigger', 'data'),
         Output('connection-success-trigger', 'data')],
        [Input('connect-btn', 'n_clicks'),
         Input('disconnect-btn', 'n_clicks'),
         Input('disconnect-modal-btn', 'n_clicks')],
        State('serial-ports', 'value'),
        prevent_initial_call=True
    )
    def manage_connection(connect_clicks, disconnect_clicks, disconnect_modal_clicks, port):
        """Gestiona la conexión/desconexión del dispositivo"""
        global device

        triggered = ctx.triggered_id

        if triggered == 'connect-btn':
            if not port or port == '':
                return "❌ Seleccione un puerto serial", "badge bg-warning px-3 py-2", False, False

            try:
                global device
                # Conexión con baudrate correcto (115200) y timeout aumentado (5s)
                device = ADMX2001(port, baudrate=115200, timeout=5.0)
                is_connected.set()
                
                # Configurar delays iniciales del dispositivo
                device.set_mdelay(1)  # 1ms measurement delay por defecto
                device.set_tdelay(0)  # Sin trigger delay por defecto
                
                logger.info(f"Dispositivo ADMX2001 conectado en {port}")
                return "✅ Conectado", "badge bg-success px-3 py-2", False, True

            except Exception as e:
                logger.error(f"Error conectando al dispositivo: {e}")
                return f"❌ Error: {str(e)[:50]}", "badge bg-danger px-3 py-2", True, False

        elif triggered in ['disconnect-btn', 'disconnect-modal-btn']:
            try:
                if device:
                    device.close()
                is_connected.clear()
                device = None
                logger.info("Dispositivo desconectado")
                return "🔌 Desconectado", "badge bg-secondary px-3 py-2", False, False

            except Exception as e:
                logger.error(f"Error desconectando: {e}")
                return f"❌ Error: {str(e)[:50]}", "badge bg-danger px-3 py-2", False, False

        return "🔌 Desconectado", "badge bg-secondary px-3 py-2", False, False

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
         Output('modal-close-interval', 'disabled')],  # Control del cierre retardado del modal
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
         State('phase-negative-store', 'data'),  # Ahora es State - solo lee valor
         State('sweep-data-store', 'data'),
         State('theme-store', 'data')],  # 11 states
        prevent_initial_call=True
    )
    def manage_sweep(n_intervals, sweep_clicks, cancel_clicks, cancel_modal_clicks,
                     start, end, points, scale, display_mode, mdelay, tdelay, magnitude, negative_phase, stored_data, theme):
        """Gestiona el barrido de frecuencia y actualización de gráficos"""
        global sweep_thread, sweep_data, sweep_progress, sweep_completed_successfully

        safe_print(f"Callback manage_sweep ejecutado - interval: {n_intervals}, triggered: {ctx.triggered_id}, negative_phase: {negative_phase}")

        # Obtener el ID del elemento que disparó el callback
        triggered = ctx.triggered_id

        # Inicializar variables básicas
        sweep_completed_trigger = False
        # Inicializar gráficas con stored_data si existe, sino gráficas vacías
        # Estas se regenerarán durante el procesamiento si hay nuevos datos
        if stored_data and len(stored_data.get('param', [])) > 0:
            bode_fig = create_bode_plot(stored_data['param'], stored_data['z_mag'], stored_data['phase'], negative_phase, theme)
            nyquist_fig = create_nyquist_plot(stored_data['z_real'], stored_data['z_imag'], stored_data['param'], theme)
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
                # Usar progreso anterior
                progress_value = sweep_progress
                print(f"Progreso actual: {progress_value}%")
                print(f"  Thread alive: {sweep_thread and sweep_thread.is_alive()}, Queue size: {sweep_queue.qsize()}")

                # Procesar cola de sweep para actualizar progreso
                current_point = 0
                has_new_data = False

                # CAMBIO CRÍTICO: Procesar SOLO UN mensaje por ejecución del callback
                # Esto permite que el UI se actualice con cada progreso intermedio
                if not sweep_queue.empty():
                    try:
                        data = sweep_queue.get_nowait()
                        print(f"CALLBACK: Recibido mensaje de cola: {list(data.keys())}")
                        has_new_data = True
                        if 'current' in data:
                            current_point = data['current']
                            total_points = data['total']
                            calculated_progress = int((current_point / total_points) * 100) if total_points > 0 else 0
                            
                            # CRÍTICO: Actualizar TODAS las variables de progreso al mismo valor
                            progress_value = calculated_progress  # aria-valuenow
                            sweep_progress = calculated_progress  # variable global
                            progress_style = {'width': f'{calculated_progress}%'}  # ancho visual
                            progress_text = f"{calculated_progress}%"  # texto mostrado
                            
                            status_text = f"Analizando punto {current_point}/{total_points} - {data.get('freq', 0):.1f} Hz"
                            # modal_class y modal_style se establecerán al final
                            print(f"📊 PROGRESO ACTUALIZADO: {calculated_progress}% (punto {current_point}/{total_points})")

                            # Actualizar gráficos en tiempo real si hay suficientes datos
                            if data.get('update_graphs', False) and sweep_data and len(sweep_data.get('param', [])) >= 3:
                                try:
                                    bode_fig = create_bode_plot(
                                        sweep_data['param'],
                                        sweep_data['z_mag'],
                                        sweep_data['phase'],
                                        negative_phase,
                                        theme
                                    )
                                    nyquist_fig = create_nyquist_plot(
                                        sweep_data['z_real'],
                                        sweep_data['z_imag'],
                                        sweep_data['param'],
                                        theme
                                    )
                                    graphs_updated = True  # Marcar que las gráficas se actualizaron
                                    # Actualizar el store con los datos actuales del sweep
                                    stored_data = {
                                        'param': sweep_data['param'].copy(),
                                        'z_real': sweep_data['z_real'].copy(),
                                        'z_imag': sweep_data['z_imag'].copy(),
                                        'z_mag': sweep_data['z_mag'].copy(),
                                        'phase': sweep_data['phase'].copy()
                                    }
                                except Exception as e:
                                    bode_fig = create_empty_figure("Procesando datos...", theme)
                                    nyquist_fig = create_empty_figure("Procesando datos...", theme)

                        elif 'completed' in data:
                            # CRÍTICO: Actualizar TODAS las variables de progreso al 100%
                            progress_value = 100  # aria-valuenow
                            sweep_progress = 100  # variable global
                            progress_style = {'width': '100%'}  # ancho visual
                            progress_text = "100%"  # texto mostrado
                            
                            status_text = f"✅ Barrido completado: {data['points']} puntos"
                            sweep_completed = True  # Marcar que el sweep se completó
                            sweep_completed_successfully = True  # Marcar que se completó exitosamente
                            # modal_style y modal_class se establecerán al final
                            print(f"🎉 BARRIDO COMPLETADO: 100%")
                            # Forzar actualización inmediata de gráficos cuando se completa el sweep
                            if sweep_data and sweep_data.get('param') and len(sweep_data['param']) > 0:
                                try:
                                    print(f"📊 ACTUALIZANDO GRÁFICAS FINALES: {len(sweep_data['param'])} puntos")
                                    bode_fig = create_bode_plot(
                                        sweep_data['param'],
                                        sweep_data['z_mag'],
                                        sweep_data['phase'],
                                        negative_phase,
                                        theme
                                    )
                                    nyquist_fig = create_nyquist_plot(
                                        sweep_data['z_real'],
                                        sweep_data['z_imag'],
                                        sweep_data['param'],
                                        theme
                                    )
                                    graphs_updated = True  # Marcar que las gráficas se actualizaron
                                    # CRÍTICO: Actualizar el store INMEDIATAMENTE con los datos completos del sweep
                                    stored_data = {
                                        'param': sweep_data['param'].copy(),
                                        'z_real': sweep_data['z_real'].copy(),
                                        'z_imag': sweep_data['z_imag'].copy(),
                                        'z_mag': sweep_data['z_mag'].copy(),
                                        'phase': sweep_data['phase'].copy()
                                    }
                                    print(f"✅ STORED_DATA ACTUALIZADO: {len(stored_data['param'])} puntos")
                                    # Activar trigger para mostrar alerta de sweep completado
                                    sweep_completed_trigger = True
                                except Exception as e:
                                    print(f"❌ ERROR actualizando gráficas: {e}")
                                    bode_fig = create_empty_figure("Error en gráfico de Bode", theme)
                                    nyquist_fig = create_empty_figure("Error en gráfico de Nyquist", theme)
                                    sweep_completed_trigger = False

                        elif 'error' in data:
                            # modal_style = {'display': 'none'}
                            # modal_class = 'modal fade'
                            sweep_progress = 0  # Reiniciar progreso en caso de error
                            progress_value = 0
                            status_text = f"❌ Error: {data['message']}"

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
                if not device or not is_connected.is_set():
                    status_text = "❌ Dispositivo no conectado"
                    progress_style = {'width': '0%'}
                    progress_text = "0%"
                    modal_style = {'display': 'none'}
                    modal_class = 'modal fade'
                    return (bode_fig, nyquist_fig, modal_style, modal_class, progress_style, progress_text, "0", status_text, status_text, stored_data, False, True, True)  # interval disabled, modal-close-interval disabled

                try:
                    # Tomar valores ACTUALES de los inputs, con fallback a valores por defecto
                    start = float(start or 100)
                    end = float(end or 100000)
                    points = int(points or 50)
                    scale = scale or 'log'
                    
                    # Log de los parámetros que se van a usar
                    print(f"🔧 PARÁMETROS DEL BARRIDO:")
                    print(f"   - Frecuencia inicial: {start} Hz")
                    print(f"   - Frecuencia final: {end} Hz")
                    print(f"   - Número de puntos: {points}")
                    print(f"   - Escala: {scale}")
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
                        return (bode_fig, nyquist_fig, modal_style, modal_class, progress_style, progress_text, "0", status_text, status_text, stored_data, False, True, True)  # interval disabled, modal-close-interval disabled

                    if end < min_freq or end > max_freq:
                        status_text = f"❌ Frecuencia final debe estar entre {min_freq} Hz y {max_freq/1000000} MHz"
                        progress_style = {'width': '0%'}
                        progress_text = "0%"
                        modal_style = {'display': 'none'}
                        modal_class = 'modal fade'
                        return (bode_fig, nyquist_fig, modal_style, modal_class, progress_style, progress_text, "0", status_text, status_text, stored_data, False, True, True)  # interval disabled, modal-close-interval disabled

                    if start >= end or points < 2:
                        status_text = "❌ Parámetros inválidos"
                        progress_style = {'width': '0%'}
                        progress_text = "0%"
                        modal_style = {'display': 'none'}
                        modal_class = 'modal fade'
                        return (bode_fig, nyquist_fig, modal_style, modal_class, progress_style, progress_text, "0", status_text, status_text, stored_data, False, True, True)  # interval disabled, modal-close-interval disabled

                    # Crear configuración con los valores actuales
                    config = {
                        'start': start,
                        'end': end,
                        'points': points,
                        'scale': scale,
                        'display_mode': display_mode or 6,
                        'mdelay': mdelay if mdelay is not None else -1,
                        'tdelay': tdelay if tdelay is not None else 0,
                        'magnitude': magnitude or 'auto'
                    }

                    # Prevenir inicio de barrido si ya hay uno activo
                    if sweep_thread and sweep_thread.is_alive():
                        print(f"⚠️ BARRIDO YA EN PROGRESO - Ignorando solicitud duplicada")
                        status_text = "⚠️ Barrido ya en progreso..."
                        # Retornar estado actual sin cambios
                        return (bode_fig, nyquist_fig, modal_style, modal_class, progress_style, progress_text, str(progress_value), status_text, status_text, stored_data, False, False, True)  # interval enabled, modal-close-interval disabled
                    
                    # Iniciar nuevo barrido
                    stop_sweep.clear()
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
                    status_text = "Iniciando barrido..."
                    interval_disabled = False  # HABILITAR interval durante el barrido

                except Exception as e:
                    status_text = f"❌ Error: {str(e)}"
                    progress_style = {'width': '0%'}
                    progress_text = "0%"
                    modal_style = {'display': 'none'}
                    modal_class = 'modal fade'
                    return (bode_fig, nyquist_fig, modal_style, modal_class, progress_style, progress_text, "0", status_text, status_text, stored_data, False, True, True)  # interval disabled, modal-close-interval disabled

            # Detener sweep
            elif triggered in ['cancel-sweep-btn', 'cancel-sweep-modal-btn']:
                stop_sweep.set()
                modal_style = {'display': 'none'}
                modal_class = 'modal fade'
                sweep_progress = 0  # Reiniciar progreso al cancelar
                interval_disabled = True  # DESHABILITAR interval cuando se cancela
                progress_value = 0
                progress_text = "0%"
                status_text = "Barrido cancelado"
                sweep_completed_successfully = False  # Resetear estado de completado

            # Establecer valores por defecto SOLO si no fueron actualizados durante el procesamiento
            # Esto preserva los valores establecidos al procesar mensajes de la cola
            if 'progress_value' not in locals():
                progress_value = sweep_progress  # Usar progreso global
            if 'progress_style' not in locals():
                progress_style = {'width': f'{sweep_progress}%'}
            if 'progress_text' not in locals():
                progress_text = f"{sweep_progress}%"
            if 'status_text' not in locals():
                status_text = "Procesando..." if has_active_sweep else "Listo"
            if 'modal_style' not in locals():
                modal_style = {'display': 'block'} if has_active_sweep else {'display': 'none'}
            if 'modal_class' not in locals():
                modal_class = 'modal fade show' if has_active_sweep else 'modal fade'
            
            print(f"🔍 Valores finales - Progress: {progress_value}%, Style width: {progress_style.get('width')}, Text: {progress_text}")
            
            # Actualizar gráficos SOLO si NO se actualizaron durante el procesamiento de mensajes
            # La bandera graphs_updated se establece a True cuando se procesan mensajes con datos
            if not graphs_updated:
                # Las gráficas NO se actualizaron durante procesamiento - generar con stored_data o sweep_data
                # PRIORIZAR sweep_data si tiene más puntos que stored_data (barrido en curso)
                sweep_points = len(sweep_data.get('param', [])) if sweep_data else 0
                stored_points = len(stored_data.get('param', [])) if stored_data else 0
                
                # Usar sweep_data si tiene datos (barrido activo o recién completado)
                # Usar stored_data solo si sweep_data está vacío (no hay barrido activo)
                if sweep_points > 0:
                    data_source = sweep_data
                    source_name = 'sweep_data'
                elif stored_points > 0:
                    data_source = stored_data
                    source_name = 'stored_data'
                else:
                    data_source = None
                    source_name = 'ninguna'
                
                if data_source and len(data_source.get('param', [])) > 0:
                    print(f"📊 Generando gráficas finales con {len(data_source['param'])} puntos (fuente: {source_name})")
                    bode_fig = create_bode_plot(data_source['param'], data_source['z_mag'], data_source['phase'], negative_phase, theme)
                    nyquist_fig = create_nyquist_plot(data_source['z_real'], data_source['z_imag'], data_source['param'], theme)
                else:
                    safe_print(f"⚠️ No hay datos disponibles - manteniendo gráficas actuales")
            else:
                safe_print(f"📊 Gráficas ya actualizadas durante procesamiento con {len(sweep_data.get('param', []))} puntos - mantener")
            
            # Log de control del interval para debugging
            safe_print(f"🔄 Return interval state - Thread alive: {sweep_thread and sweep_thread.is_alive()}, Queue empty: {sweep_queue.empty()}, Interval disabled: {interval_disabled}")
            
            # Determinar si debe activarse el intervalo de cierre del modal
            # Solo se activa cuando el sweep se completa exitosamente (100%)
            modal_close_interval_disabled = not sweep_completed  # False cuando sweep completo (habilitar intervalo)
            
            return (bode_fig, nyquist_fig, modal_style, modal_class, progress_style, progress_text, str(progress_value), status_text, status_text, stored_data, sweep_completed_trigger, interval_disabled, modal_close_interval_disabled)

        except (BrokenPipeError, IOError):
            # Ignorar errores de pipe roto (terminal cerrado)
            empty_bode = create_empty_figure("Error")
            empty_nyquist = create_empty_figure("Error")
            return (empty_bode, empty_nyquist, {'display': 'none'}, 'modal fade', {'width': '0%'}, "0%", "0",
                    "❌ Error de comunicación", "❌ Error de comunicación",
                    {'param': [], 'z_real': [], 'z_imag': [], 'z_mag': [], 'phase': []}, False, True, True)  # interval disabled, modal-close-interval disabled
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
                    {'param': [], 'z_real': [], 'z_imag': [], 'z_mag': [], 'phase': []}, False, True)  # interval disabled on error

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
            bode_fig = create_bode_plot(
                stored_data['param'], 
                stored_data['z_mag'], 
                stored_data['phase'],
                negative_phase,
                new_theme
            )
            nyquist_fig = create_nyquist_plot(
                stored_data['z_real'], 
                stored_data['z_imag'], 
                stored_data['param'],
                new_theme
            )
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
        """Muestra alerta de error cuando falla la conexión"""
        if trigger:
            alert = Alert(
                '❌ Error de Conexión',
                'No se pudo conectar al dispositivo ADMX2001. Verifique que el cable esté conectado y el puerto sea correcto.',
                icon='error'
            )
            return alert.report()
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

    # Callbacks para modal de gráfico maximizado
    @app.callback(
        [Output('chart-modal', 'style'),
         Output('chart-modal', 'className'),
         Output('modal-chart', 'figure')],
        [Input('maximize-bode-btn', 'n_clicks'),
         Input('maximize-nyquist-btn', 'n_clicks')],
        [State('chart-modal', 'style'),
         State('chart-modal', 'className'),
         State('sweep-data-store', 'data'),
         State('phase-negative-store', 'data'),
         State('theme-store', 'data')],
        prevent_initial_call=True
    )
    def toggle_modal_chart(bode_clicks, nyquist_clicks, current_style, current_class, stored_data, negative_phase, theme):
        """Muestra/oculta el modal con el gráfico maximizado"""
        if not ctx.triggered:
            return {'display': 'none'}, "modal fade", go.Figure()
        
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Determinar si mostrar u ocultar el modal
        is_visible = current_style and current_style.get('display') == 'block'
        
        if is_visible:
            # Ocultar modal
            return {'display': 'none'}, "modal fade", go.Figure()
        else:
            # Mostrar modal
            
            # Determinar qué gráfico mostrar
            if triggered_id == 'maximize-bode-btn':
                chart_type = 'bode'
                title = "Diagrama de Bode - Vista Maximizada"
            elif triggered_id == 'maximize-nyquist-btn':
                chart_type = 'nyquist'
                title = "Diagrama de Nyquist - Vista Maximizada"
            else:
                return {'display': 'none'}, "modal fade", go.Figure()
            
            # Crear el gráfico maximizado
            if stored_data and len(stored_data.get('param', [])) > 0:
                if chart_type == 'bode':
                    fig = create_bode_plot(
                        stored_data['param'], 
                        stored_data['z_mag'], 
                        stored_data['phase'],
                        negative_phase,
                        theme
                    )
                else:  # nyquist
                    fig = create_nyquist_plot(
                        stored_data['z_real'], 
                        stored_data['z_imag'], 
                        stored_data['param'],
                        theme
                    )
                
                # Actualizar el título para la vista maximizada
                fig.update_layout(
                    title={
                        'text': title,
                        'font': {'size': 20, 'color': '#6495ED' if theme == 'dark' else '#333333'}
                    },
                    height=None,  # Usar altura automática para ocupar toda la pantalla
                    margin=dict(l=40, r=40, t=60, b=40)
                )
            else:
                # Gráfico vacío si no hay datos
                fig = create_empty_figure(f"{title} - Sin datos", theme)
                fig.update_layout(
                    title={
                        'text': title,
                        'font': {'size': 20, 'color': '#6495ED' if theme == 'dark' else '#333333'}
                    },
                    height=None,
                    margin=dict(l=40, r=40, t=60, b=40)
                )
            
            return {'display': 'block'}, "modal fade show", fig

    # Callback para cerrar el modal
    @app.callback(
        [Output('chart-modal', 'style', allow_duplicate=True),
         Output('chart-modal', 'className', allow_duplicate=True)],
        [Input('modal-close-btn', 'n_clicks'),
         Input('modal-close-footer-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def close_modal(close_clicks, close_footer_clicks):
        """Cierra el modal cuando se hace clic en el botón de cerrar"""
        return {'display': 'none'}, "modal fade"

    # Callback para actualizar estado de conexión en el modal
    @app.callback(
        Output('connect-status', 'children'),
        Input('connection-status-interval', 'n_intervals'),
        prevent_initial_call=True
    )
    def update_connect_status(n):
        """Actualiza el estado de conexión mostrado en el modal"""
        global device
        
        if device and is_connected.is_set():
            try:
                # Intentar obtener información del dispositivo
                info = "✅ Dispositivo conectado y listo"
                return info
            except Exception as e:
                return f"⚠️ Dispositivo conectado pero con problemas: {str(e)[:30]}..."
        else:
            return "🔌 Dispositivo no conectado - Seleccione un puerto y haga clic en 'Conectar'"

    # Callbacks para command prompt modal
    @app.callback(
        [Output('command-output', 'children'),
         Output('command-input', 'value')],
        [Input('send-command-btn', 'n_clicks'),
         Input('quick-measure-btn', 'n_clicks'),
         Input('quick-help-btn', 'n_clicks'),
         Input('clear-terminal-btn', 'n_clicks')],
        [State('command-input', 'value'),
         State('command-output', 'children')],
        prevent_initial_call=True
    )
    def handle_command(send_clicks, measure_clicks, help_clicks, clear_clicks, command_text, current_output):
        """Maneja los comandos enviados al dispositivo ADMX2001"""
        global device
        
        if not ctx.triggered:
            return current_output or "", ""
        
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Inicializar output si es None
        if current_output is None:
            current_output = ""
        
        # Limpiar terminal
        if triggered_id == 'clear-terminal-btn':
            return "", ""
        
        # Comandos rápidos
        if triggered_id == 'quick-measure-btn':
            command = "z"
        elif triggered_id == 'quick-help-btn':
            command = "help"
        else:
            # Comando desde input
            command = command_text or ""
        
        if not command.strip():
            return current_output, ""
        
        # Verificar conexión
        if not device or not is_connected.is_set():
            new_output = f"{current_output}\n❌ ERROR: Dispositivo no conectado\n"
            return new_output, ""
        
        try:
            # Enviar comando al dispositivo
            response = device.send_command(command.strip())
            
            # Procesar respuesta como lista y limpiar códigos ANSI
            cleaned_lines = [clean_response_line(line) for line in response]
            response_text = '\n'.join(cleaned_lines)
            
            # Formatear output
            timestamp = datetime.now().strftime("%H:%M:%S")
            new_output = f"{current_output}\n[{timestamp}] ADMX2001> {command}\n{response_text}\n"
            
            # Limitar el tamaño del output (últimas 50 líneas)
            lines = new_output.split('\n')
            if len(lines) > 50:
                new_output = '\n'.join(lines[-50:])
            
            return new_output, ""
            
        except Exception as e:
            timestamp = datetime.now().strftime("%H:%M:%S")
            new_output = f"{current_output}\n[{timestamp}] ERROR: {str(e)}\n"
            return new_output, ""

    # Callback para inicializar el terminal al abrir el modal
    @app.callback(
        Output('command-output', 'children', allow_duplicate=True),
        Input('command-modal', 'style'),
        State('command-output', 'children'),
        prevent_initial_call=True
    )
    def initialize_terminal(modal_style, current_output):
        """Inicializa el terminal cuando se abre el modal"""
        if modal_style and modal_style.get('display') == 'block':
            # Si el modal se abre y no hay contenido, mostrar mensaje de bienvenida
            if not current_output or current_output.strip() == "":
                welcome_msg = "🖥️ Terminal ADMX2001 - Conectado y listo para comandos\n"
                welcome_msg += "💡 Comandos útiles: 'z' (medir), 'help' (ayuda), 'frequency 1000' (cambiar frecuencia)\n"
                welcome_msg += "💡 Use los botones rápidos o escriba comandos directamente\n\n"
                return welcome_msg
        return current_output or ""

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
            import os
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
                    return html.P("No se encontraron archivos CSV en el directorio 'data'", className="text-muted")
                
                # Crear lista de archivos
                file_list = []
                for filename in csv_files:
                    file_list.append(
                        html.Div([
                            html.I(className="fas fa-file-csv me-2 text-success"),
                            html.Span(filename, className="me-2"),
                            html.Small("(CSV)", className="text-muted")
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
            bode_fig = create_bode_plot(
                csv_data['param'], 
                csv_data['z_mag'], 
                csv_data['phase'],
                negative_phase,
                theme
            )
            nyquist_fig = create_nyquist_plot(
                csv_data['z_real'], 
                csv_data['z_imag'], 
                csv_data['param'],
                theme
            )
            
            # Cerrar modal
            return csv_data, bode_fig, nyquist_fig, {'display': 'none'}, 'modal fade'
            
        except Exception as e:
            print(f"Error cargando datos CSV: {e}")
            raise PreventUpdate

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
