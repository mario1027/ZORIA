"""
Sidebar compartido entre Dashboard ZORIA y Simulador RLC
Basado 100% en dash-plantilla VOLT Bootstrap 5
Versión mejorada con descripciones claras y organización profesional
"""
from typing import List
from dash import html, dcc
from dash_spa import prefix
from .dropdown_folder_aoi import DropdownFolderContext, DropdownFolderAIO, SidebarNavItem, dropdownFolderEntry
from ..icons.hero import ICON
from .mobile_nav import mobileSidebarHeader

# Constantes de configuración con descripciones completas
SIDEBAR_ITEMS = [
    {
        "text": "Dashboard",
        "icon": ICON.CHART_PIE,
        "href": "/",
        "description": "Panel principal de mediciones en tiempo real",
        "badge": None
    },
    {
        "text": "Calibración",
        "icon": ICON.GEAR,
        "href": "/calibration",
        "description": "Procedimientos de calibración Open-Short-Load",
        "badge": None
    },
    {
        "text": "Simulador RLC",
        "icon": ICON.VIEW_GRID,
        "href": "/simulator",
        "description": "Calculadora de circuitos y impedancias teóricas",
        "badge": None
    },
    {
        "text": "Documentación",
        "icon": ICON.DOCUMENT,
        "href": "/documentacion",
        "description": "Guías completas y procedimientos detallados",
        "badge": "New"
    },
    {
        "text": "Terminal CLI",
        "icon": ICON.CONSOLE,
        "href": "#",
        "id": "sidebar-terminal-btn",
        "className": "nav-link",
        "description": "Interfaz de línea de comandos integrada",
        "badge": None
    },
]

# Dropdowns vacíos por ahora - se pueden agregar más secciones después
DROPDOWN_ITEMS = []

# Funciones auxiliares
def create_sidebar_link(text, icon, href, description="", badge=None, hyperlink=False, target="", **kwargs):
    """
    Crea un enlace mejorado en la barra lateral con tooltip y badge opcional.

    Args:
        text (str): Texto del enlace.
        icon: Ícono asociado al enlace.
        href (str): Ruta del enlace.
        description (str): Descripción para tooltip.
        badge (str, opcional): Texto del badge (ej: "New", "Beta").
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
        "className": kwargs.pop('className', 'nav-link'),
        "title": description  # Tooltip nativo
    }
    if target:
        attributes["target"] = target
    
    # Agregar atributos adicionales
    attributes.update(kwargs)

    # Construir children con badge opcional
    children = [
        html.Span(icon, className="sidebar-icon"),
        html.Span(text, className="mt-1 ms-1 sidebar-text")
    ]
    
    if badge:
        children.append(
            html.Span(badge, className="badge bg-primary rounded-pill ms-auto", 
                     style={"fontSize": "0.65rem", "padding": "0.25em 0.5em"})
        )

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


# Componente de Información y Ayuda Rápida
def sidebar_footer_info():
    """
    Sección informativa al pie del sidebar con versión, links útiles y ayuda rápida.
    """
    return html.Div([
        # Separador
        html.Hr(className="sidebar-divider my-3 opacity-25"),
        
        # Ayuda rápida
        html.Div([
            html.Div([
                html.I(className="fas fa-question-circle me-2 text-primary"),
                html.Small("AYUDA RÁPIDA", className="text-uppercase text-muted fw-bold")
            ], className="d-flex align-items-center mb-2"),
            
            html.Div([
                # Links de ayuda compactos
                html.Small([
                    html.A([
                        html.I(className="fas fa-book me-1"),
                        "Docs"
                    ], href="/documentacion", className="text-decoration-none text-muted hover-primary"),
                    html.Span(" • ", className="text-muted mx-1"),
                    html.A([
                        html.I(className="fas fa-external-link-alt me-1"),
                        "Wiki"
                    ], href="https://wiki.analog.com/resources/eval/user-guides/admx/eval-admx2001ebz", 
                       target="_blank", className="text-decoration-none text-muted hover-primary"),
                    html.Span(" • ", className="text-muted mx-1"),
                    html.A([
                        html.I(className="fab fa-github me-1"),
                        "GitHub"
                    ], href="https://github.com/mario1027/ZORIA", 
                       target="_blank", className="text-decoration-none text-muted hover-primary"),
                ], className="d-block")
            ], className="mb-2"),
            
            # Atajos de teclado
            html.Small([
                html.Span([
                    html.Kbd("Ctrl", className="kbd-key"),
                    html.Span("+", className="mx-1"),
                    html.Kbd("`", className="kbd-key"),
                ], className="me-2"),
                html.Span("Terminal", className="text-muted small")
            ], className="d-block"),
            
        ], className="px-3 mb-2"),
        
        # Versión y créditos
        html.Div([
            html.Div([
                html.Span("ZORIA", className="fw-bold text-white"),
                html.Span(" v1.3.2", className="text-muted ms-1"),
            ], className="mb-1 small"),
            html.Small([
                "© 2024-2026 ",
                html.A("ZORIA Team", href="https://github.com/mario1027/ZORIA", 
                      target="_blank", className="text-muted text-decoration-none")
            ], className="text-muted d-block", style={"fontSize": "0.7rem"}),
        ], className="px-3 py-2 bg-dark rounded mx-2 mb-2 border border-secondary"),
        
    ], className="sidebar-footer-info mt-auto pb-3")


# Sidebar principal mejorado
@DropdownFolderContext.Provider()
def sideBar():
    """
    Construye la barra lateral principal con organización clara y profesional.
    Incluye navegación, panel de conexión y sección informativa.

    Returns:
        html.Nav: Componente HTML representando la barra lateral completa.
    """
    return html.Nav([
        html.Div([
            # Logo/Brand del sidebar (visible en desktop) con título mejorado
            dcc.Link([
                html.Img(
                    src="/assets/logo.png",
                    alt="ZORIA Logo",
                    title="ZORIA - Impedance Analysis Platform",
                    style={
                        'height': '40px',
                        'width': 'auto',
                        'objectFit': 'contain'
                    }
                )
            ], href="/", className="sidebar-brand d-none d-lg-flex align-items-center justify-content-center px-3 py-4 border-bottom border-secondary"),
            
            mobileSidebarHeader(),
            
            # Contenedor flexible para toda la navegación
            html.Div([
                # Sección de navegación principal
                html.Div([
                    html.Ul(
                        [
                            # Enlaces individuales con descripciones mejoradas
                            *[create_sidebar_link(**item) for item in SIDEBAR_ITEMS],

                            # Dropdowns dinámicos (vacío por ahora, expandible en futuro)
                            *[create_dropdown(item["title"], item["icon"], item["entries"], item["id_suffix"]) 
                              for item in DROPDOWN_ITEMS]
                        ],
                        className="nav flex-column pt-3 pt-md-0"
                    ),
                ]),
                
                # Panel de conexión (espaciado automático)
                connection_panel(),
                
                # Footer informativo con ayuda y versión
                sidebar_footer_info(),
                
            ], className="sidebar-content d-flex flex-column", 
               style={'height': 'calc(100vh - 90px)', 'overflowY': 'auto', 'overflowX': 'hidden'}),
            
        ], className="sidebar-inner px-4 pt-3 h-100")
    ], id="sidebarMenu", className="sidebar d-lg-block sidebar-dark text-white collapse")
