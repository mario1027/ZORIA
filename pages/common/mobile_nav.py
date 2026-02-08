from dash import html
from ..icons.hero import ICON

def mobileNavBar():
    """ Mobile only navbar - Volt logo & burger button """
    return html.Nav([
        html.A([
            html.Img(src='/assets/logo.png', alt='ZORIA Logo', style={'height': '32px', 'width': 'auto'})
        ], className='navbar-brand me-lg-5', href='/'),
        html.Div([
            html.Button([
                # Burger button
                html.Span(className='navbar-toggler-icon')
            ], className='navbar-toggler d-lg-none collapsed', type='button',
               **{'data-bs-toggle': 'collapse', 'data-bs-target': '#sidebarMenu'})
        ], className='d-flex align-items-center')
    ], className='navbar navbar-dark navbar-theme-primary px-4 col-12 d-lg-none')


def mobileSidebarHeader():
    """ Mobile only sidebar header - Sign Out button + Close [X] """
    return html.Div([
        html.Div([
            html.Div([
                html.A([
                    html.I(className='fas fa-sign-out-alt me-2'),
                    "Cerrar Sesión"
                ], href='/', className='btn btn-secondary btn-sm d-inline-flex align-items-center')
            ], className='d-block')
        ], className='d-flex align-items-center'),

        # Sidebar close [X] icon
        html.Div([
            html.A([
                ICON.CROSS,
            ], href='#sidebarMenu', **{'data-bs-toggle': 'collapse'})
        ], className='collapse-close d-md-none')

    ], className='user-card d-flex d-md-none align-items-center justify-content-between justify-content-md-center pb-4')
