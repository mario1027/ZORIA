#!/usr/bin/env python3
"""Test detallado de configure_sweep con timing de cada comando"""
import sys
sys.path.insert(0, '/home/mrmontero/Documents/zoria')

import time
import serial.tools.list_ports
from lib.admx2001 import ADMX2001
from lib.enums import SweepType, SweepScale

def find_device_port():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if 'ACM' in port.device or 'USB' in port.device:
            return port.device
    return ports[0].device if ports else None

def test_configure_sweep_detailed():
    port = find_device_port()
    if not port:
        print("❌ No se encontró puerto")
        return 1
    
    print(f"🔌 Conectando...")
    device = ADMX2001(port, baudrate=115200, timeout=5)
    
    print("\nEjecutando configure_sweep() con timing detallado:")
    print("="*70)
    
    total_start = time.time()
    
    # Simular lo que hace configure_sweep
    print("\n1. abort...")
    t1 = time.time()
    try:
        device.send_command("abort", expect_prompt=True)
    except:
        pass
    print(f"   ⏱️  {time.time() - t1:.3f}s")
    
    print("\n2. count 50...")
    t2 = time.time()
    device.send_command("count 50")
    print(f"   ⏱️  {time.time() - t2:.3f}s")
    
    print("\n3. sweep_type frequency 100 1000...")
    t3 = time.time()
    device.send_command("sweep_type frequency 100 1000")
    print(f"   ⏱️  {time.time() - t3:.3f}s")
    
    print("\n4. sweep_scale log...")
    t4 = time.time()
    device.send_command("sweep_scale log")
    print(f"   ⏱️  {time.time() - t4:.3f}s")
    
    total = time.time() - total_start
    
    print("\n" + "="*70)
    print(f"TOTAL: {total:.3f}s")
    print("="*70)
    
    device.close()
    return 0

if __name__ == "__main__":
    sys.exit(test_configure_sweep_detailed())
