"""
Servicio principal de la API con ask_question y manejo de contexto por departamento
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

# Importar casos de uso y DTOs
from application.use_cases.ask_question_use_case import (
    AskQuestionUseCase, DepartmentContextService, UseCaseFactory
)
from application.dto.api_dto import (
    AskQuestionRequest, AskQuestionResponse, AddDocumentRequest, 
    AddDocumentResponse, SearchDocumentsRequest, SearchDocumentsResponse,
    SystemInfoResponse, DocumentInfo
)

# Importar adaptadores y servicios
from infrastructure.adapters.rag_service_adapter import RAGServiceFactory
from infrastructure.config.rag_config import rag_config

# Importar entidades de dominio
from domain.entities.domain import (
    RAGService, RAGDomainException, InvalidQueryError,
    DocumentNotFoundError, VectorSearchError, AIServiceError
)

logger = logging.getLogger(__name__)

class MainRAGService:
    """Servicio principal para la API RAG con contexto departamental"""
    
    def __init__(self, rag_service: RAGService, department_service: DepartmentContextService):
        self.rag_service = rag_service
        self.department_service = department_service
        self.ask_question_use_case = UseCaseFactory.create_ask_question_use_case(rag_service)
        self.logger = logging.getLogger(__name__)
        
        # Estadísticas del servicio
        self._stats = {
            "questions_asked": 0,
            "documents_added": 0,
            "searches_performed": 0,
            "start_time": datetime.now()
        }
    
    async def ask_question(self, request: AskQuestionRequest) -> AskQuestionResponse:
        """
        Método principal para hacer preguntas al sistema RAG con contexto departamental
        
        Args:
            request: Solicitud de pregunta con contexto opcional de departamento
            
        Returns:
            Respuesta con información contextualizada por departamento
        """
        try:
            self.logger.info(f"Procesando pregunta: '{request.question}' para departamento: {request.department}")
            
            # Ejecutar caso de uso
            response = self.ask_question_use_case.execute(request)
            
            # Actualizar estadísticas
            self._stats["questions_asked"] += 1
            
            self.logger.info(f"Pregunta procesada exitosamente con confianza: {response.confidence:.2f}")
            return response
            
        except InvalidQueryError as e:
            self.logger.warning(f"Consulta inválida: {e}")
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
    
    async def add_document(self, request: AddDocumentRequest) -> AddDocumentResponse:
        """
        Añade un documento al sistema RAG
        
        Args:
            request: Solicitud para añadir documento
            
        Returns:
            Respuesta con información del documento añadido
        """
        try:
            self.logger.info(f"Añadiendo documento: '{request.title}' en categoría: {request.category}")
            
            # Preparar metadatos incluyendo departamento
            metadata = request.metadata or {}
            if request.department:
                metadata["department"] = request.department
            metadata["added_at"] = datetime.now().isoformat()
            
            # Añadir documento usando el servicio RAG
            document_id = self.rag_service.add_document(
                title=request.title,
                content=request.content,
                category=request.category,
                metadata=metadata
            )
            
            # Actualizar estadísticas
            self._stats["documents_added"] += 1
            
            response = AddDocumentResponse(
                document_id=document_id,
                title=request.title,
                message=f"Documento '{request.title}' añadido exitosamente"
            )
            
            self.logger.info(f"Documento añadido con ID: {document_id}")
            return response
            
        except InvalidQueryError as e:
            self.logger.warning(f"Datos de documento inválidos: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error añadiendo documento: {e}")
            raise RAGDomainException(f"Error añadiendo documento: {str(e)}")
    
    async def search_documents(self, request: SearchDocumentsRequest) -> SearchDocumentsResponse:
        """
        Busca documentos en el sistema
        
        Args:
            request: Solicitud de búsqueda
            
        Returns:
            Respuesta con documentos encontrados
        """
        try:
            self.logger.info(f"Buscando documentos para: '{request.query}'")
            
            # Realizar búsqueda
            search_results = self.rag_service.search_documents(
                query=request.query,
                top_k=request.top_k,
                category=request.category
            )
            
            # Filtrar por departamento si se especifica
            if request.department:
                search_results = self.department_service.filter_by_department(
                    search_results, request.department
                )
            
            # Convertir a DTOs
            documents = []
            for result in search_results:
                doc_info = DocumentInfo(
                    id=result.document.id,
                    title=result.document.title,
                    category=result.document.category,
                    department=result.document.metadata.get("department") if result.document.metadata else None,
                    similarity=result.relevance_score
                )
                documents.append(doc_info)
            
            # Actualizar estadísticas
            self._stats["searches_performed"] += 1
            
            response = SearchDocumentsResponse(
                documents=documents,
                total_found=len(documents),
                query=request.query
            )
            
            self.logger.info(f"Búsqueda completada: {len(documents)} documentos encontrados")
            return response
            
        except InvalidQueryError as e:
            self.logger.warning(f"Consulta de búsqueda inválida: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error en búsqueda de documentos: {e}")
            raise VectorSearchError(f"Error en búsqueda: {str(e)}")
    
    async def get_system_info(self) -> SystemInfoResponse:
        """
        Obtiene información del sistema
        
        Returns:
            Información del estado del sistema
        """
        try:
            total_documents = self.rag_service.get_document_count()
            categories = self.rag_service.get_categories()
            departments = self.department_service.get_available_departments()
            
            response = SystemInfoResponse(
                total_documents=total_documents,
                categories=categories,
                departments=departments,
                system_status="active"
            )
            
            self.logger.info("Información del sistema obtenida exitosamente")
            return response
            
        except Exception as e:
            self.logger.error(f"Error obteniendo información del sistema: {e}")
            raise RAGDomainException(f"Error obteniendo información del sistema: {str(e)}")
    
    async def get_department_categories(self, department: str) -> List[str]:
        """
        Obtiene las categorías relevantes para un departamento
        
        Args:
            department: Nombre del departamento
            
        Returns:
            Lista de categorías relevantes
        """
        try:
            categories = self.department_service.get_department_categories(department)
            self.logger.info(f"Categorías para {department}: {categories}")
            return categories
            
        except Exception as e:
            self.logger.error(f"Error obteniendo categorías para departamento: {e}")
            raise RAGDomainException(f"Error obteniendo categorías: {str(e)}")
    
    async def delete_document(self, document_id: int) -> Dict[str, Any]:
        """
        Elimina un documento del sistema
        
        Args:
            document_id: ID del documento a eliminar
            
        Returns:
            Resultado de la operación
        """
        try:
            success = self.rag_service.delete_document(document_id)
            
            if success:
                message = f"Documento {document_id} eliminado exitosamente"
                self.logger.info(message)
                return {"success": True, "message": message}
            else:
                raise DocumentNotFoundError(f"No se pudo eliminar el documento {document_id}")
                
        except DocumentNotFoundError as e:
            self.logger.warning(f"Documento no encontrado: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error eliminando documento: {e}")
            raise RAGDomainException(f"Error eliminando documento: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del servicio
        
        Returns:
            Diccionario con estadísticas de uso
        """
        uptime = datetime.now() - self._stats["start_time"]
        
        return {
            **self._stats,
            "uptime_seconds": uptime.total_seconds(),
            "uptime_formatted": str(uptime).split('.')[0]  # Formato HH:MM:SS
        }

class MainServiceFactory:
    """Factory para crear el servicio principal"""
    
    @staticmethod
    def create_main_service(config: Optional[Dict[str, Any]] = None) -> MainRAGService:
        """
        Crea una instancia del servicio principal
        
        Args:
            config: Configuración opcional
            
        Returns:
            Instancia del servicio principal
        """
        try:
            # Usar configuración por defecto si no se proporciona
            if config is None:
                config = {
                    "database_path": rag_config.database_path,
                    "embedding_model": rag_config.embedding_model
                }
            
            # Crear servicio RAG
            rag_service = RAGServiceFactory.create_rag_service_from_config(config)
            
            # Crear servicio de contexto departamental
            department_service = UseCaseFactory.create_department_context_service()
            
            # Crear servicio principal
            main_service = MainRAGService(rag_service, department_service)
            
            logger.info("Servicio principal creado exitosamente")
            return main_service
            
        except Exception as e:
            logger.error(f"Error creando servicio principal: {e}")
            raise RAGDomainException(f"Error inicializando servicio principal: {str(e)}")
    
    @staticmethod
    def create_main_service_with_custom_db(db_path: str) -> MainRAGService:
        """
        Crea una instancia del servicio principal con base de datos personalizada
        
        Args:
            db_path: Ruta a la base de datos
            
        Returns:
            Instancia del servicio principal
        """
        config = {
            "database_path": db_path,
            "embedding_model": rag_config.embedding_model
        }
        
        return MainServiceFactory.create_main_service(config)
