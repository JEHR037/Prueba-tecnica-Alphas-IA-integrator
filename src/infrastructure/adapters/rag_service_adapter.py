"""
Adaptador para integrar el servicio RAG existente con la arquitectura hexagonal
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

# Importar entidades y puertos del dominio
from domain.entities.domain import (
    Document, DocumentChunk, SearchResult, RAGResponse,
    RAGService, DocumentRepository, VectorRepository,
    EmbeddingService, TextProcessor, OpenAIClient,
    RAGDomainException, DocumentNotFoundError, InvalidQueryError,
    EmbeddingGenerationError, VectorSearchError, AIServiceError
)

# Importar el factory del servicio RAG
from infrastructure.config.rag_factory import RAGFactory
from application.use_cases.rag_service_impl import RAGServiceImpl

logger = logging.getLogger(__name__)

class RAGServiceAdapter(RAGService):
    """Adaptador que implementa la interfaz RAGService usando RAGServiceImpl"""
    
    def __init__(self, rag_system: RAGServiceImpl):
        self.rag_system = rag_system
        self.logger = logging.getLogger(__name__)
    
    def add_document(self, title: str, content: str, category: str, 
                    metadata: Dict[str, Any] = None) -> int:
        """Añade un documento al sistema RAG"""
        try:
            if not title or not title.strip():
                raise InvalidQueryError("El título del documento no puede estar vacío")
            
            if not content or not content.strip():
                raise InvalidQueryError("El contenido del documento no puede estar vacío")
            
            if not category or not category.strip():
                raise InvalidQueryError("La categoría del documento no puede estar vacía")
            
            document_id = self.rag_system.add_document(
                title=title.strip(),
                content=content.strip(),
                category=category.strip(),
                metadata=metadata or {}
            )
            
            self.logger.info(f"Documento '{title}' añadido con ID: {document_id}")
            return document_id
            
        except Exception as e:
            self.logger.error(f"Error añadiendo documento: {e}")
            if isinstance(e, (InvalidQueryError, RAGDomainException)):
                raise
            raise RAGDomainException(f"Error añadiendo documento: {str(e)}")
    
    def search_documents(self, query: str, top_k: int = 5, 
                        category: Optional[str] = None) -> List[SearchResult]:
        """Busca documentos relevantes delegando en RAGServiceImpl"""
        try:
            if not query or not query.strip():
                raise InvalidQueryError("La consulta de búsqueda no puede estar vacía")
            if top_k < 1 or top_k > 50:
                raise InvalidQueryError("top_k debe estar entre 1 y 50")

            results = self.rag_system.search_documents(
                query=query.strip(),
                top_k=top_k,
                category=category
            )
            self.logger.info(f"Encontrados {len(results)} documentos para la consulta")
            return results
        except Exception as e:
            self.logger.error(f"Error en búsqueda de documentos: {e}")
            if isinstance(e, (InvalidQueryError, RAGDomainException)):
                raise
            raise VectorSearchError(f"Error en búsqueda: {str(e)}")
    
    def generate_response(self, query: str, use_ai: bool = True) -> RAGResponse:
        """Genera una respuesta completa delegando en RAGServiceImpl"""
        try:
            if not query or not query.strip():
                raise InvalidQueryError("La consulta no puede estar vacía")
            return self.rag_system.generate_response(query.strip(), use_ai=use_ai)
        except Exception as e:
            self.logger.error(f"Error generando respuesta: {e}")
            if isinstance(e, (InvalidQueryError, RAGDomainException)):
                raise
            raise AIServiceError(f"Error generando respuesta: {str(e)}")
    
    def get_document_count(self) -> int:
        """Retorna el número total de documentos"""
        try:
            return self.rag_system.get_document_count()
        except Exception as e:
            self.logger.error(f"Error obteniendo conteo de documentos: {e}")
            raise RAGDomainException(f"Error obteniendo conteo: {str(e)}")
    
    def get_categories(self) -> List[str]:
        """Retorna todas las categorías disponibles"""
        try:
            return self.rag_system.get_categories()
        except Exception as e:
            self.logger.error(f"Error obteniendo categorías: {e}")
            raise RAGDomainException(f"Error obteniendo categorías: {str(e)}")
    
    def delete_document(self, document_id: int) -> bool:
        """Elimina un documento del sistema"""
        try:
            if document_id <= 0:
                raise InvalidQueryError("El ID del documento debe ser positivo")
            
            success = self.rag_system.delete_document(document_id)
            
            if success:
                self.logger.info(f"Documento {document_id} eliminado exitosamente")
            else:
                raise DocumentNotFoundError(f"No se pudo eliminar el documento {document_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error eliminando documento: {e}")
            if isinstance(e, (InvalidQueryError, DocumentNotFoundError, RAGDomainException)):
                raise
            raise RAGDomainException(f"Error eliminando documento: {str(e)}")

class RAGServiceFactory:
    """Factory para crear instancias del servicio RAG"""
    
    @staticmethod
    def create_rag_service(db_path: str = "hr_policies.db", 
                          model_name: str = "all-MiniLM-L6-v2") -> RAGService:
        """Crea una instancia del servicio RAG usando el factory moderno"""
        try:
            # Crear instancia del sistema RAG usando el factory moderno
            rag_system = RAGFactory.create_rag_system(
                db_path=db_path,
                embedding_model=model_name,
                use_openai=False  # Usar False para evitar problemas con API key
            )
            
            # Crear y retornar el adaptador
            return RAGServiceAdapter(rag_system)
            
        except Exception as e:
            logger.error(f"Error creando servicio RAG: {e}")
            raise RAGDomainException(f"Error inicializando servicio RAG: {str(e)}")
    
    @staticmethod
    def create_rag_service_from_config(config: Dict[str, Any]) -> RAGService:
        """Crea una instancia del servicio RAG desde configuración"""
        db_path = config.get("database_path", "hr_policies.db")
        model_name = config.get("embedding_model", "all-MiniLM-L6-v2")
        
        return RAGServiceFactory.create_rag_service(db_path, model_name)
