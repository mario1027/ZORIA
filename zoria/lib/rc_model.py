"""
Modelado y ajuste de circuito RC en paralelo (Z = R / (1 + j·omega·R·C)).
Funciones principales:
- parallel_rc_z(freq_hz, R, C): devuelve (z_real, z_imag)
- fit_parallel_rc(freq_hz, z_real, z_imag): ajusta R y C y devuelve dict {'r','c','cov'}
- fit_parallel_rc_from_csv(filepath): carga CSV (usa `lib.utils.load_sweep_data_from_csv`) y ajusta

El ajuste usa scipy.optimize.curve_fit (se requiere `scipy`).
"""
from __future__ import annotations

import math
from typing import Tuple, Dict

import numpy as np
from scipy.optimize import curve_fit

from .utils import load_sweep_data_from_csv


def parallel_rc_z(freq_hz: np.ndarray, R: float, C: float) -> Tuple[np.ndarray, np.ndarray]:
    """Calcula la parte real e imaginaria de la impedancia de un RC paralelo.

    Z(ω) = R / (1 + j·ω·R·C)

    Args:
        freq_hz: frecuencias en Hz (array)
        R: resistencia en ohmios
        C: capacitancia en faradios

    Returns:
        (z_real, z_imag) arrays
    """
    omega = 2 * math.pi * np.asarray(freq_hz)
    x = omega * R * C
    denom = 1.0 + x ** 2
    z_real = R / denom
    z_imag = -R * x / denom
    return z_real, z_imag


def _model_concat(freq_hz: np.ndarray, R: float, C: float) -> np.ndarray:
    """Función utilizada por curve_fit (paralelo): concatena real+imag en un vector 1D."""
    zr, zi = parallel_rc_z(freq_hz, R, C)
    return np.concatenate([zr, zi])


def series_rc_z(freq_hz: np.ndarray, R: float, C: float) -> Tuple[np.ndarray, np.ndarray]:
    """Calcula la parte real e imaginaria de la impedancia de un RC en serie.

    Z(ω) = R + 1/(j·ω·C) = R - j/(ω·C)

    Args:
        freq_hz: frecuencias en Hz (array)
        R: resistencia en ohmios
        C: capacitancia en faradios

    Returns:
        (z_real, z_imag) arrays
    """
    omega = 2 * math.pi * np.asarray(freq_hz)
    # evitar división por cero en omega
    omega_safe = np.where(omega == 0, 1e-30, omega)
    z_real = np.full_like(omega_safe, float(R), dtype=float)
    z_imag = -1.0 / (omega_safe * C)
    return z_real, z_imag


def _model_concat_series(freq_hz: np.ndarray, R: float, C: float) -> np.ndarray:
    """Función utilizada por curve_fit (serie): concatena real+imag en un vector 1D."""
    zr, zi = series_rc_z(freq_hz, R, C)
    return np.concatenate([zr, zi])


def fit_parallel_rc(freq_hz: np.ndarray, z_real: np.ndarray, z_imag: np.ndarray, *,
                    p0: Tuple[float, float] = None, bounds=None) -> Dict[str, object]:
    """Ajusta R y C a datos de impedancia (partes real e imaginaria).

    Devuelve dict con: 'r' (Ω), 'c' (F), 'cov' (matriz de covarianza), 'success' (bool)

    Notas:
    - Los datos reales e imaginarios se ajustan simultáneamente concatenándolos.
    - Se imponen límites R>0, C>0 por defecto.
    """
    freq = np.asarray(freq_hz, dtype=float)
    zr = np.asarray(z_real, dtype=float)
    zi = np.asarray(z_imag, dtype=float)

    if freq.size == 0 or zr.size == 0:
        raise ValueError("Los arrays de frecuencia/impedancia no pueden estar vacíos")

    ydata = np.concatenate([zr, zi])

    # Estimación inicial
    if p0 is None:
        R0 = max(np.nanmax(np.abs(zr)), 1.0)
        # estimador bruto para C: usar frecuencia media y fase aproximada
        f_med = np.median(freq)
        C0 = 1.0 / (2 * math.pi * max(f_med, 1.0) * R0)
        p0 = (R0, C0)

    # límites por defecto: R>0, C>0
    if bounds is None:
        bounds = ([1e-12, 1e-15], [1e12, 1.0])

    try:
        popt, pcov = curve_fit(_model_concat, freq, ydata, p0=p0, bounds=bounds, maxfev=20000)
        r_fit, c_fit = float(popt[0]), float(popt[1])
        success = True
    except Exception as exc:
        # devolver estimación inicial si falla el ajuste
        r_fit, c_fit, pcov, success = float(p0[0]), float(p0[1]), None, False

    return {"r": r_fit, "c": c_fit, "cov": pcov, "success": success}


def estimate_series_equivalent(freq_hz: np.ndarray, z_real: np.ndarray, z_imag: np.ndarray, *,
                               high_frac: float = 0.25) -> Dict[str, float]:
    """Estima parámetros equivalentes en serie (R_eq, C_eq) a partir del asintótico en altas frecuencias.

    Método:
    - R_eq: mediana de Re(Z) en el `high_frac` superior de frecuencias
    - C_eq: mediana de -1/(omega * Im(Z)) en las mismas frecuencias (filtrando valores válidos)

    Devuelve dict con 'r', 'c', 'r_std', 'c_std', 'n_points'.
    """
    freq = np.asarray(freq_hz, dtype=float)
    zr = np.asarray(z_real, dtype=float)
    zi = np.asarray(z_imag, dtype=float)

    if freq.size == 0:
        raise ValueError('freq vacío')

    # seleccionar las frecuencias más altas
    n = max(3, int(np.ceil(len(freq) * high_frac)))
    idx = np.argsort(freq)[-n:]
    omega = 2 * math.pi * freq[idx]

    r_vals = zr[idx]
    # calcular C estimado punto a punto: C = -1/(omega * Im(Z))
    with np.errstate(divide='ignore', invalid='ignore'):
        c_vals = -1.0 / (omega * zi[idx])

    # filtrar valores finitos y positivos
    c_vals = c_vals[np.isfinite(c_vals) & (c_vals > 0)]

    r_med = float(np.median(r_vals))
    r_std = float(np.std(r_vals))
    c_med = float(np.median(c_vals)) if c_vals.size > 0 else float('nan')
    c_std = float(np.std(c_vals)) if c_vals.size > 0 else float('nan')

    return {'r': r_med, 'c': c_med, 'r_std': r_std, 'c_std': c_std, 'n_points': int(n)}


def estimate_series_from_plateau(freq_hz: np.ndarray, z_real: np.ndarray, z_imag: np.ndarray, *,
                                 low_frac: float = 0.1, mid_frac_for_c: float = 0.5) -> Dict[str, float]:
    """Estima R desde la meseta en bajas frecuencias y C desde la parte imaginaria (serie).

    - R_est: mediana de Re(Z) en el `low_frac` inferior de frecuencias (plateau de baja f)
    - C_est: mediana de -1/(omega * Im(Z)) en la fracción superior `mid_frac_for_c` de frecuencias

    Devuelve dict con 'r','c','r_std','c_std','n_points_r','n_points_c'.
    """
    freq = np.asarray(freq_hz, dtype=float)
    zr = np.asarray(z_real, dtype=float)
    zi = np.asarray(z_imag, dtype=float)

    if freq.size == 0:
        raise ValueError('freq vacío')

    # R desde la meseta de bajas frecuencias
    n_r = max(3, int(np.ceil(len(freq) * low_frac)))
    idx_low = np.argsort(freq)[:n_r]
    r_vals = zr[idx_low]

    # C desde la parte imaginaria en la mitad superior de frecuencias
    idx_c = np.argsort(freq)[int(len(freq) * (1.0 - mid_frac_for_c)) :]
    omega_c = 2 * math.pi * freq[idx_c]
    with np.errstate(divide='ignore', invalid='ignore'):
        c_vals = -1.0 / (omega_c * zi[idx_c])
    c_vals = c_vals[np.isfinite(c_vals) & (c_vals > 0)]

    r_med = float(np.median(r_vals))
    r_std = float(np.std(r_vals))
    c_med = float(np.median(c_vals)) if c_vals.size > 0 else float('nan')
    c_std = float(np.std(c_vals)) if c_vals.size > 0 else float('nan')

    return {
        'r': r_med,
        'c': c_med,
        'r_std': r_std,
        'c_std': c_std,
        'n_points_r': int(n_r),
        'n_points_c': int(c_vals.size),
    }


def fit_series_rc(freq_hz: np.ndarray, z_real: np.ndarray, z_imag: np.ndarray, *,
                   p0: Tuple[float, float] = None, bounds=None) -> Dict[str, object]:
    """Ajusta R y C para un RC en serie usando las partes real e imaginaria (modelo IDEAL).

    Si no se proporciona `p0`, usa `estimate_series_equivalent` como inicialización (robusta
    cuando la topología es realmente serie o cuando el asintótico en alta frecuencia refleja R).

    Devuelve dict con: 'r' (Ω), 'c' (F), 'cov' (matriz de covarianza), 'success' (bool)
    """
    freq = np.asarray(freq_hz, dtype=float)
    zr = np.asarray(z_real, dtype=float)
    zi = np.asarray(z_imag, dtype=float)

    if freq.size == 0 or zr.size == 0:
        raise ValueError("Los arrays de frecuencia/impedancia no pueden estar vacíos")

    ydata = np.concatenate([zr, zi])

    # Estimación inicial usando el método asintótico en altas frecuencias si p0 no dado
    if p0 is None:
        est = estimate_series_equivalent(freq, zr, zi, high_frac=0.25)
        R0 = est['r'] if np.isfinite(est['r']) else (float(np.median(zr)) if zr.size > 0 else 1.0)
        C0 = est['c'] if np.isfinite(est['c']) else (1.0 / (2 * math.pi * max(np.median(freq), 1.0) * max(R0, 1.0)))
        p0 = (R0, C0)

    # límites por defecto: R>0, C>0
    if bounds is None:
        bounds = ([1e-12, 1e-15], [1e12, 1.0])

    try:
        popt, pcov = curve_fit(_model_concat_series, freq, ydata, p0=p0, bounds=bounds, maxfev=20000)
        r_fit, c_fit = float(popt[0]), float(popt[1])
        success = True
    except Exception:
        r_fit, c_fit, pcov, success = float(p0[0]), float(p0[1]), None, False

    return {"r": r_fit, "c": c_fit, "cov": pcov, "success": success}


def series_rc_with_leak_z(freq_hz: np.ndarray, R: float, C: float, R_leak: float) -> Tuple[np.ndarray, np.ndarray]:
    """Modelo serie real: R (serie) en serie con la rama (C en paralelo con R_leak).

    Z_total = R + Z_par,  Z_par = 1 / (1/R_leak + j·ω·C)

    Args:
        freq_hz: frecuencias en Hz
        R: resistencia serie (Ω)
        C: capacitancia (F)
        R_leak: resistencia de fuga en paralelo con C (Ω)

    Returns:
        (z_real, z_imag)
    """
    omega = 2 * math.pi * np.asarray(freq_hz)
    x = omega * R_leak * C
    denom = 1.0 + x ** 2
    z_par_real = R_leak / denom
    z_par_imag = -R_leak * x / denom
    z_real = float(R) + z_par_real
    z_imag = z_par_imag
    return z_real, z_imag


def _model_concat_series_with_leak(freq_hz: np.ndarray, R: float, C: float, R_leak: float) -> np.ndarray:
    zr, zi = series_rc_with_leak_z(freq_hz, R, C, R_leak)
    return np.concatenate([zr, zi])


def fit_series_rc_with_leak(freq_hz: np.ndarray, z_real: np.ndarray, z_imag: np.ndarray, *,
                            p0: Tuple[float, float, float] = None, bounds=None) -> Dict[str, object]:
    """Ajusta el modelo serie real: R + (C || R_leak).

    Devuelve dict con keys: 'r', 'c', 'r_leak', 'cov', 'success'.
    """
    freq = np.asarray(freq_hz, dtype=float)
    zr = np.asarray(z_real, dtype=float)
    zi = np.asarray(z_imag, dtype=float)

    if freq.size == 0 or zr.size == 0:
        raise ValueError("Los arrays de frecuencia/impedancia no pueden estar vacíos")

    ydata = np.concatenate([zr, zi])

    # estimaciones iniciales
    if p0 is None:
        R0 = float(np.median(zr)) if zr.size > 0 else 1.0
        f_med = np.median(freq)
        C0 = 1.0 / (2 * math.pi * max(f_med, 1.0) * max(R0, 1.0))
        R_leak0 = max(R0 * 10.0, 1e3)
        p0 = (R0, C0, R_leak0)

    # límites por defecto
    if bounds is None:
        bounds = ([1e-12, 1e-15, 1e0], [1e12, 1.0, 1e12])

    try:
        popt, pcov = curve_fit(_model_concat_series_with_leak, freq, ydata, p0=p0, bounds=bounds, maxfev=30000)
        r_fit, c_fit, r_leak_fit = float(popt[0]), float(popt[1]), float(popt[2])
        success = True
    except Exception:
        r_fit, c_fit, r_leak_fit, pcov, success = float(p0[0]), float(p0[1]), float(p0[2]), None, False

    return {"r": r_fit, "c": c_fit, "r_leak": r_leak_fit, "cov": pcov, "success": success}


def fit_parallel_rc_from_csv(filepath: str) -> Dict[str, object]:
    """Carga sweep desde CSV y ajusta R y C.

    Args:
        filepath: ruta al CSV (puede usarse con `data/<nombre>.csv`)

    Returns:
        Resultado idéntico a `fit_parallel_rc`.
    """
    data = load_sweep_data_from_csv(filepath)
    freq = np.array(data['param'])
    zr = np.array(data['z_real'])
    zi = np.array(data['z_imag'])
    return fit_parallel_rc(freq, zr, zi)


def fit_series_rc_from_csv(filepath: str) -> Dict[str, object]:
    """Carga sweep desde CSV y ajusta R y C usando el modelo en serie (ideal)."""
    data = load_sweep_data_from_csv(filepath)
    freq = np.array(data['param'])
    zr = np.array(data['z_real'])
    zi = np.array(data['z_imag'])
    return fit_series_rc(freq, zr, zi)


def fit_series_rc_with_leak_from_csv(filepath: str) -> Dict[str, object]:
    """Carga sweep desde CSV y ajusta el modelo serie real: R + (C || R_leak)."""
    data = load_sweep_data_from_csv(filepath)
    freq = np.array(data['param'])
    zr = np.array(data['z_real'])
    zi = np.array(data['z_imag'])
    return fit_series_rc_with_leak(freq, zr, zi)


# -----------------------------
# Evaluación y selección
# -----------------------------

def _r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """R² coefficient for concatenated vectors."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1.0 - ss_res / ss_tot) if ss_tot > 0 else 0.0


def evaluate_fit(freq_hz: np.ndarray, z_real: np.ndarray, z_imag: np.ndarray, *,
                 model: str = 'parallel', params: Dict[str, float] = None) -> Dict[str, float]:
    """Calcula métricas de calidad del ajuste para un conjunto de parámetros.

    Devuelve dict con 'r2' (sobre real+imag concatenados), 'rmse' y 'nrmse'.
    """
    freq = np.asarray(freq_hz)
    zr = np.asarray(z_real)
    zi = np.asarray(z_imag)

    if params is None:
        raise ValueError('params no puede ser None')

    R = float(params.get('r'))
    C = float(params.get('c'))

    if model == 'parallel':
        pred_r, pred_i = parallel_rc_z(freq, R, C)
    elif model == 'series':
        pred_r, pred_i = series_rc_z(freq, R, C)
    else:
        raise ValueError('modelo desconocido: use "parallel" o "series"')

    y_true = np.concatenate([zr, zi])
    y_pred = np.concatenate([pred_r, pred_i])

    r2 = _r2_score(y_true, y_pred)
    mse = float(np.mean((y_true - y_pred) ** 2))
    rmse = float(np.sqrt(mse))
    denom = float(np.mean(np.abs(y_true)))
    nrmse = rmse / denom if denom != 0 else float('inf')

    return {'r2': r2, 'rmse': rmse, 'nrmse': nrmse}


def evaluate_bode(freq_hz: np.ndarray, z_real: np.ndarray, z_imag: np.ndarray, *, model: str = 'parallel', params: Dict[str, float] = None, dense_eval: bool = False, n_points: int = 200) -> Dict[str, float]:
    """Calcula métricas separadas para Bode (magnitud y fase).

    - Si `dense_eval=True` compara la curva del modelo con una interpolación
      densa (logspace) de los datos medidos (útil para capturar discrepancias
      entre puntos medidos).
    Devuelve:
      - r2_mag, rmse_mag, nrmse_mag
      - r2_phase, rmse_phase_deg
      - r2_bode_combined (media aritmética de r2_mag y r2_phase)
    """
    if params is None:
        raise ValueError('params no puede ser None')

    freq = np.asarray(freq_hz)
    zr = np.asarray(z_real)
    zi = np.asarray(z_imag)

    R = float(params.get('r'))
    C = float(params.get('c'))

    # elegir el dominio de evaluación (nativo o denso)
    if dense_eval and freq.size > 1:
        # crear rejilla log-espaciada entre min>0 y max
        freq_positive = freq[freq > 0]
        if freq_positive.size == 0:
            freq_eval = freq.copy()
        else:
            fmin = float(np.min(freq_positive))
            fmax = float(np.max(freq))
            freq_eval = np.exp(np.linspace(np.log(max(fmin, 1e-12)), np.log(max(fmax, fmin)), n_points))

        # medir y unwarp/ordenar para interpolación
        sort_idx = np.argsort(freq)
        freq_sorted = freq[sort_idx]
        mag_true_sorted = np.hypot(zr, zi)[sort_idx]
        phase_true_sorted = np.unwrap(np.angle(zr + 1j * zi))[sort_idx]

        # interpolar magnitud y fase en la rejilla densa
        mag_true = np.interp(freq_eval, freq_sorted, mag_true_sorted)
        phase_true = np.interp(freq_eval, freq_sorted, phase_true_sorted)

        # calcular predicción del modelo en la rejilla densa
        if model == 'parallel':
            pred_r_eval, pred_i_eval = parallel_rc_z(freq_eval, R, C)
        elif model == 'series':
            pred_r_eval, pred_i_eval = series_rc_z(freq_eval, R, C)
        else:
            raise ValueError('modelo desconocido: use "parallel" o "series"')

        mag_pred = np.hypot(pred_r_eval, pred_i_eval)
        phase_pred = np.unwrap(np.angle(pred_r_eval + 1j * pred_i_eval))

        # usar arrays densos para las métricas
        mag_true_arr = mag_true
        mag_pred_arr = mag_pred
        phase_true_arr = phase_true
        phase_pred_arr = phase_pred
    else:
        # comportamiento nativo (puntos medidos)
        if model == 'parallel':
            pred_r, pred_i = parallel_rc_z(freq, R, C)
        elif model == 'series':
            pred_r, pred_i = series_rc_z(freq, R, C)
        else:
            raise ValueError('modelo desconocido: use "parallel" o "series"')

        mag_true_arr = np.hypot(zr, zi)
        mag_pred_arr = np.hypot(pred_r, pred_i)
        phase_true_arr = np.unwrap(np.angle(zr + 1j * zi))
        phase_pred_arr = np.unwrap(np.angle(pred_r + 1j * pred_i))

    # magnitud
    r2_mag = _r2_score(mag_true_arr, mag_pred_arr)
    rmse_mag = float(np.sqrt(np.mean((mag_true_arr - mag_pred_arr) ** 2)))
    denom_mag = float(np.mean(np.abs(mag_true_arr)))
    nrmse_mag = rmse_mag / denom_mag if denom_mag != 0 else float('inf')

    # fase (convertir a grados para R² comparativo)
    phase_true_deg = np.degrees(phase_true_arr)
    phase_pred_deg = np.degrees(phase_pred_arr)
    r2_phase = _r2_score(phase_true_deg, phase_pred_deg)
    rmse_phase_rad = float(np.sqrt(np.mean((phase_true_arr - phase_pred_arr) ** 2)))
    rmse_phase_deg = float(np.degrees(rmse_phase_rad))

    # métrica combinada de Bode (media simple de mag & phase R²)
    r2_bode_combined = float((r2_mag + r2_phase) / 2.0)

    return {
        'r2_mag': float(r2_mag),
        'rmse_mag': float(rmse_mag),
        'nrmse_mag': float(nrmse_mag),
        'r2_phase': float(r2_phase),
        'rmse_phase_deg': float(rmse_phase_deg),
        'r2_bode_combined': r2_bode_combined,
    }


def evaluate_nyquist(freq_hz: np.ndarray, z_real: np.ndarray, z_imag: np.ndarray, *, model: str = 'parallel', params: Dict[str, float] = None) -> Dict[str, float]:
    """Calcula métricas para Nyquist (parte real, imaginaria y combinada)."""
    if params is None:
        raise ValueError('params no puede ser None')

    freq = np.asarray(freq_hz)
    zr = np.asarray(z_real)
    zi = np.asarray(z_imag)

    R = float(params.get('r'))
    C = float(params.get('c'))

    if model == 'parallel':
        pred_r, pred_i = parallel_rc_z(freq, R, C)
    elif model == 'series':
        pred_r, pred_i = series_rc_z(freq, R, C)
    else:
        raise ValueError('modelo desconocido: use "parallel" o "series"')

    # métricas por componente
    r2_real = _r2_score(zr, pred_r)
    r2_imag = _r2_score(zi, pred_i)
    # combinado (ya disponible en evaluate_fit)
    combined = evaluate_fit(freq, zr, zi, model=model, params=params)

    rmse_real = float(np.sqrt(np.mean((zr - pred_r) ** 2)))
    rmse_imag = float(np.sqrt(np.mean((zi - pred_i) ** 2)))

    return {
        'r2_real': float(r2_real),
        'r2_imag': float(r2_imag),
        'r2_combined': float(combined.get('r2', 0.0)),
        'rmse_real': float(rmse_real),
        'rmse_imag': float(rmse_imag),
        'rmse_combined': float(combined.get('rmse', 0.0)),
    }


def select_best_model(freq_hz: np.ndarray, z_real: np.ndarray, z_imag: np.ndarray, *,
                      threshold: float = 0.99, max_iter: int = 3, outlier_sigma: float = 3.0, metric: str = 'combined', bode_dense: bool = False) -> Dict[str, object]:
    """Ajusta ambos modelos (parallel/series) y selecciona el mejor según `metric`.

    Parámetros:
      - metric: 'combined' (default, usa evaluate_fit sobre Re+Im),
                'nyquist' (usa evaluate_nyquist r2_combined),
                'bode' (usa evaluate_bode r2_bode_combined; si `bode_dense=True` usa evaluación densa).

    Retorna dict con keys: 'model', 'result', 'metrics', 'selected_metric', 'selected_score', 'passed', ...
    """
    freq = np.asarray(freq_hz)
    zr = np.asarray(z_real)
    zi = np.asarray(z_imag)

    # Fit inicial para ambos modelos
    res_p = fit_parallel_rc(freq, zr, zi)
    metrics_p = evaluate_fit(freq, zr, zi, model='parallel', params=res_p)

    res_s = fit_series_rc(freq, zr, zi)
    metrics_s = evaluate_fit(freq, zr, zi, model='series', params=res_s)

    # calcular el 'score' según la métrica solicitada
    def _score_for(model_name: str, params_obj: dict, freq_arr, zr_arr, zi_arr):
        if metric == 'combined':
            # usar R² combinado (real+imag)
            m = evaluate_fit(freq_arr, zr_arr, zi_arr, model=model_name, params=params_obj)
            return float(m['r2'])
        if metric == 'nyquist':
            m = evaluate_nyquist(freq_arr, zr_arr, zi_arr, model=model_name, params=params_obj)
            return float(m.get('r2_combined', 0.0))
        if metric == 'bode':
            m = evaluate_bode(freq_arr, zr_arr, zi_arr, model=model_name, params=params_obj, dense_eval=bode_dense)
            return float(m.get('r2_bode_combined', 0.0))
        if metric == 'both':
            # score = min(combined_r2, nyquist_r2) -> requiere que AMBAS métricas sean altas
            combined = evaluate_fit(freq_arr, zr_arr, zi_arr, model=model_name, params=params_obj)['r2']
            nyq = evaluate_nyquist(freq_arr, zr_arr, zi_arr, model=model_name, params=params_obj).get('r2_combined', 0.0)
            return float(min(combined, nyq))
        raise ValueError('metric desconocida: use combined|nyquist|bode|both')

    score_p = _score_for('parallel', res_p, freq, zr, zi)
    score_s = _score_for('series', res_s, freq, zr, zi)

    # seleccionar mejor por score
    candidates = [
        ('parallel', res_p, metrics_p, score_p),
        ('series', res_s, metrics_s, score_s),
    ]
    candidates.sort(key=lambda x: x[3], reverse=True)

    best_name, best_res, best_metrics, best_score = candidates[0]

    if best_score >= threshold:
        return {
            'model': best_name,
            'result': best_res,
            'metrics': best_metrics,
            'selected_metric': metric,
            'selected_score': best_score,
            'passed': True,
            'attempts': 0,
            'removed_indices': []
        }

    # Si no alcanza, intentar rechazo iterativo de outliers (basado en norma del residuo por punto)
    removed = []
    freq_work = freq.copy()
    zr_work = zr.copy()
    zi_work = zi.copy()

    for attempt in range(1, max_iter + 1):
        # ajustar modelo que inicialmente fue el mejor
        if best_name == 'parallel':
            cur_res = fit_parallel_rc(freq_work, zr_work, zi_work)
            pred_r, pred_i = parallel_rc_z(freq_work, cur_res['r'], cur_res['c'])
        else:
            cur_res = fit_series_rc(freq_work, zr_work, zi_work)
            pred_r, pred_i = series_rc_z(freq_work, cur_res['r'], cur_res['c'])

        # residuo por punto (norma)
        resid_norm = np.sqrt((zr_work - pred_r) ** 2 + (zi_work - pred_i) ** 2)
        sigma = np.std(resid_norm)
        if sigma == 0 or np.isnan(sigma):
            break

        mask = resid_norm <= outlier_sigma * sigma
        if mask.all():
            # no hay outliers detectados
            break

        # eliminar puntos considerados outliers
        removed_idx = np.where(~mask)[0].tolist()
        removed.extend(removed_idx)

        freq_work = freq_work[mask]
        zr_work = zr_work[mask]
        zi_work = zi_work[mask]

        # re-evaluar y recalcular score
        if best_name == 'parallel':
            cur_res = fit_parallel_rc(freq_work, zr_work, zi_work)
            cur_metrics = evaluate_fit(freq_work, zr_work, zi_work, model='parallel', params=cur_res)
            cur_score = _score_for('parallel', cur_res, freq_work, zr_work, zi_work)
        else:
            cur_res = fit_series_rc(freq_work, zr_work, zi_work)
            cur_metrics = evaluate_fit(freq_work, zr_work, zi_work, model='series', params=cur_res)
            cur_score = _score_for('series', cur_res, freq_work, zr_work, zi_work)

        if cur_score >= threshold:
            return {
                'model': best_name,
                'result': cur_res,
                'metrics': cur_metrics,
                'selected_metric': metric,
                'selected_score': cur_score,
                'passed': True,
                'attempts': attempt,
                'removed_indices': removed,
            }

    # no se alcanzó el umbral
    return {
        'model': best_name,
        'result': best_res,
        'metrics': best_metrics,
        'selected_metric': metric,
        'selected_score': best_score,
        'passed': False,
        'attempts': max_iter,
        'removed_indices': removed,
    }


def find_best_series_subrange(freq_hz: np.ndarray, z_real: np.ndarray, z_imag: np.ndarray, *,
                              min_points: int = 8, r2_threshold: float = 0.99, max_evals: int = 1000, metric: str = 'combined', bode_dense: bool = False) -> Dict[str, object]:
    """Busca un subrango contiguo donde el modelo RC en serie alcance el umbral según `metric`.

    - metric: 'combined' (R² sobre Re+Im), 'nyquist' (r2_combined de Nyquist), 'bode' (r2_bode_combined).
    - Si se especifica 'bode' se puede habilitar `bode_dense=True` para evaluación densa.

    Devuelve dict con keys: 'r','c','cov','r2' (valor de la métrica seleccionada), 'start_idx', 'end_idx', 'freq_range','n_points','success'
    """
    freq = np.asarray(freq_hz)
    zr = np.asarray(z_real)
    zi = np.asarray(z_imag)
    N = len(freq)

    if N < min_points:
        raise ValueError('Pocos puntos para buscar subrango')

    best = {'score': -1.0, 'start_idx': None, 'end_idx': None, 'result': None}

    def _score_for_slice(i0, i1, res_obj):
        # devuelve el valor de la métrica solicitada para el slice [i0:i1]
        if metric == 'combined':
            m = evaluate_fit(freq[i0:i1], zr[i0:i1], zi[i0:i1], model='series', params=res_obj)
            return float(m['r2'])
        if metric == 'nyquist':
            m = evaluate_nyquist(freq[i0:i1], zr[i0:i1], zi[i0:i1], model='series', params=res_obj)
            return float(m.get('r2_combined', 0.0))
        if metric == 'bode':
            m = evaluate_bode(freq[i0:i1], zr[i0:i1], zi[i0:i1], model='series', params=res_obj, dense_eval=bode_dense)
            return float(m.get('r2_bode_combined', 0.0))
        if metric == 'both':
            combined = evaluate_fit(freq[i0:i1], zr[i0:i1], zi[i0:i1], model='series', params=res_obj)['r2']
            nyq = evaluate_nyquist(freq[i0:i1], zr[i0:i1], zi[i0:i1], model='series', params=res_obj).get('r2_combined', 0.0)
            return float(min(combined, nyq))
        raise ValueError('metric desconocida: use combined|nyquist|bode|both')

    # 1) probar segmentos alrededor de plateau (baja-f)
    try:
        plateau = estimate_series_from_plateau(freq, zr, zi)
        n_r = plateau.get('n_points_r', min_points)
        if n_r >= min_points:
            start = 0
            end = min(N, max(min_points, 3 * n_r))
            res = fit_series_rc(freq[start:end], zr[start:end], zi[start:end])
            score = _score_for_slice(start, end, res)
            if score > best['score']:
                best = {'score': score, 'start_idx': start, 'end_idx': end, 'result': res}
                if score >= r2_threshold:
                    return {'r': res['r'], 'c': res['c'], 'cov': res.get('cov'), 'r2': score,
                            'start_idx': start, 'end_idx': end, 'freq_range': (float(freq[start]), float(freq[end-1])),
                            'n_points': end-start, 'success': True}
    except Exception:
        pass

    # 2) probar ventanas en high-f
    try:
        equiv = estimate_series_equivalent(freq, zr, zi)
        high_n = max(min_points, int(0.2 * N))
        start = max(0, N - high_n)
        end = N
        if end - start >= min_points:
            res = fit_series_rc(freq[start:end], zr[start:end], zi[start:end])
            score = _score_for_slice(start, end, res)
            if score > best['score']:
                best = {'score': score, 'start_idx': start, 'end_idx': end, 'result': res}
                if score >= r2_threshold:
                    return {'r': res['r'], 'c': res['c'], 'cov': res.get('cov'), 'r2': score,
                            'start_idx': start, 'end_idx': end, 'freq_range': (float(freq[start]), float(freq[end-1])),
                            'n_points': end-start, 'success': True}
    except Exception:
        pass

    # 3) búsqueda muestreada en percentiles (limitando evals)
    starts = np.linspace(0.0, 0.7, 20)
    ends = np.linspace(0.3, 1.0, 20)
    evals = 0
    for ps in starts:
        for pe in ends:
            if pe <= ps:
                continue
            i0 = int(ps * (N - 1))
            i1 = int(pe * (N - 1)) + 1
            if i1 - i0 < min_points:
                continue
            if evals >= max_evals:
                break
            try:
                res = fit_series_rc(freq[i0:i1], zr[i0:i1], zi[i0:i1])
                score = _score_for_slice(i0, i1, res)
                evals += 1
                if score > best['score']:
                    best = {'score': score, 'start_idx': i0, 'end_idx': i1, 'result': res}
                    if score >= r2_threshold:
                        return {'r': res['r'], 'c': res['c'], 'cov': res.get('cov'), 'r2': score,
                                'start_idx': i0, 'end_idx': i1, 'freq_range': (float(freq[i0]), float(freq[i1-1])),
                                'n_points': i1-i0, 'success': True}
            except Exception:
                continue
        if evals >= max_evals:
            break

    # Si no se alcanzó umbral, devolver el mejor encontrado (reportar 'r2' como el score usado)
    if best['start_idx'] is not None:
        r = best['result']['r']
        c = best['result']['c']
        cov = best['result'].get('cov')
        return {'r': r, 'c': c, 'cov': cov, 'r2': best['score'], 'start_idx': best['start_idx'], 'end_idx': best['end_idx'],
                'freq_range': (float(freq[best['start_idx']]), float(freq[best['end_idx']-1])), 'n_points': best['end_idx'] - best['start_idx'],
                'success': False}

    return {'success': False, 'message': 'No se encontró subrango válido'}
