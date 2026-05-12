#!/usr/bin/env python3
"""
Verifica el estado de device_state
"""
import sys
sys.path.insert(0, '/home/mrmontero/Documents/zoria')

from lib.device_state import device_state

print("="*70)
print("ESTADO DE device_state")
print("="*70)
print(f"\nis_connected: {device_state.is_connected}")
print(f"device: {device_state.device}")

if device_state.device:
    print(f"puerto: {device_state.device.port}")
else:
    print("\n device_state NO está conectado")
    print("\nPara que la página web funcione debes:")
    print("  1. Iniciar app.py (python app.py)")
    print("  2. Abrir http://localhost:8050")
    print("  3. Ir al Dashboard")
    print("  4. Hacer clic en 'Conectar'")
    print("  5. LUEGO ir a página Calibración")
    print("\nSin esos pasos, device_state.device será None")
    print("y la tabla mostrará 'Dispositivo no conectado'")
