"""
Implementación concreta del OpenAIClient
"""

import openai
import tiktoken
from typing import List, Dict
import os
import sys
from pathlib import Path

# Añadir el directorio padre al path para importar domain
sys.path.append(str(Path(__file__).parent.parent.parent))

from domain.entities.domain import OpenAIClient, AIServiceError

class OpenAIClientService(OpenAIClient):
    """Implementación de OpenAIClient usando la API de OpenAI"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        """
        Inicializa el cliente de OpenAI
        
        Args:
            api_key: Clave API de OpenAI (si no se proporciona, se busca en variables de entorno)
            model: Modelo a usar para chat completion
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise AIServiceError("No se proporcionó API key de OpenAI")
        
        openai.api_key = self.api_key
        
        # Inicializar tokenizer
        try:
            self.tokenizer = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback para modelos no reconocidos
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def get_chat_completion(self, messages: List[dict]) -> dict:
        """Envía mensajes a OpenAI API y retorna respuesta"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.3,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            return {
                "content": response.choices[0].message.content,
                "role": response.choices[0].message.role,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except openai.error.RateLimitError as e:
            raise AIServiceError(f"Límite de rate excedido: {e}")
        except openai.error.InvalidRequestError as e:
            raise AIServiceError(f"Solicitud inválida: {e}")
        except openai.error.AuthenticationError as e:
            raise AIServiceError(f"Error de autenticación: {e}")
        except openai.error.APIError as e:
            raise AIServiceError(f"Error de API: {e}")
        except Exception as e:
            raise AIServiceError(f"Error inesperado: {e}")
    
    def count_tokens(self, text: str) -> int:
        """Calcula tokens aproximados para un texto"""
        try:
            if not text:
                return 0
            
            tokens = self.tokenizer.encode(text)
            return len(tokens)
            
        except Exception as e:
            # Fallback: estimación aproximada
            return len(text.split()) * 1.3  # Aproximadamente 1.3 tokens por palabra
    
    def generate_rag_response(self, query: str, context: str) -> str:
        """Genera respuesta RAG usando el contexto proporcionado"""
        try:
            system_prompt = """Eres un asistente especializado en políticas de Recursos Humanos de Google. 
Tu trabajo es responder preguntas basándote únicamente en el contexto proporcionado.

Instrucciones:
1. Responde solo basándote en la información del contexto
2. Si la información no está en el contexto, indica que no tienes esa información específica
3. Sé preciso y directo en tus respuestas
4. Usa un tono profesional pero amigable
5. Si es relevante, menciona la fuente específica de la información"""

            user_prompt = f"""Contexto sobre políticas de RRHH de Google:
{context}

Pregunta del usuario: {query}

Por favor, responde la pregunta basándote únicamente en el contexto proporcionado."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.get_chat_completion(messages)
            return response["content"]
            
        except Exception as e:
            raise AIServiceError(f"Error generando respuesta RAG: {e}")
    
    def validate_api_key(self) -> bool:
        """Valida que la API key sea válida"""
        try:
            # Hacer una solicitud simple para validar la key
            test_messages = [{"role": "user", "content": "Hello"}]
            self.get_chat_completion(test_messages)
            return True
        except AIServiceError:
            return False
    
    def get_available_models(self) -> List[str]:
        """Obtiene lista de modelos disponibles"""
        try:
            models = openai.Model.list()
            return [model.id for model in models.data if 'gpt' in model.id]
        except Exception as e:
            raise AIServiceError(f"Error obteniendo modelos disponibles: {e}")
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Estima el costo de una solicitud (en USD)"""
        # Precios aproximados para GPT-3.5-turbo (pueden cambiar)
        if "gpt-4" in self.model:
            prompt_cost = prompt_tokens * 0.03 / 1000
            completion_cost = completion_tokens * 0.06 / 1000
        else:  # gpt-3.5-turbo
            prompt_cost = prompt_tokens * 0.0015 / 1000
            completion_cost = completion_tokens * 0.002 / 1000
        
        return prompt_cost + completion_cost
