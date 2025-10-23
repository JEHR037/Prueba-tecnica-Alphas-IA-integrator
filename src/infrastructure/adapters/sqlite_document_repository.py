"""
Implementación concreta del DocumentRepository usando SQLite
"""

import sqlite3
import json
from typing import List, Optional
from datetime import datetime
import sys
from pathlib import Path

# Añadir el directorio padre al path para importar domain
sys.path.append(str(Path(__file__).parent.parent.parent))

from domain.entities.domain import (
    Document, DocumentRepository, DocumentNotFoundError
)

class SQLiteDocumentRepository(DocumentRepository):
    """Implementación de DocumentRepository usando SQLite"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Inicializa las tablas de la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Crear índices para búsqueda eficiente
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON documents(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON documents(title)")
        
        conn.commit()
        conn.close()
    
    def save_document(self, document: Document) -> int:
        """Guarda un documento y retorna su ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if document.id is None:
                # Insertar nuevo documento
                cursor.execute("""
                    INSERT INTO documents (title, content, category, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    document.title,
                    document.content,
                    document.category,
                    json.dumps(document.metadata),
                    document.created_at
                ))
                document_id = cursor.lastrowid
            else:
                # Actualizar documento existente
                cursor.execute("""
                    UPDATE documents 
                    SET title = ?, content = ?, category = ?, metadata = ?
                    WHERE id = ?
                """, (
                    document.title,
                    document.content,
                    document.category,
                    json.dumps(document.metadata),
                    document.id
                ))
                document_id = document.id
            
            conn.commit()
            conn.close()
            
            return document_id
            
        except Exception as e:
            raise DocumentNotFoundError(f"Error guardando documento: {e}")
    
    def get_document(self, document_id: int) -> Optional[Document]:
        """Obtiene un documento por ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, title, content, category, metadata, created_at
                FROM documents WHERE id = ?
            """, (document_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return Document(
                    id=row[0],
                    title=row[1],
                    content=row[2],
                    category=row[3],
                    metadata=json.loads(row[4]) if row[4] else {},
                    created_at=datetime.fromisoformat(row[5]) if row[5] else None
                )
            
            return None
            
        except Exception as e:
            raise DocumentNotFoundError(f"Error obteniendo documento {document_id}: {e}")
    
    def get_documents_by_category(self, category: str) -> List[Document]:
        """Obtiene documentos por categoría"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, title, content, category, metadata, created_at
                FROM documents WHERE category = ?
                ORDER BY created_at DESC
            """, (category,))
            
            rows = cursor.fetchall()
            conn.close()
            
            documents = []
            for row in rows:
                documents.append(Document(
                    id=row[0],
                    title=row[1],
                    content=row[2],
                    category=row[3],
                    metadata=json.loads(row[4]) if row[4] else {},
                    created_at=datetime.fromisoformat(row[5]) if row[5] else None
                ))
            
            return documents
            
        except Exception as e:
            raise DocumentNotFoundError(f"Error obteniendo documentos por categoría {category}: {e}")
    
    def delete_document(self, document_id: int) -> bool:
        """Elimina un documento"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            deleted = cursor.rowcount > 0
            
            conn.commit()
            conn.close()
            
            return deleted
            
        except Exception as e:
            raise DocumentNotFoundError(f"Error eliminando documento {document_id}: {e}")
    
    def get_all_categories(self) -> List[str]:
        """Obtiene todas las categorías disponibles"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT category FROM documents ORDER BY category")
            rows = cursor.fetchall()
            conn.close()
            
            return [row[0] for row in rows]
            
        except Exception as e:
            raise DocumentNotFoundError(f"Error obteniendo categorías: {e}")
    
    def get_document_count(self) -> int:
        """Obtiene el número total de documentos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM documents")
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
            
        except Exception as e:
            raise DocumentNotFoundError(f"Error obteniendo conteo de documentos: {e}")
