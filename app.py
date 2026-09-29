#!/usr/bin/env python3
"""Punto de entrada legacy: ejecuta ``python app.py`` desde la raíz del repo.

La implementación real vive en ``zoria/app.py``; para instalar desde PyPI
use el comando ``zoria`` en lugar de este archivo.
"""

from zoria.app import main

if __name__ == "__main__":
    main()
