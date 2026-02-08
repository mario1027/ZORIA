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
        "text": "Dashboard ZORIA",
        "icon": ICON.CHART_PIE,
        "href": "/",
    },
    {
        "text": "Calibración",
        "icon": ICON.GEAR,  # Icono de ajustes/calibración
        "href": "/calibration",
    },
    {
        "text": "Simulador RLC",
        "icon": ICON.VIEW_GRID,
        "href": "/simulator",
    },
    {
        "text": "Documentación",
        "icon": ICON.DOCUMENT,
        "href": "/documentacion",
    },
    {
        "text": "Terminal CLI",
        "icon": ICON.CONSOLE,
        "href": "#",
        "id": "sidebar-terminal-btn",
        "className": "nav-link",
    },
]

# Dropdowns vacíos por ahora - se pueden agregar más secciones después
DROPDOWN_ITEMS = []

# Funciones auxiliares
def create_sidebar_link(text, icon, href, hyperlink=False, target="", **kwargs):
    """
    Crea un enlace simple en la barra lateral.

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
    
    attributes = {"href": href, "className": kwargs.pop('className', 'nav-link')}
    if target:
        attributes["target"] = target
    
    # Agregar atributos adicionales
    attributes.update(kwargs)

    el = element([
        html.Span(icon, className="sidebar-icon"),
        html.Span(text, className="mt-1 ms-1 sidebar-text")
    ], **attributes)

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

# Componente de Panel de Conexión para el Sidebar
def connection_panel():
    """
    Panel de conexión integrado en el sidebar.
    Diseño compacto con indicador de estado y controles rápidos.
    """
    return html.Div([
        # Separador visual
        html.Hr(className="sidebar-divider my-3 opacity-25"),
        
        # Header de la sección
        html.Div([
            html.Small("DISPOSITIVO", className="sidebar-section-label text-uppercase text-muted")
        ], className="px-3 mb-2"),
        
        # Tarjeta de estado compacta
        html.Div([
            # Fila superior: Indicador + Puerto
            html.Div([
                html.Div([
                    html.Span(className="connection-pulse", id="sidebar-connection-dot"),
                ], className="connection-indicator-wrapper"),
                html.Div([
                    html.Span("Desconectado", className="connection-status-text", id="sidebar-connection-text"),
                    html.Small("ADMX2001", className="connection-device-id d-block text-muted", id="sidebar-device-port"),
                ], className="connection-info ms-2 flex-grow-1"),
            ], className="connection-status-row d-flex align-items-center mb-2"),
            
            # Botones de acción compactos
            html.Div([
                html.Button([
                    html.I(className="fas fa-bolt")
                ], 
                id="sidebar-quick-connect-btn",
                className="btn btn-success btn-sm connection-btn",
                title="Conexión Rápida"
                ),
                html.Button([
                    html.I(className="fas fa-cog")
                ], 
                id="sidebar-config-btn",
                className="btn btn-gray-700 btn-sm connection-btn",
                title="Configurar Conexión"
                ),
                html.Button([
                    html.I(className="fas fa-power-off")
                ], 
                id="sidebar-disconnect-btn",
                className="btn btn-outline-danger btn-sm connection-btn",
                title="Desconectar",
                disabled=True
                ),
            ], className="connection-actions d-flex gap-1"),
            
        ], className="connection-panel-card p-3 mx-2 mb-3"),
        
    ], className="sidebar-connection-section mt-auto")


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
                        *[create_dropdown(item["title"], item["icon"], item["entries"], item["id_suffix"]) for item in DROPDOWN_ITEMS]
                    ],
                    className="nav flex-column pt-3 pt-md-0"
                ),
                
                # Panel de conexión (al final del sidebar)
                connection_panel(),
                
            ], className="sidebar-content d-flex flex-column", style={'height': 'calc(100vh - 90px)', 'overflowY': 'auto'}),
            
        ], className="sidebar-inner px-4 pt-3 h-100")
    ], id="sidebarMenu", className="sidebar d-lg-block sidebar-dark text-white collapse")
