"""
Servicio RAG integrado que combina el sistema RAG con datos precargados
Proporciona una interfaz unificada para el sistema completo
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
from pathlib import Path

# Añadir el directorio src al path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Importar servicios y entidades
from infrastructure.config.rag_factory import RAGFactory
from infrastructure.services.data_loader_service import DataLoaderService, AutoDataLoader
from infrastructure.adapters.rag_service_adapter import RAGServiceAdapter
from application.use_cases.rag_service_impl import RAGServiceImpl

from domain.entities.domain import (
    RAGService, Document, SearchResult, RAGResponse,
    RAGDomainException, InvalidQueryError, AIServiceError
)

logger = logging.getLogger(__name__)

class IntegratedRAGService:
    """Servicio RAG integrado con datos precargados y funcionalidades avanzadas"""
    
    def __init__(self, db_path: str = "integrated_hr_policies.db", 
                 embedding_model: str = "all-MiniLM-L6-v2",
                 auto_load_data: bool = True):
        """
        Inicializa el servicio RAG integrado
        
        Args:
            db_path: Ruta a la base de datos
            embedding_model: Modelo de embeddings
            auto_load_data: Si cargar automáticamente los datos precargados
        """
        self.db_path = db_path
        self.embedding_model = embedding_model
        self.auto_load_data = auto_load_data
        
        # Servicios internos
        self._rag_service: Optional[RAGServiceImpl] = None
        self._data_loader: Optional[DataLoaderService] = None
        self._initialized = False
        
        # Estadísticas
        self.stats = {
            "initialization_time": None,
            "documents_loaded": 0,
            "queries_processed": 0,
            "last_query_time": None,
            "system_ready": False
        }
        
        logger.info(f"🔥 Creando servicio RAG integrado con DB: {db_path}")
    
    async def initialize(self) -> Dict[str, Any]:
        """Inicializa el servicio RAG completo con datos precargados"""
        if self._initialized:
            return {"status": "already_initialized", "stats": self.stats}
        
        start_time = datetime.now()
        logger.info("🚀 Inicializando servicio RAG integrado...")
        
        try:
            # 1. Crear el servicio RAG base
            logger.info("📦 Creando servicio RAG base...")
            self._rag_service = RAGFactory.create_rag_system(
                db_path=self.db_path,
                embedding_model=self.embedding_model,
                use_openai=False  # Deshabilitado por ahora para evitar problemas de API key
            )
            
            # 2. Crear adaptador para compatibilidad
            rag_adapter = RAGServiceAdapter(self._rag_service)
            
            # 3. Cargar datos precargados si está habilitado
            if self.auto_load_data:
                logger.info("📋 Cargando datos precargados...")
                self._data_loader = await AutoDataLoader.initialize_system(
                    rag_adapter, 
                    auto_load=True
                )
                
                # Obtener estadísticas de carga
                load_stats = self._data_loader.get_load_statistics()
                self.stats["documents_loaded"] = load_stats["loaded_documents_count"]
            
            # 4. Actualizar estadísticas
            end_time = datetime.now()
            self.stats["initialization_time"] = (end_time - start_time).total_seconds()
            self.stats["system_ready"] = True
            self._initialized = True
            
            logger.info(f"✅ Servicio RAG integrado inicializado en {self.stats['initialization_time']:.2f}s")
            logger.info(f"📊 Documentos cargados: {self.stats['documents_loaded']}")
            
            return {
                "status": "initialized",
                "initialization_time": self.stats["initialization_time"],
                "documents_loaded": self.stats["documents_loaded"],
                "system_ready": True
            }
            
        except Exception as e:
            logger.error(f"❌ Error inicializando servicio RAG integrado: {e}")
            self.stats["system_ready"] = False
            raise RAGDomainException(f"Error inicializando servicio integrado: {e}")
    
    async def ask_question(self, question: str, department: Optional[str] = None,
                          top_k: int = 5, use_ai: bool = True) -> RAGResponse:
        """
        Hace una pregunta al sistema RAG integrado
        
        Args:
            question: Pregunta del usuario
            department: Departamento para filtrar (opcional)
            top_k: Número de documentos a recuperar
            use_ai: Si usar IA para generar respuesta
            
        Returns:
            Respuesta RAG completa
        """
        # Asegurar que el sistema esté inicializado
        if not self._initialized:
            await self.initialize()
        
        if not self._rag_service:
            raise RAGDomainException("Servicio RAG no inicializado")
        
        try:
            start_time = datetime.now()
            logger.info(f"🔍 Procesando pregunta: '{question}' (dept: {department})")
            
            # Validar entrada
            if not question or not question.strip():
                raise InvalidQueryError("La pregunta no puede estar vacía")
            
            # Buscar documentos relevantes
            search_results = self._rag_service.search_documents(
                query=question.strip(),
                top_k=top_k,
                category=None  # Por ahora no filtrar por categoría
            )
            
            # Generar respuesta
            if search_results and use_ai:
                # Construir contexto desde los resultados
                context_parts = []
                for result in search_results[:3]:  # Usar top 3 resultados
                    context_parts.append(f"Documento: {result.document.title}")
                    context_parts.append(f"Contenido: {result.chunk.chunk_text}")
                    context_parts.append("---")
                
                context = "\n".join(context_parts)
                
                # Generar respuesta usando el mock de OpenAI
                from domain.entities.api_mock import OpenAIMockFactory
                mock_client = OpenAIMockFactory.create_fast_mock()
                
                try:
                    answer = mock_client.generate_rag_response(question, context)
                except Exception as e:
                    logger.warning(f"Error con mock OpenAI: {e}, usando respuesta básica")
                    answer = self._generate_basic_response(question, search_results)
            else:
                answer = self._generate_basic_response(question, search_results)
            
            # Crear respuesta RAG
            response = RAGResponse(
                answer=answer,
                sources=search_results,
                confidence=0.8 if search_results else 0.2,
                query=question,
                timestamp=datetime.now()
            )
            
            # Actualizar estadísticas
            self.stats["queries_processed"] += 1
            self.stats["last_query_time"] = datetime.now()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Pregunta procesada en {processing_time:.2f}s, confianza: {response.confidence:.2f}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error procesando pregunta: {e}")
            raise RAGDomainException(f"Error procesando pregunta: {e}")
    
    def _generate_basic_response(self, question: str, search_results: List[SearchResult]) -> str:
        """Genera una respuesta básica sin IA"""
        if not search_results:
            return f"No encontré información específica sobre '{question}' en las políticas disponibles. Puedes intentar reformular tu pregunta o contactar con RRHH para más detalles."
        
        # Construir respuesta básica
        response_parts = [
            f"Basándome en las políticas disponibles, encontré {len(search_results)} documentos relevantes sobre '{question}':"
        ]
        
        for i, result in enumerate(search_results[:3], 1):
            response_parts.append(f"\n{i}. **{result.document.title}**")
            # Tomar las primeras 200 caracteres del contenido
            content_preview = result.chunk.chunk_text[:200]
            if len(result.chunk.chunk_text) > 200:
                content_preview += "..."
            response_parts.append(f"   {content_preview}")
        
        response_parts.append("\nPara información más detallada, consulta los documentos específicos o contacta con el departamento correspondiente.")
        
        return "\n".join(response_parts)
    
    def add_document(self, title: str, content: str, category: str, 
                    metadata: Dict[str, Any] = None) -> int:
        """Añade un documento al sistema"""
        if not self._rag_service:
            raise RAGDomainException("Servicio RAG no inicializado")
        
        try:
            document_id = self._rag_service.add_document(title, content, category, metadata)
            self.stats["documents_loaded"] += 1
            logger.info(f"📄 Documento añadido: {title} (ID: {document_id})")
            return document_id
        except Exception as e:
            logger.error(f"❌ Error añadiendo documento: {e}")
            raise RAGDomainException(f"Error añadiendo documento: {e}")
    
    def search_documents(self, query: str, top_k: int = 5, 
                        category: Optional[str] = None) -> List[SearchResult]:
        """Busca documentos en el sistema"""
        if not self._rag_service:
            raise RAGDomainException("Servicio RAG no inicializado")
        
        try:
            return self._rag_service.search_documents(query, top_k, category)
        except Exception as e:
            logger.error(f"❌ Error buscando documentos: {e}")
            raise RAGDomainException(f"Error buscando documentos: {e}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Obtiene información del sistema"""
        return {
            "initialized": self._initialized,
            "system_ready": self.stats["system_ready"],
            "database_path": self.db_path,
            "embedding_model": self.embedding_model,
            "auto_load_data": self.auto_load_data,
            "statistics": self.stats,
            "data_loader_available": self._data_loader is not None
        }
    
    def get_document_count(self) -> int:
        """Obtiene el número total de documentos"""
        if not self._rag_service:
            return 0
        try:
            return self._rag_service.get_document_count()
        except:
            return 0
    
    def get_categories(self) -> List[str]:
        """Obtiene las categorías disponibles"""
        if not self._rag_service:
            return []
        try:
            return self._rag_service.get_categories()
        except:
            return []
    
    async def reload_preloaded_data(self) -> Dict[str, Any]:
        """Recarga los datos precargados"""
        if not self._data_loader:
            return {"status": "no_data_loader", "message": "Data loader no disponible"}
        
        try:
            logger.info("🔄 Recargando datos precargados...")
            result = await self._data_loader.load_all_preloaded_data(force_reload=True)
            
            # Actualizar estadísticas
            load_stats = self._data_loader.get_load_statistics()
            self.stats["documents_loaded"] = load_stats["loaded_documents_count"]
            
            return result
        except Exception as e:
            logger.error(f"❌ Error recargando datos: {e}")
            raise RAGDomainException(f"Error recargando datos: {e}")

class IntegratedRAGServiceFactory:
    """Factory para crear el servicio RAG integrado"""
    
    @staticmethod
    async def create_service(db_path: str = "integrated_hr_policies.db",
                           embedding_model: str = "all-MiniLM-L6-v2",
                           auto_initialize: bool = True) -> IntegratedRAGService:
        """
        Crea y opcionalmente inicializa el servicio RAG integrado
        
        Args:
            db_path: Ruta a la base de datos
            embedding_model: Modelo de embeddings
            auto_initialize: Si inicializar automáticamente
            
        Returns:
            Servicio RAG integrado
        """
        service = IntegratedRAGService(
            db_path=db_path,
            embedding_model=embedding_model,
            auto_load_data=True
        )
        
        if auto_initialize:
            await service.initialize()
        
        return service
    
    @staticmethod
    def create_service_sync(db_path: str = "integrated_hr_policies.db",
                          embedding_model: str = "all-MiniLM-L6-v2") -> IntegratedRAGService:
        """
        Crea el servicio RAG integrado sin inicializar (versión síncrona)
        
        Args:
            db_path: Ruta a la base de datos
            embedding_model: Modelo de embeddings
            
        Returns:
            Servicio RAG integrado (no inicializado)
        """
        return IntegratedRAGService(
            db_path=db_path,
            embedding_model=embedding_model,
            auto_load_data=True
        )

# Instancia global para uso en endpoints
_global_integrated_service: Optional[IntegratedRAGService] = None

async def get_global_integrated_service() -> IntegratedRAGService:
    """Obtiene la instancia global del servicio integrado"""
    global _global_integrated_service
    
    if _global_integrated_service is None:
        logger.info("🔄 Creando instancia global del servicio RAG integrado...")
        _global_integrated_service = await IntegratedRAGServiceFactory.create_service(
            auto_initialize=True
        )
    elif not _global_integrated_service._initialized:
        logger.info("🔄 Inicializando servicio RAG integrado existente...")
        await _global_integrated_service.initialize()
    
    return _global_integrated_service

if __name__ == "__main__":
    # Ejemplo de uso
    async def demo():
        print("🔥 Demo del Servicio RAG Integrado 🔥")
        
        # Crear servicio
        service = await IntegratedRAGServiceFactory.create_service()
        
        # Hacer algunas preguntas
        questions = [
            "¿Cuáles son los beneficios de salud?",
            "¿Cómo funciona el trabajo remoto?",
            "¿Qué presupuesto tengo para capacitación?"
        ]
        
        for question in questions:
            print(f"\n❓ {question}")
            response = await service.ask_question(question)
            print(f"✅ {response.answer[:200]}...")
        
        # Mostrar estadísticas
        info = service.get_system_info()
        print(f"\n📊 Estadísticas:")
        print(f"  - Documentos: {info['statistics']['documents_loaded']}")
        print(f"  - Consultas: {info['statistics']['queries_processed']}")
        print(f"  - Sistema listo: {info['system_ready']}")
    
    # Ejecutar demo
    asyncio.run(demo())
