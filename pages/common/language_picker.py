"""
pages/common/language_picker.py  –  Selector de idioma ZORIA
Renderiza botones con banderas para elegir ES/EN/PT/ZH/RU/DE.
El dcc.Store(id='lang-store') se define en app.py (layout global).
"""

from dash import html
from lib.i18n import LANGUAGES, DEFAULT_LANG

def language_picker() -> html.Div:
    """
    Componente de selección de idioma.
    Al hacer clic en una bandera + nombre se actualiza 'lang-store'.
    El componente es responsive: en móvil sólo muestra la bandera.
    """
    buttons = []
    for code, meta in LANGUAGES.items():
        buttons.append(
            html.Button(
                children=[
                    html.Span(meta['flag'], className='lang-flag'),
                    html.Span(meta['label'], className='lang-name'),
                ],
                id={'type': 'lang-btn', 'index': code},
                # Sin clase activa en el render de Python: applyTranslations (JS)
                # es el único dueño de lang-btn--active. Si Python marcara
                # DEFAULT_LANG='es', cualquier re-render de Dash restauraría
                # la bandera española aunque el idioma activo sea otro.
                className='lang-btn',
                **{'data-lang': code},
                title=meta['label'],
                n_clicks=0,
            )
        )

    return html.Div(
        children=[
            html.Span(
                '🌐',
                className='lang-globe',
                title='',
                **{'data-i18n-title': 'ui.lang_picker'},
            ),
            html.Div(
                buttons,
                className='lang-btn-group',
                id='lang-btn-group',
            ),
            # Nota: dcc.Store(id='lang-store') se define en app.py (layout global)
        ],
        className='lang-picker',
        id='lang-picker',
    )
