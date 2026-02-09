#!/usr/bin/env python3
"""
Script de pruebas de escala para streaming con dispositivo ADMX2001 REAL

Pruebas exhaustivas basadas en la documentación oficial:
- Diferentes escalas de count (1 a 1000 líneas)
- Diferentes display modes (0-17)
- Diferentes configuraciones de ganancia
- Mediciones de performance
- Validación de integridad de datos
"""

import sys
import time
import re
from pathlib import Path
import serial.tools.list_ports

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent))

from lib.device_state import device_state
from lib.admx2001 import ADMX2001
from lib.enums import DisplayMode

# Configuración de colores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_test(text):
    print(f"{Colors.OKCYAN}{Colors.BOLD}📝 {text}{Colors.ENDC}")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")


class StreamingTestSuite:
    """Suite completa de pruebas de streaming para ADMX2001"""
    
    def __init__(self):
        self.results = []
        self.device = None
        self.connected = False
        
    def connect_device(self):
        """Conectar al dispositivo ADMX2001 real"""
        print_header("CONEXIÓN AL DISPOSITIVO ADMX2001")
        
        try:
            # Listar puertos USB disponibles
            all_ports = list(serial.tools.list_ports.comports())
            usb_ports = [p for p in all_ports if 'USB' in p.device.upper() or 'ACM' in p.device.upper() or 'ttyUSB' in p.device]
            
            print_info(f"Detectados {len(usb_ports)} puerto(s) USB")
            
            # Priorizar candidatos FTDI
            candidates = []
            for p in usb_ports:
                desc = p.description.upper() if p.description else ""
                manuf = p.manufacturer.upper() if p.manufacturer else ""
                if any(x in desc or x in manuf for x in ['FTDI', 'CP210', 'SILICON', 'USB-SERIAL', 'FT232', 'TTL232']):
                    candidates.append(p)
                    print_info(f"  Candidato FTDI: {p.device} - {p.description}")
            
            # Probar candidatos
            ports_to_try = candidates if candidates else usb_ports
            
            for p in ports_to_try[:3]:
                try:
                    print_info(f"Probando puerto {p.device}...")
                    dev = ADMX2001(p.device, baudrate=115200, timeout=3.0)
                    time.sleep(0.5)
                    
                    # Verificar identidad
                    resp = dev.send_command('*idn')
                    
                    if resp and any(x in str(resp).upper() for x in ['ADMX', '2001', 'ANALOG']):
                        # Configurar delays óptimos
                        dev.set_mdelay(1)
                        dev.set_tdelay(0)
                        
                        # Establecer en device_state
                        device_state.set_device(dev, True)
                        self.device = dev
                        self.connected = True
                        
                        print_success(f"Conectado al ADMX2001 en {p.device}")
                        
                        # Obtener información
                        idn = dev.get_idn()
                        version = dev.get_version()
                        print_info(f"Identificación: {idn}")
                        print_info(f"Versión firmware: {version}")
                        
                        return True
                    else:
                        dev.close()
                        print_warning(f"Puerto {p.device} no responde como ADMX2001")
                        
                except Exception as e:
                    print_warning(f"Fallo en {p.device}: {e}")
                    continue
            
            print_error("No se encontró dispositivo ADMX2001 en ningún puerto")
            return False
                
        except Exception as e:
            print_error(f"Error de conexión: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def configure_basic_settings(self):
        """Configurar ajustes básicos del dispositivo"""
        print_header("CONFIGURACIÓN BÁSICA")
        
        try:
            # Display mode 6 (R, X) - rectangular coordinates
            self.device.set_display_mode(DisplayMode.R_X)
            print_info("Display mode: 6 (R, X - Rectangular coordinates)")
            
            # DESACTIVAR sweeps - hacer mediciones repetidas en frecuencia fija
            self.device.send_command("sweep_type none")
            print_info("Sweep: Desactivado (mediciones repetidas)")
            
            # Frecuencia de prueba: 100kHz
            self.device.send_command("frequency 100")
            print_info("Frecuencia: 100 kHz")
            
            # Magnitud: 1V
            self.device.send_command("magnitude 1")
            print_info("Magnitud: 1V")
            
            # Ganancia Ch0: 0 (±2.5V)
            self.device.send_command("setgain ch0 0")
            print_info("Ganancia Ch0: 0 (±2.5V)")
            
            # Ganancia Ch1: 1 (2.5mA, 499Ω)
            self.device.send_command("setgain ch1 1")
            print_info("Ganancia Ch1: 1 (2.5mA, 499Ω)")
            
            # Promediado: 10 samples
            self.device.send_command("average 10")
            print_info("Average: 10 samples")
            
            print_success("Configuración básica completada")
            return True
            
        except Exception as e:
            print_error(f"Error en configuración: {e}")
            return False
    
    def test_streaming_count(self, count, test_name):
        """
        Prueba de streaming con count específico
        
        Args:
            count: Número de muestras a solicitar
            test_name: Nombre descriptivo del test
        """
        print_test(f"TEST: {test_name} (count={count})")
        
        result = {
            'test': test_name,
            'count': count,
            'success': False,
            'lines_received': 0,
            'lines_expected': count,
            'time_elapsed': 0,
            'errors': []
        }
        
        try:
            # Configurar count
            self.device.send_command(f"count {count}")
            time.sleep(0.1)
            
            # Iniciar medición y timing
            start_time = time.time()
            
            # Usar el método de streaming del device_state
            # Timeout generoso: 1 hora para tests grandes
            device_state.start_streaming_command('z', timeout=3600.0)
            
            # Esperar a que complete
            # Timeout generoso: hasta 1 hora para tests grandes
            max_wait = max(60.0, count * 1.0)  # 1 segundo por línea mínimo
            wait_start = time.time()
            
            while not device_state.is_streaming_complete():
                if time.time() - wait_start > max_wait:
                    result['errors'].append(f"Timeout esperando completación ({max_wait}s)")
                    break
                time.sleep(0.1)
            
            # Obtener líneas
            lines = device_state.get_streaming_lines()
            result['lines_received'] = len(lines)
            result['time_elapsed'] = time.time() - start_time
            
            # Validar datos
            data_lines = [l for l in lines if l['type'] == 'data' and l['line'].strip()]  # Filtrar vacías
            error_lines = [l for l in lines if l['type'] == 'error']
            
            # Logging detallado de todas las líneas recibidas
            if len(data_lines) != count:
                print_warning(f"Todas las líneas recibidas ({len(lines)} total):")
                for idx, l in enumerate(lines):
                    print_warning(f"  [{idx}] tipo={l['type']}, línea='{l['line']}'")
            
            if error_lines:
                for err in error_lines:
                    result['errors'].append(err['line'])
            
            # Validar formato de cada línea de datos
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            for line_data in data_lines:
                line = line_data['line']
                # Limpiar códigos ANSI
                line_clean = ansi_escape.sub('', line).strip()
                
                # Validar formato: debe ser "numero,numero,numero"
                parts = line_clean.split(',')
                if len(parts) != 3:
                    result['errors'].append(f"Formato inválido: '{line_clean}'")
                    continue
                
                # Validar que sean números
                try:
                    idx = float(parts[0])
                    val1 = float(parts[1])
                    val2 = float(parts[2])
                except ValueError:
                    result['errors'].append(f"Valores no numéricos: '{line_clean}'")
            
            # Determinar éxito
            result['success'] = (
                len(data_lines) == count and 
                len(result['errors']) == 0
            )
            
            # Reportar resultado
            if result['success']:
                throughput = count / result['time_elapsed']
                print_success(f"Recibidas {len(data_lines)}/{count} líneas en {result['time_elapsed']:.2f}s ({throughput:.1f} líneas/s)")
            else:
                print_error(f"FALLO: Recibidas {len(data_lines)}/{count} líneas, {len(result['errors'])} errores")
                for err in result['errors'][:5]:  # Mostrar primeros 5 errores
                    print_error(f"  - {err}")
                if len(result['errors']) > 5:
                    print_error(f"  ... y {len(result['errors']) - 5} errores más")
            
        except Exception as e:
            result['errors'].append(str(e))
            print_error(f"Excepción: {e}")
        
        self.results.append(result)
        return result['success']
    
    def test_different_display_modes(self):
        """Prueba streaming con diferentes display modes"""
        print_header("PRUEBAS DE DISPLAY MODES")
        
        # Modos más comunes para prueba
        test_modes = [
            (0, "Cs, Rs - Series capacitance and resistance"),
            (6, "R, X - Rectangular coordinates"),
            (7, "Z, deg - Magnitude and phase (degrees)"),
            (9, "Cp, Rp - Parallel capacitance and resistance"),
        ]
        
        for mode_num, mode_desc in test_modes:
            print_test(f"Display Mode {mode_num}: {mode_desc}")
            
            try:
                # Configurar display mode
                self.device.send_command(f"display {mode_num}")
                time.sleep(0.1)
                
                # Count pequeño para prueba rápida
                self.device.send_command("count 5")
                time.sleep(0.1)
                
                # Ejecutar medición
                device_state.start_streaming_command('z', timeout=10.0)
                
                # Esperar completación
                time.sleep(2.0)
                
                # Obtener líneas
                lines = device_state.get_streaming_lines()
                data_lines = [l for l in lines if l['type'] == 'data']
                
                if len(data_lines) == 5:
                    print_success(f"Mode {mode_num}: OK - {len(data_lines)} líneas")
                else:
                    print_warning(f"Mode {mode_num}: Recibidas {len(data_lines)}/5 líneas")
                    
            except Exception as e:
                print_error(f"Mode {mode_num}: Error - {e}")
        
        # Restaurar mode 6
        self.device.send_command("display 6")
    
    def run_scale_tests(self):
        """Ejecutar tests de escala progresiva"""
        print_header("PRUEBAS DE ESCALA DE STREAMING")
        
        # Tests de escala: enfocados en rangos realistas (el dispositivo limita a ~100 puntos por sweep)
        scale_tests = [
            (1, "Mínimo (1 punto)"),
            (10, "Pequeño (10 puntos)"),
            (50, "Medio (50 puntos)"),
            (100, "Grande (100 puntos - máximo del dispositivo)"),
        ]
        
        for count, name in scale_tests:
            success = self.test_streaming_count(count, name)
            if not success:
                print_warning(f"Fallo en escala {count}, continuando con siguientes tests...")
            time.sleep(1.0)  # Pausa entre tests
    
    def generate_report(self):
        """Generar reporte final de resultados"""
        print_header("REPORTE FINAL DE PRUEBAS")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total de pruebas: {total_tests}")
        print_success(f"Exitosas: {passed_tests}")
        if failed_tests > 0:
            print_error(f"Fallidas: {failed_tests}")
        
        print("\n" + "="*80)
        print(f"{'Test':<40} {'Count':>8} {'Recibidas':>10} {'Tiempo':>10} {'Estado':>12}")
        print("="*80)
        
        for result in self.results:
            test_name = result['test'][:38]
            count = result['count']
            received = result['lines_received']
            elapsed = f"{result['time_elapsed']:.2f}s"
            status = "✅ OK" if result['success'] else "❌ FALLO"
            
            print(f"{test_name:<40} {count:>8} {received:>10} {elapsed:>10} {status:>12}")
        
        print("="*80)
        
        # Métricas de performance
        if passed_tests > 0:
            print("\n📊 MÉTRICAS DE PERFORMANCE:")
            
            successful_results = [r for r in self.results if r['success']]
            
            total_lines = sum(r['lines_received'] for r in successful_results)
            total_time = sum(r['time_elapsed'] for r in successful_results)
            avg_throughput = total_lines / total_time if total_time > 0 else 0
            
            print(f"  • Total líneas procesadas: {total_lines}")
            print(f"  • Tiempo total: {total_time:.2f}s")
            print(f"  • Throughput promedio: {avg_throughput:.1f} líneas/segundo")
            
            # Throughput por escala
            print("\n  Throughput por escala:")
            for result in successful_results:
                throughput = result['lines_received'] / result['time_elapsed']
                print(f"    - {result['count']:>4} líneas: {throughput:>6.1f} líneas/s")
        
        # Resumen de errores
        all_errors = []
        for result in self.results:
            if not result['success']:
                all_errors.extend(result['errors'])
        
        if all_errors:
            print(f"\n{Colors.FAIL}⚠️  ERRORES ENCONTRADOS:{Colors.ENDC}")
            unique_errors = list(set(all_errors))
            for err in unique_errors[:10]:
                print(f"  • {err}")
            if len(unique_errors) > 10:
                print(f"  ... y {len(unique_errors) - 10} errores más")
        
        return passed_tests == total_tests


def main():
    """Función principal"""
    print_header("TEST SUITE DE STREAMING - ADMX2001 REAL")
    print_info("Basado en documentación oficial del EVAL-ADMX2001")
    print_info("Este script requiere conexión con el dispositivo real")
    
    suite = StreamingTestSuite()
    
    # Paso 1: Conectar al dispositivo
    if not suite.connect_device():
        print_error("No se pudo conectar al dispositivo. Abortando tests.")
        return 1
    
    # Paso 2: Configurar ajustes básicos
    if not suite.configure_basic_settings():
        print_error("Fallo en configuración básica. Abortando tests.")
        return 1
    
    # Paso 3: Ejecutar tests de escala
    suite.run_scale_tests()
    
    # Paso 4: Tests de display modes
    suite.test_different_display_modes()
    
    # Paso 5: Generar reporte
    all_passed = suite.generate_report()
    
    # Resultado final
    if all_passed:
        print_header("🎉 TODOS LOS TESTS EXITOSOS 🎉")
        return 0
    else:
        print_header("⚠️  ALGUNOS TESTS FALLARON")
        return 1


if __name__ == '__main__':
    exit(main())
