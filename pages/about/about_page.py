"""
ZORIA About Page - Diseño Premium Ejecutivo
Elegante, moderno, poderoso pero sobrio y profesional
Paleta: Carbón profundo + Oro/Ambar + Blanco puro
"""
from dash import html, dcc, register_page
import dash

from pages.common.sidebar import sideBar
from pages.common.mobile_nav import mobileNavBar
from pages.common.footer import footer
from pages.common.floating_terminal_button import floating_terminal_button

# ==================== REGISTRO DE PÁGINA ====================
register_page(
    __name__,
    path='/about',
    title='Acerca de ZORIA',
    name='about'
)

# ==================== DATOS DEL EQUIPO ====================
TEAM_MEMBERS = [
    {
        'name': 'Mario Ricardo Montero Hurtado',
        'role': 'Lead Developer',
        'title': 'Físico & Programador',
        'description': 'Desarrollador de Software, web, IoT y Beamdiameter. Arquitecto principal de ZORIA especializado en instrumentación científica.',
        'image': '/assets/images/abaut/MARIOMONTERO.jpeg',
        'email': 'mariomontero942@gmail.com',
        'linkedin': '#',
        'github': 'https://github.com/mario1027'
    },
    {
        'name': 'Francisco Juan Racedo Niebles',
        'role': 'Research Scientist',
        'title': 'Físico',
        'description': 'Especialista en Espectroscopia. Investigador en análisis óptico y caracterización de materiales.',
        'image': '/assets/images/abaut/FRANCISCO_RACEDO_NIEBLES_0.png',
        'email': '',
        'linkedin': '#',
        'github': '#'
    },
    {
        'name': 'Juan Carlos Alvarez Navarro',
        'role': 'Scientific Advisor',
        'title': 'Físico',
        'description': 'Especialista en Espectroscopia. Experto en técnicas avanzadas de análisis óptico y metrología.',
        'image': 'https://ui-avatars.com/api/?name=Juan+Carlos+Alvarez&size=400&background=1e293b&color=d4af37&bold=true',
        'email': '',
        'linkedin': '#',
        'github': '#'
    }
]

# ==================== COMPONENTES PREMIUM ====================

def hero_section():
    """Hero ejecutivo con tipografía monumental y animaciones suaves"""
    return html.Div([
        html.Div([
            # Badge superior minimalista
            html.Div([
                html.Span("●", style={
                    'color': '#d4af37',
                    'fontSize': '8px',
                    'marginRight': '12px',
                    'animation': 'pulse 2s infinite'
                }),
                html.Span("PROYECTO OPEN SOURCE", style={
                    'fontSize': '0.75rem',
                    'letterSpacing': '0.3em',
                    'fontWeight': '500',
                    'color': 'var(--z-color-text-tertiary)'
                })
            ], style={
                'marginBottom': '40px',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center'
            }),
            
            # Título principal - Tipografía monumental
            html.H1([
                html.Span("ZORIA", style={
                    'display': 'block',
                    'fontSize': 'clamp(4rem, 12vw, 10rem)',
                    'fontWeight': '200',
                    'letterSpacing': '-0.03em',
                    'lineHeight': '0.9',
                    'color': 'var(--z-color-text-primary)',
                    'marginBottom': '10px'
                }),
                html.Span("Impedance Analysis System", style={
                    'display': 'block',
                    'fontSize': 'clamp(1rem, 2.5vw, 1.5rem)',
                    'fontWeight': '300',
                    'letterSpacing': '0.4em',
                    'color': '#d4af37',
                    'textTransform': 'uppercase'
                })
            ], style={
                'textAlign': 'center',
                'marginBottom': '50px'
            }),
            
            # Línea decorativa
            html.Div(style={
                'width': '60px',
                'height': '1px',
                'background': 'linear-gradient(90deg, transparent, #d4af37, transparent)',
                'margin': '0 auto 50px'
            }),
            
            # Descripción
            html.P([
                "Plataforma de análisis de impedancia de precisión.",
                html.Br(),
                "Diseñada para investigación científica de alto nivel."
            ], style={
                'fontSize': 'clamp(1rem, 1.5vw, 1.25rem)',
                'fontWeight': '300',
                'color': 'var(--z-color-text-secondary)',
                'textAlign': 'center',
                'maxWidth': '600px',
                'margin': '0 auto 60px',
                'lineHeight': '1.8',
                'letterSpacing': '0.02em'
            }),
            
            # CTA Buttons - Estilo minimalista con hover mejorado
            html.Div([
                html.A([
                    html.I(className="fas fa-book-open", style={'marginRight': '10px'}),
                    html.Span("Explorar Documentación", style={
                        'fontSize': '0.85rem',
                        'letterSpacing': '0.15em',
                        'fontWeight': '500'
                    })
                ], href="/documentacion", className="btn-hero-primary"),
                html.A([
                    html.I(className="fab fa-github", style={'marginRight': '10px'}),
                    html.Span("GitHub", style={
                        'fontSize': '0.85rem',
                        'letterSpacing': '0.15em'
                    })
                ], href="https://github.com/mario1027/ZORIA", target="_blank", className="btn-hero-secondary")
            ], style={
                'display': 'flex',
                'justifyContent': 'center',
                'flexWrap': 'wrap',
                'gap': '20px'
            }),
            
            # Scroll indicator
            html.Div([
                html.Div(style={
                    'width': '1px',
                    'height': '60px',
                    'background': 'linear-gradient(180deg, #d4af37, transparent)',
                    'margin': '0 auto',
                    'animation': 'scrollIndicator 2s ease-in-out infinite'
                })
            ], style={
                'position': 'absolute',
                'bottom': '40px',
                'left': '50%',
                'transform': 'translateX(-50%)'
            })
            
        ], style={
            'maxWidth': '1400px',
            'margin': '0 auto',
            'padding': '120px 40px 100px',
            'position': 'relative'
        })
    ], style={
        'background': 'var(--z-color-bg-primary)',
        'position': 'relative',
        'overflow': 'hidden',
        'minHeight': '100vh',
        'display': 'flex',
        'alignItems': 'center'
    })


def stats_section():
    """Estadísticas con diseño de grid minimalista y animaciones"""
    stats = [
        {'value': '10', 'unit': 'MHz', 'label': 'Frecuencia Máxima', 'desc': 'Análisis de alta frecuencia'},
        {'value': '0.2', 'unit': 'Hz', 'label': 'Frecuencia Mínima', 'desc': 'Precisión en bajas frecuencias'},
        {'value': '100', 'unit': '%', 'label': 'Open Source', 'desc': 'Código completamente libre'},
        {'value': '24/7', 'unit': '', 'label': 'Soporte Continuo', 'desc': 'Comunidad activa global'}
    ]
    
    return html.Div([
        html.Div([
            *[html.Div([
                html.Div([
                    html.Div([
                        html.Span(stat['value'], className="stat-number", style={
                            'fontSize': 'clamp(3rem, 6vw, 5rem)',
                            'fontWeight': '200',
                            'color': 'var(--z-color-text-primary)',
                            'lineHeight': '1'
                        }),
                        html.Span(stat['unit'], style={
                            'fontSize': '1.5rem',
                            'fontWeight': '300',
                            'color': '#d4af37',
                            'marginLeft': '5px'
                        }) if stat['unit'] else None
                    ]),
                    html.H3(stat['label'], style={
                        'fontSize': '0.9rem',
                        'fontWeight': '500',
                        'color': '#d4af37',
                        'letterSpacing': '0.15em',
                        'textTransform': 'uppercase',
                        'margin': '15px 0 8px'
                    }),
                    html.P(stat['desc'], style={
                        'fontSize': '0.85rem',
                        'color': 'var(--z-color-text-tertiary)',
                        'fontWeight': '300'
                    })
                ], className="stat-item", style={
                    'padding': '50px 30px',
                    'borderRight': f'1px solid {"#e2e8f0" if i < len(stats)-1 else "transparent"}',
                    'textAlign': 'center',
                    'transition': 'all 0.3s ease',
                    'cursor': 'default'
                })
            ], className='col-lg-3 col-md-6', style={'marginBottom': '0'}) 
            for i, stat in enumerate(stats)]
        ], className='row g-0', style={
            'borderTop': '1px solid var(--z-color-border)',
            'borderBottom': '1px solid var(--z-color-border)'
        })
    ], style={
        'background': 'var(--z-color-bg-elevated)'
    })


def manifesto_section():
    """Sección de manifesto/misión con tipografía editorial"""
    return html.Div([
        html.Div([
            html.Div([
                html.Div([
                    # Label
                    html.Span("Nuestra Filosofía", style={
                        'fontSize': '0.75rem',
                        'letterSpacing': '0.3em',
                        'color': '#d4af37',
                        'textTransform': 'uppercase',
                        'display': 'block',
                        'marginBottom': '30px'
                    }),
                    
                    # Quote principal
                    html.Blockquote([
                        html.Span("\"", style={
                            'fontSize': '6rem',
                            'color': '#d4af37',
                            'opacity': '0.3',
                            'lineHeight': '0.5',
                            'display': 'block',
                            'marginBottom': '-20px'
                        }),
                        "La precisión en la medición de impedancia no es un lujo, ",
                        html.Br(),
                        "es la base del conocimiento científico confiable."
                    ], style={
                        'fontSize': 'clamp(1.5rem, 3vw, 2.5rem)',
                        'fontWeight': '300',
                        'color': 'var(--z-color-text-primary)',
                        'lineHeight': '1.4',
                        'margin': '0 0 40px 0',
                        'padding': '0',
                        'border': 'none'
                    }),
                    
                    # Descripción
                    html.P([
                        "ZORIA nace de la convicción de que las herramientas de análisis ",
                        "electrónico de precisión deben ser accesibles sin comprometer la calidad. ",
                        "Combinamos ingeniería de alto nivel con diseño intuitivo para democratizar ",
                        "el acceso a la caracterización de materiales y circuitos."
                    ], style={
                        'fontSize': '1.1rem',
                        'color': 'var(--z-color-text-secondary)',
                        'lineHeight': '1.9',
                        'fontWeight': '300',
                        'maxWidth': '700px'
                    })
                ], className='col-lg-8')
            ], className='row justify-content-center')
        ], style={
            'maxWidth': '1200px',
            'margin': '0 auto',
            'padding': '120px 40px'
        })
    ], style={
        'background': 'var(--z-color-bg-card)'
    })


def features_section():
    """Características con diseño de grid y iconos corregidos (FA5 disponibles)"""
    features = [
        {
            'icon': 'fa-chart-line',
            'title': 'Análisis en Tiempo Real',
            'desc': 'Visualización instantánea de parámetros de impedancia con gráficos de alta fidelidad y actualización continua.'
        },
        {
            'icon': 'fa-microchip',
            'title': 'Hardware Profesional',
            'desc': 'Integración nativa con el evaluador EVAL-ADMX2001 de Analog Devices para mediciones de precisión.'
        },
        {
            'icon': 'fa-code-branch',
            'title': 'Código Abierto',
            'desc': 'Desarrollo transparente bajo licencia MIT. Contribuciones bienvenidas y comunidad activa.'
        },
        {
            'icon': 'fa-shield-alt',
            'title': 'Calibración Precisa',
            'desc': 'Sistema de calibración automática con múltiples perfiles configurables para cada aplicación.'
        },
        {
            'icon': 'fa-database',
            'title': 'Gestión de Datos',
            'desc': 'Almacenamiento organizado de mediciones con exportación a CSV, Excel y otros formatos.'
        },
        {
            'icon': 'fa-terminal',
            'title': 'Control Total',
            'desc': 'Interfaz de terminal integrada para comandos avanzados, debugging y automatización.'
        }
    ]
    
    return html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Span("Capacidades", style={
                        'fontSize': '0.75rem',
                        'letterSpacing': '0.3em',
                        'color': '#d4af37',
                        'textTransform': 'uppercase',
                        'display': 'block',
                        'marginBottom': '20px'
                    }),
                    html.H2("Funcionalidades Principales", style={
                        'fontSize': 'clamp(2rem, 4vw, 3rem)',
                        'fontWeight': '300',
                        'color': 'var(--z-color-text-primary)',
                        'letterSpacing': '-0.02em'
                    })
                ], className='col-lg-8')
            ], className='row mb-5'),
            
            html.Div([
                *[html.Div([
                    html.Div([
                        html.Div([
                            html.I(className=f"fas {feature['icon']}", style={
                                'fontSize': '1.5rem',
                                'color': '#d4af37',
                                'transition': 'all 0.3s ease'
                            })
                        ], className="feature-icon-container", style={
                            'width': '70px',
                            'height': '70px',
                            'border': '2px solid var(--z-color-border)',
                            'borderRadius': '50%',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'marginBottom': '25px',
                            'transition': 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                            'background': 'var(--z-color-bg-card)'
                        }),
                        html.H3(feature['title'], style={
                            'fontSize': '1.15rem',
                            'fontWeight': '600',
                            'color': 'var(--z-color-text-primary)',
                            'marginBottom': '12px',
                            'letterSpacing': '-0.01em'
                        }),
                        html.P(feature['desc'], style={
                            'fontSize': '0.95rem',
                            'color': 'var(--z-color-text-tertiary)',
                            'lineHeight': '1.7',
                            'fontWeight': '400'
                        })
                    ], className="feature-card-v2", style={
                        'padding': '40px 30px',
                        'background': 'var(--z-color-bg-card)',
                        'borderRadius': '16px',
                        'border': '1px solid var(--z-color-border)',
                        'height': '100%',
                        'transition': 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                        'cursor': 'pointer'
                    })
                ], className='col-lg-4 col-md-6 mb-4') for feature in features]
            ], className='row g-4')
        ], style={
            'maxWidth': '1400px',
            'margin': '0 auto',
            'padding': '120px 40px'
        })
    ], style={
        'background': 'var(--z-color-bg-elevated)'
    })


def team_section():
    """Sección del equipo con cards premium y UX mejorado"""
    return html.Div([
        html.Div([
            # Header
            html.Div([
                html.Span("El Equipo", style={
                    'fontSize': '0.75rem',
                    'letterSpacing': '0.3em',
                    'color': '#d4af37',
                    'textTransform': 'uppercase',
                    'display': 'block',
                    'marginBottom': '20px'
                }),
                html.H2("Quienes Construyen ZORIA", style={
                    'fontSize': 'clamp(2rem, 4vw, 3rem)',
                    'fontWeight': '300',
                    'color': 'var(--z-color-text-primary)',
                    'letterSpacing': '-0.02em',
                    'marginBottom': '20px'
                }),
                html.Div(style={
                    'width': '40px',
                    'height': '2px',
                    'background': 'var(--z-color-accent, #d4af37)',
                    'margin': '30px auto'
                }),
            ], style={'textAlign': 'center', 'marginBottom': '80px'}),
            
            # Team Grid
            html.Div([
                *[html.Div([
                    html.Div([
                        # Imagen del miembro
                        html.Div([
                            html.Img(
                                src=member['image'],
                                className="team-member-img",
                                style={
                                    'width': '100%',
                                    'height': '380px',
                                    'objectFit': 'cover',
                                    'objectPosition': 'center',
                                    'filter': 'grayscale(30%)',
                                    'transition': 'all 0.6s ease'
                                }
                            )
                        ], style={
                            'position': 'relative',
                            'overflow': 'hidden'
                            }),
                        
                        # Badge de rol
                        html.Div([
                            html.Span(member['role'], style={
                                'fontSize': '0.7rem',
                                'letterSpacing': '0.1em',
                                'textTransform': 'uppercase',
                                'color': '#ffffff',
                                'fontWeight': '600'
                            })
                        ], style={
                            'position': 'absolute',
                            'top': '20px',
                            'right': '20px',
                            'background': 'var(--z-color-accent, #d4af37)',
                            'padding': '6px 14px',
                            'borderRadius': '20px',
                            'zIndex': '10'
                        }),
                        
                        # Información
                        html.Div([
                            html.H3(member['name'], style={
                                'fontSize': '1.4rem',
                                'fontWeight': '600',
                                'color': 'var(--z-color-text-primary)',
                                'marginBottom': '5px',
                                'letterSpacing': '-0.01em'
                            }),
                            html.P(member['title'], style={
                                'fontSize': '0.85rem',
                                'color': '#d4af37',
                                'marginBottom': '15px',
                                'fontWeight': '400'
                            }),
                            html.P(member['description'], style={
                                'fontSize': '0.9rem',
                                'color': 'var(--z-color-text-secondary)',
                                'lineHeight': '1.7',
                                'marginBottom': '25px',
                                'fontWeight': '300'
                            }),
                            
                            # Social links minimalistas
                            html.Div([
                                html.A(
                                    html.I(className="fab fa-github", style={'fontSize': '1.1rem'}),
                                    href=member['github'] if member['github'] != '#' else None,
                                    target="_blank" if member['github'] != '#' else None,
                                    className="social-link",
                                    style={
                                        'color': 'var(--z-color-text-tertiary)',
                                        'textDecoration': 'none',
                                        'marginRight': '20px',
                                        'transition': 'all 0.3s ease',
                                        'padding': '8px'
                                    }
                                ),
                                html.A(
                                    html.I(className="fab fa-linkedin-in", style={'fontSize': '1.1rem'}),
                                    href=member['linkedin'] if member['linkedin'] != '#' else None,
                                    target="_blank" if member['linkedin'] != '#' else None,
                                    className="social-link",
                                    style={
                                        'color': 'var(--z-color-text-tertiary)',
                                        'textDecoration': 'none',
                                        'marginRight': '20px' if member['email'] else '0',
                                        'transition': 'all 0.3s ease',
                                        'padding': '8px'
                                    }
                                ),
                                html.A(
                                    html.I(className="fas fa-envelope", style={'fontSize': '1.1rem'}),
                                    href=f"mailto:{member['email']}" if member['email'] else None,
                                    className="social-link",
                                    style={
                                        'color': 'var(--z-color-text-tertiary)',
                                        'textDecoration': 'none',
                                        'transition': 'all 0.3s ease',
                                        'padding': '8px'
                                    }
                                ) if member['email'] else None
                            ])
                        ], style={
                            'padding': '30px',
                            'background': 'var(--z-color-bg-elevated)',
                            'borderTop': '1px solid var(--z-color-border)'
                        })
                    ], className="team-card-v2", style={
                        'border': '1px solid var(--z-color-border)',
                        'borderRadius': '16px',
                        'overflow': 'hidden',
                        'position': 'relative',
                        'transition': 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                        'background': 'var(--z-color-bg-card)'
                    })
                ], className='col-lg-4 col-md-6 mb-5') for member in TEAM_MEMBERS]
            ], className='row g-4 justify-content-center')
            
        ], style={
            'maxWidth': '1400px',
            'margin': '0 auto',
            'padding': '120px 40px'
        })
    ], style={
        'background': 'var(--z-color-bg-card)'
    })


def partners_section():
    """Sección de instituciones colaboradoras"""
    return html.Div([
        html.Div([
            # Header
            html.Div([
                html.Span("Instituciones", style={
                    'fontSize': '0.75rem',
                    'letterSpacing': '0.3em',
                    'color': '#d4af37',
                    'textTransform': 'uppercase',
                    'display': 'block',
                    'marginBottom': '20px'
                }),
                html.H2("Respaldo Institucional", style={
                    'fontSize': 'clamp(2rem, 4vw, 2.5rem)',
                    'fontWeight': '300',
                    'color': 'var(--z-color-text-primary)',
                    'letterSpacing': '-0.02em',
                    'marginBottom': '20px'
                }),
                html.Div(style={
                    'width': '40px',
                    'height': '2px',
                    'background': 'var(--z-color-accent, #d4af37)',
                    'margin': '30px auto 60px'
                }),
            ], style={'textAlign': 'center'}),
            
            # Logos Grid
            html.Div([
                # Universidad
                html.Div([
                    html.Div([
                        html.Div([
                            html.Img(
                                src="/assets/images/abaut/uniatlantico.png",
                                alt="Universidad del Atlántico",
                                style={
                                    'maxWidth': '100%',
                                    'height': 'auto',
                                    'maxHeight': '180px',
                                    'objectFit': 'contain',
                                    'marginBottom': '20px'
                                }
                            )
                        ], style={'textAlign': 'center', 'marginBottom': '15px'}),
                        html.H5("Universidad del Atlántico", style={
                            'fontSize': '1.2rem',
                            'fontWeight': '600',
                            'color': 'var(--z-color-text-primary)',
                            'marginBottom': '10px',
                            'textAlign': 'center'
                        }),
                        html.P("Barranquilla, Colombia", style={
                            'fontSize': '0.9rem',
                            'color': 'var(--z-color-text-secondary)',
                            'textAlign': 'center'
                        })
                    ], style={
                        'padding': '40px 30px',
                        'background': 'var(--z-color-bg-elevated)',
                        'borderRadius': '16px',
                        'border': '1px solid var(--z-color-border)',
                        'transition': 'all 0.4s ease',
                        'cursor': 'pointer',
                        'height': '100%'
                    })
                ], className='col-md-6 mb-4'),
                
                # GEOEL
                html.Div([
                    html.Div([
                        html.Div([
                            html.Img(
                                src="/assets/images/abaut/geoel.png",
                                alt="GEOEL",
                                style={
                                    'maxWidth': '100%',
                                    'height': 'auto',
                                    'maxHeight': '180px',
                                    'objectFit': 'contain',
                                    'marginBottom': '20px'
                                }
                            )
                        ], style={'textAlign': 'center', 'marginBottom': '15px'}),
                        html.H5("GEOEL", style={
                            'fontSize': '1.2rem',
                            'fontWeight': '600',
                            'color': 'var(--z-color-text-primary)',
                            'marginBottom': '10px',
                            'textAlign': 'center'
                        }),
                        html.P("Grupo de Espectroscopia Óptica y Emisión Láser", style={
                            'fontSize': '0.9rem',
                            'color': 'var(--z-color-text-secondary)',
                            'textAlign': 'center',
                            'marginBottom': '5px'
                        }),
                        html.P("Universidad del Atlántico", style={
                            'fontSize': '0.85rem',
                            'color': 'var(--z-color-text-tertiary)',
                            'textAlign': 'center'
                        })
                    ], style={
                        'padding': '40px 30px',
                        'background': 'var(--z-color-bg-elevated)',
                        'borderRadius': '16px',
                        'border': '1px solid var(--z-color-border)',
                        'transition': 'all 0.4s ease',
                        'cursor': 'pointer',
                        'height': '100%'
                    })
                ], className='col-md-6 mb-4')
            ], className='row justify-content-center')
            
        ], style={
            'maxWidth': '900px',
            'margin': '0 auto',
            'padding': '100px 40px'
        })
    ], style={
        'background': 'var(--z-color-bg-elevated)'
    })


def cta_section():
    """CTA final ejecutivo con mejor UX"""
    return html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Span("Comienza Hoy", style={
                        'fontSize': '0.75rem',
                        'letterSpacing': '0.3em',
                        'color': '#d4af37',
                        'textTransform': 'uppercase',
                        'display': 'block',
                        'marginBottom': '30px'
                    }),
                    html.H2([
                        "¿Listo para elevar ",
                        html.Br(),
                        "tu análisis de impedancia?"
                    ], style={
                        'fontSize': 'clamp(2rem, 4vw, 3.5rem)',
                        'fontWeight': '300',
                        'color': 'var(--z-color-text-primary)',
                        'letterSpacing': '-0.02em',
                        'marginBottom': '30px',
                        'lineHeight': '1.2'
                    }),
                    html.P([
                        "Únete a la comunidad de investigadores e ingenieros ",
                        "que confían en ZORIA para sus mediciones de precisión."
                    ], style={
                        'fontSize': '1.1rem',
                        'color': 'var(--z-color-text-secondary)',
                        'maxWidth': '500px',
                        'margin': '0 auto 50px',
                        'lineHeight': '1.8',
                        'fontWeight': '300'
                    }),
                    
                    html.Div([
                        html.A([
                            html.I(className="fas fa-download", style={'marginRight': '10px'}),
                            html.Span("Descargar ZORIA", style={
                                'fontSize': '0.9rem',
                                'letterSpacing': '0.15em',
                                'fontWeight': '600'
                            })
                        ], href="https://github.com/mario1027/ZORIA/releases", target="_blank", className="btn-cta-primary"),
                        html.A([
                            html.I(className="fas fa-rocket", style={'marginRight': '10px'}),
                            html.Span("Ver Demo", style={
                                'fontSize': '0.9rem',
                                'letterSpacing': '0.15em',
                                'fontWeight': '500'
                            })
                        ], href="/", className="btn-cta-secondary")
                    ], style={
                        'display': 'flex',
                        'justifyContent': 'center',
                        'flexWrap': 'wrap',
                        'gap': '20px'
                    }),
                    
                    # Trust badges
                    html.Div([
                        html.Div([
                            html.I(className="fab fa-python", style={
                                'fontSize': '1.5rem',
                                'color': '#d4af37',
                                'marginBottom': '8px'
                            }),
                            html.Div("Python 3.13+", style={
                                'fontSize': '0.75rem',
                                'color': 'var(--z-color-text-tertiary)'
                            })
                        ], style={'textAlign': 'center'}),
                        html.Div([
                            html.I(className="fas fa-check-circle", style={
                                'fontSize': '1.5rem',
                                'color': '#d4af37',
                                'marginBottom': '8px'
                            }),
                            html.Div("MIT License", style={
                                'fontSize': '0.75rem',
                                'color': 'var(--z-color-text-tertiary)'
                            })
                        ], style={'textAlign': 'center'}),
                        html.Div([
                            html.I(className="fas fa-laptop-code", style={
                                'fontSize': '1.5rem',
                                'color': '#d4af37',
                                'marginBottom': '8px'
                            }),
                            html.Div("Multi-Platform", style={
                                'fontSize': '0.75rem',
                                'color': 'var(--z-color-text-tertiary)'
                            })
                        ], style={'textAlign': 'center'})
                    ], style={
                        'display': 'flex',
                        'justifyContent': 'center',
                        'gap': '60px',
                        'marginTop': '60px',
                        'flexWrap': 'wrap'
                    })
                    
                ], style={'textAlign': 'center'})
            ], className='row justify-content-center')
        ], style={
            'maxWidth': '1000px',
            'margin': '0 auto',
            'padding': '150px 40px'
        })
    ], style={
        'background': 'var(--z-color-bg-primary)',
        'position': 'relative'
    })


# ==================== LAYOUT PRINCIPAL ====================
layout = html.Div([
    sideBar(),
    mobileNavBar(),
    
    html.Main([
        # Hero Premium
        hero_section(),
        
        # Stats Bar
        stats_section(),
        
        # Manifesto
        manifesto_section(),
        
        # Features
        features_section(),
        
        # Team
        team_section(),
        
        # Partners & Institutions
        partners_section(),
        
        # CTA Final
        cta_section()
        
    ], className="content", style={
        'background': 'var(--z-color-bg-card)'
    }),
    
    # Footer fuera del main (igual que otras páginas)
    footer(),
    
    floating_terminal_button()
    
], className="about-page sc-chart d-flex flex-column", style={
    'minHeight': '100vh',
    'background': 'var(--z-color-bg-card)'
})


# ==================== CALLBACKS ====================
def register_callbacks(app):
    """Registrar callbacks de la página About"""
    pass


def register_about_page(app):
    """Registrar la página About en la aplicación"""
    register_callbacks(app)
