"""
Servidor de producción para el simulador RLC
"""
from waitress import serve
from app import server

if __name__ == '__main__':
    print("╔════════════════════════════════════════════════════════════╗")
    print("║        Simulador RLC - Servidor de Producción             ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("\n🚀 Servidor iniciado en: http://localhost:8050")
    print("📊 Accede a la aplicación para visualizar circuitos RLC")
    print("\n⚡ Presiona CTRL+C para detener el servidor\n")
    
    serve(server, host='0.0.0.0', port=8050, threads=4)
