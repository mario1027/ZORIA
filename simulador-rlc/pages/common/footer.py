from dash import html, dcc

def footer():
    return  html.Footer([
        html.Div([
            html.Div([
                html.P([
                    "© 2025 ",
                    html.Span("Grupo GEOEL", className='text-primary fw-bold me-2'),
                    html.Br(),
                    html.Small([
                        "Espectroscopía Óptica y Emisión Láser",
                        html.Br(),
                        "Universidad del Atlántico"
                    ], className='text-muted')
                ], className='mb-0 text-center text-lg-start')
            ], className='col-12 col-md-6 col-xl-8 mb-4 mb-md-0'),
            html.Div([
                html.Ul([
                    html.Li([
                        dcc.Link("Universidad del Atlántico", href='https://www.uniatlantico.edu.co', target='_blank', className='text-decoration-none')
                    ], className='list-inline-item px-0 px-sm-2'),
                    html.Li([
                        dcc.Link("Grupo GEOEL", href='#', className='text-decoration-none')
                    ], className='list-inline-item px-0 px-sm-2'),
                    html.Li([
                        dcc.Link("Simulador RLC", href='/', className='text-decoration-none')
                    ], className='list-inline-item px-0 px-sm-2')
                ], className='list-inline list-group-flush list-group-borderless text-md-end mb-0')
            ], className='col-12 col-md-6 col-xl-4 text-center text-lg-start')
        ], className='row')
    ], className='bg-white rounded shadow p-5 mb-4 mt-4')
