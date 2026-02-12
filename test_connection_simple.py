#!/usr/bin/env python3
"""
Test simple de conexión USB al ADMX2001
"""
import serial
import time
import sys

def test_connection():
    """Prueba básica de conexión"""
    
    print("\n" + "="*60)
    print("TEST DE CONEXIÓN USB - ADMX2001")
    print("="*60 + "\n")
    
    # Buscar puertos disponibles
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("❌ No se encontraron puertos USB")
        print("   Verifica que el dispositivo esté conectado")
        return
    
    print(f"✓ Puertos disponibles: {len(ports)}")
    for port in ports:
        print(f"  • {port.device} - {port.description}")
    
    # Buscar puerto USB (ttyUSB* primero)
    usb_ports = [p for p in ports if 'ttyUSB' in p.device or 'USB' in p.description]
    
    if not usb_ports:
        print("\n⚠️  No se encontraron puertos USB (ttyUSB*)")
        print("   El dispositivo puede no estar conectado o reconocido")
        return
    
    # Intentar conectar al primer puerto USB
    port = usb_ports[0].device
    print(f"\n📡 Intentando conectar a {port} ({usb_ports[0].description})...")
    
    try:
        # Abrir puerto serial
        ser = serial.Serial(
            port=port,
            baudrate=230400,
            timeout=2.0,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
        
        print(f"✓ Puerto {port} abierto")
        
        # Limpiar buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        time.sleep(0.2)
        
        # Enviar Enter
        print("📤 Enviando Enter...")
        ser.write(b'\n')
        ser.flush()
        time.sleep(0.5)
        
        # Leer respuesta
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            print(f"📥 Respuesta: {repr(response[:200])}")
            
            if 'ADMX2001>' in response:
                print("\n✅ ¡CONEXIÓN EXITOSA! Prompt detectado")
            else:
                print("\n⚠️  Respuesta recibida pero sin prompt")
        else:
            print("⚠️  Sin respuesta al Enter")
        
        # Probar comando *idn
        print("\n📤 Enviando *idn...")
        ser.write(b'*idn\n')
        ser.flush()
        time.sleep(0.5)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            print(f"📥 Respuesta *idn:")
            for line in response.split('\n'):
                line = line.strip()
                if line:
                    print(f"   {line}")
            
            if 'Analog Devices' in response or 'ADMX2001>' in response:
                print("\n✅ ¡DISPOSITIVO IDENTIFICADO CORRECTAMENTE!")
            else:
                print("\n⚠️  Respuesta inesperada")
        else:
            print("❌ Sin respuesta a *idn")
        
        # Cerrar puerto
        ser.close()
        print("\n✓ Puerto cerrado")
        
    except serial.SerialException as e:
        print(f"\n❌ Error de conexión serial:")
        print(f"   {e}")
        print("\n💡 Soluciones posibles:")
        print("   1. Verifica que no hay otra aplicación usando el puerto")
        print("      sudo lsof /dev/ttyUSB0")
        print("   2. Verifica permisos del usuario")
        print("      sudo usermod -a -G dialout $USER")
        print("      (luego cerrar sesión y volver a entrar)")
        print("   3. Reconnecta el cable USB")
        
    except Exception as e:
        print(f"\n❌ Error inesperado:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_connection()
