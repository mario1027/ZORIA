"""
Status Bar ZORIA — Persistent top bar (24px)
Device, acquisition, and live data indicators.
"""
from dash import html
from lib.i18n import t as i18n_t


def status_bar(lang: str = "es"):
    """Create the persistent status bar component."""
    return html.Div(
        [
            # Left: device status
            html.Div(
                [
                    html.Span(
                        className="status-dot",
                        id="status-bar-device-dot",
                    ),
                    html.Span(
                        i18n_t("conn.disconnected", lang),
                        id="status-bar-device-text",
                        className="status-label",
                    ),
                ],
                className="status-group",
            ),
            # Center: acquisition state
            html.Div(
                [
                    html.Span(
                        className="status-dot status-dot-acquisition",
                        id="status-bar-acq-dot",
                    ),
                    html.Span(
                        i18n_t("dash.status.ready", lang),
                        id="status-bar-acq-text",
                        className="status-label",
                    ),
                ],
                className="status-group",
            ),
            # Right: live data indicator
            html.Div(
                [
                    html.Span(
                        className="status-dot status-dot-live",
                        id="status-bar-live-dot",
                    ),
                    html.Span(
                        i18n_t("generic.loading", lang),
                        id="status-bar-live-text",
                        className="status-label",
                    ),
                ],
                className="status-group",
            ),
        ],
        id="zoria-status-bar",
        className="status-bar",
    )
