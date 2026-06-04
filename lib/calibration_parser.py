"""
Helpers para parsear la salida de 'calibrate list'.

El firmware ADMX2001 usa **kHz** en ``calibrate list`` y ``calibrate list <freq>``
(sin sufijo Hz/MHz en el argumento).
"""
import re

INVALID_KEYWORDS = [
    'idn',
    'admx',
    'firmware',
    'hardware',
    'error',
    'command',
    'unknown',
    'invalid',
    'not found',
    'failed'
]

FREQ_MIN_HZ = 0.2
FREQ_MAX_HZ = 10000000


def khz_to_hz(khz):
    return float(khz) * 1000.0


def hz_to_khz(hz):
    return float(hz) / 1000.0


def format_calibrate_list_khz(khz):
    """Token para ``calibrate list <freq>`` (kHz, sin unidad)."""
    khz = float(khz)
    if khz == int(khz):
        return str(int(khz))
    return f"{khz:g}"


def format_freq_label_from_khz(khz):
    """Etiqueta legible a partir del valor en kHz del firmware."""
    try:
        hz = khz_to_hz(khz)
    except (TypeError, ValueError):
        return f"{khz} kHz"
    if hz >= 1e6:
        return f"{hz / 1e6:g} MHz"
    if hz >= 1e3:
        return f"{hz / 1e3:g} kHz"
    return f"{hz:g} Hz"


def khz_in_device_range(khz):
    try:
        hz = khz_to_hz(khz)
    except (TypeError, ValueError):
        return False
    return FREQ_MIN_HZ <= hz <= FREQ_MAX_HZ


def parse_freq_value_to_khz(raw_value):
    """Convierte un valor con unidad opcional a kHz (para calibrate list)."""
    match = re.match(r'^(\d+\.?\d*)\s*(hz|khz|mhz)?$', raw_value.strip(), re.IGNORECASE)
    if not match:
        return None
    value = float(match.group(1))
    unit = (match.group(2) or 'khz').lower()
    if unit == 'hz':
        return value / 1000.0
    if unit == 'mhz':
        return value * 1000.0
    return value


def parse_bare_calibrate_list_khz(raw_line):
    """Número solo en la salida de ``calibrate list`` → kHz."""
    token = raw_line.strip()
    if not re.match(r'^\d+\.?\d*$', token):
        return None
    return float(token)


def extract_calibrate_list_khz_from_line(raw_line):
    """Extrae frecuencia en kHz desde una línea (con o sin unidad explícita)."""
    freq_match = re.search(
        r'(?:freq(?:uency)?)\s*[:=]?\s*(\d+\.?\d*)\s*(hz|khz|mhz)?',
        raw_line,
        re.IGNORECASE,
    )
    if freq_match:
        unit = freq_match.group(2) or 'khz'
        return parse_freq_value_to_khz(f"{freq_match.group(1)} {unit}")

    token_matches = re.findall(r'(\d+\.?\d*)\s*(hz|khz|mhz)?', raw_line, re.IGNORECASE)
    if token_matches:
        value, unit = token_matches[-1]
        if unit:
            return parse_freq_value_to_khz(f"{value} {unit}")
        bare = parse_bare_calibrate_list_khz(value)
        if bare is not None:
            return bare

    return parse_bare_calibrate_list_khz(raw_line)


def format_calibrate_gain_cell(config):
    """Texto de columna Ganancia (Vg/Ig del firmware)."""
    vg = config.get('vg', config.get('ch0', '?'))
    ig = config.get('ig', config.get('ch1', '?'))
    return f"Vg={vg}, Ig={ig}"


def format_calibrate_steps_cell(config):
    """Resumen open/short/load para columna Estado."""
    parts = []
    for step in ('open', 'short', 'load'):
        val = config.get(step)
        if val and val != '?':
            parts.append(f"{step}:{val}")
    return ', '.join(parts) if parts else '—'


def calibrate_config_is_complete(config):
    """True si open, short y load están en Done."""
    return all(
        str(config.get(step, '')).strip().lower() == 'done'
        for step in ('open', 'short', 'load')
    )


# Rango de impedancia asociado a cada par (Vg, Ig) según tabla ADMX2001
_IMPEDANCE_RANGE_BY_GAIN = {
    (3, 0): '< 10 Ω',
    (2, 0): '10–25 Ω',
    (1, 0): '25–100 Ω',
    (0, 0): '100 Ω – 1 kΩ',
    (0, 1): '1–10 kΩ',
    (0, 2): '10–100 kΩ',
    (0, 3): '> 100 kΩ',
}


def impedance_range_label_from_gains(vg, ig):
    """Etiqueta del rango de impedancia para un par Vg/Ig."""
    try:
        key = (int(vg), int(ig))
    except (TypeError, ValueError):
        return None
    return _IMPEDANCE_RANGE_BY_GAIN.get(key)


def format_calibrate_resistance_cell(config):
    """
    Texto para columna Resistencia.

    El firmware no guarda el valor exacto usado en ``calibrate rt``; solo
    expone Vg/Ig. Si hay ``res`` en la respuesta se muestra; si no, el rango
    inferido de la tabla de ganancias.
    """
    res = config.get('res')
    if res not in (None, '', '?'):
        try:
            r_val = float(res)
            if r_val > 0:
                return f"{r_val:g} Ω", f"Resistencia reportada por el firmware: {r_val:g} Ω"
        except (TypeError, ValueError):
            pass

    vg = config.get('vg', config.get('ch0'))
    ig = config.get('ig', config.get('ch1'))
    label = impedance_range_label_from_gains(vg, ig)
    if label:
        return (
            f"~{label}",
            "El firmware no almacena la R exacta del load. "
            f"Vg={vg}, Ig={ig} → rango de impedancia calibrado {label}. "
            "El valor exacto solo se conoce si lo anotaste al ejecutar calibrate rt.",
        )
    return (
        '—',
        "El firmware no devuelve la resistencia de load en calibrate list.",
    )


def _gain_entry_to_config(entry):
    return {
        'vg': entry['vg'],
        'ig': entry['ig'],
        'ch0': entry['vg'],
        'ch1': entry['ig'],
        'open': entry.get('open') or '?',
        'short': entry.get('short') or '?',
        'load': entry.get('load') or '?',
        'res': '?',
        'raw': entry.get('raw', ''),
    }


def parse_calibrate_list_detail_lines(lines, context_freq_khz=None):
    """
    Parsea salida de ``calibrate list <kHz>``::

        Vg =0, Ig =0
        open:Done
        short:Done
        load:Done
    """
    configs = []
    current = None

    for cal_line in lines or []:
        line = cal_line.strip()
        if not line or line.startswith('#'):
            continue
        line_lower = line.lower()
        if line_lower == 'calibrate list' or line_lower.startswith('calibrate list '):
            continue
        if line_looks_like_firmware_error(line):
            continue

        gain_m = re.search(r'Vg\s*=\s*(\d+)\s*,\s*Ig\s*=\s*(\d+)', line, re.I)
        if gain_m:
            if current:
                configs.append(_gain_entry_to_config(current))
            current = {
                'vg': gain_m.group(1),
                'ig': gain_m.group(2),
                'open': None,
                'short': None,
                'load': None,
                'raw': line,
            }
            continue

        step_m = re.match(r'(open|short|load)\s*:\s*(\S+)', line, re.I)
        if step_m and current is not None:
            step = step_m.group(1).lower()
            current[step] = step_m.group(2)
            current['raw'] = f"{current.get('raw', '')}; {line}".strip('; ')
            continue

    if current:
        configs.append(_gain_entry_to_config(current))

    return configs


def format_calibrate_list_for_terminal(lines, context_freq_khz=None):
    """
    Convierte la salida cruda de ``calibrate list`` en líneas legibles para el terminal.
    """
    parsed = parse_calibrate_list_lines(lines, context_freq_khz=context_freq_khz)
    if not parsed:
        return None

    formatted = [
        f"── {len(parsed)} frecuencia(s) con calibración en flash ──"
    ]
    for freq_khz, configs in sorted(
        parsed.items(),
        key=lambda x: float(x[0]) if str(x[0]).replace('.', '', 1).isdigit() else 0,
    ):
        if freq_khz == '?':
            formatted.append("  (entradas sin frecuencia identificada)")
            continue

        f_label = format_freq_label_from_khz(freq_khz)
        cmd_arg = format_calibrate_list_khz(freq_khz)

        if configs and configs[0].get('placeholder'):
            formatted.append(f"  • {f_label} — use: calibrate list {cmd_arg}")
            continue

        formatted.append(f"  • {f_label}:")
        for cfg in configs:
            ch0 = cfg.get('ch0', '?')
            ch1 = cfg.get('ch1', '?')
            res = cfg.get('res', '?')
            formatted.append(f"      CH0={ch0}  CH1={ch1}  R={res}")

    formatted.append("── fin calibrate list ──")
    return formatted


def line_looks_like_firmware_error(line: str) -> bool:
    """True solo si la línea parece un error real del firmware (no 'Not Done')."""
    low = (line or '').lower()
    if re.search(r'\b(error|failed|invalid command|unknown command)\b', low):
        return True
    if low.strip().startswith('error:') or low.strip().startswith('fail:'):
        return True
    return False


def parse_calibrate_commit_args(command: str):
    """
    Parsea ``calibrate commit`` según firmware ADMX2001.

    Formato oficial: ``calibrate commit <unix_ts>`` → PASSWORD> → contraseña.
    También acepta: ``calibrate commit <ts> <password>``.
    """
    parts = (command or '').split()
    password = None
    timestamp = None
    if len(parts) >= 3:
        arg2 = parts[2]
        if len(parts) >= 4:
            timestamp = arg2
            password = parts[3]
        elif arg2.isdigit() or (
            arg2.replace('.', '', 1).isdigit() and arg2.count('.') <= 1
        ):
            timestamp = arg2
        else:
            password = arg2
    return timestamp, password


def _store_config(frequencies_with_configs, freq_khz_key, config, context_freq_khz=None):
    if freq_khz_key is None or freq_khz_key == '?':
        if context_freq_khz is not None and khz_in_device_range(context_freq_khz):
            freq_khz_key = format_calibrate_list_khz(context_freq_khz)
        else:
            freq_khz_key = '?'
    if freq_khz_key not in frequencies_with_configs:
        frequencies_with_configs[freq_khz_key] = []
    frequencies_with_configs[freq_khz_key].append(config)


def parse_calibrate_list_lines(lines, context_freq_khz=None):
    """
    Parsea líneas de ``calibrate list`` y agrupa por frecuencia.

    Las claves del dict son valores en **kHz** (argumento del comando firmware).
    """
    frequencies_with_configs = {}
    if not lines:
        return frequencies_with_configs

    if context_freq_khz is not None:
        try:
            context_freq_khz = float(context_freq_khz)
        except (TypeError, ValueError):
            context_freq_khz = None

    pending_gain = None

    for cal_line in lines:
        try:
            line = cal_line.strip()
            if not line or line.startswith('#'):
                continue

            line_lower = line.lower()
            if line_lower == 'calibrate list' or line_lower.startswith('calibrate list '):
                continue
            if line_looks_like_firmware_error(line):
                continue
            if any(
                junk in line_lower
                for junk in ('*idn', 'admx2001>', 'help ', 'firmware version', 'hardware version')
            ):
                continue

            gain_m = re.search(r'Vg\s*=\s*(\d+)\s*,\s*Ig\s*=\s*(\d+)', line, re.I)
            if gain_m:
                if pending_gain:
                    freq_key = (
                        format_calibrate_list_khz(context_freq_khz)
                        if context_freq_khz is not None
                        else '?'
                    )
                    _store_config(
                        frequencies_with_configs,
                        freq_key,
                        _gain_entry_to_config(pending_gain),
                        context_freq_khz=context_freq_khz,
                    )
                pending_gain = {
                    'vg': gain_m.group(1),
                    'ig': gain_m.group(2),
                    'open': None,
                    'short': None,
                    'load': None,
                    'raw': line,
                }
                continue

            step_m = re.match(r'(open|short|load)\s*:\s*(\S+)', line, re.I)
            if step_m and pending_gain is not None:
                pending_gain[step_m.group(1).lower()] = step_m.group(2)
                pending_gain['raw'] = f"{pending_gain.get('raw', '')}; {line}".strip('; ')
                continue

            parsed_data = {}
            has_equals = '=' in line and not re.search(r'Vg\s*=', line, re.I)

            if has_equals:
                parts = line.split()
                for part in parts:
                    cleaned_part = part.strip().strip(',;')
                    if '=' in cleaned_part:
                        key, value = cleaned_part.split('=', 1)
                        parsed_data[key.upper()] = value.strip().strip(',;')
                    elif ':' in cleaned_part:
                        key, value = cleaned_part.split(':', 1)
                        if key.strip().upper() in ['FREQ', 'FREQUENCY', 'CH0', 'CH1', 'RES', 'RESISTANCE']:
                            parsed_data[key.strip().upper()] = value.strip().strip(',;')

                freq = parsed_data.get('FREQ', parsed_data.get('FREQUENCY', None))
                ch0 = parsed_data.get('CH0', '?')
                ch1 = parsed_data.get('CH1', '?')
                res = parsed_data.get('RES', parsed_data.get('RESISTANCE', '?'))

                freq_khz = None
                if freq:
                    freq_khz = parse_freq_value_to_khz(freq)
                    if freq_khz is None or not khz_in_device_range(freq_khz):
                        continue

                freq_key = format_calibrate_list_khz(freq_khz) if freq_khz is not None else '?'
                _store_config(
                    frequencies_with_configs,
                    freq_key,
                    {'ch0': ch0, 'ch1': ch1, 'res': res, 'raw': line},
                    context_freq_khz=context_freq_khz,
                )
            else:
                if 'ch0' in line_lower or 'ch1' in line_lower:
                    ch0_match = re.search(r'ch0\s*[:=]?\s*(\d+)', line, re.IGNORECASE)
                    ch1_match = re.search(r'ch1\s*[:=]?\s*(\d+)', line, re.IGNORECASE)
                    res_match = re.search(r'(?:res|resistance|rt)\s*[:=]?\s*([\d\.]+)', line, re.IGNORECASE)
                    if ch0_match or ch1_match or res_match:
                        freq_khz = extract_calibrate_list_khz_from_line(line)
                        if freq_khz is not None and khz_in_device_range(freq_khz):
                            freq_key = format_calibrate_list_khz(freq_khz)
                        else:
                            freq_key = '?'

                        _store_config(
                            frequencies_with_configs,
                            freq_key,
                            {
                                'ch0': ch0_match.group(1) if ch0_match else '?',
                                'ch1': ch1_match.group(1) if ch1_match else '?',
                                'res': res_match.group(1) if res_match else '?',
                                'raw': line,
                            },
                            context_freq_khz=context_freq_khz,
                        )
                        continue

                freq_khz = extract_calibrate_list_khz_from_line(line)
                if freq_khz is not None:
                    if not khz_in_device_range(freq_khz):
                        continue

                    freq_key = format_calibrate_list_khz(freq_khz)
                    if freq_key not in frequencies_with_configs:
                        frequencies_with_configs[freq_key] = []
                    if not frequencies_with_configs[freq_key]:
                        frequencies_with_configs[freq_key] = [{'placeholder': True}]
        except Exception:
            continue

    if pending_gain:
        freq_key = (
            format_calibrate_list_khz(context_freq_khz)
            if context_freq_khz is not None
            else '?'
        )
        _store_config(
            frequencies_with_configs,
            freq_key,
            _gain_entry_to_config(pending_gain),
            context_freq_khz=context_freq_khz,
        )

    return frequencies_with_configs
