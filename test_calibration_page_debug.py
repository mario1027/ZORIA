#!/usr/bin/env python3
"""
Test de debug para calibrations page
Inicia el dashboard con logs detallados
"""
import sys
import os

# Asegurar que el logging esté al máximo
os.environ['DASH_DEBUG'] = 'true'

# Ejecutar app
print("="*70)
print("DASHBOARD CON DEBUG DETALLADO")
print("="*70)
print("\n1. Conecta el dispositivo desde Dashboard")
print("2. Ve a la página 'Calibración'")
print("3. Haz clic en el botón 'Actualizar' (refresh)")
print("4. Mira los logs que aparecen aquí en la terminal")
print("\nLos logs mostrarán:")
print("  - Líneas crudas recibidas de 'calibrate list'")
print("  - Resultado del parseo")
print("  - Filas generadas para la tabla")
print("\n" + "="*70 + "\n")

# Importar y ejecutar
from app import app

if __name__ == '__main__':
    app.run_server(debug=True, port=8050, host='0.0.0.0')
