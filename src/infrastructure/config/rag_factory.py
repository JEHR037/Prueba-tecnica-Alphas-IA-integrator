"""
Factory para crear instancias del sistema RAG con todas sus dependencias
"""

import os
from typing import Optional, TYPE_CHECKING
import sys
from pathlib import Path

# Añadir directorios al path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Importar todas las implementaciones
from infrastructure.adapters.sqlite_document_repository import SQLiteDocumentRepository
from infrastructure.adapters.sqlite_vector_repository import SQLiteVectorRepository
from infrastructure.adapters.sentence_transformer_service import SentenceTransformerService
from infrastructure.adapters.text_processor_service import BasicTextProcessor
from application.use_cases.rag_service_impl import RAGServiceImpl
from infrastructure.config.rag_config import rag_config

if TYPE_CHECKING:
    # Solo para type checking; import perezoso en runtime
    from infrastructure.adapters.openai_client_service import OpenAIClientService  # type: ignore

class RAGFactory:
    """Factory para crear instancias del sistema RAG"""
    
    @staticmethod
    def create_rag_system(
        db_path: Optional[str] = None,
        embedding_model: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        use_openai: bool = True
    ) -> RAGServiceImpl:
        """
        Crea una instancia completa del sistema RAG
        
        Args:
            db_path: Ruta a la base de datos SQLite
            embedding_model: Modelo de embeddings a usar
            openai_api_key: Clave API de OpenAI
            use_openai: Si usar OpenAI para generación de respuestas
            
        Returns:
            Instancia configurada del sistema RAG
        """
        
        # Usar configuración por defecto si no se especifica
        db_path = db_path or rag_config.database_path
        embedding_model = embedding_model or rag_config.embedding_model
        openai_api_key = openai_api_key or rag_config.openai_api_key
        
        # Crear repositorios
        document_repo = SQLiteDocumentRepository(db_path)
        vector_repo = SQLiteVectorRepository(db_path)
        
        # Crear servicios
        embedding_service = SentenceTransformerService(embedding_model)
        text_processor = BasicTextProcessor()
        
        # Crear cliente OpenAI si se especifica (import perezoso para evitar dependencia de tiktoken)
        openai_client = None
        if use_openai and openai_api_key:
            try:
                from infrastructure.adapters.openai_client_service import OpenAIClientService  # type: ignore
                openai_client = OpenAIClientService(openai_api_key)
            except Exception as e:
                print(f"Warning: No se pudo inicializar OpenAI client: {e}")
        
        # Crear servicio RAG
        rag_service = RAGServiceImpl(
            document_repo=document_repo,
            vector_repo=vector_repo,
            embedding_service=embedding_service,
            text_processor=text_processor,
            openai_client=openai_client
        )
        
        return rag_service
    
    @staticmethod
    def create_document_repository(db_path: str) -> SQLiteDocumentRepository:
        """Crea solo el repositorio de documentos"""
        return SQLiteDocumentRepository(db_path)
    
    @staticmethod
    def create_vector_repository(db_path: str) -> SQLiteVectorRepository:
        """Crea solo el repositorio de vectores"""
        return SQLiteVectorRepository(db_path)
    
    @staticmethod
    def create_embedding_service(model_name: str = None) -> SentenceTransformerService:
        """Crea solo el servicio de embeddings"""
        model_name = model_name or rag_config.embedding_model
        return SentenceTransformerService(model_name)
    
    @staticmethod
    def create_text_processor() -> BasicTextProcessor:
        """Crea solo el procesador de texto"""
        return BasicTextProcessor()
    
    @staticmethod
    def create_openai_client(api_key: str = None, model: str = "gpt-3.5-turbo") -> "OpenAIClientService":
        """Crea solo el cliente de OpenAI"""
        api_key = api_key or rag_config.openai_api_key or os.getenv("OPENAI_API_KEY")
        return OpenAIClientService(api_key, model)

# Función de conveniencia para crear el sistema RAG
def create_google_hr_rag_system(
    db_path: str = "google_hr_policies.db",
    use_openai: bool = True
) -> RAGServiceImpl:
    """
    Función de conveniencia para crear el sistema RAG de políticas de RRHH de Google
    
    Args:
        db_path: Ruta a la base de datos
        use_openai: Si usar OpenAI para respuestas mejoradas
        
    Returns:
        Sistema RAG configurado y listo para usar
    """
    return RAGFactory.create_rag_system(
        db_path=db_path,
        use_openai=use_openai
    )
