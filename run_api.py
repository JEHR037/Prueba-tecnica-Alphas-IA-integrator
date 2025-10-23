#!/usr/bin/env python3
"""
Script de inicio para la API RAG Consolidada ALPHAS
"""

import sys
import os
from pathlib import Path

# Añadir el directorio src al path
sys.path.append(str(Path(__file__).parent / "src"))

from infrastructure.web.server import main

if __name__ == "__main__":
    main()
