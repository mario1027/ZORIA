#!/usr/bin/env python3
"""
test_n_limit_hw.py — Mapeo del límite real de N por rango de décadas
======================================================================

Prueba sistemáticamente distintos valores de N para distintos rangos
de frecuencia a fin de determinar el límite máximo de puntos que
acepta el firmware del EVAL-ADMX2001.

Para cada rango se prueba N ∈ {10, 50, 100, 150, 200, 250, 300, 400, 500}
y se registra el número de puntos efectivamente recibidos.

USO:
    python test_n_limit_hw.py --port /dev/ttyUSB0
    python test_n_limit_hw.py --port /dev/ttyUSB0 --verbose

SALIDA:
    Tabla por rango con N_pedido → N_recibido y si hubo corte.
    Al final imprime un resumen del límite detectado por décadas.
"""

import sys
import os
import time
import argparse
import math

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

GREEN  = '\033[92m'
RED    = '\033[91m'
YELLOW = '\033[93m'
CYAN   = '\033[96m'
BOLD   = '\033[1m'
DIM    = '\033[2m'
RESET  = '\033[0m'


def _abort(device):
    try:
        device.send_command("abort", expect_prompt=False)
        time.sleep(0.2)
    except Exception:
        pass


def _run_n(device, f_start_hz, f_end_hz, n_req, verbose=False):
    """
    Ejecuta un sweep con N=n_req. Devuelve (n_recibido, error_str|None).
    """
    from lib.enums import SweepType, SweepScale, DisplayMode

    _abort(device)

    try:
        device.set_display_mode(DisplayMode.R_X)
        device.set_gain_auto()
        device.set_average(1)
        device.set_mdelay(0)
        device.set_tdelay(0)
        device.set_magnitude(1.0)
    except Exception as e:
        return 0, f'config: {e}'

    try:
        device.configure_sweep(
            SweepType.FREQUENCY,
            f_start_hz / 1000.0,
            f_end_hz   / 1000.0,
            SweepScale.LOG,
            n_req
        )
    except Exception as e:
        return 0, f'configure: {e}'

    # Timeout conservador: min 60s, máximo 120s (sólo usamos bandas rápidas)
    timeout = 120.0

    try:
        t0 = time.perf_counter()
        results = device.perform_sweep(timeout=timeout)
        elapsed = (time.perf_counter() - t0) * 1000.0
    except Exception as e:
        return 0, str(e)

    n_got = len(results) if results else 0
    if verbose:
        print(f'      N={n_req:>5} → {n_got:>5} pts  ({elapsed/1000:.1f}s)')
    return n_got, None


def _decades(f_start, f_end):
    return math.log10(f_end / f_start)


def probe_range(device, label, f_start_hz, f_end_hz, n_list, verbose=False):
    """
    Prueba todos los N en n_list para el rango dado.
    Devuelve lista de (n_req, n_got).
    """
    dec = _decades(f_start_hz, f_end_hz)
    print(f'\n{BOLD}{CYAN}  ─── {label}  ({f_start_hz:.4g} Hz – {f_end_hz:.4g} Hz, '
          f'{dec:.2f} déc) ───{RESET}')
    print(f'  {"N_pedido":>8}  {"N_recibido":>10}  {"Estado":>10}')
    print(f'  {"─"*8}  {"─"*10}  {"─"*10}')

    results = []
    prev_limit = None  # una vez que cortamos, anotamos el límite

    for n_req in n_list:
        n_got, err = _run_n(device, f_start_hz, f_end_hz, n_req, verbose)

        if err:
            status = f'{RED}ERROR: {err[:30]}{RESET}'
            results.append((n_req, 0, 'error'))
        elif n_got >= n_req:
            status = f'{GREEN}OK{RESET}'
            results.append((n_req, n_got, 'ok'))
            prev_limit = n_req  # este N pasó
        else:
            # Recibimos menos de lo pedido — el dispositivo limitó
            pct = 100.0 * n_got / n_req if n_req > 0 else 0
            status = f'{RED}CORTADO → {n_got} ({pct:.0f}%){RESET}'
            results.append((n_req, n_got, 'cut'))

        print(f'  {n_req:>8}  {n_got:>10}  {status}')

        # Si recibimos 0 o muy pocos (<10) dos veces seguidas, el device
        # está en mal estado — abortar el rango.
        if n_got <= 10 and n_req >= 50:
            print(f'  {YELLOW}⚠ Dispositivo en mal estado — abortando rango{RESET}')
            _abort(device)
            time.sleep(1.0)
            break

    # Determinar límite para este rango
    oks = [n for n, got, st in results if st == 'ok']
    cuts = [n for n, got, st in results if st == 'cut']
    limit = max(oks) if oks else 0
    first_cut = min(cuts) if cuts else None

    if first_cut is not None and limit < first_cut:
        print(f'  {BOLD}→ Límite estimado: N ≤ {limit} '
              f'(corte en N={first_cut}){RESET}')
    elif oks:
        print(f'  {BOLD}→ Todos los N probados aceptados (máx: {limit}){RESET}')
    else:
        print(f'  {BOLD}→ No se pudo determinar límite{RESET}')

    return results, limit


def main():
    ap = argparse.ArgumentParser(description='Mapeo límite N por décadas en ADMX2001')
    ap.add_argument('--port', default='/dev/ttyUSB0')
    ap.add_argument('--verbose', action='store_true')
    args = ap.parse_args()

    from lib.admx2001 import ADMX2001

    print(f'{BOLD}{"═"*68}{RESET}')
    print(f'{BOLD}  MAPEO LÍMITE N — EVAL-ADMX2001  port={args.port}{RESET}')
    print(f'{BOLD}{"═"*68}{RESET}')

    device = ADMX2001(port=args.port, baudrate=115200)
    device.connect()
    print(f'  Conectado → {args.port}')

    # Valores de N a probar
    N_LIST = [10, 50, 100, 150, 200, 250, 300, 400, 500]

    # Rangos ordenados de menor a mayor número de décadas.
    # Evitamos frecuencias muy bajas para no perder tiempo.
    RANGES = [
        # (label, f_start_hz, f_end_hz)
        ('0.3 déc  100kHz–200kHz',  100_000,   200_000),   # 0.30 déc
        ('0.5 déc  100kHz–300kHz',  100_000,   300_000),   # 0.48 déc
        ('1 déc    100kHz–1MHz',    100_000, 1_000_000),   # 1.00 déc
        ('1.5 déc  100kHz–3MHz',    100_000, 3_000_000),   # 1.48 déc
        ('2 déc    100kHz–10MHz',   100_000,10_000_000),   # 2.00 déc
        ('2 déc    10kHz–1MHz',      10_000, 1_000_000),   # 2.00 déc alt
        ('3 déc    10kHz–10MHz',     10_000,10_000_000),   # 3.00 déc
        ('4 déc    1kHz–10MHz',       1_000,10_000_000),   # 4.00 déc
        ('5 déc    100Hz–10MHz',        100,10_000_000),   # 5.00 déc
    ]

    summary = []  # [(label, dec, limit)]

    try:
        for label, f0, f1 in RANGES:
            results, limit = probe_range(device, label, f0, f1, N_LIST,
                                         verbose=args.verbose)
            dec = _decades(f0, f1)
            summary.append((label, dec, limit))
    finally:
        try:
            device.disconnect()
            print(f'\n  Dispositivo desconectado.')
        except Exception:
            pass

    # Resumen final
    print(f'\n{BOLD}{"═"*68}{RESET}')
    print(f'{BOLD}  RESUMEN — LÍMITE N POR DÉCADAS{RESET}')
    print(f'{BOLD}{"═"*68}{RESET}')
    print(f'  {"Rango":<35}  {"Décadas":>7}  {"N máx":>6}')
    print(f'  {"─"*35}  {"─"*7}  {"─"*6}')
    for label, dec, limit in summary:
        color = GREEN if limit >= 200 else (YELLOW if limit >= 100 else RED)
        print(f'  {label:<35}  {dec:>7.2f}  {color}{limit:>6}{RESET}')
    print(f'{BOLD}{"═"*68}{RESET}')


if __name__ == '__main__':
    main()
