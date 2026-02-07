#!/usr/bin/env python3
"""
ADMX2001 - Firmware Update Assistant
Verifica requisitos y guía el proceso de actualización de firmware.

Versión Actual Detectada: 1.2.2 (Build RT-2 Apr 18 2024)
Versión Más Reciente: 1.3.2 (Estable)
"""

import sys
import os
import subprocess
import platform
import shutil
from pathlib import Path

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓{Colors.ENDC} {text}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠{Colors.ENDC} {text}")

def print_error(text):
    print(f"{Colors.FAIL}✗{Colors.ENDC} {text}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ{Colors.ENDC} {text}")

def check_python_version():
    """Verifica que Python sea 3.7+"""
    print_info("Verificando versión de Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} instalado")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} encontrado. Se requiere Python 3.7+")
        return False

def check_quartus():
    """Verifica si Intel Quartus Prime está instalado"""
    print_info("Verificando Intel Quartus Prime Programmer...")
    
    # Comandos comunes de Quartus
    quartus_commands = ['quartus_pgm', 'quartus', 'quartus_sh']
    
    for cmd in quartus_commands:
        if shutil.which(cmd):
            print_success(f"Quartus encontrado: {cmd}")
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.stdout:
                    print(f"  Versión: {result.stdout.strip()[:100]}")
            except:
                pass
            return True
    
    print_warning("Quartus Prime Programmer no encontrado en PATH")
    print(f"  {Colors.CYAN}Debe instalarse desde:{Colors.ENDC}")
    print(f"  https://www.intel.com/content/www/us/en/software-kit/785086/intel-quartus-prime-lite-edition-design-software-version-23-1-1-for-linux.html")
    return False

def check_usb_blaster():
    """Verifica si hay un USB Blaster conectado"""
    print_info("Verificando Intel Altera USB Blaster...")
    
    try:
        # Buscar dispositivos USB Altera
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        if 'Altera' in result.stdout or '09fb' in result.stdout:  # 09fb = Altera Vendor ID
            print_success("USB Blaster detectado")
            for line in result.stdout.split('\n'):
                if 'Altera' in line or '09fb' in line:
                    print(f"  {line.strip()}")
            return True
        else:
            print_warning("USB Blaster no detectado")
            print(f"  {Colors.CYAN}Conecte el Intel Altera USB Blaster a la placa EVAL-ADMX2001EBZ{Colors.ENDC}")
            return False
    except FileNotFoundError:
        print_warning("Comando 'lsusb' no disponible")
        return False

def check_firmware_file(firmware_path=None):
    """Verifica si el archivo de firmware *.pof existe"""
    print_info("Verificando archivo de firmware...")
    
    if firmware_path and Path(firmware_path).exists():
        print_success(f"Archivo de firmware encontrado: {firmware_path}")
        return True
    
    # Buscar en ubicaciones comunes
    common_paths = [
        "Admx2001Firmware-Rel1.3.2/Firmware/admx_lcr_encrypted.pof",
        "firmware/admx_lcr_encrypted.pof",
        "admx_lcr_encrypted.pof",
        os.path.expanduser("~/Downloads/admx_lcr_encrypted.pof"),
    ]
    
    for path in common_paths:
        if Path(path).exists():
            print_success(f"Archivo de firmware encontrado: {path}")
            return path
    
    print_error("Archivo de firmware (*.pof) no encontrado")
    print(f"  {Colors.CYAN}Debe solicitarse contactando: admx-support@analog.com{Colors.ENDC}")
    print(f"  Especificar versión deseada: 1.3.2 (recomendada)")
    return False

def check_device_connection():
    """Verifica si el dispositivo ADMX2001 está conectado"""
    print_info("Verificando conexión con ADMX2001...")
    
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            try:
                import serial
                ser = serial.Serial(port.device, 115200, timeout=2)
                ser.write(b"*IDN?\r\n")
                response = ser.read(200).decode('utf-8', errors='ignore')
                ser.close()
                
                if 'ADMX2001' in response:
                    print_success(f"ADMX2001 conectado en {port.device}")
                    print(f"  {response.strip()}")
                    return port.device
            except:
                pass
        
        print_warning("ADMX2001 no detectado en puertos seriales")
        return False
    except ImportError:
        print_warning("pyserial no instalado (pip install pyserial)")
        return False

def backup_calibrations_warning():
    """Muestra advertencia sobre backup de calibraciones"""
    print_warning("IMPORTANTE: RESPALDO DE CALIBRACIONES")
    print(f"\n{Colors.BOLD}Antes de actualizar el firmware, DEBE:{Colors.ENDC}")
    print(f"  1. Ir al Dashboard de ZORIA")
    print(f"  2. Conectar el dispositivo")
    print(f"  3. Ir a Terminal CLI")
    print(f"  4. Ejecutar: {Colors.CYAN}calibrate list{Colors.ENDC}")
    print(f"  5. Guardar la salida completa en un archivo")
    print(f"  6. Para cada frecuencia listada, ejecutar:")
    print(f"     {Colors.CYAN}calibrate list <frecuencia>{Colors.ENDC}")
    print(f"  7. Guardar todas las respuestas")
    print(f"\n{Colors.WARNING}{'!'*70}{Colors.ENDC}")
    print(f"{Colors.WARNING}⚠  LA ACTUALIZACIÓN PUEDE BORRAR TODAS LAS CALIBRACIONES GUARDADAS  ⚠{Colors.ENDC}")
    print(f"{Colors.WARNING}{'!'*70}{Colors.ENDC}\n")

def show_update_steps():
    """Muestra los pasos para actualizar el firmware"""
    print_header("PASOS PARA ACTUALIZAR FIRMWARE")
    
    steps = [
        ("Respaldo de Calibraciones", [
            "Ejecutar 'calibrate list' y guardar salida",
            "Para cada frecuencia: 'calibrate list <freq>' y guardar",
            "Anotar todas las configuraciones importantes"
        ]),
        ("Preparación del Hardware", [
            "Conectar adaptador de corriente 9VDC a EVAL-ADMX2001EBZ",
            "Conectar Intel Altera USB Blaster a la placa",
            "Conectar USB Blaster a la PC",
            "Verificar que los LEDs de la placa estén encendidos"
        ]),
        ("Obtención del Firmware", [
            "Contactar: admx-support@analog.com",
            "Solicitar: Firmware versión 1.3.2 para ADMX2001B",
            "Descargar y descomprimir el archivo recibido",
            "Localizar el archivo: admx_lcr_encrypted.pof"
        ]),
        ("Instalación de Software", [
            "Descargar Intel Quartus Prime Programmer And Tools",
            "Instalar drivers para Altera USB Blaster",
            "Verificar instalación: quartus_pgm --version"
        ]),
        ("Actualización", [
            "Ejecutar el script de actualización:",
            "  python admx2001_flash_pof.py --pof <ruta_al_archivo.pof>",
            "NO INTERRUMPIR el proceso (20-30 segundos)",
            "Esperar mensaje de confirmación"
        ]),
        ("Verificación Post-Actualización", [
            "Desconectar y reconectar el dispositivo",
            "Conectar desde ZORIA Dashboard",
            "Ejecutar: *IDN? en Terminal CLI",
            "Verificar que la versión sea 1.3.2",
            "Restaurar calibraciones si es necesario"
        ])
    ]
    
    for idx, (title, substeps) in enumerate(steps, 1):
        print(f"\n{Colors.BOLD}{idx}. {title}{Colors.ENDC}")
        for substep in substeps:
            print(f"   • {substep}")

def show_firmware_versions():
    """Muestra tabla de versiones de firmware"""
    print_header("VERSIONES DE FIRMWARE DISPONIBLES")
    
    print(f"{Colors.BOLD}{'Versión':<10} {'Estado':<10} {'Características'}{Colors.ENDC}")
    print("-" * 70)
    
    versions = [
        ("1.3.2", "Estable", "Optimizaciones de tiempo, correcciones menores", True),
        ("1.3.1", "Estable", "Mejoras sustanciales de ruido y correcciones", False),
        ("1.2.4", "Estable", "Mismo que 1.2.2 + script de instalación", False),
        ("1.2.2", "Actual", "Calibración sobre frecuencia, triggers", True),
        ("1.2.0", "Estable", "Correcciones, mejoras de ruido", False),
    ]
    
    for version, status, features, highlight in versions:
        if highlight:
            print(f"{Colors.GREEN}{version:<10}{Colors.ENDC} {status:<10} {features}")
        else:
            print(f"{version:<10} {status:<10} {features}")
    
    print("\n" + Colors.CYAN + "Recomendación: Actualizar a versión 1.3.2" + Colors.ENDC)
    print(f"Beneficios de 1.3.2 sobre 1.2.2:")
    print(f"  • Mejoras de ruido (de 1.3.1)")
    print(f"  • Optimización de tiempos de medición")
    print(f"  • GUI Python incluida")
    print(f"  • Mayor estabilidad")

def main():
    """Función principal"""
    print_header("ASISTENTE DE ACTUALIZACIÓN DE FIRMWARE ADMX2001")
    
    print(f"{Colors.BOLD}Versión Actual Detectada:{Colors.ENDC}")
    print(f"ADMX2001 - Firmware 1.2.2 - Build RT-2 Apr 18 2024")
    print(f"Board ID: 0x2820d10431c29880\n")
    
    print(f"{Colors.BOLD}Versión Recomendada:{Colors.ENDC}")
    print(f"ADMX2001 - Firmware 1.3.2 (Estable, última versión)\n")
    
    # Mostrar versiones disponibles
    show_firmware_versions()
    
    # Advertencia de respaldo
    backup_calibrations_warning()
    
    input(f"\n{Colors.CYAN}Presiona ENTER para continuar con la verificación de requisitos...{Colors.ENDC}")
    
    print_header("VERIFICACIÓN DE REQUISITOS")
    
    results = {}
    results['python'] = check_python_version()
    results['quartus'] = check_quartus()
    results['usb_blaster'] = check_usb_blaster()
    results['firmware_file'] = check_firmware_file()
    results['device'] = check_device_connection()
    
    # Resumen
    print_header("RESUMEN DE VERIFICACIÓN")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nRequisitos cumplidos: {passed}/{total}\n")
    
    for name, result in results.items():
        status = "✓ OK" if result else "✗ FALTA"
        color = Colors.GREEN if result else Colors.FAIL
        print(f"{color}{status}{Colors.ENDC} - {name.replace('_', ' ').title()}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}¡Todos los requisitos están listos!{Colors.ENDC}")
        show_update_steps()
        print(f"\n{Colors.CYAN}Puede proceder con la actualización siguiendo los pasos de arriba.{Colors.ENDC}")
    else:
        print(f"\n{Colors.WARNING}{Colors.BOLD}Faltan requisitos.{Colors.ENDC}")
        print(f"Complete los requisitos faltantes antes de actualizar.\n")
        show_update_steps()
    
    # Información de contacto
    print_header("SOPORTE Y DESCARGA")
    print(f"Para obtener el firmware y script de actualización:")
    print(f"  {Colors.BOLD}Email:{Colors.ENDC} admx-support@analog.com")
    print(f"  {Colors.BOLD}Solicitar:{Colors.ENDC} Firmware versión 1.3.2 para ADMX2001B")
    print(f"  {Colors.BOLD}Script:{Colors.ENDC} admx2001_flash_pof.py (incluido en descarga)\n")
    
    print(f"{Colors.WARNING}RECORDATORIO FINAL:{Colors.ENDC}")
    print(f"1. Respaldar TODAS las calibraciones antes de actualizar")
    print(f"2. NO interrumpir el proceso de actualización")
    print(f"3. Verificar la actualización con *IDN? después de completar\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Proceso cancelado por el usuario.{Colors.ENDC}")
        sys.exit(1)
