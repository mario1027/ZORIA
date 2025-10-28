"""
Página del Simulador RLC integrada en la aplicación multi-página
Usando el estilo de la plantilla Volt con navegación avanzada
"""
from dash import html, Input, Output, State, dcc
from dash_spa import register_page
import plotly.graph_objects as go

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
    # Store para el tema de los gráficos del simulador
    dcc.Store(id="simulator-theme-store", data={"theme": "dark"}, storage_type="local"),
    
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
                    html.Div([
                        html.H1("Simulador de Circuitos RLC", className="h2 mb-4"),
                        html.P("Analiza la respuesta en frecuencia de diferentes configuraciones de circuitos RLC", className="text-muted")
                    ], className="d-flex justify-content-between align-items-center mb-4"),

                    # Botón de toggle de tema para gráficos
                    html.Div([
                        html.Button(
                            id="simulator-theme-toggle",
                            className="btn btn-outline-secondary btn-sm d-flex align-items-center gap-2",
                            children=[
                                html.I(className="fas fa-moon", id="simulator-theme-icon"),
                                html.Span("Tema Gráficos", id="simulator-theme-text")
                            ]
                        )
                    ], className="mb-3"),

                    html.Div(
                        className="row g-4",
                        children=[
                            html.Div(
                                className="col-lg-4",
                                children=[
                                    circuit_selector_card(),
                                    html.Div(className="row g-3 mt-1", children=[
                                        html.Div(className="col-12", children=[resistance_input_card()]),
                                        html.Div(className="col-12", children=[inductance_input_card()]),
                                        html.Div(className="col-12", children=[capacitance_input_card()])
                                    ]),
                                    frequency_range_card()
                                ]
                            ),
                            html.Div(
                                className="col-lg-8",
                                children=[
                                    bode_plot_card(),
                                    nyquist_plot_card(),
                                    impedance_info_card()
                                ]
                            )
                        ]
                    )
                ]
            )
        ], className="main-content w-100")
    
    ], className="d-flex flex-grow-1"),

    # Footer al final, fuera del flex sidebar-content
    footer()

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
         Input("simulator-theme-store", "data")],
        prevent_initial_call=False
    )
    def calculate_impedance(n_clicks, circuit_type, R, L, C, f_start, f_end, n_points, theme_data):
        safe_print(f"🚀 BOTÓN PRESIONADO: n_clicks = {n_clicks}")
        safe_print(f"📊 Datos recibidos: circuit_type={circuit_type}, R={R}, L={L}, C={C}")

        # Obtener el tema actual
        theme = theme_data.get('theme', 'dark') if theme_data else 'dark'
        safe_print(f"🎨 Tema actual: {theme}")

        CIRCUIT_INFO = get_circuit_info()

        if not circuit_type or circuit_type.startswith("header"):
            circuit_type = "RC_series"

        if R is None: R = 1000
        if L is None: L = 0.001
        if C is None: C = 1e-6
        if f_start is None: f_start = 10
        if f_end is None: f_end = 100000
        if n_points is None: n_points = 100

        if R <= 0: R = 1000
        if L <= 0: L = 0.001
        if C <= 0: C = 1e-6
        if f_start <= 0: f_start = 10
        if f_end <= f_start: f_end = f_start * 1000
        if n_points < 10: n_points = 10

        try:
            calc = ImpedanceCalculator(f_start, f_end, n_points)
            Z = calc.calculate_impedance(circuit_type, R=R, L=L, C=C)
            bode_data = calc.get_bode_data(Z)
            nyquist_data = calc.get_nyquist_data(Z)

            # Definir colores basados en el tema
            if theme == 'light':
                mag_color = '#00BFFF'  # Cyan más oscuro para light theme
                phase_color = '#FF1493'  # Pink más oscuro para light theme
                nyquist_color = '#FF8C00'  # Orange más oscuro para light theme
                bg_color = '#FFFFFF'
                grid_color = '#E0E0E0'
                text_color = '#333333'
            else:  # dark theme
                mag_color = '#00FFFF'  # Cyan brillante para dark theme
                phase_color = '#FF69B4'  # Pink para dark theme
                nyquist_color = '#FFA500'  # Orange para dark theme
                bg_color = '#0D213A'
                grid_color = '#1F3D68'
                text_color = '#6495ED'

            bode_fig = go.Figure()
            bode_fig.add_trace(go.Scatter(
                x=bode_data["frequencies"],
                y=bode_data["magnitude_db"],
                mode="lines",
                name="Magnitud |Z|",
                line=dict(color=mag_color, width=2),
                yaxis="y1"
            ))
            bode_fig.add_trace(go.Scatter(
                x=bode_data["frequencies"],
                y=bode_data["phase_deg"],
                mode="lines",
                name="Fase φ",
                line=dict(color=phase_color, width=2),
                yaxis="y2"
            ))

            bode_fig.update_layout(
                title={"text": f"Diagrama de Bode - {CIRCUIT_INFO[circuit_type]['name']}", "font": {"size": 16, "color": text_color}},
                xaxis=dict(
                    title="Frecuencia (Hz)", 
                    type="log", 
                    showgrid=True,
                    gridcolor=grid_color,
                    linecolor=text_color,
                    tickcolor=text_color,
                    tickfont=dict(color=text_color),
                    title_font=dict(color=text_color)
                ),
                yaxis=dict(
                    title=dict(text="Magnitud |Z| (dB)", font=dict(color=mag_color)), 
                    tickfont={"color": mag_color}, 
                    side="left",
                    showgrid=True,
                    gridcolor=grid_color,
                    linecolor=text_color,
                    tickcolor=text_color,
                    title_font=dict(color=text_color)
                ),
                yaxis2=dict(
                    title=dict(text="Fase φ (°)", font=dict(color=phase_color)), 
                    tickfont={"color": phase_color}, 
                    anchor="x", 
                    overlaying="y", 
                    side="right",
                    showgrid=False,
                    linecolor=text_color,
                    tickcolor=text_color,
                    title_font=dict(color=text_color)
                ),
                legend=dict(x=0.7, y=0.95),
                height=450,
                margin=dict(l=60, r=60, t=50, b=50),
                plot_bgcolor=bg_color,
                paper_bgcolor=bg_color,
                font=dict(color=text_color, size=12, family="Arial, sans-serif")
            )

            # Crear gráfico de Nyquist con colormap jet basado en frecuencia
            nyquist_fig = go.Figure()

            # Obtener frecuencias para el colormap
            frequencies = nyquist_data["frequencies"] if "frequencies" in nyquist_data else calc.frequencies

            # Crear la traza principal con colormap jet
            nyquist_fig.add_trace(go.Scatter(
                x=nyquist_data["real"],
                y=-nyquist_data["imaginary"],  # Usamos -Z'' para la parte imaginaria
                mode="lines+markers",
                name="Z(jω)",
                line=dict(
                    color=nyquist_color,
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
                title={"text": f"Diagrama de Nyquist - {CIRCUIT_INFO[circuit_type]['name']}", "font": {"size": 14, "color": text_color}},
                xaxis=dict(
                    title="Parte Real Z' (Ω)",
                    showgrid=True,
                    zeroline=True,
                    autorange=True,
                    gridcolor=grid_color,
                    linecolor=text_color,
                    tickcolor=text_color,
                    tickfont=dict(color=text_color),
                    title_font=dict(color=text_color)
                ),
                yaxis=dict(
                    title="Parte Imaginaria -Z'' (Ω)",
                    showgrid=True,
                    zeroline=True,
                    autorange=True,
                    gridcolor=grid_color,
                    linecolor=text_color,
                    tickcolor=text_color,
                    tickfont=dict(color=text_color),
                    title_font=dict(color=text_color)
                ),
                height=450,
                margin=dict(l=60, r=60, t=50, b=50),
                plot_bgcolor=bg_color,
                paper_bgcolor=bg_color,
                font=dict(color=text_color, size=12, family="Arial, sans-serif")
            )

            info_content = [
                html.H6(CIRCUIT_INFO[circuit_type]["name"], className="text-primary mb-2"),
                html.P(CIRCUIT_INFO[circuit_type]["description"], className="text-muted small mb-3"),
                html.P([html.Code(CIRCUIT_INFO[circuit_type]["formula"])], className="mb-3")
            ]

            return bode_fig, nyquist_fig, html.Div(info_content)

        except Exception as e:
            safe_print(f"❌ Error: {e}")
            # Definir colores para el error basados en el tema
            if theme == 'light':
                bg_color = '#FFFFFF'
                text_color = '#333333'
            else:
                bg_color = '#0D213A'
                text_color = '#6495ED'
                
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
                    font=dict(size=14, color=text_color)
                )],
                plot_bgcolor=bg_color,
                paper_bgcolor=bg_color,
                font=dict(color=text_color, size=12, family="Arial, sans-serif"),
                title_font=dict(color=text_color, size=16)
            )
            return empty_fig, empty_fig, html.Div([html.P("Error en el cálculo")])

    @app.callback(
        [Output("simulator-theme-store", "data"),
         Output("simulator-theme-icon", "className"),
         Output("simulator-theme-text", "children")],
        [Input("simulator-theme-toggle", "n_clicks")],
        [State("simulator-theme-store", "data")],
        prevent_initial_call=True
    )
    def toggle_simulator_theme(n_clicks, theme_data):
        """Alterna entre tema oscuro y claro para los gráficos del simulador"""
        if theme_data is None:
            theme_data = {"theme": "dark"}
        
        current_theme = theme_data.get("theme", "dark")
        new_theme = "light" if current_theme == "dark" else "dark"
        
        # Actualizar icono y texto
        if new_theme == "light":
            icon_class = "fas fa-sun"
            text = "Tema Claro"
        else:
            icon_class = "fas fa-moon"
            text = "Tema Oscuro"
        
        safe_print(f"🎨 Cambiando tema del simulador: {current_theme} → {new_theme}")
        
        return {"theme": new_theme}, icon_class, text

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