"""
Botón flotante para abrir el terminal CLI desde cualquier página.
"""
from dash import html

def floating_terminal_button():
    """
    Crea un botón flotante en la esquina inferior derecha
    para abrir rápidamente el terminal CLI.
    """
    return html.Div([
        # Botón flotante principal
        html.Button([
            html.I(className="fas fa-terminal")
        ],
        id="floating-terminal-btn",
        className="floating-terminal-btn",
        title="Abrir Terminal CLI (Ctrl+`)"
        ),
        
        # Tooltip
        html.Span(
            "Terminal",
            className="floating-terminal-tooltip"
        )
    ], className="floating-terminal-container")


def floating_terminal_styles():
    """
    Retorna los estilos CSS para el botón flotante.
    Agregar a assets/css/navigation.css
    """
    return """
    /* Contenedor del botón flotante */
    .floating-terminal-container {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 9998;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
    }

    /* Botón flotante */
    .floating-terminal-btn {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: linear-gradient(135deg, #00ff64 0%, #00cc50 100%);
        border: none;
        color: #0a0a0a;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 
            0 4px 15px rgba(0, 255, 100, 0.4),
            0 0 0 1px rgba(0, 255, 100, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .floating-terminal-btn:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 
            0 8px 25px rgba(0, 255, 100, 0.5),
            0 0 0 2px rgba(0, 255, 100, 0.3);
    }

    .floating-terminal-btn:active {
        transform: translateY(-1px) scale(0.98);
    }

    /* Tooltip */
    .floating-terminal-tooltip {
        background: #1a1a1a;
        color: #00ff64;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-family: 'JetBrains Mono', monospace;
        opacity: 0;
        transform: translateY(10px);
        transition: all 0.3s ease;
        pointer-events: none;
        white-space: nowrap;
        border: 1px solid #333;
    }

    .floating-terminal-container:hover .floating-terminal-tooltip {
        opacity: 1;
        transform: translateY(0);
    }

    /* Animación de pulso */
    @keyframes terminal-pulse {
        0% {
            box-shadow: 0 4px 15px rgba(0, 255, 100, 0.4);
        }
        50% {
            box-shadow: 0 4px 25px rgba(0, 255, 100, 0.6);
        }
        100% {
            box-shadow: 0 4px 15px rgba(0, 255, 100, 0.4);
        }
    }

    .floating-terminal-btn {
        animation: terminal-pulse 2s infinite;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .floating-terminal-container {
            bottom: 20px;
            right: 20px;
        }
        
        .floating-terminal-btn {
            width: 48px;
            height: 48px;
            font-size: 20px;
        }
    }
    """
