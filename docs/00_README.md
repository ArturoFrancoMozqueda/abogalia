# Legalia — documentación maestra

Estado vigente, tareas y dependencias: [plan por agentes](27_development_plan_agents.md).
La visión funcional siguiente describe el producto objetivo, no capacidades ya
publicadas. Abogalia es el nombre histórico; Legalia es el nombre aprobado.
Los checkpoints distinguen aprobación de implementación y aceptación real.


Abogalia es una plataforma digital para conectar personas con abogados verificados y proporcionar a abogados independientes y despachos las herramientas necesarias para gestionar prospectos, consultas, clientes y operación comercial.

El proyecto no se plantea como un producto mínimo o temporal. La intención es diseñar y construir una plataforma completa, modular, escalable y preparada para evolucionar hacia un ecosistema legal digital integral.

## Visión general

Abogalia combinará tres capacidades principales:

1. **Marketplace legal**
   - Descubrimiento de abogados.
   - Clasificación de necesidades legales.
   - Matching entre usuarios y profesionales.
   - Reserva y pago de consultas.
   - Reputación y confianza transaccional.

2. **SaaS para abogados y despachos**
   - Gestión de prospectos.
   - Agenda y disponibilidad.
   - Intake estructurado.
   - Gestión de consultas.
   - Seguimiento comercial.
   - Administración de clientes.
   - Métricas y operación de equipos.

3. **Plataforma de datos**
   - Analítica de producto.
   - Inteligencia de matching.
   - Medición de conversión.
   - Calidad de datos.
   - Modelos de comportamiento.
   - Observabilidad operativa.
   - Futuras capacidades de inteligencia artificial.

## Principios del proyecto

- Diseñar para el producto completo, aunque la entrega se realice por fases.
- Evitar decisiones técnicas prematuras.
- Construir mediante dominios y módulos desacoplados.
- Priorizar confianza, privacidad y trazabilidad.
- No confundir directorio con marketplace.
- No confundir marketplace con SaaS.
- No confundir automatización con asesoría legal.
- Instrumentar los datos desde el inicio.
- Diseñar cada flujo con criterios jurídicos, operativos y comerciales.
- Mantener al usuario y al abogado en control de las decisiones relevantes.

## Documentos

La dirección de producto refinada y sus estados de aprobación están en `23_refined_product.md`. Las revisiones previas conservan contexto; una recomendación documentada no equivale a decisión aprobada.

| Documento | Propósito |
|---|---|
| `01_product_vision.md` | Visión, misión, posicionamiento y alcance del producto |
| `02_market_strategy.md` | Mercado objetivo, competencia y estrategia de entrada |
| `03_users_and_personas.md` | Usuarios, abogados, despachos y necesidades |
| `04_value_proposition.md` | Propuesta de valor y diferenciadores |
| `05_product_scope.md` | Alcance funcional completo de la plataforma |
| `06_user_journeys.md` | Flujos de usuarios, abogados y operaciones |
| `07_business_model.md` | Monetización, pricing y unidad económica |
| `08_marketplace_strategy.md` | Liquidez, matching, confianza y reputación |
| `09_operating_model.md` | Operación, soporte, verificación y moderación |
| `10_data_architecture.md` | Dominios, entidades, gobierno y ciclo de vida de datos |
| `11_analytics_strategy.md` | Eventos, métricas, modelos analíticos y dashboards |
| `12_security_privacy_risk.md` | Seguridad, privacidad, riesgo y cumplimiento |
| `13_ai_strategy.md` | Uso responsable de IA en la plataforma |
| `14_technical_architecture_brainstorm.md` | Preguntas y opciones para definir el stack |
| `15_delivery_roadmap.md` | Construcción por capacidades y etapas |
| `16_product_metrics.md` | North Star Metric, KPIs y métricas operativas |
| `17_risk_register.md` | Riesgos de negocio, producto, datos y tecnología |
| `18_open_questions.md` | Decisiones pendientes y sesiones de trabajo |
| `19_solution_definition.md` | Análisis crítico y definición propuesta de solución, pendiente de aprobación |
| `20_critical_review.md` | Crítica de mercado, producto, economía, operación, datos y tecnología |
| `21_process_friction.md` | Fricciones del recorrido legal y de la experiencia propuesta para Abogalia |
| `22_research_findings.md` | Evidencia pública mexicana, competencia y límites de interpretación |
| `23_refined_product.md` | Propuesta refinada con decisiones aprobadas y modelo de respuesta recomendado |
| `24_competitive_research.md` | Abogalia Argentina, competencia, modelos comerciales e ideas ligadas a fricción |
| `25_kova_lessons_and_setup_order.md` | Lecciones verificadas de Kova, opciones de base técnica y orden de servicios |
| `26_services_and_tiers.md` | Tarifas oficiales verificadas, tiers propuestos y escenarios de una suite independiente |
| `27_development_plan_agents.md` | Plan asignable por agentes, dependencias, criterios y protección de secretos |
| `operations/agent-task-template.md` | Orden de trabajo y reporte sanitizado para cada agente |
| `checkpoints/ai-assistance.md` | Flujos aprobados de las dos funciones de IA y decisiones técnicas pendientes |
| `checkpoints/platform-foundation.md` | Comparación anterior de suite administrada y escenarios con Vercel |
| `checkpoints/platform-foundation-low-cost.md` | Propuesta vigente de inicio pequeño: Cloudflare/Fly, Supabase/Resend Free y aislamiento de Kova |
| `checkpoints/repository-and-empty-database.md` | Primer bloque de configuración; estructura, Auth y región por elegir |
| `operations/service-registry.md` | Recursos e identificadores reales de Abogalia, sin secretos |
| `decisions/decision-log.md` | Decisiones expresadas por Arturo y propuestas con estado explícito |
| `decisions/ADR-001-react-fastapi.md` | Elección aprobada de React y FastAPI, alcance y consecuencias |
| `decisions/ADR-002-administration-and-product-isolation.md` | Administración con posprojectsupport y espacios propios; configuración pendiente |
| `decisions/ADR-003-supabase-auth.md` | Proveedor de identidad aprobado; integración y flujos pendientes |
| `decisions/ADR-004-empty-supabase-project.md` | Proyecto vacío propio Free/us-east-1 creado y verificado; sin integración de aplicación |
| `decisions/ADR-005-monorepo-and-rendering.md` | Monorepo y prerenderizado implementados en su base local |
| `operations/local-foundation-verification.md` | Evidencia de build y conexión real navegador/API; límites de la entrega |
| `product/open-questions.md` | Preguntas consolidadas y respuestas de las sesiones de definición |

## Decisión ejecutiva actual

Abogalia debe construirse como:

> Una plataforma de intake, descubrimiento, matching, reserva y gestión de servicios legales con abogados verificados, acompañada de un sistema operativo comercial y administrativo para abogados y despachos.

El proyecto debe evolucionar por capacidades, no como un prototipo desechable.
