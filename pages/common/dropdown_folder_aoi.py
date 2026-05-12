from typing import Dict, List
from dash import html, dcc
from dash.dependencies import Input, Output, State, ALL

from dash_spa import prefix, callback
from dash_spa.spa_context import createContext, ContextState, dataclass
from dash_spa.logging import log
from dash_spa.components.icons import ARROW

# Constantes
DEFAULT_CLASSNAME = 'multi-level collapse'


@dataclass
class DropdownFolderState(ContextState):
    """Representa el estado de un folder desplegable en la barra lateral."""
    className: str = DEFAULT_CLASSNAME
    arrowClass: str = 'link-arrow'  # Clase por defecto de la flecha


# Contexto global para DropdownFolder
DropdownFolderContext: Dict[str, DropdownFolderState] = createContext()


class SidebarNavItem(html.Li):
    """
    Componente de navegación lateral con manejo dinámico de clases 'active'.
    """

    def __init__(self, children, href: str, **kwargs):
        """
        Constructor del componente SidebarNavItem.

        Args:
            children: Contenido del componente.
            href (str): URL asociada al enlace.
        """
        # Agregar clase base 'nav-item' si no está presente
        className = kwargs.pop('className', 'nav-item')
        if 'nav-item' not in className:
            className += ' nav-item'

        # Inicializa el componente con un ID único basado en el href
        super().__init__(children, id={'type': 'sidebar-item', 'href': href}, className=className, **kwargs)


def dropdownFolderEntry(text: str, href: str) -> SidebarNavItem:
    """
    Crea una entrada en el dropdown de la barra lateral.

    Args:
        text (str): Texto del enlace.
        href (str): Ruta asociada al enlace.

    Returns:
        SidebarNavItem: Entrada en el dropdown.
    """
    return SidebarNavItem(
        [
            dcc.Link(
                [html.Span(text, className='sidebar-text')],
                className='nav-link',
                href=href
            )
        ],
        href=href
    )


class DropdownFolderAIO(html.Div):
    """
    Componente de carpeta desplegable para la barra lateral.

    Incluye ícono, texto y una flecha que permite expandir/contraer el contenido.
    """

    def __init__(self, children: List[SidebarNavItem], text: str, icon: html.Span, id: str = None):
        """
        Constructor del componente DropdownFolderAIO.

        Args:
            children (List[SidebarNavItem]): Lista de entradas dentro del folder.
            text (str): Título del folder.
            icon (html.Span): Ícono asociado.
            id (str, opcional): ID único para el folder.
        """
        pid = prefix(id)
        state, setState = DropdownFolderContext.useState(
            pid('state'),
            initial_state=DropdownFolderState(DEFAULT_CLASSNAME, 'link-arrow')
        )

        log.info(f'DropdownFolderAIO id={id}, initial state="{state.className}"')

        # Botón del folder
        button = html.Span(
            [
                html.Span(
                    [html.Span(icon, className='sidebar-icon'), html.Span(text, className='sidebar-text')]
                ),
                html.Span(ARROW, id=pid('arrow'), className=state.arrowClass)
            ],
            id=pid('btn'),
            className='nav-link collapsed d-flex justify-content-between align-items-center'
        )

        # Contenedor de las entradas del folder
        container = html.Div(
            [html.Ul(children, className='flex-column nav')],
            id=pid('container'),
            className=state.className,
            role='list'
        )

        # Callback para manejar la expansión/contracción del folder
        @DropdownFolderContext.On(button.input.n_clicks)
        def update_dropdown(n_clicks: int):
            if n_clicks is not None:
                state.className = (
                    state.className.replace(' collapse', '')
                    if 'collapse' in state.className
                    else state.className + ' collapse'
                )
                state.arrowClass = (
                    'link-arrow rotate' if 'collapse' not in state.className else 'link-arrow'
                )
                log.info(f'Updated DropdownFolderAIO id={id}, new state="{state.className}"')
            return state

        # Inicialización del componente base
        super().__init__(html.Li([button, container], className='nav-item'))


@callback(
    Output({'type': 'sidebar-item', 'href': ALL}, 'className'),
    Output({'type': 'dropdown-folder', 'id': ALL}, 'className'),
    Input('url', 'pathname'),
    State({'type': 'sidebar-item', 'href': ALL}, 'id'),
    State({'type': 'dropdown-folder', 'id': ALL}, 'id')
)
def update_active_class(pathname: str, item_ids: List[Dict], folder_ids: List[Dict]) -> List[str]:
    """
    Actualiza dinámicamente la clase del elemento de la barra lateral según la ruta activa.

    Args:
        pathname (str): Ruta actual del navegador.
        item_ids (list): Lista de IDs de los elementos de la barra lateral.
        folder_ids (list): Lista de IDs de los dropdowns.

    Returns:
        list, list: Lista de clases actualizadas para los elementos y los dropdowns.
    """
    updated_item_classes = []
    updated_folder_classes = []

    # Actualizar las clases de los elementos
    for item_id in item_ids:
        href = item_id['href']
        class_name = 'nav-item'
        # "/" solo activa en la raíz exacta; otras rutas usan prefix por segmento
        if href == '/':
            is_active = pathname == '/'
        else:
            is_active = pathname == href or pathname.startswith(href + '/')
        if is_active:
            class_name += ' active'
        updated_item_classes.append(class_name)

    # Actualizar las clases de los dropdowns
    for folder_id in folder_ids:
        folder_class = 'multi-level'
        for item_id in item_ids:
            href = item_id['href']
            if pathname.startswith(href) and folder_id['id'] in href:
                folder_class += ' collapse show'
        updated_folder_classes.append(folder_class)

    return updated_item_classes, updated_folder_classes
