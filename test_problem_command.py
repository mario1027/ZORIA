#!/usr/bin/env python3
"""Test específico del comando problemático"""
import sys
sys.path.insert(0, '/home/mrmontero/Documents/zoria')

import time
import serial.tools.list_ports
from lib.admx2001 import ADMX2001
import logging

logging.basicConfig(level=logging.INFO)

def find_device_port():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if 'ACM' in port.device or 'USB' in port.device:
            return port.device
    return ports[0].device if ports else None

def test_problem_command():
    port = find_device_port()
    device = ADMX2001(port, baudrate=115200, timeout=5)
    
    print("Enviando: sweep_type frequency 100 1000")
    start = time.time()
    try:
        response = device.send_command("sweep_type frequency 100 1000", timeout=5.0)
        elapsed = time.time() - start
        print(f"✅ Respuesta en {elapsed:.3f}s")
        print(f"Líneas: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        device.close()

if __name__ == "__main__":
    test_problem_command()
