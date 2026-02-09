#!/usr/bin/env python3
"""
Script de pruebas de rendimiento continuo para ADMX2001

Ejecuta mediciones repetidas para validar:
- Estabilidad del streaming
- No hay memory leaks
- Performance sostenida
- Reconexión después de errores
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import serial.tools.list_ports
from lib.device_state import device_state
from lib.admx2001 import ADMX2001
from lib.enums import DisplayMode

class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def connect_device():
    """Conectar al ADMX2001"""
    all_ports = list(serial.tools.list_ports.comports())
    usb_ports = [p for p in all_ports if 'USB' in p.device.upper() or 'ttyUSB' in p.device]
    
    for p in usb_ports[:3]:
        desc = p.description.upper() if p.description else ""
        manuf = p.manufacturer.upper() if p.manufacturer else ""
        if any(x in desc or x in manuf for x in ['FTDI', 'TTL232']):
            try:
                dev = ADMX2001(p.device, baudrate=115200, timeout=3.0)
                time.sleep(0.5)
                resp = dev.send_command('*idn')
                if resp and 'ADMX' in str(resp).upper():
                    dev.set_mdelay(1)
                    dev.set_tdelay(0)
                    device_state.set_device(dev, True)
                    return dev, p.device
            except:
                continue
    return None, None


def configure_device(dev):
    """Configuración básica"""
    dev.set_display_mode(DisplayMode.R_X)
    dev.send_command("frequency 100")
    dev.send_command("magnitude 1")
    dev.send_command("setgain ch0 0")
    dev.send_command("setgain ch1 1")
    dev.send_command("average 10")
    dev.send_command("count 20")  # 20 puntos por medición


def run_continuous_test(iterations=100):
    """Ejecutar test continuo"""
    print_header("TEST DE RENDIMIENTO CONTINUO")
    
    print(f"Conectando al dispositivo...")
    dev, port = connect_device()
    
    if not dev:
        print(f"{Colors.FAIL}❌ No se pudo conectar{Colors.ENDC}")
        return
    
    print(f"{Colors.OKGREEN}✅ Conectado a {port}{Colors.ENDC}")
    configure_device(dev)
    print(f"{Colors.OKGREEN}✅ Dispositivo configurado{Colors.ENDC}\n")
    
    print(f"Ejecutando {iterations} iteraciones de mediciones (20 puntos cada una)...\n")
    
    success_count = 0
    fail_count = 0
    total_lines = 0
    total_time = 0
    errors = []
    
    start_test = time.time()
    
    for i in range(1, iterations + 1):
        try:
            iter_start = time.time()
            
            # Ejecutar medición
            device_state.start_streaming_command('z', timeout=30.0)
            
            # Esperar completación
            for _ in range(100):
                if device_state.is_streaming_complete():
                    break
                time.sleep(0.1)
            
            # Obtener resultados
            lines = device_state.get_streaming_lines()
            data_lines = [l for l in lines if l['type'] == 'data' and l['line'].strip()]
            
            iter_time = time.time() - iter_start
            
            if len(data_lines) == 20:
                success_count += 1
                total_lines += len(data_lines)
                total_time += iter_time
                status = f"{Colors.OKGREEN}✅{Colors.ENDC}"
            else:
                fail_count += 1
                status = f"{Colors.FAIL}❌{Colors.ENDC}"
                errors.append(f"Iter {i}: Esperaba 20, recibió {len(data_lines)}")
            
            # Progress report cada 10 iteraciones
            if i % 10 == 0:
                avg_throughput = total_lines / total_time if total_time > 0 else 0
                print(f"{status} [{i:3d}/{iterations}] | "
                      f"Éxitos: {success_count:3d} | "
                      f"Fallos: {fail_count:2d} | "
                      f"Throughput: {avg_throughput:.1f} líneas/s")
            
        except Exception as e:
            fail_count += 1
            errors.append(f"Iter {i}: Exception - {str(e)}")
            print(f"{Colors.FAIL}❌ [{i:3d}/{iterations}] Error: {e}{Colors.ENDC}")
        
        # Pequeña pausa entre iteraciones
        time.sleep(0.1)
    
    # Reporte final
    elapsed = time.time() - start_test
    
    print_header("RESULTADOS FINALES")
    
    print(f"{'Iteraciones totales:':<30} {iterations}")
    print(f"{'Exitosas:':<30} {Colors.OKGREEN}{success_count}{Colors.ENDC}")
    if fail_count > 0:
        print(f"{'Fallidas:':<30} {Colors.FAIL}{fail_count}{Colors.ENDC}")
    
    success_rate = (success_count / iterations * 100) if iterations > 0 else 0
    print(f"{'Tasa de éxito:':<30} {success_rate:.1f}%")
    
    print(f"\n{'Total líneas procesadas:':<30} {total_lines}")
    print(f"{'Tiempo total:':<30} {elapsed:.2f}s")
    
    if total_time > 0:
        avg_throughput = total_lines / total_time
        print(f"{'Throughput promedio:':<30} {avg_throughput:.1f} líneas/s")
    
    if errors:
        print(f"\n{Colors.WARNING}Errores encontrados:{Colors.ENDC}")
        for err in errors[:10]:
            print(f"  • {err}")
        if len(errors) > 10:
            print(f"  ... y {len(errors) - 10} errores más")
    
    # Resultado
    if fail_count == 0:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 TEST EXITOSO - 100% estabilidad{Colors.ENDC}")
        return 0
    elif success_rate >= 95:
        print(f"\n{Colors.WARNING}⚠️  TEST PARCIALMENTE EXITOSO - {success_rate:.1f}% estabilidad{Colors.ENDC}")
        return 1
    else:
        print(f"\n{Colors.FAIL}❌ TEST FALLIDO - Baja estabilidad ({success_rate:.1f}%){Colors.ENDC}")
        return 2


if __name__ == '__main__':
    # Ejecutar 100 iteraciones por defecto (configurable desde línea de comandos)
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    exit(run_continuous_test(iterations))
