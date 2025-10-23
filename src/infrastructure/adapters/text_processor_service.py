"""
Implementación concreta del TextProcessor
"""

import re
from typing import List
import sys
from pathlib import Path

# Añadir el directorio padre al path para importar domain
sys.path.append(str(Path(__file__).parent.parent.parent))

from domain.entities.domain import TextProcessor

class BasicTextProcessor(TextProcessor):
    """Implementación básica de TextProcessor"""
    
    def __init__(self):
        # Patrones para limpieza de texto
        self.whitespace_pattern = re.compile(r'\s+')
        self.special_chars_pattern = re.compile(r'[^\w\s\-.,!?;:()\[\]{}"]')
        
        # Palabras vacías en español
        self.stop_words = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le',
            'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'como',
            'pero', 'sus', 'le', 'ya', 'o', 'fue', 'este', 'ha', 'si', 'porque', 'esta', 'son',
            'entre', 'cuando', 'muy', 'sin', 'sobre', 'ser', 'tiene', 'también', 'me', 'hasta',
            'hay', 'donde', 'han', 'quien', 'están', 'estado', 'desde', 'todo', 'nos', 'durante',
            'todos', 'uno', 'les', 'ni', 'contra', 'otros', 'fueron', 'ese', 'eso', 'había',
            'ante', 'ellos', 'e', 'esto', 'mí', 'antes', 'algunos', 'qué', 'unos', 'yo', 'otro',
            'otras', 'otra', 'él', 'tanto', 'esa', 'estos', 'mucho', 'quienes', 'nada', 'muchos',
            'cual', 'sea', 'poco', 'ella', 'estar', 'haber', 'estas', 'estaba', 'estamos', 'pueden',
            'hacen', 'entonces', 'fui', 'foto', 'fotos', 'cada', 'veía', 'algo', 'somos', 'así'
        }
    
    def split_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Divide texto en chunks con overlap"""
        if not text or not text.strip():
            return []
        
        # Limpiar texto primero
        cleaned_text = self.clean_text(text)
        words = cleaned_text.split()
        
        if len(words) <= chunk_size:
            return [cleaned_text]
        
        chunks = []
        start = 0
        
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            chunk = " ".join(chunk_words)
            
            if chunk.strip():
                chunks.append(chunk.strip())
            
            # Si llegamos al final, salir
            if end >= len(words):
                break
            
            # Mover el inicio considerando el overlap
            start = end - overlap
            
            # Evitar overlap negativo
            if start < 0:
                start = 0
        
        return chunks
    
    def clean_text(self, text: str) -> str:
        """Limpia y normaliza texto"""
        if not text:
            return ""
        
        # Convertir a minúsculas
        cleaned = text.lower()
        
        # Reemplazar múltiples espacios en blanco con uno solo
        cleaned = self.whitespace_pattern.sub(' ', cleaned)
        
        # Remover caracteres especiales pero mantener puntuación básica
        # cleaned = self.special_chars_pattern.sub(' ', cleaned)
        
        # Remover espacios al inicio y final
        cleaned = cleaned.strip()
        
        # Remover líneas vacías múltiples
        lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
        cleaned = '\n'.join(lines)
        
        return cleaned
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extrae palabras clave del texto"""
        if not text:
            return []
        
        # Limpiar texto
        cleaned = self.clean_text(text)
        
        # Dividir en palabras
        words = re.findall(r'\b\w+\b', cleaned.lower())
        
        # Filtrar palabras vacías y palabras muy cortas
        keywords = [
            word for word in words 
            if len(word) > 2 and word not in self.stop_words
        ]
        
        # Contar frecuencias
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Ordenar por frecuencia y retornar las más comunes
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, freq in sorted_words[:max_keywords]]
    
    def get_text_stats(self, text: str) -> dict:
        """Obtiene estadísticas del texto"""
        if not text:
            return {
                "characters": 0,
                "words": 0,
                "sentences": 0,
                "paragraphs": 0
            }
        
        # Contar caracteres
        char_count = len(text)
        
        # Contar palabras
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        
        # Contar oraciones (aproximado)
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Contar párrafos
        paragraphs = text.split('\n\n')
        paragraph_count = len([p for p in paragraphs if p.strip()])
        
        return {
            "characters": char_count,
            "words": word_count,
            "sentences": sentence_count,
            "paragraphs": paragraph_count
        }
    
    def truncate_text(self, text: str, max_length: int = 1000) -> str:
        """Trunca texto a una longitud máxima"""
        if not text or len(text) <= max_length:
            return text
        
        # Truncar en el último espacio antes del límite
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.8:  # Si el último espacio está cerca del final
            truncated = truncated[:last_space]
        
        return truncated + "..."
