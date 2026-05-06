"""
Footer ZORIA - Pie de página premium oscuro con detalles dorados
Diseño elegante de 4 columnas con tema dark/gold
"""
from dash import html, dcc

def footer():
    """
    Footer premium con tema oscuro y detalles dorados.
    """
    return html.Footer(
        [
            html.Div(
                [
                    # Separador superior con gradiente
                    html.Div(className="footer-top-line"),
                    html.Div(
                        [
                            # Columna 1: Logo y descripción
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Img(
                                                src="/assets/logo.png",
                                                alt="ZORIA",
                                                style={
                                                    'height': '50px',
                                                    'width': 'auto',
                                                    'objectFit': 'contain',
                                                    'marginBottom': '1.5rem',
                                                    'filter': 'drop-shadow(0 0 10px rgba(212, 175, 55, 0.3))'
                                                }
                                            ),
                                            html.P(
                                                '',
                                                **{'data-i18n': 'footer.description'},
                                                style={
                                                    'color': '#4b5563',
                                                    'fontSize': '0.95rem',
                                                    'lineHeight': '1.7',
                                                    'marginBottom': '1.5rem'
                                                }
                                            ),
                                            html.Div(
                                                [
                                                    html.Span(
                                                        "v1.3.2",
                                                        style={
                                                            'background': 'linear-gradient(135deg, #d4af37, #b8941f)',
                                                            'color': '#0f172a',
                                                            'padding': '0.4rem 0.9rem',
                                                            'borderRadius': '6px',
                                                            'fontSize': '0.75rem',
                                                            'fontWeight': '600',
                                                            'letterSpacing': '0.5px'
                                                        }
                                                    ),
                                                    html.Span(
                                                        "MIT",
                                                        style={
                                                            'background': 'rgba(212, 175, 55, 0.12)',
                                                            'border': '1px solid rgba(212, 175, 55, 0.35)',
                                                            'color': '#7c5b00',
                                                            'padding': '0.4rem 0.9rem',
                                                            'borderRadius': '6px',
                                                            'fontSize': '0.75rem',
                                                            'fontWeight': '600',
                                                            'marginLeft': '0.5rem'
                                                        }
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ],
                                className='col-lg-4 col-md-6 mb-5 mb-lg-0'
                            ),
                            # Columna 2: Navegación
                            html.Div(
                                [
                                    html.H6(
                                        html.Span('', **{'data-i18n': 'footer.navigation'}),
                                        style={
                                            'color': '#0f172a',
                                            'fontSize': '0.85rem',
                                            'fontWeight': '700',
                                            'letterSpacing': '1.5px',
                                            'textTransform': 'uppercase',
                                            'marginBottom': '1.5rem'
                                        }
                                    ),
                                    html.Div(
                                        [
                                            html.A(
                                                [
                                                    html.I(
                                                        className="fas fa-chart-line me-3",
                                                        style={
                                                            'width': '20px',
                                                            'color': '#d4af37',
                                                            'fontSize': '1rem'
                                                        }
                                                    ),
                                                    html.Span("Dashboard", style={'fontSize': '0.95rem'})
                                                ],
                                                href="/",
                                                className="footer-link"
                                            ),
                                            html.A(
                                                [
                                                    html.I(
                                                        className="fas fa-calculator me-3",
                                                        style={
                                                            'width': '20px',
                                                            'color': '#d4af37',
                                                            'fontSize': '1rem'
                                                        }
                                                    ),
                                                    html.Span('', **{'data-i18n': 'footer.nav_simulator'}, style={'fontSize': '0.95rem'})
                                                ],
                                                href="/simulator",
                                                className="footer-link"
                                            ),
                                            html.A(
                                                [
                                                    html.I(
                                                        className="fas fa-cogs me-3",
                                                        style={
                                                            'width': '20px',
                                                            'color': '#d4af37',
                                                            'fontSize': '1rem'
                                                        }
                                                    ),
                                                    html.Span('', **{'data-i18n': 'footer.nav_calib'}, style={'fontSize': '0.95rem'})
                                                ],
                                                href="/calibration",
                                                className="footer-link"
                                            ),
                                            html.A(
                                                [
                                                    html.I(
                                                        className="fas fa-book me-3",
                                                        style={
                                                            'width': '20px',
                                                            'color': '#d4af37',
                                                            'fontSize': '1rem'
                                                        }
                                                    ),
                                                    html.Span('', **{'data-i18n': 'footer.nav_docs'}, style={'fontSize': '0.95rem'})
                                                ],
                                                href="/documentacion",
                                                className="footer-link"
                                            )
                                        ]
                                    )
                                ],
                                className='col-lg-2 col-md-6 col-6 mb-5 mb-lg-0'
                            ),
                            # Columna 3: Recursos
                            html.Div(
                                [
                                    html.H6(
                                        html.Span('', **{'data-i18n': 'footer.resources'}),
                                        style={
                                            'color': '#0f172a',
                                            'fontSize': '0.85rem',
                                            'fontWeight': '700',
                                            'letterSpacing': '1.5px',
                                            'textTransform': 'uppercase',
                                            'marginBottom': '1.5rem'
                                        }
                                    ),
                                    html.Div(
                                        [
                                            html.A(
                                                [
                                                    html.I(
                                                        className="fab fa-github me-3",
                                                        style={
                                                            'width': '20px',
                                                            'color': '#d4af37',
                                                            'fontSize': '1rem'
                                                        }
                                                    ),
                                                    html.Span("GitHub", style={'fontSize': '0.95rem'})
                                                ],
                                                href="https://github.com/mario1027/ZORIA",
                                                target="_blank",
                                                className="footer-link"
                                            ),
                                            html.A(
                                                [
                                                    html.I(
                                                        className="fas fa-microchip me-3",
                                                        style={
                                                            'width': '20px',
                                                            'color': '#d4af37',
                                                            'fontSize': '1rem'
                                                        }
                                                    ),
                                                    html.Span("ADMX2001", style={'fontSize': '0.95rem'})
                                                ],
                                                href="https://www.analog.com/en/products/admx2001.html",
                                                target="_blank",
                                                className="footer-link"
                                            ),
                                            html.A(
                                                [
                                                    html.I(
                                                        className="fas fa-book-open me-3",
                                                        style={
                                                            'width': '20px',
                                                            'color': '#d4af37',
                                                            'fontSize': '1rem'
                                                        }
                                                    ),
                                                    html.Span("Wiki Analog", style={'fontSize': '0.95rem'})
                                                ],
                                                href="https://wiki.analog.com/eval-admx2001",
                                                target="_blank",
                                                className="footer-link"
                                            )
                                        ]
                                    )
                                ],
                                className='col-lg-2 col-md-6 col-6 mb-5 mb-lg-0'
                            ),
                            # Columna 4: Atajos de teclado
                            html.Div(
                                [
                                    html.H6(
                                        html.Span('', **{'data-i18n': 'footer.shortcuts'}),
                                        style={
                                            'color': '#0f172a',
                                            'fontSize': '0.85rem',
                                            'fontWeight': '700',
                                            'letterSpacing': '1.5px',
                                            'textTransform': 'uppercase',
                                            'marginBottom': '1.5rem'
                                        }
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Kbd("Alt", className="footer-kbd"),
                                                            html.Span("+", style={'color': '#9ca3af', 'margin': '0 0.4rem'}),
                                                            html.Kbd("T", className="footer-kbd")
                                                        ],
                                                        style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '0.4rem'}
                                                    ),
                                                    html.Span('', **{'data-i18n': 'footer.terminal'}, style={'color': '#4b5563', 'fontSize': '0.9rem'})
                                                ],
                                                style={'marginBottom': '1rem'}
                                            ),
                                            html.Div(
                                                [
                                                    html.Kbd("Esc", className="footer-kbd", style={'marginBottom': '0.4rem'}),
                                                    html.Span('', **{'data-i18n': 'footer.close'}, style={'color': '#4b5563', 'fontSize': '0.9rem'})
                                                ],
                                                style={'marginBottom': '1rem'}
                                            ),
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Kbd("Ctrl", className="footer-kbd"),
                                                            html.Span("+", style={'color': '#9ca3af', 'margin': '0 0.4rem'}),
                                                            html.Kbd("L", className="footer-kbd")
                                                        ],
                                                        style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '0.4rem'}
                                                    ),
                                                    html.Span('', **{'data-i18n': 'footer.clear'}, style={'color': '#4b5563', 'fontSize': '0.9rem'})
                                                ]
                                            )
                                        ]
                                    )
                                ],
                                className='col-lg-4 col-md-6'
                            )
                        ],
                        className='row align-items-start',
                        style={'paddingTop': '3rem', 'paddingBottom': '2rem'}
                    ),
                    # Separador inferior
                    html.Div(
                        style={
                            'height': '1px',
                            'background': 'rgba(15, 23, 42, 0.1)',
                            'margin': '0'
                        }
                    ),
                    # Barra inferior - Copyright y equipo
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                "© 2024-2026 ZORIA",
                                                style={
                                                    'color': '#4b5563',
                                                    'fontSize': '0.9rem'
                                                }
                                            ),
                                            html.Span(" · ", style={'color': '#9ca3af', 'margin': '0 0.5rem'}),
                                            html.A(
                                                "MIT License",
                                                href="https://opensource.org/licenses/MIT",
                                                target="_blank",
                                                style={
                                                    'color': '#7c5b00',
                                                    'textDecoration': 'none',
                                                    'fontSize': '0.9rem',
                                                    'transition': 'all 0.3s ease'
                                                },
                                                className="footer-license-link"
                                            )
                                        ],
                                        className='col-lg-6 text-center text-lg-start mb-3 mb-lg-0'
                                    ),
                                    html.Div(
                                        [
                                            html.Span(
                                                "Mario Montero · Juan Alvarez · Francisco Racedo",
                                                style={'color': '#4b5563', 'fontSize': '0.9rem'}
                                            ),
                                        ],
                                        className='col-lg-6 text-center'
                                    )
                                ],
                                className='row align-items-center',
                                style={'paddingTop': '1.5rem', 'paddingBottom': '1.5rem'}
                            )
                        ],
                        className='footer-content'
                    )
                ],
                className='footer-surface'
            )
        ],
        className='footer',
        style={
            'background': 'transparent',
            'width': '100%',
            'margin': '0',
            'padding': '0'
        }
    )