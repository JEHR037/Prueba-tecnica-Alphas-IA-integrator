#!/usr/bin/env python3
"""
Script de prueba simple para el sistema RAG integrado
"""

import requests
import json
import time

# URL base de la API
API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """Prueba el health check básico"""
    print("\n=== HEALTH CHECK BASICO ===")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"ERROR: Health check fallo: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR conectando a la API: {e}")
        print("SOLUCION: Asegurate de que la API este ejecutandose en http://localhost:8000")
        return False

def test_integrated_question(question: str):
    """Prueba una pregunta con el endpoint integrado"""
    print(f"\n--- Probando pregunta: '{question}' ---")
    
    try:
        data = {
            "question": question,
            "department": "rrhh",
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
            answer = result.get('answer', 'Sin respuesta')
            confidence = result.get('confidence', 0)
            sources_count = len(result.get('sources', []))
            
            print(f"EXITO: Respuesta recibida")
            print(f"Confianza: {confidence:.2f}")
            print(f"Fuentes: {sources_count}")
            print(f"Respuesta: {answer[:150]}...")
            
            return True
        else:
            print(f"ERROR: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Detalle: {error_data.get('detail', 'Sin detalles')}")
            except:
                print(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR: {e}")
        return False

def test_system_status():
    """Prueba el estado del sistema"""
    print("\n=== ESTADO DEL SISTEMA INTEGRADO ===")
    
    try:
        response = requests.get(f"{API_BASE_URL}/system/integrated/status", timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            system_info = data.get("system_info", {})
            
            print(f"Estado: {status}")
            print(f"Sistema listo: {system_info.get('system_ready', False)}")
            print(f"Inicializado: {system_info.get('initialized', False)}")
            
            stats = system_info.get('statistics', {})
            print(f"Documentos cargados: {stats.get('documents_loaded', 0)}")
            print(f"Consultas procesadas: {stats.get('queries_processed', 0)}")
            
            return system_info.get('system_ready', False)
        else:
            print(f"ERROR: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("PRUEBAS DEL SISTEMA RAG INTEGRADO")
    print("=" * 50)
    
    # 1. Health check
    if not test_health_check():
        print("\nERROR: Health check fallo. Deteniendo pruebas.")
        return 1
    
    # 2. Estado del sistema
    print("\nEsperando inicializacion del sistema...")
    time.sleep(3)
    
    system_ready = test_system_status()
    if not system_ready:
        print("\nADVERTENCIA: Sistema no esta listo, pero continuando...")
    
    # 3. Pruebas de preguntas
    print("\n=== PRUEBAS DE PREGUNTAS ===")
    
    questions = [
        "¿Cuales son los beneficios de salud disponibles?",
        "¿Como funciona la politica de vacaciones?",
        "¿Puedo trabajar desde casa?"
    ]
    
    success_count = 0
    
    for i, question in enumerate(questions, 1):
        print(f"\nPREGUNTA {i}:")
        if test_integrated_question(question):
            success_count += 1
        time.sleep(1)
    
    # 4. Resumen
    print(f"\n=== RESUMEN ===")
    print(f"Pruebas exitosas: {success_count}/{len(questions)}")
    
    if success_count > 0:
        print("EXITO: El sistema RAG integrado esta funcionando!")
        print("Los datos precargados estan disponibles.")
    else:
        print("ERROR: El sistema RAG integrado no funciona correctamente.")
        print("Revisar logs del servidor para mas detalles.")
    
    print(f"\nDocumentacion: {API_BASE_URL}/docs")
    print(f"Health check: {API_BASE_URL}/health")
    
    return 0 if success_count > 0 else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nPruebas interrumpidas por el usuario")
        exit(1)
    except Exception as e:
        print(f"\n\nError durante las pruebas: {e}")
        exit(1)
