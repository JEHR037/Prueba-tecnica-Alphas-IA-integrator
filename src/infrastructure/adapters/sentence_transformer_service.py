"""
Implementación concreta del EmbeddingService usando SentenceTransformers
"""

from typing import List
try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:
    SentenceTransformer = None  # fallback
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
        self.model_name = model_name
        self._embedding_dim = None
        if SentenceTransformer is None:
            # Fallback ligero basado en hashing si no hay modelos disponibles
            self.model = None
        else:
            try:
                self.model = SentenceTransformer(model_name)
            except Exception as e:
                # Fallback si falla la carga del modelo pesado
                self.model = None
    
    def encode_text(self, text: str) -> List[float]:
        """Convierte texto en embedding vectorial"""
        try:
            if not text or not text.strip():
                raise EmbeddingGenerationError("El texto no puede estar vacío")
            
            if self.model is not None:
                embedding = self.model.encode(text.strip())
                return embedding.tolist()
            # Fallback: embedding determinista ligero (no semántico) por hashing
            import hashlib
            h = hashlib.sha256(text.strip().encode("utf-8")).digest()
            # Mapear a vector fijo de 128 floats en [0,1)
            vec = [b / 255.0 for b in h[:128]] if len(h) >= 128 else [b / 255.0 for b in (h + b"\x00" * (128 - len(h)))]
            return vec
            
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
            
            if self.model is not None:
                embeddings = self.model.encode(valid_texts)
                return [embedding.tolist() for embedding in embeddings]
            # Fallback por hashing
            return [self.encode_text(t) for t in valid_texts]
            
        except Exception as e:
            raise EmbeddingGenerationError(f"Error generando embeddings en lote: {e}")
    
    def get_embedding_dimension(self) -> int:
        """Retorna la dimensión del embedding"""
        if self._embedding_dim is None:
            if self.model is not None:
                try:
                    test_embedding = self.model.encode("test")
                    self._embedding_dim = len(test_embedding)
                except Exception as e:
                    raise EmbeddingGenerationError(f"Error obteniendo dimensión del embedding: {e}")
            else:
                # Dimensión del fallback
                self._embedding_dim = 128
        
        return self._embedding_dim
    
    def get_model_info(self) -> dict:
        """Retorna información sobre el modelo"""
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.get_embedding_dimension(),
            "max_seq_length": getattr(self.model, 'max_seq_length', 'unknown')
        }
