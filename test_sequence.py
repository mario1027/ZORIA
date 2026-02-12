#!/usr/bin/env python3
"""Test simple de secuencia"""
import sys
sys.path.insert(0, '/home/mrmontero/Documents/zoria')

import time
import serial.tools.list_ports
from lib.admx2001 import ADMX2001

def find_device_port():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if 'ACM' in port.device or 'USB' in port.device:
            return port.device
    return ports[0].device if ports else None

def test_sequence():
    port = find_device_port()
    device = ADMX2001(port, baudrate=115200, timeout=5)
    
    print("1. count 50")
    device.send_command("count 50", timeout=5.0)
    print("   ✅")
    
    print("2. sweep_type frequency 100 1000  (CON TIMEOUT 5s)")
    start = time.time()
    try:
        device.send_command("sweep_type frequency 100 1000", timeout=5.0)
        print(f"   ✅ {time.time()-start:.3f}s")
    except Exception as e:
        print(f"   ❌ TIMEOUT/ERROR: {e}")
    
    device.close()

if __name__ == "__main__":
    test_sequence()
