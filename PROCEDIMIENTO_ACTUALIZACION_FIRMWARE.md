# PROCEDIMIENTO DE ACTUALIZACIÓN DE FIRMWARE ADMX2001

## 📊 Versión Actual vs. Disponible

| Componente | Versión Actual | Versión Disponible | Estado |
|------------|----------------|-------------------|---------|
| **Firmware** | 1.2.2 (Build RT-2) | 1.3.2 (Estable) | ⚠️ **Actualización Disponible** |
| **Build Date** | Apr 18 2024 | Más reciente | - |
| **Board ID** | 0x2820d10431c29880 | - | - |

## 🎯 Beneficios de Actualizar 1.2.2 → 1.3.2

### Versión 1.3.1 (intermedia):
- ✅ **Mejoras sustanciales de ruido**
- ✅ Múltiples correcciones de bugs
- ✅ Mayor estabilidad general

### Versión 1.3.2 (objetivo):
- ✅ **Optimizaciones de tiempo de medición**
- ✅ Correcciones menores adicionales
- ✅ **GUI Python incluida** en la descarga
- ✅ Script simplificado de instalación

## ⚠️ ADVERTENCIAS CRÍTICAS

### 🔴 ANTES DE ACTUALIZAR:

```
┌─────────────────────────────────────────────────────────────┐
│  ⚠️  LA ACTUALIZACIÓN PUEDE BORRAR LAS CALIBRACIONES  ⚠️   │
│                                                              │
│  DEBE HACER RESPALDO COMPLETO ANTES DE PROCEDER            │
└─────────────────────────────────────────────────────────────┘
```

1. **Respaldo de Calibraciones**:
   ```bash
   # En Terminal CLI de ZORIA:
   calibrate list
   # Anotar TODAS las frecuencias listadas
   
   # Para cada frecuencia:
   calibrate list 1000
   calibrate list 5000
   # ... etc.
   
   # Guardar TODA la salida en archivo de texto
   ```

2. **NO interrumpir** el proceso de actualización
3. **NO desconectar** la placa durante la actualización
4. **Proceso toma** 20-30 segundos

## 📋 REQUISITOS DE HARDWARE

### Equipo Necesario:
- ✅ Placa **EVAL-ADMX2001EBZ**
- ✅ Módulo **ADMX2001B** (instalado en la placa)
- 🔧 **Intel Altera USB Blaster** (programador)
- 🔌 **Adaptador de corriente 9VDC**

### Conexiones:
```
PC ----USB----> USB Blaster ----JTAG----> EVAL-ADMX2001EBZ <----9VDC
                                                 |
                                                 |
                                            ADMX2001B
                                            (Módulo)
```

## 💻 REQUISITOS DE SOFTWARE

### Sistema Operativo:
- ✅ Linux (actual)
- También compatible: Windows, macOS

### Software Requerido:

1. **Python 3.7+** ✅ (ya instalado)
   ```bash
   python --version
   # Debe mostrar: Python 3.7 o superior
   ```

2. **Intel Quartus Prime Programmer And Tools**
   - **Descarga**: https://www.intel.com/content/www/us/en/software-kit/785086/
   - **Versión**: 23.1.1 para Linux (última estable)
   - **Componentes necesarios**: Solo "Programmer And Tools" (no requiere el IDE completo)
   - **Tamaño**: ~4 GB de descarga, ~10 GB instalado

3. **Drivers Altera USB Blaster**
   - Incluidos con Quartus Prime
   - En Linux: puede requerir configuración de udev rules

4. **pyserial** ✅ (ya instalado en ZORIA)
   ```bash
   pip install pyserial
   ```

## 📦 OBTENCIÓN DEL FIRMWARE

### Paso 1: Contactar Soporte

**Email**: admx-support@analog.com

**Plantilla de solicitud**:
```
Asunto: Solicitud de Firmware 1.3.2 para ADMX2001B

Estimado equipo de soporte,

Solicito el paquete de firmware versión 1.3.2 para el módulo 
ADMX2001B.

Información del dispositivo actual:
- Modelo: ADMX2001B
- Placa: EVAL-ADMX2001EBZ
- Firmware actual: 1.2.2 (Build RT-2 Apr 18 2024)
- Board ID: 0x2820d10431c29880
- Sistema operativo: Linux

Requiero:
- Archivo de firmware (*.pof)
- Script de instalación (admx2001_flash_pof.py)
- Documentación de actualización

Gracias,
[Tu nombre]
```

### Paso 2: Descargar y Descomprimir

Recibirás un archivo comprimido con estructura:
```
Admx2001Firmware-Rel1.3.2/
├── Firmware/
│   └── admx_lcr_encrypted.pof    ← Archivo principal
├── admx2001_flash_pof.py          ← Script de actualización
├── GUI/                            ← Interfaz gráfica Python
│   └── [archivos GUI]
├── README.txt
└── RELEASE_NOTES.txt
```

## 🔧 INSTALACIÓN DE QUARTUS PRIME

### Para Linux (Ubuntu/Debian):

```bash
# 1. Descargar desde Intel
wget https://downloads.intel.com/akdlm/software/acdsinst/23.1std.1/993/ib_installers/QuartusProgrammerSetup-23.1std.1.993-linux.run

# 2. Dar permisos de ejecución
chmod +x QuartusProgrammerSetup-23.1std.1.993-linux.run

# 3. Instalar
./QuartusProgrammerSetup-23.1std.1.993-linux.run

# 4. Agregar a PATH (editar ~/.bashrc)
export PATH=$PATH:/home/$USER/intelFPGA/23.1std/quartus/bin

# 5. Recargar configuración
source ~/.bashrc

# 6. Verificar instalación
quartus_pgm --version
```

### Configurar USB Blaster en Linux:

```bash
# Crear regla udev para USB Blaster
sudo nano /etc/udev/rules.d/51-altera-usb-blaster.rules

# Agregar esta línea:
SUBSYSTEM=="usb", ATTR{idVendor}=="09fb", ATTR{idProduct}=="6001", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="09fb", ATTR{idProduct}=="6002", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="09fb", ATTR{idProduct}=="6003", MODE="0666"

# Recargar reglas
sudo udevadm control --reload-rules
sudo udevadm trigger

# Verificar detección
lsusb | grep Altera
# Debe mostrar: Bus XXX Device XXX: ID 09fb:XXXX Altera
```

## 🚀 PROCEDIMIENTO DE ACTUALIZACIÓN

### CHECKLIST PRE-ACTUALIZACIÓN:

```
[ ] Respaldo completo de calibraciones guardado
[ ] Adaptador 9VDC conectado a EVAL-ADMX2001EBZ
[ ] USB Blaster conectado a placa
[ ] USB Blaster conectado a PC
[ ] LEDs de la placa encendidos
[ ] Quartus Prime instalado y en PATH
[ ] Archivo .pof descargado y localizado
[ ] Script admx2001_flash_pof.py disponible
```

### EJECUCIÓN:

```bash
# 1. Navegar a carpeta del firmware
cd ~/Downloads/Admx2001Firmware-Rel1.3.2/

# 2. Verificar archivos
ls -la
# Debe mostrar: admx2001_flash_pof.py y carpeta Firmware/

# 3. Ejecutar actualización
python admx2001_flash_pof.py --pof "Firmware/admx_lcr_encrypted.pof"

# 4. Esperar salida (ejemplo):
#   Checking for USB Blaster... Found
#   Programming FPGA...
#   [===================] 100%
#   Verification... OK
#   Update completed successfully!

# 5. NO INTERRUMPIR (20-30 segundos)
```

### SALIDA ESPERADA:

```
Intel Quartus Prime Programmer
Loading POF file...
Info: Device chain detection successful
Info: Programming device...
Info (209060): Started Programmer operation at [timestamp]
Info (209016): Configuring device index 1
Info (209017): Device 10M08SAE144 contains JTAG ID code 0x02D020DD
Info (209034): Programmer operation PASSED
Info (209061): Ended Programmer operation at [timestamp]
Info: Operation successful

✓ Firmware actualizado a versión 1.3.2
```

## ✅ VERIFICACIÓN POST-ACTUALIZACIÓN

### Paso 1: Reconectar Dispositivo
```bash
# 1. Desconectar USB serial del ADMX2001
# 2. Esperar 5 segundos
# 3. Reconectar USB serial
```

### Paso 2: Verificar en ZORIA
```bash
# 1. Iniciar ZORIA
python app.py

# 2. Ir a Dashboard → Conectar dispositivo

# 3. Ir a Terminal CLI (abajo)

# 4. Ejecutar comando:
*IDN?

# 5. Verificar salida (debe mostrar):
ADMX2001 - Precision Impedance Analyzer Measurement Module 1.3.2 - Build ...
Board ID - 0x2820d10431c29880
```

### Paso 3: Pruebas Funcionales

1. **Medición básica**:
   ```
   frequency 1000
   z
   # Debe retornar medición válida
   ```

2. **Verificar calibraciones**:
   ```
   calibrate list
   # Si está vacío → restaurar desde respaldo
   ```

3. **Prueba de sweep**:
   ```
   sweep_type freq 1000 10000
   sweep_scale log
   # Ejecutar desde Dashboard
   ```

## 🔄 RESTAURACIÓN DE CALIBRACIONES

Si las calibraciones se borraron durante la actualización:

### Opción A: Recalibrar (Recomendado)

1. Ir a **Calibration** → **Iniciar Wizard**
2. Seguir proceso: Open → Short → Load
3. Ejecutar y guardar cada paso
4. Commit para guardar en flash

### Opción B: Comando Manual (si tienes respaldo)

```bash
# Si respaldaste los comandos exactos, repetirlos:
calibrate open
calibrate short
calibrate rt 1000 xt 0
calibrate commit 12345
# etc.
```

## 📊 COMPARACIÓN DE VERSIONES

| Característica | v1.2.2 (Actual) | v1.3.2 (Nueva) |
|----------------|-----------------|----------------|
| **Calibración sobre frecuencia** | ✅ | ✅ |
| **Triggers externos** | ✅ | ✅ |
| **Mejoras de ruido** | Básicas | ✅ Sustanciales |
| **Optimización de tiempos** | - | ✅ Mejorado |
| **GUI Python** | ❌ | ✅ Incluida |
| **Script de instalación** | ❌ | ✅ Incluido |
| **Estabilidad** | Estable | ✅ Más estable |

## 🆘 SOLUCIÓN DE PROBLEMAS

### Error: "USB Blaster no detectado"

```bash
# Verificar conexión
lsusb | grep Altera

# Si no aparece:
1. Verificar cable USB Blaster
2. Verificar LEDs en USB Blaster
3. Revisar udev rules (ver sección anterior)
4. Probar otro puerto USB
```

### Error: "Permission denied"

```bash
# Agregar usuario a grupo de dialout
sudo usermod -a -G dialout $USER

# Cerrar sesión y volver a entrar
```

### Error: "POF file not found"

```bash
# Verificar ruta completa
ls -la Firmware/admx_lcr_encrypted.pof

# Si no existe, re-descargar firmware
```

### Actualización se colgó

```
⚠️ NO DESCONECTAR
1. Esperar hasta 5 minutos
2. Si no responde, contactar soporte
3. NO intentar actualizar de nuevo sin soporte
```

## 📞 SOPORTE

**Email**: admx-support@analog.com

**Información a incluir en caso de problemas**:
- Versión de firmware original (1.2.2)
- Board ID (0x2820d10431c29880)
- Sistema operativo (Linux)
- Logs completos del proceso
- Mensaje de error exacto

## 📚 RECURSOS ADICIONALES

- **Documentación oficial**: Incluida en descarga del firmware
- **Foro Intel Quartus**: community.intel.com/t5/Programmable-Devices/bd-p/programmable-devices
- **ZORIA Dashboard**: Interfaz completa para operación post-actualización

---

**Última actualización**: 7 de febrero de 2026
**Versión del documento**: 1.0
**Autor**: ZORIA Firmware Update Assistant
