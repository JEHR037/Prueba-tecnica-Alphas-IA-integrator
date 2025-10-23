"""
ALPHAS TECHNIQUE TEST IA - Logger Module
Sistema de logging avanzado para captura de errores en middleware FastAPI
"""

from .alphas_logger import (
    AlphasLogger,
    AlphasLogLevel,
    alphas_logger,
    log_alphas_error,
    log_alphas_middleware_error,
    log_alphas_rag_error,
    log_alphas_info,
    log_alphas_warning
)

from .fastapi_middleware import (
    AlphasErrorMiddleware,
    AlphasPerformanceMiddleware,
    setup_alphas_middleware,
    alphas_endpoint_logger
)

__all__ = [
    # Logger classes and instances
    "AlphasLogger",
    "AlphasLogLevel", 
    "alphas_logger",
    
    # Logging functions
    "log_alphas_error",
    "log_alphas_middleware_error",
    "log_alphas_rag_error",
    "log_alphas_info",
    "log_alphas_warning",
    
    # Middleware classes and functions
    "AlphasErrorMiddleware",
    "AlphasPerformanceMiddleware",
    "setup_alphas_middleware",
    "alphas_endpoint_logger"
]
