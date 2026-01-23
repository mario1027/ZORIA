"""
Sistema de breadcrumbs para navegación contextual
"""
from typing import List, Dict
from dash import html, dcc

class BreadcrumbItem:
    """Elemento individual del breadcrumb"""
    def __init__(self, text, href: str = None, active: bool = False):
        self.content = text  # Puede ser string o lista de elementos
        self.href = href
        self.active = active

    def to_html(self) -> html.Li:
        """Convierte a elemento HTML"""
        if self.active or not self.href:
            return html.Li(self.content, className="breadcrumb-item active")
        else:
            return html.Li(
                dcc.Link(self.content, href=self.href, className="breadcrumb-link"),
                className="breadcrumb-item"
            )

class BreadcrumbBuilder:
    """Constructor de breadcrumbs basado en rutas"""

    # Mapeo de rutas a breadcrumbs
    ROUTE_MAP = {
        "/": ["Inicio", "Dashboard ZORIA"],
        "/simulator": ["Inicio", "Simulador RLC", "Análisis de Circuitos"],
        "/simulator#circuits": ["Inicio", "Simulador RLC", "Circuitos"],
        "/simulator#parameters": ["Inicio", "Simulador RLC", "Parámetros"],
        "/simulator#analysis": ["Inicio", "Simulador RLC", "Análisis"],
        "/simulator#results": ["Inicio", "Simulador RLC", "Resultados"],
        "/#connection": ["Inicio", "Dashboard ZORIA", "Conexión"],
        "/#measurements": ["Inicio", "Dashboard ZORIA", "Mediciones"],
        "/#sweeps": ["Inicio", "Dashboard ZORIA", "Barridos"],
        "/#plots": ["Inicio", "Dashboard ZORIA", "Gráficos"]
    }

    @staticmethod
    def build_from_path(current_path: str) -> html.Nav:
        """
        Construye breadcrumbs basados en la ruta actual

        Args:
            current_path: Ruta actual de la aplicación

        Returns:
            Componente de navegación con breadcrumbs
        """
        # Normalizar la ruta (remover fragmentos para matching)
        base_path = current_path.split('#')[0] if '#' in current_path else current_path

        # Obtener la estructura del breadcrumb
        breadcrumb_parts = BreadcrumbBuilder.ROUTE_MAP.get(base_path, ["Inicio", "Página"])

        # Crear elementos del breadcrumb
        breadcrumb_items = []

        for i, part in enumerate(breadcrumb_parts):
            is_last = i == len(breadcrumb_parts) - 1

            if i == 0:  # Siempre "Inicio" con enlace
                item = BreadcrumbItem(part, href="/", active=False)
            elif is_last:  # Último elemento activo
                item = BreadcrumbItem(part, active=True)
            else:
                # Intentar encontrar href para elementos intermedios
                href = BreadcrumbBuilder._get_href_for_part(part)
                item = BreadcrumbItem(part, href=href, active=False)

            breadcrumb_items.append(item.to_html())

        return html.Nav([
            html.Ol(breadcrumb_items, className="breadcrumb bg-transparent mb-0")
        ], **{"aria-label": "breadcrumb"})

    @staticmethod
    def _get_href_for_part(part: str) -> str:
        """Obtiene el href correspondiente para una parte del breadcrumb"""
        href_map = {
            "Dashboard ZORIA": "/",
            "Simulador RLC": "/simulator"
        }
        return href_map.get(part, "#")

def create_contextual_breadcrumbs(current_path: str, context: Dict = None) -> html.Nav:
    """
    Crea breadcrumbs contextuales con información adicional

    Args:
        current_path: Ruta actual
        context: Contexto adicional (opcional)

    Returns:
        Breadcrumbs con contexto
    """
    # Obtener la estructura base del breadcrumb
    base_breadcrumbs = BreadcrumbBuilder.build_from_path(current_path)

    # Si no hay contexto, devolver breadcrumbs base
    if not context:
        return base_breadcrumbs

    # Crear elementos de contexto
    context_items = []

    if "circuit_type" in context:
        context_items.append(
            html.Span(f"Circuito: {context['circuit_type']}",
                     className="badge bg-primary ms-2")
        )

    if "measurement_mode" in context:
        context_items.append(
            html.Span(f"Modo: {context['measurement_mode']}",
                     className="badge bg-info ms-1")
        )

    # Si hay elementos de contexto, crear nuevos breadcrumbs con contexto
    if context_items:
        # Obtener las partes del breadcrumb
        breadcrumb_parts = BreadcrumbBuilder.ROUTE_MAP.get(current_path.split('#')[0], ["Inicio", "Página"])

        # Crear elementos del breadcrumb con contexto en el último elemento
        breadcrumb_items = []

        for i, part in enumerate(breadcrumb_parts):
            is_last = i == len(breadcrumb_parts) - 1

            if i == 0:  # Siempre "Inicio" con enlace
                item = BreadcrumbItem(part, href="/", active=False)
            elif is_last:  # Último elemento activo con contexto
                # Crear un contenedor que incluya el texto y los elementos de contexto
                content = [part]
                content.extend(context_items)
                item = BreadcrumbItem(content, active=True)
            else:
                # Intentar encontrar href para elementos intermedios
                href = BreadcrumbBuilder._get_href_for_part(part)
                item = BreadcrumbItem(part, href=href, active=False)

            breadcrumb_items.append(item.to_html())

        return html.Nav([
            html.Ol(breadcrumb_items, className="breadcrumb bg-transparent mb-0")
        ], **{"aria-label": "breadcrumb"})

    return base_breadcrumbs