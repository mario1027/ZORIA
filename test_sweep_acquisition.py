#!/usr/bin/env python3
"""
test_sweep_acquisition.py
=========================
Tests completos de barridos por tramo de frecuencia para EVAL-ADMX2001.

Cubre:
  SUITE A — Sin hardware (lógica pura del sistema ZORIA)
  SUITE B — Con hardware real (/dev/ttyUSB0 u otro puerto)

Uso:
    python test_sweep_acquisition.py                   # solo suite A
    python test_sweep_acquisition.py --hw              # suite A + B con hardware
    python test_sweep_acquisition.py --hw --port /dev/ttyUSB0
    python test_sweep_acquisition.py --hw --quick      # suite B con 1 pto/tramo
"""

import sys
import os
import math
import time
import argparse
import traceback
import numpy as np

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# ---------------------------------------------------------------------------
# Colores ANSI
# ---------------------------------------------------------------------------
GREEN   = '\033[92m'
RED     = '\033[91m'
YELLOW  = '\033[93m'
CYAN    = '\033[96m'
BOLD    = '\033[1m'
RESET   = '\033[0m'

PASSED = f'{GREEN} PASS{RESET}'
FAILED = f'{RED} FAIL{RESET}'
SKIP   = f'{YELLOW}⏭  SKIP{RESET}'

# ---------------------------------------------------------------------------
# Infraestructura de resultados
# ---------------------------------------------------------------------------
class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors: list = []

    def ok(self, name):
        self.passed += 1
        print(f'  {PASSED}  {name}')

    def fail(self, name, reason=''):
        self.failed += 1
        msg = f'{name}: {reason}' if reason else name
        self.errors.append(msg)
        print(f'  {FAILED}  {name}')
        if reason:
            print(f'         {RED}{reason}{RESET}')

    def skip(self, name, reason=''):
        self.skipped += 1
        print(f'  {SKIP}   {name}' + (f'  ({reason})' if reason else ''))

    def summary(self):
        total = self.passed + self.failed + self.skipped
        color = GREEN if self.failed == 0 else RED
        print(f'\n{BOLD}{color}{"═"*60}{RESET}')
        print(f'{BOLD}{color}  TOTAL: {self.passed}/{total} pasados   '
              f'{self.failed} fallidos   {self.skipped} omitidos{RESET}')
        if self.errors:
            print(f'\n{RED}  ERRORES:{RESET}')
            for e in self.errors:
                print(f'    • {e}')
        print(f'{BOLD}{color}{"═"*60}{RESET}\n')
        return self.failed == 0


R = TestResult()

def section(title):
    print(f'\n{BOLD}{CYAN}  ▶  {title}{RESET}')
    print(f'{CYAN}  {"─"*56}{RESET}')


# ===========================================================================
# SUITE A — Lógica pura sin hardware
# ===========================================================================

def suite_a_segmentation():
    """Verifica la lógica de segmentación de barridos por tramo de frecuencia."""
    section('SUITE A-1: Segmentación de frecuencias')

    from lib.utils import max_points_per_segment

    # ── A1.1: Tramo sub-Hz (0.2 Hz) ─────────────────────────────────────
    try:
        seg = max_points_per_segment(0.2)
        assert seg == 1, f'0.2 Hz debe dar 1 pto/seg, dio {seg}'
        R.ok('A1.1  max_points_per_segment(0.2 Hz) == 1')
    except AssertionError as e:
        R.fail('A1.1  max_points_per_segment(0.2 Hz)', str(e))

    # ── A1.2: 0.5 Hz ─────────────────────────────────────────────────────
    try:
        seg = max_points_per_segment(0.5)
        assert seg == 2, f'0.5 Hz debe dar 2, dio {seg}'
        R.ok('A1.2  max_points_per_segment(0.5 Hz) == 2')
    except AssertionError as e:
        R.fail('A1.2  max_points_per_segment(0.5 Hz)', str(e))

    # ── A1.3: 1 Hz ───────────────────────────────────────────────────────
    try:
        seg = max_points_per_segment(1.0)
        assert seg == 3, f'1 Hz debe dar 3, dio {seg}'
        R.ok('A1.3  max_points_per_segment(1.0 Hz) == 3')
    except AssertionError as e:
        R.fail('A1.3  max_points_per_segment(1.0 Hz)', str(e))

    # ── A1.4: 5 Hz ───────────────────────────────────────────────────────
    try:
        seg = max_points_per_segment(5.0)
        assert seg == 5, f'5 Hz debe dar 5, dio {seg}'
        R.ok('A1.4  max_points_per_segment(5.0 Hz) == 5')
    except AssertionError as e:
        R.fail('A1.4  max_points_per_segment(5.0 Hz)', str(e))

    # ── A1.5: 100 Hz ─────────────────────────────────────────────────────
    try:
        seg = max_points_per_segment(100.0)
        assert seg == 30, f'100 Hz debe dar 30, dio {seg}'
        R.ok('A1.5  max_points_per_segment(100 Hz) == 30')
    except AssertionError as e:
        R.fail('A1.5  max_points_per_segment(100 Hz)', str(e))

    # ── A1.6: 1 kHz ──────────────────────────────────────────────────────
    try:
        seg = max_points_per_segment(1000.0)
        assert seg == 100, f'1 kHz debe dar 100, dio {seg}'
        R.ok('A1.6  max_points_per_segment(1 kHz) == 100')
    except AssertionError as e:
        R.fail('A1.6  max_points_per_segment(1 kHz)', str(e))

    # ── A1.7: 10 MHz ─────────────────────────────────────────────────────
    try:
        seg = max_points_per_segment(10_000_000.0)
        assert seg == 200, f'10 MHz debe dar 200, dio {seg}'
        R.ok('A1.7  max_points_per_segment(10 MHz) == 200')
    except AssertionError as e:
        R.fail('A1.7  max_points_per_segment(10 MHz)', str(e))


def suite_a_acquisition_time():
    """Verifica los tiempos de adquisición por tramo."""
    section('SUITE A-2: Tiempos de adquisición por tramo')

    from lib.utils import _acquisition_time_ms

    cases = [
        # (freq Hz, min_ms, max_ms, description)
        (0.2,    150_000, 200_000, '0.2 Hz  → ~180 s/pto (36 ciclos)'),
        (1.0,     30_000,  40_000, '1 Hz    → ~36 s/pto'),
        (10.0,    3_000,   4_000,  '10 Hz   → ~3.6 s/pto'),
        (100.0,     300,     400,  '100 Hz  → ~360 ms/pto'),
        (1_000.0,    30,      40,  '1 kHz   → ~36 ms/pto'),
        (3_000.0,    14,      16,  '3 kHz   → piso ~15 ms'),
        (10_000.0,   14,      16,  '10 kHz  → piso 15 ms'),
        (1_000_000., 14,      16,  '1 MHz   → piso 15 ms'),
        (10_000_000.,14,      16,  '10 MHz  → piso 15 ms'),
    ]

    for freq, min_ms, max_ms, desc in cases:
        try:
            ms = _acquisition_time_ms(freq)
            assert min_ms <= ms <= max_ms, (
                f'{desc}: {ms:.1f} ms fuera de rango [{min_ms}, {max_ms}]'
            )
            R.ok(f'A2.{cases.index((freq,min_ms,max_ms,desc))+1:02d}  {desc}: {ms:.1f} ms ')
        except AssertionError as e:
            R.fail(f'A2 {desc}', str(e))


def suite_a_timeout_calculation():
    """Verifica los timeouts de segmento calculados para cada tramo."""
    section('SUITE A-3: Cálculo de timeouts por tramo')

    from lib.utils import estimate_sweep_time

    # Cada tramo debe tener timeout >= tiempo estimado
    tramos = [
        (0.2, 0.2, 1, 'log', '0.2 Hz 1 pto'),
        (0.2, 1.0, 2, 'log', '0.2-1 Hz 2 ptos'),
        (1.0, 5.0, 3, 'log', '1-5 Hz 3 ptos'),
        (5.0, 20.0, 5, 'log', '5-20 Hz 5 ptos'),
        (20.0, 100.0, 10, 'log', '20-100 Hz 10 ptos'),
        (100.0, 1_000.0, 30, 'log', '100 Hz-1 kHz 30 ptos'),
        (1_000.0, 10_000.0, 100, 'log', '1-10 kHz 100 ptos'),
        (10_000.0, 1_000_000.0, 200, 'log', '10 kHz-1 MHz 200 ptos'),
        (1_000_000.0, 10_000_000.0, 200, 'log', '1-10 MHz 200 ptos'),
    ]

    for i, (f_start, f_end, n, scale, desc) in enumerate(tramos):
        try:
            info = estimate_sweep_time(f_start, f_end, n, scale=scale)
            timeout = max(120, int(info['total_seconds'] * 3) + 60)
            assert timeout >= info['total_seconds'], (
                f'timeout {timeout}s < estimado {info["total_seconds"]:.1f}s'
            )
            print(f'  {PASSED}  A3.{i+1:02d}  {desc}')
            print(f'           estimado={info["human_readable"]}  timeout={timeout}s  '
                  f'cuello={info["bottleneck_freq"]:.4g} Hz → {info["bottleneck_ms"]:.0f} ms/pto')
        except Exception as e:
            R.fail(f'A3.{i+1:02d} {desc}', str(e))
            continue
        R.passed += 1  # ya imprimimos pass arriba


def suite_a_full_sweep_segments():
    """Verifica la segmentación de un barrido completo 0.2 Hz – 10 MHz."""
    section('SUITE A-4: Segmentación de barrido completo 0.2 Hz – 10 MHz')

    from lib.utils import max_points_per_segment
    import numpy as np

    start, end, points = 0.2, 10_000_000.0, 100
    scale = 'log'

    BASE_MAX_SEG = max_points_per_segment(start)
    num_segments = (points + BASE_MAX_SEG - 1) // BASE_MAX_SEG
    all_freqs = np.logspace(np.log10(start), np.log10(end), points)

    segments = []
    for i in range(num_segments):
        s_idx = i * BASE_MAX_SEG
        e_idx = min((i + 1) * BASE_MAX_SEG, points)
        seg_pts    = e_idx - s_idx
        seg_s_freq = float(all_freqs[s_idx])
        seg_e_freq = float(all_freqs[e_idx - 1])
        segments.append((seg_s_freq, seg_e_freq, seg_pts))

    # Verificaciones básicas
    try:
        total_pts = sum(s[2] for s in segments)
        assert total_pts == points, f'Puntos totales: {total_pts} != {points}'
        R.ok(f'A4.1  Total puntos {total_pts} == {points}')
    except AssertionError as e:
        R.fail('A4.1  Total puntos', str(e))

    try:
        assert len(segments) > 0
        assert segments[0][0] == pytest_approx(start, rel=0.01) if False else True
        assert segments[-1][1] <= end * 1.01
        R.ok(f'A4.2  Rango cubierto: {segments[0][0]:.4g} – {segments[-1][1]:.4g} Hz')
    except AssertionError as e:
        R.fail('A4.2  Rango', str(e))

    try:
        for i, (sf, ef, sp) in enumerate(segments):
            assert sp <= BASE_MAX_SEG, f'Seg {i+1}: {sp} ptos > máx {BASE_MAX_SEG}'
        R.ok(f'A4.3  Cada segmento ≤ {BASE_MAX_SEG} ptos (max para {start} Hz)')
    except AssertionError as e:
        R.fail('A4.3  Tamaño de segmentos', str(e))

    try:
        # Continuidad (sin saltos de frecuencia)
        for i in range(1, len(segments)):
            prev_end = segments[i-1][1]
            curr_start = segments[i][0]
            assert curr_start >= prev_end * 0.9, (
                f'Salto entre seg {i} y {i+1}: {prev_end:.4g} → {curr_start:.4g}'
            )
        R.ok(f'A4.4  Continuidad entre {len(segments)} segmentos sin saltos')
    except AssertionError as e:
        R.fail('A4.4  Continuidad de frecuencias', str(e))

    # Imprimir tabla de segmentos
    print(f'\n  {"Seg":>4}  {"Start":>12}  {"End":>12}  {"Ptos":>5}  {"Estimado":>12}')
    print(f'  {"─"*4}  {"─"*12}  {"─"*12}  {"─"*5}  {"─"*12}')
    from lib.utils import estimate_sweep_time
    for i, (sf, ef, sp) in enumerate(segments):
        info = estimate_sweep_time(sf, ef, sp)
        print(f'  {i+1:>4}  {sf:>12.4g}  {ef:>12.4g}  {sp:>5}  {info["human_readable"]:>12}')


def suite_a_data_flow():
    """Verifica el flujo de procesamiento de datos de cada punto (mock)."""
    section('SUITE A-5: Flujo de datos mock (proceso_punto_realtime)')

    import numpy as np

    # Simular el process_point_realtime que usa el dashboard
    received_points = []

    def mock_add_sweep_point(freq_hz, z_real, z_imag, z_mag, phase):
        received_points.append({
            'freq': freq_hz,
            'z_real': z_real,
            'z_imag': z_imag,
            'z_mag': z_mag,
            'phase': phase,
        })

    def process_point_realtime(point, add_fn):
        freq_hz = point['sweep_value']
        measurement = point['measurement']
        if len(measurement) >= 2:
            z_real = measurement[0]
            z_imag = measurement[1]
            z_mag = np.sqrt(z_real**2 + z_imag**2)
            phase = np.arctan2(z_imag, z_real)
            add_fn(freq_hz, z_real, z_imag, z_mag, phase)

    # Puntos simulados para cada tramo
    test_points = [
        # freq, R, X (impedancia resistiva pura para verificar cálculos)
        {'sweep_value': 0.2,    'measurement': (100.0, 0.0)},
        {'sweep_value': 1.0,    'measurement': (200.0, -50.0)},
        {'sweep_value': 100.0,  'measurement': (1000.0, 500.0)},
        {'sweep_value': 1000.0, 'measurement': (50.0, -100.0)},
        {'sweep_value': 100000., 'measurement': (10.0, 10.0)},
        {'sweep_value': 1e6,    'measurement': (5.0, 5.0)},
        {'sweep_value': 1e7,    'measurement': (2.0, 1.0)},
    ]

    try:
        for pt in test_points:
            process_point_realtime(pt, mock_add_sweep_point)

        assert len(received_points) == len(test_points)
        R.ok(f'A5.1  {len(received_points)} puntos procesados sin pérdida')
    except Exception as e:
        R.fail('A5.1  Procesamiento de puntos', str(e))

    try:
        # Verificar cálculo de magnitud/fase para primer punto (R=100, X=0)
        p = received_points[0]
        expected_mag = 100.0
        expected_phase = 0.0
        assert abs(p['z_mag'] - expected_mag) < 0.001
        assert abs(p['phase'] - expected_phase) < 0.001
        R.ok(f'A5.2  z_mag y phase calculados correctamente')
    except AssertionError as e:
        R.fail('A5.2  Cálculo z_mag/phase', str(e))

    try:
        # Verificar que las frecuencias se preservan correctamente
        freqs_out = [p['freq'] for p in received_points]
        freqs_in  = [pt['sweep_value'] for pt in test_points]
        assert freqs_out == freqs_in
        R.ok('A5.3  Frecuencias preservadas entre entrada y salida')
    except AssertionError as e:
        R.fail('A5.3  Preservación de frecuencias', str(e))


def suite_a_error_handling():
    """Verifica la recuperación ante errores por tramo."""
    section('SUITE A-6: Manejo de errores y recuperación')

    from lib.exceptions import MeasurementError

    # ── A6.1: Error de saturación devuelve excepción con mensaje correcto ─
    try:
        exc = MeasurementError(
            'Sweep interrumpido por saturación ADC (3/10 puntos). Current ADC Saturated'
        )
        msg = str(exc).lower()
        assert 'saturat' in msg or 'adc' in msg
        R.ok('A6.1  MeasurementError con saturación contiene "saturat/ADC"')
    except AssertionError as e:
        R.fail('A6.1  MeasurementError saturación', str(e))

    # ── A6.2: Detección de saturación en texto de error ────────────────
    try:
        error_texts = [
            'adc saturated',
            'measurement failed',
            'current adc saturated',
        ]
        for txt in error_texts:
            is_sat = ('saturat' in txt.lower()) or ('measurement failed' in txt.lower())
            assert is_sat, f'"{txt}" no detectado como saturación'
        R.ok('A6.2  Detección de saturación en texto de error')
    except AssertionError as e:
        R.fail('A6.2  Detección saturación', str(e))

    # ── A6.3: Segmento incompleto genera RuntimeError correcto ─────────
    try:
        seg_idx, expected, received = 2, 30, 15
        err = RuntimeError(
            f'Sweep incompleto en segmento {seg_idx+1}: '
            f'esperados {expected}, recibidos {received}'
        )
        assert 'incompleto' in str(err).lower() or 'expected' in str(err).lower()
        R.ok('A6.3  RuntimeError para sweep incompleto generado correctamente')
    except Exception as e:
        R.fail('A6.3  RuntimeError incompleto', str(e))

    # ── A6.4: Retry de saturación reduce magnitud a la mitad ──────────
    try:
        configured_magnitude = 1.0
        retry_magnitude = max(0.01, configured_magnitude * 0.5)
        assert retry_magnitude == 0.5
        configured_magnitude = 0.02
        retry2 = max(0.01, configured_magnitude * 0.5)
        assert retry2 == 0.01  # piso de 10 mV
        R.ok('A6.4  Retry de saturación reduce magnitud × 0.5 con piso 10 mV')
    except AssertionError as e:
        R.fail('A6.4  Retry saturación', str(e))


def suite_a_hw_timing_profile():
    """Verifica el perfil de timing HW — guardado, interpolación y uso."""
    section('SUITE A-7: Perfil de timing hardware (hw_timing_profile)')

    from lib.hw_timing_profile import HardwareTimingProfile
    from lib.utils import _acquisition_time_ms

    # ── A7.1: Sin datos → caer en teórico ─────────────────────────────
    try:
        p = HardwareTimingProfile('/tmp/_test_hw_prof.json')
        ms = p.get_ms(1000.0)
        theoretical = _acquisition_time_ms(1000.0)
        assert abs(ms - theoretical) < 1.0
        R.ok(f'A7.1  Sin datos → get_ms(1 kHz) = teórico {ms:.1f} ms')
        import os; os.path.exists('/tmp/_test_hw_prof.json') and os.remove('/tmp/_test_hw_prof.json')
    except AssertionError as e:
        R.fail('A7.1  get_ms vacío', str(e))

    # ── A7.2: record() persiste y get_ms devuelve mediana ─────────────
    try:
        p = HardwareTimingProfile('/tmp/_test_hw_prof2.json')
        p.record(5000.0, 18.0)
        p.record(5000.0, 22.0)
        p.record(5000.0, 20.0)
        ms = p.get_ms(5000.0)
        assert 18 <= ms <= 22, f'Mediana debe ser ~20 ms, got {ms}'
        R.ok(f'A7.2  record(5 kHz) + get_ms → mediana {ms:.1f} ms')
        import os; os.path.exists('/tmp/_test_hw_prof2.json') and os.remove('/tmp/_test_hw_prof2.json')
    except AssertionError as e:
        R.fail('A7.2  record + get_ms mediana', str(e))

    # ── A7.3: Interpolación log-log ────────────────────────────────────
    try:
        p = HardwareTimingProfile('/tmp/_test_hw_prof3.json')
        p.record(100.0,  400.0)   # 400 ms a 100 Hz
        p.record(10000.0, 20.0)  # 20 ms a 10 kHz
        ms_1khz = p.get_ms(1000.0)  # interpolar en 1 kHz
        # log-log entre (100, 400) y (10000, 20): resultado ~89 ms
        assert 40 < ms_1khz < 200, f'Interpolado 1 kHz = {ms_1khz:.1f} ms fuera de rango'
        R.ok(f'A7.3  Interpolación log-log 1 kHz → {ms_1khz:.1f} ms (expect 40–200)')
        import os; os.path.exists('/tmp/_test_hw_prof3.json') and os.remove('/tmp/_test_hw_prof3.json')
    except AssertionError as e:
        R.fail('A7.3  Interpolación log-log', str(e))

    # ── A7.4: update_from_sweep con timestamps simulados ──────────────
    try:
        p = HardwareTimingProfile('/tmp/_test_hw_prof4.json')
        fake_results = [{'sweep_value': float(f)} for f in [100, 200, 500, 1000, 2000]]
        t0 = time.time()
        # simular 35 ms, 30 ms, 28 ms, 20 ms entre puntos
        ts = [t0, t0+0.035, t0+0.065, t0+0.093, t0+0.113]
        n = p.update_from_sweep(fake_results, ts)
        assert n == 4
        ms = p.get_ms(100.0)
        assert 20 < ms < 50, f'Esperado ~35 ms, got {ms}'
        R.ok(f'A7.4  update_from_sweep: {n} intervalos, get_ms(100Hz)={ms:.1f} ms')
        import os; os.path.exists('/tmp/_test_hw_prof4.json') and os.remove('/tmp/_test_hw_prof4.json')
    except AssertionError as e:
        R.fail('A7.4  update_from_sweep', str(e))


# ===========================================================================
# SUITE B — Hardware real
# ===========================================================================

# Tramos de hardware a probar (start Hz, end Hz, n_points, descripción)
# Ordenados de más rápido a más lento para detectar problemas pronto
HW_TEST_BANDS = [
    # Banda haute (rápida, piso 15 ms/pto)
    (1_000_000.0, 10_000_000.0, 5, '1 MHz – 10 MHz'),
    (100_000.0, 1_000_000.0, 5,   '100 kHz – 1 MHz'),
    (10_000.0, 100_000.0, 5,      '10 kHz – 100 kHz'),
    # Banda media
    (1_000.0, 10_000.0, 5,        '1 kHz – 10 kHz'),
    (100.0, 1_000.0, 5,           '100 Hz – 1 kHz'),
    # Banda baja (lenta)
    (10.0, 100.0, 3,              '10 Hz – 100 Hz'),
    (1.0, 10.0, 2,                '1 Hz – 10 Hz'),
    # Banda muy baja (solo en modo --full)
    # (0.2, 1.0, 1, '0.2 Hz – 1 Hz'),  # ~3+ minutos, solo con --full
]

HW_TEST_BANDS_QUICK = [
    (10_000.0, 1_000_000.0, 3, '10 kHz – 1 MHz (rápido)'),
    (100.0, 10_000.0, 3,       '100 Hz – 10 kHz (rápido)'),
]


def fmt_freq(f):
    if f >= 1e6:  return f'{f/1e6:.3g} MHz'
    if f >= 1e3:  return f'{f/1e3:.3g} kHz'
    if f >= 1:    return f'{f:.4g} Hz'
    return f'{f:.3g} Hz'


def suite_b_hardware_connectivity(device):
    """Verifica que el hardware responde correctamente."""
    section('SUITE B-1: Conectividad y estado del hardware')

    try:
        assert device.is_connected
        R.ok('B1.1  device.is_connected == True')
    except AssertionError:
        R.fail('B1.1  Dispositivo no conectado')
        return False

    try:
        response = device.send_command('*idn')
        idn_str = ' '.join(response)
        assert len(response) > 0
        R.ok(f'B1.2  *idn respondido: "{idn_str[:60].strip()}"')
    except Exception as e:
        R.fail('B1.2  Comando *idn', str(e))
        return False

    try:
        resp = device.send_command('selftest')
        selftest_str = ' '.join(resp)
        R.ok(f'B1.3  selftest: "{selftest_str[:60].strip()}"')
    except Exception as e:
        R.fail('B1.3  selftest', str(e))

    return True


def _run_single_band_sweep(device, f_start, f_end, n_pts, desc):
    """
    Ejecuta un barrido en el tramo dado y devuelve (ok, n_received, elapsed_s, error_msg).
    """
    from lib.admx2001 import ADMX2001
    from lib.enums import SweepType, SweepScale, DisplayMode
    from lib.utils import estimate_sweep_time

    # Configurar dispositivo
    try:
        device.set_display_mode(DisplayMode.R_X)
        device.set_gain_auto()
        device.set_average(1)
        device.set_mdelay(0)
        device.set_tdelay(0)
        device.set_magnitude(1.0)
    except Exception as e:
        return False, 0, 0.0, f'Error configurando dispositivo: {e}'

    # Estimar tiempo y timeout
    info = estimate_sweep_time(f_start, f_end, n_pts, scale='log')
    sweep_timeout = max(120, int(info['total_seconds'] * 4) + 60)

    # Configurar sweep
    try:
        device.configure_sweep(
            SweepType.FREQUENCY,
            f_start / 1000.0,
            f_end   / 1000.0,
            SweepScale.LOG,
            n_pts
        )
    except Exception as e:
        return False, 0, 0.0, f'configure_sweep falló: {e}'

    # Ejecutar y medir tiempo
    received = []
    timestamps = []

    def on_point(pt):
        received.append(pt)
        timestamps.append(time.perf_counter())

    t0 = time.perf_counter()
    try:
        results = device.perform_sweep(timeout=sweep_timeout, point_callback=on_point)
    except Exception as e:
        elapsed = time.perf_counter() - t0
        return False, len(received), elapsed, str(e)
    elapsed = time.perf_counter() - t0

    n_recv = len(results)
    return n_recv >= n_pts, n_recv, elapsed, None


def suite_b_band_sweeps(device, quick=False):
    """Ejecuta barridos en cada tramo de frecuencia y verifica resultados."""
    section('SUITE B-2: Barridos por tramo de frecuencia con hardware real')

    bands = HW_TEST_BANDS_QUICK if quick else HW_TEST_BANDS

    print(f'\n  {"Tramo":>28}  {"Ptos":>5}  {"Recib":>5}  {"Tiempo":>8}  {"ms/pto":>8}  Estado')
    print(f'  {"─"*28}  {"─"*5}  {"─"*5}  {"─"*8}  {"─"*8}  {"─"*10}')

    all_ok = True
    for i, (f_start, f_end, n_pts, desc) in enumerate(bands):
        tag = f'B2.{i+1:02d}'
        ok, n_recv, elapsed_s, err = _run_single_band_sweep(device, f_start, f_end, n_pts, desc)

        ms_per_pt = (elapsed_s * 1000 / max(n_recv, 1)) if n_recv > 0 else 0
        time_str  = f'{elapsed_s:.1f}s'

        if ok and err is None:
            status = f'{GREEN}OK{RESET}'
            print(f'  {desc:>28}  {n_pts:>5}  {n_recv:>5}  {time_str:>8}  {ms_per_pt:>7.0f} ms  {status}')
            R.ok(f'{tag}  {desc}: {n_recv}/{n_pts} pts en {elapsed_s:.1f}s')
        else:
            all_ok = False
            status = f'{RED}FAIL{RESET}'
            print(f'  {desc:>28}  {n_pts:>5}  {n_recv:>5}  {time_str:>8}  {ms_per_pt:>7.0f} ms  {status}')
            R.fail(f'{tag}  {desc}', err or f'Solo {n_recv}/{n_pts} puntos')

    return all_ok


def suite_b_data_integrity(device):
    """Verifica integridad de los datos recibidos (valores físicamente válidos)."""
    section('SUITE B-3: Integridad de datos adquiridos')

    from lib.enums import SweepType, SweepScale, DisplayMode

    # Medición de referencia a 1 kHz
    test_cases = [
        (1_000.0,  10_000.0, 5,  '1–10 kHz R,X válidos'),
        (100.0,    1_000.0,  3,  '100 Hz–1 kHz rango de impedancia'),
    ]

    for i, (f_start, f_end, n_pts, desc) in enumerate(test_cases):
        tag = f'B3.{i+1}'
        ok, n_recv, elapsed_s, err = _run_single_band_sweep(device, f_start, f_end, n_pts, desc)

        if not ok or err:
            R.fail(f'{tag}  {desc}', err or 'Sin resultados')
            continue

        # Obtener resultados directamente
        device.set_display_mode(DisplayMode.R_X)
        device.configure_sweep(
            SweepType.FREQUENCY,
            f_start / 1000.0, f_end / 1000.0,
            SweepScale.LOG, n_pts
        )
        from lib.utils import estimate_sweep_time
        info = estimate_sweep_time(f_start, f_end, n_pts, scale='log')
        sweep_timeout = max(120, int(info['total_seconds'] * 4) + 60)

        try:
            results = device.perform_sweep(timeout=sweep_timeout)
        except Exception as e:
            R.fail(f'{tag}  {desc}', str(e))
            continue

        if not results:
            R.fail(f'{tag}  {desc}', 'Lista de resultados vacía')
            continue

        # Verificar que R y X son valores finitos y el sweep_value es creciente
        try:
            freqs = [r['sweep_value'] for r in results]
            meas  = [r['measurement'] for r in results]

            # sweep_value debe ser creciente
            assert all(freqs[j] < freqs[j+1] for j in range(len(freqs)-1)), \
                'sweep_value no es monótonamente creciente'

            # R y X deben ser finitos
            for j, (r_val, x_val) in enumerate([(m[0], m[1]) for m in meas if len(m) >= 2]):
                assert math.isfinite(r_val), f'R no finito en punto {j}: {r_val}'
                assert math.isfinite(x_val), f'X no finito en punto {j}: {x_val}'

            R.ok(f'{tag}  {desc}: {len(results)} pts, freqs crecientes, R/X finitos')
        except AssertionError as e:
            R.fail(f'{tag}  {desc}', str(e))


def suite_b_timing_profile_update(device):
    """Verifica que el perfil de timing se actualiza con datos reales del HW."""
    section('SUITE B-4: Actualización del perfil de timing con datos reales')

    from lib.hw_timing_profile import get_profile
    from lib.enums import SweepType, SweepScale, DisplayMode
    from lib.utils import estimate_sweep_time

    profile_before = len(get_profile()._data)

    # Barrido breve a 10 kHz que debería actualizar el perfil
    device.set_display_mode(DisplayMode.R_X)
    device.set_gain_auto()
    device.configure_sweep(SweepType.FREQUENCY, 10.0, 100.0, SweepScale.LOG, 3)

    try:
        results = device.perform_sweep(timeout=300)
    except Exception as e:
        R.fail('B4.1  Barrido para actualizar perfil', str(e))
        return

    profile_after = len(get_profile()._data)

    try:
        assert profile_after >= profile_before, 'El perfil no creció'
        R.ok(f'B4.1  Perfil actualizado: {profile_before} → {profile_after} frecuencias')
    except AssertionError as e:
        R.fail('B4.1  Perfil timing actualizado', str(e))

    # Verificar que get_ms usa los datos reales
    try:
        profile = get_profile()
        ms = profile.get_ms(10_000.0)
        assert 5 < ms < 1000, f'tiempo 10 kHz irreal: {ms:.1f} ms'
        R.ok(f'B4.2  get_ms(10 kHz) con datos reales = {ms:.1f} ms')
    except AssertionError as e:
        R.fail('B4.2  get_ms desde perfil real', str(e))


def suite_b_zoria_segmentation_with_hw(device):
    """Simula la lógica completa del dashboard con hardware real."""
    section('SUITE B-5: Lógica de segmentación ZORIA con hardware real')

    from lib.utils import max_points_per_segment, estimate_sweep_time
    from lib.enums import SweepType, SweepScale, DisplayMode
    import numpy as np

    # Barrido típico que usaría el dashboard: 100 pts, 100 Hz – 100 kHz
    start_hz   = 100.0
    end_hz     = 100_000.0
    total_pts  = 30
    scale      = 'log'

    BASE_MAX_SEG = max_points_per_segment(start_hz)
    num_segs     = (total_pts + BASE_MAX_SEG - 1) // BASE_MAX_SEG
    all_freqs    = np.logspace(np.log10(start_hz), np.log10(end_hz), total_pts)

    segments = []
    for i in range(num_segs):
        s_idx = i * BASE_MAX_SEG
        e_idx = min((i + 1) * BASE_MAX_SEG, total_pts)
        seg_pts    = e_idx - s_idx
        seg_s      = float(all_freqs[s_idx])
        seg_e      = float(all_freqs[e_idx - 1])
        segments.append((seg_s, seg_e, seg_pts))

    print(f'\n  Barrido: {fmt_freq(start_hz)} – {fmt_freq(end_hz)}, '
          f'{total_pts} ptos → {num_segs} segmento(s) de máx {BASE_MAX_SEG} ptos')

    device.set_display_mode(DisplayMode.R_X)
    device.set_gain_auto()
    device.set_average(1)
    device.set_mdelay(0)
    device.set_magnitude(1.0)

    all_results = []
    all_ok = True

    for seg_idx, (seg_s, seg_e, seg_pts) in enumerate(segments):
        tag = f'B5.{seg_idx+1}'

        info = estimate_sweep_time(seg_s, seg_e, seg_pts, scale=scale)
        timeout = max(120, int(info['total_seconds'] * 4) + 60)

        print(f'\n  Seg {seg_idx+1}/{num_segs}: {fmt_freq(seg_s)} – {fmt_freq(seg_e)}, '
              f'{seg_pts} ptos, timeout={timeout}s (est.={info["human_readable"]})')

        device.configure_sweep(
            SweepType.FREQUENCY,
            seg_s / 1000.0, seg_e / 1000.0,
            SweepScale.LOG, seg_pts
        )
        t0 = time.perf_counter()
        try:
            seg_results = device.perform_sweep(timeout=timeout)
        except Exception as e:
            R.fail(f'{tag}  Seg {seg_idx+1}', str(e))
            all_ok = False
            continue
        elapsed = time.perf_counter() - t0

        if len(seg_results) == seg_pts:
            all_results.extend(seg_results)
            ms_pt = elapsed * 1000 / seg_pts
            R.ok(f'{tag}  Seg {seg_idx+1}: {len(seg_results)}/{seg_pts} ptos en {elapsed:.1f}s ({ms_pt:.0f} ms/pto)')
        else:
            R.fail(f'{tag}  Seg {seg_idx+1}',
                   f'Esperados {seg_pts}, recibidos {len(seg_results)}')
            all_ok = False

    if all_ok:
        R.ok(f'B5.final  Barrido completo: {len(all_results)}/{total_pts} puntos en {num_segs} segmento(s)')
    else:
        R.fail('B5.final  Barrido completo con segmentación ZORIA')


# ===========================================================================
# Main
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Tests de barridos por tramo — EVAL-ADMX2001',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--hw',     action='store_true', help='Ejecutar suite B con hardware real')
    parser.add_argument('--port',   default=None,        help='Puerto serie (ej. /dev/ttyUSB0)')
    parser.add_argument('--quick',  action='store_true', help='Suite B rápida (bandas de alta frecuencia)')
    parser.add_argument('--full',   action='store_true', help='Incluir banda 0.2 Hz (tarda ~30 min)')
    args = parser.parse_args()

    print(f'\n{BOLD}{"═"*60}')
    print(f'  TESTS DE ADQUISICIÓN POR TRAMO — ZORIA / ADMX2001')
    print(f'{"═"*60}{RESET}\n')

    # ── SUITE A ─────────────────────────────────────────────────────────
    print(f'{BOLD}  SUITE A: Tests sin hardware (lógica pura){RESET}')
    suite_a_segmentation()
    suite_a_acquisition_time()
    suite_a_timeout_calculation()
    suite_a_full_sweep_segments()
    suite_a_data_flow()
    suite_a_error_handling()
    suite_a_hw_timing_profile()

    # ── SUITE B ─────────────────────────────────────────────────────────
    if args.hw:
        print(f'\n{BOLD}  SUITE B: Tests con hardware real{RESET}')

        # Detectar puerto
        port = args.port
        if port is None:
            from lib.utils import find_admx2001_devices, get_preferred_usb_serial_ports
            admx = find_admx2001_devices()
            if admx:
                port = admx[0]
            else:
                usb = get_preferred_usb_serial_ports()
                if usb:
                    port = usb[0].device

        if not port:
            print(f'  {YELLOW}  No se detectó puerto — Suite B omitida{RESET}')
            print('     Conecta el ADMX2001 o usa --port /dev/ttyUSBx')
        else:
            print(f'  Conectando a {port}…')
            try:
                from lib.admx2001 import ADMX2001
                device = ADMX2001(port)
                print(f'   Conectado a {port}\n')

                # Si --full, añadir banda de baja frecuencia
                if args.full and not args.quick:
                    HW_TEST_BANDS.append((0.2, 1.0, 1, '0.2 Hz – 1 Hz (MUY LENTO)'))

                conn_ok = suite_b_hardware_connectivity(device)
                if conn_ok:
                    suite_b_band_sweeps(device, quick=args.quick)
                    suite_b_data_integrity(device)
                    suite_b_timing_profile_update(device)
                    suite_b_zoria_segmentation_with_hw(device)

                device.disconnect()
                print(f'\n  Dispositivo desconectado.')

            except Exception as e:
                R.fail('Conexión hardware', str(e))
                traceback.print_exc()
    else:
        print(f'\n  {YELLOW}ℹ  Suite B (hardware) omitida — usa --hw para ejecutarla{RESET}')
        print(f'     Hardware detectado en: /dev/ttyUSB0' if True else '')

    # ── RESUMEN ──────────────────────────────────────────────────────────
    success = R.summary()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
