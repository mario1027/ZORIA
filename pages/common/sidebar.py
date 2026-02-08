"""
Sidebar compartido entre Dashboard ZORIA y Simulador RLC
Basado 100% en dash-plantilla VOLT Bootstrap 5
"""
from typing import List
from dash import html, dcc
from dash_spa import prefix
from .dropdown_folder_aoi import DropdownFolderContext, DropdownFolderAIO, SidebarNavItem, dropdownFolderEntry
from ..icons.hero import ICON
from .mobile_nav import mobileSidebarHeader

# Constantes de configuración
SIDEBAR_ITEMS = [
    {
        "text": "Dashboard",
        "icon": ICON.CHART_PIE,
        "href": "/"
    },
    {
        "text": "Calibración",
        "icon": ICON.GEAR,
        "href": "/calibration"
    },
    {
        "text": "Simulador RLC",
        "icon": ICON.VIEW_GRID,
        "href": "/simulator"
    },
    {
        "text": "Documentación",
        "icon": ICON.DOCUMENT,
        "href": "/documentacion"
    },
    {
        "text": "Terminal CLI",
        "icon": ICON.CONSOLE,
        "href": "#",
        "id": "sidebar-terminal-btn",
        "className": "nav-link"
    },
]

# Dropdowns vacíos por ahora
DROPDOWN_ITEMS = []

# Funciones auxiliares
def create_sidebar_link(text, icon, href, hyperlink=False, target="", **kwargs):
    """
    Crea un enlace en la barra lateral.

    Args:
        text (str): Texto del enlace.
        icon: Ícono asociado al enlace.
        href (str): Ruta del enlace.
        hyperlink (bool, opcional): Si el enlace debe ser un `html.A`. Por defecto es `False`.
        target (str, opcional): Target del enlace. Por defecto es una cadena vacía.
        **kwargs: Atributos adicionales como data-bs-toggle, data-bs-target, id, etc.

    Returns:
        SidebarNavItem: Componente de enlace para la barra lateral.
    """
    # Si hay atributos Bootstrap (data-bs-*) o un id específico, forzar el uso de html.A
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
    
    # Agregar atributos adicionales
    attributes.update(kwargs)

    children = [
        html.Span(icon, className="sidebar-icon"),
        html.Span(text, className="mt-1 ms-1 sidebar-text")
    ]

    el = element(children, **attributes)

    return SidebarNavItem(el, href=href)


def create_dropdown(title, icon, entries, id_suffix):
    """
    Crea un dropdown dinámico en la barra lateral.

    Args:
        title (str): Título del dropdown.
        icon: Ícono asociado al dropdown.
        entries (list): Lista de entradas en el dropdown.
        id_suffix (str): Sufijo para generar un ID único.

    Returns:
        DropdownFolderAIO: Componente de dropdown.
    """
    pid = prefix('sidebar')
    dropdown_entries = [dropdownFolderEntry(item["text"], item["href"]) for item in entries]
    return DropdownFolderAIO(dropdown_entries, title, icon, id=pid(id_suffix))

# Componente de Panel de Conexión mejorado para el Sidebar
def connection_panel():
    """
    Panel de conexión integrado en el sidebar con información clara del estado.
    Diseño compacto con indicador de estado visual y controles rápidos.
    """
    return html.Div([
        # Separador visual elegante
        html.Hr(className="sidebar-divider my-3 opacity-25"),
        
        # Header de la sección con icono
        html.Div([
            html.Div([
                html.I(className="fas fa-plug me-2 text-muted"),
                html.Small("CONEXIÓN DISPOSITIVO", className="sidebar-section-label text-uppercase text-muted fw-bold")
            ], className="d-flex align-items-center")
        ], className="px-3 mb-2"),
        
        # Tarjeta de estado compacta con diseño mejorado
        html.Div([
            # Fila superior: Indicador pulsante + Información
            html.Div([
                html.Div([
                    html.Span(className="connection-pulse", id="sidebar-connection-dot"),
                ], className="connection-indicator-wrapper"),
                html.Div([
                    html.Span("Desconectado", className="connection-status-text fw-bold", id="sidebar-connection-text"),
                    html.Small("ADMX2001 - Esperando conexión", className="connection-device-id d-block text-muted small", 
                             id="sidebar-device-port"),
                ], className="connection-info ms-2 flex-grow-1"),
            ], className="connection-status-row d-flex align-items-center mb-3"),
            
            # Botones de acción compactos con tooltips claros
            html.Div([
                html.Button([
                    html.I(className="fas fa-bolt me-1 d-none d-lg-inline"),
                    html.Span("Conectar", className="d-none d-xl-inline")
                ], 
                id="sidebar-quick-connect-btn",
                className="btn btn-success btn-sm connection-btn flex-grow-1",
                title="Conexión rápida al último puerto usado"
                ),
                html.Button([
                    html.I(className="fas fa-cog")
                ], 
                id="sidebar-config-btn",
                className="btn btn-secondary btn-sm connection-btn",
                title="Configurar puerto y parámetros"
                ),
                html.Button([
                    html.I(className="fas fa-power-off")
                ], 
                id="sidebar-disconnect-btn",
                className="btn btn-outline-danger btn-sm connection-btn",
                title="Desconectar dispositivo",
                disabled=True
                ),
            ], className="connection-actions d-flex gap-1"),
            
        ], className="connection-panel-card bg-dark p-3 mx-2 mb-2 rounded border border-secondary"),
        
    ], className="sidebar-connection-section")


# Sidebar principal
@DropdownFolderContext.Provider()
def sideBar():
    """
    Construye la barra lateral principal.

    Returns:
        html.Nav: Componente HTML representando la barra lateral.
    """
    return html.Nav([
        html.Div([
            # Logo/Brand del sidebar (visible en desktop)
            dcc.Link([
                html.Img(
                    src="/assets/logo.png",
                    alt="Logo",
                    style={
                        'height': '40px',
                        'width': 'auto',
                        'objectFit': 'contain'
                    }
                )
            ], href="/", className="sidebar-brand d-none d-lg-flex align-items-center justify-content-center px-3 py-4 border-bottom border-secondary"),
            
            mobileSidebarHeader(),
            
            # Contenedor flexible para navegación + panel de conexión
            html.Div([
                # Navegación principal
                html.Ul(
                    [
                        # Enlaces individuales
                        *[create_sidebar_link(**item) for item in SIDEBAR_ITEMS],

                        # Dropdowns dinámicos (vacío por ahora)
                        *[create_dropdown(item["title"], item["icon"], item["entries"], item["id_suffix"]) 
                          for item in DROPDOWN_ITEMS]
                    ],
                    className="nav flex-column pt-3 pt-md-0"
                ),
                
                # Panel de conexión (al final del sidebar)
                connection_panel(),
                
            ], className="sidebar-content d-flex flex-column", 
               style={'height': 'calc(100vh - 90px)', 'overflowY': 'auto'}),
            
        ], className="sidebar-inner px-4 pt-3 h-100")
    ], id="sidebarMenu", className="sidebar d-lg-block sidebar-dark text-white collapse")
