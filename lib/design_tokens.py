"""
lib/design_tokens.py — ZORIA Design Tokens (programmatic access)

Provides theme-aware color tokens for Plotly charts and Python-side
components that cannot use CSS custom properties directly.

Usage:
    from lib.design_tokens import ZORIA_THEME
    fig = go.Figure()
    fig.update_layout(plot_bgcolor=ZORIA_THEME['dark']['chart_bg'])
"""

ZORIA_THEME = {
    'dark': {
        # Backgrounds
        'bg_deepest': '#020617',
        'bg_primary': '#0F172A',
        'bg_elevated': '#1E293B',
        'bg_surface': '#334155',
        'bg_card': '#1E293B',
        'bg_input': '#0F172A',

        # Text
        'text_primary': '#F8FAFC',
        'text_secondary': '#94A3B8',
        'text_tertiary': '#64748B',
        'text_disabled': '#475569',

        # Borders
        'border': 'rgba(148, 163, 184, 0.12)',
        'border_hover': 'rgba(148, 163, 184, 0.24)',

        # Semantic
        'primary': '#3b82f6',
        'primary_hover': '#2563eb',
        'accent': '#22c55e',
        'accent_glow': '#4ADE80',
        'danger': '#ef4444',
        'warning': '#f59e0b',
        'info': '#3b82f6',

        # Charts (Bode / Nyquist)
        'chart_bg': '#0D213A',
        'chart_grid': '#1F3D68',
        'chart_text': '#6495ED',
        'chart_magnitude': '#00FFFF',
        'chart_phase': '#FF69B4',
        'chart_nyquist': '#FFA500',
        'chart_trigger_palette': [
            '#60a5fa', '#f87171', '#34d399', '#fbbf24', '#a78bfa', '#22d3ee'
        ],

        # Connection
        'conn_connected': '#22c55e',
        'conn_disconnected': '#6b7280',
        'conn_error': '#ef4444',
        'conn_connecting': '#f59e0b',

        # Terminal
        'term_bg_deepest': '#050816',
        'term_bg_surface': '#0a0f1a',
        'term_bg_elevated': '#0e1525',
        'term_accent': '#00c896',
        'term_ice': '#4fd1ff',
        'term_amber': '#d29922',
        'term_red': '#ff6b6b',
    },

    'light': {
        # Backgrounds
        'bg_deepest': '#f8fafc',
        'bg_primary': '#ffffff',
        'bg_elevated': '#f1f5f9',
        'bg_surface': '#e2e8f0',
        'bg_card': '#ffffff',
        'bg_input': '#ffffff',

        # Text
        'text_primary': '#0f172a',
        'text_secondary': '#475569',
        'text_tertiary': '#94a3b8',
        'text_disabled': '#cbd5e1',

        # Borders
        'border': 'rgba(15, 23, 42, 0.1)',
        'border_hover': 'rgba(15, 23, 42, 0.2)',

        # Semantic
        'primary': '#2563eb',
        'primary_hover': '#1d4ed8',
        'accent': '#16a34a',
        'accent_glow': 'rgba(22, 163, 74, 0.2)',
        'danger': '#dc2626',
        'warning': '#d97706',
        'info': '#2563eb',

        # Charts
        'chart_bg': '#FFFFFF',
        'chart_grid': '#E0E0E0',
        'chart_text': '#333333',
        'chart_magnitude': '#00BFFF',
        'chart_phase': '#FF1493',
        'chart_nyquist': '#FF8C00',
        'chart_trigger_palette': [
            '#2563eb', '#dc2626', '#059669', '#d97706', '#7c3aed', '#0891b2'
        ],

        # Connection
        'conn_connected': '#16a34a',
        'conn_disconnected': '#6b7280',
        'conn_error': '#dc2626',
        'conn_connecting': '#d97706',

        # Terminal
        'term_bg_deepest': '#050816',
        'term_bg_surface': '#0a0f1a',
        'term_bg_elevated': '#0e1525',
        'term_accent': '#00c896',
        'term_ice': '#4fd1ff',
        'term_amber': '#d29922',
        'term_red': '#ff6b6b',
    },
}


def get_theme(theme_name: str = 'dark') -> dict:
    """Retorna el diccionario de tokens para el tema indicado.

    Args:
        theme_name: 'dark' o 'light'

    Returns:
        Diccionario con todos los tokens del tema.
    """
    return ZORIA_THEME.get(theme_name, ZORIA_THEME['dark'])


def create_empty_figure(title: str = None, theme: str = 'dark', hint: bool = False) -> 'go.Figure':
    """Crea una figura vacía con estilo consistente usando tokens.

    Args:
        title: Título de la figura (None = usa i18n default).
        theme: 'dark' o 'light'.
        hint: Si True, muestra hint accionable en vez de mensaje genérico.

    Returns:
        Figura Plotly vacía con estilo del tema.
    """
    import plotly.graph_objs as go
    from lib.i18n import t as i18n_t

    if title is None:
        title = i18n_t('dash.empty_no_data')
    t = get_theme(theme)
    msg = i18n_t('dash.empty_hint') if hint else i18n_t('dash.empty_no_data')
    fig = go.Figure()
    fig.update_layout(
        title=title,
        annotations=[dict(
            text=msg,
            showarrow=False,
            xref="paper", yref="paper",
            x=0.5, y=0.45,
            font=dict(size=14, color=t['text_tertiary'])
        )],
        plot_bgcolor=t['chart_bg'],
        paper_bgcolor=t['chart_bg'],
        font=dict(color=t['text_primary'], size=14, family="Fira Sans, Arial, sans-serif"),
        title_font=dict(color=t['text_primary'], size=18)
    )
    return fig