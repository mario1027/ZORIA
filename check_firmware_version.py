#!/usr/bin/env python3
"""
Verificar versión de firmware
"""

import serial
import time

port = '/dev/ttyUSB0'
ser = serial.Serial(port, 115200, timeout=5.0)
time.sleep(1)

print("Verificando versión de firmware...")
ser.write(b'*idn\n')
ser.flush()
time.sleep(1)

while ser.in_waiting > 0:
    line = ser.readline().decode('utf-8', errors='ignore').strip()
    if line and not line.startswith('ADMX2001>'):
        print(f"  {line}")

ser.close()
