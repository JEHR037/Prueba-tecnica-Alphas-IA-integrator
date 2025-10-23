"""
Implementación del servicio RAG usando arquitectura hexagonal
"""

from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

# Añadir el directorio padre al path para importar domain
sys.path.append(str(Path(__file__).parent.parent.parent))

from domain.entities.domain import (
    Document, DocumentChunk, SearchResult, RAGResponse,
    DocumentRepository, VectorRepository, EmbeddingService,
    TextProcessor, OpenAIClient, RAGService, HRPolicyService,
    RAGDomainException, DocumentNotFoundError, InvalidQueryError,
    EmbeddingGenerationError, VectorSearchError, AIServiceError
)

class RAGServiceImpl(RAGService, HRPolicyService):
    """Implementación concreta del servicio RAG"""
    
    def __init__(
        self,
        document_repo: DocumentRepository,
        vector_repo: VectorRepository,
        embedding_service: EmbeddingService,
        text_processor: TextProcessor,
        openai_client: Optional[OpenAIClient] = None
    ):
        self.document_repo = document_repo
        self.vector_repo = vector_repo
        self.embedding_service = embedding_service
        self.text_processor = text_processor
        self.openai_client = openai_client
        
        # Cargar políticas predefinidas si no existen
        if self.get_document_count() == 0:
            self.load_predefined_policies()
    
    def add_document(self, title: str, content: str, category: str, 
                    metadata: Dict[str, Any] = None) -> int:
        """Añade un documento al sistema RAG"""
        try:
            if not title or not content or not category:
                raise InvalidQueryError("Título, contenido y categoría son requeridos")
            
            # Crear documento
            document = Document(
                title=title.strip(),
                content=content.strip(),
                category=category.strip(),
                metadata=metadata or {}
            )
            
            # Guardar documento
            document_id = self.document_repo.save_document(document)
            document.id = document_id
            
            # Procesar texto en chunks
            chunks = self.text_processor.split_text(content)
            
            # Generar embeddings para cada chunk
            embeddings = self.embedding_service.encode_batch(chunks)
            
            # Guardar embeddings
            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_text=chunk_text,
                    embedding=embedding,
                    chunk_index=i
                )
                self.vector_repo.save_embedding(chunk)
            
            return document_id
            
        except Exception as e:
            if isinstance(e, RAGDomainException):
                raise
            raise RAGDomainException(f"Error añadiendo documento: {e}")
    
    def search_documents(self, query: str, top_k: int = 5, 
                        category: Optional[str] = None) -> List[SearchResult]:
        """Busca documentos relevantes para una consulta"""
        try:
            if not query or not query.strip():
                raise InvalidQueryError("La consulta no puede estar vacía")
            
            # Generar embedding de la consulta
            query_embedding = self.embedding_service.encode_text(query.strip())
            
            # Buscar chunks similares
            similar_chunks = self.vector_repo.search_similar(
                query_embedding, top_k, category
            )
            
            # Convertir a SearchResults
            results = []
            for chunk in similar_chunks:
                # Obtener documento completo
                document = self.document_repo.get_document(chunk.document_id)
                if document:
                    result = SearchResult(
                        document=document,
                        chunk=chunk,
                        relevance_score=chunk.similarity_score
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            if isinstance(e, RAGDomainException):
                raise
            raise VectorSearchError(f"Error en búsqueda de documentos: {e}")
    
    def generate_response(self, query: str, use_ai: bool = True) -> RAGResponse:
        """Genera una respuesta completa usando RAG"""
        try:
            if not query or not query.strip():
                raise InvalidQueryError("La consulta no puede estar vacía")
            
            # Buscar documentos relevantes
            search_results = self.search_documents(query, top_k=3)
            
            if not search_results:
                return RAGResponse(
                    answer="Lo siento, no encontré información relevante sobre tu consulta en las políticas de RRHH de Google.",
                    sources=[],
                    confidence=0.0,
                    query=query
                )
            
            # Construir contexto
            context_parts = []
            for result in search_results:
                context_parts.append(f"Documento: {result.document.title}")
                context_parts.append(f"Contenido: {result.chunk.chunk_text}")
                context_parts.append("---")
            
            context = "\n".join(context_parts)
            
            # Generar respuesta
            if use_ai and self.openai_client:
                try:
                    answer = self.openai_client.generate_rag_response(query, context)
                except AIServiceError:
                    # Fallback a respuesta template si falla OpenAI
                    answer = self._generate_template_response(query, search_results)
            else:
                answer = self._generate_template_response(query, search_results)
            
            # Calcular confianza basada en la similitud promedio
            confidence = sum(r.relevance_score for r in search_results) / len(search_results)
            
            return RAGResponse(
                answer=answer,
                sources=search_results,
                confidence=confidence,
                query=query
            )
            
        except Exception as e:
            if isinstance(e, RAGDomainException):
                raise
            raise RAGDomainException(f"Error generando respuesta: {e}")
    
    def _generate_template_response(self, query: str, results: List[SearchResult]) -> str:
        """Genera respuesta usando templates predefinidos"""
        if not results:
            return "No encontré información específica sobre tu consulta en las políticas de Google."
        
        best_result = results[0]
        
        response = f"Basándome en las políticas de RRHH de Google, específicamente en '{best_result.document.title}':\n\n"
        response += best_result.chunk.chunk_text[:400]
        
        if len(best_result.chunk.chunk_text) > 400:
            response += "..."
        
        if len(results) > 1:
            response += f"\n\nTambién encontré información relacionada en {len(results)-1} documento(s) adicional(es)."
        
        return response
    
    def get_document_count(self) -> int:
        """Retorna el número total de documentos"""
        return self.document_repo.get_document_count()
    
    def get_categories(self) -> List[str]:
        """Retorna todas las categorías disponibles"""
        return self.document_repo.get_all_categories()
    
    def delete_document(self, document_id: int) -> bool:
        """Elimina un documento del sistema"""
        try:
            # Eliminar embeddings primero
            self.vector_repo.delete_embeddings_by_document(document_id)
            
            # Eliminar documento
            return self.document_repo.delete_document(document_id)
            
        except Exception as e:
            raise DocumentNotFoundError(f"Error eliminando documento {document_id}: {e}")
    
    # Implementación de HRPolicyService
    
    def load_predefined_policies(self) -> int:
        """Carga políticas predefinidas de RRHH"""
        policies = [
            {
                "title": "Política de Diversidad e Inclusión",
                "category": "diversidad",
                "content": """
                Google se compromete a crear un ambiente de trabajo diverso e inclusivo. 
                Nuestra política incluye:
                - Igualdad de oportunidades para todos los empleados
                - Programas de mentoría para grupos subrepresentados
                - Capacitación en sesgo inconsciente para todos los managers
                - Comités de diversidad en cada oficina
                - Métricas de diversidad transparentes y objetivos anuales
                - Proceso de contratación libre de sesgos
                - Apoyo a comunidades LGBTQ+, mujeres en tecnología, y minorías étnicas
                """
            },
            {
                "title": "Política de Trabajo Remoto e Híbrido",
                "category": "trabajo_remoto",
                "content": """
                Google ofrece flexibilidad laboral a través de:
                - Trabajo híbrido: 3 días en oficina, 2 días remotos por semana
                - Trabajo completamente remoto para roles elegibles
                - Horarios flexibles con core hours de 10am-3pm
                - Subsidio para equipamiento de oficina en casa ($1000 anuales)
                - Reembolso de internet y servicios ($75 mensuales)
                - Espacios de coworking disponibles globalmente
                - Reuniones por defecto con opción virtual
                - Política de 'no meetings' los viernes por la tarde
                """
            },
            {
                "title": "Beneficios de Salud y Bienestar",
                "category": "beneficios",
                "content": """
                Beneficios integrales de Google incluyen:
                - Seguro médico, dental y de visión 100% cubierto
                - Seguro de vida y discapacidad
                - Programa de asistencia al empleado (EAP)
                - Gimnasios en el campus y membresías externas
                - Clases de mindfulness y manejo del estrés
                - Licencia parental de 18 semanas (primario) y 12 semanas (secundario)
                - Apoyo para fertilidad y adopción
                - Días de salud mental ilimitados
                - Programa de wellness con incentivos
                """
            },
            {
                "title": "Política de Desarrollo Profesional",
                "category": "desarrollo",
                "content": """
                Google invierte en el crecimiento profesional mediante:
                - 20% del tiempo para proyectos personales
                - Presupuesto anual de $3000 para capacitación
                - Programa interno de certificaciones técnicas
                - Mentoría cruzada entre equipos
                - Rotaciones internas cada 2 años
                - Conferencias y eventos de la industria
                - Cursos de liderazgo para managers
                - Programa de PhD fellowship
                - Sabbaticals cada 5 años (3 meses pagados)
                """
            },
            {
                "title": "Código de Conducta y Ética",
                "category": "etica",
                "content": """
                El código de conducta de Google establece:
                - "Don't be evil" como principio fundamental
                - Respeto y dignidad para todos los empleados
                - Política de tolerancia cero para acoso
                - Confidencialidad de información del usuario
                - Conflictos de interés deben ser reportados
                - Uso responsable de recursos corporativos
                - Protección de propiedad intelectual
                - Cumplimiento de leyes locales e internacionales
                - Canal anónimo para reportar violaciones
                - Investigación imparcial de todas las denuncias
                """
            },
            {
                "title": "Política de Compensación y Equidad Salarial",
                "category": "compensacion",
                "content": """
                Sistema de compensación transparente de Google:
                - Bandas salariales públicas por nivel y ubicación
                - Revisiones salariales anuales basadas en performance
                - Equity grants para todos los empleados
                - Bonos de performance hasta 30% del salario base
                - Ajustes por costo de vida por ubicación
                - Auditorías anuales de equidad salarial
                - Pay transparency: empleados pueden conocer rangos salariales
                - Programa de referidos con bonos hasta $5000
                - Beneficios adicionales: comida, transporte, guardería
                """
            },
            {
                "title": "Política de Vacaciones y Tiempo Libre",
                "category": "vacaciones",
                "content": """
                Política flexible de tiempo libre en Google:
                - Vacaciones ilimitadas con mínimo recomendado de 15 días
                - Días festivos globales y locales respetados
                - Sabbatical de 3 meses cada 5 años
                - Licencia por duelo: 10 días para familia inmediata
                - Licencia por enfermedad ilimitada
                - Tiempo libre para voluntariado: 20 horas anuales pagadas
                - Días de bienestar mental sin preguntas
                - Política de desconexión digital fuera del horario laboral
                - Apoyo para emergencias familiares
                """
            }
        ]
        
        loaded_count = 0
        for policy in policies:
            try:
                self.add_document(
                    title=policy["title"],
                    content=policy["content"],
                    category=policy["category"],
                    metadata={"source": "predefined", "version": "1.0"}
                )
                loaded_count += 1
            except Exception as e:
                print(f"Error cargando política {policy['title']}: {e}")
        
        return loaded_count
    
    def query_policy(self, question: str) -> RAGResponse:
        """Consulta específica sobre políticas de RRHH"""
        return self.generate_response(question, use_ai=True)
    
    def get_policy_categories(self) -> List[str]:
        """Obtiene categorías específicas de políticas de RRHH"""
        return self.get_categories()
    
    def validate_policy_query(self, query: str) -> bool:
        """Valida si una consulta es apropiada para políticas de RRHH"""
        if not query or not query.strip():
            return False
        
        # Palabras clave relacionadas con RRHH
        hr_keywords = [
            'política', 'beneficio', 'salario', 'vacaciones', 'trabajo', 'remoto',
            'diversidad', 'inclusión', 'desarrollo', 'capacitación', 'ética',
            'conducta', 'compensación', 'seguro', 'salud', 'licencia', 'permiso',
            'horario', 'flexible', 'empleado', 'recursos humanos', 'rrhh'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in hr_keywords)
