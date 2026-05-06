"""
Componente de Terminal CLI Global
Disponible en todas las páginas de la aplicación
"""
from dash import html, dcc

def global_terminal_component():
    """
    Terminal CLI global que se incluye en todas las páginas.
    Se activa mediante el botón flotante o desde el sidebar.
    """
    MODAL_ID = 'command-modal'
    
    return html.Div([
        # Stores para estado del terminal (solo una vez en la app)
        dcc.Store(id='command-history-store', data={'commands': [], 'index': -1}, storage_type='session'),
        dcc.Store(id='terminal-initialized', data=False),
        dcc.Store(id='terminal-focus-trigger', data=None),
        dcc.Store(id='terminal-drag-init', data=0),  # Para inicialización de ventana arrastrable
        dcc.Store(id='terminal-scroll-trigger', data=0),  # Para auto-scroll del terminal
        dcc.Store(id='terminal-streaming-state', data={'active': False, 'command': ''}),  # Estado de streaming
        dcc.Store(id='terminal-password-state', data={'waiting': False, 'original_command': ''}, storage_type='memory'),  # Estado de espera de contraseña
        
        # Interval para polling de líneas en streaming (100ms)
        dcc.Interval(id='terminal-streaming-interval', interval=100, disabled=True, n_intervals=0),
        
        # Terminal ventana arrastrable
        html.Div([
            # Header - estructura estandarizada
            html.Div([
                # Título + status
                html.Div([
                    html.I(className="fas fa-terminal me-2"),
                    html.Span("", **{'data-i18n': 'ui.terminal_title'}),
                    html.Span([
                        html.Span(className="status-pulse me-1", id="terminal-status-dot"),
                        html.Small(id="terminal-status-text", className="text-muted status-text d-none d-sm-inline")
                    ], className="ms-3 d-none d-sm-inline-flex align-items-center")
                ], className="window-title"),
                
                # Controles
                html.Div([
                    html.Button(
                        html.I(className="fas fa-minus"),
                        id="terminal-minimize-btn",
                        className="window-control-btn window-btn-minimize",
                        title="",
                        **{'data-i18n-title': 'ui.minimize'}
                    ),
                    html.Button(
                        html.I(className="fas fa-expand"),
                        id="terminal-maximize-btn",
                        className="window-control-btn window-btn-maximize",
                        title="",
                        **{'data-i18n-title': 'ui.max_restore'}
                    ),
                    html.Button(
                        html.I(className="fas fa-times"),
                        id="terminal-close-btn",
                        className="window-control-btn window-btn-close",
                        title="",
                        **{'data-i18n-title': 'ui.close_esc'}
                    ),
                ], className="window-controls")
            ], className="window-header", id="terminal-header-drag"),
            
            # Body
            html.Div([
                # Área de output
                html.Div([
                    html.Div(
                        id="command-output",
                        className="terminal-float-screen",
                        children=[
                            html.Div([
                                html.Pre("""
╔══════════════════════════════════════════════════╗
║  ADMX2001 - Terminal Interactivo v2.0            ║
║  Impedance Analyzer CLI                          ║
║  Analog Devices Evaluation Board                 ║
╚══════════════════════════════════════════════════╝
                                """, className="terminal-banner text-success mb-2")
                            ]),
                            html.Div([
                                # Estado del sistema
                                html.Div([
                                    html.Span("$ ", className="text-success fw-bold"),
                                    html.Span("system", className="text-info"),
                                    html.Span(" --status", className="text-muted")
                                ], className="terminal-line"),
                                html.Div([
                                    html.Span("→ ", className="text-warning"),
                                    html.Span("", className="text-muted", **{'data-i18n': 'ui.waiting_connection'})
                                ], className="terminal-line mb-2"),
                                
                                # Ayuda de comandos
                                html.Div([
                                    html.Span("💡 ", className="terminal-prompt-icon"),
                                    html.Span("", className="text-info fw-bold", **{'data-i18n': 'ui.available_commands'})
                                ], className="terminal-line mb-1"),
                                html.Div([
                                    html.Span("   • ", className="text-muted"),
                                    html.Code("help", className="terminal-code"),
                                    html.Span("", className="text-muted", **{'data-i18n': 'term.help_list_cmds'})
                                ], className="terminal-line"),
                                html.Div([
                                    html.Span("   • ", className="text-muted"),
                                    html.Code("z", className="terminal-code"),
                                    html.Span("", className="text-muted", **{'data-i18n': 'term.help_measure'})
                                ], className="terminal-line"),
                                html.Div([
                                    html.Span("   • ", className="text-muted"),
                                    html.Code("status", className="terminal-code"),
                                    html.Span("", className="text-muted", **{'data-i18n': 'term.help_status'})
                                ], className="terminal-line"),
                                html.Div([
                                    html.Span("   • ", className="text-muted"),
                                    html.Code("sweep", className="terminal-code"),
                                    html.Span("", className="text-muted", **{'data-i18n': 'term.help_sweep'})
                                ], className="terminal-line mb-2"),
                                
                                # Atajos de teclado
                                html.Div([
                                    html.Span("⌨️  ", className="terminal-prompt-icon"),
                                    html.Span("", className="text-info me-2", **{'data-i18n': 'ui.shortcuts_label'}),
                                    html.Span("Alt+T", style={
                                        'background': 'rgba(255,255,255,0.15)',
                                        'border': '1px solid rgba(255,255,255,0.3)',
                                        'borderRadius': '3px',
                                        'padding': '1px 5px',
                                        'fontSize': '0.75rem',
                                        'color': '#fff'
                                    }),
                                    html.Span("", className="small text-light me-2", **{'data-i18n': 'ui.open_close'}),
                                    html.Span("↑↓", style={
                                        'background': 'rgba(255,255,255,0.15)',
                                        'border': '1px solid rgba(255,255,255,0.3)',
                                        'borderRadius': '3px',
                                        'padding': '1px 5px',
                                        'fontSize': '0.75rem',
                                        'color': '#fff'
                                    }),
                                    html.Span("", className="small text-light", **{'data-i18n': 'ui.history'})
                                ], className="terminal-line"),
                            ], className="terminal-content-area")
                        ]
                    )
                ], className="window-body", style={'background': '#0a0a0a'}),
                
                # Input line
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span("➜", className="terminal-prompt-icon"),
                            html.Span(" ~", className="terminal-prompt-path")
                        ], className="terminal-prompt d-flex align-items-center"),
                        
                        dcc.Input(
                            id="command-input",
                            type="text",
                            placeholder="",
                            autoComplete="off",
                            autoFocus=False,
                            className="terminal-command-input",
                            n_submit=0,
                            n_blur=0
                        ),
                        
                        html.Span("█", className="terminal-cursor", id="terminal-cursor")
                    ], className="terminal-input-wrapper d-flex align-items-center px-3 py-2")
                ], className="terminal-float-input-area"),
                
                # Footer con botones rápidos
                html.Div([
                    html.Div([
                        html.Div([
                            html.Button([
                                html.I(className="fas fa-zap text-warning")
                            ], id="quick-measure-btn", className="terminal-float-quick-btn", title="z"),
                            html.Button([
                                html.I(className="fas fa-question text-info")
                            ], id="quick-help-btn", className="terminal-float-quick-btn", title="help"),
                            html.Button([
                                html.I(className="fas fa-info text-primary")
                            ], id="quick-status-btn", className="terminal-float-quick-btn", title="status"),
                            html.Button([
                                html.I(className="fas fa-code-branch text-secondary")
                            ], id="quick-version-btn", className="terminal-float-quick-btn", title="version"),
                        ], className="terminal-float-quick-group"),
                        
                        html.Div(className="terminal-float-divider"),
                        
                        html.Div([
                            html.Button([
                                html.I(className="fas fa-trash-alt text-danger")
                            ], id="clear-terminal-btn", className="terminal-float-quick-btn", title="", **{'data-i18n-title': 'footer.clear'}),
                            html.Button([
                                html.I(className="fas fa-download text-success")
                            ], id="export-terminal-btn", className="terminal-float-quick-btn", title="", **{'data-i18n-title': 'ui.export'}),
                        ], className="terminal-float-quick-group"),
                    ], className="terminal-float-footer-inner d-flex align-items-center px-2 py-1")
                ], className="terminal-float-footer")
            ], className="window-body"),
            
            # Resize handle
            html.Div(className="window-resize-handle")
        ], 
        id=MODAL_ID,
        className='draggable-window terminal-window',
        style={'display': 'none', 'visibility': 'visible', 'opacity': '1'}
        )
    ])
