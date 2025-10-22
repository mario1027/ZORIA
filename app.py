import dash
from dash import html, dcc
from dash_spa import DashSPA, page_container
from themes import VOLT
import os
from flask import Flask

external_stylesheets = [
    "https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/chartist/0.11.4/chartist.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.2.0/css/all.min.css",
    "https://cdn.jsdelivr.net/npm/notyf@3/notyf.min.css",
    VOLT,
    "/assets/css/navigation.css",
    "/assets/css/mobile-nav.css"
    ]

external_scripts = [
    "https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/js/bootstrap.bundle.min.js",
    "https://cdn.jsdelivr.net/npm/sweetalert2@11.4.20/dist/sweetalert2.all.min.js",
    "https://cdn.jsdelivr.net/npm/notyf@3/notyf.min.js",
    "https://cdn.jsdelivr.net/npm/vanillajs-datepicker@1.3.4/dist/css/datepicker.min.css"
    ]

def create_app() -> DashSPA:
    """Crear y configurar la aplicación DashSPA"""
    app = DashSPA(__name__,
        prevent_initial_callbacks=True,
        suppress_callback_exceptions=True,
        external_scripts=external_scripts,
        external_stylesheets=external_stylesheets,
        url_base_pathname="/",
        assets_folder='assets',
        title='ADMX2001 Dashboard',
        update_title=None)  # Sin pages_folder, usa el default
    
    # Configurar favicon
    app._favicon = 'logo.png'

    # Importar y registrar páginas
    from pages.dashboard.dashboard_page import register_dashboard_page
    from pages.simulator.simulator_page import register_simulator_page

    register_dashboard_page(app)
    register_simulator_page(app)

    app.layout = page_container
    app.server.config['SECRET_KEY'] = "A secret key"
    return app

# Crear instancia global de la app
app = create_app()

# Para compatibilidad con server.py
if __name__ == "__main__":
    sport = int(os.environ.get("PORT", 8050))
    hostname = os.environ.get("HOSTNAME", "localhost")
    # Desactivar reloader para evitar doble registro de callbacks
    app.run(host=hostname, port=sport, debug=True, use_reloader=False)