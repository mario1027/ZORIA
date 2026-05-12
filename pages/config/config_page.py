"""
ZORIA Config Page  –  Configuración / Settings
Idioma y preferencias de la aplicación.

Flujo de persistencia de idioma:
  1. El usuario hace clic en una tarjeta  → escribe a cfg-pending-lang (local, sesión).
  2. [Guardar configuración] → copia cfg-pending-lang → lang-store (localStorage global).
  3. Callback global serve_translations reacciona al cambio de lang-store
     → actualiza lang-translations-store → apply_i18n → ZORIA_I18N.apply() → DOM.
  4. Al volver a esta página:
     • init_pending_from_store lee lang-store → cfg-pending-lang → sync_lang_cards
       aplica la clase activa en la tarjeta correcta vía Dash output (no JS puro).
"""
import logging

from dash import html, dcc, register_page, ctx, ALL
from dash.exceptions import PreventUpdate
from lib.i18n import LANGUAGES

from pages.common.sidebar import sideBar
from pages.common.mobile_nav import mobileNavBar
from pages.common.footer import footer
from pages.common.floating_terminal_button import floating_terminal_button

logger = logging.getLogger(__name__)

register_page(
    __name__,
    path='/config',
    title='Configuración — ZORIA',
    name='config',
)


# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════

def _card(icon_cls, icon_color_cls, title_key, subtitle_key, *children, card_id=None):
    kw = {'className': 'cfg-card'}
    if card_id:
        kw['id'] = card_id
    return html.Div([
        html.Div([
            html.Div(html.I(className=icon_cls),
                     className=f'cfg-card-icon {icon_color_cls}'),
            html.Div([
                html.P('', className='cfg-card-title mb-0', **{'data-i18n': title_key}),
                html.P('', className='cfg-card-subtitle',   **{'data-i18n': subtitle_key}),
            ]),
        ], className='cfg-card-header'),
        *children,
    ], **kw)


def _flabel(i18n_key, icon_cls=None):
    ch = []
    if icon_cls:
        ch.append(html.I(className=f'{icon_cls} me-2'))
    ch.append(html.Span('', **{'data-i18n': i18n_key}))
    return html.Label(ch, className='cfg-form-label d-block mb-1')


# ══════════════════════════════════════════════════════════════
#  SECTION: LANGUAGE
# ══════════════════════════════════════════════════════════════

def language_section():
    """
    Tarjetas de idioma.
    IDs: {'type': 'cfg-lang-card', 'index': code}  — NO usan el patrón global
    'lang-btn' para que el click NO escriba directamente a lang-store.
    El botón Guardar es quien aplica el cambio de idioma al sistema global.
    """
    native = {'es': 'Español', 'en': 'English', 'pt': 'Português',
              'zh': '中文',    'ru': 'Русский',  'de': 'Deutsch'}
    under  = {'es': 'Spanish', 'en': 'Inglés',  'pt': 'Portugués',
              'zh': 'Chino',   'ru': 'Ruso',    'de': 'Alemán'}

    cards = [
        html.Button([
            html.Span(meta['flag'], className='lang-card__flag'),
            html.Span(native[code], className='lang-card__name'),
            html.Span(under[code],  className='lang-card__native'),
        ],
        id={'type': 'cfg-lang-card', 'index': code},
        className='lang-card',
        **{'data-lang': code},
        n_clicks=0)
        for code, meta in LANGUAGES.items()
    ]

    return _card(
        'fas fa-globe', 'cfg-card-icon--purple',
        'config.sec_lang', 'config.sec_lang_sub',
        html.Div(cards, className='lang-cards-grid'),
        # Hint
        html.P('', className='text-muted small mt-3 mb-0',
               **{'data-i18n': 'config.save_hint'}),
        # Indicador de cambios pendientes (oculto hasta que se modifica)
        html.Div(id='cfg-unsaved-indicator', className='mt-2',
                 style={'display': 'none'}),
    )


# ══════════════════════════════════════════════════════════════
#  SECTION: PREFERENCES
# ══════════════════════════════════════════════════════════════

def preferences_section():
    return _card(
        'fas fa-paint-brush', 'cfg-card-icon--green',
        'config.sec_prefs', 'config.sec_prefs_sub',

        # Chart theme
        html.Div([
            _flabel('config.chart_theme', 'fas fa-palette'),
            html.Div([
                html.Button([
                    html.Span('', className='theme-option__icon d-block'),
                    html.Span('', className='theme-option__label',
                              **{'data-i18n': 'config.theme_dark'}),
                ], id='cfg-theme-dark-btn', className='theme-option',
                   n_clicks=0, **{'data-theme': 'dark'}),
                html.Button([
                    html.Span('', className='theme-option__icon d-block'),
                    html.Span('', className='theme-option__label',
                              **{'data-i18n': 'config.theme_light'}),
                ], id='cfg-theme-light-btn', className='theme-option',
                   n_clicks=0, **{'data-theme': 'light'}),
            ], className='theme-toggle-options'),
        ], className='mb-4'),

        # Auto-connect
        html.Div([
            _flabel('config.autoconn', 'fas fa-wifi'),
            html.Div([
                html.Button([
                    html.I(className='fas fa-check me-2'),
                    html.Span('', **{'data-i18n': 'config.autoconn_on'}),
                ], id='cfg-autoconn-on',
                   className='btn btn-sm btn-outline-success me-2', n_clicks=0),
                html.Button([
                    html.I(className='fas fa-times me-2'),
                    html.Span('', **{'data-i18n': 'config.autoconn_off'}),
                ], id='cfg-autoconn-off',
                   className='btn btn-sm btn-outline-secondary', n_clicks=0),
            ]),
            html.Div(id='cfg-prefs-feedback', className='mt-3'),
        ]),
    )


# ══════════════════════════════════════════════════════════════
#  LAYOUT
# ══════════════════════════════════════════════════════════════

layout = html.Div([
    sideBar(),
    mobileNavBar(),

    html.Main([
        html.Div([
            # ── Header (igual que dashboard/simulador) ────────────
            html.Div([
                html.Div([
                    html.H2([
                        html.I(className='fas fa-sliders-h me-2'),
                        html.Span('', **{'data-i18n': 'config.page_title'}),
                    ], className='h3 mb-0'),
                    html.P('', className='text-muted mb-0 mt-1',
                           **{'data-i18n': 'config.page_subtitle'}),
                ], className='col-12 col-md-8 mb-2 mb-md-0'),
            ], className='row align-items-center py-4'),

            # ── Cards ─────────────────────────────────────────────
            html.Div([
                html.Div([language_section()],    className='col-12 col-xl-7'),
                html.Div([preferences_section()], className='col-12 col-xl-5'),
            ], className='row'),

            dcc.Store(id='cfg-init', data=0),
            # storage_type='memory' → nunca persiste entre navegaciones, siempre
            # se inicializa limpio desde los stores globales (lang-store, theme-store,
            # autoconn-store). Esto evita que sessionStorage devuelva un valor
            # obsoleto antes de que el callback de init se ejecute.
            dcc.Store(id='cfg-pending-lang',     storage_type='memory', data=None),
            dcc.Store(id='cfg-pending-theme',    storage_type='memory', data=None),
            dcc.Store(id='cfg-pending-autoconn', storage_type='memory', data=None),
            dcc.Store(id='cfg-cards-sync', data=0),

            # ── Botón Guardar (fila separada, ancho completo) ──────────────
            html.Div([
                html.Div([
                    html.Button([
                        html.I(className='fas fa-save me-2'),
                        html.Span('', **{'data-i18n': 'config.save_btn'}),
                    ], id='cfg-save-btn',
                       className='btn btn-primary btn-lg px-5',
                       n_clicks=0),
                    html.Div(id='cfg-save-feedback', className='mt-3 text-center'),
                ], className='d-flex flex-column align-items-center py-4'),
            ], className='row'),
        ], className='container-fluid px-4 pb-4'),

    ], className='main-content w-100'),

    footer(),
    floating_terminal_button(),

], className='sc-chart d-flex flex-column min-vh-100')


# ══════════════════════════════════════════════════════════════
#  CALLBACKS
# ══════════════════════════════════════════════════════════════

def register_callbacks(app):
    from dash import Input, Output, State

    # ──────────────────────────────────────────────────────────────────────────
    # 1. INIT: Al cargar /config, copia los valores guardados a los stores
    #    pendientes (memory). storage_type='memory' garantiza que este callback
    #    siempre gana — no hay valor previo en sessionStorage que lo pise.
    # ──────────────────────────────────────────────────────────────────────────
    app.clientside_callback(
        """
        function(_init, saved_lang, saved_theme, saved_autoconn) {
            return [
                saved_lang    || 'es',
                saved_theme   || 'dark',
                saved_autoconn != null ? saved_autoconn : false
            ];
        }
        """,
        Output('cfg-pending-lang',     'data'),
        Output('cfg-pending-theme',    'data'),
        Output('cfg-pending-autoconn', 'data'),
        Input('cfg-init',   'data'),
        State('lang-store',     'data'),
        State('theme-store',    'data'),
        State('autoconn-store', 'data'),
        prevent_initial_call=False,
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 1b. REHYDRATE: Si los stores globales cambian (guardar o cambio externo),
    #     reflejarlo en los stores pending para que la UI de config no quede
    #     desincronizada del estado real de la app.
    # ──────────────────────────────────────────────────────────────────────────
    @app.callback(
        Output('cfg-pending-lang', 'data', allow_duplicate=True),
        Output('cfg-pending-theme', 'data', allow_duplicate=True),
        Output('cfg-pending-autoconn', 'data', allow_duplicate=True),
        Input('lang-store', 'data'),
        Input('theme-store', 'data'),
        Input('autoconn-store', 'data'),
        prevent_initial_call=True,
    )
    def sync_pending_from_global(saved_lang, saved_theme, saved_autoconn):
        return (
            saved_lang or 'es',
            saved_theme or 'dark',
            saved_autoconn if saved_autoconn is not None else False,
        )

    # ──────────────────────────────────────────────────────────────────────────
    # 2. IDIOMA: Clic en tarjeta → actualiza cfg-pending-lang
    # ──────────────────────────────────────────────────────────────────────────
    @app.callback(
        Output('cfg-pending-lang', 'data', allow_duplicate=True),
        Input({'type': 'cfg-lang-card', 'index': ALL}, 'n_clicks'),
        prevent_initial_call=True,
    )
    def pick_lang_card(n_clicks_list):
        if not ctx.triggered_id:
            raise PreventUpdate
        trig = ctx.triggered_id
        if isinstance(trig, dict) and trig.get('type') == 'cfg-lang-card':
            return trig['index']
        raise PreventUpdate

    # ──────────────────────────────────────────────────────────────────────────
    # 3. SYNC VISUAL: Sincroniza clases activas en tarjetas de idioma + indicador
    # ──────────────────────────────────────────────────────────────────────────
    app.clientside_callback(
        """
        function(pending_lang, pending_theme, pending_autoconn,
                 saved_lang, saved_theme, saved_autoconn) {

            var lang    = pending_lang    || saved_lang    || 'es';
            var theme   = pending_theme   || saved_theme   || 'dark';
            var autoconn = pending_autoconn != null ? pending_autoconn
                         : (saved_autoconn != null ? saved_autoconn : false);

            /* ── Tarjetas de idioma ── */
            document.querySelectorAll('.lang-card').forEach(function(btn) {
                btn.classList.toggle('lang-card--active',
                    btn.getAttribute('data-lang') === lang);
            });

            /* ── Botones de tema ── */
            document.querySelectorAll('.theme-option').forEach(function(btn) {
                btn.classList.toggle('theme-option--active',
                    btn.getAttribute('data-theme') === theme);
            });

            /* ── Botones de autoconn ── */
            var btnOn  = document.getElementById('cfg-autoconn-on');
            var btnOff = document.getElementById('cfg-autoconn-off');
            if (btnOn)  btnOn.className  = autoconn
                ? 'btn btn-sm btn-success me-2'
                : 'btn btn-sm btn-outline-success me-2';
            if (btnOff) btnOff.className = autoconn
                ? 'btn btn-sm btn-outline-secondary'
                : 'btn btn-sm btn-secondary';

            /* ── Indicador de cambios sin guardar ── */
            var changed = (lang !== (saved_lang || 'es'))
                       || (theme !== (saved_theme || 'dark'))
                       || (autoconn !== !!(saved_autoconn));
            var indicator = document.getElementById('cfg-unsaved-indicator');
            if (indicator) {
                indicator.style.display = changed ? 'block' : 'none';
                if (changed) {
                    var dict = window.ZORIA_TRANSLATIONS || {};
                    indicator.textContent = dict['config.unsaved_hint'] || '● Cambios sin guardar';
                    indicator.className = 'mt-2 text-warning small fw-bold';
                }
            }
            return 1;
        }
        """,
        Output('cfg-cards-sync', 'data'),
        Input('cfg-pending-lang',     'data'),
        Input('cfg-pending-theme',    'data'),
        Input('cfg-pending-autoconn', 'data'),
        Input('lang-store',     'data'),
        Input('theme-store',    'data'),
        Input('autoconn-store', 'data'),
        prevent_initial_call=False,
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 4. TEMA: Clic en botón → actualiza cfg-pending-theme (NO theme-store directo)
    # ──────────────────────────────────────────────────────────────────────────
    app.clientside_callback(
        """
        function(dark_n, light_n) {
            var ctx_obj = window.dash_clientside.callback_context;
            if (!ctx_obj || !ctx_obj.triggered || ctx_obj.triggered.length === 0)
                return window.dash_clientside.no_update;
            var tid = ctx_obj.triggered[0].prop_id;
            return tid.includes('cfg-theme-dark-btn') ? 'dark' : 'light';
        }
        """,
        Output('cfg-pending-theme', 'data', allow_duplicate=True),
        Input('cfg-theme-dark-btn',  'n_clicks'),
        Input('cfg-theme-light-btn', 'n_clicks'),
        prevent_initial_call=True,
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 5. AUTO-CONNECT: Clic → actualiza cfg-pending-autoconn (NO autoconn-store directo)
    # ──────────────────────────────────────────────────────────────────────────
    @app.callback(
        Output('cfg-pending-autoconn', 'data', allow_duplicate=True),
        Input('cfg-autoconn-on',  'n_clicks'),
        Input('cfg-autoconn-off', 'n_clicks'),
        prevent_initial_call=True,
    )
    def pick_autoconn(on_n, off_n):
        if not ctx.triggered_id:
            raise PreventUpdate
        return ctx.triggered_id == 'cfg-autoconn-on'

    # ──────────────────────────────────────────────────────────────────────────
    # 6. GUARDAR: Escribe los 3 pending stores → stores globales de una vez.
    #    Esto dispara serve_translations → apply_i18n → DOM para el idioma.
    # ──────────────────────────────────────────────────────────────────────────
    @app.callback(
        Output('lang-store',     'data', allow_duplicate=True),
        Output('theme-store',    'data', allow_duplicate=True),
        Output('autoconn-store', 'data', allow_duplicate=True),
        Output('cfg-save-feedback',       'children'),
        Output('cfg-unsaved-indicator',   'style'),
        Input('cfg-save-btn', 'n_clicks'),
        State('cfg-pending-lang',     'data'),
        State('cfg-pending-theme',    'data'),
        State('cfg-pending-autoconn', 'data'),
        State('lang-store',     'data'),
        State('theme-store',    'data'),
        State('autoconn-store', 'data'),
        prevent_initial_call=True,
    )
    def save_config(n_clicks, p_lang, p_theme, p_autoconn,
                    s_lang, s_theme, s_autoconn):
        if not n_clicks:
            raise PreventUpdate
        lang    = p_lang    or s_lang    or 'es'
        theme   = p_theme   or s_theme   or 'dark'
        autoconn = p_autoconn if p_autoconn is not None else (s_autoconn or False)
        feedback = html.Div([
            html.I(className='fas fa-check-circle me-2 text-success'),
            html.Span('', **{'data-i18n': 'config.save_ok'}),
        ], className='text-success fw-bold')
        return lang, theme, autoconn, feedback, {'display': 'none'}


def register_config_page(app):
    register_callbacks(app)