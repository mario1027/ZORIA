#!/usr/bin/env python3
"""
benchmark_timing.py — Mide los tiempos reales de medición del EVAL-ADMX2001.

Este script conecta al hardware y ejecuta barridos cortos (sweeps) en cada
banda de frecuencia usando el mismo método que la aplicación ZORIA (configure_sweep
+ perform_sweep). Los tiempos inter-punto se registran automáticamente en
hw_timing_profile.json mediante update_from_sweep().

MÉTODO CORRECTO:
  Se usan sweeps reales (no el comando z individual), porque el z puntual
  incluye un overhead fijo de comunicación de ~3s por comando que NO es
  representativo del tiempo real de adquisición en un barrido continuo.

Ese perfil es utilizado automáticamente por la aplicación ZORIA para:
  - Calcular timeouts de segmento precisos (no teóricos).
  - Estimar la duración real de un barrido antes de iniciarlo.

USO:
    python benchmark_timing.py
    python benchmark_timing.py --port /dev/ttyUSB0
    python benchmark_timing.py --port /dev/ttyUSB0 --average 2
    python benchmark_timing.py --full         # incluye bandas lentas (>2 min)
    python benchmark_timing.py --show         # solo muestra el perfil guardado

OPCIONES:
    --port PORT     Puerto serie del dispositivo (auto-detección si se omite)
    --average N     Número de promedios por medición (default: 1)
    --full          Incluir bandas de frecuencia baja (<20 Hz, muy lento)
    --show          Muestra el perfil guardado sin conectar al hardware

RESULTADO:
    Genera/actualiza hw_timing_profile.json con los tiempos reales medidos.
    Muestra tabla de resultados y comparación con el modelo teórico.
"""

import sys
import os
import time
import argparse
import math

# Asegurar que el directorio del proyecto esté en el path
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)


# ---------------------------------------------------------------------------
# Bandas de benchmark: barridos cortos representativos por tramo
# Cada banda = (start_hz, end_hz, n_points, label, slow=optional)
# slow=True → se omite a menos que se use --full
# ---------------------------------------------------------------------------
BENCHMARK_BANDS = [
    # (start_hz,  end_hz,  n_pts, label,                      slow)
    (1_000_000.0, 10_000_000.0,  8, "1 MHz – 10 MHz",         False),
    (  100_000.0,  1_000_000.0,  8, "100 kHz – 1 MHz",        False),
    (   10_000.0,    100_000.0,  8, "10 kHz – 100 kHz",       False),
    (    1_000.0,     10_000.0,  8, "1 kHz – 10 kHz",         False),
    (      100.0,      1_000.0,  8, "100 Hz – 1 kHz",         False),
    (       10.0,        100.0,  6, "10 Hz – 100 Hz",         False),
    (        1.0,         10.0,  4, "1 Hz – 10 Hz",           True),   # ~2.5 min
    (        0.2,          1.0,  2, "0.2 Hz – 1 Hz",          True),   # ~10 min
]


def fmt_freq(f: float) -> str:
    """Formatea frecuencias de forma legible."""
    if f >= 1_000_000:
        return f"{f/1_000_000:.3g} MHz"
    if f >= 1_000:
        return f"{f/1_000:.3g} kHz"
    if f >= 1:
        return f"{f:.4g} Hz"
    return f"{f:.3g} Hz"


def fmt_time(ms: float) -> str:
    """Formatea tiempo en ms de forma legible."""
    if ms < 1000:
        return f"{ms:.1f} ms"
    if ms < 60_000:
        return f"{ms/1000:.2f} s"
    return f"{ms/60_000:.2f} min"


def run_benchmark(port: str, average: int, include_slow: bool = False) -> None:
    """
    Ejecuta el benchmark usando sweeps reales (configure_sweep + perform_sweep).

    Este es el método correcto: mide el tiempo inter-punto dentro de un sweep
    continuo, que es exactamente lo que hace la app ZORIA en producción.
    Los tiempos se guardan automáticamente en hw_timing_profile.json mediante
    update_from_sweep() que ya está implementado en perform_sweep().
    """
    from lib.admx2001 import ADMX2001
    from lib.enums import DisplayMode, SweepType, SweepScale
    from lib.hw_timing_profile import HardwareTimingProfile, DEFAULT_PROFILE_PATH
    from lib.utils import _acquisition_time_ms

    profile = HardwareTimingProfile()

    bands = [(s, e, n, lbl) for s, e, n, lbl, slow in BENCHMARK_BANDS
             if not slow or include_slow]

    # Tiempo total estimado
    total_est_s = sum(
        _acquisition_time_ms(s, average) * n / 1000.0
        for s, e, n, _ in bands
    )

    print(f"\n{'═'*68}")
    print(f"  BENCHMARK DE TIMING — EVAL-ADMX2001 (método: sweep real)")
    print(f"{'═'*68}")
    print(f"  Puerto:    {port}")
    print(f"  Average:   {average}")
    print(f"  Bandas:    {len(bands)}")
    print(f"  Perfil:    {DEFAULT_PROFILE_PATH}")
    print(f"  Est. total: ~{fmt_time(total_est_s*1000)} (teórico)")
    if not include_slow:
        print(f"  Nota: bandas <1 Hz omitidas (muy lentas). Usa --full para incluirlas.")
    print(f"{'─'*68}\n")

    print("Conectando al dispositivo…")
    try:
        device = ADMX2001(port)
    except Exception as e:
        print(f" Error conectando: {e}")
        sys.exit(1)
    print(" Conectado\n")

    # Preparar dispositivo
    try:
        device.set_display_mode(DisplayMode.R_X)
        device.set_magnitude(1.0)
        device.set_average(average)
        device.set_mdelay(0)
        device.set_tdelay(0)
        device.set_gain_auto()
    except Exception as e:
        print(f" Error configurando dispositivo: {e}")

    print(f"  {'Banda':<30}  {'Ptos':>4}  {'Tiempo':>8}  {'ms/pto':>8}  {'Teórico':>8}  {'Ratio':>6}  Estado")
    print(f"  {'─'*30}  {'─'*4}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*6}  {'─'*12}")

    all_results = {}

    for start_hz, end_hz, n_pts, label in bands:
        theoretical_ms = _acquisition_time_ms(start_hz, average)
        est_total_s = theoretical_ms * n_pts / 1000.0
        sweep_timeout = max(120.0, est_total_s * 5 + 30.0)

        try:
            device.configure_sweep(
                SweepType.FREQUENCY,
                start_hz / 1000.0,   # configure_sweep espera kHz
                end_hz / 1000.0,
                SweepScale.LOG,
                count=n_pts
            )
        except Exception as e:
            print(f"  {label:<30}    configure_sweep falló: {e}")
            continue

        t0 = time.perf_counter()
        try:
            results = device.perform_sweep(timeout=sweep_timeout)
        except Exception as e:
            elapsed = time.perf_counter() - t0
            print(f"  {label:<30}  {n_pts:>4}  {fmt_time(elapsed*1000):>8}  "
                  f"{'—':>8}  {fmt_time(theoretical_ms):>8}  {'—':>6}   {e}")
            continue
        elapsed_s = time.perf_counter() - t0

        n_recv = len(results)
        if n_recv < 2:
            print(f"  {label:<30}  {n_pts:>4}  {fmt_time(elapsed_s*1000):>8}  "
                  f"{'<2 pts':>8}  {fmt_time(theoretical_ms):>8}  {'—':>6}   insuficiente")
            continue

        # Tiempo medio por punto (excluyendo overhead de setup: tomar desde 2° punto)
        ms_per_pt = elapsed_s * 1000.0 / n_recv

        ratio = ms_per_pt / theoretical_ms if theoretical_ms > 0 else float('nan')
        if ratio < 0.3:
            indicator = " muy rápido"
        elif ratio < 0.8:
            indicator = " rápido"
        elif ratio <= 1.5:
            indicator = " ok"
        elif ratio <= 3.0:
            indicator = " lento"
        else:
            indicator = " MUY LENTO"

        print(f"  {label:<30}  {n_recv:>4}  {fmt_time(elapsed_s*1000):>8}  "
              f"{fmt_time(ms_per_pt):>8}  {fmt_time(theoretical_ms):>8}  "
              f"{ratio:>5.2f}×  {indicator}")

        all_results[label] = {
            'start_hz': start_hz,
            'n_pts': n_recv,
            'elapsed_ms': elapsed_s * 1000.0,
            'ms_per_pt': ms_per_pt,
            'theoretical_ms': theoretical_ms,
            'ratio': ratio,
        }

    device.disconnect()

    # Recargar perfil (fue actualizado por update_from_sweep dentro de perform_sweep)
    profile.load()
    print(f"\n{'─'*68}")
    print(f" Perfil actualizado: {profile.path}")
    print(f"   {profile.summary()}")
    print(f"{'═'*68}\n")

    # Resumen
    if all_results:
        off = {lbl: v for lbl, v in all_results.items()
               if v['ratio'] > 3.0 or v['ratio'] < 0.2}
        if off:
            print("  BANDAS CON RATIO FUERA DEL ESPERADO (>3× o <0.2×):")
            for lbl, v in off.items():
                print(f"   {lbl:<30}: medido={fmt_time(v['ms_per_pt'])} "
                      f"vs teoría={fmt_time(v['theoretical_ms'])} "
                      f"(ratio={v['ratio']:.2f}×)")
            print("\n  → El perfil real se usará para futuros timeouts.")
            print("  → El modelo teórico puede necesitar ajuste.\n")
        else:
            print(" Todos los ratios dentro del rango esperado (0.2×–3×).\n")


    device.disconnect()


def show_profile() -> None:
    """Muestra el perfil de timing guardado."""
    from lib.hw_timing_profile import HardwareTimingProfile, DEFAULT_PROFILE_PATH
    from lib.utils import _acquisition_time_ms

    profile = HardwareTimingProfile()

    if not profile._data:
        print("Perfil vacío — ejecuta el benchmark con hardware conectado primero.")
        return

    print(f"\n{'═'*60}")
    print(f"  PERFIL DE TIMING HARDWARE: {DEFAULT_PROFILE_PATH}")
    print(f"{'═'*60}")
    print(f"  {profile.summary()}")
    print(f"{'─'*60}")
    print(f"{'Frecuencia':>12}  {'Mediana':>10}  {'Muestras':>8}  {'vs Teórico':>12}")
    print(f"{'─'*12}  {'─'*10}  {'─'*8}  {'─'*12}")

    for freq_hz in sorted(profile._data.keys()):
        samples = profile._data[freq_hz]
        s = sorted(samples)
        median = s[len(s) // 2]
        theoretical = _acquisition_time_ms(float(freq_hz))
        ratio = median / theoretical if theoretical > 0 else float('nan')
        print(f"{fmt_freq(float(freq_hz)):>12}  {fmt_time(median):>10}  "
              f"{len(samples):>8}  {ratio:>10.2f}×")

    print(f"{'═'*60}\n")


def detect_port() -> str:
    """Auto-detecta el puerto del ADMX2001."""
    from lib.utils import find_admx2001_devices, get_preferred_usb_serial_ports
    import serial.tools.list_ports

    # Primero intentar con el detector específico
    admx_ports = find_admx2001_devices()
    if admx_ports:
        print(f"  Puerto detectado automáticamente: {admx_ports[0]}")
        return admx_ports[0]

    # Si no, listar todos los USB seriales
    ports = get_preferred_usb_serial_ports()
    if ports:
        port = ports[0].device
        print(f"  Puerto USB serie detectado: {port}")
        return port

    print(" No se encontró ningún dispositivo serie USB.")
    print("   Conecta el cable USB-UART y vuelve a intentar,")
    print("   o especifica el puerto con --port /dev/ttyUSBx")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark de timing real del EVAL-ADMX2001",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--port', default=None,
                        help="Puerto serie (ej. /dev/ttyUSB0, COM3)")
    parser.add_argument('--average', type=int, default=1,
                        help="Número de promedios por medición (default: 1)")
    parser.add_argument('--full', action='store_true',
                        help="Incluir bandas de baja frecuencia (<1 Hz, muy lento)")
    parser.add_argument('--show', action='store_true',
                        help="Solo muestra el perfil guardado sin conectar hardware")

    args = parser.parse_args()

    if args.show:
        show_profile()
        return

    # Validar argumentos
    if args.average < 1 or args.average > 256:
        parser.error("--average debe estar entre 1 y 256")

    port = args.port or detect_port()
    run_benchmark(port, args.average, include_slow=args.full)


if __name__ == '__main__':
    main()
