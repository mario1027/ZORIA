"""Garantiza que ``dash_spa`` pueda cargar su configuración al importarse.

``dash_spa`` busca obligatoriamente ``config/spa_config.ini``, ``spa_config.ini``
o ``.env`` **en el directorio de trabajo actual** y lanza ``ConfigurationError``
si no los encuentra. Cuando ZORIA está instalado con ``pip install zoria`` y se
ejecuta el comando ``zoria`` desde cualquier carpeta, ese archivo no existe.

Esta utilidad resuelve el problema sin dejar archivos basura en el directorio
del usuario: si la configuración no está en el CWD, importa ``dash_spa`` desde
un directorio temporal que contiene la configuración por defecto empaquetada
(``zoria/config/spa_config.ini``). ``dash_spa`` sólo lee el archivo una vez (al
importarse), por lo que basta con tenerlo presente durante ese primer import.
"""

import os
import shutil
import tempfile
from pathlib import Path

# Rutas que dash_spa.spa_config.read_config() busca en el CWD, en orden.
_CWD_CANDIDATES = ("config/spa_config.ini", "spa_config.ini", ".env")

_PACKAGED_CONFIG = Path(__file__).resolve().parent / "config" / "spa_config.ini"


def ensure_dash_spa() -> None:
    """Importa ``dash_spa`` asegurando que encuentre su ``spa_config.ini``."""
    import sys

    if "dash_spa" in sys.modules:
        return

    if any(os.path.exists(candidate) for candidate in _CWD_CANDIDATES) or \
            not _PACKAGED_CONFIG.exists():
        import dash_spa  # noqa: F401  (configuración del usuario o error original)
        return

    sandbox = tempfile.mkdtemp(prefix="zoria-spa-")
    try:
        target = Path(sandbox) / "config" / "spa_config.ini"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(_PACKAGED_CONFIG, target)

        previous_cwd = os.getcwd()
        os.chdir(sandbox)
        try:
            import dash_spa  # noqa: F401
        finally:
            os.chdir(previous_cwd)
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)
