"""
ALPHAS TECHNIQUE TEST IA - Servidor API RAG Consolidado
Sistema RAG monolítico para políticas de RRHH con logging avanzado ALPHAS
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Añadir el directorio src al path
sys.path.append(str(Path(__file__).parent.parent.parent))

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Body, Depends, status, Path as PathParam
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Importar logger ALPHAS
try:
    from infrastructure.logger import (
        setup_alphas_middleware,
        alphas_endpoint_logger,
        log_alphas_info,
        log_alphas_error,
        log_alphas_rag_error,
        alphas_logger
    )
    ALPHAS_LOGGER_AVAILABLE = True
except ImportError:
    ALPHAS_LOGGER_AVAILABLE = False
    print("ALPHAS Logger no disponible, usando logging estándar")

# Importar sistema RAG
try:
    from services.RAG import GoogleHRPoliciesRAG, create_rag_system
    ALPHAS_RAG_AVAILABLE = True
except ImportError:
    ALPHAS_RAG_AVAILABLE = False
    print("ALPHAS RAG no disponible")

# Importar DTOs y servicios
try:
    from application.dto.api_dto import (
        AskQuestionRequest, AskQuestionResponse, AddDocumentRequest, 
        AddDocumentResponse, SearchDocumentsRequest, SearchDocumentsResponse,
        SystemInfoResponse, ErrorResponse, ValidationErrorResponse, DocumentInfo
    )
    from application.use_cases.ask_question_use_case import (
        AskQuestionUseCase, DepartmentContextService, UseCaseFactory
    )
    from infrastructure.adapters.rag_service_adapter import RAGServiceFactory
    from infrastructure.config.rag_config import rag_config
    from domain.entities.domain import (
        RAGService, RAGDomainException, InvalidQueryError,
        DocumentNotFoundError, VectorSearchError, AIServiceError
    )
    STANDARD_RAG_AVAILABLE = True
except ImportError:
    STANDARD_RAG_AVAILABLE = False
    print("Sistema RAG estándar no disponible")

# ============================================================================
# MODELOS PYDANTIC CONSOLIDADOS
# ============================================================================

class QueryRequest(BaseModel):
    """Modelo para requests de consulta ALPHAS"""
    question: str = Field(..., description="Pregunta sobre políticas de RRHH", min_length=3)
    category: Optional[str] = Field(None, description="Categoría específica para filtrar")
    department: Optional[str] = Field(None, description="Departamento para filtrar contexto")
    use_openai: bool = Field(True, description="Usar OpenAI para generar respuesta")
    use_ai: bool = Field(True, description="Usar IA para generar respuesta")
    top_k: int = Field(5, description="Número de documentos similares a retornar", ge=1, le=20)

class DocumentRequest(BaseModel):
    """Modelo para añadir documentos"""
    title: str = Field(..., description="Título del documento", min_length=3)
    content: str = Field(..., description="Contenido del documento", min_length=10)
    category: str = Field(..., description="Categoría del documento", min_length=2)
    department: Optional[str] = Field(None, description="Departamento al que pertenece")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")

class RAGResponse(BaseModel):
    """Modelo para respuestas del sistema RAG"""
    success: bool
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    technique: str = "ALPHAS TECHNIQUE TEST IA"
    request_id: Optional[str] = None

class DocumentResponse(BaseModel):
    """Modelo para respuestas de documentos"""
    success: bool
    document_id: Optional[int] = None
    title: Optional[str] = None
    message: str
    technique: str = "ALPHAS TECHNIQUE TEST IA"

class SystemInfoResponseConsolidated(BaseModel):
    """Modelo para información del sistema consolidado"""
    technique: str = "ALPHAS TECHNIQUE TEST IA"
    total_documents: int
    categories: List[str]
    departments: List[str] = []
    status: str
    system_status: str = "active"
    version: str = "1.0.0"
    alphas_system: bool = False
    standard_system: bool = False

# ============================================================================
# SERVICIO CONSOLIDADO
# ============================================================================

class ConsolidatedRAGService:
    """Servicio RAG consolidado con funcionalidades ALPHAS y estándar"""
    
    def __init__(self):
        self.rag_service: Optional[RAGService] = None
        self.department_service: Optional[DepartmentContextService] = None
        self.ask_question_use_case: Optional[AskQuestionUseCase] = None
        self.alphas_rag_system: Optional[GoogleHRPoliciesRAG] = None
        self.logger = logging.getLogger(__name__)
        
        # Estadísticas del servicio
        self._stats = {
            "questions_asked": 0,
            "documents_added": 0,
            "searches_performed": 0,
            "start_time": datetime.now()
        }
    
    async def initialize(self):
        """Inicializar todos los servicios disponibles"""
        try:
            if ALPHAS_LOGGER_AVAILABLE:
                log_alphas_info("🚀 Initializing ALPHAS TECHNIQUE TEST IA Consolidated RAG System...")
                
                # Configurar contexto del logger
                alphas_logger.set_context(
                    component="CONSOLIDATED_RAG_API",
                    version="1.0.0",
                    environment="production"
                )
            else:
                self.logger.info("🚀 Initializing Consolidated RAG System...")
            
            # Inicializar sistema RAG ALPHAS si está disponible
            if ALPHAS_RAG_AVAILABLE:
                try:
                    self.alphas_rag_system = create_rag_system("alphas_hr_policies.db")
                    if ALPHAS_LOGGER_AVAILABLE:
                        log_alphas_info("✅ ALPHAS RAG System initialized successfully")
                    else:
                        self.logger.info("✅ ALPHAS RAG System initialized successfully")
                except Exception as e:
                    self.logger.error(f"Error initializing ALPHAS RAG: {e}")
            
            # Inicializar sistema RAG estándar si está disponible
            if STANDARD_RAG_AVAILABLE:
                try:
                    config = {
                        "database_path": rag_config.database_path,
                        "embedding_model": rag_config.embedding_model
                    }
                    self.rag_service = RAGServiceFactory.create_rag_service_from_config(config)
                    self.department_service = UseCaseFactory.create_department_context_service()
                    self.ask_question_use_case = UseCaseFactory.create_ask_question_use_case(self.rag_service)
                    self.logger.info("✅ Standard RAG System initialized successfully")
                except Exception as e:
                    self.logger.error(f"Error initializing Standard RAG: {e}")
            
            total_docs = self.get_document_count()
            categories = len(self.get_categories())
            
            if ALPHAS_LOGGER_AVAILABLE:
                log_alphas_info(f"✅ Consolidated RAG System ready | Documents: {total_docs} | Categories: {categories}")
            else:
                self.logger.info(f"✅ Consolidated RAG System ready | Documents: {total_docs} | Categories: {categories}")
            
        except Exception as e:
            if ALPHAS_LOGGER_AVAILABLE:
                log_alphas_rag_error("startup", e, operation="consolidated_system_initialization")
            else:
                self.logger.error(f"Error in system initialization: {e}")
            raise
    
    def get_document_count(self) -> int:
        """Obtener número total de documentos"""
        total = 0
        try:
            if self.alphas_rag_system:
                total += self.alphas_rag_system.get_document_count()
        except:
            pass
        try:
            if self.rag_service:
                total += self.rag_service.get_document_count()
        except:
            pass
        return total
    
    def get_categories(self) -> List[str]:
        """Obtener categorías disponibles"""
        categories = set()
        try:
            if self.alphas_rag_system:
                categories.update(self.alphas_rag_system.get_categories())
        except:
            pass
        try:
            if self.rag_service:
                categories.update(self.rag_service.get_categories())
        except:
            pass
        return list(categories)
    
    def get_departments(self) -> List[str]:
        """Obtener departamentos disponibles"""
        try:
            if self.department_service:
                return self.department_service.get_available_departments()
        except:
            pass
        return []
    
    async def ask_question_consolidated(self, request: QueryRequest) -> RAGResponse:
        """Procesar pregunta usando el mejor sistema disponible"""
        try:
            # Priorizar sistema ALPHAS si está disponible
            if self.alphas_rag_system:
                return await self._ask_question_alphas(request)
            elif self.ask_question_use_case:
                return await self._ask_question_standard(request)
            else:
                raise HTTPException(status_code=503, detail="No RAG system available")
                
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error in consolidated ask_question: {e}")
            raise HTTPException(status_code=500, detail="Error processing question")
    
    async def _ask_question_alphas(self, request: QueryRequest) -> RAGResponse:
        """Procesar pregunta usando sistema ALPHAS"""
        if ALPHAS_LOGGER_AVAILABLE:
            log_alphas_info(f"🔍 ALPHAS RAG QUERY | Question: {request.question[:100]}...")
        
        result = self.alphas_rag_system.generate_rag_response(
            query=request.question,
            use_openai=request.use_openai
        )
        
        # Buscar documentos similares adicionales si se especifica top_k diferente
        if request.top_k != 5:
            similar_docs = self.alphas_rag_system.search_similar(
                query=request.question,
                top_k=request.top_k,
                category=request.category
            )
            
            result["sources"] = [
                {
                    "title": doc["title"],
                    "category": doc["category"],
                    "similarity": doc["similarity"]
                }
                for doc in similar_docs
            ]
        
        self._stats["questions_asked"] += 1
        
        if ALPHAS_LOGGER_AVAILABLE:
            log_alphas_info(f"✅ ALPHAS RAG QUERY SUCCESS | Confidence: {result['confidence']:.3f}")
        
        return RAGResponse(
            success=True,
            answer=result["answer"],
            sources=result["sources"],
            confidence=result["confidence"]
        )
    
    async def _ask_question_standard(self, request: QueryRequest) -> RAGResponse:
        """Procesar pregunta usando sistema estándar"""
        standard_request = AskQuestionRequest(
            question=request.question,
            department=request.department,
            use_ai=request.use_ai,
            top_k=request.top_k
        )
        
        response = self.ask_question_use_case.execute(standard_request)
        self._stats["questions_asked"] += 1
        
        # Convertir a formato ALPHAS
        return RAGResponse(
            success=True,
            answer=response.answer,
            sources=[
                {
                    "title": source.title,
                    "category": source.category,
                    "similarity": source.similarity
                }
                for source in response.sources
            ],
            confidence=response.confidence
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del servicio consolidado"""
        uptime = datetime.now() - self._stats["start_time"]
        
        return {
            **self._stats,
            "uptime_seconds": uptime.total_seconds(),
            "uptime_formatted": str(uptime).split('.')[0],
            "technique": "ALPHAS TECHNIQUE TEST IA",
            "alphas_system_available": self.alphas_rag_system is not None,
            "standard_system_available": self.rag_service is not None
        }

# ============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN FASTAPI
# ============================================================================

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI consolidada
app = FastAPI(
    title="ALPHAS TECHNIQUE TEST IA - Consolidated RAG API",
    description="Sistema RAG consolidado para políticas de RRHH con logging avanzado ALPHAS",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar middlewares ALPHAS si está disponible
if ALPHAS_LOGGER_AVAILABLE:
    setup_alphas_middleware(
        app=app,
        include_request_body=True,
        max_body_size=2048,
        enable_performance_monitoring=True,
        slow_request_threshold=2.0
    )

# Instancia global del servicio consolidado
consolidated_service: Optional[ConsolidatedRAGService] = None

def get_consolidated_service() -> ConsolidatedRAGService:
    """Dependencia para obtener el servicio consolidado"""
    global consolidated_service
    if consolidated_service is None:
        raise HTTPException(status_code=503, detail="Consolidated service not initialized")
    return consolidated_service

# ============================================================================
# EVENTOS DE CICLO DE VIDA
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Inicialización del sistema consolidado al arrancar la API"""
    global consolidated_service
    
    try:
        consolidated_service = ConsolidatedRAGService()
        await consolidated_service.initialize()
        
    except Exception as e:
        if ALPHAS_LOGGER_AVAILABLE:
            log_alphas_rag_error("startup", e, operation="consolidated_system_initialization")
        else:
            logger.error(f"Error in startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al cerrar la API"""
    if ALPHAS_LOGGER_AVAILABLE:
        log_alphas_info("🔄 Shutting down ALPHAS TECHNIQUE TEST IA Consolidated RAG System...")
    else:
        logger.info("🔄 Shutting down Consolidated RAG System...")

# ============================================================================
# MANEJADORES DE EXCEPCIONES
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handler personalizado para errores 404"""
    return JSONResponse(
        status_code=404,
        content={
            "technique": "ALPHAS TECHNIQUE TEST IA",
            "error": True,
            "message": "Endpoint not found",
            "suggestion": "Check /docs for available endpoints"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handler personalizado para errores 500"""
    if ALPHAS_LOGGER_AVAILABLE:
        log_alphas_error("Internal server error in ALPHAS Consolidated API", exc)
    else:
        logger.error(f"Internal server error: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "technique": "ALPHAS TECHNIQUE TEST IA",
            "error": True,
            "message": "Internal server error",
            "support": "Contact ALPHAS TECHNIQUE TEST IA support team"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Manejador para excepciones generales"""
    logger.error(f"Error inesperado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "technique": "ALPHAS TECHNIQUE TEST IA",
            "error": True,
            "message": "Error interno del servidor",
            "timestamp": datetime.now().isoformat()
        }
    )

# ============================================================================
# ENDPOINTS PRINCIPALES
# ============================================================================

@app.get("/")
async def root():
    """Endpoint raíz con información ALPHAS consolidada"""
    return {
        "message": "🔥 ALPHAS TECHNIQUE TEST IA - Consolidated RAG API 🔥",
        "technique": "ALPHAS TECHNIQUE TEST IA",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs",
        "features": "Consolidated ALPHAS + Standard RAG with Departmental Context",
        "alphas_system": ALPHAS_RAG_AVAILABLE,
        "standard_system": STANDARD_RAG_AVAILABLE,
        "alphas_logger": ALPHAS_LOGGER_AVAILABLE
    }

@app.get("/health")
async def health_check():
    """Health check consolidado"""
    try:
        service = get_consolidated_service()
        
        return {
            "technique": "ALPHAS TECHNIQUE TEST IA",
            "status": "healthy",
            "consolidated_system": "operational",
            "alphas_rag_system": "operational" if service.alphas_rag_system else "unavailable",
            "standard_rag_system": "operational" if service.rag_service else "unavailable",
            "total_documents": service.get_document_count(),
            "categories": service.get_categories(),
            "departments": service.get_departments(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        if ALPHAS_LOGGER_AVAILABLE:
            log_alphas_rag_error("health_check", e)
        else:
            logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=503, detail="System health check failed")

# ============================================================================
# ENDPOINTS CONSOLIDADOS
# ============================================================================

@app.post("/ask", response_model=RAGResponse)
async def ask_question(
    request: QueryRequest,
    service: ConsolidatedRAGService = Depends(get_consolidated_service)
):
    """Endpoint principal para hacer preguntas al sistema RAG consolidado"""
    if ALPHAS_LOGGER_AVAILABLE:
        return await alphas_endpoint_logger("consolidated_ask_question")(
            lambda: service.ask_question_consolidated(request)
        )()
    else:
        return await service.ask_question_consolidated(request)

@app.get("/ask", response_model=RAGResponse)
async def ask_question_get(
    question: str = Query(..., description="La pregunta a realizar", min_length=1, max_length=1000),
    department: Optional[str] = Query(None, description="Departamento para filtrar contexto"),
    category: Optional[str] = Query(None, description="Categoría para filtrar"),
    use_ai: bool = Query(True, description="Si usar IA para generar la respuesta"),
    top_k: int = Query(5, description="Número máximo de documentos a considerar", ge=1, le=20),
    service: ConsolidatedRAGService = Depends(get_consolidated_service)
):
    """Versión GET del endpoint ask_question para consultas rápidas"""
    
    request = QueryRequest(
        question=question,
        department=department,
        category=category,
        use_ai=use_ai,
        use_openai=use_ai,
        top_k=top_k
    )
    
    return await ask_question(request, service)

@app.get("/system/info", response_model=SystemInfoResponseConsolidated)
async def get_system_info(
    service: ConsolidatedRAGService = Depends(get_consolidated_service)
):
    """Obtener información del sistema consolidado"""
    if ALPHAS_LOGGER_AVAILABLE:
        log_alphas_info("Obteniendo información del sistema consolidado")
    else:
        logger.info("Obteniendo información del sistema consolidado")
    
    return SystemInfoResponseConsolidated(
        total_documents=service.get_document_count(),
        categories=service.get_categories(),
        departments=service.get_departments(),
        status="operational",
        alphas_system=service.alphas_rag_system is not None,
        standard_system=service.rag_service is not None
    )

@app.get("/system/stats")
async def get_system_stats(
    service: ConsolidatedRAGService = Depends(get_consolidated_service)
):
    """Obtener estadísticas del sistema consolidado"""
    return service.get_stats()

@app.get("/departments", response_model=List[str])
async def get_departments(
    service: ConsolidatedRAGService = Depends(get_consolidated_service)
):
    """Obtener lista de departamentos disponibles"""
    return service.get_departments()

# ============================================================================
# CLASE SERVIDOR RAG
# ============================================================================

class RAGServer:
    """Servidor para la API RAG consolidada"""
    
    def __init__(self, 
                 host: str = "127.0.0.1",
                 port: int = 8000,
                 reload: bool = False,
                 workers: int = 1):
        self.host = host
        self.port = port
        self.reload = reload
        self.workers = workers
        self.app = app
        
    def run(self):
        """Ejecuta el servidor"""
        logger.info(f"Iniciando servidor ALPHAS Consolidated RAG API en {self.host}:{self.port}")
        logger.info(f"Documentación disponible en: http://{self.host}:{self.port}/docs")
        logger.info(f"Endpoint principal: http://{self.host}:{self.port}/ask")
        
        # Configuración de uvicorn
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            reload=self.reload,
            workers=self.workers if not self.reload else 1,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        server.run()

def create_server_from_env() -> RAGServer:
    """Crea el servidor usando variables de entorno"""
    host = os.getenv("RAG_API_HOST", "127.0.0.1")
    port = int(os.getenv("RAG_API_PORT", "8000"))
    reload = os.getenv("RAG_API_RELOAD", "false").lower() == "true"
    workers = int(os.getenv("RAG_API_WORKERS", "1"))
    
    return RAGServer(host=host, port=port, reload=reload, workers=workers)

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Servidor API RAG Consolidado ALPHAS")
    parser.add_argument("--host", default="127.0.0.1", help="Host del servidor")
    parser.add_argument("--port", type=int, default=8000, help="Puerto del servidor")
    parser.add_argument("--reload", action="store_true", help="Habilitar recarga automática")
    parser.add_argument("--workers", type=int, default=1, help="Número de workers")
    parser.add_argument("--env", action="store_true", help="Usar configuración de variables de entorno")
    
    args = parser.parse_args()
    
    if args.env:
        server = create_server_from_env()
    else:
        server = RAGServer(
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers
        )
    
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"Error ejecutando servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()