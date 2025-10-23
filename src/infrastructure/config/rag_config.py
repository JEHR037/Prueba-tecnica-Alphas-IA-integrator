"""
Configuración para el sistema RAG de políticas de RRHH de Google
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings

class RAGConfig(BaseSettings):
    """Configuración del sistema RAG"""
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    
    # Database Configuration
    database_path: str = "hr_policies.db"
    
    # Embedding Model Configuration
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # Text Processing Configuration
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # Search Configuration
    default_top_k: int = 5
    similarity_threshold: float = 0.3
    
    # Logging Configuration
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instancia global de configuración
rag_config = RAGConfig()
