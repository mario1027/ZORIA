"""
Página del Simulador RLC integrada en la aplicación multi-página
Usando el estilo de la plantilla Volt con navegación avanzada
"""
from dash import html, Input, Output, State, dcc
from dash.exceptions import PreventUpdate
from dash_spa import register_page
import plotly.graph_objects as go
import numpy as np

from pages.simulator.components import (
    circuit_selector_card,
    resistance_input_card,
    inductance_input_card,
    capacitance_input_card,
    frequency_range_card,
    bode_plot_card,
    nyquist_plot_card,
    impedance_info_card
)
from pages.simulator.impedance_calculator import ImpedanceCalculator, get_circuit_info
from pages.common.sidebar import sideBar
from pages.common.mobile_nav import mobileNavBar
from pages.common.footer import footer
from pages.common.terminal_component import global_terminal_component
from pages.common.floating_terminal_button import floating_terminal_button
from lib.design_tokens import get_theme as get_design_theme

# Función helper para prints seguros (maneja BrokenPipeError)
def safe_print(message):
    """Imprime un mensaje manejando errores de pipe roto"""
    try:
        print(message)
    except (BrokenPipeError, IOError):
        pass  # Ignorar si el terminal está cerrado

CIRCUIT_INFO = get_circuit_info()

# Layout principal con navegación compartida
layout = html.Div([
    # Mobile Navbar (solo visible en móvil)
    mobileNavBar(),
    
    # Contenedor flex para sidebar y contenido principal
    html.Div([
        # Sidebar compartido (navegación izquierda)
        sideBar(),

        # Contenido principal - aprovecha todo el espacio horizontal disponible
        html.Main([
            html.Div(
                className="container-fluid py-4",
                children=[
                    # Header con título y botón de tema
                    html.Div([
                        html.Div([
                            html.H2([
                                html.Span('', **{'data-i18n': 'sim.title'})
                            ], className="h3 mb-0")
                        ], className="col-12 col-md-6 mb-2 mb-md-0"),
                        html.Div([
                            # Botón de tema
                            html.Button(
                                id="simulator-theme-toggle",
                                className="btn btn-outline-secondary",
                                children=[
                                    html.I(className="fas fa-moon", id="simulator-theme-icon")
                                ],
                                title="",
                                **{'data-i18n-title': 'ui.change_chart_theme'}
                            )
                        ], className="col-12 col-md-6 d-flex justify-content-md-end align-items-center")
                    ], className="row align-items-center py-4"),

                    # PRIORIDAD #1: GRÁFICOS PRIMERO (70% altura visual)
                    html.Div([
                        # Diagrama de Bode
                        html.Div([
                            bode_plot_card()
                        ], className="col-12 col-lg-6 mb-4"),

                        # Diagrama de Nyquist
                        html.Div([
                            nyquist_plot_card()
                        ], className="col-12 col-lg-6 mb-4")
                    ], className="row"),
                    
                    # PRIORIDAD #2: CONFIGURACIÓN COMPACTA (30% altura visual)
                    html.Div([
                        # Configuración de circuito
                        html.Div([
                            html.Div([
                                circuit_selector_card(),
                                html.Div(className="row g-3 mt-1", children=[
                                    html.Div(className="col-md-4", children=[resistance_input_card()]),
                                    html.Div(className="col-md-4", children=[inductance_input_card()]),
                                    html.Div(className="col-md-4", children=[capacitance_input_card()])
                                ])
                            ], className="col-lg-8 mb-4"),
                            
                            # Rango de frecuencia
                            html.Div([
                                frequency_range_card()
                            ], className="col-lg-4 mb-4")
                        ], className="row"),
                        
                        # Información de impedancia
                        html.Div([
                            html.Div([
                                impedance_info_card()
                            ], className="col-12")
                        ], className="row")
                    ])
                ]
            )
        ], className="main-content w-100")
    
    ], className="d-flex flex-grow-1"),

    # Footer al final, fuera del flex sidebar-content
    footer(),
    
    # Botón flotante del terminal
    floating_terminal_button()

], className="d-flex flex-column min-vh-100")

def format_frequency(f):
    if f >= 1000000:
        return f"{f/1000000:.3f} MHz"
    elif f >= 1000:
        return f"{f/1000:.3f} kHz"
    else:
        return f"{f:.3f} Hz"

def create_simulator_page():
    """Crea la página del simulador RLC"""
    return layout

def register_simulator_callbacks(app):
    """Registra los callbacks para la página del simulador"""

    @app.callback(
        Output("calculate-btn", "n_clicks"),
        [Input("circuit-type", "value")],
        prevent_initial_call=True
    )
    def force_recalculation(circuit_type):
        if circuit_type and not circuit_type.startswith("header"):
            return 1
        return 0

    @app.callback(
        [Output("simulator-bode-plot", "figure"),
         Output("simulator-nyquist-plot", "figure"),
         Output("simulator-impedance-info", "children")],
        [Input("calculate-btn", "n_clicks"),
         Input("circuit-type", "value"),
         Input("resistance-input", "value"),
         Input("inductance-input", "value"),
         Input("capacitance-input", "value"),
         Input("freq-start", "value"),
         Input("freq-end", "value"),
         Input("freq-points", "value"),
         Input("theme-store", "data")],
        prevent_initial_call=False
    )
    def calculate_impedance(n_clicks, circuit_type, R, L, C, f_start, f_end, n_points, theme_data):
        safe_print(f" BOTÓN PRESIONADO: n_clicks = {n_clicks}")
        safe_print(f"Datos recibidos: circuit_type={circuit_type}, R={R}, L={L}, C={C}")

        theme = theme_data if theme_data else 'dark'
        if isinstance(theme, dict):
            theme = theme.get('theme', 'dark')
        safe_print(f"Tema actual: {theme}")

        CIRCUIT_INFO = get_circuit_info()

        if not circuit_type or circuit_type.startswith("header"):
            circuit_type = "RC_series"

        if R is None: R = 1000
        if L is None: L = 0.001
        if C is None: C = 1e-6
        if f_start is None: f_start = 0.2
        if f_end is None: f_end = 10000000
        if n_points is None: n_points = 1000

        if R <= 0: R = 1000
        if L <= 0: L = 0.001
        if C <= 0: C = 1e-6
        if f_start < 0.2: f_start = 0.2
        if f_end > 10000000: f_end = 10000000
        if f_end <= f_start: f_end = f_start * 1000
        if n_points < 10: n_points = 10

        try:
            calc = ImpedanceCalculator(f_start, f_end, n_points)
            Z = calc.calculate_impedance(circuit_type, R=R, L=L, C=C)
            bode_data = calc.get_bode_data(Z)
            nyquist_data = calc.get_nyquist_data(Z)

            t = get_design_theme(theme)

            bode_fig = go.Figure()
            bode_fig.add_trace(go.Scatter(
                x=bode_data["frequencies"],
                y=bode_data["magnitude_db"],
                mode="lines",
                name="Magnitud |Z|",
                line=dict(color=t['chart_magnitude'], width=2),
                yaxis="y1"
            ))
            bode_fig.add_trace(go.Scatter(
                x=bode_data["frequencies"],
                y=bode_data["phase_deg"],
                mode="lines",
                name="Fase φ",
                line=dict(color=t['chart_phase'], width=2),
                yaxis="y2"
            ))

            bode_fig.update_layout(
                title={"text": f"Diagrama de Bode - {CIRCUIT_INFO[circuit_type]['name']}", "font": {"size": 16, "color": t['text_primary']}},
                xaxis=dict(
                    title="Frecuencia (Hz)",
                    type="log",
                    range=[np.log10(max(0.1, f_start)), np.log10(f_end)],
                    showgrid=True,
                    gridcolor=t['chart_grid'],
                    linecolor=t['chart_text'],
                    tickcolor=t['chart_text'],
                    tickfont=dict(color=t['chart_text']),
                    title_font=dict(color=t['chart_text']),
                    tickvals=[0.2, 1, 10, 100, 1e3, 1e4, 1e5, 1e6, 1e7],
                    ticktext=["0.2", "1", "10", "100", "1k", "10k", "100k", "1M", "10M"],
                ),
                yaxis=dict(
                    title=dict(text="Magnitud |Z| (dB)", font=dict(color=t['chart_magnitude'])),
                    tickfont={"color": t['chart_magnitude']},
                    side="left",
                    showgrid=True,
                    gridcolor=t['chart_grid'],
                    linecolor=t['chart_text'],
                    tickcolor=t['chart_text'],
                    title_font=dict(color=t['chart_text'])
                ),
                yaxis2=dict(
                    title=dict(text="Fase φ (°)", font=dict(color=t['chart_phase'])),
                    tickfont={"color": t['chart_phase']},
                    anchor="x",
                    overlaying="y",
                    side="right",
                    showgrid=False,
                    linecolor=t['chart_text'],
                    tickcolor=t['chart_text'],
                    title_font=dict(color=t['chart_text'])
                ),
                legend=dict(x=0.7, y=0.95),
                height=450,
                margin=dict(l=60, r=60, t=50, b=50),
                plot_bgcolor=t['chart_bg'],
                paper_bgcolor=t['chart_bg'],
                font=dict(color=t['text_primary'], size=14, family="Fira Sans, Arial, sans-serif"),
                title_font=dict(color=t['text_primary'], size=18)
            )

            # Crear gráfico de Nyquist con colormap basado en frecuencia
            nyquist_fig = go.Figure()

            frequencies = nyquist_data["frequencies"] if "frequencies" in nyquist_data else calc.frequencies

            nyquist_fig.add_trace(go.Scatter(
                x=nyquist_data["real"],
                y=-nyquist_data["imaginary"],
                mode="lines+markers",
                name="Z(jω)",
                line=dict(
                    color=t['chart_nyquist'],
                    width=2
                ),
                marker=dict(
                    color=frequencies,
                    size=8,
                    showscale=False
                ),
                text=[f"f = {format_frequency(f)}" for f in frequencies],
                hovertemplate="<b>%{text}</b><br>" +
                            "Z' = %{x:.2f} Ω<br>" +
                            "-Z'' = %{y:.2f} Ω<br>" +
                            "<extra></extra>",
                showlegend=False
            ))

            nyquist_fig.update_layout(
                title={"text": f"Diagrama de Nyquist - {CIRCUIT_INFO[circuit_type]['name']}", "font": {"size": 14, "color": t['text_primary']}},
                xaxis=dict(
                    title="Parte Real Z' (Ω)",
                    showgrid=True,
                    zeroline=True,
                    autorange=True,
                    gridcolor=t['chart_grid'],
                    linecolor=t['chart_text'],
                    tickcolor=t['chart_text'],
                    tickfont=dict(color=t['chart_text']),
                    title_font=dict(color=t['chart_text'])
                ),
                yaxis=dict(
                    title="Parte Imaginaria -Z'' (Ω)",
                    showgrid=True,
                    zeroline=True,
                    autorange=True,
                    gridcolor=t['chart_grid'],
                    linecolor=t['chart_text'],
                    tickcolor=t['chart_text'],
                    tickfont=dict(color=t['chart_text']),
                    title_font=dict(color=t['chart_text'])
                ),
                height=450,
                margin=dict(l=60, r=60, t=50, b=50),
                plot_bgcolor=t['chart_bg'],
                paper_bgcolor=t['chart_bg'],
                font=dict(color=t['text_primary'], size=14, family="Fira Sans, Arial, sans-serif"),
                title_font=dict(color=t['text_primary'], size=18)
            )

            info_content = [
                html.H6(CIRCUIT_INFO[circuit_type]["name"], className="text-primary mb-2"),
                html.P(CIRCUIT_INFO[circuit_type]["description"], className="text-muted small mb-3"),
                html.P([html.Code(CIRCUIT_INFO[circuit_type]["formula"])], className="mb-3")
            ]

            return bode_fig, nyquist_fig, html.Div(info_content)

        except Exception as e:
            safe_print(f"Error: {e}")
            t = get_design_theme(theme)
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title="Error en el cálculo",
                annotations=[dict(
                    text="Error en el cálculo de impedancia",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    font=dict(size=16, color=t['text_tertiary'])
                )],
                plot_bgcolor=t['chart_bg'],
                paper_bgcolor=t['chart_bg'],
                font=dict(color=t['text_primary'], size=14, family="Fira Sans, Arial, sans-serif"),
                title_font=dict(color=t['text_primary'], size=18)
            )
            return empty_fig, empty_fig, html.Div([html.P("Error en el cálculo")])

    @app.callback(
        [Output("theme-store", "data", allow_duplicate=True),
         Output("simulator-theme-icon", "className", allow_duplicate=True)],
        [Input("simulator-theme-toggle", "n_clicks")],
        [State("theme-store", "data")],
        prevent_initial_call=True
    )
    def toggle_simulator_theme(n_clicks, theme_data):
        """Alterna entre tema oscuro y claro — actualiza el theme-store global"""
        if not n_clicks:
            raise PreventUpdate
        current_theme = theme_data if isinstance(theme_data, str) else 'dark'
        new_theme = "light" if current_theme == "dark" else "dark"
        # Icono refleja el estado ACTUAL tras el cambio (igual que el dashboard)
        icon_class = "fas fa-moon" if new_theme == "light" else "fas fa-sun"
        safe_print(f"Cambiando tema global desde simulador: {current_theme} → {new_theme}")
        return new_theme, icon_class

    @app.callback(
        Output("simulator-theme-icon", "className", allow_duplicate=True),
        Input("theme-store", "data"),
        prevent_initial_call=False
    )
    def sync_simulator_theme_icon(theme):
        """Sincroniza el icono del simulador con el theme-store global al cargar"""
        return "fas fa-moon" if theme == "light" else "fas fa-sun"

def register_simulator_page(app):
    """Registra la página del simulador en la aplicación DashSPA"""
    register_page(
        __name__,
        path="/simulator",
        title="RLC Circuit Simulator",
        name="Simulator",
        layout=layout
    )
    
    # Registrar callbacks del simulador
    register_simulator_callbacks(app)