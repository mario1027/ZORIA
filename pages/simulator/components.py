"""
Componentes de formulario para el simulador RLC
Usando el estilo de la plantilla Volt
"""
from dash import html, dcc
from pages.icons.hero import ICON


def circuit_selector_card():
    """Tarjeta con selector de tipo de circuito"""
    return html.Div([
        html.Div([
            html.H5([
                html.Span(ICON.GEAR, className='me-2'),
                html.Span('', **{'data-i18n': 'ui.circuit_select'})
            ], className='card-title mb-4'),

            html.Div([
                html.Label(html.Span('', **{'data-i18n': 'ui.circuit_type'}), className='form-label fw-bold', htmlFor='circuit-type'),
                dcc.Dropdown(
                    id='circuit-type',
                    options=[
                        # ============ CIRCUITOS IDEALES ============
                        {'label': '───────── CIRCUITOS IDEALES ─────────', 'value': 'header_ideal', 'disabled': True},
                        {'label': '─── Componentes Individuales ───', 'value': 'header1', 'disabled': True},
                        {'label': 'Resistor (R)', 'value': 'R'},
                        {'label': 'Inductor (L)', 'value': 'L'},
                        {'label': 'Capacitor (C)', 'value': 'C'},
                        {'label': '─── RC ───', 'value': 'header2', 'disabled': True},
                        {'label': 'RC en Serie', 'value': 'RC_series'},
                        {'label': 'RC en Paralelo', 'value': 'RC_parallel'},
                        {'label': '─── RL ───', 'value': 'header3', 'disabled': True},
                        {'label': 'RL en Serie', 'value': 'RL_series'},
                        {'label': 'RL en Paralelo', 'value': 'RL_parallel'},
                        {'label': '─── LC ───', 'value': 'header4', 'disabled': True},
                        {'label': 'LC en Serie', 'value': 'LC_series'},
                        {'label': 'LC en Paralelo', 'value': 'LC_parallel'},
                        {'label': '─── RLC ───', 'value': 'header5', 'disabled': True},
                        {'label': 'RLC en Serie', 'value': 'RLC_series'},
                        {'label': 'RLC en Paralelo', 'value': 'RLC_parallel'},

                        # ============ CIRCUITOS REALES CON PARÁSITOS ============
                        {'label': '───────── CIRCUITOS REALES (CON PARÁSITOS) ─────────', 'value': 'header_real', 'disabled': True},
                        {'label': '─── Componentes Individuales Reales ───', 'value': 'header1_real', 'disabled': True},
                        {'label': 'Resistor Real (R + parásitos)', 'value': 'R_real'},
                        {'label': 'Inductor Real (L + parásitos)', 'value': 'L_real'},
                        {'label': 'Capacitor Real (C + ESR + ESL)', 'value': 'C_real'},
                        {'label': '─── RC Reales ───', 'value': 'header2_real', 'disabled': True},
                        {'label': 'RC en Serie Real', 'value': 'RC_series_real'},
                        {'label': 'RC en Paralelo Real', 'value': 'RC_parallel_real'},
                        {'label': '─── RL Reales ───', 'value': 'header3_real', 'disabled': True},
                        {'label': 'RL en Serie Real', 'value': 'RL_series_real'},
                        {'label': 'RL en Paralelo Real', 'value': 'RL_parallel_real'},
                        {'label': '─── LC Reales ───', 'value': 'header4_real', 'disabled': True},
                        {'label': 'LC en Serie Real', 'value': 'LC_series_real'},
                        {'label': 'LC en Paralelo Real', 'value': 'LC_parallel_real'},
                        {'label': '─── RLC Reales ───', 'value': 'header5_real', 'disabled': True},
                        {'label': 'RLC en Serie Real', 'value': 'RLC_series_real'},
                        {'label': 'RLC en Paralelo Real', 'value': 'RLC_parallel_real'},
                    ],
                    value='RC_series',
                    clearable=False,
                    className='mb-3'
                ),
            ], className='mb-3'),

            # Descripción del circuito
            html.Div([
                html.Div(id='circuit-description', className='alert alert-info')
            ]),

            # Fórmula
            html.Div([
                html.Small([
                    html.Strong(html.Span('', **{'data-i18n': 'ui.formula'})),
                    html.Span(id='circuit-formula', className='font-monospace')
                ], className='text-muted')
            ])

        ], className='card-body')
    ], className='card border-0 shadow-sm mb-4')


def resistance_input_card():
    """Input para resistencia con icono"""
    return html.Div([
        html.Div([
            html.Label([
                html.Span("", className='me-2'),
                html.Span('', **{'data-i18n': 'ui.resistance_r'})
            ], className='form-label fw-bold', htmlFor='resistance-input'),

            html.Div([
                html.Span([
                    html.I(className='fas fa-omega')
                ], className='input-group-text'),
                dcc.Input(
                    id='resistance-input',
                    type='number',
                    value=1000,
                    className='form-control',
                    placeholder='1 Ω a 10 MΩ',
                    required=False,
                    debounce=True,
                    style={'border': '1px solid #d1d5db', 'box-shadow': 'none'}
                ),
                html.Span("Ω", className='input-group-text')
            ], className='input-group mb-2'),

            html.Small('', className='form-text text-muted', **{'data-i18n': 'ui.sample_res'})
        ], className='card-body')
    ], id='resistance-card', className='card border-0 shadow-sm mb-3')


def inductance_input_card():
    """Input para inductancia con icono"""
    return html.Div([
        html.Div([
            html.Label([
                html.Span("", className='me-2'),
                html.Span('', **{'data-i18n': 'ui.inductance_l'})
            ], className='form-label fw-bold', htmlFor='inductance-input'),

            html.Div([
                html.Span([
                    html.I(className='fas fa-wave-square')
                ], className='input-group-text'),
                dcc.Input(
                    id='inductance-input',
                    type='number',
                    value=0.001,
                    className='form-control',
                    placeholder='1 nH a 100 H',
                    required=False,
                    debounce=True,
                    style={'border': '1px solid #d1d5db', 'box-shadow': 'none'}
                ),
                html.Span("H", className='input-group-text')
            ], className='input-group mb-2'),

            html.Small('', className='form-text text-muted', **{'data-i18n': 'ui.sample_ind'})
        ], className='card-body')
    ], id='inductance-card', className='card border-0 shadow-sm mb-3')


def capacitance_input_card():
    """Input para capacitancia con icono"""
    return html.Div([
        html.Div([
            html.Label([
                html.Span("", className='me-2'),
                html.Span('', **{'data-i18n': 'ui.capacitance_c'})
            ], className='form-label fw-bold', htmlFor='capacitance-input'),

            html.Div([
                html.Span([
                    html.I(className='fas fa-battery-half')
                ], className='input-group-text'),
                dcc.Input(
                    id='capacitance-input',
                    type='number',
                    value=0.000001,
                    className='form-control',
                    placeholder='1 pF a 1 F',
                    required=False,
                    debounce=True,
                    style={'border': '1px solid #d1d5db', 'box-shadow': 'none'}
                ),
                html.Span("F", className='input-group-text')
            ], className='input-group mb-2'),

            html.Small('', className='form-text text-muted', **{'data-i18n': 'ui.sample_cap'})
        ], className='card-body')
    ], id='capacitance-card', className='card border-0 shadow-sm mb-3')


def frequency_range_card():
    """Tarjeta de configuración de rango de frecuencias"""
    return html.Div([
        html.Div([
            html.H5([
                html.Span("", className='me-2'),
                html.Span('', **{'data-i18n': 'ui.range_freq'})
            ], className='card-title mb-3'),

            # Frecuencia inicial
            html.Div([
                html.Label(html.Span('', **{'data-i18n': 'ui.freq_start'}), className='form-label fw-bold', htmlFor='freq-start'),
                html.Div([
                    html.Span([
                        html.I(className='fas fa-play')
                    ], className='input-group-text'),
                    dcc.Input(
                        id='freq-start',
                        type='number',
                        value=0.2,
                        min=0.2,
                        max=10000000,
                        step=0.1,
                        className='form-control',
                        required=False,
                        debounce=True,
                        style={'border': '1px solid #d1d5db', 'box-shadow': 'none'}
                    ),
                    html.Span("Hz", className='input-group-text')
                ], className='input-group mb-1'),
                html.Small("Mín: 0.2 Hz", className='form-text text-muted')
            ], className='mb-3'),

            # Frecuencia final
            html.Div([
                html.Label(html.Span('', **{'data-i18n': 'ui.freq_end'}), className='form-label fw-bold', htmlFor='freq-end'),
                html.Div([
                    html.Span([
                        html.I(className='fas fa-stop')
                    ], className='input-group-text'),
                    dcc.Input(
                        id='freq-end',
                        type='number',
                        value=10000000,
                        min=0.2,
                        max=10000000,
                        step=1,
                        className='form-control',
                        required=False,
                        debounce=True,
                        style={'border': '1px solid #d1d5db', 'box-shadow': 'none'}
                    ),
                    html.Span("Hz", className='input-group-text')
                ], className='input-group mb-1'),
                html.Small("Máx: 10 MHz", className='form-text text-muted')
            ], className='mb-3'),

            # Número de puntos
            html.Div([
                html.Label(html.Span('', **{'data-i18n': 'ui.num_points'}), className='form-label fw-bold', htmlFor='freq-points'),
                html.Div([
                    html.Span([
                        html.I(className='fas fa-circle')
                    ], className='input-group-text'),
                    dcc.Input(
                        id='freq-points',
                        type='number',
                        value=1000,
                        min=10,
                        max=5000,
                        step=10,
                        className='form-control',
                        required=False,
                        debounce=True,
                        style={'border': '1px solid #d1d5db', 'box-shadow': 'none'}
                    )
                ], className='input-group mb-3')
            ]),

            # Botón calcular
            html.Button([
                html.I(className='fas fa-calculator me-2'),
                html.Span('', **{'data-i18n': 'sim.run'}),
            ], id='calculate-btn', n_clicks=0, className='btn btn-primary btn-lg w-100')

        ], className='card-body')
    ], className='card border-0 shadow-sm mb-4')


def bode_plot_card():
    """Tarjeta para el diagrama de Bode"""
    return html.Div([
        html.Div([
            html.H5([
                html.I(className="fas fa-chart-line me-2"),
                html.Span('', **{'data-i18n': 'dash.bode_title'})
            ], className='mb-0 chart-title')
        ], className='d-flex justify-content-between align-items-center card-header border-bottom border-gray-300 p-3'),
        html.Div([
            dcc.Loading(
                id='loading-bode',
                type='circle',
                children=dcc.Graph(
                    id='simulator-bode-plot',
                    config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['lasso2d', 'select2d']
                    },
                    style={'height': '500px'}
                ),
                color='#262B40'
            )
        ], className='card-body p-2')
    ], className='card border-0 shadow h-100')


def nyquist_plot_card():
    """Tarjeta para el diagrama de Nyquist"""
    return html.Div([
        html.Div([
            html.H5([
                html.I(className="fas fa-circle-notch me-2"),
                html.Span('', **{'data-i18n': 'dash.nyquist_title'})
            ], className='mb-0 chart-title')
        ], className='d-flex justify-content-between align-items-center card-header border-bottom border-gray-300 p-3'),
        html.Div([
            dcc.Loading(
                id='loading-nyquist',
                type='circle',
                children=dcc.Graph(
                    id='simulator-nyquist-plot',
                    config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['lasso2d', 'select2d']
                    },
                    style={'height': '500px'}
                ),
                color='#262B40'
            )
        ], className='card-body p-2')
    ], className='card border-0 shadow h-100')


def impedance_info_card():
    """Tarjeta de información de impedancia"""
    return html.Div([
        html.Div([
            html.H5([
                html.I(className="fas fa-info-circle me-2"),
                html.Span('', **{'data-i18n': 'ui.info_impedance'})
            ], className='mb-0')
        ], className='d-flex justify-content-between align-items-center card-header border-bottom border-gray-300 p-3'),
        html.Div([
            html.Div(id='simulator-impedance-info', className='text-center py-4')
        ], className='card-body')
    ], className='card border-0 shadow mb-4')