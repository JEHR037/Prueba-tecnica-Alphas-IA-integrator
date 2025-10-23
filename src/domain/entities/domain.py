from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# ============================================================================
# ENTIDADES DE DOMINIO PARA SISTEMA RAG
# ============================================================================

@dataclass
class Document:
    """Entidad que representa un documento en el sistema RAG"""
    id: Optional[int] = None
    title: str = ""
    content: str = ""
    category: str = ""
    metadata: Dict[str, Any] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class DocumentChunk:
    """Entidad que representa un fragmento de documento con su embedding"""
    id: Optional[int] = None
    document_id: int = 0
    chunk_text: str = ""
    embedding: Optional[List[float]] = None
    chunk_index: int = 0
    similarity_score: float = 0.0

@dataclass
class SearchResult:
    """Entidad que representa el resultado de una búsqueda"""
    document: Document
    chunk: DocumentChunk
    relevance_score: float
    
@dataclass
class RAGResponse:
    """Entidad que representa la respuesta del sistema RAG"""
    answer: str
    sources: List[SearchResult]
    confidence: float
    query: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

# ============================================================================
# INTERFACES/PUERTOS PARA SISTEMA RAG
# ============================================================================

class DocumentRepository(ABC):
    """Puerto para repositorio de documentos"""
    
    @abstractmethod
    def save_document(self, document: Document) -> int:
        """Guarda un documento y retorna su ID"""
        pass
    
    @abstractmethod
    def get_document(self, document_id: int) -> Optional[Document]:
        """Obtiene un documento por ID"""
        pass
    
    @abstractmethod
    def get_documents_by_category(self, category: str) -> List[Document]:
        """Obtiene documentos por categoría"""
        pass
    
    @abstractmethod
    def delete_document(self, document_id: int) -> bool:
        """Elimina un documento"""
        pass
    
    @abstractmethod
    def get_all_categories(self) -> List[str]:
        """Obtiene todas las categorías disponibles"""
        pass

class VectorRepository(ABC):
    """Puerto para repositorio de vectores/embeddings"""
    
    @abstractmethod
    def save_embedding(self, chunk: DocumentChunk) -> int:
        """Guarda un embedding y retorna su ID"""
        pass
    
    @abstractmethod
    def search_similar(self, query_embedding: List[float], top_k: int = 5, 
                      category: Optional[str] = None) -> List[DocumentChunk]:
        """Busca chunks similares usando embeddings"""
        pass
    
    @abstractmethod
    def delete_embeddings_by_document(self, document_id: int) -> bool:
        """Elimina todos los embeddings de un documento"""
        pass

class EmbeddingService(ABC):
    """Puerto para servicio de embeddings"""
    
    @abstractmethod
    def encode_text(self, text: str) -> List[float]:
        """Convierte texto en embedding vectorial"""
        pass
    
    @abstractmethod
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Convierte múltiples textos en embeddings"""
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Retorna la dimensión del embedding"""
        pass

class TextProcessor(ABC):
    """Puerto para procesamiento de texto"""
    
    @abstractmethod
    def split_text(self, text: str, chunk_size: int = 500, 
                  overlap: int = 50) -> List[str]:
        """Divide texto en chunks con overlap"""
        pass
    
    @abstractmethod
    def clean_text(self, text: str) -> str:
        """Limpia y normaliza texto"""
        pass
    
    @abstractmethod
    def extract_keywords(self, text: str) -> List[str]:
        """Extrae palabras clave del texto"""
        pass

class OpenAIClient(ABC):
    """Puerto para cliente de OpenAI"""
    
    @abstractmethod
    def get_chat_completion(self, messages: List[dict]) -> dict:
        """Envía mensajes a OpenAI API y retorna respuesta"""
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Calcula tokens aproximados para un texto"""
        pass
    
    @abstractmethod
    def generate_rag_response(self, query: str, context: str) -> str:
        """Genera respuesta RAG usando el contexto proporcionado"""
        pass

# ============================================================================
# SERVICIOS DE DOMINIO
# ============================================================================

class RAGService(ABC):
    """Servicio principal del sistema RAG"""
    
    @abstractmethod
    def add_document(self, title: str, content: str, category: str, 
                    metadata: Dict[str, Any] = None) -> int:
        """Añade un documento al sistema RAG"""
        pass
    
    @abstractmethod
    def search_documents(self, query: str, top_k: int = 5, 
                        category: Optional[str] = None) -> List[SearchResult]:
        """Busca documentos relevantes para una consulta"""
        pass
    
    @abstractmethod
    def generate_response(self, query: str, use_ai: bool = True) -> RAGResponse:
        """Genera una respuesta completa usando RAG"""
        pass
    
    @abstractmethod
    def get_document_count(self) -> int:
        """Retorna el número total de documentos"""
        pass
    
    @abstractmethod
    def get_categories(self) -> List[str]:
        """Retorna todas las categorías disponibles"""
        pass
    
    @abstractmethod
    def delete_document(self, document_id: int) -> bool:
        """Elimina un documento del sistema"""
        pass

class HRPolicyService(ABC):
    """Servicio especializado para políticas de RRHH"""
    
    @abstractmethod
    def load_predefined_policies(self) -> int:
        """Carga políticas predefinidas de RRHH"""
        pass
    
    @abstractmethod
    def query_policy(self, question: str) -> RAGResponse:
        """Consulta específica sobre políticas de RRHH"""
        pass
    
    @abstractmethod
    def get_policy_categories(self) -> List[str]:
        """Obtiene categorías específicas de políticas de RRHH"""
        pass
    
    @abstractmethod
    def validate_policy_query(self, query: str) -> bool:
        """Valida si una consulta es apropiada para políticas de RRHH"""
        pass

# ============================================================================
# CASOS DE USO (INTERFACES)
# ============================================================================

class AddDocumentUseCase(ABC):
    """Caso de uso para añadir documentos"""
    
    @abstractmethod
    def execute(self, title: str, content: str, category: str, 
               metadata: Dict[str, Any] = None) -> int:
        pass

class SearchDocumentsUseCase(ABC):
    """Caso de uso para buscar documentos"""
    
    @abstractmethod
    def execute(self, query: str, top_k: int = 5, 
               category: Optional[str] = None) -> List[SearchResult]:
        pass

class GenerateResponseUseCase(ABC):
    """Caso de uso para generar respuestas RAG"""
    
    @abstractmethod
    def execute(self, query: str, use_ai: bool = True) -> RAGResponse:
        pass

class QueryHRPolicyUseCase(ABC):
    """Caso de uso específico para consultas de políticas de RRHH"""
    
    @abstractmethod
    def execute(self, question: str) -> RAGResponse:
        pass

# ============================================================================
# EXCEPCIONES DE DOMINIO
# ============================================================================

class RAGDomainException(Exception):
    """Excepción base del dominio RAG"""
    pass

class DocumentNotFoundError(RAGDomainException):
    """Error cuando no se encuentra un documento"""
    pass

class InvalidQueryError(RAGDomainException):
    """Error cuando la consulta es inválida"""
    pass

class EmbeddingGenerationError(RAGDomainException):
    """Error al generar embeddings"""
    pass

class VectorSearchError(RAGDomainException):
    """Error en búsqueda vectorial"""
    pass

class AIServiceError(RAGDomainException):
    """Error en servicio de IA"""
    pass