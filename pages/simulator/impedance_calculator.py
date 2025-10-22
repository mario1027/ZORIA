"""
Calculadora de Impedancia para circuitos RLC
Genera datos para diagramas de Bode y Nyquist

Soporta 11 configuraciones:
- R, L, C (componentes individuales)
- RC, RL, LC (serie y paralelo)
- RLC (serie y paralelo)
"""
import numpy as np

class ImpedanceCalculator:
    """Calcula la impedancia compleja para diferentes configuraciones de circuitos"""
    
    def __init__(self, freq_start=1, freq_end=100000, points=1000):
        """
        Inicializa el calculador con rango de frecuencias
        
        Args:
            freq_start: Frecuencia inicial en Hz
            freq_end: Frecuencia final en Hz
            points: Número de puntos en el rango (log scale)
        """
        self.frequencies = np.logspace(np.log10(freq_start), np.log10(freq_end), points)
        self.omega = 2 * np.pi * self.frequencies
    
    # ============ COMPONENTES INDIVIDUALES ============
    
    def resistor(self, R):
        """Impedancia de resistor puro: Z = R"""
        return np.full_like(self.omega, R, dtype=complex)
    
    def capacitor(self, C):
        """Impedancia de capacitor: Z = 1/(jωC) = -j/(ωC)"""
        if C <= 0:
            raise ValueError("La capacitancia debe ser mayor que 0")
        return 1 / (1j * self.omega * C)
    
    def inductor(self, L):
        """Impedancia de inductor: Z = jωL"""
        if L <= 0:
            raise ValueError("La inductancia debe ser mayor que 0")
        return 1j * self.omega * L
    
    # ============ COMBINACIONES RC ============
    
    def rc_series(self, R, C):
        """
        Impedancia RC en serie
        Z = R + 1/(jωC)
        """
        return R + self.capacitor(C)
    
    def rc_parallel(self, R, C):
        """
        Impedancia RC en paralelo
        Z = R || (1/jωC) = R/(1+jωRC)
        """
        Zc = self.capacitor(C)
        return (R * Zc) / (R + Zc)
    
    # ============ COMBINACIONES RL ============
    
    def rl_series(self, R, L):
        """
        Impedancia RL en serie
        Z = R + jωL
        """
        return R + self.inductor(L)
    
    def rl_parallel(self, R, L):
        """
        Impedancia RL en paralelo
        Z = R || jωL = R(jωL)/(R+jωL)
        """
        Zl = self.inductor(L)
        return (R * Zl) / (R + Zl)
    
    # ============ COMBINACIONES LC ============
    
    def lc_series(self, L, C):
        """
        Impedancia LC en serie
        Z = jωL + 1/(jωC)
        Resonancia en ω₀ = 1/√(LC)
        """
        return self.inductor(L) + self.capacitor(C)
    
    def lc_parallel(self, L, C):
        """
        Impedancia LC en paralelo
        Z = (jωL) || (1/jωC)
        """
        Zl = self.inductor(L)
        Zc = self.capacitor(C)
        return (Zl * Zc) / (Zl + Zc)
    
    # ============ COMBINACIONES RLC ============
    
    def rlc_series(self, R, L, C):
        """
        Impedancia RLC en serie
        Z = R + jωL + 1/(jωC)
        Resonancia en ω₀ = 1/√(LC)
        Factor Q = ω₀L/R = 1/(ω₀RC)
        """
        return R + self.inductor(L) + self.capacitor(C)
    
    def rlc_parallel(self, R, L, C):
        """
        Impedancia RLC en paralelo
        1/Z = 1/R + 1/(jωL) + jωC
        """
        Zl = self.inductor(L)
        Zc = self.capacitor(C)
        # Admitancia total
        Y_total = 1/R + 1/Zl + 1/Zc
        return 1 / Y_total
    
    # ============ DISPATCHER ============
    
    def calculate_impedance(self, circuit_type, **params):
        """
        Calcula la impedancia según el tipo de circuito
        
        Args:
            circuit_type: Tipo de circuito (string)
            **params: Parámetros del circuito (R, L, C)
        
        Returns:
            Array de impedancia compleja
            
        Raises:
            ValueError: Si el tipo de circuito es desconocido o faltan parámetros
        """
        # Extraer parámetros con valores por defecto
        R = params.get('R', 1000)  # 1kΩ default
        L = params.get('L', 0.001)  # 1mH default
        C = params.get('C', 1e-6)   # 1µF default
        
        # Mapa de circuitos a funciones
        circuit_map = {
            # Circuitos ideales
            'R': lambda: self.resistor(R),
            'L': lambda: self.inductor(L),
            'C': lambda: self.capacitor(C),
            'RC_series': lambda: self.rc_series(R, C),
            'RC_parallel': lambda: self.rc_parallel(R, C),
            'RL_series': lambda: self.rl_series(R, L),
            'RL_parallel': lambda: self.rl_parallel(R, L),
            'LC_series': lambda: self.lc_series(L, C),
            'LC_parallel': lambda: self.lc_parallel(L, C),
            'RLC_series': lambda: self.rlc_series(R, L, C),
            'RLC_parallel': lambda: self.rlc_parallel(R, L, C),
            # Circuitos reales con parásitos
            'R_real': lambda: self.resistor_real(R),
            'L_real': lambda: self.inductor_real(L),
            'C_real': lambda: self.capacitor_real(C),
            'RC_series_real': lambda: self.rc_series_real(R, C),
            'RC_parallel_real': lambda: self.rc_parallel_real(R, C),
            'RL_series_real': lambda: self.rl_series_real(R, L),
            'RL_parallel_real': lambda: self.rl_parallel_real(R, L),
            'LC_series_real': lambda: self.lc_series_real(L, C),
            'LC_parallel_real': lambda: self.lc_parallel_real(L, C),
            'RLC_series_real': lambda: self.rlc_series_real(R, L, C),
            'RLC_parallel_real': lambda: self.rlc_parallel_real(R, L, C),
        }
        
        if circuit_type not in circuit_map:
            raise ValueError(f"Tipo de circuito desconocido: {circuit_type}")
        
        try:
            return circuit_map[circuit_type]()
        except Exception as e:
            raise ValueError(f"Error calculando impedancia: {str(e)}")
    
    # ============ CONVERSIÓN A DIAGRAMAS ============
    
    def get_bode_data(self, Z):
        """
        Convierte impedancia compleja a datos de Bode
        
        Args:
            Z: Array de impedancia compleja
        
        Returns:
            dict con frequencies, magnitude_db, phase_deg
        """
        magnitude = np.abs(Z)
        # Evitar log de cero
        magnitude = np.where(magnitude > 1e-10, magnitude, 1e-10)
        magnitude_db = 20 * np.log10(magnitude)
        phase = np.angle(Z, deg=True)
        
        return {
            'frequencies': self.frequencies,
            'magnitude_db': magnitude_db,
            'phase_deg': phase
        }
    
    def get_nyquist_data(self, Z):
        """
        Convierte impedancia compleja a datos de Nyquist
        
        Args:
            Z: Array de impedancia compleja
        
        Returns:
            dict con real, imaginary, frequencies
        """
        return {
            'real': Z.real,
            'imaginary': Z.imag,
            'frequencies': self.frequencies
        }
    
    def get_resonance_frequency(self, L, C):
        """
        Calcula la frecuencia de resonancia para LC
        f₀ = 1/(2π√(LC))
        
        Args:
            L: Inductancia en H
            C: Capacitancia en F
            
        Returns:
            Frecuencia de resonancia en Hz
        """
        if L <= 0 or C <= 0:
            return None
        return 1 / (2 * np.pi * np.sqrt(L * C))
    
    def get_quality_factor(self, R, L, C):
        """
        Calcula el factor de calidad Q para RLC
        Q = (1/R) * √(L/C) para serie
        Q = R * √(C/L) para paralelo
        
        Args:
            R: Resistencia en Ω
            L: Inductancia en H  
            C: Capacitancia en F
            
        Returns:
            Factor de calidad Q
        """
        if L <= 0 or C <= 0 or R <= 0:
            return None
        omega_0 = 1 / np.sqrt(L * C)
        return omega_0 * L / R

    # ============ CIRCUITOS REALES CON PARÁSITOS ============
    
    def resistor_real(self, R, L_parasitic=1e-9, C_parasitic=1e-12):
        """
        Resistor real con inductancia y capacitancia parásitas
        Z = R + jωL_p + 1/(jωC_p) en serie con paralelo de C_p
        """
        Z_L_series = 1j * self.omega * L_parasitic
        Z_C_parallel = 1 / (1j * self.omega * C_parasitic)
        return R + Z_L_series + (R * Z_C_parallel) / (R + Z_C_parallel)
    
    def capacitor_real(self, C, R_esr=0.1, L_esl=1e-9):
        """
        Capacitor real con ESR (resistencia serie) y ESL (inductancia serie)
        Z = R_esr + jωL_esl + 1/(jωC)
        """
        return R_esr + 1j * self.omega * L_esl + 1 / (1j * self.omega * C)
    
    def inductor_real(self, L, R_dc=0.1, C_parasitic=1e-12):
        """
        Inductor real con resistencia DC y capacitancia parásita en paralelo
        Z = (R_dc + jωL) || (1/(jωC_p))
        """
        Z_rl = R_dc + 1j * self.omega * L
        Z_c = 1 / (1j * self.omega * C_parasitic)
        return (Z_rl * Z_c) / (Z_rl + Z_c)
    
    def rc_series_real(self, R, C, R_esr=0.1, L_esl=1e-9, L_r_parasitic=1e-9):
        """
        RC serie real con parásitos
        """
        Z_r_real = R + 1j * self.omega * L_r_parasitic  # Resistor con L parásita
        Z_c_real = R_esr + 1j * self.omega * L_esl + 1 / (1j * self.omega * C)  # Capacitor real
        return Z_r_real + Z_c_real
    
    def rc_parallel_real(self, R, C, R_esr=0.1, L_esl=1e-9, L_r_parasitic=1e-9):
        """
        RC paralelo real con parásitos
        """
        Z_r_real = R + 1j * self.omega * L_r_parasitic
        Z_c_real = R_esr + 1j * self.omega * L_esl + 1 / (1j * self.omega * C)
        return (Z_r_real * Z_c_real) / (Z_r_real + Z_c_real)
    
    def rl_series_real(self, R, L, R_dc=0.1, C_l_parasitic=1e-12, L_r_parasitic=1e-9):
        """
        RL serie real con parásitos
        """
        Z_r_real = R + 1j * self.omega * L_r_parasitic
        Z_l_real = R_dc + 1j * self.omega * L
        Z_l_with_c = (Z_l_real * (1 / (1j * self.omega * C_l_parasitic))) / (Z_l_real + 1 / (1j * self.omega * C_l_parasitic))
        return Z_r_real + Z_l_with_c
    
    def rl_parallel_real(self, R, L, R_dc=0.1, C_l_parasitic=1e-12, L_r_parasitic=1e-9):
        """
        RL paralelo real con parásitos
        """
        Z_r_real = R + 1j * self.omega * L_r_parasitic
        Z_l_real = R_dc + 1j * self.omega * L
        Z_l_with_c = (Z_l_real * (1 / (1j * self.omega * C_l_parasitic))) / (Z_l_real + 1 / (1j * self.omega * C_l_parasitic))
        return (Z_r_real * Z_l_with_c) / (Z_r_real + Z_l_with_c)
    
    def lc_series_real(self, L, C, R_l_dc=0.1, C_l_parasitic=1e-12, R_c_esr=0.1, L_c_esl=1e-9):
        """
        LC serie real con parásitos
        """
        Z_l_real = R_l_dc + 1j * self.omega * L
        Z_l_with_c_par = (Z_l_real * (1 / (1j * self.omega * C_l_parasitic))) / (Z_l_real + 1 / (1j * self.omega * C_l_parasitic))
        Z_c_real = R_c_esr + 1j * self.omega * L_c_esl + 1 / (1j * self.omega * C)
        return Z_l_with_c_par + Z_c_real
    
    def lc_parallel_real(self, L, C, R_l_dc=0.1, C_l_parasitic=1e-12, R_c_esr=0.1, L_c_esl=1e-9):
        """
        LC paralelo real con parásitos
        """
        Z_l_real = R_l_dc + 1j * self.omega * L
        Z_l_with_c_par = (Z_l_real * (1 / (1j * self.omega * C_l_parasitic))) / (Z_l_real + 1 / (1j * self.omega * C_l_parasitic))
        Z_c_real = R_c_esr + 1j * self.omega * L_c_esl + 1 / (1j * self.omega * C)
        return (Z_l_with_c_par * Z_c_real) / (Z_l_with_c_par + Z_c_real)
    
    def rlc_series_real(self, R, L, C, R_l_dc=0.1, C_l_parasitic=1e-12, R_c_esr=0.1, L_c_esl=1e-9, L_r_parasitic=1e-9):
        """
        RLC serie real con todos los parásitos
        """
        Z_r_real = R + 1j * self.omega * L_r_parasitic
        Z_l_real = R_l_dc + 1j * self.omega * L
        Z_l_with_c_par = (Z_l_real * (1 / (1j * self.omega * C_l_parasitic))) / (Z_l_real + 1 / (1j * self.omega * C_l_parasitic))
        Z_c_real = R_c_esr + 1j * self.omega * L_c_esl + 1 / (1j * self.omega * C)
        return Z_r_real + Z_l_with_c_par + Z_c_real
    
    def rlc_parallel_real(self, R, L, C, R_l_dc=0.1, C_l_parasitic=1e-12, R_c_esr=0.1, L_c_esl=1e-9, L_r_parasitic=1e-9):
        """
        RLC paralelo real con todos los parásitos
        """
        Z_r_real = R + 1j * self.omega * L_r_parasitic
        Z_l_real = R_l_dc + 1j * self.omega * L
        Z_l_with_c_par = (Z_l_real * (1 / (1j * self.omega * C_l_parasitic))) / (Z_l_real + 1 / (1j * self.omega * C_l_parasitic))
        Z_c_real = R_c_esr + 1j * self.omega * L_c_esl + 1 / (1j * self.omega * C)
        
        # Paralelo de los tres elementos reales
        Z_inv = 1/Z_r_real + 1/Z_l_with_c_par + 1/Z_c_real
        return 1 / Z_inv


def get_circuit_info():
    """Retorna información sobre los circuitos disponibles"""
    return {
        # ============ CIRCUITOS IDEALES ============
        'R': {
            'name': 'Resistor (R)',
            'params': ['R'],
            'description': 'Resistencia pura - Impedancia constante en todas las frecuencias',
            'formula': 'Z = R',
            'category': 'individual'
        },
        'L': {
            'name': 'Inductor (L)',
            'params': ['L'],
            'description': 'Inductancia pura - Impedancia aumenta con la frecuencia',
            'formula': 'Z = jωL',
            'category': 'individual'
        },
        'C': {
            'name': 'Capacitor (C)',
            'params': ['C'],
            'description': 'Capacitancia pura - Impedancia disminuye con la frecuencia',
            'formula': 'Z = 1/(jωC)',
            'category': 'individual'
        },
        'RC_series': {
            'name': 'RC en Serie',
            'params': ['R', 'C'],
            'description': 'Filtro paso-bajo de primer orden',
            'formula': 'Z = R + 1/(jωC)',
            'category': 'RC'
        },
        'RC_parallel': {
            'name': 'RC en Paralelo',
            'params': ['R', 'C'],
            'description': 'Resistor y capacitor en paralelo',
            'formula': 'Z = R/(1+jωRC)',
            'category': 'RC'
        },
        'RL_series': {
            'name': 'RL en Serie',
            'params': ['R', 'L'],
            'description': 'Filtro paso-alto de primer orden',
            'formula': 'Z = R + jωL',
            'category': 'RL'
        },
        'RL_parallel': {
            'name': 'RL en Paralelo',
            'params': ['R', 'L'],
            'description': 'Resistor e inductor en paralelo',
            'formula': 'Z = R(jωL)/(R+jωL)',
            'category': 'RL'
        },
        'LC_series': {
            'name': 'LC en Serie',
            'params': ['L', 'C'],
            'description': 'Circuito resonante en serie',
            'formula': 'Z = jωL + 1/(jωC)',
            'category': 'LC'
        },
        'LC_parallel': {
            'name': 'LC en Paralelo',
            'params': ['L', 'C'],
            'description': 'Circuito resonante en paralelo (tanque)',
            'formula': 'Z = (jωL)(1/jωC)/(jωL+1/jωC)',
            'category': 'LC'
        },
        'RLC_series': {
            'name': 'RLC en Serie',
            'params': ['R', 'L', 'C'],
            'description': 'Circuito RLC resonante en serie',
            'formula': 'Z = R + jωL + 1/(jωC)',
            'category': 'RLC'
        },
        'RLC_parallel': {
            'name': 'RLC en Paralelo',
            'params': ['R', 'L', 'C'],
            'description': 'Circuito RLC resonante en paralelo',
            'formula': '1/Z = 1/R + 1/(jωL) + jωC',
            'category': 'RLC'
        },
        
        # ============ CIRCUITOS REALES CON PARÁSITOS ============
        'R_real': {
            'name': 'Resistor Real (R)',
            'params': ['R'],
            'description': 'Resistor con inductancia y capacitancia parásitas',
            'formula': 'Z = R + jωLp + efectos de Cp',
            'category': 'individual_real'
        },
        'L_real': {
            'name': 'Inductor Real (L)',
            'params': ['L'],
            'description': 'Inductor con resistencia DC y capacitancia parásita',
            'formula': 'Z = (Rdc + jωL) || (1/(jωCp))',
            'category': 'individual_real'
        },
        'C_real': {
            'name': 'Capacitor Real (C)',
            'params': ['C'],
            'description': 'Capacitor con ESR y ESL (elementos parásitos)',
            'formula': 'Z = ESR + jωESL + 1/(jωC)',
            'category': 'individual_real'
        },
        'RC_series_real': {
            'name': 'RC en Serie Real',
            'params': ['R', 'C'],
            'description': 'RC serie con resistor y capacitor reales (con parásitos)',
            'formula': 'Z = (R + jωLp) + (ESR + jωESL + 1/(jωC))',
            'category': 'RC_real'
        },
        'RC_parallel_real': {
            'name': 'RC en Paralelo Real',
            'params': ['R', 'C'],
            'description': 'RC paralelo con componentes reales y sus parásitos',
            'formula': 'Z = (R + jωLp) || (ESR + jωESL + 1/(jωC))',
            'category': 'RC_real'
        },
        'RL_series_real': {
            'name': 'RL en Serie Real',
            'params': ['R', 'L'],
            'description': 'RL serie con resistor e inductor reales (con parásitos)',
            'formula': 'Z = (R + jωLp) + ((Rdc + jωL) || 1/(jωCp))',
            'category': 'RL_real'
        },
        'RL_parallel_real': {
            'name': 'RL en Paralelo Real',
            'params': ['R', 'L'],
            'description': 'RL paralelo con componentes reales y sus parásitos',
            'formula': 'Z = (R + jωLp) || ((Rdc + jωL) || 1/(jωCp))',
            'category': 'RL_real'
        },
        'LC_series_real': {
            'name': 'LC en Serie Real',
            'params': ['L', 'C'],
            'description': 'LC serie con inductor y capacitor reales (con parásitos)',
            'formula': 'Z = ((Rdc + jωL) || 1/(jωCp)) + (ESR + jωESL + 1/(jωC))',
            'category': 'LC_real'
        },
        'LC_parallel_real': {
            'name': 'LC en Paralelo Real',
            'params': ['L', 'C'],
            'description': 'LC paralelo con componentes reales y todos sus parásitos',
            'formula': 'Z = ((Rdc + jωL) || 1/(jωCp)) || (ESR + jωESL + 1/(jωC))',
            'category': 'LC_real'
        },
        'RLC_series_real': {
            'name': 'RLC en Serie Real',
            'params': ['R', 'L', 'C'],
            'description': 'RLC serie con todos los componentes reales y sus parásitos',
            'formula': 'Z = (R + jωLp) + ((Rdc + jωL) || 1/(jωCp)) + (ESR + jωESL + 1/(jωC))',
            'category': 'RLC_real'
        },
        'RLC_parallel_real': {
            'name': 'RLC en Paralelo Real',
            'params': ['R', 'L', 'C'],
            'description': 'RLC paralelo con todos los componentes reales y sus parásitos',
            'formula': '1/Z = 1/(R + jωLp) + 1/((Rdc + jωL) || 1/(jωCp)) + 1/(ESR + jωESL + 1/(jωC))',
            'category': 'RLC_real'
        }
    }


def get_circuits_by_category():
    """Agrupa los circuitos por categoría"""
    circuits = get_circuit_info()
    categories = {}
    
    for circuit_id, info in circuits.items():
        category = info['category']
        if category not in categories:
            categories[category] = []
        categories[category].append({
            'id': circuit_id,
            'name': info['name'],
            'description': info['description']
        })
    
    return categories