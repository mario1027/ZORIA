"""
Índice de búsqueda para la documentación ZORIA.
Cada entrada enlaza pestaña Dash + ancla HTML + palabras clave.
"""
from __future__ import annotations

DOC_SEARCH_INDEX = [
    {
        "id": "qs-drivers",
        "tab": "inicio",
        "anchor": "doc-sec-drivers",
        "title": "Instalación de drivers FTDI VCP",
        "keywords": "driver ftdi vcp com puerto serial usb uart device manager",
        "snippet": "Descargar drivers FTDI VCP e identificar el puerto COM en el Administrador de dispositivos.",
    },
    {
        "id": "qs-teraterm",
        "tab": "inicio",
        "anchor": "doc-sec-teraterm",
        "title": "Terminal TeraTerm — conexión serial",
        "keywords": "teraterm terminal emulator serial 115200 8n1 putty cli",
        "snippet": "Instalar TeraTerm, conectar al puerto COM a 115200 8N1 y ver el prompt ADMX2001>.",
    },
    {
        "id": "qs-hardware",
        "tab": "hardware",
        "anchor": "doc-sec-hw-setup",
        "title": "Conexiones básicas del hardware",
        "keywords": "hardware conexion bnc open gnd dut alimentacion 9v self-test led",
        "snippet": "Montaje ADMX2001B, switches OPEN/GND, alimentación, UART y pinzas BNC al DUT.",
    },
    {
        "id": "qs-measure",
        "tab": "inicio",
        "anchor": "doc-sec-measure",
        "title": "Medición básica con comando z",
        "keywords": "medicion z frequency magnitude average display sweep",
        "snippet": "Configurar frecuencia y magnitud, luego medir impedancia con el comando z.",
    },
    {
        "id": "cal-open",
        "tab": "calibracion",
        "anchor": "doc-sec-cal-open",
        "title": "Calibración Open (circuito abierto)",
        "keywords": "calibrate open osl open short load calibracion pinzas",
        "snippet": "Procedimiento open: separar H_CUR/H_POT y L_CUR/L_POT antes de calibrate open.",
    },
    {
        "id": "cal-short",
        "tab": "calibracion",
        "anchor": "doc-sec-cal-short",
        "title": "Calibración Short (cortocircuito)",
        "keywords": "calibrate short cortocircuito shorting",
        "snippet": "Unir terminales según guía Analog antes de calibrate short.",
    },
    {
        "id": "cal-load",
        "tab": "calibracion",
        "anchor": "doc-sec-cal-load",
        "title": "Calibración Load (carga conocida)",
        "keywords": "calibrate rt load resistencia 1000 ohm commit password",
        "snippet": "Conectar resistencia de referencia y ejecutar calibrate rt; guardar con calibrate commit.",
    },
    {
        "id": "cal-list",
        "tab": "calibracion",
        "anchor": "doc-sec-cal-list",
        "title": "Listar calibraciones en flash",
        "keywords": "calibrate list flash almacenadas ch0 ch1 gain reload erase",
        "snippet": "calibrate list muestra frecuencias calibradas; calibrate list <Hz> muestra CH0/CH1.",
    },
    {
        "id": "cli-help",
        "tab": "cli",
        "anchor": "doc-sec-cli-help",
        "title": "Comandos CLI — help e *idn",
        "keywords": "cli help idn comandos firmware version terminal",
        "snippet": "help lista comandos; *idn identifica firmware y hardware.",
    },
    {
        "id": "cli-sweep",
        "tab": "cli",
        "anchor": "doc-sec-cli-sweep",
        "title": "Barrido de frecuencia (sweep)",
        "keywords": "sweep frequency start end points scale linear log trigger",
        "snippet": "sweep start/end/points/scale; escala log o linear; modo trigger para N mediciones.",
    },
    {
        "id": "cli-gain",
        "tab": "cli",
        "anchor": "doc-sec-cli-gain",
        "title": "Ganancia por canal (setgain)",
        "keywords": "setgain auto ch0 ch1 gain rango impedancia tabla",
        "snippet": "Tabla de ganancia CH0/CH1 según |Z|; setgain auto o valores manuales 0-3.",
    },
    {
        "id": "math-impedance",
        "tab": "matematica",
        "anchor": "doc-sec-math-z",
        "title": "Impedancia compleja Z = R + jX",
        "keywords": "impedancia reactancia fase magnitud nyquist bode matematica",
        "snippet": "Z en coordenadas rectangulares y polares; relación con gráficos Bode y Nyquist.",
    },
    {
        "id": "fw-update",
        "tab": "firmware",
        "anchor": "doc-sec-fw-update",
        "title": "Actualización de firmware",
        "keywords": "firmware update pof programador admx-support analog",
        "snippet": "Solicitar archivo .pof a Analog Devices; no interrumpir alimentación durante update.",
    },
    {
        "id": "sw-zoria",
        "tab": "software",
        "anchor": "doc-sec-zoria-dash",
        "title": "ZORIA Dashboard y terminal integrado",
        "keywords": "zoria dash dashboard python gui barrido graficos terminal",
        "snippet": "Interfaz web ZORIA: dashboard, calibración guiada, simulador RLC y terminal CLI.",
    },
    {
        "id": "hw-pinout",
        "tab": "hardware",
        "anchor": "doc-sec-pinout",
        "title": "Pinout ADMX2001B",
        "keywords": "pinout conector som uart spi sdp arduino sma trigger clock",
        "snippet": "Señales UART, SPI, trigger, clock y headers Arduino en EVAL-ADMX2001EBZ.",
    },
    {
        "id": "wiki-official",
        "tab": "inicio",
        "anchor": "doc-sec-wiki-link",
        "title": "Wiki oficial Analog Devices EVAL-ADMX2001EBZ",
        "keywords": "wiki analog devices documentacion oficial eval admx2001ebz",
        "snippet": "Guía completa en wiki.analog.com — hardware, calibración, CLI y firmware.",
    },
]


def search_documentation(query: str, limit: int = 12) -> list:
    """Filtra entradas por consulta (título, keywords, snippet)."""
    q = (query or "").strip().lower()
    if not q:
        return []

    tokens = [t for t in q.split() if len(t) >= 2]
    if not tokens:
        return []

    scored = []
    for entry in DOC_SEARCH_INDEX:
        haystack = " ".join(
            [entry["title"], entry["keywords"], entry["snippet"]]
        ).lower()
        score = sum(1 for t in tokens if t in haystack)
        if score > 0:
            scored.append((score, entry))

    scored.sort(key=lambda x: (-x[0], x[1]["title"]))
    return [e for _, e in scored[:limit]]
