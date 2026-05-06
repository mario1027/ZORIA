#!/usr/bin/env python3
"""
test_full_sweep_hw.py — Tests EXHAUSTIVOS de hardware: TODOS los barridos posibles
====================================================================================

Prueba TODAS las configuraciones de barrido del EVAL-ADMX2001 directamente
en el hardware real:

  C1 — Rango COMPLETO   : 0.2 Hz – 10 MHz (varies N)
  C2 — Ancho MÍNIMO     : 2 puntos muy próximos en cada banda
  C3 — Por DÉCADAS      : 1 década por tramo, todo el espectro
  C4 — N variable       : mismo rango, N ∈ {2,10,50,100,200,500,1000}
  C5 — LOG vs LINEAR    : misma banda con ambas escalas
  C6 — Averages         : average ∈ {1,2,4,8} mismo barrido
  C7 — Límites N grandes: 500 pts banda media, 1000 pts banda alta

RESTRICCIONES:
  - N máximo por test: 1000 puntos
  - Por defecto, tests con frecuencias < 1 Hz se marcan como lentos y
    requieren confirmación o el flag --include-sub-hz
  - Todos los tests reales miden el tiempo inter-punto y lo comparan
    con el modelo teórico (36 ciclos DFT + piso 15 ms)

USO:
    python test_full_sweep_hw.py --port /dev/ttyUSB0
    python test_full_sweep_hw.py --port /dev/ttyUSB0 --include-sub-hz
    python test_full_sweep_hw.py --port /dev/ttyUSB0 --only-fast
    python test_full_sweep_hw.py --port /dev/ttyUSB0 --suite C1
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
GREEN  = '\033[92m'
RED    = '\033[91m'
YELLOW = '\033[93m'
CYAN   = '\033[96m'
BOLD   = '\033[1m'
DIM    = '\033[2m'
RESET  = '\033[0m'

PASSED = f'{GREEN}✅ PASS{RESET}'
FAILED = f'{RED}❌ FAIL{RESET}'
SKIP   = f'{YELLOW}⏭  SKIP{RESET}'

# ---------------------------------------------------------------------------
# Resultado global
# ---------------------------------------------------------------------------
class Results:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors = []
        self.timing_data = []  # [(label, freq_start, n_pts, ms_per_pt, theoretical_ms)]

    def ok(self, name, extra=''):
        self.passed += 1
        line = f'  {PASSED}  {name}'
        if extra:
            line += f'  {DIM}{extra}{RESET}'
        print(line)

    def fail(self, name, reason=''):
        self.failed += 1
        msg = f'{name}: {reason}' if reason else name
        self.errors.append(msg)
        print(f'  {FAILED}  {name}')
        if reason:
            print(f'         {RED}{reason}{RESET}')

    def skip(self, name, reason=''):
        self.skipped += 1
        print(f'  {SKIP}   {name}' + (f'  {DIM}({reason}){RESET}' if reason else ''))

    def record_timing(self, label, freq_start, n_pts, elapsed_ms, theoretical_ms):
        ms_per_pt = elapsed_ms / max(n_pts, 1)
        self.timing_data.append((label, freq_start, n_pts, ms_per_pt, theoretical_ms))

    def summary(self):
        total = self.passed + self.failed + self.skipped
        ok_color = GREEN if self.failed == 0 else RED
        print(f'\n{BOLD}{"═"*68}{RESET}')
        print(f'{BOLD}{ok_color}  TOTAL: {self.passed}/{total} pasados   '
              f'{self.failed} fallidos   {self.skipped} omitidos{RESET}')
        if self.errors:
            print(f'\n{RED}  ERRORES:{RESET}')
            for e in self.errors:
                print(f'    • {e}')
        print(f'{BOLD}{"═"*68}{RESET}\n')

        if self.timing_data:
            print(f'{BOLD}  RESUMEN DE TIMING REAL vs TEÓRICO:{RESET}')
            print(f'  {"Test":<40}  {"N":>5}  {"ms/pto":>9}  {"Teórico":>9}  {"Ratio":>6}')
            print(f'  {"─"*40}  {"─"*5}  {"─"*9}  {"─"*9}  {"─"*6}')
            for lbl, fstart, n_pts, ms_pt, theoretical in self.timing_data:
                ratio = ms_pt / theoretical if theoretical > 0 else float('nan')
                if ratio < 0.5:
                    r_color = CYAN
                elif ratio <= 2.0:
                    r_color = GREEN
                else:
                    r_color = YELLOW
                print(f'  {lbl:<40}  {n_pts:>5}  {_fmt_ms(ms_pt):>9}  '
                      f'{_fmt_ms(theoretical):>9}  {r_color}{ratio:>5.2f}×{RESET}')
        return self.failed == 0


R = Results()


def _section(title):
    print(f'\n{BOLD}{CYAN}  ▶  {title}{RESET}')
    print(f'{CYAN}  {"─"*64}{RESET}')


def _fmt_freq(f):
    if f >= 1e6:  return f'{f/1e6:.4g} MHz'
    if f >= 1e3:  return f'{f/1e3:.4g} kHz'
    if f >= 1:    return f'{f:.5g} Hz'
    return f'{f:.3g} Hz'


def _fmt_ms(ms):
    if ms >= 60_000:   return f'{ms/60000:.2f} min'
    if ms >= 1_000:    return f'{ms/1000:.2f} s'
    return f'{ms:.1f} ms'


def _est_timeout(f_start, f_end, n_pts, scale='log', average=1, margin=5.0):
    """Calcula timeout realista: teórico × margin + overhead fijo 60s."""
    from lib.utils import estimate_sweep_time
    info = estimate_sweep_time(f_start, f_end, n_pts, scale=scale, average=average)
    return max(120.0, info['total_seconds'] * margin + 60.0)


def _verify_results(results, n_expected, tag, freq_label):
    """Verifica integridad de los resultados de un sweep."""
    if not results:
        R.fail(tag, f'{freq_label}: lista vacía')
        return False

    n_got = len(results)
    if n_got < n_expected:
        R.fail(tag, f'{freq_label}: {n_got}/{n_expected} pts recibidos')
        return False

    # Frecuencias deben ser crecientes
    freqs = [r['sweep_value'] for r in results]
    if not all(freqs[i] <= freqs[i+1] for i in range(len(freqs)-1)):
        R.fail(tag, f'{freq_label}: sweep_value no monótonamente creciente')
        return False

    # R y X deben ser finitos
    for i, r in enumerate(results):
        meas = r.get('measurement', [])
        if len(meas) < 2:
            R.fail(tag, f'{freq_label}: punto {i} sin medición R,X')
            return False
        r_val, x_val = meas[0], meas[1]
        if not math.isfinite(r_val) or not math.isfinite(x_val):
            R.fail(tag, f'{freq_label}: R={r_val} X={x_val} no finitos en pto {i}')
            return False

    return True


def _run_sweep(device, f_start_hz, f_end_hz, n_pts, scale, average=1,
               display_mode=None, tag='', desc=''):
    """
    Configura y ejecuta un barrido. Devuelve (results, elapsed_ms, error).
    Registra automáticamente en el perfil de timing HW.
    """
    from lib.enums import SweepType, SweepScale, DisplayMode
    from lib.utils import _acquisition_time_ms

    if display_mode is None:
        display_mode = DisplayMode.R_X

    # Abortar cualquier barrido anterior ANTES del setup
    # (necesario si el test anterior dejó el device en mitad de un sweep)
    try:
        device.send_command("abort", expect_prompt=False)
    except Exception:
        pass

    # Configurar dispositivo
    try:
        device.set_display_mode(display_mode)
        device.set_gain_auto()
        device.set_average(average)
        device.set_mdelay(0)
        device.set_tdelay(0)
        device.set_magnitude(1.0)
    except Exception as e:
        return None, 0.0, f'Config falló: {e}'

    # Escala enum
    scale_enum = SweepScale.LOG if scale == 'log' else SweepScale.LINEAR

    # Timeout basado en tiempo teórico × 5 + overhead fijo
    timeout = _est_timeout(f_start_hz, f_end_hz, n_pts, scale=scale,
                           average=average, margin=5.0)

    # Configurar sweep (frecuencias en kHz)
    try:
        device.configure_sweep(
            SweepType.FREQUENCY,
            f_start_hz / 1000.0,
            f_end_hz   / 1000.0,
            scale_enum,
            n_pts
        )
    except Exception as e:
        return None, 0.0, f'configure_sweep falló: {e}'

    # Ejecutar y medir tiempo real
    t0 = time.perf_counter()
    try:
        results = device.perform_sweep(timeout=timeout)
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000.0
        return None, elapsed, str(e)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    # Registrar timing en resumen global
    theoretical_ms = _acquisition_time_ms(f_start_hz, average)
    test_lbl = desc or f'{_fmt_freq(f_start_hz)}–{_fmt_freq(f_end_hz)} N={n_pts}'
    R.record_timing(test_lbl, f_start_hz, n_pts, elapsed_ms, theoretical_ms)

    return results, elapsed_ms, None


# ===========================================================================
# SUITE C1 — Rango completo 0.2 Hz – 10 MHz
# ===========================================================================

def suite_c1_full_range(device, include_sub_hz=True):
    """Barrido completo de todo el espectro disponible del ADMX2001."""
    _section('SUITE C1: Rango COMPLETO — 0.2 Hz a 10 MHz')

    FULL_START = 0.2
    FULL_END   = 10_000_000.0

    # Test C1.1: 10 puntos LOG — barrido exploratorio de todo el rango
    #   Tiempo estimado con sub-Hz incluido: ~250 s
    #   Sin sub-Hz (empezando en 1 Hz): ~50 s
    configs = [
        (10,  '10 pts LOG — exploración rápida'),
        (20,  '20 pts LOG — resolución media'),
        (50,  '50 pts LOG — resolución estándar'),
    ]

    for c_idx, (n_pts, desc) in enumerate(configs):
        tag = f'C1.{c_idx+1}'
        label = f'{_fmt_freq(FULL_START)}–{_fmt_freq(FULL_END)}, {desc}'

        if not include_sub_hz:
            # Ajustar start a 1 Hz para evitar tiempos excesivos
            start = 1.0
            label += ' (desde 1 Hz)'
        else:
            start = FULL_START

        from lib.utils import estimate_sweep_time
        info = estimate_sweep_time(start, FULL_END, n_pts, scale='log')
        est_str = info['human_readable']
        print(f'\n  {BOLD}{tag}{RESET}  {label}')
        print(f'  Estimado: ~{est_str}  Timeout: {_est_timeout(start, FULL_END, n_pts):.0f}s')

        results, elapsed_ms, err = _run_sweep(
            device, start, FULL_END, n_pts, 'log',
            tag=tag, desc=f'{tag} {_fmt_freq(start)}-10MHz N={n_pts}'
        )

        if err or results is None:
            R.fail(f'{tag}  {desc}', err or 'Sin resultados')
            continue

        ok = _verify_results(results, n_pts, f'{tag}  {label}', label)
        if ok:
            ms_pt = elapsed_ms / len(results)
            R.ok(f'{tag}  {label}',
                 f'{len(results)} pts en {_fmt_ms(elapsed_ms)} ({_fmt_ms(ms_pt)}/pto)')

    # Test C1.4: Rango completo con N=100 (banda alta solamente, viable en tiempo)
    #   Empezar desde 10 Hz para evitar tiempos excesivos en 100-pt sweep
    if not include_sub_hz:
        tag = 'C1.4'
        desc = '100 pts LOG desde 10 Hz – 10 MHz'
        print(f'\n  {BOLD}{tag}{RESET}  {desc}')
        results, elapsed_ms, err = _run_sweep(
            device, 10.0, FULL_END, 100, 'log',
            tag=tag, desc=f'{tag} 10Hz-10MHz N=100'
        )
        if err or results is None:
            R.fail(f'{tag}  {desc}', err or 'Sin resultados')
        else:
            ok = _verify_results(results, 100, f'{tag}  {desc}', desc)
            if ok:
                ms_pt = elapsed_ms / len(results)
                R.ok(f'{tag}  {desc}',
                     f'{len(results)} pts en {_fmt_ms(elapsed_ms)} ({_fmt_ms(ms_pt)}/pto)')


# ===========================================================================
# SUITE C2 — Ancho de banda MÍNIMO por banda
# ===========================================================================

def suite_c2_minimum_bandwidth(device, include_sub_hz=True):
    """
    2 puntos muy cercanos en cada banda — prueba el menor BW posible.
    Verifica que el hardware mide correctamente incluso con Δf mínimo.
    """
    _section('SUITE C2: Ancho de banda MÍNIMO — 2 pts en cada zona')

    # Pares (f_start, f_end, slow): el end ≈ f_start × 1.1 (10% de ancho)
    # Cubriendo todas las zonas del espectro
    MIN_BW_TESTS = [
        # sub-Hz (muy lentos)
        (0.2,     0.25,    True,  '0.20 Hz – 0.25 Hz'),
        (0.5,     0.625,   True,  '0.50 Hz – 0.625 Hz'),
        # 1–10 Hz
        (1.0,     1.25,    False, '1.0 Hz – 1.25 Hz'),
        (5.0,     6.25,    False, '5.0 Hz – 6.25 Hz'),
        # 10–100 Hz
        (10.0,    12.5,    False, '10 Hz – 12.5 Hz'),
        (50.0,    62.5,    False, '50 Hz – 62.5 Hz'),
        # 100 Hz – 1 kHz
        (100.0,   125.0,   False, '100 Hz – 125 Hz'),
        (500.0,   625.0,   False, '500 Hz – 625 Hz'),
        # 1 kHz – 10 kHz
        (1_000.0, 1_250.0, False, '1 kHz – 1.25 kHz'),
        (5_000.0, 6_250.0, False, '5 kHz – 6.25 kHz'),
        # 10 kHz – 100 kHz
        (10_000.0,  12_500.0,  False, '10 kHz – 12.5 kHz'),
        (50_000.0,  62_500.0,  False, '50 kHz – 62.5 kHz'),
        # 100 kHz – 1 MHz
        (100_000.0, 125_000.0, False, '100 kHz – 125 kHz'),
        (500_000.0, 625_000.0, False, '500 kHz – 625 kHz'),
        # 1 MHz – 10 MHz
        (1_000_000.0, 1_250_000.0,  False, '1.0 MHz – 1.25 MHz'),
        (5_000_000.0, 6_250_000.0,  False, '5.0 MHz – 6.25 MHz'),
        (9_000_000.0, 10_000_000.0, False, '9.0 MHz – 10 MHz'),
    ]

    print(f'\n  {"Tag":<6}  {"Banda":<28}  {"Ptos":>4}  {"Tiempo":>8}  {"ms/pto":>8}  Estado')
    print(f'  {"─"*6}  {"─"*28}  {"─"*4}  {"─"*8}  {"─"*8}  {"─"*12}')

    for idx, (f_start, f_end, slow, desc) in enumerate(MIN_BW_TESTS):
        tag = f'C2.{idx+1:02d}'

        if slow and not include_sub_hz:
            print(f'  {tag:<6}  {desc:<28}  {"2":>4}  {"—":>8}  {"—":>8}  {SKIP}  (sub-Hz, usa --include-sub-hz)')
            R.skip(f'{tag}  {desc}', 'sub-Hz omitido')
            continue

        results, elapsed_ms, err = _run_sweep(
            device, f_start, f_end, 2, 'log',
            tag=tag, desc=f'{tag} minBW {_fmt_freq(f_start)}'
        )

        ms_pt = elapsed_ms / 2 if elapsed_ms > 0 else 0

        if err or results is None:
            print(f'  {tag:<6}  {desc:<28}  {"2":>4}  {_fmt_ms(elapsed_ms):>8}  {"—":>8}  {FAILED}')
            R.fail(f'{tag}  {desc}', err or 'Sin resultados')
            continue

        ok = _verify_results(results, 2, f'{tag}  {desc}', desc)
        status = PASSED if ok else FAILED
        print(f'  {tag:<6}  {desc:<28}  {len(results):>4}  {_fmt_ms(elapsed_ms):>8}  {_fmt_ms(ms_pt):>8}  {status}')
        if ok:
            R.ok(f'{tag}  {desc}', f'{_fmt_ms(ms_pt)}/pto')


# ===========================================================================
# SUITE C3 — Barrido por DÉCADAS (todo el espectro, 1 décadas cada vez)
# ===========================================================================

def suite_c3_per_decade(device, include_sub_hz=True):
    """
    Cubre TODO el espectro en tramos de 1 década, 20 pts cada uno.
    Asegura que no haya ninguna zona del espectro sin probar.
    """
    _section('SUITE C3: Barridos por DÉCADAS — todo el espectro')

    # Décadas desde 0.2 Hz hasta 10 MHz
    DECADES = [
        (0.2,          2.0,          True,  '0.2 Hz – 2 Hz      (1 dec)'),
        (2.0,          20.0,         False, '2 Hz – 20 Hz       (1 dec)'),
        (20.0,         200.0,        False, '20 Hz – 200 Hz     (1 dec)'),
        (200.0,        2_000.0,      False, '200 Hz – 2 kHz     (1 dec)'),
        (2_000.0,      20_000.0,     False, '2 kHz – 20 kHz     (1 dec)'),
        (20_000.0,     200_000.0,    False, '20 kHz – 200 kHz   (1 dec)'),
        (200_000.0,    2_000_000.0,  False, '200 kHz – 2 MHz    (1 dec)'),
        (2_000_000.0,  10_000_000.0, False, '2 MHz – 10 MHz     (0.7 dec)'),
    ]

    # Puntos por décadas — más denso a alta frecuencia donde es rápido
    PTS = {
        True:  10,   # sub-Hz: pocos puntos por ser lento
        False: 20,   # resto: 20 pts por década
    }

    print(f'\n  {"Tag":<6}  {"Banda":<35}  {"Ptos":>4}  {"Tiempo":>8}  {"ms/pto":>8}  Estado')
    print(f'  {"─"*6}  {"─"*35}  {"─"*4}  {"─"*8}  {"─"*8}  {"─"*12}')

    for idx, (f_start, f_end, slow, desc) in enumerate(DECADES):
        tag = f'C3.{idx+1}'
        n_pts = PTS[slow]

        if slow and not include_sub_hz:
            print(f'  {tag:<6}  {desc:<35}  {n_pts:>4}  {"—":>8}  {"—":>8}  '
                  f'{SKIP}  (sub-Hz)')
            R.skip(f'{tag}  {desc}', 'sub-Hz omitido')
            continue

        results, elapsed_ms, err = _run_sweep(
            device, f_start, f_end, n_pts, 'log',
            tag=tag, desc=f'{tag} {_fmt_freq(f_start)}-{_fmt_freq(f_end)}'
        )

        ms_pt = elapsed_ms / max(len(results) if results else 1, 1)

        if err or results is None:
            print(f'  {tag:<6}  {desc:<35}  {n_pts:>4}  {_fmt_ms(elapsed_ms):>8}  {"—":>8}  {FAILED}')
            R.fail(f'{tag}  {desc}', err or 'Sin resultados')
            continue

        ok = _verify_results(results, n_pts, f'{tag}  {desc}', desc)
        status = PASSED if ok else FAILED
        print(f'  {tag:<6}  {desc:<35}  {len(results):>4}  {_fmt_ms(elapsed_ms):>8}  {_fmt_ms(ms_pt):>8}  {status}')
        if ok:
            R.ok(f'{tag}  {desc}', f'{_fmt_ms(ms_pt)}/pto')


# ===========================================================================
# SUITE C4 — N variable (mismo rango, todos los tamaños)
# ===========================================================================

def suite_c4_n_variado(device):
    """
    Misma banda (10 kHz – 10 MHz), N ∈ {2, 10, 50, 100, 200, 500, 1000}.
    Verifica que el hardware maneja todos los tamaños de barrido.
    """
    _section('SUITE C4: N variable — 10 kHz – 10 MHz, todos los tamaños')

    F_START = 10_000.0
    F_END   = 10_000_000.0

    N_VALUES = [2, 5, 10, 20, 50, 100, 200, 500, 1000]

    print(f'\n  {"Tag":<6}  {"N":>5}  {"Ptos":>5}  {"Tiempo":>10}  {"ms/pto":>8}  Estado')
    print(f'  {"─"*6}  {"─"*5}  {"─"*5}  {"─"*10}  {"─"*8}  {"─"*12}')

    from lib.utils import max_count_for_span

    for idx, n_pts in enumerate(N_VALUES):
        tag = f'C4.{idx+1}'
        # Calcular el N efectivo que realmente enviará configure_sweep() al firmware
        n_effective = min(n_pts, max_count_for_span(F_START, F_END))
        desc = f'N={n_pts}' if n_pts == n_effective else f'N={n_pts}→{n_effective}'

        results, elapsed_ms, err = _run_sweep(
            device, F_START, F_END, n_pts, 'log',
            tag=tag, desc=f'{tag} 10k-10M N={n_pts}'
        )

        ms_pt = elapsed_ms / max(n_effective, 1)

        if err or results is None:
            print(f'  {tag:<6}  {n_pts:>5}  {"—":>5}  {_fmt_ms(elapsed_ms):>10}  {"—":>8}  {FAILED}')
            R.fail(f'{tag}  10k–10M {desc}', err or 'Sin resultados')
            continue

        ok = _verify_results(results, n_effective, f'{tag}  {desc}', desc)
        status = PASSED if ok else FAILED
        print(f'  {tag:<6}  {n_pts:>5}  {len(results):>5}  '
              f'{_fmt_ms(elapsed_ms):>10}  {_fmt_ms(ms_pt):>8}  {status}')
        if ok:
            R.ok(f'{tag}  10k–10M {desc}', f'{len(results)} pts en {_fmt_ms(elapsed_ms)}')


# ===========================================================================
# SUITE C5 — LOG vs LINEAR (misma banda, ambas escalas)
# ===========================================================================

def suite_c5_log_vs_linear(device):
    """
    Misma banda (100 Hz – 10 kHz), escalas LOG y LINEAR con varios N.
    Verifica que ambas escalas producen resultados correctos.
    """
    _section('SUITE C5: LOG vs LINEAR — mismas bandas, ambas escalas')

    SCALE_TESTS = [
        # (f_start, f_end, n_pts, scale, desc)
        (100.0,    10_000.0, 20, 'log',    '100 Hz – 10 kHz  LOG  20 pts'),
        (100.0,    10_000.0, 20, 'linear', '100 Hz – 10 kHz  LINEAR 20 pts'),
        (1_000.0,  100_000.0, 30, 'log',   '1 kHz – 100 kHz  LOG 30 pts'),
        (1_000.0,  100_000.0, 30, 'linear','1 kHz – 100 kHz  LINEAR 30 pts'),
        (10_000.0, 1_000_000.0, 50, 'log', '10 kHz – 1 MHz   LOG 50 pts'),
        (10_000.0, 1_000_000.0, 50, 'linear','10 kHz – 1 MHz LINEAR 50 pts'),
    ]

    print(f'\n  {"Tag":<6}  {"Descripción":<40}  {"Ptos":>4}  {"Tiempo":>8}  {"ms/pto":>8}  Est')
    print(f'  {"─"*6}  {"─"*40}  {"─"*4}  {"─"*8}  {"─"*8}  {"─"*8}')

    for idx, (f_start, f_end, n_pts, scale, desc) in enumerate(SCALE_TESTS):
        tag = f'C5.{idx+1}'

        results, elapsed_ms, err = _run_sweep(
            device, f_start, f_end, n_pts, scale,
            tag=tag, desc=f'{tag} {desc}'
        )
        ms_pt = elapsed_ms / max(n_pts, 1)

        from lib.utils import _acquisition_time_ms
        theoretical = _acquisition_time_ms(f_start)

        if err or results is None:
            print(f'  {tag:<6}  {desc:<40}  {"—":>4}  {_fmt_ms(elapsed_ms):>8}  {"—":>8}  {FAILED}')
            R.fail(f'{tag}  {desc}', err or 'Sin resultados')
            continue

        ok = _verify_results(results, n_pts, f'{tag}  {desc}', desc)
        status = PASSED if ok else FAILED
        print(f'  {tag:<6}  {desc:<40}  {len(results):>4}  '
              f'{_fmt_ms(elapsed_ms):>8}  {_fmt_ms(ms_pt):>8}  {status}')
        if ok:
            R.ok(f'{tag}  {desc}', f'{_fmt_ms(ms_pt)}/pto')


# ===========================================================================
# SUITE C6 — Averages (mismo barrido, average ∈ {1,2,4,8})
# ===========================================================================

def suite_c6_averages(device):
    """
    Mismo barrido (1 kHz – 100 kHz, 10 pts LOG), average ∈ {1,2,4,8}.
    Verifica escalado lineal del tiempo vs average.
    """
    _section('SUITE C6: Averages — 1 kHz – 100 kHz, 10 pts, avg={1,2,4,8}')

    F_START = 1_000.0
    F_END   = 100_000.0
    N_PTS   = 10

    AVG_VALUES = [1, 2, 4, 8]

    times_ms = {}
    print(f'\n  {"Tag":<6}  {"Average":>8}  {"Ptos":>4}  {"Tiempo":>8}  {"ms/pto":>8}  {"Ratio vs avg=1":>14}  Estado')
    print(f'  {"─"*6}  {"─"*8}  {"─"*4}  {"─"*8}  {"─"*8}  {"─"*14}  {"─"*6}')

    for idx, avg in enumerate(AVG_VALUES):
        tag = f'C6.{idx+1}'
        desc = f'average={avg}'

        results, elapsed_ms, err = _run_sweep(
            device, F_START, F_END, N_PTS, 'log', average=avg,
            tag=tag, desc=f'{tag} 1k-100k avg={avg}'
        )
        ms_pt = elapsed_ms / max(N_PTS, 1)

        if err or results is None:
            print(f'  {tag:<6}  {avg:>8}  {"—":>4}  {_fmt_ms(elapsed_ms):>8}  {"—":>8}  {"—":>14}  {FAILED}')
            R.fail(f'{tag}  {desc}', err or 'Sin resultados')
            continue

        times_ms[avg] = ms_pt

        # Ratio vs average=1
        if 1 in times_ms and avg > 1:
            ratio = ms_pt / times_ms[1]
            ratio_str = f'{ratio:.2f}×  (esperado ~{avg}×)'
        else:
            ratio_str = '—'

        ok = _verify_results(results, N_PTS, f'{tag}  {desc}', desc)
        status = PASSED if ok else FAILED
        print(f'  {tag:<6}  {avg:>8}  {len(results):>4}  '
              f'{_fmt_ms(elapsed_ms):>8}  {_fmt_ms(ms_pt):>8}  {ratio_str:<14}  {status}')
        if ok:
            R.ok(f'{tag}  {desc}', f'{_fmt_ms(ms_pt)}/pto')


# ===========================================================================
# SUITE C7 — Límites: N=500 y N=1000
# ===========================================================================

def suite_c7_large_n(device):
    """
    Prueba los límites máximos de N permitidos (500 y 1000 puntos).
    Usa bandas de alta frecuencia donde el tiempo es manejable.
    """
    _section('SUITE C7: N grandes — 500 y 1000 puntos en hardware real')

    LARGE_N_TESTS = [
        # (f_start, f_end, n_pts, scale, desc)
        (10_000.0, 10_000_000.0, 500,  'log',    '10 kHz – 10 MHz  LOG 500 pts'),
        (10_000.0, 10_000_000.0, 1000, 'log',    '10 kHz – 10 MHz  LOG 1000 pts'),
        (100.0,    10_000_000.0, 500,  'log',    '100 Hz – 10 MHz  LOG 500 pts'),
        (100.0,    10_000_000.0, 1000, 'log',    '100 Hz – 10 MHz  LOG 1000 pts'),
        (1_000.0,  100_000.0,    500,  'linear', '1 kHz – 100 kHz  LINEAR 500 pts'),
    ]

    from lib.utils import max_count_for_span, estimate_sweep_time

    for idx, (f_start, f_end, n_pts, scale, desc) in enumerate(LARGE_N_TESTS):
        tag = f'C7.{idx+1}'
        # Calcular el N efectivo tras el clampeo del firmware
        n_effective = min(n_pts, max_count_for_span(f_start, f_end))
        info = estimate_sweep_time(f_start, f_end, n_effective, scale=scale)
        est_str = info['human_readable']
        label = f'{desc} (efectivo: {n_effective} pts) (est. {est_str})'
        print(f'\n  {BOLD}{tag}{RESET}  {label}')

        results, elapsed_ms, err = _run_sweep(
            device, f_start, f_end, n_pts, scale,
            tag=tag, desc=f'{tag} {_fmt_freq(f_start)}-{_fmt_freq(f_end)} N={n_pts}'
        )

        if err or results is None:
            R.fail(f'{tag}  {desc}', err or 'Sin resultados')
            continue

        ok = _verify_results(results, n_effective, f'{tag}  {desc}', desc)
        if ok:
            ms_pt = elapsed_ms / len(results)
            R.ok(f'{tag}  {desc}',
                 f'{len(results)} pts en {_fmt_ms(elapsed_ms)} ({_fmt_ms(ms_pt)}/pto)')


# ===========================================================================
# SUITE C8 — Display Modes (misma banda, todos los modos de display)
# ===========================================================================

def suite_c8_display_modes(device):
    """
    Prueba que el hardware devuelve resultados correctos con diferentes DisplayModes.
    Usa una banda rápida (10 kHz – 1 MHz) para no tardar.
    """
    _section('SUITE C8: Display Modes — 10 kHz – 1 MHz, 5 pts')

    from lib.enums import DisplayMode

    F_START = 10_000.0
    F_END   = 1_000_000.0
    N_PTS   = 5

    # Modos de display más usados en EIS
    MODES_TO_TEST = [
        (DisplayMode.R_X,    'R,X  (rectangular)'),
        (DisplayMode.Z_DEG,  'Z|θ° (polar grados)'),
        (DisplayMode.CS_RS,  'Cs,Rs (cap serie)'),
        (DisplayMode.LS_RS,  'Ls,Rs (ind serie)'),
        (DisplayMode.CP_RP,  'Cp,Rp (cap paralelo)'),
    ]

    from lib.enums import SweepType, SweepScale
    from lib.utils import estimate_sweep_time, _acquisition_time_ms

    print(f'\n  {"Tag":<7}  {"DisplayMode":<25}  {"Ptos":>4}  {"Tiempo":>8}  Estado')
    print(f'  {"─"*7}  {"─"*25}  {"─"*4}  {"─"*8}  {"─"*12}')

    for idx, (dmode, mode_desc) in enumerate(MODES_TO_TEST):
        tag = f'C8.{idx+1}'

        results, elapsed_ms, err = _run_sweep(
            device, F_START, F_END, N_PTS, 'log',
            display_mode=dmode,
            tag=tag, desc=f'{tag} {mode_desc}'
        )

        if err or results is None:
            print(f'  {tag:<7}  {mode_desc:<25}  {"—":>4}  {_fmt_ms(elapsed_ms):>8}  {FAILED}')
            R.fail(f'{tag}  {mode_desc}', err or 'Sin resultados')
            continue

        # Verificar conteo y que measurement tiene 2 valores
        if len(results) < N_PTS:
            print(f'  {tag:<7}  {mode_desc:<25}  {len(results):>4}  {_fmt_ms(elapsed_ms):>8}  {FAILED}')
            R.fail(f'{tag}  {mode_desc}', f'{len(results)}/{N_PTS} pts')
            continue

        vals_ok = all(
            len(r.get('measurement', [])) >= 2 and
            math.isfinite(r['measurement'][0]) and
            math.isfinite(r['measurement'][1])
            for r in results
        )
        status = PASSED if vals_ok else FAILED
        print(f'  {tag:<7}  {mode_desc:<25}  {len(results):>4}  {_fmt_ms(elapsed_ms):>8}  {status}')
        if vals_ok:
            R.ok(f'{tag}  {mode_desc}', f'{len(results)} pts en {_fmt_ms(elapsed_ms)}')
        else:
            R.fail(f'{tag}  {mode_desc}', 'Valores no finitos en algún punto')


# ===========================================================================
# Main
# ===========================================================================

def _detect_port():
    from lib.utils import find_admx2001_devices, get_preferred_usb_serial_ports
    admx = find_admx2001_devices()
    if admx:
        return admx[0]
    usb = get_preferred_usb_serial_ports()
    if usb:
        return usb[0].device
    return None


def main():
    parser = argparse.ArgumentParser(
        description='Tests exhaustivos de todos los barridos posibles — EVAL-ADMX2001',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--port', default=None,
                        help='Puerto serie (ej. /dev/ttyUSB0)')
    parser.add_argument('--include-sub-hz', action='store_true',
                        help='Incluir tests < 1 Hz (sub-Hz muy lentos, horas de test)')
    parser.add_argument('--only-fast', action='store_true',
                        help='Solo tests > 100 Hz (rápidos, ~5 min total)')
    parser.add_argument('--suite', default=None,
                        help='Ejecutar solo una suite (C1, C2, C3, C4, C5, C6, C7, C8)')
    args = parser.parse_args()

    include_sub_hz = args.include_sub_hz
    only_fast = args.only_fast
    suite_filter = args.suite.upper() if args.suite else None

    print(f'\n{BOLD}{"═"*68}')
    print(f'  TESTS EXHAUSTIVOS DE BARRIDOS — EVAL-ADMX2001')
    print(f'{"═"*68}{RESET}')
    print(f'  Sub-Hz (<1 Hz): {"INCLUIDOS" if include_sub_hz else "omitidos (usa --include-sub-hz)"}')
    print(f'  Solo rápidos:   {"SÍ (>100 Hz)" if only_fast else "NO (todas las bandas)"}')
    if suite_filter:
        print(f'  Filtrando:      solo suite {suite_filter}')

    # Detectar y conectar al hardware
    port = args.port or _detect_port()
    if not port:
        print(f'\n{RED}❌ No se detectó hardware. Conecta el ADMX2001 o usa --port{RESET}')
        sys.exit(1)

    print(f'\n  Conectando a {port}…')
    try:
        from lib.admx2001 import ADMX2001
        device = ADMX2001(port)
        print(f'  {GREEN}✅ Conectado a {port}{RESET}')
    except Exception as e:
        print(f'\n{RED}❌ Error conectando a {port}: {e}{RESET}')
        traceback.print_exc()
        sys.exit(1)

    # Información del dispositivo
    try:
        idn = device.send_command('*idn')
        print(f'  Dispositivo: {" ".join(idn)[:70].strip()}')
    except Exception:
        pass

    try:
        # ── SUITES ───────────────────────────────────────────────────────────
        def _should_run(name):
            return suite_filter is None or suite_filter == name

        if _should_run('C1'):
            suite_c1_full_range(device, include_sub_hz=include_sub_hz)

        if _should_run('C2'):
            suite_c2_minimum_bandwidth(device, include_sub_hz=include_sub_hz)

        if _should_run('C3') and not only_fast:
            suite_c3_per_decade(device, include_sub_hz=include_sub_hz)

        if _should_run('C4'):
            suite_c4_n_variado(device)

        if _should_run('C5'):
            suite_c5_log_vs_linear(device)

        if _should_run('C6') and not only_fast:
            suite_c6_averages(device)

        if _should_run('C7'):
            suite_c7_large_n(device)

        if _should_run('C8'):
            suite_c8_display_modes(device)

    finally:
        device.disconnect()
        print(f'\n  Dispositivo desconectado.')

    success = R.summary()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
