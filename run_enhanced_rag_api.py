#!/usr/bin/env python3
"""
Script de inicio para la API RAG mejorada con datos precargados
Inicializa automáticamente el sistema con políticas de RRHH
"""

import sys
import os
import asyncio
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
    """Función principal para iniciar la API RAG mejorada"""
    
    print("🔥 INICIANDO API RAG MEJORADA CON DATOS PRECARGADOS 🔥")
    print("=" * 60)
    
    try:
        # Verificar que los archivos necesarios existan
        required_files = [
            "src/infrastructure/web/api/rag_enhanced_endpoints.py",
            "src/infrastructure/data/preloaded_hr_policies.py",
            "src/infrastructure/services/data_loader_service.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            logger.error("❌ Archivos requeridos no encontrados:")
            for file_path in missing_files:
                logger.error(f"   - {file_path}")
            return 1
        
        logger.info("✅ Todos los archivos requeridos encontrados")
        
        # Importar y ejecutar la aplicación
        logger.info("🚀 Iniciando servidor FastAPI...")
        
        import uvicorn
        
        # Configuración del servidor
        config = {
            "app": "infrastructure.web.api.rag_enhanced_endpoints:app",
            "host": "127.0.0.1",
            "port": 8002,
            "reload": True,
            "log_level": "info",
            "access_log": True
        }
        
        logger.info(f"🌐 Servidor iniciando en http://{config['host']}:{config['port']}")
        logger.info("📚 Documentación disponible en: http://127.0.0.1:8002/enhanced/docs")
        logger.info("🔍 Health check en: http://127.0.0.1:8002/enhanced/health")
        logger.info("ℹ️ Información del sistema en: http://127.0.0.1:8002/enhanced")
        
        print("\n🎯 ENDPOINTS PRINCIPALES:")
        print("  • POST /enhanced/ask - Pregunta principal mejorada")
        print("  • GET  /enhanced/ask/quick - Pregunta rápida")
        print("  • POST /enhanced/system/initialize - Inicializar sistema")
        print("  • GET  /enhanced/system/status - Estado del sistema")
        print("  • GET  /enhanced/data/info - Información de datos precargados")
        print("  • GET  /enhanced/search/faq - Buscar en FAQs")
        print("  • GET  /enhanced/categories - Categorías con estadísticas")
        print("  • GET  /enhanced/health - Health check mejorado")
        
        print("\n📋 DATOS PRECARGADOS INCLUIDOS:")
        print("  • Políticas de Beneficios (seguro médico, 401k, etc.)")
        print("  • Políticas de Vacaciones (tiempo libre flexible)")
        print("  • Políticas de Trabajo Remoto (modelo híbrido)")
        print("  • Políticas de Desarrollo Profesional (20% time, capacitación)")
        print("  • Políticas de Diversidad e Inclusión")
        print("  • Políticas de Compensación")
        print("  • Código de Conducta y Ética")
        print("  • Preguntas Frecuentes (FAQs)")
        
        print("\n🔧 FUNCIONALIDADES AVANZADAS:")
        print("  • Carga automática de datos al inicio")
        print("  • Búsqueda optimizada en políticas precargadas")
        print("  • Filtrado por departamento y categoría")
        print("  • Búsqueda específica en FAQs")
        print("  • Health checks detallados")
        print("  • Estadísticas de uso y rendimiento")
        
        print(f"\n{'='*60}")
        print("🚀 INICIANDO SERVIDOR...")
        print("   Presiona Ctrl+C para detener")
        print(f"{'='*60}\n")
        
        # Iniciar servidor
        uvicorn.run(**config)
        
    except KeyboardInterrupt:
        logger.info("\n⏹️ Servidor detenido por el usuario")
        return 0
    except ImportError as e:
        logger.error(f"❌ Error de importación: {e}")
        logger.error("💡 Asegúrate de tener todas las dependencias instaladas")
        return 1
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
