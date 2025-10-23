"""
Endpoints FastAPI para el sistema RAG con contexto departamental
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, status, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Importar DTOs
from application.dto.api_dto import (
    AskQuestionRequest, AskQuestionResponse, AddDocumentRequest, 
    AddDocumentResponse, SearchDocumentsRequest, SearchDocumentsResponse,
    SystemInfoResponse, ErrorResponse, ValidationErrorResponse
)

# Importar servicio principal
from infrastructure.web.api.main_service import MainRAGService, MainServiceFactory

# Importar excepciones de dominio
from domain.entities.domain import (
    RAGDomainException, InvalidQueryError, DocumentNotFoundError,
    VectorSearchError, AIServiceError
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN FASTAPI
# ============================================================================

app = FastAPI(
    title="Sistema RAG para Políticas de RRHH",
    description="API para consultas inteligentes sobre políticas de recursos humanos con contexto departamental",
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

# ============================================================================
# DEPENDENCIAS
# ============================================================================

# Instancia global del servicio principal
_main_service: Optional[MainRAGService] = None
_integrated_service = None

def get_main_service() -> MainRAGService:
    """Dependencia para obtener el servicio principal"""
    global _main_service
    if _main_service is None:
        _main_service = MainServiceFactory.create_main_service()
    return _main_service

async def get_integrated_service():
    """Dependencia para obtener el servicio RAG integrado"""
    global _integrated_service
    if _integrated_service is None:
        from infrastructure.services.integrated_rag_service import get_global_integrated_service
        _integrated_service = await get_global_integrated_service()
    return _integrated_service

# ============================================================================
# MANEJADORES DE EXCEPCIONES
# ============================================================================

@app.exception_handler(InvalidQueryError)
async def invalid_query_handler(request, exc: InvalidQueryError):
    """Manejador para errores de consulta inválida"""
    logger.warning(f"Consulta inválida: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error="InvalidQueryError",
            message=str(exc),
            timestamp=datetime.now()
        ).dict()
    )

@app.exception_handler(DocumentNotFoundError)
async def document_not_found_handler(request, exc: DocumentNotFoundError):
    """Manejador para errores de documento no encontrado"""
    logger.warning(f"Documento no encontrado: {exc}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse(
            error="DocumentNotFoundError",
            message=str(exc),
            timestamp=datetime.now()
        ).dict()
    )

@app.exception_handler(VectorSearchError)
async def vector_search_error_handler(request, exc: VectorSearchError):
    """Manejador para errores de búsqueda vectorial"""
    logger.error(f"Error en búsqueda vectorial: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="VectorSearchError",
            message="Error interno en el sistema de búsqueda",
            details={"original_error": str(exc)},
            timestamp=datetime.now()
        ).dict()
    )

@app.exception_handler(AIServiceError)
async def ai_service_error_handler(request, exc: AIServiceError):
    """Manejador para errores del servicio de IA"""
    logger.error(f"Error en servicio de IA: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=ErrorResponse(
            error="AIServiceError",
            message="Servicio de IA temporalmente no disponible",
            details={"original_error": str(exc)},
            timestamp=datetime.now()
        ).dict()
    )

@app.exception_handler(RAGDomainException)
async def rag_domain_exception_handler(request, exc: RAGDomainException):
    """Manejador para excepciones generales del dominio RAG"""
    logger.error(f"Error de dominio RAG: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="RAGDomainException",
            message="Error interno del sistema",
            details={"original_error": str(exc)},
            timestamp=datetime.now()
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Manejador para excepciones generales"""
    logger.error(f"Error inesperado: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="Error interno del servidor",
            timestamp=datetime.now()
        ).dict()
    )

# ============================================================================
# ENDPOINTS PRINCIPALES
# ============================================================================

@app.post("/ask", 
          response_model=AskQuestionResponse,
          summary="Hacer pregunta al sistema RAG",
          description="Endpoint principal para hacer preguntas con contexto departamental y datos precargados")
async def ask_question(
    request: AskQuestionRequest
) -> AskQuestionResponse:
    """
    Hace una pregunta al sistema RAG integrado con datos precargados
    
    - **question**: La pregunta a realizar
    - **department**: Departamento para filtrar contexto (opcional)
    - **use_ai**: Si usar IA para generar la respuesta
    - **top_k**: Número máximo de documentos a considerar
    
    Este endpoint utiliza el sistema RAG integrado que incluye:
    - Datos precargados de políticas de RRHH
    - Sistema de embeddings optimizado
    - Respuestas mejoradas con contexto
    """
    logger.info(f"Recibida pregunta: '{request.question}' para departamento: {request.department}")
    
    try:
        # Obtener servicio RAG integrado
        integrated_service = await get_integrated_service()
        
        # Procesar pregunta con el servicio integrado
        rag_response = await integrated_service.ask_question(
            question=request.question,
            department=request.department,
            top_k=request.top_k,
            use_ai=request.use_ai
        )
        
        # Convertir a DTO de respuesta
        from application.dto.api_dto import SourceInfo, DocumentInfo
        
        sources = []
        for search_result in rag_response.sources:
            document_info = DocumentInfo(
                id=search_result.document.id,
                title=search_result.document.title,
                category=search_result.document.category,
                department=search_result.document.metadata.get("department") if search_result.document.metadata else None,
                similarity=search_result.chunk.similarity_score
            )
            
            source_info = SourceInfo(
                document=document_info,
                chunk_text=search_result.chunk.chunk_text[:200] + "..." if len(search_result.chunk.chunk_text) > 200 else search_result.chunk.chunk_text,
                relevance_score=search_result.relevance_score
            )
            
            sources.append(source_info)
        
        response = AskQuestionResponse(
            answer=rag_response.answer,
            question=request.question,
            sources=sources,
            confidence=rag_response.confidence,
            department=request.department,
            timestamp=datetime.now()
        )
        
        logger.info(f"Pregunta procesada exitosamente con confianza: {response.confidence:.2f}")
        return response
        
    except Exception as e:
        logger.error(f"Error procesando pregunta: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando pregunta: {str(e)}"
        )

@app.get("/ask",
         response_model=AskQuestionResponse,
         summary="Hacer pregunta simple via GET",
         description="Endpoint GET simplificado para hacer preguntas rápidas con datos precargados")
async def ask_question_get(
    question: str = Query(..., description="La pregunta a realizar", min_length=1, max_length=1000),
    department: Optional[str] = Query(None, description="Departamento para filtrar contexto"),
    use_ai: bool = Query(True, description="Si usar IA para generar la respuesta"),
    top_k: int = Query(5, description="Número máximo de documentos a considerar", ge=1, le=20)
) -> AskQuestionResponse:
    """Versión GET del endpoint ask_question para consultas rápidas con datos precargados"""
    
    request = AskQuestionRequest(
        question=question,
        department=department,
        use_ai=use_ai,
        top_k=top_k
    )
    
    return await ask_question(request)


@app.get("/system/integrated/status",
         summary="Estado del sistema integrado",
         description="Obtiene el estado del sistema RAG integrado")
async def get_integrated_system_status() -> Dict[str, Any]:
    """Obtiene el estado del sistema RAG integrado"""
    try:
        integrated_service = await get_integrated_service()
        system_info = integrated_service.get_system_info()
        
        return {
            "status": "healthy" if system_info["system_ready"] else "initializing",
            "system_info": system_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado integrado: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# ENDPOINTS DE GESTIÓN DE DOCUMENTOS
# ============================================================================

@app.post("/documents",
          response_model=AddDocumentResponse,
          status_code=status.HTTP_201_CREATED,
          summary="Añadir documento",
          description="Añade un nuevo documento al sistema RAG")
async def add_document(
    request: AddDocumentRequest,
    service: MainRAGService = Depends(get_main_service)
) -> AddDocumentResponse:
    """
    Añade un nuevo documento al sistema RAG
    
    - **title**: Título del documento
    - **content**: Contenido del documento
    - **category**: Categoría del documento
    - **department**: Departamento al que pertenece (opcional)
    - **metadata**: Metadatos adicionales (opcional)
    """
    logger.info(f"Añadiendo documento: '{request.title}' en categoría: {request.category}")
    
    response = await service.add_document(request)
    
    logger.info(f"Documento añadido con ID: {response.document_id}")
    return response

@app.get("/documents/search",
         response_model=SearchDocumentsResponse,
         summary="Buscar documentos",
         description="Busca documentos en el sistema con filtros opcionales")
async def search_documents(
    query: str = Query(..., description="Consulta de búsqueda", min_length=1, max_length=500),
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    department: Optional[str] = Query(None, description="Filtrar por departamento"),
    top_k: int = Query(5, description="Número de resultados", ge=1, le=50),
    service: MainRAGService = Depends(get_main_service)
) -> SearchDocumentsResponse:
    """
    Busca documentos en el sistema
    
    - **query**: Consulta de búsqueda
    - **category**: Filtrar por categoría (opcional)
    - **department**: Filtrar por departamento (opcional)
    - **top_k**: Número máximo de resultados
    """
    request = SearchDocumentsRequest(
        query=query,
        category=category,
        department=department,
        top_k=top_k
    )
    
    logger.info(f"Buscando documentos para: '{query}'")
    
    response = await service.search_documents(request)
    
    logger.info(f"Búsqueda completada: {response.total_found} documentos encontrados")
    return response

@app.delete("/documents/{document_id}",
            summary="Eliminar documento",
            description="Elimina un documento del sistema")
async def delete_document(
    document_id: int = Path(..., description="ID del documento a eliminar", ge=1),
    service: MainRAGService = Depends(get_main_service)
) -> Dict[str, Any]:
    """
    Elimina un documento del sistema
    
    - **document_id**: ID del documento a eliminar
    """
    logger.info(f"Eliminando documento con ID: {document_id}")
    
    result = await service.delete_document(document_id)
    
    logger.info(f"Documento {document_id} eliminado exitosamente")
    return result

# ============================================================================
# ENDPOINTS DE INFORMACIÓN DEL SISTEMA
# ============================================================================

@app.get("/system/info",
         response_model=SystemInfoResponse,
         summary="Información del sistema",
         description="Obtiene información general del sistema RAG")
async def get_system_info(
    service: MainRAGService = Depends(get_main_service)
) -> SystemInfoResponse:
    """
    Obtiene información general del sistema
    
    Incluye:
    - Número total de documentos
    - Categorías disponibles
    - Departamentos disponibles
    - Estado del sistema
    """
    logger.info("Obteniendo información del sistema")
    
    response = await service.get_system_info()
    
    logger.info("Información del sistema obtenida exitosamente")
    return response

@app.get("/system/stats",
         summary="Estadísticas del sistema",
         description="Obtiene estadísticas de uso del sistema")
async def get_system_stats(
    service: MainRAGService = Depends(get_main_service)
) -> Dict[str, Any]:
    """
    Obtiene estadísticas de uso del sistema
    
    Incluye:
    - Número de preguntas realizadas
    - Número de documentos añadidos
    - Número de búsquedas realizadas
    - Tiempo de actividad
    """
    logger.info("Obteniendo estadísticas del sistema")
    
    stats = service.get_stats()
    
    logger.info("Estadísticas obtenidas exitosamente")
    return stats

@app.get("/departments",
         response_model=List[str],
         summary="Listar departamentos",
         description="Obtiene la lista de departamentos disponibles")
async def get_departments(
    service: MainRAGService = Depends(get_main_service)
) -> List[str]:
    """
    Obtiene la lista de departamentos disponibles
    """
    logger.info("Obteniendo lista de departamentos")
    
    system_info = await service.get_system_info()
    
    logger.info(f"Departamentos obtenidos: {len(system_info.departments)}")
    return system_info.departments

@app.get("/departments/{department}/categories",
         response_model=List[str],
         summary="Categorías por departamento",
         description="Obtiene las categorías relevantes para un departamento")
async def get_department_categories(
    department: str = Path(..., description="Nombre del departamento"),
    service: MainRAGService = Depends(get_main_service)
) -> List[str]:
    """
    Obtiene las categorías relevantes para un departamento específico
    
    - **department**: Nombre del departamento
    """
    logger.info(f"Obteniendo categorías para departamento: {department}")
    
    categories = await service.get_department_categories(department)
    
    logger.info(f"Categorías para {department}: {len(categories)}")
    return categories

# ============================================================================
# ENDPOINTS DE SALUD Y MONITOREO
# ============================================================================

@app.get("/health",
         summary="Estado de salud",
         description="Endpoint de health check")
async def health_check() -> Dict[str, Any]:
    """
    Endpoint de health check para monitoreo
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "RAG API",
        "version": "1.0.0"
    }

@app.get("/",
         summary="Información de la API",
         description="Información básica de la API")
async def root() -> Dict[str, Any]:
    """
    Endpoint raíz con información básica de la API
    """
    return {
        "message": "Sistema RAG para Políticas de RRHH",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "main_endpoint": "/ask"
    }

# ============================================================================
# FUNCIÓN PARA EJECUTAR LA APLICACIÓN
# ============================================================================

def run_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """
    Ejecuta el servidor FastAPI
    
    Args:
        host: Host donde ejecutar el servidor
        port: Puerto donde ejecutar el servidor
        reload: Si habilitar recarga automática en desarrollo
    """
    logger.info(f"Iniciando servidor en {host}:{port}")
    
    uvicorn.run(
        "infrastructure.web.api.endpoints:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    run_server(reload=True)
