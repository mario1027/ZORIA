"""
Iconos SVG para componentes electrónicos RLC
"""

# Rutas de los iconos de componentes
COMPONENT_ICONS = {
    'resistor': '/assets/img/components/resistor.svg',
    'inductor': '/assets/img/components/inductor.svg', 
    'capacitor': '/assets/img/components/capacitor.svg'
}

def get_component_icon(component_type):
    """
    Obtiene la ruta del icono para un tipo de componente
    
    Args:
        component_type (str): Tipo de componente ('R', 'L', 'C')
        
    Returns:
        str: Ruta del icono SVG
    """
    icon_map = {
        'R': COMPONENT_ICONS['resistor'],
        'L': COMPONENT_ICONS['inductor'],
        'C': COMPONENT_ICONS['capacitor']
    }
    return icon_map.get(component_type, '')

def get_component_icon_element(component_type, className="", style=None):
    """
    Crea un elemento img con el icono del componente
    
    Args:
        component_type (str): Tipo de componente ('R', 'L', 'C')
        className (str): Clases CSS adicionales
        style (dict): Estilos CSS adicionales
        
    Returns:
        html.Img: Elemento de imagen con el icono
    """
    from dash import html
    
    icon_src = get_component_icon(component_type)
    if not icon_src:
        return html.Span()  # Retorna elemento vacío si no hay icono
    
    default_style = {
        'width': '24px',
        'height': '24px',
        'filter': 'invert(1)' if 'text-white' in className else 'none'
    }
    
    if style:
        default_style.update(style)
    
    return html.Img(
        src=icon_src,
        className=className,
        style=default_style,
        alt=f"Icono {component_type}"
    )