"""
Componente de Terminal CLI Global
Estetica: Entorno de Instrumentacion Computacional — Round 3
"""
from dash import html, dcc

def global_terminal_component():
    """
    Terminal CLI global que se incluye en todas las paginas.
    Se activa mediante el boton flotante o desde el sidebar.
    """
    MODAL_ID = 'command-modal'
    
    return html.Div([
        dcc.Store(id='command-history-store', data={'commands': [], 'index': -1}, storage_type='session'),
        dcc.Store(id='terminal-initialized', data=False),
        dcc.Store(id='terminal-focus-trigger', data=None),
        dcc.Store(id='terminal-drag-init', data=0),
        dcc.Store(id='terminal-scroll-trigger', data=0),
        dcc.Store(id='terminal-streaming-state', data={'active': False, 'command': ''}),
        dcc.Store(id='terminal-password-state', data={'waiting': False, 'original_command': ''}, storage_type='memory'),
        
        dcc.Interval(id='terminal-streaming-interval', interval=100, disabled=True, n_intervals=0),
        
        html.Div([
            # ── Header: ADMX2001 · Connected — ttyUSB0 ──
            html.Div([
                # Traffic lights
                html.Div([
                    html.Button(html.I(className="fas fa-minus"), id="terminal-minimize-btn", className="window-control-btn window-btn-minimize", title="", **{'data-i18n-title': 'ui.minimize'}),
                    html.Button(html.I(className="fas fa-expand"), id="terminal-maximize-btn", className="window-control-btn window-btn-maximize", title="", **{'data-i18n-title': 'ui.max_restore'}),
                    html.Button(html.I(className="fas fa-times"), id="terminal-close-btn", className="window-control-btn window-btn-close", title="", **{'data-i18n-title': 'ui.close_esc'}),
                ], className="window-controls"),
                
                # Title: ZORIA · ADMX2001 · status — port
                html.Div([
                    html.Span("◈ ", className="title-mark"),
                    html.Span("ZORIA", className="title-system"),
                    html.Span(" · ", className="title-sep"),
                    html.Span("ADMX2001", className="title-device"),
                    html.Span(" · ", className="title-sep"),
                    html.Span("", id="terminal-status-text", className="title-status"),
                    html.Span(" — ", className="title-sep"),
                    html.Span("", id="terminal-port-label", className="title-port"),
                ], className="window-title"),
            ], className="window-header", id="terminal-header-drag"),
            
            # ── Status Bar: 4 telemetry badges ──
            html.Div([
                html.Span([
                    html.Span(className="terminal-badge-dot"),
                    html.Span("con", className="terminal-badge-label"),
                    html.Span("", id="badge-connection-value", className="terminal-badge-value"),
                ], className="terminal-status-badge", id="badge-connection", **{'data-state': 'idle'}),
                
                html.Span("\u00b7", className="terminal-status-sep"),
                
                html.Span([
                    html.Span(className="terminal-badge-dot"),
                    html.Span("port", className="terminal-badge-label"),
                    html.Span("\u2014", id="badge-port-value", className="terminal-badge-value"),
                ], className="terminal-status-badge", id="badge-port", **{'data-state': 'idle'}),
                
                html.Span("\u00b7", className="terminal-status-sep"),
                
                html.Span([
                    html.Span(className="terminal-badge-dot"),
                    html.Span("baud", className="terminal-badge-label"),
                    html.Span("\u2014", id="badge-baud-value", className="terminal-badge-value"),
                ], className="terminal-status-badge", id="badge-baud", **{'data-state': 'idle'}),
                
                html.Span("\u00b7", className="terminal-status-sep"),
                
                html.Span([
                    html.Span(className="terminal-badge-dot"),
                    html.Span("sweep", className="terminal-badge-label"),
                    html.Span("\u2014", id="badge-sweep-value", className="terminal-badge-value"),
                ], className="terminal-status-badge", id="badge-sweep", **{'data-state': 'idle'}),
            ], className="terminal-status-bar"),
            
            # ── Body (screen + input) ──
            html.Div([
                # Output
                html.Div([
                    html.Div(
                        id="command-output",
                        className="terminal-float-screen",
                        children=[
                            # Banner — Scientific instrument identity
                            html.Div([
                                html.Div([
                                    html.Span("◈", className="terminal-banner-mark"),
                                    html.Span("ZORIA", className="terminal-banner-system"),
                                    html.Span(" Runtime", className="terminal-banner-runtime-label"),
                                ], className="terminal-banner-identity"),
                                html.Div("Impedance Analysis Runtime", className="terminal-banner-subtitle"),
                                html.Div([
                                    html.Span("ADMX2001", className="terminal-banner-device"),
                                    html.Span(" · ", className="terminal-banner-sep"),
                                    html.Span("Analog Devices", className="terminal-banner-meta-text"),
                                    html.Span(" · ", className="terminal-banner-sep"),
                                    html.Span("Evaluation Board", className="terminal-banner-meta-text"),
                                ], className="terminal-banner-meta"),
                            ], className="terminal-banner"),
                            html.Div([
                                # Runtime init
                                html.Div([
                                    html.Span("◌ ", className="t-spinner t-spinner-think"),
                                    html.Span("runtime", className="t-cmd"),
                                    html.Span(".initialize", className="t-arg"),
                                    html.Span(" — acquisition layer", className="t-arg"),
                                ], className="terminal-line t-role-runtime"),
                                html.Div([
                                    html.Span("◦ ", style={'color': 'var(--t-text-disabled)', 'marginRight': '4px'}),
                                    html.Span("", className="t-arg", **{'data-i18n': 'ui.waiting_connection'})
                                ], className="terminal-line mb-2"),
                                
                                # Operational primitives
                                html.Div([
                                    html.Span("", className="t-role-section", **{'data-i18n': 'ui.available_commands'})
                                ], className="terminal-line mb-2"),
                                html.Div([
                                    html.Span("› ", className="t-prompt-mini"),
                                    html.Code("help", className="terminal-code"),
                                    html.Span("", className="t-role-label", **{'data-i18n': 'term.help_list_cmds'})
                                ], className="terminal-line"),
                                html.Div([
                                    html.Span("› ", className="t-prompt-mini"),
                                    html.Code("z", className="terminal-code"),
                                    html.Span("", className="t-role-label", **{'data-i18n': 'term.help_measure'})
                                ], className="terminal-line t-role-measurement"),
                                html.Div([
                                    html.Span("› ", className="t-prompt-mini"),
                                    html.Code("status", className="terminal-code"),
                                    html.Span("", className="t-role-label", **{'data-i18n': 'term.help_status'})
                                ], className="terminal-line"),
                                html.Div([
                                    html.Span("› ", className="t-prompt-mini"),
                                    html.Code("sweep", className="terminal-code"),
                                    html.Span("", className="t-role-label", **{'data-i18n': 'term.help_sweep'})
                                ], className="terminal-line mb-2"),
                                # Keyboard shortcuts
                                html.Div([
                                    html.Span("", className="t-arg me-2", **{'data-i18n': 'ui.shortcuts_label'}),
                                    html.Span("Alt+T", className="terminal-kbd"),
                                    html.Span("", className="t-arg me-2", **{'data-i18n': 'ui.open_close'}),
                                    html.Span("↑↓", className="terminal-kbd"),
                                    html.Span("", className="t-arg", **{'data-i18n': 'ui.history'})
                                ], className="terminal-line t-role-meta"),
                            ], className="terminal-content-area")
                        ]
                    )
                ], className="window-body", style={'background': 'var(--t-bg-layer2)'}),
                
                # Input line
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span("›", className="terminal-prompt-icon")
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
                        
                        html.Span("_", className="terminal-cursor", id="terminal-cursor")
                    ], className="terminal-input-wrapper d-flex align-items-center")
                ], className="terminal-float-input-area"),
                
                # ── Footer: grouped buttons with labels ──
                html.Div([
                    html.Div([
                        # Left group: action buttons
                        html.Div([
                            html.Button([
                                html.I(className="fas fa-bolt"),
                                html.Span("z", className="btn-label")
                            ], id="quick-measure-btn", className="terminal-float-quick-btn", title="z"),
                            html.Button([
                                html.I(className="fas fa-question"),
                                html.Span("help", className="btn-label")
                            ], id="quick-help-btn", className="terminal-float-quick-btn", title="help"),
                            html.Button([
                                html.I(className="fas fa-chart-bar"),
                                html.Span("status", className="btn-label")
                            ], id="quick-status-btn", className="terminal-float-quick-btn", title="status"),
                            html.Button([
                                html.I(className="fas fa-code-branch"),
                                html.Span("ver", className="btn-label")
                            ], id="quick-version-btn", className="terminal-float-quick-btn", title="version"),
                        ], className="terminal-footer-group-left"),
                        
                        html.Div(className="terminal-footer-divider"),
                        
                        # Right group: utility buttons
                        html.Div([
                            html.Button([
                                html.I(className="fas fa-trash-alt"),
                                html.Span("clear", className="btn-label")
                            ], id="clear-terminal-btn", className="terminal-float-quick-btn", title="", **{'data-i18n-title': 'footer.clear'}),
                            html.Button([
                                html.I(className="fas fa-download"),
                                html.Span("export", className="btn-label")
                            ], id="export-terminal-btn", className="terminal-float-quick-btn", title="", **{'data-i18n-title': 'ui.export'}),
                        ], className="terminal-footer-group-right"),
                    ], className="terminal-float-footer-inner d-flex align-items-center")
                ], className="terminal-float-footer")
            ], className="window-body"),
            
            # Resize handle
            html.Div(className="window-resize-handle")
        ], 
        id=MODAL_ID,
        className='draggable-window terminal-window',
        **{'data-system-state': 'disconnected'},
        style={'display': 'none', 'visibility': 'visible', 'opacity': '1'}
        )
    ])