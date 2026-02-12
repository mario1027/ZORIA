#!/usr/bin/env python3
"""Test simple para ver timing de comando básico"""
import sys
sys.path.insert(0, '/home/mrmontero/Documents/zoria')

import time
import serial.tools.list_ports
from lib.admx2001 import ADMX2001
import logging

# Configurar logging para ver TODOS los mensajes
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)-8s %(name)s/%(lineno)-4d %(message)s'
)

def find_device_port():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if 'ACM' in port.device or 'USB' in port.device:
            return port.device
    return ports[0].device if ports else None

def test_simple_command():
    port = find_device_port()
    if not port:
        print("❌ No se encontró puerto")
        return 1
    
    print(f"🔌 Conectando a {port}...")
    device = ADMX2001(port, baudrate=115200, timeout=5)
    
    print("\n" + "="*70)
    print("Ejecutando: count 50")
    print("="*70)
    
    start = time.time()
    response = device.send_command("count 50")
    elapsed = time.time() - start
    
    print(f"\n✅ Respuesta recibida en {elapsed:.3f}s")
    print(f"Líneas: {len(response)}")
    for i, line in enumerate(response):
        print(f"  [{i}] {repr(line)}")
    
    device.close()
    return 0

if __name__ == "__main__":
    sys.exit(test_simple_command())
