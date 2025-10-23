"""
DTOs (Data Transfer Objects) para la API del sistema RAG
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

# ============================================================================
# REQUEST DTOs
# ============================================================================

class AskQuestionRequest(BaseModel):
    """DTO para solicitud de pregunta al sistema RAG"""
    question: str = Field(..., description="Pregunta del usuario", min_length=1, max_length=1000)
    department: Optional[str] = Field(None, description="Departamento para filtrar contexto")
    use_ai: bool = Field(True, description="Si usar IA para generar respuesta")
    top_k: int = Field(5, description="Número máximo de documentos a considerar", ge=1, le=20)
    
    class Config:
        schema_extra = {
            "example": {
                "question": "¿Cuál es la política de trabajo remoto?",
                "department": "rrhh",
                "use_ai": True,
                "top_k": 5
            }
        }

class AddDocumentRequest(BaseModel):
    """DTO para añadir un documento al sistema"""
    title: str = Field(..., description="Título del documento", min_length=1, max_length=200)
    content: str = Field(..., description="Contenido del documento", min_length=1)
    category: str = Field(..., description="Categoría del documento", min_length=1, max_length=50)
    department: Optional[str] = Field(None, description="Departamento al que pertenece")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Política de Vacaciones",
                "content": "Los empleados tienen derecho a 25 días de vacaciones anuales...",
                "category": "beneficios",
                "department": "rrhh",
                "metadata": {"version": "1.0", "author": "RRHH"}
            }
        }

class SearchDocumentsRequest(BaseModel):
    """DTO para búsqueda de documentos"""
    query: str = Field(..., description="Consulta de búsqueda", min_length=1, max_length=500)
    category: Optional[str] = Field(None, description="Filtrar por categoría")
    department: Optional[str] = Field(None, description="Filtrar por departamento")
    top_k: int = Field(5, description="Número de resultados", ge=1, le=50)
    
    class Config:
        schema_extra = {
            "example": {
                "query": "política de trabajo remoto",
                "category": "trabajo_remoto",
                "department": "rrhh",
                "top_k": 10
            }
        }

# ============================================================================
# RESPONSE DTOs
# ============================================================================

class DocumentInfo(BaseModel):
    """DTO para información de documento"""
    id: Optional[int] = Field(None, description="ID del documento")
    title: str = Field(..., description="Título del documento")
    category: str = Field(..., description="Categoría del documento")
    department: Optional[str] = Field(None, description="Departamento")
    similarity: Optional[float] = Field(None, description="Puntuación de similitud")
    
class SourceInfo(BaseModel):
    """DTO para información de fuente"""
    document: DocumentInfo
    chunk_text: Optional[str] = Field(None, description="Fragmento de texto relevante")
    relevance_score: float = Field(..., description="Puntuación de relevancia")

class AskQuestionResponse(BaseModel):
    """DTO para respuesta de pregunta"""
    answer: str = Field(..., description="Respuesta generada")
    question: str = Field(..., description="Pregunta original")
    sources: List[SourceInfo] = Field(default_factory=list, description="Fuentes consultadas")
    confidence: float = Field(..., description="Nivel de confianza", ge=0.0, le=1.0)
    department: Optional[str] = Field(None, description="Departamento consultado")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp de la respuesta")
    
    class Config:
        schema_extra = {
            "example": {
                "answer": "Google ofrece trabajo híbrido con 3 días en oficina y 2 días remotos...",
                "question": "¿Cuál es la política de trabajo remoto?",
                "sources": [
                    {
                        "document": {
                            "id": 1,
                            "title": "Política de Trabajo Remoto",
                            "category": "trabajo_remoto",
                            "department": "rrhh",
                            "similarity": 0.95
                        },
                        "relevance_score": 0.95
                    }
                ],
                "confidence": 0.95,
                "department": "rrhh",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }

class SearchDocumentsResponse(BaseModel):
    """DTO para respuesta de búsqueda de documentos"""
    documents: List[DocumentInfo] = Field(default_factory=list, description="Documentos encontrados")
    total_found: int = Field(..., description="Total de documentos encontrados")
    query: str = Field(..., description="Consulta original")
    
class AddDocumentResponse(BaseModel):
    """DTO para respuesta de añadir documento"""
    document_id: int = Field(..., description="ID del documento creado")
    title: str = Field(..., description="Título del documento")
    message: str = Field(..., description="Mensaje de confirmación")

class SystemInfoResponse(BaseModel):
    """DTO para información del sistema"""
    total_documents: int = Field(..., description="Total de documentos")
    categories: List[str] = Field(default_factory=list, description="Categorías disponibles")
    departments: List[str] = Field(default_factory=list, description="Departamentos disponibles")
    system_status: str = Field(..., description="Estado del sistema")

# ============================================================================
# ERROR DTOs
# ============================================================================

class ErrorResponse(BaseModel):
    """DTO para respuestas de error"""
    error: str = Field(..., description="Tipo de error")
    message: str = Field(..., description="Mensaje de error")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del error")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "La pregunta no puede estar vacía",
                "details": {"field": "question"},
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }

class ValidationErrorResponse(BaseModel):
    """DTO para errores de validación"""
    error: str = Field(default="ValidationError", description="Tipo de error")
    message: str = Field(..., description="Mensaje de error")
    validation_errors: List[Dict[str, Any]] = Field(default_factory=list, description="Errores de validación")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del error")
