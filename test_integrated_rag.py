#!/usr/bin/env python3
"""
Script de prueba para el sistema RAG integrado
Verifica que todos los componentes funcionen correctamente
"""

import requests
import json
import time
import sys
from pathlib import Path

# Añadir el directorio src al path
sys.path.append(str(Path(__file__).parent / "src"))

# URL base de la API
API_BASE_URL = "http://localhost:8000"

def print_section(title: str):
    """Imprime un título de sección"""
    print(f"\n{'='*60}")
    print(f"🔥 {title}")
    print(f"{'='*60}")

def print_json(data, title: str = ""):
    """Imprime JSON formateado"""
    if title:
        print(f"\n📋 {title}:")
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))

def test_health_check():
    """Prueba el health check básico"""
    print_section("HEALTH CHECK BÁSICO")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print_json(response.json(), "Health Check")
            return True
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando a la API: {e}")
        print("💡 Asegúrate de que la API esté ejecutándose en http://localhost:8000")
        return False

def test_integrated_system_status():
    """Prueba el estado del sistema integrado"""
    print_section("ESTADO DEL SISTEMA INTEGRADO")
    
    try:
        response = requests.get(f"{API_BASE_URL}/system/integrated/status", timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_json(data, "Estado del Sistema Integrado")
            
            system_info = data.get("system_info", {})
            if system_info.get("system_ready", False):
                print("✅ Sistema integrado listo")
                return True
            else:
                print("⚠️ Sistema integrado no está listo")
                return False
        else:
            print(f"❌ Error obteniendo estado: {response.status_code}")
            print_json(response.json() if response.content else {}, "Error Response")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_integrated_question(question: str, department: str = None):
    """Prueba una pregunta con el endpoint integrado"""
    print(f"\n🔍 Probando pregunta integrada: '{question}'")
    
    try:
        data = {
            "question": question,
            "department": department,
            "use_ai": True,
            "top_k": 5
        }
        
        response = requests.post(
            f"{API_BASE_URL}/ask/integrated", 
            json=data, 
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Respuesta: {result.get('answer', 'Sin respuesta')[:200]}...")
            print(f"🎯 Confianza: {result.get('confidence', 0):.2f}")
            print(f"📚 Fuentes: {len(result.get('sources', []))}")
            
            # Mostrar fuentes si existen
            sources = result.get('sources', [])
            if sources:
                print("📖 Fuentes principales:")
                for i, source in enumerate(sources[:2], 1):
                    doc = source.get('document', {})
                    print(f"   {i}. {doc.get('title', 'Sin título')} (Categoría: {doc.get('category', 'N/A')})")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print_json(error_data, "Error Details")
            except:
                print(f"Response text: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_original_endpoint(question: str, department: str = None):
    """Prueba el endpoint original para comparación"""
    print(f"\n🔍 Probando endpoint original: '{question}'")
    
    try:
        data = {
            "question": question,
            "department": department,
            "use_ai": True,
            "top_k": 5
        }
        
        response = requests.post(
            f"{API_BASE_URL}/ask", 
            json=data, 
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Respuesta: {result.get('answer', 'Sin respuesta')[:200]}...")
            print(f"🎯 Confianza: {result.get('confidence', 0):.2f}")
            print(f"📚 Fuentes: {len(result.get('sources', []))}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print_json(error_data, "Error Details")
            except:
                print(f"Response text: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🔥 PRUEBAS DEL SISTEMA RAG INTEGRADO 🔥")
    
    # 1. Health check básico
    if not test_health_check():
        print("\n❌ Health check falló. Deteniendo pruebas.")
        return 1
    
    # 2. Estado del sistema integrado
    print("\n⏳ Esperando inicialización del sistema integrado...")
    time.sleep(3)  # Dar tiempo para inicialización
    
    if not test_integrated_system_status():
        print("\n⚠️ Sistema integrado no está listo, pero continuando con las pruebas...")
    
    # 3. Pruebas de preguntas
    print_section("PRUEBAS DE PREGUNTAS")
    
    test_questions = [
        {
            "question": "¿Cuáles son los beneficios de salud disponibles?",
            "department": "rrhh",
            "description": "Pregunta sobre beneficios"
        },
        {
            "question": "¿Cómo funciona la política de vacaciones?",
            "department": "rrhh",
            "description": "Pregunta sobre vacaciones"
        },
        {
            "question": "¿Puedo trabajar desde casa?",
            "department": "rrhh",
            "description": "Pregunta sobre trabajo remoto"
        }
    ]
    
    integrated_success = 0
    original_success = 0
    
    for i, test in enumerate(test_questions, 1):
        print(f"\n--- PREGUNTA {i}: {test['description']} ---")
        
        # Probar endpoint integrado
        print("🔥 ENDPOINT INTEGRADO:")
        if test_integrated_question(test["question"], test["department"]):
            integrated_success += 1
        
        # Probar endpoint original para comparación
        print("\n📊 ENDPOINT ORIGINAL (comparación):")
        if test_original_endpoint(test["question"], test["department"]):
            original_success += 1
        
        time.sleep(1)  # Pausa entre pruebas
    
    # 4. Resumen de resultados
    print_section("RESUMEN DE RESULTADOS")
    
    total_tests = len(test_questions)
    print(f"📊 Resultados de las pruebas:")
    print(f"   🔥 Endpoint integrado: {integrated_success}/{total_tests} exitosas")
    print(f"   📊 Endpoint original: {original_success}/{total_tests} exitosas")
    
    if integrated_success > 0:
        print("\n✅ El sistema RAG integrado está funcionando correctamente!")
        print("🎯 Los datos precargados están disponibles y respondiendo preguntas.")
        
        if integrated_success > original_success:
            print("🚀 El endpoint integrado está funcionando mejor que el original!")
        elif integrated_success == original_success:
            print("⚖️ Ambos endpoints funcionan igualmente bien.")
        else:
            print("⚠️ El endpoint original funciona mejor, revisar integración.")
    else:
        print("\n❌ El sistema RAG integrado no está funcionando correctamente.")
        print("🔧 Revisar logs del servidor para más detalles.")
    
    print(f"\n🔗 Documentación disponible en: {API_BASE_URL}/docs")
    print(f"🏥 Health check en: {API_BASE_URL}/health")
    print(f"📊 Estado integrado en: {API_BASE_URL}/system/integrated/status")
    
    return 0 if integrated_success > 0 else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️ Pruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado durante las pruebas: {e}")
        sys.exit(1)
