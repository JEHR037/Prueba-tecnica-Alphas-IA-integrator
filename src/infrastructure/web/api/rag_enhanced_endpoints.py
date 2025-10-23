"""
Endpoints RAG mejorados con datos precargados y funcionalidades avanzadas
Incluye carga automática de políticas de RRHH y optimizaciones para modelos modernos
"""

from typing import List, Dict, Any, Optional, AsyncGenerator
import logging
from datetime import datetime, timedelta
import asyncio
import json
from enum import Enum
import sys
from pathlib import Path

# Añadir el directorio src al path
sys.path.append(str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException, Depends, status, Query, Path as PathParam, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Importar DTOs existentes
from application.dto.api_dto import (
    AskQuestionRequest, AskQuestionResponse, AddDocumentRequest, 
    AddDocumentResponse, SearchDocumentsRequest, SearchDocumentsResponse,
    SystemInfoResponse, ErrorResponse
)

# Importar servicios de datos precargados
from infrastructure.services.data_loader_service import DataLoaderService, AutoDataLoader
from infrastructure.data.preloaded_hr_policies import (
    get_policy_categories, get_policy_departments, get_faq_data,
    get_all_preloaded_policies
)

# Importar servicio principal (simulado para este ejemplo)
# from infrastructure.web.api.main_service import MainRAGService, MainServiceFactory

# ============================================================================
# NUEVOS DTOs PARA RAG MEJORADO
# ============================================================================

class DataLoadStatus(BaseModel):
    """Estado de carga de datos precargados"""
    loaded: bool = Field(..., description="Si los datos están cargados")
    total_documents: int = Field(..., description="Total de documentos cargados")
    categories: List[str] = Field(..., description="Categorías disponibles")
    departments: List[str] = Field(..., description="Departamentos disponibles")
    last_load: Optional[datetime] = Field(None, description="Última carga de datos")
    load_time_seconds: Optional[float] = Field(None, description="Tiempo de carga")

class PreloadedDataInfo(BaseModel):
    """Información sobre datos precargados disponibles"""
    total_policies: int = Field(..., description="Total de políticas disponibles")
    categories: Dict[str, int] = Field(..., description="Políticas por categoría")
    departments: Dict[str, int] = Field(..., description="Políticas por departamento")
    sample_policies: List[Dict[str, Any]] = Field(..., description="Muestra de políticas")
    faq_count: int = Field(..., description="Número de FAQs disponibles")

class EnhancedAskRequest(AskQuestionRequest):
    """Request mejorado que incluye opciones de datos precargados"""
    use_preloaded_only: bool = Field(False, description="Usar solo datos precargados")
    include_faq: bool = Field(True, description="Incluir FAQs en búsqueda")
    prefer_recent: bool = Field(False, description="Preferir documentos recientes")

class SystemInitRequest(BaseModel):
    """Request para inicialización del sistema"""
    force_reload: bool = Field(False, description="Forzar recarga de datos")
    load_categories: Optional[List[str]] = Field(None, description="Categorías específicas a cargar")
    auto_validate: bool = Field(True, description="Validar datos después de cargar")

# ============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="🔥 ALPHAS RAG Enhanced API 🔥",
    description="API RAG mejorada con datos precargados de políticas de RRHH y funcionalidades avanzadas",
    version="2.1.0",
    docs_url="/enhanced/docs",
    redoc_url="/enhanced/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales para servicios
_data_loader: Optional[DataLoaderService] = None
_system_initialized: bool = False

# ============================================================================
# SERVICIOS SIMULADOS (En implementación real, usar servicios reales)
# ============================================================================

class MockRAGService:
    """Servicio RAG simulado para demostración"""
    
    def __init__(self):
        self.documents = []
        self.doc_counter = 0
        self.categories = set()
    
    def add_document(self, title: str, content: str, category: str, metadata: Dict[str, Any] = None) -> int:
        self.doc_counter += 1
        doc = {
            "id": self.doc_counter,
            "title": title,
            "content": content,
            "category": category,
            "metadata": metadata or {}
        }
        self.documents.append(doc)
        self.categories.add(category)
        return self.doc_counter
    
    def get_document_count(self) -> int:
        return len(self.documents)
    
    def get_categories(self) -> List[str]:
        return list(self.categories)
    
    def search_documents(self, query: str, top_k: int = 5, category: Optional[str] = None):
        # Búsqueda simulada simple
        results = []
        query_lower = query.lower()
        
        for doc in self.documents:
            if category and doc["category"] != category:
                continue
            
            # Búsqueda simple en título y contenido
            if (query_lower in doc["title"].lower() or 
                query_lower in doc["content"].lower()):
                
                # Simular resultado de búsqueda
                from domain.entities.domain import Document, DocumentChunk, SearchResult
                
                document = Document(
                    id=doc["id"],
                    title=doc["title"],
                    content=doc["content"],
                    category=doc["category"],
                    metadata=doc["metadata"]
                )
                
                chunk = DocumentChunk(
                    id=doc["id"],
                    document_id=doc["id"],
                    chunk_text=doc["content"][:200] + "...",
                    similarity_score=0.85
                )
                
                result = SearchResult(
                    document=document,
                    chunk=chunk,
                    relevance_score=0.85
                )
                
                results.append(result)
                
                if len(results) >= top_k:
                    break
        
        return results
    
    def generate_response(self, query: str, use_ai: bool = True):
        # Generar respuesta simulada
        from domain.entities.domain import RAGResponse
        
        search_results = self.search_documents(query, top_k=3)
        
        if search_results:
            answer = f"Basándome en las políticas cargadas, puedo responder sobre '{query}'. "
            answer += f"Encontré {len(search_results)} documentos relevantes. "
            answer += f"El más relevante es: {search_results[0].document.title}"
        else:
            answer = f"No encontré información específica sobre '{query}' en las políticas cargadas."
        
        return RAGResponse(
            answer=answer,
            sources=search_results,
            confidence=0.8 if search_results else 0.2,
            query=query
        )

# Instancia global del servicio simulado
_mock_rag_service = MockRAGService()

# ============================================================================
# DEPENDENCIAS
# ============================================================================

async def get_data_loader() -> DataLoaderService:
    """Dependencia para obtener el data loader"""
    global _data_loader, _system_initialized
    
    if _data_loader is None or not _system_initialized:
        logger.info("🚀 Inicializando sistema RAG con datos precargados...")
        _data_loader = await AutoDataLoader.initialize_system(_mock_rag_service, auto_load=True)
        _system_initialized = True
        logger.info("✅ Sistema RAG inicializado correctamente")
    
    return _data_loader

def get_rag_service():
    """Dependencia para obtener el servicio RAG"""
    return _mock_rag_service

# ============================================================================
# ENDPOINTS DE INICIALIZACIÓN Y GESTIÓN DE DATOS
# ============================================================================

@app.post("/enhanced/system/initialize",
          response_model=Dict[str, Any],
          summary="Inicializar sistema con datos precargados",
          description="Inicializa o reinicializa el sistema RAG con datos precargados")
async def initialize_system(
    request: SystemInitRequest,
    background_tasks: BackgroundTasks,
    data_loader: DataLoaderService = Depends(get_data_loader)
) -> Dict[str, Any]:
    """
    Inicializa el sistema RAG con datos precargados
    
    - **force_reload**: Forzar recarga aunque ya existan datos
    - **load_categories**: Cargar solo categorías específicas
    - **auto_validate**: Validar datos después de cargar
    """
    logger.info("🔄 Iniciando inicialización del sistema RAG...")
    
    try:
        # Cargar datos en background si es una recarga completa
        if request.force_reload:
            background_tasks.add_task(
                _reload_system_data, 
                data_loader, 
                request.load_categories,
                request.auto_validate
            )
            
            return {
                "status": "initializing",
                "message": "Recarga del sistema iniciada en background",
                "force_reload": request.force_reload,
                "categories": request.load_categories,
                "timestamp": datetime.now().isoformat()
            }
        
        # Obtener estadísticas actuales
        stats = data_loader.get_load_statistics()
        
        return {
            "status": "ready" if stats["system_ready"] else "not_initialized",
            "message": "Sistema RAG listo" if stats["system_ready"] else "Sistema requiere inicialización",
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error inicializando sistema: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inicializando sistema: {e}"
        )

async def _reload_system_data(
    data_loader: DataLoaderService, 
    categories: Optional[List[str]], 
    validate: bool
):
    """Tarea en background para recargar datos del sistema"""
    try:
        if categories:
            for category in categories:
                await data_loader.reload_category(category)
        else:
            await data_loader.load_all_preloaded_data(force_reload=True)
        
        if validate:
            await data_loader.validate_loaded_data()
            
        logger.info("✅ Recarga del sistema completada en background")
        
    except Exception as e:
        logger.error(f"❌ Error en recarga background: {e}")

@app.get("/enhanced/system/status",
         response_model=DataLoadStatus,
         summary="Estado del sistema de datos",
         description="Obtiene el estado actual de los datos precargados")
async def get_system_status(
    data_loader: DataLoaderService = Depends(get_data_loader)
) -> DataLoadStatus:
    """Obtiene el estado actual del sistema de datos precargados"""
    
    stats = data_loader.get_load_statistics()
    
    return DataLoadStatus(
        loaded=stats["system_ready"],
        total_documents=stats["loaded_documents_count"],
        categories=stats["available_categories"],
        departments=stats["available_departments"],
        last_load=stats["load_stats"]["last_load"],
        load_time_seconds=stats["load_stats"]["load_time"]
    )

@app.get("/enhanced/data/info",
         response_model=PreloadedDataInfo,
         summary="Información de datos precargados",
         description="Obtiene información sobre los datos precargados disponibles")
async def get_preloaded_data_info() -> PreloadedDataInfo:
    """Obtiene información sobre los datos precargados disponibles"""
    
    all_policies = get_all_preloaded_policies()
    faq_data = get_faq_data()
    
    # Contar por categoría
    categories = {}
    departments = {}
    
    for policy in all_policies:
        cat = policy["category"]
        dept = policy.get("department", "unknown")
        
        categories[cat] = categories.get(cat, 0) + 1
        departments[dept] = departments.get(dept, 0) + 1
    
    # Muestra de políticas (primeras 3)
    sample_policies = [
        {
            "title": policy["title"],
            "category": policy["category"],
            "department": policy.get("department"),
            "content_preview": policy["content"][:200] + "..."
        }
        for policy in all_policies[:3]
    ]
    
    return PreloadedDataInfo(
        total_policies=len(all_policies),
        categories=categories,
        departments=departments,
        sample_policies=sample_policies,
        faq_count=len(faq_data)
    )

# ============================================================================
# ENDPOINTS PRINCIPALES MEJORADOS
# ============================================================================

@app.post("/enhanced/ask",
          response_model=AskQuestionResponse,
          summary="Pregunta mejorada con datos precargados",
          description="Endpoint principal mejorado que utiliza datos precargados")
async def ask_enhanced(
    request: EnhancedAskRequest,
    data_loader: DataLoaderService = Depends(get_data_loader),
    rag_service = Depends(get_rag_service)
) -> AskQuestionResponse:
    """
    Endpoint mejorado para preguntas que utiliza datos precargados
    
    Características:
    - Acceso a políticas de RRHH precargadas
    - Búsqueda en FAQs
    - Filtrado por datos precargados únicamente
    - Preferencia por documentos recientes
    """
    logger.info(f"🔍 Procesando pregunta mejorada: '{request.question}'")
    
    try:
        # Verificar que el sistema esté inicializado
        stats = data_loader.get_load_statistics()
        if not stats["system_ready"]:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Sistema no inicializado. Use /enhanced/system/initialize primero."
            )
        
        # Generar respuesta usando el servicio RAG
        rag_response = rag_service.generate_response(request.question, request.use_ai)
        
        # Convertir a formato de respuesta
        from application.dto.api_dto import SourceInfo, DocumentInfo
        
        sources = []
        for search_result in rag_response.sources:
            document_info = DocumentInfo(
                id=search_result.document.id,
                title=search_result.document.title,
                category=search_result.document.category,
                department=search_result.document.metadata.get("department"),
                similarity=search_result.chunk.similarity_score
            )
            
            source_info = SourceInfo(
                document=document_info,
                chunk_text=search_result.chunk.chunk_text,
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
        
        logger.info(f"✅ Pregunta procesada con confianza: {response.confidence:.2f}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error procesando pregunta: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando pregunta: {e}"
        )

@app.get("/enhanced/ask/quick",
         response_model=AskQuestionResponse,
         summary="Pregunta rápida con datos precargados",
         description="Endpoint GET para preguntas rápidas usando datos precargados")
async def ask_quick(
    question: str = Query(..., description="Pregunta a realizar", min_length=1, max_length=500),
    department: Optional[str] = Query(None, description="Departamento para filtrar"),
    include_faq: bool = Query(True, description="Incluir FAQs en búsqueda"),
    data_loader: DataLoaderService = Depends(get_data_loader)
) -> AskQuestionResponse:
    """Endpoint GET para preguntas rápidas usando datos precargados"""
    
    request = EnhancedAskRequest(
        question=question,
        department=department,
        include_faq=include_faq,
        use_preloaded_only=True
    )
    
    return await ask_enhanced(request, data_loader)

# ============================================================================
# ENDPOINTS DE GESTIÓN DE CATEGORÍAS Y DEPARTAMENTOS
# ============================================================================

@app.get("/enhanced/categories",
         response_model=List[Dict[str, Any]],
         summary="Categorías con estadísticas",
         description="Obtiene categorías disponibles con estadísticas de documentos")
async def get_categories_with_stats(
    data_loader: DataLoaderService = Depends(get_data_loader)
) -> List[Dict[str, Any]]:
    """Obtiene categorías disponibles con estadísticas"""
    
    stats = data_loader.get_load_statistics()
    categories_info = []
    
    for category in stats["available_categories"]:
        # Obtener estadísticas de la categoría
        category_stats = stats["load_stats"]["categories"].get(category, 0)
        
        categories_info.append({
            "name": category,
            "document_count": category_stats,
            "description": _get_category_description(category),
            "sample_topics": _get_category_topics(category)
        })
    
    return categories_info

@app.get("/enhanced/departments/{department}/policies",
         response_model=List[Dict[str, Any]],
         summary="Políticas por departamento",
         description="Obtiene políticas específicas de un departamento")
async def get_department_policies(
    department: str = PathParam(..., description="Nombre del departamento"),
    data_loader: DataLoaderService = Depends(get_data_loader)
) -> List[Dict[str, Any]]:
    """Obtiene políticas específicas de un departamento"""
    
    from infrastructure.data.preloaded_hr_policies import get_policies_by_department
    
    policies = get_policies_by_department(department)
    
    if not policies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron políticas para el departamento: {department}"
        )
    
    # Formatear respuesta
    formatted_policies = []
    for policy in policies:
        formatted_policies.append({
            "title": policy["title"],
            "category": policy["category"],
            "content_preview": policy["content"][:300] + "...",
            "metadata": policy.get("metadata", {}),
            "last_updated": policy.get("metadata", {}).get("effective_date")
        })
    
    return formatted_policies

# ============================================================================
# ENDPOINTS DE BÚSQUEDA AVANZADA
# ============================================================================

@app.get("/enhanced/search/faq",
         response_model=List[Dict[str, Any]],
         summary="Buscar en FAQs",
         description="Búsqueda específica en preguntas frecuentes")
async def search_faq(
    query: str = Query(..., description="Consulta de búsqueda", min_length=1),
    category: Optional[str] = Query(None, description="Filtrar por categoría")
) -> List[Dict[str, Any]]:
    """Búsqueda específica en preguntas frecuentes"""
    
    faq_data = get_faq_data()
    results = []
    query_lower = query.lower()
    
    for faq in faq_data:
        # Filtrar por categoría si se especifica
        if category and faq["category"] != category:
            continue
        
        # Búsqueda en pregunta, respuesta y keywords
        if (query_lower in faq["question"].lower() or
            query_lower in faq["answer"].lower() or
            any(query_lower in keyword.lower() for keyword in faq["keywords"])):
            
            results.append({
                "question": faq["question"],
                "answer": faq["answer"],
                "category": faq["category"],
                "keywords": faq["keywords"],
                "relevance": "high"  # Simplificado para demo
            })
    
    return results

# ============================================================================
# ENDPOINTS DE MONITOREO Y SALUD
# ============================================================================

@app.get("/enhanced/health",
         summary="Health check mejorado",
         description="Health check que incluye estado de datos precargados")
async def enhanced_health_check(
    data_loader: DataLoaderService = Depends(get_data_loader)
) -> Dict[str, Any]:
    """Health check mejorado que incluye estado de datos precargados"""
    
    stats = data_loader.get_load_statistics()
    
    health_status = {
        "status": "healthy" if stats["system_ready"] else "degraded",
        "timestamp": datetime.now().isoformat(),
        "version": "2.1.0",
        "components": {
            "preloaded_data": {
                "status": "healthy" if stats["system_ready"] else "not_loaded",
                "documents_loaded": stats["loaded_documents_count"],
                "categories_available": len(stats["available_categories"]),
                "last_load": stats["load_stats"]["last_load"].isoformat() if stats["load_stats"]["last_load"] else None
            },
            "rag_service": {
                "status": "healthy",
                "total_documents": _mock_rag_service.get_document_count(),
                "categories": len(_mock_rag_service.get_categories())
            }
        },
        "capabilities": {
            "preloaded_policies": True,
            "faq_search": True,
            "department_filtering": True,
            "category_filtering": True,
            "enhanced_search": True
        }
    }
    
    return health_status

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def _get_category_description(category: str) -> str:
    """Obtiene descripción de una categoría"""
    descriptions = {
        "beneficios": "Políticas relacionadas con beneficios de empleados, seguros y compensaciones",
        "vacaciones": "Políticas de tiempo libre, vacaciones y licencias",
        "trabajo_remoto": "Políticas de trabajo remoto, híbrido y flexibilidad laboral",
        "desarrollo": "Programas de desarrollo profesional y capacitación",
        "diversidad": "Políticas de diversidad, inclusión y equidad",
        "compensacion": "Estructura de compensación, salarios y bonos",
        "etica": "Código de conducta, ética y cumplimiento"
    }
    return descriptions.get(category, "Categoría de políticas de RRHH")

def _get_category_topics(category: str) -> List[str]:
    """Obtiene temas principales de una categoría"""
    topics = {
        "beneficios": ["seguro médico", "401k", "seguro dental", "bienestar"],
        "vacaciones": ["tiempo libre flexible", "días festivos", "licencia parental"],
        "trabajo_remoto": ["modelo híbrido", "equipamiento", "productividad"],
        "desarrollo": ["20% time", "presupuesto capacitación", "mentorship"],
        "diversidad": ["ERGs", "inclusión", "anti-discriminación"],
        "compensacion": ["bandas salariales", "equity", "bonus", "evaluación"],
        "etica": ["código de conducta", "conflictos de interés", "cumplimiento"]
    }
    return topics.get(category, ["políticas generales"])

# ============================================================================
# ENDPOINT RAÍZ
# ============================================================================

@app.get("/enhanced",
         summary="Información de la API mejorada",
         description="Información básica de la API RAG mejorada")
async def enhanced_root() -> Dict[str, Any]:
    """Endpoint raíz con información de la API mejorada"""
    
    return {
        "message": "🔥 ALPHAS RAG Enhanced API 🔥",
        "version": "2.1.0",
        "features": [
            "Datos precargados de políticas de RRHH",
            "Búsqueda en FAQs",
            "Filtrado por departamento y categoría",
            "Inicialización automática del sistema",
            "Endpoints de gestión de datos",
            "Health checks mejorados"
        ],
        "endpoints": {
            "main": "/enhanced/ask",
            "quick": "/enhanced/ask/quick",
            "initialize": "/enhanced/system/initialize",
            "status": "/enhanced/system/status",
            "health": "/enhanced/health",
            "docs": "/enhanced/docs"
        },
        "data_info": {
            "preloaded_policies": len(get_all_preloaded_policies()),
            "faq_count": len(get_faq_data()),
            "categories": get_policy_categories(),
            "departments": get_policy_departments()
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "rag_enhanced_endpoints:app",
        host="127.0.0.1",
        port=8002,
        reload=True,
        log_level="info"
    )
