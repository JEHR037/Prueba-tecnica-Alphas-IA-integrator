"""
Implementación concreta del EmbeddingService usando SentenceTransformers
"""

from typing import List
from sentence_transformers import SentenceTransformer
import sys
from pathlib import Path

# Añadir el directorio padre al path para importar domain
sys.path.append(str(Path(__file__).parent.parent.parent))

from domain.entities.domain import EmbeddingService, EmbeddingGenerationError

class SentenceTransformerService(EmbeddingService):
    """Implementación de EmbeddingService usando SentenceTransformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Inicializa el servicio de embeddings
        
        Args:
            model_name: Nombre del modelo de SentenceTransformers
        """
        try:
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
            self._embedding_dim = None
        except Exception as e:
            raise EmbeddingGenerationError(f"Error inicializando modelo {model_name}: {e}")
    
    def encode_text(self, text: str) -> List[float]:
        """Convierte texto en embedding vectorial"""
        try:
            if not text or not text.strip():
                raise EmbeddingGenerationError("El texto no puede estar vacío")
            
            embedding = self.model.encode(text.strip())
            return embedding.tolist()
            
        except Exception as e:
            raise EmbeddingGenerationError(f"Error generando embedding para texto: {e}")
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Convierte múltiples textos en embeddings"""
        try:
            if not texts:
                return []
            
            # Filtrar textos vacíos
            valid_texts = [text.strip() for text in texts if text and text.strip()]
            
            if not valid_texts:
                raise EmbeddingGenerationError("No hay textos válidos para procesar")
            
            embeddings = self.model.encode(valid_texts)
            return [embedding.tolist() for embedding in embeddings]
            
        except Exception as e:
            raise EmbeddingGenerationError(f"Error generando embeddings en lote: {e}")
    
    def get_embedding_dimension(self) -> int:
        """Retorna la dimensión del embedding"""
        if self._embedding_dim is None:
            try:
                # Generar un embedding de prueba para obtener la dimensión
                test_embedding = self.model.encode("test")
                self._embedding_dim = len(test_embedding)
            except Exception as e:
                raise EmbeddingGenerationError(f"Error obteniendo dimensión del embedding: {e}")
        
        return self._embedding_dim
    
    def get_model_info(self) -> dict:
        """Retorna información sobre el modelo"""
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.get_embedding_dimension(),
            "max_seq_length": getattr(self.model, 'max_seq_length', 'unknown')
        }
