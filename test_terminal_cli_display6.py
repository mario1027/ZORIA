#!/usr/bin/env python3
"""
Test del flujo del Terminal CLI con display 6 y comando siguiente.
Mide tiempos de respuesta y valida que no se bloquee.
"""

import time
import serial

PORT = "/dev/ttyUSB0"
BAUD = 115200


def read_until_prompt(ser, timeout=5.0):
    """Lee hasta encontrar el prompt ADMX2001> o timeout."""
    start = time.time()
    buffer = ""
    lines = []

    while time.time() - start < timeout:
        if ser.in_waiting:
            chunk = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
            buffer += chunk
            if "ADMX2001>" in buffer:
                break
        else:
            time.sleep(0.05)

    if buffer:
        for line in buffer.split("\n"):
            line = line.strip()
            if line and "ADMX2001>" not in line:
                lines.append(line)

    return lines, buffer


def send_command(ser, command, timeout=5.0):
    """Envia un comando y retorna lineas y tiempo transcurrido."""
    ser.reset_input_buffer()
    start = time.time()
    ser.write((command + "\n").encode("utf-8"))
    ser.flush()
    lines, raw = read_until_prompt(ser, timeout=timeout)
    elapsed = time.time() - start
    return lines, raw, elapsed


def main():
    print("=" * 70)
    print("TEST: display 6 + comando siguiente")
    print("=" * 70)

    ser = serial.Serial(PORT, BAUD, timeout=1, write_timeout=1)
    time.sleep(0.5)

    try:
        # Comando 1: display 6
        print("\n[1] display 6")
        lines, raw, elapsed = send_command(ser, "display 6", timeout=8.0)
        print(f"Tiempo: {elapsed:.2f}s")
        for line in lines:
            print(f"  {line}")

        # Comando 2: stop para evitar streaming residual
        print("\n[2] stop (limpiar streaming)")
        lines, raw, elapsed = send_command(ser, "stop", timeout=3.0)
        print(f"Tiempo: {elapsed:.2f}s")
        for line in lines:
            print(f"  {line}")

        # Comando 3: z inmediatamente
        print("\n[3] z (despues de stop)")
        lines, raw, elapsed = send_command(ser, "z", timeout=8.0)
        print(f"Tiempo: {elapsed:.2f}s")
        for line in lines[:5]:
            print(f"  {line}")
        if len(lines) > 5:
            print(f"  ... ({len(lines) - 5} lineas mas)")

        # Comando 4: calibrate list
        print("\n[4] calibrate list")
        lines, raw, elapsed = send_command(ser, "calibrate list", timeout=30.0)
        print(f"Tiempo: {elapsed:.2f}s")
        if lines:
            for line in lines[:10]:
                print(f"  {line}")
            if len(lines) > 10:
                print(f"  ... ({len(lines) - 10} lineas mas)")
        else:
            print("  (sin lineas)")

        print("\n✅ Test completado")

    finally:
        ser.close()


if __name__ == "__main__":
    main()
