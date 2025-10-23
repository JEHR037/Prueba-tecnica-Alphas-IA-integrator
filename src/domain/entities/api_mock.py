"""
Mock de la API de OpenAI para el sistema RAG
Simula respuestas realistas de OpenAI sin hacer llamadas reales a la API
"""
import random
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
from pathlib import Path

# Añadir el directorio src al path para importaciones
sys.path.append(str(Path(__file__).parent.parent.parent))

from domain.entities.domain import OpenAIClient, AIServiceError


class OpenAIMockClient(OpenAIClient):
    """Mock del cliente de OpenAI que simula respuestas realistas"""
    
    def __init__(self, model: str = "gpt-3.5-turbo", simulate_delay: bool = True):
        """
        Inicializa el mock del cliente de OpenAI
        
        Args:
            model: Modelo a simular
            simulate_delay: Si simular delay de red
        """
        self.model = model
        self.simulate_delay = simulate_delay
        self.call_count = 0
        
        # Respuestas predefinidas para diferentes tipos de consultas
        self.predefined_responses = {
            "beneficios": {
                "keywords": ["beneficio", "seguro", "salud", "dental", "vision", "jubilacion", "pension"],
                "response": """Según las políticas de Google, los empleados tienen acceso a un paquete integral de beneficios que incluye:

**Beneficios de Salud:**
- Seguro médico completo con cobertura del 100% para empleados
- Seguro dental y de visión
- Programas de bienestar y salud mental

**Beneficios Financieros:**
- Plan de jubilación 401(k) con contribución de la empresa
- Opciones de acciones de Google
- Bonos de desempeño anuales

**Tiempo Libre:**
- Vacaciones flexibles
- Días de enfermedad pagados
- Licencia parental extendida

Estos beneficios están diseñados para apoyar el bienestar integral de nuestros empleados."""
            },
            "vacaciones": {
                "keywords": ["vacacion", "tiempo libre", "dias libres", "ausencia", "permiso"],
                "response": """La política de vacaciones de Google se basa en un sistema flexible:

**Política de Tiempo Libre Flexible:**
- No hay límite específico de días de vacaciones
- Los empleados pueden tomar el tiempo que necesiten, coordinando con su equipo
- Se requiere aprobación del manager para ausencias prolongadas

**Días Festivos:**
- Google observa los días festivos nacionales
- Días flotantes adicionales para celebraciones personales o culturales

**Proceso de Solicitud:**
1. Coordinar con el equipo y manager
2. Registrar en el sistema interno
3. Asegurar cobertura de responsabilidades

La filosofía es confiar en que los empleados gestionen su tiempo de manera responsable."""
            },
            "trabajo_remoto": {
                "keywords": ["remoto", "casa", "hibrido", "oficina", "teletrabajo"],
                "response": """Google ha adoptado un modelo de trabajo flexible post-pandemia:

**Opciones de Trabajo:**
- Trabajo híbrido (3 días en oficina, 2 remotos)
- Trabajo completamente remoto (con aprobación especial)
- Trabajo presencial completo

**Políticas para Trabajo Remoto:**
- Equipamiento proporcionado por la empresa
- Estipendio para configuración de oficina en casa
- Acceso completo a herramientas y sistemas corporativos

**Expectativas:**
- Mantener productividad y colaboración efectiva
- Participar en reuniones de equipo regulares
- Cumplir con horarios de disponibilidad acordados

El objetivo es maximizar la flexibilidad mientras se mantiene la cultura colaborativa de Google."""
            },
            "desarrollo": {
                "keywords": ["desarrollo", "carrera", "crecimiento", "promocion", "capacitacion"],
                "response": """Google invierte significativamente en el desarrollo profesional de sus empleados:

**Programas de Desarrollo:**
- 20% del tiempo para proyectos personales de innovación
- Presupuesto anual de $3,000 para capacitación externa
- Programas internos de mentoría

**Crecimiento de Carrera:**
- Revisiones de desempeño semestrales
- Planes de desarrollo individual (IDP)
- Rotaciones internas entre equipos y proyectos

**Recursos de Aprendizaje:**
- Plataforma interna de cursos (Grow with Google)
- Conferencias y certificaciones pagadas por la empresa
- Grupos de estudio y comunidades de práctica

El enfoque es crear un ambiente donde cada empleado pueda alcanzar su máximo potencial."""
            }
        }
        
        # Respuestas genéricas para consultas no específicas
        self.generic_responses = [
            "Basándome en las políticas de Google disponibles, puedo proporcionar información general sobre este tema. Sin embargo, para detalles específicos, recomiendo consultar con el departamento de Recursos Humanos.",
            "Esta consulta requiere información más específica de las políticas internas. Te sugiero revisar el portal de empleados o contactar directamente con tu manager o RRHH.",
            "Google mantiene políticas actualizadas sobre este tema. Para obtener la información más reciente y precisa, te recomiendo acceder a los recursos oficiales de la empresa.",
        ]
    
    def get_chat_completion(self, messages: List[dict]) -> dict:
        """Simula una respuesta de chat completion de OpenAI"""
        try:
            self.call_count += 1
            
            # Validar mensajes de entrada
            self._validate_messages(messages)
            
            # Simular delay de red
            if self.simulate_delay:
                time.sleep(random.uniform(0.5, 2.0))
            
            # Extraer el contenido del último mensaje del usuario
            user_message = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    user_message = msg.get("content", "")
                    break
            
            # Generar respuesta basada en el contenido
            response_content = self._generate_contextual_response(user_message)
            
            # Calcular tokens aproximados
            prompt_tokens = sum(len(msg.get("content", "").split()) for msg in messages) * 1.3
            completion_tokens = len(response_content.split()) * 1.3
            
            return {
                "content": response_content,
                "role": "assistant",
                "finish_reason": "stop",
                "usage": {
                    "prompt_tokens": int(prompt_tokens),
                    "completion_tokens": int(completion_tokens),
                    "total_tokens": int(prompt_tokens + completion_tokens)
                }
            }
            
        except Exception as e:
            raise AIServiceError(f"Error en mock de OpenAI: {e}")
    
    def count_tokens(self, text: str) -> int:
        """Simula el conteo de tokens"""
        if not text:
            return 0
        
        # Estimación aproximada: ~1.3 tokens por palabra
        words = len(text.split())
        return int(words * 1.3)
    
    def generate_rag_response(self, query: str, context: str) -> str:
        """Genera respuesta RAG usando el contexto proporcionado"""
        try:
            # Validar entrada
            self._validate_rag_input(query, context)
            
            # Simular delay
            if self.simulate_delay:
                time.sleep(random.uniform(1.0, 2.5))
            
            # Analizar el contexto para generar una respuesta más específica
            response = self._generate_rag_response_from_context(query, context)
            
            return response
            
        except Exception as e:
            raise AIServiceError(f"Error generando respuesta RAG mock: {e}")
    
    def _validate_messages(self, messages: List[dict]) -> None:
        """Valida los mensajes de entrada para chat completion"""
        if not messages:
            raise AIServiceError("❌ Los mensajes no pueden estar vacíos")
        
        for msg in messages:
            content = msg.get("content", "")
            
            # Validar que la pregunta no esté vacía
            if msg.get("role") == "user" and not content.strip():
                raise AIServiceError("❌ Pregunta no puede estar vacía")
            
            # Validar longitud máxima de pregunta (500 caracteres - consistente con DTO)
            if msg.get("role") == "user" and len(content) > 500:
                raise AIServiceError("❌ Pregunta no puede exceder 500 caracteres")
    
    def _validate_rag_input(self, query: str, context: str) -> None:
        """Valida la entrada para respuesta RAG"""
        # Validar que la pregunta no esté vacía
        if not query or not query.strip():
            raise AIServiceError("❌ Pregunta no puede estar vacía")
        
        # Validar longitud máxima de pregunta (500 caracteres - consistente con DTO)
        if len(query) > 500:
            raise AIServiceError("❌ Pregunta no puede exceder 500 caracteres")
        
        # Validar longitud máxima de contexto (2000 caracteres) - opcional
        if context and len(context) > 2000:
            raise AIServiceError("❌ Contexto opcional no puede exceder 2000 caracteres")
    
    def _generate_contextual_response(self, user_message: str) -> str:
        """Genera respuesta basada en el contexto del mensaje"""
        user_message_lower = user_message.lower()
        
        # Buscar en respuestas predefinidas
        for category, data in self.predefined_responses.items():
            if any(keyword in user_message_lower for keyword in data["keywords"]):
                return data["response"]
        
        # Si no encuentra una respuesta específica, usar genérica
        return random.choice(self.generic_responses)
    
    def _generate_rag_response_from_context(self, query: str, context: str) -> str:
        """Genera respuesta RAG más sofisticada basada en el contexto"""
        query_lower = query.lower()
        context_lower = context.lower()
        
        # Analizar el tipo de pregunta
        if any(word in query_lower for word in ["qué", "que", "what", "cuál", "cual"]):
            response_type = "definition"
        elif any(word in query_lower for word in ["cómo", "como", "how"]):
            response_type = "process"
        elif any(word in query_lower for word in ["cuándo", "cuando", "when"]):
            response_type = "timing"
        elif any(word in query_lower for word in ["dónde", "donde", "where"]):
            response_type = "location"
        else:
            response_type = "general"
        
        # Extraer información relevante del contexto
        context_sentences = context.split('.')[:3]  # Primeras 3 oraciones
        
        # Generar respuesta estructurada
        if response_type == "definition":
            response = f"Según la información disponible, {context_sentences[0].strip()}."
            if len(context_sentences) > 1:
                response += f" Además, {context_sentences[1].strip()}."
        
        elif response_type == "process":
            response = f"El proceso se describe de la siguiente manera: {context_sentences[0].strip()}."
            if len(context_sentences) > 1:
                response += f" Los pasos incluyen: {context_sentences[1].strip()}."
        
        elif response_type == "timing":
            response = f"En cuanto al tiempo, {context_sentences[0].strip()}."
            if "día" in context_lower or "semana" in context_lower or "mes" in context_lower:
                response += " Los plazos específicos están detallados en las políticas correspondientes."
        
        else:
            response = f"Basándome en la información disponible: {context_sentences[0].strip()}."
            if len(context_sentences) > 1:
                response += f" {context_sentences[1].strip()}."
        
        # Añadir disclaimer
        response += "\n\nPara información más específica o actualizada, te recomiendo consultar directamente con el departamento correspondiente."
        
        return response
    
    def validate_api_key(self) -> bool:
        """Simula validación de API key (siempre exitosa en el mock)"""
        if self.simulate_delay:
            time.sleep(0.5)
        return True
    
    def get_available_models(self) -> List[str]:
        """Retorna lista de modelos simulados"""
        return [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-4",
            "gpt-4-32k",
            "gpt-4-turbo-preview"
        ]
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Estima el costo simulado (siempre $0 para el mock)"""
        return 0.0
    
    def get_mock_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del mock para debugging"""
        return {
            "model": self.model,
            "call_count": self.call_count,
            "simulate_delay": self.simulate_delay,
            "predefined_categories": list(self.predefined_responses.keys())
        }
    
    def reset_stats(self) -> None:
        """Reinicia las estadísticas del mock"""
        self.call_count = 0


class OpenAIMockFactory:
    """Factory para crear diferentes tipos de mocks de OpenAI"""
    
    @staticmethod
    def create_fast_mock() -> OpenAIMockClient:
        """Crea un mock rápido sin delays"""
        return OpenAIMockClient(simulate_delay=False)
    
    @staticmethod
    def create_realistic_mock() -> OpenAIMockClient:
        """Crea un mock con delays realistas"""
        return OpenAIMockClient(simulate_delay=True)
    
    @staticmethod
    def create_gpt4_mock() -> OpenAIMockClient:
        """Crea un mock simulando GPT-4"""
        return OpenAIMockClient(model="gpt-4", simulate_delay=True)


# Ejemplo de uso y testing
if __name__ == "__main__":
    # Crear mock
    mock_client = OpenAIMockFactory.create_realistic_mock()
    
    print("=== PRUEBAS DEL MOCK DE OPENAI ===\n")
    
    # Probar chat completion válido
    print("1. Probando chat completion válido:")
    messages = [
        {"role": "system", "content": "Eres un asistente de RRHH de Google"},
        {"role": "user", "content": "¿Cuáles son los beneficios de salud disponibles?"}
    ]
    
    try:
        response = mock_client.get_chat_completion(messages)
        print("✅ Respuesta exitosa:")
        print(response["content"])
        print(f"Tokens utilizados: {response['usage']['total_tokens']}")
    except AIServiceError as e:
        print(f"❌ Error: {e}")
    
    # Probar validaciones - pregunta vacía
    print("\n2. Probando validación - pregunta vacía:")
    try:
        empty_messages = [
            {"role": "system", "content": "Eres un asistente"},
            {"role": "user", "content": ""}
        ]
        mock_client.get_chat_completion(empty_messages)
    except AIServiceError as e:
        print(f"✅ Validación funcionando: {e}")
    
    # Probar validaciones - pregunta muy larga
    print("\n3. Probando validación - pregunta muy larga (>500 caracteres):")
    try:
        long_question = "¿" + "Cuál es la política de " * 50  # Más de 500 caracteres
        long_messages = [
            {"role": "system", "content": "Eres un asistente"},
            {"role": "user", "content": long_question}
        ]
        mock_client.get_chat_completion(long_messages)
    except AIServiceError as e:
        print(f"✅ Validación funcionando: {e}")
    
    # Probar RAG response válido
    print("\n4. Probando RAG response válido:")
    query = "¿Cómo funciona la política de vacaciones?"
    context = "Google ofrece tiempo libre flexible. Los empleados pueden tomar vacaciones coordinando con su equipo."
    
    try:
        rag_response = mock_client.generate_rag_response(query, context)
        print("✅ Respuesta RAG exitosa:")
        print(rag_response)
    except AIServiceError as e:
        print(f"❌ Error: {e}")
    
    # Probar validación RAG - contexto muy largo
    print("\n5. Probando validación RAG - contexto muy largo (>2000 caracteres):")
    try:
        long_context = "Este es un contexto muy largo. " * 100  # Más de 2000 caracteres
        mock_client.generate_rag_response("¿Qué dice sobre vacaciones?", long_context)
    except AIServiceError as e:
        print(f"✅ Validación funcionando: {e}")
    
    # Probar validación RAG - pregunta vacía
    print("\n6. Probando validación RAG - pregunta vacía:")
    try:
        mock_client.generate_rag_response("", "Contexto válido")
    except AIServiceError as e:
        print(f"✅ Validación funcionando: {e}")
    
    # Mostrar estadísticas
    print("\n=== ESTADÍSTICAS DEL MOCK ===")
    stats = mock_client.get_mock_stats()
    print(f"Modelo: {stats['model']}")
    print(f"Llamadas realizadas: {stats['call_count']}")
    print(f"Simula delay: {stats['simulate_delay']}")
    print(f"Categorías predefinidas: {', '.join(stats['predefined_categories'])}")
