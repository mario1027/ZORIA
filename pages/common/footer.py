from dash import html, dcc

def footer():
    return html.Footer([
        html.Div([
            # Logo centrado
            html.Div([
                html.Img(
                    src="/assets/logo.png",
                    alt="Logo",
                    style={
                        'height': '30px',
                        'width': 'auto',
                        'objectFit': 'contain',
                        'marginBottom': '10px'
                    }
                )
            ], className='col-12 text-center mb-2'),
            
            # Enlaces de navegación
            html.Div([
                html.A("Dashboard", href="/", className="text-decoration-none mx-2"),
                " | ",
                html.A("Simulador", href="/simulator", className="text-decoration-none mx-2"),
                " | ",
                html.A("Calibración", href="/calibration", className="text-decoration-none mx-2"),
                " | ",
                html.A("Documentación", href="/documentacion", className="text-decoration-none mx-2"),
            ], className='col-12 text-center mb-2'),
            
            # About Me
            html.Div([
                html.P([
                    html.Strong("About Me:"),
                    " Desarrollado por Mario Ricardo Montero, Juan Carlos Alvarez y Francisco J. Racedo N.",
                ], className='mb-1 text-center text-muted small')
            ], className='col-12'),
            
            # Información de copyright
            html.Div([
                html.P([
                    "© 2026 ZORIA Dashboard & RLC Simulator. Todos los derechos reservados."
                ], className='mb-0 text-center text-muted small')
            ], className='col-12')
        ], className='row')
    ], className='footer bg-white border-top py-4 mt-auto w-100')
