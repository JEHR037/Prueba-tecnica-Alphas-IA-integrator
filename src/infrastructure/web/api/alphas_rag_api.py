"""
ALPHAS TECHNIQUE TEST IA - FastAPI RAG API
API REST con middleware de logging personalizado para el sistema RAG
"""

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

# Añadir paths para importar módulos
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

# Importar logger ALPHAS
from infrastructure.logger import (
    setup_alphas_middleware,
    alphas_endpoint_logger,
    log_alphas_info,
    log_alphas_error,
    log_alphas_rag_error,
    alphas_logger
)

# Importar sistema RAG
from services.RAG import GoogleHRPoliciesRAG, create_rag_system

# Modelos Pydantic para la API
class QueryRequest(BaseModel):
    """Modelo para requests de consulta"""
    question: str = Field(..., description="Pregunta sobre políticas de RRHH", min_length=3)
    category: Optional[str] = Field(None, description="Categoría específica para filtrar")
    use_openai: bool = Field(True, description="Usar OpenAI para generar respuesta")
    top_k: int = Field(5, description="Número de documentos similares a retornar", ge=1, le=20)

class DocumentRequest(BaseModel):
    """Modelo para añadir documentos"""
    title: str = Field(..., description="Título del documento", min_length=3)
    content: str = Field(..., description="Contenido del documento", min_length=10)
    category: str = Field(..., description="Categoría del documento", min_length=2)
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
    message: str
    technique: str = "ALPHAS TECHNIQUE TEST IA"

class SystemInfoResponse(BaseModel):
    """Modelo para información del sistema"""
    technique: str = "ALPHAS TECHNIQUE TEST IA"
    total_documents: int
    categories: List[str]
    status: str
    version: str = "1.0.0"

# Crear aplicación FastAPI
app = FastAPI(
    title="ALPHAS TECHNIQUE TEST IA - RAG API",
    description="Sistema RAG para políticas de RRHH de Google con logging avanzado ALPHAS",
    version="1.0.0",
    docs_url="/alphas/docs",
    redoc_url="/alphas/redoc"
)

# Configurar middlewares ALPHAS
setup_alphas_middleware(
    app=app,
    include_request_body=True,
    max_body_size=2048,
    enable_performance_monitoring=True,
    slow_request_threshold=2.0
)

# Inicializar sistema RAG
rag_system: GoogleHRPoliciesRAG = None

@app.on_event("startup")
async def startup_event():
    """Inicialización del sistema RAG al arrancar la API"""
    global rag_system
    
    try:
        log_alphas_info("🚀 Initializing ALPHAS TECHNIQUE TEST IA RAG System...")
        
        # Configurar contexto del logger
        alphas_logger.set_context(
            component="RAG_API",
            version="1.0.0",
            environment="production"
        )
        
        # Crear sistema RAG
        rag_system = create_rag_system("alphas_hr_policies.db")
        
        log_alphas_info(
            f"✅ ALPHAS RAG System initialized successfully | "
            f"Documents: {rag_system.get_document_count()} | "
            f"Categories: {len(rag_system.get_categories())}"
        )
        
    except Exception as e:
        log_alphas_rag_error("startup", e, operation="system_initialization")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al cerrar la API"""
    log_alphas_info("🔄 Shutting down ALPHAS TECHNIQUE TEST IA RAG System...")

# Endpoints de la API

@app.get("/", response_model=Dict[str, str])
@alphas_endpoint_logger("root_endpoint")
async def root():
    """Endpoint raíz con información ALPHAS"""
    return {
        "message": "🔥 ALPHAS TECHNIQUE TEST IA - RAG API 🔥",
        "technique": "ALPHAS TECHNIQUE TEST IA",
        "version": "1.0.0",
        "status": "active",
        "docs": "/alphas/docs"
    }

@app.get("/alphas/health", response_model=Dict[str, Any])
@alphas_endpoint_logger("health_check")
async def health_check():
    """Health check con información del sistema ALPHAS"""
    try:
        if not rag_system:
            raise HTTPException(status_code=503, detail="RAG system not initialized")
        
        return {
            "technique": "ALPHAS TECHNIQUE TEST IA",
            "status": "healthy",
            "rag_system": "operational",
            "total_documents": rag_system.get_document_count(),
            "categories": rag_system.get_categories(),
            "timestamp": alphas_logger.alphas_context.get("initialized_at")
        }
        
    except Exception as e:
        log_alphas_rag_error("health_check", e)
        raise HTTPException(status_code=503, detail="System health check failed")

@app.post("/alphas/query", response_model=RAGResponse)
@alphas_endpoint_logger("rag_query")
async def query_rag_system(request: QueryRequest):
    """
    Realizar consulta al sistema RAG con logging ALPHAS
    """
    try:
        if not rag_system:
            raise HTTPException(status_code=503, detail="RAG system not available")
        
        log_alphas_info(
            f"🔍 ALPHAS RAG QUERY | Question: {request.question[:100]}... | Category: {request.category}"
        )
        
        # Realizar consulta RAG
        result = rag_system.generate_rag_response(
            query=request.question,
            use_openai=request.use_openai
        )
        
        # Buscar documentos similares adicionales si se especifica top_k diferente
        if request.top_k != 5:
            similar_docs = rag_system.search_similar(
                query=request.question,
                top_k=request.top_k,
                category=request.category
            )
            
            # Actualizar fuentes con documentos adicionales
            result["sources"] = [
                {
                    "title": doc["title"],
                    "category": doc["category"],
                    "similarity": doc["similarity"]
                }
                for doc in similar_docs
            ]
        
        log_alphas_info(
            f"✅ ALPHAS RAG QUERY SUCCESS | "
            f"Confidence: {result['confidence']:.3f} | "
            f"Sources: {len(result['sources'])}"
        )
        
        return RAGResponse(
            success=True,
            answer=result["answer"],
            sources=result["sources"],
            confidence=result["confidence"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_alphas_rag_error(
            "query_processing", 
            e, 
            query=request.question,
            category=request.category
        )
        raise HTTPException(
            status_code=500, 
            detail="Error processing RAG query - ALPHAS TECHNIQUE TEST IA"
        )

@app.post("/alphas/documents", response_model=DocumentResponse)
@alphas_endpoint_logger("add_document")
async def add_document(request: DocumentRequest):
    """
    Añadir nuevo documento al sistema RAG
    """
    try:
        if not rag_system:
            raise HTTPException(status_code=503, detail="RAG system not available")
        
        log_alphas_info(
            f"📄 ALPHAS ADD DOCUMENT | Title: {request.title} | Category: {request.category}"
        )
        
        # Añadir documento
        document_id = rag_system.add_document(
            title=request.title,
            content=request.content,
            category=request.category,
            metadata=request.metadata or {}
        )
        
        log_alphas_info(f"✅ ALPHAS DOCUMENT ADDED | ID: {document_id} | Title: {request.title}")
        
        return DocumentResponse(
            success=True,
            document_id=document_id,
            message=f"Document '{request.title}' added successfully with ID {document_id}"
        )
        
    except Exception as e:
        log_alphas_rag_error(
            "add_document", 
            e, 
            title=request.title,
            category=request.category
        )
        raise HTTPException(
            status_code=500, 
            detail="Error adding document - ALPHAS TECHNIQUE TEST IA"
        )

@app.get("/alphas/documents/search", response_model=Dict[str, Any])
@alphas_endpoint_logger("search_documents")
async def search_documents(
    query: str = Query(..., description="Consulta de búsqueda"),
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    top_k: int = Query(5, description="Número de resultados", ge=1, le=20)
):
    """
    Buscar documentos similares sin generar respuesta
    """
    try:
        if not rag_system:
            raise HTTPException(status_code=503, detail="RAG system not available")
        
        log_alphas_info(f"🔎 ALPHAS SEARCH DOCUMENTS | Query: {query[:100]}...")
        
        # Buscar documentos similares
        similar_docs = rag_system.search_similar(
            query=query,
            top_k=top_k,
            category=category
        )
        
        log_alphas_info(f"✅ ALPHAS SEARCH SUCCESS | Found: {len(similar_docs)} documents")
        
        return {
            "technique": "ALPHAS TECHNIQUE TEST IA",
            "success": True,
            "query": query,
            "category": category,
            "total_results": len(similar_docs),
            "documents": similar_docs
        }
        
    except Exception as e:
        log_alphas_rag_error("search_documents", e, query=query, category=category)
        raise HTTPException(
            status_code=500, 
            detail="Error searching documents - ALPHAS TECHNIQUE TEST IA"
        )

@app.get("/alphas/system/info", response_model=SystemInfoResponse)
@alphas_endpoint_logger("system_info")
async def get_system_info():
    """
    Obtener información del sistema RAG
    """
    try:
        if not rag_system:
            raise HTTPException(status_code=503, detail="RAG system not available")
        
        return SystemInfoResponse(
            total_documents=rag_system.get_document_count(),
            categories=rag_system.get_categories(),
            status="operational"
        )
        
    except Exception as e:
        log_alphas_rag_error("system_info", e)
        raise HTTPException(
            status_code=500, 
            detail="Error getting system info - ALPHAS TECHNIQUE TEST IA"
        )

@app.delete("/alphas/documents/{document_id}", response_model=DocumentResponse)
@alphas_endpoint_logger("delete_document")
async def delete_document(document_id: int):
    """
    Eliminar documento del sistema RAG
    """
    try:
        if not rag_system:
            raise HTTPException(status_code=503, detail="RAG system not available")
        
        log_alphas_info(f"🗑️ ALPHAS DELETE DOCUMENT | ID: {document_id}")
        
        # Eliminar documento
        success = rag_system.delete_document(document_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        log_alphas_info(f"✅ ALPHAS DOCUMENT DELETED | ID: {document_id}")
        
        return DocumentResponse(
            success=True,
            message=f"Document {document_id} deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_alphas_rag_error("delete_document", e, document_id=document_id)
        raise HTTPException(
            status_code=500, 
            detail="Error deleting document - ALPHAS TECHNIQUE TEST IA"
        )

# Manejo de errores personalizado
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handler personalizado para errores 404"""
    return JSONResponse(
        status_code=404,
        content={
            "technique": "ALPHAS TECHNIQUE TEST IA",
            "error": True,
            "message": "Endpoint not found",
            "suggestion": "Check /alphas/docs for available endpoints"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handler personalizado para errores 500"""
    log_alphas_error("Internal server error in ALPHAS API", exc)
    
    return JSONResponse(
        status_code=500,
        content={
            "technique": "ALPHAS TECHNIQUE TEST IA",
            "error": True,
            "message": "Internal server error",
            "support": "Contact ALPHAS TECHNIQUE TEST IA support team"
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    log_alphas_info("🚀 Starting ALPHAS TECHNIQUE TEST IA RAG API Server...")
    
    uvicorn.run(
        "alphas_rag_api:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
