"""
Servicio de carga automática de datos precargados para el sistema RAG
Inicializa el sistema con políticas de RRHH por defecto
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
from pathlib import Path

# Añadir el directorio src al path
sys.path.append(str(Path(__file__).parent.parent.parent))

from infrastructure.data.preloaded_hr_policies import (
    get_all_preloaded_policies,
    get_policies_by_category,
    get_faq_data,
    get_policy_categories,
    get_policy_departments
)

from domain.entities.domain import (
    Document, RAGService, RAGDomainException
)

logger = logging.getLogger(__name__)

class DataLoaderService:
    """Servicio para cargar datos precargados al sistema RAG"""
    
    def __init__(self, rag_service: RAGService):
        """
        Inicializa el servicio de carga de datos
        
        Args:
            rag_service: Servicio RAG donde cargar los datos
        """
        self.rag_service = rag_service
        self.loaded_documents = []
        self.load_stats = {
            "total_loaded": 0,
            "successful": 0,
            "failed": 0,
            "categories": {},
            "load_time": None,
            "last_load": None
        }
    
    async def load_all_preloaded_data(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        Carga todos los datos precargados al sistema RAG
        
        Args:
            force_reload: Si forzar recarga aunque ya existan datos
            
        Returns:
            Estadísticas de la carga
        """
        start_time = datetime.now()
        logger.info("🔥 Iniciando carga de datos precargados ALPHAS RAG...")
        
        try:
            # Verificar si ya hay datos cargados
            if not force_reload and await self._check_existing_data():
                logger.info("✅ Datos precargados ya existen, saltando carga")
                return self._get_load_summary()
            
            # Cargar políticas de RRHH
            await self._load_hr_policies()
            
            # Cargar preguntas frecuentes como documentos adicionales
            await self._load_faq_data()
            
            # Actualizar estadísticas
            end_time = datetime.now()
            self.load_stats["load_time"] = (end_time - start_time).total_seconds()
            self.load_stats["last_load"] = end_time
            
            logger.info(f"✅ Carga completada: {self.load_stats['successful']} documentos cargados en {self.load_stats['load_time']:.2f}s")
            
            return self._get_load_summary()
            
        except Exception as e:
            logger.error(f"❌ Error durante la carga de datos: {e}")
            raise RAGDomainException(f"Error cargando datos precargados: {e}")
    
    async def _check_existing_data(self) -> bool:
        """Verifica si ya existen datos precargados en el sistema"""
        try:
            total_docs = self.rag_service.get_document_count()
            return total_docs > 0
        except Exception:
            return False
    
    async def _load_hr_policies(self) -> None:
        """Carga las políticas de RRHH precargadas"""
        logger.info("📋 Cargando políticas de RRHH...")
        
        policies = get_all_preloaded_policies()
        
        for policy in policies:
            try:
                # Crear documento desde política
                document_id = self.rag_service.add_document(
                    title=policy["title"],
                    content=policy["content"],
                    category=policy["category"],
                    metadata={
                        **policy.get("metadata", {}),
                        "department": policy.get("department"),
                        "source_type": "preloaded_policy",
                        "load_timestamp": datetime.now().isoformat()
                    }
                )
                
                self.loaded_documents.append({
                    "id": document_id,
                    "title": policy["title"],
                    "category": policy["category"],
                    "type": "policy"
                })
                
                # Actualizar estadísticas
                self.load_stats["successful"] += 1
                category = policy["category"]
                if category not in self.load_stats["categories"]:
                    self.load_stats["categories"][category] = 0
                self.load_stats["categories"][category] += 1
                
                logger.debug(f"✅ Cargada política: {policy['title']}")
                
            except Exception as e:
                logger.error(f"❌ Error cargando política {policy['title']}: {e}")
                self.load_stats["failed"] += 1
        
        self.load_stats["total_loaded"] = len(policies)
        logger.info(f"📋 Políticas de RRHH cargadas: {self.load_stats['successful']}/{len(policies)}")
    
    async def _load_faq_data(self) -> None:
        """Carga las preguntas frecuentes como documentos adicionales"""
        logger.info("❓ Cargando preguntas frecuentes...")
        
        faq_data = get_faq_data()
        
        for faq in faq_data:
            try:
                # Crear documento FAQ
                faq_content = f"""
PREGUNTA FRECUENTE: {faq['question']}

RESPUESTA: {faq['answer']}

PALABRAS CLAVE: {', '.join(faq['keywords'])}

Esta es una pregunta frecuente sobre {faq['category']} que los empleados suelen hacer.
Para más información detallada, consulta las políticas específicas de esta categoría.
                """.strip()
                
                document_id = self.rag_service.add_document(
                    title=f"FAQ: {faq['question']}",
                    content=faq_content,
                    category=faq["category"],
                    metadata={
                        "source_type": "faq",
                        "keywords": faq["keywords"],
                        "original_question": faq["question"],
                        "load_timestamp": datetime.now().isoformat()
                    }
                )
                
                self.loaded_documents.append({
                    "id": document_id,
                    "title": f"FAQ: {faq['question']}",
                    "category": faq["category"],
                    "type": "faq"
                })
                
                self.load_stats["successful"] += 1
                
                logger.debug(f"✅ Cargada FAQ: {faq['question']}")
                
            except Exception as e:
                logger.error(f"❌ Error cargando FAQ {faq['question']}: {e}")
                self.load_stats["failed"] += 1
        
        logger.info(f"❓ FAQs cargadas: {len(faq_data)} preguntas frecuentes")
    
    def _get_load_summary(self) -> Dict[str, Any]:
        """Genera resumen de la carga de datos"""
        return {
            "status": "completed",
            "summary": {
                "total_documents": len(self.loaded_documents),
                "successful_loads": self.load_stats["successful"],
                "failed_loads": self.load_stats["failed"],
                "categories_loaded": list(self.load_stats["categories"].keys()),
                "load_time_seconds": self.load_stats["load_time"],
                "last_load": self.load_stats["last_load"].isoformat() if self.load_stats["last_load"] else None
            },
            "categories": self.load_stats["categories"],
            "loaded_documents": self.loaded_documents[:10],  # Primeros 10 para preview
            "available_categories": get_policy_categories(),
            "available_departments": get_policy_departments()
        }
    
    async def reload_category(self, category: str) -> Dict[str, Any]:
        """
        Recarga documentos de una categoría específica
        
        Args:
            category: Categoría a recargar
            
        Returns:
            Estadísticas de la recarga
        """
        logger.info(f"🔄 Recargando categoría: {category}")
        
        try:
            # Obtener políticas de la categoría
            policies = get_policies_by_category(category)
            
            if not policies:
                return {
                    "status": "no_data",
                    "message": f"No hay políticas precargadas para la categoría: {category}"
                }
            
            loaded_count = 0
            failed_count = 0
            
            for policy in policies:
                try:
                    document_id = self.rag_service.add_document(
                        title=f"[RELOAD] {policy['title']}",
                        content=policy["content"],
                        category=policy["category"],
                        metadata={
                            **policy.get("metadata", {}),
                            "department": policy.get("department"),
                            "source_type": "reloaded_policy",
                            "reload_timestamp": datetime.now().isoformat()
                        }
                    )
                    loaded_count += 1
                    logger.debug(f"✅ Recargada: {policy['title']}")
                    
                except Exception as e:
                    logger.error(f"❌ Error recargando {policy['title']}: {e}")
                    failed_count += 1
            
            return {
                "status": "completed",
                "category": category,
                "loaded": loaded_count,
                "failed": failed_count,
                "total_policies": len(policies)
            }
            
        except Exception as e:
            logger.error(f"❌ Error recargando categoría {category}: {e}")
            raise RAGDomainException(f"Error recargando categoría {category}: {e}")
    
    def get_load_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de carga actuales"""
        return {
            "load_stats": self.load_stats,
            "loaded_documents_count": len(self.loaded_documents),
            "available_categories": get_policy_categories(),
            "available_departments": get_policy_departments(),
            "system_ready": self.load_stats["successful"] > 0
        }
    
    async def validate_loaded_data(self) -> Dict[str, Any]:
        """Valida que los datos cargados sean accesibles"""
        logger.info("🔍 Validando datos cargados...")
        
        validation_results = {
            "total_documents": 0,
            "categories_found": [],
            "sample_searches": [],
            "validation_errors": []
        }
        
        try:
            # Verificar total de documentos
            validation_results["total_documents"] = self.rag_service.get_document_count()
            
            # Verificar categorías
            validation_results["categories_found"] = self.rag_service.get_categories()
            
            # Hacer búsquedas de prueba
            test_queries = [
                "beneficios de salud",
                "política de vacaciones", 
                "trabajo remoto",
                "desarrollo profesional"
            ]
            
            for query in test_queries:
                try:
                    results = self.rag_service.search_documents(query, top_k=3)
                    validation_results["sample_searches"].append({
                        "query": query,
                        "results_found": len(results),
                        "top_result": results[0].document.title if results else None
                    })
                except Exception as e:
                    validation_results["validation_errors"].append(f"Error buscando '{query}': {e}")
            
            logger.info(f"✅ Validación completada: {validation_results['total_documents']} documentos disponibles")
            
        except Exception as e:
            validation_results["validation_errors"].append(f"Error general de validación: {e}")
            logger.error(f"❌ Error en validación: {e}")
        
        return validation_results

class AutoDataLoader:
    """Cargador automático de datos que se ejecuta al inicio del sistema"""
    
    @staticmethod
    async def initialize_system(rag_service: RAGService, auto_load: bool = True) -> DataLoaderService:
        """
        Inicializa el sistema con datos precargados
        
        Args:
            rag_service: Servicio RAG a inicializar
            auto_load: Si cargar automáticamente los datos
            
        Returns:
            Instancia del DataLoaderService
        """
        loader = DataLoaderService(rag_service)
        
        if auto_load:
            logger.info("🚀 Inicializando sistema RAG con datos precargados...")
            await loader.load_all_preloaded_data()
            
            # Validar que los datos se cargaron correctamente
            validation = await loader.validate_loaded_data()
            
            if validation["validation_errors"]:
                logger.warning(f"⚠️ Errores de validación encontrados: {validation['validation_errors']}")
            else:
                logger.info("✅ Sistema RAG inicializado correctamente con datos precargados")
        
        return loader

# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Este código se ejecutaría al inicializar el sistema
    async def demo_data_loading():
        """Demostración de carga de datos"""
        
        # Simular servicio RAG (en implementación real, usar el servicio real)
        class MockRAGService:
            def __init__(self):
                self.documents = []
                self.doc_counter = 0
            
            def add_document(self, title, content, category, metadata=None):
                self.doc_counter += 1
                doc = {
                    "id": self.doc_counter,
                    "title": title,
                    "content": content,
                    "category": category,
                    "metadata": metadata or {}
                }
                self.documents.append(doc)
                return self.doc_counter
            
            def get_document_count(self):
                return len(self.documents)
            
            def get_categories(self):
                return list(set(doc["category"] for doc in self.documents))
            
            def search_documents(self, query, top_k=5):
                # Búsqueda simulada
                return []
        
        # Crear servicio mock y cargar datos
        mock_rag = MockRAGService()
        loader = await AutoDataLoader.initialize_system(mock_rag, auto_load=True)
        
        # Mostrar estadísticas
        stats = loader.get_load_statistics()
        print("📊 Estadísticas de carga:")
        print(f"  - Documentos cargados: {stats['loaded_documents_count']}")
        print(f"  - Categorías disponibles: {stats['available_categories']}")
        print(f"  - Sistema listo: {stats['system_ready']}")
    
    # Ejecutar demo
    asyncio.run(demo_data_loading())
