"""
Footer ZORIA - Pie de página con tema dual (dark/light)
Diseño elegante de 4 columnas con estilos via CSS tokens.
"""
from dash import html, dcc

def footer():
    """
    Footer con tema dual. Los colores se gestionan via CSS custom properties
    en navigation.css y zoria-tokens.css.
    """
    return html.Footer(
        [
            html.Div(
                [
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
                                                className="footer-logo"
                                            ),
                                            html.P(
                                                '',
                                                **{'data-i18n': 'footer.description'},
                                                className="footer-description"
                                            ),
                                            html.Div(
                                                className="footer-badges",
                                                children=[
                                                    html.Span("v1.3.2", className="footer-version-badge"),
                                                    html.Span("MIT", className="footer-license-badge")
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
                                        className="footer-heading"
                                    ),
                                    html.Div(
                                        [
                                            html.A(
                                                [
                                                    html.I(className="fas fa-chart-line me-3 footer-icon"),
                                                    html.Span("Dashboard")
                                                ],
                                                href="/",
                                                className="footer-link"
                                            ),
                                            html.A(
                                                [
                                                    html.I(className="fas fa-calculator me-3 footer-icon"),
                                                    html.Span("Simulador RLC", **{'data-i18n': 'footer.nav_simulator'})
                                                ],
                                                href="/simulator",
                                                className="footer-link"
                                            ),
                                            html.A(
                                                [
                                                    html.I(className="fas fa-cogs me-3 footer-icon"),
                                                    html.Span("Calibración", **{'data-i18n': 'footer.nav_calib'})
                                                ],
                                                href="/calibration",
                                                className="footer-link"
                                            ),
                                            html.A(
                                                [
                                                    html.I(className="fas fa-book me-3 footer-icon"),
                                                    html.Span("Documentación", **{'data-i18n': 'footer.nav_docs'})
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
                                        className="footer-heading"
                                    ),
                                    html.Div(
                                        [
                                            html.A(
                                                [
                                                    html.I(className="fab fa-github me-3 footer-icon"),
                                                    html.Span("GitHub")
                                                ],
                                                href="https://github.com/mario1027/ZORIA",
                                                target="_blank",
                                                className="footer-link"
                                            ),
                                            html.A(
                                                [
                                                    html.I(className="fas fa-microchip me-3 footer-icon"),
                                                    html.Span("ADMX2001")
                                                ],
                                                href="https://www.analog.com/en/products/admx2001.html",
                                                target="_blank",
                                                className="footer-link"
                                            ),
                                            html.A(
                                                [
                                                    html.I(className="fas fa-book-open me-3 footer-icon"),
                                                    html.Span("Wiki Analog")
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
                                        className="footer-heading"
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Kbd("Alt", className="footer-kbd"),
                                                            html.Span("+", className="footer-kbd-sep"),
                                                            html.Kbd("T", className="footer-kbd")
                                                        ],
                                                        className="footer-kbd-row"
                                                    ),
                                                    html.Span("Terminal", **{'data-i18n': 'footer.terminal'}, className="footer-shortcut-text")
                                                ],
                                                className="footer-shortcut-item"
                                            ),
                                            html.Div(
                                                [
                                                    html.Kbd("Esc", className="footer-kbd footer-kbd-single"),
                                                    html.Span("Cerrar", **{'data-i18n': 'footer.close'}, className="footer-shortcut-text")
                                                ],
                                                className="footer-shortcut-item"
                                            ),
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Kbd("Ctrl", className="footer-kbd"),
                                                            html.Span("+", className="footer-kbd-sep"),
                                                            html.Kbd("L", className="footer-kbd")
                                                        ],
                                                        className="footer-kbd-row"
                                                    ),
                                                    html.Span("Limpiar", **{'data-i18n': 'footer.clear'}, className="footer-shortcut-text")
                                                ]
                                            )
                                        ]
                                    )
                                ],
                                className='col-lg-4 col-md-6'
                            )
                        ],
                        className='row align-items-start footer-columns'
                    ),
                    # Separador inferior
                    html.Div(className="footer-bottom-sep"),
                    # Barra inferior - Copyright y equipo
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span("© 2024-2026 ZORIA", className="footer-copyright"),
                                            html.Span(" · ", className="footer-copyright-sep"),
                                            html.A(
                                                "MIT License",
                                                href="https://opensource.org/licenses/MIT",
                                                target="_blank",
                                                className="footer-license-link"
                                            )
                                        ],
                                        className='col-lg-6 text-center text-lg-start mb-3 mb-lg-0'
                                    ),
                                    html.Div(
                                        [
                                            html.Span(
                                                "Mario Montero · Juan Alvarez · Francisco Racedo",
                                                className="footer-authors"
                                            ),
                                        ],
                                        className='col-lg-6 text-center'
                                    )
                                ],
                                className='row align-items-center footer-bottom-row'
                            )
                        ],
                        className='footer-content'
                    )
                ],
                className='footer-surface'
            )
        ],
        className='footer'
    )
