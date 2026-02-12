#!/bin/bash
# Script de diagnóstico completo para problema de tabla de calibraciones

echo "======================================================================"
echo "DIAGNÓSTICO: Tabla de calibraciones vacía"
echo "======================================================================"
echo ""
echo "Este script te guiará para encontrar por qué la tabla sigue vacía"
echo ""
echo "Requisitos:"
echo "  - Dispositivo ADMX2001 conectado por USB"
echo "  - Puerto serial accesible (ej: /dev/ttyACM0)"
echo ""
echo "======================================================================"
echo ""

# Función para esperar tecla
wait_key() {
    echo ""
    read -p "Presiona ENTER para continuar..."
    echo ""
}

# Paso 1: Verificar dispositivo
echo "PASO 1: Verificar dispositivo conectado"
echo "----------------------------------------------------------------------"
echo ""
echo "Buscando puertos seriales..."
python3 -c "
import serial.tools.list_ports
ports = list(serial.tools.list_ports.comports())
if ports:
    print(f'✅ Puertos encontrados: {len(ports)}')
    for p in ports:
        print(f'  - {p.device}: {p.description}')
else:
    print('❌ No se encontraron puertos seriales')
    print('   Verifica que el dispositivo esté conectado')
"
wait_key

# Paso 2: Test directo del callback
echo "PASO 2: Simular el callback de calibración"
echo "----------------------------------------------------------------------"
echo ""
echo "Este test simula EXACTAMENTE lo que hace la página web"
echo "Te mostrará:"
echo "  1. Qué líneas recibe de 'calibrate list'"
echo "  2. Cómo las parsea"
echo "  3. Cuántas filas genera para la tabla"
echo ""
echo "Ejecutando test..."
echo ""

/usr/bin/python test_callback_simulation.py

EXIT_CODE=$?

echo ""
echo "======================================================================"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ El test funcionó correctamente"
    echo ""
    echo "Si el test muestra filas pero la web no, el problema es:"
    echo "  A) El callback no se ejecuta cuando haces clic"
    echo "  B) Hay error en el renderizado HTML"
    echo "  C) Problema de cache del navegador"
    echo ""
    echo "Soluciones:"
    echo "  1. Abre el navegador en modo incógnito"
    echo "  2. Recarga con Ctrl+Shift+R (forzar recarga)"
    echo "  3. Abre la consola del navegador (F12) y busca errores"
else
    echo "❌ El test encontró problemas"
    echo ""
    echo "Revisa la salida arriba para ver qué falló:"
    echo "  - Si no hay líneas crudas: problema de comunicación"
    echo "  - Si hay líneas pero no se parsean: formato incorrecto"
    echo "  - Si se parsea pero no hay filas: lógica de tabla"
fi

echo "======================================================================"
echo ""

wait_key

# Paso 3: Logs del dashboard
echo "PASO 3: Dashboard con logs detallados (OPCIONAL)"
echo "----------------------------------------------------------------------"
echo ""
echo "Si quieres ver los logs EN VIVO mientras usas la web:"
echo ""
echo "  1. Ejecuta en otra terminal:"
echo "     python test_calibration_page_debug.py"
echo ""
echo "  2. Abre http://localhost:8050 en el navegador"
echo ""
echo "  3. Conecta el dispositivo"
echo ""
echo "  4. Ve a Calibración y haz clic en 'Actualizar'"
echo ""
echo "  5. Mira los logs en la terminal donde ejecutaste el script"
echo ""
echo "======================================================================"
echo ""
echo "Diagnóstico completo. Revisa los resultados arriba."
echo ""
