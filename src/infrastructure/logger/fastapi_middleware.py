"""
ALPHAS TECHNIQUE TEST IA - FastAPI Middleware
Middleware personalizado para captura de errores y logging avanzado
"""

import time
import uuid
import json
import traceback
from typing import Callable, Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .alphas_logger import alphas_logger, log_alphas_middleware_error, log_alphas_info, log_alphas_error

class AlphasErrorMiddleware(BaseHTTPMiddleware):
    """
    Middleware ALPHAS TECHNIQUE TEST IA para captura y logging de errores
    """
    
    def __init__(self, app: ASGIApp, include_request_body: bool = False, max_body_size: int = 1024):
        super().__init__(app)
        self.include_request_body = include_request_body
        self.max_body_size = max_body_size
        
        # Inicializar contexto ALPHAS
        alphas_logger.set_context(
            middleware="AlphasErrorMiddleware",
            technique="ALPHAS TECHNIQUE TEST IA",
            component="FastAPI_Middleware"
        )
        
        log_alphas_info("🚀 ALPHAS Error Middleware initialized successfully")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Procesa cada request con logging ALPHAS"""
        
        # Generar ID único para el request
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Extraer información del request
        request_info = await self._extract_request_info(request, request_id)
        
        # Log de inicio de request
        log_alphas_info(
            f"🌐 ALPHAS REQUEST START | ID: {request_id} | Method: {request.method} | URL: {request.url}",
            request_id=request_id,
            method=request.method,
            url=str(request.url)
        )
        
        try:
            # Procesar request
            response = await call_next(request)
            
            # Calcular tiempo de procesamiento
            process_time = time.time() - start_time
            
            # Log de respuesta exitosa
            await self._log_successful_response(request_info, response, process_time)
            
            # Añadir headers ALPHAS
            response.headers["X-Alphas-Request-ID"] = request_id
            response.headers["X-Alphas-Process-Time"] = f"{process_time:.3f}s"
            response.headers["X-Alphas-Technique"] = "ALPHAS-TECHNIQUE-TEST-IA"
            
            return response
            
        except HTTPException as http_exc:
            # Manejar excepciones HTTP conocidas
            process_time = time.time() - start_time
            await self._log_http_exception(request_info, http_exc, process_time)
            
            return await self._create_error_response(
                request_id=request_id,
                status_code=http_exc.status_code,
                message=http_exc.detail,
                error_type="HTTPException",
                process_time=process_time
            )
            
        except Exception as exc:
            # Manejar excepciones no controladas
            process_time = time.time() - start_time
            await self._log_unhandled_exception(request_info, exc, process_time)
            
            return await self._create_error_response(
                request_id=request_id,
                status_code=500,
                message="Internal Server Error - ALPHAS TECHNIQUE TEST IA",
                error_type=type(exc).__name__,
                error_details=str(exc),
                process_time=process_time
            )
    
    async def _extract_request_info(self, request: Request, request_id: str) -> Dict[str, Any]:
        """Extrae información detallada del request"""
        
        # Headers básicos
        user_agent = request.headers.get("user-agent", "Unknown")
        client_ip = self._get_client_ip(request)
        content_type = request.headers.get("content-type", "Unknown")
        
        # Información básica
        request_info = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_ip": client_ip,
            "user_agent": user_agent,
            "content_type": content_type,
            "timestamp": datetime.now().isoformat()
        }
        
        # Incluir body si está habilitado
        if self.include_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if len(body) <= self.max_body_size:
                    if content_type and "application/json" in content_type:
                        try:
                            request_info["body"] = json.loads(body.decode())
                        except:
                            request_info["body"] = body.decode()[:self.max_body_size]
                    else:
                        request_info["body"] = body.decode()[:self.max_body_size]
                else:
                    request_info["body"] = f"[BODY TOO LARGE: {len(body)} bytes]"
            except Exception as e:
                request_info["body"] = f"[ERROR READING BODY: {str(e)}]"
        
        return request_info
    
    def _get_client_ip(self, request: Request) -> str:
        """Obtiene la IP real del cliente considerando proxies"""
        # Verificar headers de proxy
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # IP directa
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "Unknown"
    
    async def _log_successful_response(self, request_info: Dict, response: Response, process_time: float):
        """Log para respuestas exitosas"""
        log_alphas_info(
            f"✅ ALPHAS REQUEST SUCCESS | "
            f"ID: {request_info['request_id']} | "
            f"Method: {request_info['method']} | "
            f"URL: {request_info['url']} | "
            f"Status: {response.status_code} | "
            f"Time: {process_time:.3f}s",
            **request_info,
            status_code=response.status_code,
            process_time=process_time
        )
        
        # Log de performance si es lento
        if process_time > 1.0:  # Más de 1 segundo
            alphas_logger.alphas_warning(
                f"🐌 SLOW REQUEST DETECTED | "
                f"ID: {request_info['request_id']} | "
                f"Time: {process_time:.3f}s | "
                f"URL: {request_info['url']}"
            )
    
    async def _log_http_exception(self, request_info: Dict, http_exc: HTTPException, process_time: float):
        """Log para excepciones HTTP"""
        log_alphas_middleware_error(
            request_method=request_info['method'],
            request_url=request_info['url'],
            error=http_exc,
            status_code=http_exc.status_code,
            user_agent=request_info['user_agent'],
            client_ip=request_info['client_ip'],
            request_id=request_info['request_id'],
            process_time=process_time,
            include_traceback=False  # No incluir traceback para HTTP exceptions
        )
    
    async def _log_unhandled_exception(self, request_info: Dict, exc: Exception, process_time: float):
        """Log para excepciones no controladas"""
        log_alphas_middleware_error(
            request_method=request_info['method'],
            request_url=request_info['url'],
            error=exc,
            status_code=500,
            user_agent=request_info['user_agent'],
            client_ip=request_info['client_ip'],
            request_id=request_info['request_id'],
            process_time=process_time,
            include_traceback=True
        )
        
        # Log crítico para errores graves
        alphas_logger.alphas_critical(
            f"🚨 UNHANDLED EXCEPTION IN ALPHAS MIDDLEWARE | "
            f"ID: {request_info['request_id']} | "
            f"URL: {request_info['url']} | "
            f"Error: {str(exc)}",
            error=exc
        )
    
    async def _create_error_response(self, 
                                   request_id: str,
                                   status_code: int,
                                   message: str,
                                   error_type: str,
                                   error_details: str = None,
                                   process_time: float = None) -> JSONResponse:
        """Crea una respuesta de error estructurada ALPHAS"""
        
        error_response = {
            "error": True,
            "technique": "ALPHAS TECHNIQUE TEST IA",
            "request_id": request_id,
            "status_code": status_code,
            "message": message,
            "error_type": error_type,
            "timestamp": datetime.now().isoformat(),
            "support_message": "Si el error persiste, contacta al equipo de ALPHAS TECHNIQUE TEST IA"
        }
        
        # Añadir detalles adicionales si están disponibles
        if error_details:
            error_response["error_details"] = error_details
        
        if process_time:
            error_response["process_time"] = f"{process_time:.3f}s"
        
        # Headers ALPHAS
        headers = {
            "X-Alphas-Request-ID": request_id,
            "X-Alphas-Error": "true",
            "X-Alphas-Technique": "ALPHAS-TECHNIQUE-TEST-IA"
        }
        
        if process_time:
            headers["X-Alphas-Process-Time"] = f"{process_time:.3f}s"
        
        return JSONResponse(
            status_code=status_code,
            content=error_response,
            headers=headers
        )

class AlphasPerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware ALPHAS para monitoreo de rendimiento
    """
    
    def __init__(self, app: ASGIApp, slow_request_threshold: float = 1.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
        
        log_alphas_info("⚡ ALPHAS Performance Middleware initialized")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Monitorea el rendimiento de cada request"""
        
        start_time = time.time()
        
        # Procesar request
        response = await call_next(request)
        
        # Calcular métricas
        process_time = time.time() - start_time
        
        # Log de rendimiento
        alphas_logger.alphas_performance_log(
            operation=f"{request.method} {request.url.path}",
            duration=process_time,
            status_code=response.status_code,
            url=str(request.url)
        )
        
        # Advertencia para requests lentos
        if process_time > self.slow_request_threshold:
            alphas_logger.alphas_warning(
                f"🐌 SLOW REQUEST | "
                f"URL: {request.url} | "
                f"Time: {process_time:.3f}s | "
                f"Threshold: {self.slow_request_threshold}s"
            )
        
        # Añadir header de performance
        response.headers["X-Alphas-Performance-Time"] = f"{process_time:.3f}s"
        
        return response

def setup_alphas_middleware(app: FastAPI, 
                          include_request_body: bool = False,
                          max_body_size: int = 1024,
                          enable_performance_monitoring: bool = True,
                          slow_request_threshold: float = 1.0):
    """
    Configura todos los middlewares ALPHAS TECHNIQUE TEST IA
    
    Args:
        app: Instancia de FastAPI
        include_request_body: Si incluir el body del request en los logs
        max_body_size: Tamaño máximo del body a loggear
        enable_performance_monitoring: Si habilitar monitoreo de rendimiento
        slow_request_threshold: Umbral para considerar un request como lento
    """
    
    log_alphas_info("🔧 Setting up ALPHAS TECHNIQUE TEST IA middlewares...")
    
    # Middleware de errores (debe ir primero)
    app.add_middleware(
        AlphasErrorMiddleware,
        include_request_body=include_request_body,
        max_body_size=max_body_size
    )
    
    # Middleware de rendimiento (opcional)
    if enable_performance_monitoring:
        app.add_middleware(
            AlphasPerformanceMiddleware,
            slow_request_threshold=slow_request_threshold
        )
    
    log_alphas_info("✅ ALPHAS middlewares configured successfully")
    
    return app

# Decorador para endpoints que requieren logging especial
def alphas_endpoint_logger(operation_name: str):
    """Decorador para logging especializado de endpoints"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                log_alphas_info(f"🎯 ALPHAS ENDPOINT START | Operation: {operation_name}")
                result = await func(*args, **kwargs)
                
                process_time = time.time() - start_time
                log_alphas_info(
                    f"✅ ALPHAS ENDPOINT SUCCESS | "
                    f"Operation: {operation_name} | "
                    f"Time: {process_time:.3f}s"
                )
                
                return result
                
            except Exception as e:
                process_time = time.time() - start_time
                log_alphas_error(
                    f"❌ ALPHAS ENDPOINT ERROR | "
                    f"Operation: {operation_name} | "
                    f"Time: {process_time:.3f}s",
                    error=e,
                    operation=operation_name
                )
                raise
        
        return wrapper
    return decorator
