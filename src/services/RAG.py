"""
Sistema RAG (Retrieval-Augmented Generation) para políticas de RRHH de Google
Utiliza SQLite con extensiones vectoriales para indexación y búsqueda semántica
Implementa las interfaces definidas en domain.py siguiendo arquitectura hexagonal
"""

import sqlite3
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
import openai
from datetime import datetime
import logging
import os
import sys
from pathlib import Path

# Añadir el directorio padre al path para importar domain
sys.path.append(str(Path(__file__).parent.parent))

# Importar entidades y puertos del dominio
from domain.entities.domain import (
    Document, DocumentChunk, SearchResult, RAGResponse,
    DocumentRepository, VectorRepository, EmbeddingService, 
    TextProcessor, OpenAIClient, RAGService, HRPolicyService,
    RAGDomainException, DocumentNotFoundError, InvalidQueryError,
    EmbeddingGenerationError, VectorSearchError, AIServiceError
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleHRPoliciesRAG:
    """
    Sistema RAG especializado en políticas de RRHH de Google
    DEPRECATED: Usar RAGFactory.create_rag_system() para nueva arquitectura
    """
    
    def __init__(self, db_path: str = "hr_policies.db", model_name: str = "all-MiniLM-L6-v2"):
        """
        Inicializa el sistema RAG (versión legacy)
        
        Args:
            db_path: Ruta a la base de datos SQLite
            model_name: Nombre del modelo de embeddings
        """
        print("WARNING: Esta clase está deprecated. Usa RAGFactory.create_rag_system() para la nueva arquitectura.")
        
        # Importar factory para crear nueva instancia
        from infrastructure.config.rag_factory import RAGFactory
        
        # Crear instancia usando nueva arquitectura
        self._rag_service = RAGFactory.create_rag_system(
            db_path=db_path,
            embedding_model=model_name,
            use_openai=True
        )
        
        # Mantener compatibilidad con API antigua
        self.db_path = db_path
        self.model = self._rag_service.embedding_service.model
        self.embedding_dim = self._rag_service.embedding_service.get_embedding_dimension()
    
    # Métodos delegados a la nueva arquitectura
    
    def add_document(self, title: str, content: str, category: str, metadata: Dict = None) -> int:
        """Añade un documento al sistema RAG (delegado a nueva arquitectura)"""
        return self._rag_service.add_document(title, content, category, metadata)
    
    def search_similar(self, query: str, top_k: int = 5, category: str = None) -> List[Dict]:
        """Busca documentos similares (delegado a nueva arquitectura)"""
        search_results = self._rag_service.search_documents(query, top_k, category)
        
        # Convertir a formato legacy
        legacy_results = []
        for result in search_results:
            legacy_results.append({
                'chunk_text': result.chunk.chunk_text,
                'document_id': result.document.id,
                'title': result.document.title,
                'category': result.document.category,
                'metadata': result.document.metadata,
                'similarity': result.relevance_score,
                'chunk_index': result.chunk.chunk_index
            })
        
        return legacy_results
    
    def generate_rag_response(self, query: str, use_openai: bool = True) -> Dict[str, Any]:
        """Genera respuesta RAG (delegado a nueva arquitectura)"""
        rag_response = self._rag_service.generate_response(query, use_openai)
        
        # Convertir a formato legacy
        return {
            "answer": rag_response.answer,
            "sources": [
                {
                    "title": result.document.title,
                    "category": result.document.category,
                    "similarity": result.relevance_score
                }
                for result in rag_response.sources
            ],
            "confidence": rag_response.confidence
        }
    
    def get_categories(self) -> List[str]:
        """Retorna categorías (delegado a nueva arquitectura)"""
        return self._rag_service.get_categories()
    
    def get_document_count(self) -> int:
        """Retorna conteo de documentos (delegado a nueva arquitectura)"""
        return self._rag_service.get_document_count()
    
    def delete_document(self, document_id: int) -> bool:
        """Elimina documento (delegado a nueva arquitectura)"""
        return self._rag_service.delete_document(document_id)


# Funciones de utilidad para usar el sistema RAG
def create_rag_system(db_path: str = "hr_policies.db") -> GoogleHRPoliciesRAG:
    """Crea una instancia del sistema RAG (legacy - usar RAGFactory para nueva arquitectura)"""
    return GoogleHRPoliciesRAG(db_path)

def query_hr_policies(rag_system: GoogleHRPoliciesRAG, question: str) -> Dict[str, Any]:
    """Función de conveniencia para hacer consultas"""
    return rag_system.generate_rag_response(question)

# Nueva función recomendada usando la arquitectura hexagonal
def create_modern_rag_system(db_path: str = "hr_policies.db", use_openai: bool = True):
    """Crea sistema RAG usando nueva arquitectura hexagonal"""
    from infrastructure.config.rag_factory import create_google_hr_rag_system
    return create_google_hr_rag_system(db_path, use_openai)


if __name__ == "__main__":
    # Ejemplo de uso
    print("Inicializando sistema RAG para políticas de RRHH de Google...")
    
    rag = create_rag_system()
    
    # Consultas de ejemplo
    questions = [
        "¿Cuál es la política de trabajo remoto de Google?",
        "¿Qué beneficios de salud ofrece Google?",
        "¿Cómo funciona el desarrollo profesional en Google?",
        "¿Cuáles son las políticas de diversidad e inclusión?",
        "¿Cuántas vacaciones puedo tomar?"
    ]
    
    print(f"\nSistema inicializado con {rag.get_document_count()} documentos")
    print(f"Categorías disponibles: {', '.join(rag.get_categories())}")
    
    print("\n" + "="*50)
    print("EJEMPLOS DE CONSULTAS")
    print("="*50)
    
    for question in questions:
        print(f"\n🔍 Pregunta: {question}")
        response = query_hr_policies(rag, question)
        print(f"📝 Respuesta: {response['answer'][:200]}...")
        print(f"📊 Confianza: {response['confidence']:.2f}")
        print(f"📚 Fuentes: {len(response['sources'])} documento(s)")
