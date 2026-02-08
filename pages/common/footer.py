"""
Footer Component - Pie de página con navegación, ayuda y versión
"""
from dash import html, dcc

def footer():
    """
    Componente footer con navegación, enlaces útiles, atajos de teclado y versión.
    
    Returns:
        html.Footer: Componente HTML del pie de página.
    """
    return html.Footer([
        html.Div([
            # Logo + Versión
            html.Div([
                html.Div([
                    html.Img(
                        src="/assets/logo.png",
                        alt="ZORIA",
                        style={
                            'height': '32px',
                            'width': 'auto',
                            'objectFit': 'contain',
                            'marginBottom': '8px'
                        }
                    ),
                    html.Div([
                        html.Span("v1.3.2", className="badge bg-primary ms-2"),
                    ])
                ], className='d-flex align-items-center justify-content-center')
            ], className='col-12 text-center mb-3'),
            
            # Enlaces de navegación
            html.Div([
                html.A([
                    html.I(className="fas fa-home me-1"),
                    "Dashboard"
                ], href="/", className="text-decoration-none mx-2"),
                html.Span("·", className="text-muted mx-1"),
                html.A([
                    html.I(className="fas fa-wave-square me-1"),
                    "Simulador"
                ], href="/simulator", className="text-decoration-none mx-2"),
                html.Span("·", className="text-muted mx-1"),
                html.A([
                    html.I(className="fas fa-tools me-1"),
                    "Calibración"
                ], href="/calibration", className="text-decoration-none mx-2"),
                html.Span("·", className="text-muted mx-1"),
                html.A([
                    html.I(className="fas fa-book me-1"),
                    "Documentación"
                ], href="/documentacion", className="text-decoration-none mx-2"),
            ], className='col-12 text-center mb-3'),
            
            # Enlaces externos y recursos
            html.Div([
                html.Div([
                    html.A([
                        html.I(className="fab fa-github me-1"),
                        "GitHub"
                    ], href="https://github.com/mario1027/ZORIA", target="_blank", 
                       className="text-decoration-none mx-2"),
                    html.Span("·", className="text-muted mx-1"),
                    html.A([
                        html.I(className="fas fa-microchip me-1"),
                        "ADMX2001"
                    ], href="https://www.analog.com/en/products/admx2001.html", target="_blank", 
                       className="text-decoration-none mx-2"),
                    html.Span("·", className="text-muted mx-1"),
                    html.A([
                        html.I(className="fas fa-book-open me-1"),
                        "Wiki ADI"
                    ], href="https://wiki.analog.com/eval-admx2001", target="_blank", 
                       className="text-decoration-none mx-2"),
                ], className="mb-2"),
            ], className='col-12 text-center mb-3 small'),
            
            # Atajos de teclado
            html.Div([
                html.Div([
                    html.I(className="fas fa-keyboard me-2 text-primary"),
                    html.Span("Atajos: ", className="text-muted fw-bold"),
                    html.Kbd("Ctrl+`", className="mx-1", style={"fontSize": "0.75rem"}),
                    html.Span("Terminal", className="text-muted small me-3"),
                    html.Kbd("ESC", className="mx-1", style={"fontSize": "0.75rem"}),
                    html.Span("Cerrar", className="text-muted small"),
                ], className='d-flex align-items-center justify-content-center mb-2')
            ], className='col-12 text-center mb-3'),
            
            # Equipo de desarrollo
            html.Div([
                html.P([
                    html.Strong("Equipo:"),
                    " Mario Ricardo Montero · Juan Carlos Alvarez · Francisco J. Racedo N.",
                ], className='mb-2 text-center text-muted small')
            ], className='col-12'),
            
            # Copyright
            html.Div([
                html.P([
                    html.I(className="far fa-copyright me-1"),
                    "2024-2026 ZORIA. Todos los derechos reservados.",
                ], className='mb-1 text-center text-muted small'),
                html.P([
                    html.Small([
                        "Powered by ",
                        html.A("Dash", href="https://dash.plotly.com", target="_blank", className="text-decoration-none"),
                        " + ",
                        html.A("Plotly", href="https://plotly.com", target="_blank", className="text-decoration-none"),
                    ], className="text-muted")
                ], className='mb-0 text-center')
            ], className='col-12')
        ], className='row')
    ], className='footer bg-white border-top py-4 mt-auto w-100')
