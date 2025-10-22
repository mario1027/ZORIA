"""
Sidebar compartido entre Dashboard ADMX2001 y Simulador RLC
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
    {"text": "Dashboard ADMX2001", "icon": ICON.CHART_PIE, "href": "/"},
    {"text": "Simulador RLC", "icon": ICON.VIEW_GRID, "href": "/simulator"},
]

# Dropdowns vacíos por ahora - se pueden agregar más secciones después
DROPDOWN_ITEMS = []

# Funciones auxiliares
def create_sidebar_link(text, icon, href, hyperlink=False, target=""):
    """
    Crea un enlace simple en la barra lateral.

    Args:
        text (str): Texto del enlace.
        icon: Ícono asociado al enlace.
        href (str): Ruta del enlace.
        hyperlink (bool, opcional): Si el enlace debe ser un `html.A`. Por defecto es `False`.
        target (str, opcional): Target del enlace. Por defecto es una cadena vacía.

    Returns:
        SidebarNavItem: Componente de enlace para la barra lateral.
    """
    element = html.A if hyperlink else dcc.Link
    attributes = {"href": href, "className": "nav-link"}
    if target:
        attributes["target"] = target

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
            html.Ul(
                [
                    # Enlaces individuales
                    *[create_sidebar_link(**item) for item in SIDEBAR_ITEMS],

                    # Dropdowns dinámicos (vacío por ahora)
                    *[create_dropdown(item["title"], item["icon"], item["entries"], item["id_suffix"]) for item in DROPDOWN_ITEMS]
                ],
                className="nav flex-column pt-3 pt-md-0"
            )
        ], className="sidebar-inner px-4 pt-3")
    ], id="sidebarMenu", className="sidebar d-lg-block bg-gray-800 text-white collapse")
