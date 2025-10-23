"""
Datos precargados de políticas de RRHH para el sistema RAG
Incluye políticas completas de Google y otras empresas tech como ejemplos
"""

from typing import List, Dict, Any
from datetime import datetime

# ============================================================================
# POLÍTICAS DE BENEFICIOS
# ============================================================================

BENEFITS_POLICIES = [
    {
        "title": "Política de Beneficios de Salud - Google",
        "category": "beneficios",
        "department": "rrhh",
        "content": """
**POLÍTICA DE BENEFICIOS DE SALUD - GOOGLE**

**1. COBERTURA MÉDICA INTEGRAL**
Google proporciona cobertura médica completa para todos los empleados de tiempo completo y sus familias:

• Seguro médico con cobertura del 100% de primas para empleados
• Cobertura familiar disponible con contribución del empleado
• Red nacional de proveedores médicos de primera clase
• Cobertura internacional para viajes de trabajo

**2. SERVICIOS PREVENTIVOS**
• Exámenes médicos anuales gratuitos
• Vacunas y screenings preventivos
• Programas de bienestar en el sitio
• Clínicas médicas en campus principales

**3. SALUD MENTAL Y BIENESTAR**
• Cobertura completa de salud mental
• Programas de asistencia al empleado (EAP)
• Sesiones de terapia y counseling
• Aplicaciones de mindfulness y meditación

**4. BENEFICIOS ADICIONALES**
• Seguro dental y de visión incluido
• Cobertura de medicamentos recetados
• Programas de fertilidad y maternidad
• Cuidado de dependientes y eldercare

**5. PROCESO DE INSCRIPCIÓN**
• Período de inscripción abierta anual en noviembre
• Cambios de vida permiten inscripción especial
• Portal online para gestión de beneficios
• Soporte dedicado de HR para consultas

**Contacto:** benefits@google.com | Teléfono: 1-800-GOOGLE-HR
**Última actualización:** Enero 2024
        """,
        "metadata": {
            "version": "2024.1",
            "author": "Google HR Team",
            "effective_date": "2024-01-01",
            "review_date": "2024-12-31"
        }
    },
    {
        "title": "Plan de Jubilación 401(k) - Google",
        "category": "beneficios", 
        "department": "rrhh",
        "content": """
**PLAN DE JUBILACIÓN 401(k) - GOOGLE**

**1. ELEGIBILIDAD**
• Todos los empleados de tiempo completo son elegibles inmediatamente
• Empleados de medio tiempo elegibles después de 6 meses
• No hay período de espera para participación

**2. CONTRIBUCIONES**
• Contribución del empleado: hasta 100% del salario (límites del IRS aplican)
• Matching de Google: 50% de las primeras 6% de contribución
• Contribución máxima de matching: $3,000 anuales
• Vesting inmediato del 100% en contribuciones del empleado

**3. OPCIONES DE INVERSIÓN**
• Más de 20 fondos mutuos diversificados
• Fondos índice de bajo costo disponibles
• Opción de inversión en acciones de Google (GOOG)
• Servicios de asesoría financiera gratuitos

**4. CARACTERÍSTICAS ESPECIALES**
• Préstamos del 401(k) disponibles
• Retiros por dificultades económicas
• Rollover automático de planes anteriores
• Calculadoras de jubilación online

**5. GESTIÓN DE CUENTA**
• Portal web 24/7 para gestión de cuenta
• App móvil para monitoreo
• Estados de cuenta trimestrales
• Alertas automáticas de balance

**Proveedor:** Fidelity Investments
**Contacto:** 401k@google.com | 1-800-FIDELITY
**Última actualización:** Enero 2024
        """,
        "metadata": {
            "version": "2024.1",
            "author": "Google Benefits Team",
            "effective_date": "2024-01-01"
        }
    }
]

# ============================================================================
# POLÍTICAS DE VACACIONES Y TIEMPO LIBRE
# ============================================================================

VACATION_POLICIES = [
    {
        "title": "Política de Tiempo Libre Flexible - Google",
        "category": "vacaciones",
        "department": "rrhh",
        "content": """
**POLÍTICA DE TIEMPO LIBRE FLEXIBLE - GOOGLE**

**1. FILOSOFÍA**
Google cree en dar a los empleados la flexibilidad para gestionar su tiempo de manera que les permita ser más productivos y mantener un equilibrio saludable entre trabajo y vida personal.

**2. TIEMPO LIBRE ILIMITADO**
• No hay límite específico de días de vacaciones
• Los empleados pueden tomar el tiempo que necesiten
• Se espera que coordinen con sus equipos y managers
• Mínimo recomendado: 3 semanas al año

**3. PROCESO DE APROBACIÓN**
• Solicitar con al menos 2 semanas de anticipación
• Aprobación del manager directo requerida
• Para ausencias de más de 2 semanas, aprobación de HR
• Usar el sistema interno de gestión de tiempo

**4. DÍAS FESTIVOS**
• Google observa 11 días festivos nacionales
• 2 días flotantes adicionales por año
• Días culturales y religiosos respetados
• Oficinas internacionales siguen calendarios locales

**5. TIEMPO POR ENFERMEDAD**
• Tiempo ilimitado por enfermedad
• No requiere certificado médico para ausencias cortas
• Licencia médica extendida disponible
• Apoyo de HR para casos complejos

**6. LICENCIAS ESPECIALES**
• Licencia parental: 12-18 semanas pagadas
• Licencia por duelo: hasta 2 semanas
• Licencia por servicio militar: según ley federal
• Licencia sabática: disponible para empleados senior

**7. MEJORES PRÁCTICAS**
• Planificar vacaciones con anticipación
• Asegurar cobertura de responsabilidades
• Desconectarse completamente durante vacaciones
• Comunicar claramente fechas de ausencia

**Contacto:** timeoff@google.com
**Última actualización:** Enero 2024
        """,
        "metadata": {
            "version": "2024.1",
            "author": "Google People Operations",
            "effective_date": "2024-01-01"
        }
    }
]

# ============================================================================
# POLÍTICAS DE TRABAJO REMOTO
# ============================================================================

REMOTE_WORK_POLICIES = [
    {
        "title": "Política de Trabajo Híbrido - Google",
        "category": "trabajo_remoto",
        "department": "rrhh",
        "content": """
**POLÍTICA DE TRABAJO HÍBRIDO - GOOGLE**

**1. MODELO HÍBRIDO ESTÁNDAR**
Google ha adoptado un modelo de trabajo híbrido como estándar post-pandemia:
• 3 días por semana en la oficina (martes, miércoles, jueves)
• 2 días de trabajo remoto (lunes y viernes típicamente)
• Flexibilidad para ajustar según necesidades del equipo

**2. OPCIONES DISPONIBLES**
• **Híbrido Estándar:** 3 días oficina, 2 días remoto
• **Remoto Completo:** Aprobación especial requerida
• **Presencial Completo:** Disponible para quienes prefieren oficina
• **Flexible:** Arreglos personalizados según rol y necesidades

**3. REQUISITOS PARA TRABAJO REMOTO**
• Espacio de trabajo adecuado en casa
• Conexión a internet confiable (mínimo 25 Mbps)
• Participación en reuniones de equipo regulares
• Disponibilidad durante horas core (10 AM - 3 PM zona local)

**4. EQUIPAMIENTO Y SOPORTE**
• Laptop y monitor adicional proporcionados
• Estipendio de $1,000 para setup de oficina en casa
• Silla ergonómica y accesorios de oficina
• Soporte técnico 24/7 para empleados remotos

**5. COMUNICACIÓN Y COLABORACIÓN**
• Uso obligatorio de Google Workspace
• Reuniones híbridas con tecnología de video avanzada
• Documentación en tiempo real en Google Docs
• Slack para comunicación informal

**6. EXPECTATIVAS DE PRODUCTIVIDAD**
• Mantener o mejorar niveles de productividad
• Participar activamente en reuniones virtuales
• Cumplir con deadlines y objetivos del equipo
• Estar disponible durante horas de trabajo acordadas

**7. PROCESO DE SOLICITUD**
• Discutir con manager directo
• Completar formulario de trabajo remoto
• Aprobación de HR para casos especiales
• Revisión trimestral de arreglos

**8. POLÍTICAS DE VIAJE**
• Empleados remotos deben visitar oficina mensualmente
• Gastos de viaje cubiertos por la empresa
• Hoteling disponible para empleados remotos
• Eventos de equipo trimestrales obligatorios

**Contacto:** remotework@google.com
**Última actualización:** Enero 2024
        """,
        "metadata": {
            "version": "2024.1",
            "author": "Google Workplace Team",
            "effective_date": "2024-01-01"
        }
    }
]

# ============================================================================
# POLÍTICAS DE DESARROLLO PROFESIONAL
# ============================================================================

DEVELOPMENT_POLICIES = [
    {
        "title": "Programa de Desarrollo Profesional - Google",
        "category": "desarrollo",
        "department": "rrhh",
        "content": """
**PROGRAMA DE DESARROLLO PROFESIONAL - GOOGLE**

**1. FILOSOFÍA DE DESARROLLO**
Google está comprometido con el crecimiento continuo de sus empleados, proporcionando oportunidades para desarrollar habilidades técnicas y de liderazgo.

**2. TIEMPO PARA INNOVACIÓN (20% TIME)**
• 20% del tiempo de trabajo dedicado a proyectos personales
• Proyectos deben alinearse con objetivos de Google
• Presentación trimestral de avances requerida
• Muchos productos de Google nacieron del 20% time

**3. PRESUPUESTO DE CAPACITACIÓN**
• $3,000 anuales por empleado para desarrollo
• Cubre cursos, certificaciones, conferencias
• Libros y materiales de aprendizaje incluidos
• Proceso de aprobación simplificado

**4. PROGRAMAS INTERNOS**
• **g2g (Googler-to-Googler):** Enseñanza entre empleados
• **BOLD Immersion:** Programa de liderazgo
• **Engineering Residency:** Para nuevos graduados
• **Manager Training:** Desarrollo de habilidades gerenciales

**5. EDUCACIÓN EXTERNA**
• Partnerships con universidades top
• MBA sponsorship para empleados calificados
• Certificaciones técnicas (AWS, GCP, etc.)
• Conferencias industriales (I/O, WWDC, etc.)

**6. MENTORSHIP Y COACHING**
• Programa formal de mentorship
• Coaching ejecutivo para managers
• Peer mentoring circles
• Reverse mentoring para diversidad

**7. ROTACIONES INTERNAS**
• Oportunidades de rotación entre equipos
• Programa de intercambio internacional
• Shadowing de roles de interés
• Proyectos cross-funcionales

**8. EVALUACIÓN Y SEGUIMIENTO**
• Planes de desarrollo individual (IDP)
• Revisiones de progreso trimestrales
• 360-degree feedback anual
• Métricas de crecimiento profesional

**9. RECURSOS DE APRENDIZAJE**
• **Grow with Google:** Plataforma interna de cursos
• Biblioteca técnica y de negocios
• Subscripciones a plataformas online
• Workshops y seminarios semanales

**10. RECONOCIMIENTO Y AVANCE**
• Programa de promociones transparente
• Peer nomination awards
• Publicación interna de logros
• Oportunidades de speaking en conferencias

**Contacto:** learning@google.com
**Última actualización:** Enero 2024
        """,
        "metadata": {
            "version": "2024.1",
            "author": "Google Learning & Development",
            "effective_date": "2024-01-01"
        }
    }
]

# ============================================================================
# POLÍTICAS DE DIVERSIDAD E INCLUSIÓN
# ============================================================================

DIVERSITY_POLICIES = [
    {
        "title": "Política de Diversidad e Inclusión - Google",
        "category": "diversidad",
        "department": "rrhh",
        "content": """
**POLÍTICA DE DIVERSIDAD E INCLUSIÓN - GOOGLE**

**1. COMPROMISO CON LA DIVERSIDAD**
Google se compromete a crear un ambiente de trabajo inclusivo donde todos los empleados puedan prosperar, independientemente de su origen, identidad o experiencia.

**2. PRINCIPIOS FUNDAMENTALES**
• **Pertenencia:** Todos se sienten valorados y respetados
• **Equidad:** Oportunidades justas para todos
• **Representación:** Diversidad en todos los niveles
• **Inclusión:** Voces diversas en la toma de decisiones

**3. GRUPOS DE RECURSOS DE EMPLEADOS (ERGs)**
• **Black Googler Network (BGN)**
• **Latinx@Google**
• **Women@Google**
• **LGBTQ+ Googlers and Allies**
• **Veterans at Google**
• **Disability Alliance**
• **Asian Pacific Islander Googlers**

**4. INICIATIVAS DE CONTRATACIÓN**
• Partnerships con universidades HBCU
• Programas de internships para grupos subrepresentados
• Eliminación de sesgos en procesos de entrevista
• Metas específicas de diversidad por equipo

**5. DESARROLLO Y RETENCIÓN**
• Programas de sponsorship para minorías
• Círculos de liderazgo inclusivo
• Capacitación en unconscious bias obligatoria
• Métricas de inclusión en evaluaciones de managers

**6. POLÍTICAS ANTI-DISCRIMINACIÓN**
• Tolerancia cero para discriminación y acoso
• Múltiples canales para reportar incidentes
• Investigaciones confidenciales y justas
• Protección contra represalias

**7. ACOMODACIONES Y ACCESIBILIDAD**
• Acomodaciones razonables para discapacidades
• Tecnología asistiva disponible
• Espacios de trabajo accesibles
• Políticas flexibles para necesidades individuales

**8. CELEBRACIÓN DE LA DIVERSIDAD**
• Meses de herencia cultural reconocidos
• Eventos y celebraciones inclusivas
• Oradores diversos en eventos corporativos
• Contenido educativo sobre diferentes culturas

**9. MEDICIÓN Y TRANSPARENCIA**
• Reportes anuales de diversidad publicados
• Métricas de progreso compartidas internamente
• Auditorías regulares de equidad salarial
• Feedback continuo de empleados

**10. RECURSOS Y SOPORTE**
• **Employee Resource Groups:** Apoyo y networking
• **Inclusion Training:** Capacitación continua
• **Bias Interruption:** Herramientas para reducir sesgos
• **Ally Programs:** Programas para aliados

**Contacto:** diversity@google.com
**Última actualización:** Enero 2024
        """,
        "metadata": {
            "version": "2024.1",
            "author": "Google Diversity & Inclusion Team",
            "effective_date": "2024-01-01"
        }
    }
]

# ============================================================================
# POLÍTICAS DE COMPENSACIÓN
# ============================================================================

COMPENSATION_POLICIES = [
    {
        "title": "Estructura de Compensación - Google",
        "category": "compensacion",
        "department": "rrhh",
        "content": """
**ESTRUCTURA DE COMPENSACIÓN - GOOGLE**

**1. FILOSOFÍA DE COMPENSACIÓN**
Google busca atraer, retener y motivar el mejor talento a través de una compensación competitiva, equitativa y basada en el desempeño.

**2. COMPONENTES DE COMPENSACIÓN**
• **Salario Base:** Competitivo con el mercado
• **Bonus Anual:** Basado en desempeño individual y de la empresa
• **Equity (RSUs):** Restricted Stock Units de Google
• **Beneficios:** Paquete integral de beneficios

**3. BANDAS SALARIALES**
• Estructura transparente de niveles (L3-L11+)
• Rangos salariales definidos por nivel y ubicación
• Progresión clara entre niveles
• Ajustes anuales por costo de vida

**4. EVALUACIÓN DE DESEMPEÑO**
• **Perf:** Evaluación semestral de desempeño
• **Impact:** Medición del impacto en objetivos
• **Collaboration:** Evaluación de trabajo en equipo
• **Innovation:** Contribuciones creativas e innovadoras

**5. EQUITY PROGRAM**
• RSUs otorgadas en contratación y promociones
• Vesting schedule de 4 años (25% anual)
• Refresher grants anuales basadas en desempeño
• ESPP (Employee Stock Purchase Plan) disponible

**6. BONUS STRUCTURE**
• Target bonus como % del salario base
• Multiplicador basado en desempeño (0.8x - 1.4x)
• Bonus de equipo por logros excepcionales
• Spot bonuses para reconocimiento inmediato

**7. EQUIDAD SALARIAL**
• Auditorías regulares de equidad salarial
• Ajustes proactivos para cerrar brechas
• Transparencia en criterios de compensación
• Proceso de apelación para revisiones salariales

**8. BENEFICIOS ADICIONALES**
• Seguro de vida y discapacidad
• Programas de bienestar financiero
• Descuentos en productos Google
• Subsidios de transporte y comida

**9. PROCESO DE REVISIÓN**
• Revisiones salariales anuales en marzo
• Promociones evaluadas semestralmente
• Feedback continuo de managers
• Calibración cross-team para equidad

**10. RECURSOS**
• **Compensation Calculator:** Herramienta interna
• **Career Ladder:** Progresión clara de niveles
• **Market Data:** Benchmarking externo regular
• **Total Rewards Statement:** Resumen anual personalizado

**Contacto:** compensation@google.com
**Última actualización:** Enero 2024
        """,
        "metadata": {
            "version": "2024.1",
            "author": "Google Compensation Team",
            "effective_date": "2024-01-01"
        }
    }
]

# ============================================================================
# POLÍTICAS DE ÉTICA Y CUMPLIMIENTO
# ============================================================================

ETHICS_POLICIES = [
    {
        "title": "Código de Conducta - Google",
        "category": "etica",
        "department": "legal",
        "content": """
**CÓDIGO DE CONDUCTA - GOOGLE**

**1. PRINCIPIOS FUNDAMENTALES**
"Don't be evil" - Este principio guía todas nuestras acciones y decisiones en Google.

**2. INTEGRIDAD Y HONESTIDAD**
• Actuar con integridad en todas las interacciones
• Ser honesto y transparente en comunicaciones
• Reportar violaciones éticas sin temor a represalias
• Mantener la confianza de usuarios y partners

**3. CONFLICTOS DE INTERÉS**
• Evitar situaciones que comprometan el juicio profesional
• Divulgar potenciales conflictos a management
• No usar posición para beneficio personal
• Políticas específicas para inversiones y trabajos externos

**4. CONFIDENCIALIDAD Y PRIVACIDAD**
• Proteger información confidencial de Google
• Respetar la privacidad de usuarios y empleados
• Uso apropiado de datos y sistemas internos
• Cumplimiento con regulaciones de privacidad (GDPR, CCPA)

**5. ANTI-CORRUPCIÓN**
• Prohibición estricta de sobornos y kickbacks
• Regalos y entretenimiento dentro de límites apropiados
• Transparencia en relaciones con gobiernos
• Cumplimiento con leyes anti-corrupción globales

**6. COMPETENCIA JUSTA**
• Competir de manera justa y legal
• Respetar derechos de propiedad intelectual
• No participar en prácticas anti-competitivas
• Cumplimiento con leyes antimonopolio

**7. DIVERSIDAD E INCLUSIÓN**
• Ambiente libre de discriminación y acoso
• Respeto por todas las personas independientemente de diferencias
• Oportunidades equitativas para todos
• Reporte de comportamientos inapropiados

**8. SEGURIDAD Y PROTECCIÓN**
• Mantener ambiente de trabajo seguro
• Proteger activos físicos e intelectuales de Google
• Cumplir con protocolos de seguridad
• Reportar incidentes de seguridad inmediatamente

**9. RESPONSABILIDAD SOCIAL**
• Contribuir positivamente a las comunidades
• Consideraciones ambientales en decisiones
• Uso responsable de recursos
• Apoyo a causas benéficas apropiadas

**10. CUMPLIMIENTO Y REPORTE**
• **Ethics Hotline:** 1-877-GOOGLE-1
• **Online Reporting:** ethics.google.com
• **Open Door Policy:** Comunicación directa con management
• **Investigation Process:** Proceso justo y confidencial

**11. CONSECUENCIAS**
• Violaciones pueden resultar en acción disciplinaria
• Desde coaching hasta terminación según severidad
• Proceso justo con oportunidad de respuesta
• Protección contra represalias por reportes de buena fe

**Contacto:** ethics@google.com
**Última actualización:** Enero 2024
        """,
        "metadata": {
            "version": "2024.1",
            "author": "Google Legal & Ethics Team",
            "effective_date": "2024-01-01"
        }
    }
]

# ============================================================================
# CONSOLIDACIÓN DE TODOS LOS DATOS
# ============================================================================

def get_all_preloaded_policies() -> List[Dict[str, Any]]:
    """Retorna todas las políticas precargadas"""
    all_policies = []
    all_policies.extend(BENEFITS_POLICIES)
    all_policies.extend(VACATION_POLICIES)
    all_policies.extend(REMOTE_WORK_POLICIES)
    all_policies.extend(DEVELOPMENT_POLICIES)
    all_policies.extend(DIVERSITY_POLICIES)
    all_policies.extend(COMPENSATION_POLICIES)
    all_policies.extend(ETHICS_POLICIES)
    
    # Agregar timestamps y IDs únicos
    for i, policy in enumerate(all_policies):
        policy['id'] = i + 1
        policy['created_at'] = datetime.now()
        if 'metadata' not in policy:
            policy['metadata'] = {}
        policy['metadata']['preloaded'] = True
        policy['metadata']['source'] = 'system_default'
    
    return all_policies

def get_policies_by_category(category: str) -> List[Dict[str, Any]]:
    """Retorna políticas filtradas por categoría"""
    all_policies = get_all_preloaded_policies()
    return [policy for policy in all_policies if policy['category'] == category]

def get_policies_by_department(department: str) -> List[Dict[str, Any]]:
    """Retorna políticas filtradas por departamento"""
    all_policies = get_all_preloaded_policies()
    return [policy for policy in all_policies if policy['department'] == department]

def get_policy_categories() -> List[str]:
    """Retorna todas las categorías disponibles"""
    return ['beneficios', 'vacaciones', 'trabajo_remoto', 'desarrollo', 'diversidad', 'compensacion', 'etica']

def get_policy_departments() -> List[str]:
    """Retorna todos los departamentos disponibles"""
    return ['rrhh', 'legal', 'it', 'finanzas']

# ============================================================================
# PREGUNTAS FRECUENTES Y RESPUESTAS PREDEFINIDAS
# ============================================================================

FAQ_DATA = [
    {
        "question": "¿Cuántos días de vacaciones tengo?",
        "answer": "Google tiene una política de tiempo libre flexible sin límite específico de días. Se recomienda un mínimo de 3 semanas al año.",
        "category": "vacaciones",
        "keywords": ["vacaciones", "días libres", "tiempo libre"]
    },
    {
        "question": "¿Cómo funciona el trabajo remoto?",
        "answer": "Google usa un modelo híbrido: 3 días en oficina, 2 días remotos. También hay opciones de trabajo remoto completo con aprobación especial.",
        "category": "trabajo_remoto",
        "keywords": ["remoto", "híbrido", "casa", "oficina"]
    },
    {
        "question": "¿Qué beneficios de salud tengo?",
        "answer": "Google ofrece cobertura médica completa (100% de primas), seguro dental y de visión, programas de bienestar y clínicas en campus.",
        "category": "beneficios",
        "keywords": ["salud", "médico", "seguro", "beneficios"]
    },
    {
        "question": "¿Cómo funciona el 401k?",
        "answer": "Google ofrece matching del 50% en las primeras 6% de contribución, con vesting inmediato y más de 20 opciones de inversión.",
        "category": "beneficios",
        "keywords": ["401k", "jubilación", "retirement", "matching"]
    },
    {
        "question": "¿Qué presupuesto tengo para capacitación?",
        "answer": "Cada empleado tiene $3,000 anuales para desarrollo profesional, cubriendo cursos, certificaciones y conferencias.",
        "category": "desarrollo",
        "keywords": ["capacitación", "desarrollo", "presupuesto", "cursos"]
    }
]

def get_faq_data() -> List[Dict[str, Any]]:
    """Retorna datos de preguntas frecuentes"""
    return FAQ_DATA

if __name__ == "__main__":
    # Ejemplo de uso
    policies = get_all_preloaded_policies()
    print(f"Total de políticas precargadas: {len(policies)}")
    
    for category in get_policy_categories():
        category_policies = get_policies_by_category(category)
        print(f"Categoría '{category}': {len(category_policies)} políticas")
