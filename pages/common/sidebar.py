"""
Sidebar ZORIA - Navegación principal
"""
from typing import List
from dash import html, dcc
from dash_spa import prefix
from .dropdown_folder_aoi import DropdownFolderContext, DropdownFolderAIO, SidebarNavItem, dropdownFolderEntry
from ..icons.hero import ICON
from .mobile_nav import mobileSidebarHeader

SIDEBAR_ITEMS = [
    {"text": "Dashboard",     "icon": ICON.CHART_PIE, "href": "/",            "i18n": "nav.dashboard"},
    {"text": "Calibración",   "icon": ICON.GEAR,      "href": "/calibration", "i18n": "nav.calibration"},
    {"text": "Simulador RLC", "icon": ICON.VIEW_GRID,  "href": "/simulator",   "i18n": "nav.simulator"},
    {"text": "Configuración", "icon": html.I(className="fas fa-sliders-h"), "href": "/config", "i18n": "nav.config"},
    {"text": "Documentación", "icon": ICON.DOCUMENT,  "href": "/documentacion","i18n": "nav.documentation"},
    {"text": "Acerca de",     "icon": ICON.PEOPLE,    "href": "/about",        "i18n": "nav.about"},
    {"text": "Terminal CLI",  "icon": ICON.CONSOLE,   "href": "#",             "i18n": "nav.terminal",
     "id": "sidebar-terminal-btn", "className": "nav-link"},
]

DROPDOWN_ITEMS = []


def create_sidebar_link(text, icon, href, hyperlink=False, target="", i18n=None, **kwargs):
    """Crea un enlace en la barra lateral"""
    has_bootstrap_attrs = any(key.startswith('data-bs-') for key in kwargs.keys())
    has_id = 'id' in kwargs
    
    if has_bootstrap_attrs or hyperlink or has_id:
        element = html.A
    else:
        element = dcc.Link
    
    attributes = {
        "href": href, 
        "className": kwargs.pop('className', 'nav-link')
    }
    if target:
        attributes["target"] = target
    attributes.update(kwargs)

    text_span = html.Span(
        text,
        className="mt-1 ms-1 sidebar-text",
        **({'data-i18n': i18n} if i18n else {})
    )

    children = [
        html.Span(icon, className="sidebar-icon"),
        text_span,
    ]

    el = element(children, **attributes)
    return SidebarNavItem(el, href=href)


def create_dropdown(title, icon, entries, id_suffix):
    """Crea un dropdown dinámico"""
    pid = prefix('sidebar')
    dropdown_entries = [dropdownFolderEntry(item["text"], item["href"]) for item in entries]
    return DropdownFolderAIO(dropdown_entries, title, icon, id=pid(id_suffix))


def connection_panel():
    """Panel de conexión con los 3 botones clásicos"""
    return html.Div([
        html.Hr(className="sidebar-divider my-3 opacity-25"),
        
        html.Div([
            html.Small(
                "DISPOSITIVO",
                className="sidebar-section-label text-uppercase fw-bold",
                **{'data-i18n': 'conn.section_label'},
            )
        ], className="px-3 mb-2"),
        
        html.Div([
            # Fila superior: Indicador + Estado
            html.Div([
                html.Div([
                    html.Span(className="connection-pulse", id="sidebar-connection-dot"),
                ], className="connection-indicator-wrapper"),
                html.Div([
                    html.Span(
                        "Desconectado",
                        className="connection-status-text fw-bold",
                        id="sidebar-connection-text",
                    ),
                    html.Small(
                        "ADMX2001",
                        className="connection-device-id d-block",
                        id="sidebar-device-port",
                    ),
                ], className="connection-info ms-2 flex-grow-1"),
            ], className="connection-status-row d-flex align-items-center mb-3"),
            
            # Botones de conexión
            html.Div([
                html.Button([
                    html.I(className="fas fa-bolt"),
                ], 
                id="sidebar-quick-connect-btn",
                className="btn btn-conn-connect btn-sm connection-btn flex-fill",
                title="Conexión Rápida",
                **{'data-i18n-title': 'conn.quick_connect'},
                ),
                html.Button([
                    html.I(className="fas fa-cog"),
                ],
                id="sidebar-config-btn",
                className="btn btn-conn-config btn-sm connection-btn",
                title="Configurar",
                **{'data-i18n-title': 'conn.configure'},
                ),
                html.Button([
                    html.I(className="fas fa-power-off"),
                ], 
                id="sidebar-disconnect-btn",
                className="btn btn-conn-off btn-sm connection-btn",
                title="Desconectar",
                disabled=True,
                **{'data-i18n-title': 'conn.disconnect'},
                ),
            ], className="connection-actions d-flex gap-1"),
            
        ], className="connection-panel-card p-2 mx-2 mb-2 rounded border border-secondary"),
        
    ], className="sidebar-connection-section mt-auto")


@DropdownFolderContext.Provider()
def sideBar():
    """Sidebar principal"""
    return html.Nav([
        dcc.Location(id='url', refresh=False),
        html.Div([
            # Logo
            dcc.Link([
                html.Img(
                    src="/assets/logo.png",
                    alt="Logo",
                    style={'height': '40px', 'width': 'auto', 'objectFit': 'contain'}
                )
            ], href="/", className="sidebar-brand d-none d-lg-flex align-items-center justify-content-center px-3 py-3 border-bottom border-secondary"),
            
            mobileSidebarHeader(),
            
            # Contenedor principal
            html.Div([
                # Navegación
                html.Ul(
                    [
                        *[create_sidebar_link(**item) for item in SIDEBAR_ITEMS],
                        *[create_dropdown(item["title"], item["icon"], item["entries"], item["id_suffix"]) 
                          for item in DROPDOWN_ITEMS]
                    ],
                    className="nav flex-column pt-3 pt-md-0"
                ),
                
                # Panel de conexión
                connection_panel(),
                
            ], className="sidebar-content d-flex flex-column", style={'height': 'calc(100vh - 70px)', 'overflowY': 'auto'}),
            
        ], className="sidebar-inner px-4 pt-3 h-100")
    ], id="sidebarMenu", className="sidebar d-lg-block collapse")
