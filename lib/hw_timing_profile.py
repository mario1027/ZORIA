"""
Perfil de tiempos reales del hardware ADMX2001.

En lugar de estimar tiempos teóricamente, este módulo almacena los tiempos
MEDIDOS durante barridos reales. Esto permite que el sistema aprenda los
tiempos reales del hardware conectado y los use para:

  - Calcular timeouts de segmento más precisos (sin margen teórico extra).
  - Mostrar estimaciones de duración del barrido más fiables al usuario.
  - Detectar anomalías (punto que tardar mucho más de lo habitual).

Funcionamiento:
  1. Durante un barrido real, perform_sweep() registra timestamps por punto.
  2. Los intervalos inter-punto se guardan aquí via record().
  3. Al estimar el tiempo de un nuevo barrido, get_ms(freq) devuelve el
     tiempo medido (mediana) interpolado logarítmicamente, o la fórmula
     teórica si aún no hay datos para esa región de frecuencia.
  4. Los datos persisten en hw_timing_profile.json en el directorio raíz.

Política de actualización:
  - Se guardan las últimas 20 mediciones por cada frecuencia.
  - Se usa la mediana para robustez frente a outliers.
  - Una nueva medición actualiza el perfil y guarda el archivo.
"""

import json
import math
import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Directorio raíz del proyecto (un nivel arriba de lib/)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PROFILE_PATH = os.path.join(_PROJECT_ROOT, 'hw_timing_profile.json')

# Máximo de muestras a mantener por frecuencia
_MAX_SAMPLES_PER_FREQ = 20


def _theoretical_ms(freq_hz: float, average: int = 1) -> float:
    """Fórmula teórica de respaldo cuando no hay datos medidos."""
    from .utils import _acquisition_time_ms
    return _acquisition_time_ms(freq_hz, average)


def _log_interpolate(f: float, f_lo: float, f_hi: float,
                     t_lo: float, t_hi: float) -> float:
    """Interpolación log-log entre dos puntos de frecuencia."""
    if f_lo <= 0 or f_hi <= 0 or t_lo <= 0 or t_hi <= 0:
        return t_lo
    alpha = (math.log10(f) - math.log10(f_lo)) / (math.log10(f_hi) - math.log10(f_lo))
    log_t = math.log10(t_lo) + alpha * (math.log10(t_hi) - math.log10(t_lo))
    return pow(10, log_t)


def _median(values: List[float]) -> float:
    s = sorted(values)
    n = len(s)
    if n == 0:
        return 0.0
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2.0


class HardwareTimingProfile:
    """
    Almacena y recupera tiempos de medición reales del ADMX2001.

    Uso típico:
        profile = HardwareTimingProfile()
        profile.record(freq_hz=100.0, elapsed_ms=312.0)
        ms = profile.get_ms(100.0)   # → tiempo real medido
        profile.save()
    """

    def __init__(self, path: str = None):
        """
        Args:
            path: Ruta al archivo JSON de perfil. Si None, usa el default.
        """
        self.path = path or DEFAULT_PROFILE_PATH
        # Dict: float(freq_hz) → List[float] (lista de ms medidos)
        self._data: Dict[float, List[float]] = {}
        self.load()

    # ------------------------------------------------------------------
    # Persistencia
    # ------------------------------------------------------------------

    def load(self) -> None:
        """Carga el perfil desde disco (no lanza excepción si no existe)."""
        try:
            if os.path.exists(self.path):
                with open(self.path, 'r') as f:
                    raw = json.load(f)
                self._data = {float(k): list(v) for k, v in raw.items()}
                logger.debug(
                    f"Perfil de timing HW cargado: {len(self._data)} frecuencias "
                    f"de {self.path}"
                )
        except Exception as e:
            logger.warning(f"No se pudo cargar perfil de timing HW: {e}")
            self._data = {}

    def save(self) -> None:
        """Guarda el perfil a disco."""
        try:
            with open(self.path, 'w') as f:
                json.dump(
                    {str(k): v for k, v in sorted(self._data.items())},
                    f, indent=2
                )
            logger.debug(f"Perfil de timing HW guardado: {self.path}")
        except Exception as e:
            logger.warning(f"No se pudo guardar perfil de timing HW: {e}")

    # ------------------------------------------------------------------
    # Registro de mediciones reales
    # ------------------------------------------------------------------

    def record(self, freq_hz: float, elapsed_ms: float) -> None:
        """
        Registra un tiempo medido real para una frecuencia.

        Filtra outliers obvios (< 5 ms o > 10 min) antes de guardar.

        Args:
            freq_hz:    Frecuencia de excitación en Hz
            elapsed_ms: Tiempo real transcurrido en ms (inter-punto)
        """
        if elapsed_ms < 5.0 or elapsed_ms > 600_000:
            # Sanity check: ignorar mediciones imposibles
            return
        if freq_hz <= 0:
            return

        # Redondear frecuencia a 6 cifras para agrupar puntos cercanos
        key = round(float(freq_hz), 4)

        if key not in self._data:
            self._data[key] = []

        self._data[key].append(float(elapsed_ms))

        # Mantener solo las últimas N muestras
        if len(self._data[key]) > _MAX_SAMPLES_PER_FREQ:
            self._data[key] = self._data[key][-_MAX_SAMPLES_PER_FREQ:]

    def update_from_sweep(
        self,
        sweep_results: list,
        point_timestamps: list
    ) -> int:
        """
        Actualiza el perfil usando los timestamps reales de un barrido completo.

        Los intervalos entre timestamps consecutivos son el tiempo real que
        tardó el hardware en completar cada medición en esa frecuencia.

        Args:
            sweep_results:     Lista de {'sweep_value': freq_hz, ...}
            point_timestamps:  Lista de time.time() cuando llegó cada punto

        Returns:
            Número de puntos registrados correctamente
        """
        n = min(len(sweep_results), len(point_timestamps))
        if n < 2:
            return 0

        recorded = 0
        for i in range(1, n):
            dt_ms = (point_timestamps[i] - point_timestamps[i - 1]) * 1000.0
            # dt_ms ≈ tiempo de medición del punto i-1 en esa frecuencia
            freq = sweep_results[i - 1].get('sweep_value', 0)
            if freq and freq > 0:
                self.record(float(freq), dt_ms)
                recorded += 1

        logger.info(
            f"Perfil HW actualizado: {recorded} puntos de timing registrados"
        )
        self.save()
        return recorded

    # ------------------------------------------------------------------
    # Consulta de tiempos
    # ------------------------------------------------------------------

    def get_ms(self, freq_hz: float, average: int = 1) -> float:
        """
        Devuelve el mejor estimado del tiempo de medición en ms para freq_hz.

        Prioridad:
        1. Datos medidos directos (tolerancia ±20 % en log)
        2. Interpolación log-log entre dos puntos medidos adyacentes
        3. Fórmula teórica de respaldo (36 ciclos + piso 15 ms)

        Args:
            freq_hz: Frecuencia en Hz
            average: Número de promedios (multiplica tiempo linealmente)

        Returns:
            Tiempo estimado en ms (incluyendo overhead de comunicación)
        """
        if not self._data:
            return _theoretical_ms(freq_hz, average)

        sorted_freqs = sorted(self._data.keys())

        # 1. Búsqueda directa con tolerancia logarítmica del 20 %
        for f in sorted_freqs:
            if f <= 0:
                continue
            ratio = freq_hz / f if f < freq_hz else f / freq_hz
            if ratio <= 1.2:
                t = _median(self._data[f])
                return t * max(1, average)

        # 2. Interpolación log-log entre los dos vecinos más cercanos
        lo_f: Optional[float] = None
        hi_f: Optional[float] = None
        for f in sorted_freqs:
            if f <= freq_hz:
                lo_f = f
            if f >= freq_hz and hi_f is None:
                hi_f = f

        if lo_f is not None and hi_f is not None and lo_f != hi_f:
            t_lo = _median(self._data[lo_f])
            t_hi = _median(self._data[hi_f])
            t = _log_interpolate(freq_hz, lo_f, hi_f, t_lo, t_hi)
            return t * max(1, average)

        # 3. Extrapolación / fallback
        if lo_f is not None and hi_f is None:
            # Por encima del rango medido → usar el punto más alto medido
            # (zona de piso, 15 ms — la extrapolación es segura)
            return _median(self._data[lo_f]) * max(1, average)

        # Por debajo del rango medido ó sin vecinos útiles:
        # Los ciclos DFT dominan a baja frecuencia → usar fórmula teórica.
        # El punto medido más cercano (en frecuencias más altas) NO puede
        # extrapolarse hacia abajo: 1 Hz ≠ 10 Hz en tiempo DFT.
        return _theoretical_ms(freq_hz, average)

    def has_data_for(self, freq_start: float, freq_end: float) -> bool:
        """
        Devuelve True si hay datos medidos que cubran el rango [freq_start, freq_end].
        Útil para decidir si usar el perfil o la fórmula teórica.
        """
        if not self._data:
            return False
        freqs = sorted(self._data.keys())
        measured_min = freqs[0]
        measured_max = freqs[-1]
        return measured_min <= freq_start * 2 and measured_max >= freq_end / 2

    def summary(self) -> str:
        """Resumen del perfil para logging/debug."""
        if not self._data:
            return "Perfil vacío (sin mediciones reales)"
        freqs = sorted(self._data.keys())
        counts = [len(self._data[f]) for f in freqs]
        return (
            f"Perfil HW: {len(freqs)} frecuencias, "
            f"{sum(counts)} mediciones totales, "
            f"rango {freqs[0]:.3g}–{freqs[-1]:.3g} Hz"
        )


# ---------------------------------------------------------------------------
# Instancia global (singleton) para uso en toda la aplicación
# ---------------------------------------------------------------------------
_global_profile: Optional[HardwareTimingProfile] = None


def get_profile() -> HardwareTimingProfile:
    """Devuelve la instancia global del perfil de timing de hardware."""
    global _global_profile
    if _global_profile is None:
        _global_profile = HardwareTimingProfile()
    return _global_profile
