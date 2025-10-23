"""
Casos de uso para el sistema de preguntas y respuestas con contexto por departamento
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import logging
from datetime import datetime

# Importar entidades y puertos del dominio
from domain.entities.domain import (
    Document, DocumentChunk, SearchResult, RAGResponse,
    RAGService, HRPolicyService, RAGDomainException,
    InvalidQueryError, VectorSearchError, AIServiceError
)

# Importar DTOs
from application.dto.api_dto import (
    AskQuestionRequest, AskQuestionResponse, SourceInfo, DocumentInfo
)

logger = logging.getLogger(__name__)

# ============================================================================
# INTERFACES DE CASOS DE USO
# ============================================================================

class AskQuestionUseCase(ABC):
    """Caso de uso para hacer preguntas al sistema RAG"""
    
    @abstractmethod
    def execute(self, request: AskQuestionRequest) -> AskQuestionResponse:
        """Ejecuta el caso de uso de pregunta"""
        pass

class DepartmentContextService(ABC):
    """Servicio para manejar contexto por departamento"""
    
    @abstractmethod
    def get_department_categories(self, department: str) -> List[str]:
        """Obtiene las categorías relevantes para un departamento"""
        pass
    
    @abstractmethod
    def filter_by_department(self, documents: List[SearchResult], department: str) -> List[SearchResult]:
        """Filtra documentos por departamento"""
        pass
    
    @abstractmethod
    def get_available_departments(self) -> List[str]:
        """Obtiene los departamentos disponibles"""
        pass

# ============================================================================
# IMPLEMENTACIONES
# ============================================================================

class DepartmentContextServiceImpl(DepartmentContextService):
    """Implementación del servicio de contexto por departamento"""
    
    def __init__(self):
        # Mapeo de departamentos a categorías relevantes
        self.department_categories = {
            "rrhh": ["beneficios", "vacaciones", "desarrollo", "diversidad", "compensacion", "etica"],
            "it": ["trabajo_remoto", "desarrollo", "innovacion", "tecnologia"],
            "legal": ["etica", "cumplimiento", "politicas", "contratos"],
            "finanzas": ["compensacion", "beneficios", "presupuesto"],
            "marketing": ["comunicacion", "branding", "eventos"],
            "ventas": ["incentivos", "comisiones", "objetivos"],
            "operaciones": ["procesos", "calidad", "eficiencia"],
            "general": []  # Sin filtro específico
        }
        
        # Palabras clave por departamento para filtrado adicional
        self.department_keywords = {
            "rrhh": ["empleado", "personal", "contratación", "beneficio", "salario", "vacaciones"],
            "it": ["tecnología", "sistema", "software", "desarrollo", "código"],
            "legal": ["legal", "contrato", "cumplimiento", "regulación", "ley"],
            "finanzas": ["financiero", "presupuesto", "costo", "inversión", "gasto"],
            "marketing": ["marketing", "publicidad", "campaña", "marca", "cliente"],
            "ventas": ["venta", "cliente", "objetivo", "comisión", "meta"],
            "operaciones": ["proceso", "operación", "calidad", "eficiencia", "producción"]
        }
    
    def get_department_categories(self, department: str) -> List[str]:
        """Obtiene las categorías relevantes para un departamento"""
        department_lower = department.lower() if department else "general"
        return self.department_categories.get(department_lower, [])
    
    def filter_by_department(self, documents: List[SearchResult], department: str) -> List[SearchResult]:
        """Filtra documentos por departamento usando categorías y palabras clave"""
        if not department or department.lower() == "general":
            return documents
        
        department_lower = department.lower()
        relevant_categories = self.get_department_categories(department_lower)
        keywords = self.department_keywords.get(department_lower, [])
        
        filtered_docs = []
        
        for doc in documents:
            # Filtrar por categoría
            if relevant_categories and doc.document.category in relevant_categories:
                filtered_docs.append(doc)
                continue
            
            # Filtrar por palabras clave en el contenido
            content_lower = (doc.chunk.chunk_text + " " + doc.document.title).lower()
            if any(keyword in content_lower for keyword in keywords):
                # Ajustar el score de relevancia basado en el contexto departamental
                doc.relevance_score *= 0.8  # Penalizar ligeramente por no estar en categoría específica
                filtered_docs.append(doc)
        
        return filtered_docs
    
    def get_available_departments(self) -> List[str]:
        """Obtiene los departamentos disponibles"""
        return list(self.department_categories.keys())

class AskQuestionUseCaseImpl(AskQuestionUseCase):
    """Implementación del caso de uso para hacer preguntas"""
    
    def __init__(self, rag_service: RAGService, department_service: DepartmentContextService):
        self.rag_service = rag_service
        self.department_service = department_service
        self.logger = logging.getLogger(__name__)
    
    def execute(self, request: AskQuestionRequest) -> AskQuestionResponse:
        """Ejecuta el caso de uso de pregunta con contexto departamental"""
        try:
            # Validar la solicitud
            self._validate_request(request)
            
            # Buscar documentos relevantes
            search_results = self._search_documents(request)
            
            # Filtrar por departamento si se especifica
            if request.department:
                search_results = self.department_service.filter_by_department(
                    search_results, request.department
                )
            
            # Generar respuesta
            rag_response = self._generate_response(request, search_results)
            
            # Convertir a DTO de respuesta
            return self._convert_to_response_dto(rag_response, request)
            
        except InvalidQueryError as e:
            self.logger.error(f"Consulta inválida: {e}")
            raise
        except VectorSearchError as e:
            self.logger.error(f"Error en búsqueda vectorial: {e}")
            raise
        except AIServiceError as e:
            self.logger.error(f"Error en servicio de IA: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado en ask_question: {e}")
            raise RAGDomainException(f"Error procesando pregunta: {str(e)}")
    
    def _validate_request(self, request: AskQuestionRequest) -> None:
        """Valida la solicitud de pregunta"""
        if not request.question or not request.question.strip():
            raise InvalidQueryError("La pregunta no puede estar vacía")
        
        if len(request.question) > 1000:
            raise InvalidQueryError("La pregunta es demasiado larga (máximo 1000 caracteres)")
        
        if request.top_k < 1 or request.top_k > 20:
            raise InvalidQueryError("top_k debe estar entre 1 y 20")
        
        # Validar departamento si se proporciona
        if request.department:
            available_departments = self.department_service.get_available_departments()
            if request.department.lower() not in available_departments:
                raise InvalidQueryError(
                    f"Departamento '{request.department}' no válido. "
                    f"Departamentos disponibles: {', '.join(available_departments)}"
                )
    
    def _search_documents(self, request: AskQuestionRequest) -> List[SearchResult]:
        """Busca documentos relevantes"""
        try:
            # Determinar categoría basada en departamento
            category = None
            if request.department:
                dept_categories = self.department_service.get_department_categories(request.department)
                # Si hay categorías específicas para el departamento, no filtrar por categoría aquí
                # El filtrado se hará después con más sofisticación
                pass
            
            return self.rag_service.search_documents(
                query=request.question,
                top_k=request.top_k,
                category=category
            )
        except Exception as e:
            raise VectorSearchError(f"Error en búsqueda de documentos: {str(e)}")
    
    def _generate_response(self, request: AskQuestionRequest, search_results: List[SearchResult]) -> RAGResponse:
        """Genera la respuesta usando el servicio RAG"""
        try:
            # Si no hay resultados relevantes
            if not search_results:
                return RAGResponse(
                    answer=self._get_no_results_message(request.department),
                    sources=[],
                    confidence=0.0,
                    query=request.question
                )
            
            # Generar respuesta usando el servicio RAG
            return self.rag_service.generate_response(
                query=request.question,
                use_ai=request.use_ai
            )
            
        except Exception as e:
            raise AIServiceError(f"Error generando respuesta: {str(e)}")
    
    def _get_no_results_message(self, department: Optional[str]) -> str:
        """Genera mensaje cuando no hay resultados"""
        if department:
            return (f"No encontré información específica sobre tu consulta en las políticas "
                   f"del departamento de {department}. Puedes intentar con una pregunta más "
                   f"general o consultar otro departamento.")
        else:
            return ("No encontré información relevante sobre tu consulta en las políticas "
                   "disponibles. Puedes intentar reformular tu pregunta o especificar "
                   "un departamento específico.")
    
    def _convert_to_response_dto(self, rag_response: RAGResponse, request: AskQuestionRequest) -> AskQuestionResponse:
        """Convierte la respuesta del dominio a DTO"""
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
        
        return AskQuestionResponse(
            answer=rag_response.answer,
            question=request.question,
            sources=sources,
            confidence=rag_response.confidence,
            department=request.department,
            timestamp=datetime.now()
        )

# ============================================================================
# FACTORY PARA CASOS DE USO
# ============================================================================

class UseCaseFactory:
    """Factory para crear casos de uso"""
    
    @staticmethod
    def create_ask_question_use_case(rag_service: RAGService) -> AskQuestionUseCase:
        """Crea el caso de uso de ask_question"""
        department_service = DepartmentContextServiceImpl()
        return AskQuestionUseCaseImpl(rag_service, department_service)
    
    @staticmethod
    def create_department_context_service() -> DepartmentContextService:
        """Crea el servicio de contexto departamental"""
        return DepartmentContextServiceImpl()
