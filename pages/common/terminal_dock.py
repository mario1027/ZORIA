"""
Terminal Dock ZORIA — Persistent bottom dock (~140px)
Replaces the floating terminal FAB with an always-visible dock.
"""
from dash import html, dcc
from lib.i18n import t as i18n_t


def terminal_dock(lang: str = "es"):
    """Create the persistent terminal dock component."""
    return html.Div(
        [
            # Dock header with toggle
            html.Div(
                [
                    html.Div(
                        [
                            html.I(className="fas fa-terminal"),
                            html.Span(
                                i18n_t("terminal.title", lang),
                                className="dock-title",
                            ),
                        ],
                        className="dock-header-left",
                    ),
                    html.Div(
                        [
                            html.Button(
                                html.I(className="fas fa-chevron-down"),
                                id="terminal-dock-collapse-btn",
                                className="dock-collapse-btn",
                                title=i18n_t("ui.minimize", lang),
                            ),
                            html.Button(
                                html.I(className="fas fa-times"),
                                id="terminal-dock-close-btn",
                                className="dock-close-btn",
                                title=i18n_t("ui.close_esc", lang),
                            ),
                        ],
                        className="dock-header-right",
                    ),
                ],
                className="terminal-dock-header",
            ),
            # Terminal output area
            html.Div(
                [
                    html.Div(
                        id="terminal-dock-output",
                        className="terminal-dock-screen",
                        children=[
                            html.Div(
                                [
                                    html.Span(
                                        i18n_t("ui.waiting_connection", lang),
                                        className="dock-waiting-text",
                                    ),
                                ],
                                className="dock-empty-state",
                            ),
                        ],
                    ),
                ],
                className="terminal-dock-body",
            ),
            # Input line
            html.Div(
                [
                    html.Span("\u276f", className="dock-prompt-icon"),
                    dcc.Input(
                        id="terminal-dock-input",
                        type="text",
                        placeholder=i18n_t("terminal.placeholder", lang),
                        autoComplete="off",
                        className="terminal-dock-command-input",
                        n_submit=0,
                    ),
                    html.Button(
                        html.I(className="fas fa-paper-plane"),
                        id="terminal-dock-send-btn",
                        className="dock-send-btn",
                        title=i18n_t("terminal.send", lang),
                    ),
                ],
                className="terminal-dock-input-line",
            ),
        ],
        id="terminal-dock",
        className="terminal-dock",
    )
