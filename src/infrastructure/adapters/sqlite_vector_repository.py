"""
Implementación concreta del VectorRepository usando SQLite
"""

import sqlite3
import numpy as np
from typing import List, Optional
import sys
from pathlib import Path

# Añadir el directorio padre al path para importar domain
sys.path.append(str(Path(__file__).parent.parent.parent))

from domain.entities.domain import (
    DocumentChunk, VectorRepository, VectorSearchError
)

class SQLiteVectorRepository(VectorRepository):
    """Implementación de VectorRepository usando SQLite"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Inicializa las tablas de embeddings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                chunk_text TEXT NOT NULL,
                embedding BLOB NOT NULL,
                chunk_index INTEGER,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        """)
        
        # Crear índices para búsqueda eficiente
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_document_id ON embeddings(document_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunk_index ON embeddings(chunk_index)")
        
        conn.commit()
        conn.close()
    
    def save_embedding(self, chunk: DocumentChunk) -> int:
        """Guarda un embedding y retorna su ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convertir embedding a bytes
            embedding_blob = np.array(chunk.embedding, dtype=np.float32).tobytes()
            
            if chunk.id is None:
                # Insertar nuevo embedding
                cursor.execute("""
                    INSERT INTO embeddings (document_id, chunk_text, embedding, chunk_index)
                    VALUES (?, ?, ?, ?)
                """, (
                    chunk.document_id,
                    chunk.chunk_text,
                    embedding_blob,
                    chunk.chunk_index
                ))
                embedding_id = cursor.lastrowid
            else:
                # Actualizar embedding existente
                cursor.execute("""
                    UPDATE embeddings 
                    SET document_id = ?, chunk_text = ?, embedding = ?, chunk_index = ?
                    WHERE id = ?
                """, (
                    chunk.document_id,
                    chunk.chunk_text,
                    embedding_blob,
                    chunk.chunk_index,
                    chunk.id
                ))
                embedding_id = chunk.id
            
            conn.commit()
            conn.close()
            
            return embedding_id
            
        except Exception as e:
            raise VectorSearchError(f"Error guardando embedding: {e}")
    
    def search_similar(self, query_embedding: List[float], top_k: int = 5, 
                      category: Optional[str] = None) -> List[DocumentChunk]:
        """Busca chunks similares usando embeddings"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Construir consulta SQL
            if category:
                sql_query = """
                    SELECT e.id, e.document_id, e.chunk_text, e.embedding, e.chunk_index
                    FROM embeddings e
                    JOIN documents d ON e.document_id = d.id
                    WHERE d.category = ?
                """
                params = [category]
            else:
                sql_query = """
                    SELECT id, document_id, chunk_text, embedding, chunk_index
                    FROM embeddings
                """
                params = []
            
            cursor.execute(sql_query, params)
            results = cursor.fetchall()
            conn.close()
            
            # Calcular similitudes
            query_vector = np.array(query_embedding, dtype=np.float32)
            similarities = []
            
            for row in results:
                embedding_id, doc_id, chunk_text, embedding_blob, chunk_idx = row
                
                # Convertir embedding de bytes a numpy array
                stored_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                
                # Calcular similitud coseno
                similarity = np.dot(query_vector, stored_embedding) / (
                    np.linalg.norm(query_vector) * np.linalg.norm(stored_embedding)
                )
                
                chunk = DocumentChunk(
                    id=embedding_id,
                    document_id=doc_id,
                    chunk_text=chunk_text,
                    embedding=stored_embedding.tolist(),
                    chunk_index=chunk_idx,
                    similarity_score=float(similarity)
                )
                
                similarities.append(chunk)
            
            # Ordenar por similitud y retornar top_k
            similarities.sort(key=lambda x: x.similarity_score, reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            raise VectorSearchError(f"Error en búsqueda vectorial: {e}")
    
    def delete_embeddings_by_document(self, document_id: int) -> bool:
        """Elimina todos los embeddings de un documento"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM embeddings WHERE document_id = ?", (document_id,))
            deleted = cursor.rowcount > 0
            
            conn.commit()
            conn.close()
            
            return deleted
            
        except Exception as e:
            raise VectorSearchError(f"Error eliminando embeddings del documento {document_id}: {e}")
    
    def get_embeddings_by_document(self, document_id: int) -> List[DocumentChunk]:
        """Obtiene todos los embeddings de un documento"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, document_id, chunk_text, embedding, chunk_index
                FROM embeddings 
                WHERE document_id = ?
                ORDER BY chunk_index
            """, (document_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            chunks = []
            for row in results:
                embedding_id, doc_id, chunk_text, embedding_blob, chunk_idx = row
                stored_embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                
                chunk = DocumentChunk(
                    id=embedding_id,
                    document_id=doc_id,
                    chunk_text=chunk_text,
                    embedding=stored_embedding.tolist(),
                    chunk_index=chunk_idx
                )
                chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            raise VectorSearchError(f"Error obteniendo embeddings del documento {document_id}: {e}")
