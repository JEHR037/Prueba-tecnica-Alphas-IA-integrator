#!/usr/bin/env python3
"""
Script para ejecutar la API RAG actualizada con datos precargados
Usa los endpoints actualizados que incluyen el servicio RAG integrado
"""

import sys
import os
import logging
from pathlib import Path

# Añadir el directorio src al path
sys.path.append(str(Path(__file__).parent / "src"))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Función principal para ejecutar la API actualizada"""
    
    print("=" * 60)
    print("INICIANDO API RAG ACTUALIZADA CON DATOS PRECARGADOS")
    print("=" * 60)
    
    try:
        # Importar la aplicación actualizada
        from infrastructure.web.api.endpoints import app
        
        logger.info("✅ Aplicación importada correctamente")
        
        # Configurar uvicorn
        import uvicorn
        
        # Para usar reload/workers en uvicorn se requiere un import string de la app
        import_string = "infrastructure.web.api.endpoints:app"
        config = {
            "app": import_string,
            "host": "127.0.0.1",
            "port": 8000,
            "reload": True,
            "log_level": "info",
            "access_log": True
        }
        
        print(f"\nServidor iniciando en http://{config['host']}:{config['port']}")
        print("Documentacion disponible en: http://127.0.0.1:8000/docs")
        print("Health check en: http://127.0.0.1:8000/health")
        print("Informacion del sistema en: http://127.0.0.1:8000/")
        print("Estado integrado en: http://127.0.0.1:8000/system/integrated/status")
        
        print("\nENDPOINTS PRINCIPALES:")
        print("  - POST /ask - Pregunta principal con datos precargados")
        print("  - GET  /ask - Pregunta rapida via GET")
        print("  - GET  /system/info - Informacion del sistema")
        print("  - GET  /system/stats - Estadisticas del sistema")
        print("  - GET  /health - Health check")
        
        print("\nCARACTERISTICAS:")
        print("  + Datos precargados de politicas de RRHH")
        print("  + Sistema de embeddings optimizado")
        print("  + Busqueda semantica avanzada")
        print("  + Respuestas contextuales mejoradas")
        print("  + Filtrado por departamento y categoria")
        print("  + Inicializacion automatica del sistema")
        
        print(f"\n{'='*60}")
        print("INICIANDO SERVIDOR...")
        print("   Presiona Ctrl+C para detener")
        print(f"{'='*60}\n")
        
        # Iniciar servidor
        uvicorn.run(**config)
        
    except ImportError as e:
        logger.error(f"ERROR de importacion: {e}")
        logger.error("SOLUCION: Asegurate de tener todas las dependencias instaladas")
        return 1
    except KeyboardInterrupt:
        logger.info("\nServidor detenido por el usuario")
        return 0
    except Exception as e:
        logger.error(f"ERROR inesperado: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
