"""
Helpers para parsear la salida de 'calibrate list'.
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


def parse_freq_value(raw_value):
    """Convierte un valor de frecuencia con unidad opcional a Hz."""
    match = re.match(r'^(\d+\.?\d*)\s*(hz|khz|mhz)?$', raw_value.strip(), re.IGNORECASE)
    if not match:
        return None
    value = float(match.group(1))
    unit = match.group(2) or 'hz'
    if unit.lower() == 'khz':
        value *= 1000
    elif unit.lower() == 'mhz':
        value *= 1000000
    return value


def extract_frequency_from_line(raw_line):
    """Extrae una frecuencia desde una linea flexible (Hz/kHz/MHz)."""
    freq_match = re.search(
        r'(?:freq(?:uency)?)\s*[:=]?\s*(\d+\.?\d*)\s*(hz|khz|mhz)?',
        raw_line,
        re.IGNORECASE
    )
    if freq_match:
        return parse_freq_value(f"{freq_match.group(1)} {freq_match.group(2) or ''}")

    token_matches = re.findall(r'(\d+\.?\d*)\s*(hz|khz|mhz)?', raw_line, re.IGNORECASE)
    if token_matches:
        value, unit = token_matches[-1]
        return parse_freq_value(f"{value} {unit or ''}")

    return None


def parse_calibrate_list_lines(lines):
    """Parsea lineas de 'calibrate list' y agrupa por frecuencia."""
    frequencies_with_configs = {}
    if not lines:
        return frequencies_with_configs

    for cal_line in lines:
        try:
            line = cal_line.strip()
            if not line or line.startswith('#'):
                continue

            line_lower = line.lower()
            if line_lower == 'calibrate list' or line_lower.startswith('calibrate list '):
                continue
            if any(keyword in line_lower for keyword in INVALID_KEYWORDS):
                continue

            parsed_data = {}
            has_equals = '=' in line

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

                freq_value = None
                if freq:
                    freq_value = parse_freq_value(freq)
                    if freq_value is None:
                        continue
                    if freq_value < FREQ_MIN_HZ or freq_value > FREQ_MAX_HZ:
                        continue

                if freq and freq_value is not None:
                    freq_key = str(int(freq_value))
                    if freq_key not in frequencies_with_configs:
                        frequencies_with_configs[freq_key] = []
                    frequencies_with_configs[freq_key].append({
                        'ch0': ch0,
                        'ch1': ch1,
                        'res': res,
                        'raw': line
                    })
                else:
                    if '?' not in frequencies_with_configs:
                        frequencies_with_configs['?'] = []
                    frequencies_with_configs['?'].append({
                        'ch0': ch0,
                        'ch1': ch1,
                        'res': res,
                        'raw': line
                    })
            else:
                if 'ch0' in line_lower or 'ch1' in line_lower:
                    ch0_match = re.search(r'ch0\s*[:=]?\s*(\d+)', line, re.IGNORECASE)
                    ch1_match = re.search(r'ch1\s*[:=]?\s*(\d+)', line, re.IGNORECASE)
                    res_match = re.search(r'(?:res|resistance|rt)\s*[:=]?\s*([\d\.]+)', line, re.IGNORECASE)
                    if ch0_match or ch1_match or res_match:
                        freq_value = extract_frequency_from_line(line)
                        if freq_value is not None and FREQ_MIN_HZ <= freq_value <= FREQ_MAX_HZ:
                            freq_key = str(int(freq_value))
                            if freq_key not in frequencies_with_configs:
                                frequencies_with_configs[freq_key] = []
                            target_key = freq_key
                        else:
                            if '?' not in frequencies_with_configs:
                                frequencies_with_configs['?'] = []
                            target_key = '?'

                        frequencies_with_configs[target_key].append({
                            'ch0': ch0_match.group(1) if ch0_match else '?',
                            'ch1': ch1_match.group(1) if ch1_match else '?',
                            'res': res_match.group(1) if res_match else '?',
                            'raw': line
                        })
                        continue

                freq_value = extract_frequency_from_line(line)
                if freq_value is not None:
                    if freq_value < FREQ_MIN_HZ or freq_value > FREQ_MAX_HZ:
                        continue

                    freq_str = str(int(freq_value))
                    if freq_str not in frequencies_with_configs:
                        frequencies_with_configs[freq_str] = []
                    if not frequencies_with_configs[freq_str]:
                        frequencies_with_configs[freq_str] = [{'placeholder': True}]
        except Exception:
            continue

    return frequencies_with_configs
