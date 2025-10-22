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
            
            # Información de copyright
            html.Div([
                html.P([
                    "© 2024 ADMX2001 Dashboard & RLC Simulator. ",
                    html.A("Documentación", href="/docs", className="text-decoration-none ms-2"),
                    " | ",
                    html.A("Soporte", href="/support", className="text-decoration-none ms-2")
                ], className='mb-0 text-center text-muted')
            ], className='col-12')
        ], className='row')
    ], className='footer bg-white border-top py-4 mt-auto w-100')
