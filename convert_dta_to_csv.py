"""
Convierte archivos .DTA (formato Gamry Instruments) al formato CSV de ZORIA.

Formato .DTA:
- Tab-delimited, coma como separador decimal
- Sección ZCURVE TABLE con columnas: Pt, Time, Freq, Zreal, Zimag, Zsig, Zmod, Zphz, ...
- Zphz está en grados

Formato ZORIA .csv:
- Comma-delimited, punto decimal
- Columnas: frequency_hz, z_real_ohm, z_imag_ohm, z_magnitude_ohm, phase_rad, phase_deg
"""

import os
import re
import csv
import math
import sys

DATA_DIR = 'data'


def parse_euro_number(s: str) -> float:
    """Convierte '985,834' o '-11,45652' a float."""
    return float(s.strip().replace(',', '.'))


def find_zcurve_lines(filepath: str):
    """Encuentra las líneas de datos de la sección ZCURVE TABLE."""
    with open(filepath, 'r', encoding='latin-1') as f:
        lines = f.readlines()

    in_zcurve = False
    header_line = None
    data_start = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('ZCURVE'):
            in_zcurve = True
            continue
        if in_zcurve:
            # Saltar línea de encabezados de columna y de unidades
            if stripped.startswith('Pt') or stripped.startswith('#'):
                continue
            if stripped == '' or stripped.startswith('EOC') or stripped.startswith('XCURVE'):
                break
            # Es una línea de datos
            columns = line.strip().split('\t')
            if len(columns) >= 8:
                yield columns
            else:
                break


def convert_dta_to_csv(dta_path: str) -> str | None:
    """Convierte un archivo .DTA a .csv ZORIA. Retorna el path del CSV creado o None."""
    basename = os.path.splitext(os.path.basename(dta_path))[0]
    csv_filename = basename + '.csv'
    csv_path = os.path.join(DATA_DIR, csv_filename)

    rows = []
    for cols in find_zcurve_lines(dta_path):
        try:
            freq = parse_euro_number(cols[2])       # Freq (Hz)
            zreal = parse_euro_number(cols[3])       # Zreal (ohm)
            zimag = parse_euro_number(cols[4])       # Zimag (ohm)
            zmag = parse_euro_number(cols[6])        # Zmod (ohm)
            phase_deg = parse_euro_number(cols[7])   # Zphz (grados)
            phase_rad = math.radians(phase_deg)
            rows.append((freq, zreal, zimag, zmag, phase_rad, phase_deg))
        except (ValueError, IndexError) as e:
            print(f"  [!] Error parseando línea: {cols} → {e}", file=sys.stderr)

    if not rows:
        print(f"  [X] No se encontraron datos ZCURVE en {dta_path}", file=sys.stderr)
        return None

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['frequency_hz', 'z_real_ohm', 'z_imag_ohm',
                         'z_magnitude_ohm', 'phase_rad', 'phase_deg'])
        for row in rows:
            writer.writerow(row)

    print(f"  [OK] {len(rows)} puntos → {csv_path}")
    return csv_path


def main():
    print("=== Conversor .DTA → .csv ZORIA ===\n")

    dta_files = sorted([
        os.path.join(DATA_DIR, f)
        for f in os.listdir(DATA_DIR)
        if f.upper().endswith('.DTA')
    ])

    if not dta_files:
        print("No se encontraron archivos .DTA en data/")
        return

    converted = []
    for dta_path in dta_files:
        print(f"Procesando: {dta_path}")
        result = convert_dta_to_csv(dta_path)
        if result:
            converted.append(result)

    print(f"\n{'='*50}")
    print(f"Convertidos {len(converted)} de {len(dta_files)} archivos.")


if __name__ == '__main__':
    main()
