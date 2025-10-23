"""
ALPHAS TECHNIQUE TEST IA - Logger Personalizado
Sistema de logging avanzado para captura de errores en middleware FastAPI
"""

import logging
import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, Union
from enum import Enum
from pathlib import Path
import sys
import os

class AlphasLogLevel(Enum):
    """Niveles de log personalizados para ALPHAS TECHNIQUE TEST IA"""
    ALPHAS_DEBUG = "ALPHAS_DEBUG"
    ALPHAS_INFO = "ALPHAS_INFO"
    ALPHAS_WARNING = "ALPHAS_WARNING"
    ALPHAS_ERROR = "ALPHAS_ERROR"
    ALPHAS_CRITICAL = "ALPHAS_CRITICAL"
    ALPHAS_MIDDLEWARE = "ALPHAS_MIDDLEWARE"
    ALPHAS_RAG_ERROR = "ALPHAS_RAG_ERROR"
    ALPHAS_AI_ERROR = "ALPHAS_AI_ERROR"

class AlphasFormatter(logging.Formatter):
    """Formatter personalizado para ALPHAS TECHNIQUE TEST IA"""
    
    def __init__(self):
        super().__init__()
        self.format_string = (
            "🔥 ALPHAS TECHNIQUE TEST IA 🔥 | "
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(funcName)s:%(lineno)d | "
            "%(message)s"
        )
    
    def format(self, record):
        # Añadir información adicional de ALPHAS
        if hasattr(record, 'alphas_context'):
            record.message = f"[ALPHAS-CTX: {record.alphas_context}] {record.getMessage()}"
        else:
            record.message = f"[ALPHAS-TECH] {record.getMessage()}"
        
        # Formatear timestamp personalizado
        record.asctime = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Aplicar colores según el nivel
        level_colors = {
            'DEBUG': '\033[36m',      # Cyan
            'INFO': '\033[32m',       # Verde
            'WARNING': '\033[33m',    # Amarillo
            'ERROR': '\033[31m',      # Rojo
            'CRITICAL': '\033[35m',   # Magenta
        }
        
        color = level_colors.get(record.levelname, '\033[0m')
        reset_color = '\033[0m'
        
        formatted = self.format_string % record.__dict__
        return f"{color}{formatted}{reset_color}"

class AlphasLogger:
    """
    Logger personalizado para ALPHAS TECHNIQUE TEST IA
    Especializado en captura de errores de middleware FastAPI
    """
    
    def __init__(self, name: str = "alphas_technique_test_ia", log_file: str = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Evitar duplicación de handlers
        if not self.logger.handlers:
            self._setup_handlers(log_file)
        
        # Contexto global para ALPHAS
        self.alphas_context = {
            "technique": "ALPHAS TECHNIQUE TEST IA",
            "version": "1.0.0",
            "component": "RAG_MIDDLEWARE_LOGGER",
            "initialized_at": datetime.now().isoformat()
        }
    
    def _setup_handlers(self, log_file: Optional[str] = None):
        """Configura los handlers del logger"""
        formatter = AlphasFormatter()
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Handler para archivo si se especifica
        if log_file:
            # Crear directorio si no existe
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # Formatter para archivo (sin colores)
            file_formatter = logging.Formatter(
                "🔥 ALPHAS TECHNIQUE TEST IA 🔥 | "
                "%(asctime)s | "
                "%(levelname)s | "
                "%(name)s | "
                "%(funcName)s:%(lineno)d | "
                "%(message)s"
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def _create_log_entry(self, level: str, message: str, **kwargs) -> Dict[str, Any]:
        """Crea una entrada de log estructurada para ALPHAS"""
        return {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "technique": "ALPHAS TECHNIQUE TEST IA",
            "message": message,
            "context": self.alphas_context,
            "additional_data": kwargs
        }
    
    def alphas_debug(self, message: str, **kwargs):
        """Log de debug con contexto ALPHAS"""
        extra = {"alphas_context": "DEBUG"}
        self.logger.debug(f"🔍 ALPHAS-DEBUG: {message}", extra=extra)
    
    def alphas_info(self, message: str, **kwargs):
        """Log de información con contexto ALPHAS"""
        extra = {"alphas_context": "INFO"}
        self.logger.info(f"ℹ️ ALPHAS-INFO: {message}", extra=extra)
    
    def alphas_warning(self, message: str, **kwargs):
        """Log de advertencia con contexto ALPHAS"""
        extra = {"alphas_context": "WARNING"}
        self.logger.warning(f"⚠️ ALPHAS-WARNING: {message}", extra=extra)
    
    def alphas_error(self, message: str, error: Exception = None, **kwargs):
        """Log de error con contexto ALPHAS y stack trace"""
        extra = {"alphas_context": "ERROR"}
        
        error_details = ""
        if error:
            error_details = f" | Error: {str(error)} | Type: {type(error).__name__}"
            if kwargs.get('include_traceback', True):
                error_details += f" | Traceback: {traceback.format_exc()}"
        
        self.logger.error(f"❌ ALPHAS-ERROR: {message}{error_details}", extra=extra)
    
    def alphas_critical(self, message: str, error: Exception = None, **kwargs):
        """Log crítico con contexto ALPHAS"""
        extra = {"alphas_context": "CRITICAL"}
        
        error_details = ""
        if error:
            error_details = f" | Critical Error: {str(error)} | Type: {type(error).__name__}"
            error_details += f" | Traceback: {traceback.format_exc()}"
        
        self.logger.critical(f"🚨 ALPHAS-CRITICAL: {message}{error_details}", extra=extra)
    
    def alphas_middleware_error(self, 
                              request_method: str,
                              request_url: str, 
                              error: Exception,
                              status_code: int = 500,
                              **kwargs):
        """Log especializado para errores de middleware FastAPI"""
        extra = {"alphas_context": "MIDDLEWARE"}
        
        middleware_info = {
            "request_method": request_method,
            "request_url": str(request_url),
            "status_code": status_code,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "user_agent": kwargs.get('user_agent', 'Unknown'),
            "client_ip": kwargs.get('client_ip', 'Unknown'),
            "request_id": kwargs.get('request_id', 'Unknown')
        }
        
        message = (
            f"MIDDLEWARE ERROR CAPTURED | "
            f"Method: {request_method} | "
            f"URL: {request_url} | "
            f"Status: {status_code} | "
            f"Error: {str(error)}"
        )
        
        if kwargs.get('include_traceback', True):
            message += f" | Traceback: {traceback.format_exc()}"
        
        self.logger.error(f"🌐 ALPHAS-MIDDLEWARE: {message}", extra=extra)
        
        # Log adicional con detalles estructurados
        self.logger.info(f"📊 ALPHAS-MIDDLEWARE-DETAILS: {json.dumps(middleware_info, indent=2)}", extra=extra)
    
    def alphas_rag_error(self, operation: str, error: Exception, **kwargs):
        """Log especializado para errores del sistema RAG"""
        extra = {"alphas_context": "RAG"}
        
        rag_info = {
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "query": kwargs.get('query', 'Unknown'),
            "document_id": kwargs.get('document_id', 'Unknown'),
            "embedding_model": kwargs.get('embedding_model', 'Unknown')
        }
        
        message = (
            f"RAG SYSTEM ERROR | "
            f"Operation: {operation} | "
            f"Error: {str(error)}"
        )
        
        self.logger.error(f"🤖 ALPHAS-RAG: {message}", extra=extra)
        self.logger.debug(f"🔬 ALPHAS-RAG-DETAILS: {json.dumps(rag_info, indent=2)}", extra=extra)
    
    def alphas_ai_error(self, service: str, error: Exception, **kwargs):
        """Log especializado para errores de servicios de IA"""
        extra = {"alphas_context": "AI_SERVICE"}
        
        ai_info = {
            "service": service,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "model": kwargs.get('model', 'Unknown'),
            "tokens_used": kwargs.get('tokens_used', 0),
            "request_id": kwargs.get('request_id', 'Unknown')
        }
        
        message = (
            f"AI SERVICE ERROR | "
            f"Service: {service} | "
            f"Error: {str(error)}"
        )
        
        self.logger.error(f"🧠 ALPHAS-AI: {message}", extra=extra)
        self.logger.debug(f"🔍 ALPHAS-AI-DETAILS: {json.dumps(ai_info, indent=2)}", extra=extra)
    
    def alphas_performance_log(self, operation: str, duration: float, **kwargs):
        """Log de rendimiento para ALPHAS TECHNIQUE TEST IA"""
        extra = {"alphas_context": "PERFORMANCE"}
        
        perf_info = {
            "operation": operation,
            "duration_ms": round(duration * 1000, 2),
            "memory_usage": kwargs.get('memory_usage', 'Unknown'),
            "cpu_usage": kwargs.get('cpu_usage', 'Unknown')
        }
        
        message = f"PERFORMANCE METRIC | Operation: {operation} | Duration: {duration:.3f}s"
        
        self.logger.info(f"⚡ ALPHAS-PERFORMANCE: {message}", extra=extra)
        self.logger.debug(f"📈 ALPHAS-PERF-DETAILS: {json.dumps(perf_info, indent=2)}", extra=extra)
    
    def set_context(self, **context):
        """Actualiza el contexto global de ALPHAS"""
        self.alphas_context.update(context)
    
    def get_logger(self) -> logging.Logger:
        """Retorna el logger base para uso directo"""
        return self.logger

# Instancia global del logger ALPHAS
alphas_logger = AlphasLogger(
    name="alphas_technique_test_ia",
    log_file="logs/alphas_technique_test_ia.log"
)

# Funciones de conveniencia
def log_alphas_error(message: str, error: Exception = None, **kwargs):
    """Función de conveniencia para logging de errores ALPHAS"""
    alphas_logger.alphas_error(message, error, **kwargs)

def log_alphas_middleware_error(request_method: str, request_url: str, error: Exception, **kwargs):
    """Función de conveniencia para errores de middleware"""
    alphas_logger.alphas_middleware_error(request_method, request_url, error, **kwargs)

def log_alphas_rag_error(operation: str, error: Exception, **kwargs):
    """Función de conveniencia para errores RAG"""
    alphas_logger.alphas_rag_error(operation, error, **kwargs)

def log_alphas_info(message: str, **kwargs):
    """Función de conveniencia para información ALPHAS"""
    alphas_logger.alphas_info(message, **kwargs)

def log_alphas_warning(message: str, **kwargs):
    """Función de conveniencia para advertencias ALPHAS"""
    alphas_logger.alphas_warning(message, **kwargs)
