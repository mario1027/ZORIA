"""
Mobile Navigation Component - Navegación móvil optimizada
Incluye: navbar colapsable, header del sidebar, controles claros
"""
from dash import html
from ..icons.hero import ICON

def mobileNavBar():
    """
    Barra de navegación móvil con logo y botón de menú desplegable.
    Solo visible en pantallas pequeñas (< 992px).
    
    Returns:
        html.Nav: Componente navbar para móvil con branding y toggle.
    """
    return html.Nav([
        # Logo/Brand con título descriptivo
        html.A([
            html.Img(
                src='/assets/logo.png', 
                alt='ZORIA - Impedance Analysis Platform',
                title='',
                **{'data-i18n-title': 'ui.brand_title'},
                style={'height': '32px', 'width': 'auto'}
            )
        ], className='navbar-brand me-lg-5', href='/', title='', **{'data-i18n-title': 'ui.go_dashboard'}),
        
        # Contenedor de controles
        html.Div([
            # Botón burger mejorado con tooltip
            html.Button([
                html.Span(className='navbar-toggler-icon')
            ], 
            className='navbar-toggler d-lg-none collapsed', 
            type='button',
            title='',
            **{'data-i18n-title': 'ui.open_menu'},
            **{
                'data-bs-toggle': 'collapse', 
                'data-bs-target': '#sidebarMenu',
                'aria-controls': 'sidebarMenu',
                'aria-expanded': 'false',
                'aria-label': 'Toggle navigation'
            })
        ], className='d-flex align-items-center')
    ], className='navbar navbar-dark navbar-theme-primary px-4 col-12 d-lg-none')


def mobileSidebarHeader():
    """
    Encabezado del sidebar móvil con cierre y acciones rápidas.
    Incluye botón de cierre [X] y botón de navegación.
    
    Returns:
        html.Div: Componente de header del sidebar móvil.
    """
    return html.Div([
        # Sección de acciones (botón de inicio rápido)
        html.Div([
            html.Div([
                html.A([
                    html.I(className='fas fa-home me-2'),
                    "Ir a Dashboard"
                ], 
                href='/', 
                className='btn btn-primary btn-sm d-inline-flex align-items-center',
                title='',
                **{'data-i18n-title': 'ui.back_dashboard'})
            ], className='d-block')
        ], className='d-flex align-items-center'),

        # Botón de cierre [X] con tooltip descriptivo
        html.Div([
            html.A([
                ICON.CROSS,
            ], 
            href='#sidebarMenu', 
            title='',
            **{'data-i18n-title': 'ui.close_menu'},
            **{
                'data-bs-toggle': 'collapse',
                'aria-label': 'Cerrar menú'
            })
        ], className='collapse-close d-md-none')

    ], className='user-card d-flex d-md-none align-items-center justify-content-between justify-content-md-center pb-4')

