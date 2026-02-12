# ANÁLISIS: Parseo de Comunicación Serial - TeraTerm vs ZORIA

## 🔍 Problema Central

**Estado Actual**: En nuestro terminal CLI, algunas respuestas se parsean incorrectamente o se pierden líneas. El problema está en cómo:
1. Recibimos datos del puerto serial
2. Detectamos el final de una respuesta
3. Filtramos el eco del comando
4. Separamos líneas individuales
5. Manejamos códigos especiales (CR, LF, ANSI)

---

## 📊 Comparación: TeraTerm vs ZORIA

### **1. RECEPCIÓN DE DATOS**

#### TeraTerm (C):
```c
// teraterm/teraterm/commlib.c
// Lee del puerto serial en un loop continuo
while (InBuffCount < InBuffSize - 1024) {
    ReadFile(hComm, &InBuff[InBuffCount], 
             InBuffSize - InBuffCount, &C, NULL);
    InBuffCount += C;
}
// Procesa byte por byte inmediatamente
ProcessIncomingChar(ch);
```

**Características**:
- ✅ Lee en chunks grandes (hasta llenar buffer)
- ✅ Procesa byte por byte en tiempo real
- ✅ No espera líneas completas
- ✅ Maneja caracteres especiales inmediatamente

#### ZORIA Actual (Python):
```python
# lib/admx2001.py: send_command()
while time.time() - start_time < timeout:
    if self.serial.in_waiting > 0:
        chunk = self.serial.read(self.serial.in_waiting)
        response_buffer += chunk.decode('utf-8', errors='ignore')
        
    if 'ADMX2001>' in response_buffer:
        break
```

**Problemas**:
- ❌ Lee todo in_waiting de una vez (puede perder datos si llegan rápido)
- ❌ Espera ver el prompt para terminar
- ❌ No maneja bien respuestas sin prompt
- ❌ Decodifica antes de procesar completamente

---

### **2. DETECCIÓN DE FINAL DE RESPUESTA**

#### TeraTerm:
```c
// Múltiples métodos de detección:
1. Detecta prompt específico (configurableUser defined)
2. Timeout sin datos nuevos (inactivity timeout)
3. Patrones específicos esperados (sendln/wait pairs)
4. Timeout absoluto
```

**Ventajas**:
- ✅ No depende solo del prompt
- ✅ Timeout inteligente (sin datos ≠ timeout total)
- ✅ Configurable por comando

#### ZORIA Actual:
```python
# Problema principal: depende SOLO del prompt
if 'ADMX2001>' in response_buffer:
    break
    
# Timeout por falta de datos es muy permisivo
if time_without_data > no_data_timeout:
    break  # no_data_timeout = 2.0s es mucho
```

**Problemas**:
- ❌ `calibrate list` puede NO terminar en prompt si lista está vacía
- ❌ Streaming puede perder último chunk si no hay prompt
- ❌ Too much delay (2 segundos sin datos)

---

### **3. FILTRADO DE ECO DE COMANDO**

#### TeraTerm:
```c
// vtterm.c
// El eco se maneja a nivel de configuración del terminal
if (ts.LocalEcho == 0) {
    // No mostrar caracteres enviados
    skip_echo = TRUE;
}
// Además, el dispositivo puede hacer echo
// TeraTerm filtra SOLO si detecta que es exactamente el comando enviado
```

**Ventajas**:
- ✅ Sabe si el eco viene del dispositivo o es local
- ✅ Configuración explícita de local echo
- ✅ Filtro inteligente: solo si coincide EXACTAMENTE

#### ZORIA Actual:
```python
# device_state.py: start_streaming_command()
if line_clean == cmd_echo:
    continue  # Filtrar eco exacto
elif line_clean.startswith(cmd_echo):
    line_clean = line_clean[len(cmd_echo):].strip()
```

**Problemas**:
- ❌ Asume que siempre hay eco
- ❌ No diferencia entre eco del dispositivo vs datos reales
- ❌ Puede filtrar líneas válidas que empiezan igual que el comando
- Ejemplo: comando `freq` filtraría línea válida `frequency: 1000 Hz`

---

### **4. SEPARACIÓN DE LÍNEAS**

#### TeraTerm:
```c
// buffer.c: BuffPutChar()
switch(ch) {
    case CR:  // Carriage Return
        if (ts.CRReceive == CRreceive_CR) {
            CarriageReturn();
        } else if (ts.CRReceive == CRreceive_CRLF) {
            // Esperar LF antes de procesar
            pending_cr = TRUE;
        }
        break;
    case LF:  // Line Feed
        if (pending_cr && ts.CRReceive == CRreceive_CRLF) {
            CarriageReturn();
            LineFeed();
        } else if (ts.LFReceive == LFreceive_LF) {
            LineFeed();
        }
        break;
}
```

**Características**:
- ✅ Configurable: CR, LF, CRLF
- ✅ Maneja ambos caracteres correctamente
- ✅ No pierde datos entre separadores

#### ZORIA Actual:
```python
# Simplemente split por \n
for line in response_buffer.split('\n'):
    line = clean_response_line(line)  # Limpia \r, espacios, ANSI
```

**Problemas**:
- ❌ Solo split por `\n`, ignora combinaciones CR+LF
- ❌ Si el dispositivo envía solo CR, no se detecta como nueva línea
- ❌ No configurable

---

### **5. LIMPIEZA DE CÓDIGOS ESPECIALES**

#### TeraTerm:
```c
// vtterm.c: ParseControl()
// Procesa caracteres de control en tiempo real
switch(b) {
    case ESC: // Escape sequences (ANSI)
        EscapeState = 1;
        break;
    case HT:  // Tab
        Tab();
        break;
    case BS:  // Backspace
        BackSpace();
        break;
    case BEL: // Bell
        BeepFlag = TRUE;
        break;
    // ... etc
}
```

**Características**:
- ✅ Procesa códigos mientras recibe
- ✅ Maneja ANSI sequences completos
- ✅ Emula correctamente el comportamiento del terminal

#### ZORIA Actual:
```python
# lib/utils.py: clean_response_line()
def clean_response_line(line: str) -> str:
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    line = ansi_escape.sub('', line)
    line = line.replace('\r', '').strip()
    return line
```

**Problemas**:
- ❌ Limpia DESPUÉS de recibir todo
- ❌ No procesa secuencias de control (Backspace, Clear Screen, etc.)
- ❌ Regex puede fallar con secuencias malformadas
- ❌ No emula comportamiento real del terminal

---

## 🔧 PROBLEMAS ESPECÍFICOS IDENTIFICADOS

### **Problema 1: `calibrate list` tabla vacía**

**Root Cause**:
```python
# pages/calibration/calibration_page.py
calibrations_raw = device.calibration.list_calibrations()
# Esto llama a:
# lib/admx2001.py -> send_command("calibrate list")

# Si la respuesta es:
# "calibrate list\nFREQ: 100000 Hz\nADMX2001>"
```

**¿Qué falla?**
1. La primera línea (eco) se filtra correctamente
2. PERO si device_state está en modo streaming, puede aplicar filtro doble
3. O si hay delay, el prompt puede llegar DESPUÉS del timeout sin datos

**Solución TeraTerm Style**:
```python
def send_command_improved(self, command, timeout=5.0):
    """Envío mejorado estilo TeraTerm"""
    
    # 1. Configurar timeout BASE (no para falta de datos)
    start_time = time.time()
    absolute_timeout = start_time + timeout
    
    # 2. Enviar comando
    self.serial.write((command + '\n').encode('utf-8'))
    self.serial.flush()
    
    # 3. Leer con estrategia de "no hay más datos"
    response_buffer = bytearray()  # Usar bytes, no string
    last_data_time = time.time()
    no_data_threshold = 0.3  # 300ms sin datos = terminar
    
    echo_filtered = False
    prompt_seen = False
    
    while time.time() < absolute_timeout:
        if self.serial.in_waiting > 0:
            # HAY DATOS - leer
            chunk = self.serial.read(self.serial.in_waiting)
            response_buffer.extend(chunk)
            last_data_time = time.time()
        else:
            # NO HAY DATOS
            idle_time = time.time() - last_data_time
            
            # ¿Prompt detectado?
            if b'ADMX2001>' in response_buffer:
                prompt_seen = True
                # Esperar 100ms más por si hay datos finales
                time.sleep(0.1)
                if self.serial.in_waiting == 0:
                    break
            
            # ¿Mucho tiempo sin datos?
            if idle_time > no_data_threshold:
                # Si ya tenemos datos, asumir que terminó
                if len(response_buffer) > 0:
                    break
            
            time.sleep(0.05)  # Breve pausa
    
    # 4. Decodificar UNA SOLA VEZ
    try:
        response_text = response_buffer.decode('utf-8', errors='replace')
    except:
        response_text = response_buffer.decode('latin-1', errors='replace')
    
    # 5. Filtrar eco (SOLO primera línea)
    lines = response_text.split('\n')
    cmd_lower = command.lower().strip()
    
    result_lines = []
    for idx, line in enumerate(lines):
        line_clean = clean_response_line(line)
        
        # Primera línea: verificar si es eco
        if idx == 0 and line_clean.lower() == cmd_lower:
            continue  # Filtrar eco
        
        # Última línea: verificar si es solo el prompt
        if idx == len(lines) - 1 and line_clean == 'ADMX2001>':
            continue
        
        # Líneas vacías: mantener SOLO si no es primera ni última
        if not line_clean:
            if idx > 0 and idx < len(lines) - 1:
                result_lines.append('')  # Separador
            continue
        
        # Línea válida
        if 'ADMX2001>' in line_clean:
            # Remover prompt inline
            line_clean = line_clean.replace('ADMX2001>', '').strip()
            if not line_clean:
                continue
        
        result_lines.append(line_clean)
    
    return result_lines
```

---

### **Problema 2: Streaming pierde últimas líneas**

**Root Cause**:
```python
# device_state.py
while '\n' in response_buffer:
    line, response_buffer = response_buffer.split('\n', 1)
    # Procesar línea...

# Si prompt llega SIN \n después:
# "Line 100\nADMX2001>"
# Solo procesa "Line 100"
# Nunca procesa "ADMX2001>" porque no tiene \n después
```

**Solución TeraTerm Style**:
```python
while True:
    # Procesar líneas completas
    while '\n' in response_buffer:
        line, response_buffer = response_buffer.split('\n', 1)
        process_line(line)
    
    # ¿Prompt en buffer (puede no tener \n)?
    if 'ADMX2001>' in response_buffer:
        prompt_seen = True
        # Procesar lo que queda antes del prompt
        if response_buffer:
            parts = response_buffer.split('ADMX2001>')
            if parts[0]:
                process_line(parts[0])
        break
    
    # Más datos?
    if self.serial.in_waiting > 0:
        chunk = self.serial.read(self.serial.in_waiting)
        response_buffer += chunk.decode('utf-8', errors='ignore')
    else:
        # Sin datos - ¿timeout?
        if time.time() - last_data_time > 0.3:
            # Procesar buffer final aunque no tenga \n
            if response_buffer.strip():
                process_line(response_buffer)
            break
```

---

### **Problema 3: clean_response_line() demasiado agresivo**

**Root Cause**:
```python
def clean_response_line(line: str) -> str:
    # Problema: limpia TODO, incluso datos válidos
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    line = ansi_escape.sub('', line)
    line = line.replace('\r', '').strip()
    
    # ¿Y si la línea es "  FREQ: 1000 Hz  "?
    # strip() elimina espacios de indentación que pueden ser significativos
    return line
```

**Solución TeraTerm Style**:
```python
def clean_response_line_improved(line: str, preserve_indent=False) -> str:
    """Limpieza mejorada estilo TeraTerm"""
    
    # 1. Remover códigos ANSI
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    line = ansi_escape.sub('', line)
    
    # 2. Normalizar line endings (CR+LF -> LF)
    line = line.replace('\r\n', '\n').replace('\r', '\n')
    
    # 3. Remover NULL bytes y caracteres de control (excepto \n)
    line = ''.join(ch for ch in line if ch >= ' ' or ch == '\n')
    
    # 4. Strip condicional
    if preserve_indent:
        # Remover SOLO trailing whitespace
        line = line.rstrip()
    else:
        # Strip completo
        line = line.strip()
    
    return line
```

---

## ✅ MEJORAS PROPUESTAS

### **Prioridad ALTA - Implementar Ya**:

1. **Mejorar `send_command()` en lib/admx2001.py**
   - Usar bytearray en lugar de string para buffer
   - Implementar timeout por "falta de datos" (300ms)
   - No depender solo del prompt
   - Filtrar eco SOLO en primera línea
   - Procesar buffer final aunque no tenga `\n`

2. **Mejorar `clean_response_line()` en lib/utils.py**
   - Opción para preservar indentación
   - Mejor manejo de CR+LF
   - No ser tan agresivo con strip()

3. **Fix streaming en device_state.py**
   - Procesar buffer final aunque no tenga `\n`
   - Detectar prompt sin necesidad de `\n` después
   - Reducir timeout sin datos de 2.0s a 0.3s

### **Prioridad MEDIA - Próxima Iteración**:

4. **Configuración de line endings**
   - Permitir CR, LF, o CRLF
   - Detectar automáticamente en respuestas

5. **Mejor filtrado de eco**
   - Diferenciar eco local vs dispositivo
   - Configuración explícita de "local echo"

6. **Buffer circular para terminal**
   - Limitar a N líneas (1000)
   - Auto-scroll inteligente

### **Prioridad BAJA - Futuro**:

7. **Emulación completa de terminal**
   - Procesar backspace, clear screen, etc.
   - Posición de cursor real
   - Full ANSI support

---

## 📝 SIGUIENTE PASO

**¿Implementar las 3 mejoras de PRIORIDAD ALTA ahora?**

Esto solucionaría:
- ✅ Tabla de calibraciones vacía
- ✅ Streaming que pierde líneas
- ✅ Filtrado incorrecto de respuestas

Archivos a modificar:
1. `lib/admx2001.py` - método `send_command()`
2. `lib/utils.py` - función `clean_response_line()`
3. `lib/device_state.py` - método `start_streaming_command()`
