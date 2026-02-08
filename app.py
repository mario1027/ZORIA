"""
ZORIA Dashboard - Aplicación principal

Dashboard web interactivo para análisis de impedancia y caracterización de circuitos.
Utiliza Dash/Plotly para visualización y se comunica con dispositivos ADMX2001 vía serial.

Author: Mario Ricardo Montero, Juan Carlos Alvarez, Francisco J. Racedo N.
Email: mariomontero942@gmail.com 
License: MIT
"""

# =============================================================================
# IMPORTS ESTÁNDAR
# =============================================================================
import os
import logging
import sys
from pathlib import Path
from typing import Optional

# =============================================================================
# IMPORTS DE TERCEROS
# =============================================================================
from dash_spa import DashSPA, page_container

# =============================================================================
# IMPORTS LOCALES
# =============================================================================
from themes import VOLT


# =============================================================================
# CONFIGURACIÓN DE LOGGING
# =============================================================================
def setup_logging(log_level: Optional[str] = None) -> logging.Logger:
    """
    Configura el sistema de logging de la aplicación.
    
    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR). 
                  Si es None, usa la variable de entorno LOG_LEVEL o INFO por defecto.
    
    Returns:
        Logger configurado para la aplicación.
    """
    level = (log_level or os.environ.get("LOG_LEVEL", "INFO")).upper()
    
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    return logging.getLogger(__name__)


# =============================================================================
# CONFIGURACIÓN DE RECURSOS (SOPORTE OFFLINE)
# =============================================================================
# Estas dependencias están descargadas localmente en assets/vendor/
# para permitir el funcionamiento sin conexión a internet.

EXTERNAL_STYLESHEETS = [
    # Normalización CSS (local)
    "/assets/vendor/css/normalize.min.css",
    # Chartist para gráficos (local)
    "/assets/vendor/css/chartist.min.css",
    # Font Awesome para iconos (local)
    "/assets/vendor/css/all.min.css",
    # Notyf para notificaciones (local)
    "/assets/vendor/css/notyf.min.css",
    # Tema VOLT Bootstrap 5 (local)
    "/assets/vendor/css/volt.min.css",
    # Estilos locales de la aplicación
    "/assets/css/navigation.css",
    "/assets/css/mobile-nav.css",
    "/assets/css/scichart-themes.css",
    "/assets/css/calibration.css",
    "/assets/css/calibration-wizard.css",
    "/assets/css/windows.css",
    "/assets/css/modal-connect.css",
]

EXTERNAL_SCRIPTS = [
    # Bootstrap 5 JS (local)
    "/assets/vendor/js/bootstrap.bundle.min.js",
    # SweetAlert2 para modales mejorados (local)
    "/assets/vendor/js/sweetalert2.all.min.js",
    # Notyf para notificaciones (local)
    "/assets/vendor/js/notyf.min.js",
    # Sistema de ventanas arrastrables (local)
    "/assets/js/draggable_windows.js",
]

# =============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# =============================================================================
DEFAULT_CONFIG = {
    "title": "ZORIA Dashboard",
    "assets_folder": "assets",
    "favicon": "logo.png",
    "port": 8050,
    "host": "localhost",
    "debug": True,
    "use_reloader": False,
}


def register_global_terminal_callbacks(app):
    """
    Registra los callbacks globales del terminal CLI.
    Estos callbacks están disponibles en todas las páginas.
    """
    from dash import Input, Output, State, ctx, html
    from dash.exceptions import PreventUpdate
    from datetime import datetime
    from lib.device_state import device_state
    
    # Clientside callback para inicializar terminal (teclado + arrastre)
    app.clientside_callback(
        """
        function(style) {
            console.log('[Terminal] Callback ejecutado, style:', style);
            
            // Solo ejecutar cuando está visible
            if (!style || style.display !== 'flex') {
                return window.dash_clientside.no_update;
            }
            
            console.log('[Terminal] Ventana mostrada, inicializando...');
            
            setTimeout(function() {
                var input = document.getElementById('command-input');
                var terminal = document.getElementById('command-modal');
                
                if (!input || !terminal) {
                    console.warn('[Terminal] Elementos no encontrados');
                    return;
                }
                
                // === INICIALIZAR TECLADO ===
                input.onkeydown = function(e) {
                    var historyData = JSON.parse(JSON.stringify(
                        document.getElementById('command-history-store').data || {'commands': [], 'index': -1}
                    ));
                    var commands = historyData.commands || [];
                    var currentIndex = historyData.index;
                    if (currentIndex === undefined) currentIndex = commands.length;
                    
                    if (e.key === 'Enter') {
                        return;
                    }
                    
                    if (e.key === 'ArrowUp') {
                        e.preventDefault();
                        if (commands.length > 0 && currentIndex > 0) {
                            currentIndex--;
                            input.value = commands[currentIndex];
                            document.getElementById('command-history-store').data = {
                                'commands': commands,
                                'index': currentIndex
                            };
                        }
                        return false;
                    }
                    
                    if (e.key === 'ArrowDown') {
                        e.preventDefault();
                        if (currentIndex < commands.length - 1) {
                            currentIndex++;
                            input.value = commands[currentIndex];
                            document.getElementById('command-history-store').data = {
                                'commands': commands,
                                'index': currentIndex
                            };
                        } else if (currentIndex === commands.length - 1) {
                            currentIndex = commands.length;
                            input.value = '';
                            document.getElementById('command-history-store').data = {
                                'commands': commands,
                                'index': currentIndex
                            };
                        }
                        return false;
                    }
                    
                    if (e.key === 'Escape') {
                        if (input.value === '') {
                            terminal.style.display = 'none';
                        } else {
                            input.value = '';
                        }
                        return false;
                    }
                    
                    if (e.key === 'l' && e.ctrlKey) {
                        e.preventDefault();
                        var clearBtn = document.getElementById('clear-terminal-btn');
                        if (clearBtn) clearBtn.click();
                        return false;
                    }
                };
                
                // === INICIALIZAR SISTEMA DE ARRASTRE ===
                terminal.classList.remove('terminal-hidden-initial');
                
                if (!window.DraggableWindows) {
                    console.error('[Terminal] DraggableWindows no disponible');
                    return;
                }
                
                if (window.DraggableWindows.isInitialized('command-modal')) {
                    console.log('[Terminal] Ya inicializado - traer al frente');
                    window.DraggableWindows.bringToFront('command-modal');
                } else {
                    console.log('[Terminal] Inicializando sistema de arrastre...');
                    var success = window.DraggableWindows.init('command-modal', 'terminal-header-drag', {
                        width: 700,
                        height: 500
                    });
                    
                    if (success) {
                        console.log('[Terminal] ✅ Sistema inicializado');
                    }
                }
                
                // Enfocar input
                setTimeout(function() {
                    if (input) {
                        input.focus();
                    }
                }, 100);
                
            }, 250);
            
            return window.dash_clientside.no_update;
        }
        """,
        Output('terminal-initialized', 'data'),
        Input('command-modal', 'style')
    )
    
    # Callback para abrir/cerrar terminal desde cualquier página
    @app.callback(
        Output('command-modal', 'style', allow_duplicate=True),
        Output('command-modal', 'className', allow_duplicate=True),
        Input('sidebar-terminal-btn', 'n_clicks'),
        Input('floating-terminal-btn', 'n_clicks'),
        Input('terminal-close-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def toggle_terminal_sidebar(sidebar_clicks, floating_clicks, close_clicks):
        """Abre o cierra el terminal desde cualquier botón"""
        if not ctx.triggered:
            raise PreventUpdate
        
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Solo abrir cuando se hace clic específicamente en los botones de abrir
        if triggered_id in ['sidebar-terminal-btn', 'floating-terminal-btn']:
            if (triggered_id == 'sidebar-terminal-btn' and sidebar_clicks and sidebar_clicks > 0) or \
               (triggered_id == 'floating-terminal-btn' and floating_clicks and floating_clicks > 0):
                return {'display': 'flex'}, 'draggable-window terminal-window'
        # Cerrar por botón de cerrar
        elif triggered_id == 'terminal-close-btn' and close_clicks and close_clicks > 0:
            return {'display': 'none'}, 'draggable-window terminal-window'
        
        raise PreventUpdate
    
    # Callback para actualizar indicador de estado del terminal
    @app.callback(
        [Output('terminal-status-dot', 'className'),
         Output('terminal-status-text', 'children')],
        Input('command-modal', 'style'),
        prevent_initial_call=True
    )
    def update_terminal_status(style):
        """Actualiza el indicador visual de conexión del terminal"""
        from lib.device_state import device_state
        
        if style and style.get('display') == 'flex':
            # Verificar estado real del dispositivo
            is_conn, status_msg, port = device_state.verify_connection()
            
            if is_conn:
                port_text = f" ({port})" if port else ""
                return "status-pulse status-connected", f"conectado{port_text}"
            else:
                return "status-pulse status-disconnected", "desconectado"
        return "status-pulse", ""
    
    # Callback principal para manejar comandos del terminal
    @app.callback(
        [Output('command-output', 'children', allow_duplicate=True),
         Output('command-input', 'value', allow_duplicate=True),
         Output('command-history-store', 'data', allow_duplicate=True)],
        [Input('command-input', 'n_submit'),
         Input('quick-measure-btn', 'n_clicks'),
         Input('quick-help-btn', 'n_clicks'),
         Input('quick-status-btn', 'n_clicks'),
         Input('quick-version-btn', 'n_clicks'),
         Input('clear-terminal-btn', 'n_clicks')],
        [State('command-input', 'value'),
         State('command-output', 'children'),
         State('command-history-store', 'data')],
        prevent_initial_call=True
    )
    def handle_terminal_command_global(
        n_submit, measure_clicks, help_clicks, status_clicks, version_clicks,
        clear_clicks, command_text, current_output, history_store
    ):
        """
        Maneja todos los comandos del terminal CLI globalmente.
        Versión simplificada - funciona en todas las páginas.
        """
        # Inicializar historial
        if history_store is None:
            history_store = {'commands': [], 'index': -1}
        
        if not ctx.triggered:
            return current_output or [], "", history_store
        
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Normalizar output
        if current_output is None:
            current_output = []
        elif not isinstance(current_output, list):
            current_output = [current_output]
        
        # ===== LIMPIAR TERMINAL =====
        if triggered_id == 'clear-terminal-btn':
            welcome = html.Div([
                html.Div([
                    html.Span("$ ", className="text-success fw-bold"),
                    html.Span("clear", className="text-light")
                ], className="terminal-line"),
                html.Div([
                    html.Span("→ Terminal limpiada", className="text-muted")
                ], className="terminal-line mb-2")
            ])
            return [welcome], "", history_store
        
        # ===== DETERMINAR COMANDO =====
        quick_commands = {
            'quick-measure-btn': 'z',
            'quick-help-btn': 'help',
            'quick-status-btn': 'status',
            'quick-version-btn': 'version'
        }
        
        if triggered_id in quick_commands:
            command = quick_commands[triggered_id]
        elif triggered_id == 'command-input' and n_submit and n_submit > 0:
            command = (command_text or "").strip()
            if not command:
                return current_output, "", history_store
        else:
            return current_output, "", history_store
        
        # ===== AGREGAR AL HISTORIAL =====
        if triggered_id == 'command-input':
            if command and (not history_store['commands'] or history_store['commands'][-1] != command):
                history_store['commands'].append(command)
                if len(history_store['commands']) > 100:
                    history_store['commands'] = history_store['commands'][-100:]
            history_store['index'] = len(history_store['commands'])
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Obtener referencia al dispositivo desde el estado global
        device = device_state.device
        is_device_connected = device_state.is_connected
        
        # ===== PROCESAR COMANDO =====
        # Línea del comando
        cmd_block = html.Div([
            html.Div([
                html.Span(f"[{timestamp}] ", className="terminal-timestamp"),
                html.Span("➜ ", className="terminal-prompt-symbol"),
                html.Span(command, className="terminal-cmd-text")
            ], className="terminal-line")
        ])
        current_output.append(cmd_block)
        
        # ===== COMANDOS LOCALES (funcionan siempre, con o sin hardware) =====
        cmd_lower = command.lower()
        
        if cmd_lower == 'version':
            # Comando version: mostrar información local y del hardware
            response_children = [
                html.Div([
                    html.Span("  ", className="terminal-indent"),
                    html.Span("SOFTWARE:", className="terminal-response-line text-info fw-bold")
                ], className="terminal-line"),
                html.Div([
                    html.Span("    ", className="terminal-indent"),
                    html.Span("ZORIA Dashboard v1.0.0", className="terminal-response-line terminal-response-success")
                ], className="terminal-line"),
                html.Div([
                    html.Span("    ", className="terminal-indent"),
                    html.Span("Python Dashboard for ADMX2001 Impedance Analyzer", className="terminal-response-line")
                ], className="terminal-line"),
                html.Div([
                    html.Span("    ", className="terminal-indent"),
                    html.Span("Authors: Mario R. Montero, Juan C. Alvarez, Francisco J. Racedo N.", className="terminal-response-line")
                ], className="terminal-line"),
                html.Div([
                    html.Span("  ", className="terminal-indent"),
                    html.Span("", className="terminal-response-line")
                ], className="terminal-line"),
            ]
            
            # Intentar obtener información del hardware
            if is_device_connected and device is not None:
                try:
                    hw_response = device_state.send_command('*idn')
                    response_children.append(
                        html.Div([
                            html.Span("  ", className="terminal-indent"),
                            html.Span("HARDWARE:", className="terminal-response-line text-warning fw-bold")
                        ], className="terminal-line")
                    )
                    if hw_response:
                        for line in hw_response:
                            if line.strip():
                                response_children.append(
                                    html.Div([
                                        html.Span("    ", className="terminal-indent"),
                                        html.Span(line.strip(), className="terminal-response-line terminal-response-success")
                                    ], className="terminal-line")
                                )
                    else:
                        response_children.append(
                            html.Div([
                                html.Span("    ", className="terminal-indent"),
                                html.Span("(sin respuesta del hardware)", className="terminal-response-line text-muted")
                            ], className="terminal-line")
                        )
                except Exception as e:
                    response_children.append(
                        html.Div([
                            html.Span("  ", className="terminal-indent"),
                            html.Span("HARDWARE:", className="terminal-response-line text-warning fw-bold")
                        ], className="terminal-line")
                    )
                    response_children.append(
                        html.Div([
                            html.Span("    ", className="terminal-indent"),
                            html.Span(f"Error al consultar hardware: {str(e)}", className="terminal-response-line terminal-response-error")
                        ], className="terminal-line")
                    )
            else:
                response_children.append(
                    html.Div([
                        html.Span("  ", className="terminal-indent"),
                        html.Span("HARDWARE:", className="terminal-response-line text-warning fw-bold")
                    ], className="terminal-line")
                )
                response_children.append(
                    html.Div([
                        html.Span("    ", className="terminal-indent"),
                        html.Span("No conectado (modo simulación)", className="terminal-response-line text-muted")
                    ], className="terminal-line")
                )
            
            current_output.append(html.Div(response_children))
            current_output.append(html.Div(className="terminal-separator"))
            if len(current_output) > 80:
                current_output = current_output[-80:]
            return current_output, "", history_store
        
        # Verificar si hay dispositivo conectado
        if is_device_connected and device is not None:
            # ===== MODO REAL: Usar dispositivo ADMX2001 =====
            try:
                response = device_state.send_command(command)
                
                if response:
                    # Limpiar y procesar respuesta
                    cleaned_lines = []
                    for line in response:
                        if line.strip():
                            # Limpiar línea según utils
                            line_clean = line.strip()
                            cleaned_lines.append(line_clean)
                    
                    if cleaned_lines:
                        response_children = []
                        for line in cleaned_lines:
                            line_lower = line.lower()
                            css_class = "terminal-response-line"
                            prefix = html.Span("  ", className="terminal-indent")
                            
                            if any(err in line_lower for err in ['error', 'fail', 'invalid', 'unknown']):
                                css_class = "terminal-response-line terminal-response-error"
                                prefix = html.Span("✗ ", className="terminal-error-icon")
                            elif any(ok in line_lower for ok in ['ok', 'success', 'done', 'ready', 'pass']):
                                css_class = "terminal-response-line terminal-response-success"
                                prefix = html.Span("✓ ", className="terminal-success-icon")
                            elif any(warn in line_lower for warn in ['warning', 'warn', 'caution']):
                                css_class = "terminal-response-line terminal-response-warning"
                                prefix = html.Span("⚠ ", className="terminal-warning-icon")
                            
                            response_children.append(
                                html.Div([prefix, html.Span(line, className=css_class)], className="terminal-line")
                            )
                        current_output.append(html.Div(response_children))
                    else:
                        current_output.append(
                            html.Div([
                                html.Span("  ", className="terminal-indent"),
                                html.Span("(comando ejecutado - sin salida)", className="terminal-empty-response")
                            ], className="terminal-line")
                        )
                else:
                    current_output.append(
                        html.Div([
                            html.Span("  ", className="terminal-indent"),
                            html.Span("(sin respuesta)", className="terminal-empty-response")
                        ], className="terminal-line")
                    )
                    
            except Exception as e:
                error_msg = str(e)
                # Mensaje más amigable si es error de conexión
                if "not connected" in error_msg.lower() or "no conectado" in error_msg.lower():
                    error_msg = "Dispositivo desconectado. Reconecte desde el Dashboard."
                current_output.append(
                    html.Div([
                        html.Span("✗ ", className="terminal-error-icon"),
                        html.Span(f"Error: {error_msg}", className="terminal-error-text")
                    ], className="terminal-line terminal-error-line")
                )
        else:
            # ===== MODO SIMULACIÓN: Respuestas simuladas =====
            cmd_lower = command.lower()
            
            if cmd_lower == 'help':
                response_lines = [
                    "═══════════════════════════════════════════════════",
                    "  ADMX2001 - Comandos CLI (Documentación v1.3.2)",
                    "═══════════════════════════════════════════════════",
                    "",
                    "MEDICIÓN:",
                    "  z                      Medir impedancia",
                    "  frequency <Hz>         Configurar frecuencia (ej: 100 = 100kHz)",
                    "  magnitude <V>          Configurar magnitud señal (0.01-2V)",
                    "  offset <V>             Offset DC (-5V a +5V)",
                    "  average <1-256>        Promedio de muestras",
                    "  count <n>              Número de lecturas",
                    "  mdelay <ms>            Delay entre mediciones",
                    "  tdelay <ms>            Delay post-trigger",
                    "",
                    "DISPLAY:",
                    "  display <0-17>         Modo de display:",
                    "                         0=Cs-Rs, 3=Ls-Rs, 6=R-X (default)",
                    "                         7=Z-deg, 9=Cp-Rp, 15=G-B",
                    "",
                    "GANANCIA:",
                    "  setgain ch0 <0-3>      Ganancia voltaje (0=1x, 3=8x)",
                    "  setgain ch1 <0-3>      Ganancia corriente (0=25mA, 3=25uA)",
                    "  setgain auto           Auto-ranging",
                    "",
                    "BARRIDOS:",
                    "  sweep_type freq <s> <e>  Barrido de frecuencia",
                    "  sweep_scale log|linear   Escala del barrido",
                    "",
                    "CALIBRACIÓN:",
                    "  calibrate open         Medición open",
                    "  calibrate short        Medición short", 
                    "  calibrate rt <R> xt <X>  Medición load",
                    "  calibrate commit <ts>  Guardar calibración",
                    "  calibrate list         Listar calibraciones",
                    "",
                    "SISTEMA:",
                    "  *idn                   Identificación del hardware ADMX2001",
                    "  version                Información del Dashboard ZORIA",
                    "  help                   Esta ayuda",
                    "  status                 Estado del sistema",
                    "  reset                  Reset del sistema",
                    "",
                    "═══════════════════════════════════════════════════",
                    "Modo: SIMULACIÓN - Conecte el dispositivo en Dashboard",
                    "═══════════════════════════════════════════════════"
                ]
            elif cmd_lower == 'z':
                response_lines = [
                    "0,1.000021e+03,8.220137e-01",
                    "[SIMULADO] Z = 1.000kΩ + 0.822jΩ"
                ]
            elif cmd_lower == '*idn':
                response_lines = [
                    "ADMX2001B,FW=1.3.2,HW=Rev.A (SIMULADO)",
                ]
            elif cmd_lower == 'status':
                response_lines = [
                    "Sistema: Listo (modo simulación)",
                    "Conexión: No conectado a hardware",
                    "Para conectar: vaya al Dashboard principal"
                ]
            elif cmd_lower.startswith('frequency'):
                parts = command.split()
                freq_val = parts[1] if len(parts) > 1 else '1000'
                response_lines = [f"frequency = {freq_val}.0000Hz"]
            elif cmd_lower.startswith('setgain'):
                response_lines = ["setgain: configuración actualizada (simulado)"]
            elif cmd_lower.startswith('display'):
                response_lines = ["display: modo actualizado (simulado)"]
            elif cmd_lower.startswith('average'):
                response_lines = [f"average = {command.split()[1] if len(command.split()) > 1 else '1'}"]
            elif cmd_lower.startswith('calibrate'):
                response_lines = [
                    "calibrate: use el Dashboard para calibración completa",
                    "Wizard disponible en: Calibración > Iniciar Wizard"
                ]
            else:
                response_lines = [
                    f"Comando: {command}",
                    "",
                    "Nota: Conecte el dispositivo en el Dashboard",
                    "para obtener respuestas reales del hardware."
                ]
            
            # Renderizar respuesta simulada
            response_children = []
            for line in response_lines:
                response_children.append(
                    html.Div([
                        html.Span("  ", className="terminal-indent"),
                        html.Span(line, className="terminal-response-line")
                    ], className="terminal-line")
                )
            current_output.append(html.Div(response_children))
        
        # Línea separadora
        current_output.append(html.Div(className="terminal-separator"))
        
        # Limitar output
        if len(current_output) > 80:
            current_output = current_output[-80:]
        
        return current_output, "", history_store


def set_global_device(device, is_connected=False):
    """
    Establece el dispositivo global para el terminal CLI.
    Llamado desde dashboard_page cuando se conecta/desconecta.
    """
    from lib.device_state import device_state
    device_state.set_device(device, is_connected)


def get_secret_key() -> str:
    """
    Obtiene la SECRET_KEY para Flask.
    
    Prioridad:
    1. Variable de entorno SECRET_KEY
    2. Variable de entorno FLASK_SECRET_KEY
    3. Fallback seguro para desarrollo (con advertencia)
    
    Returns:
        String con la secret key.
    """
    secret = os.environ.get("SECRET_KEY") or os.environ.get("FLASK_SECRET_KEY")
    
    if not secret:
        # Fallback para desarrollo - NO USAR EN PRODUCCIÓN
        secret = "zoria-dev-secret-key-change-in-production"
        logging.getLogger(__name__).warning(
            "⚠️  Usando SECRET_KEY de desarrollo. "
            "Para producción, configure la variable de entorno SECRET_KEY"
        )
    
    return secret


def get_app_config() -> dict:
    """
    Obtiene la configuración de la aplicación desde variables de entorno.
    
    Returns:
        Diccionario con la configuración completa.
    """
    return {
        "title": os.environ.get("APP_TITLE", DEFAULT_CONFIG["title"]),
        "port": int(os.environ.get("PORT", DEFAULT_CONFIG["port"])),
        "host": os.environ.get("HOSTNAME", DEFAULT_CONFIG["host"]),
        "debug": os.environ.get("DEBUG", "true").lower() == "true",
        "use_reloader": os.environ.get("USE_RELOADER", "false").lower() == "true",
        "secret_key": get_secret_key(),
    }


# =============================================================================
# CREACIÓN DE LA APLICACIÓN
# =============================================================================
def create_app() -> DashSPA:
    """
    Crea y configura la aplicación DashSPA.
    
    Esta función inicializa la aplicación Dash con todas las configuraciones
    necesarias, registra las páginas y configura el servidor Flask subyacente.
    
    Returns:
        Instancia configurada de DashSPA.
    
    Raises:
        RuntimeError: Si hay un error crítico en la creación de la app.
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🚀 Inicializando ZORIA Dashboard...")
        
        # Crear instancia de DashSPA
        app = DashSPA(
            __name__,
            prevent_initial_callbacks=True,
            suppress_callback_exceptions=True,
            external_scripts=EXTERNAL_SCRIPTS,
            external_stylesheets=EXTERNAL_STYLESHEETS,
            url_base_pathname="/",
            assets_folder=DEFAULT_CONFIG["assets_folder"],
            title=DEFAULT_CONFIG["title"],
            update_title=None,
        )
        
        # Configurar favicon
        app._favicon = DEFAULT_CONFIG["favicon"]
        
        # Obtener configuración
        config = get_app_config()
        
        # Configurar servidor Flask
        app.server.config["SECRET_KEY"] = config["secret_key"]
        
        # Configurar modo debug
        if config["debug"]:
            logger.info("🔧 Modo DEBUG activado")
        
        logger.info("📦 Registrando páginas...")
        
        # Importar y registrar páginas
        # Nota: Los imports se hacen aquí para evitar problemas de circular import
        try:
            from pages.dashboard.dashboard_page import register_dashboard_page
            from pages.simulator.simulator_page import register_simulator_page
            from pages.calibration.calibration_page import register_calibration_page
            from pages.common.terminal_component import global_terminal_component
            from dash import html
            
            register_dashboard_page(app)
            logger.info("  ✓ Dashboard registrado")
            
            register_simulator_page(app)
            logger.info("  ✓ Simulator registrado")
            
            register_calibration_page(app)
            logger.info("  ✓ Calibration registrado")
            
            # Registrar callbacks globales del terminal
            register_global_terminal_callbacks(app)
            logger.info("  ✓ Terminal global registrado")
            
        except ImportError as e:
            logger.error(f"❌ Error registrando páginas: {e}")
            raise RuntimeError(f"No se pudieron registrar las páginas: {e}") from e
        
        # Establecer layout principal con terminal global
        # El terminal se inyecta en el layout para estar disponible en todas las páginas
        original_layout = page_container
        app.layout = html.Div([
            global_terminal_component(),
            original_layout
        ])
        
        logger.info("✅ Aplicación inicializada correctamente")
        return app
        
    except Exception as e:
        logger.error(f"❌ Error crítico al crear la aplicación: {e}")
        raise RuntimeError(f"Error al inicializar la aplicación: {e}") from e


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================
def main():
    """
    Punto de entrada principal de la aplicación.
    
    Configura logging, crea la aplicación y la ejecuta.
    """
    # Configurar logging primero
    logger = setup_logging()
    
    try:
        # Crear aplicación
        app = create_app()
        
        # Obtener configuración
        config = get_app_config()
        
        logger.info(f"🌐 Iniciando servidor en http://{config['host']}:{config['port']}")
        logger.info(f"⏹️  Para detener presione Ctrl+C")
        
        # Ejecutar aplicación
        app.run(
            host=config["host"],
            port=config["port"],
            debug=config["debug"],
            use_reloader=config["use_reloader"]
        )
        
    except KeyboardInterrupt:
        logger.info("\n👋 Servidor detenido por el usuario")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        sys.exit(1)


# =============================================================================
# INSTANCIA GLOBAL (para compatibilidad con server.py y despliegues)
# =============================================================================
# Configurar logging básico para imports
logger = setup_logging()

# Crear instancia global
try:
    app = create_app()
except Exception as e:
    logger.error(f"No se pudo crear la aplicación global: {e}")
    app = None  # type: ignore

# =============================================================================
# EJECUCIÓN DIRECTA
# =============================================================================
if __name__ == "__main__":
    main()
