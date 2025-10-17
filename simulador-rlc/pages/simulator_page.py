"""
Página principal del Simulador RLC
Usando el estilo de la plantilla Volt
"""
from dash import html, Input, Output, State, register_page
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

from .common.sidebar import sideBar
from .common.footer import footer

from .simulator.components import (
    circuit_selector_card,
    resistance_input_card,
    inductance_input_card,
    capacitance_input_card,
    frequency_range_card,
    bode_plot_card,
    nyquist_plot_card,
    impedance_info_card
)
from .simulator.impedance_calculator import ImpedanceCalculator, get_circuit_info

import numpy as np

def format_frequency(f):
    if f >= 1000000:
        return f"{f/1000000:.3f} MHz"
    elif f >= 1000:
        return f"{f/1000:.3f} kHz"
    else:
        return f"{f:.3f} Hz"

def register_simulator_page(app):
    register_page(
        __name__,
        path="/",
        title="Simulador RLC",
        name="Simulador RLC",
        layout=layout
    )
    register_callbacks(app)

CIRCUIT_INFO = get_circuit_info()

layout = html.Div([
    sideBar(),
    html.Div([
        html.Div(
            className="container-fluid py-4",
            children=[
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
    ],
    className="main-content position-relative bg-gray-100 max-height-vh-100 h-100",
    id="main-content"
    ),
    footer()
])

def register_callbacks(app):
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
        [Output("bode-plot", "figure"),
         Output("nyquist-plot", "figure"),
         Output("impedance-info", "children")],
        [Input("calculate-btn", "n_clicks"),
         Input("circuit-type", "value"),
         Input("resistance-input", "value"),
         Input("inductance-input", "value"),
         Input("capacitance-input", "value"),
         Input("freq-start", "value"),
         Input("freq-end", "value"),
         Input("freq-points", "value")],
        prevent_initial_call=False
    )
    def calculate_impedance(n_clicks, circuit_type, R, L, C, f_start, f_end, n_points):
        print(f"🚀 BOTÓN PRESIONADO: n_clicks = {n_clicks}")
        print(f"📊 Datos recibidos: circuit_type={circuit_type}, R={R}, L={L}, C={C}")
        
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
            
            bode_fig = go.Figure()
            bode_fig.add_trace(go.Scatter(
                x=bode_data["frequencies"],
                y=bode_data["magnitude_db"],
                mode="lines",
                name="Magnitud |Z|",
                line=dict(color="blue", width=2),
                yaxis="y1"
            ))
            bode_fig.add_trace(go.Scatter(
                x=bode_data["frequencies"],
                y=bode_data["phase_deg"],
                mode="lines",
                name="Fase φ",
                line=dict(color="red", width=2),
                yaxis="y2"
            ))
            
            bode_fig.update_layout(
                title={"text": f"Diagrama de Bode - {CIRCUIT_INFO[circuit_type]["name"]}", "font": {"size": 16}},
                xaxis=dict(title="Frecuencia (Hz)", type="log", showgrid=True),
                yaxis=dict(title=dict(text="Magnitud |Z| (dB)", font=dict(color="blue")), tickfont={"color": "blue"}, side="left"),
                yaxis2=dict(title=dict(text="Fase φ (°)", font=dict(color="red")), tickfont={"color": "red"}, anchor="x", overlaying="y", side="right"),
                legend=dict(x=0.7, y=0.95),
                height=450,
                margin=dict(l=60, r=60, t=50, b=50)
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
                    color="darkblue",
                    width=2
                ),
                marker=dict(
                    color=frequencies,
                    colorscale='Jet',
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
                title={"text": f"Diagrama de Nyquist - {CIRCUIT_INFO[circuit_type]["name"]}", "font": {"size": 14}},
                xaxis=dict(title="Parte Real Z' (Ω)"),
                yaxis=dict(title="Parte Imaginaria -Z'' (Ω)"),
                height=450,
                margin=dict(l=60, r=60, t=50, b=50)
            )
            
            info_content = [
                html.H6(CIRCUIT_INFO[circuit_type]["name"], className="text-primary mb-2"),
                html.P(CIRCUIT_INFO[circuit_type]["description"], className="text-muted small mb-3"),
                html.P([html.Code(CIRCUIT_INFO[circuit_type]["formula"])], className="mb-3")
            ]
            
            return bode_fig, nyquist_fig, html.Div(info_content)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            empty_fig = go.Figure()
            return empty_fig, empty_fig, html.Div([html.P("Error en el cálculo")])
