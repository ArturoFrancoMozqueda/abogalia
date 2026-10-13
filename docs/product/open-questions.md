# Preguntas para definir Abogalia

Las siguientes preguntas consolidan la sesión de definición del 12 de octubre de 2026. Las cinco primeras ya se presentaron a Arturo y están pendientes; no se interpretan opciones recomendadas como respuestas. El inventario anterior se conserva en [preguntas abiertas](../18_open_questions.md).

| ID | Categoría | Pregunta | Estado | Recomendación pendiente |
|---|---|---|---|---|
| Q-001 | Product, Business | ¿La suscripción se sostiene principalmente por operación, adquisición o ambas? | Pending | Operación útil con clientes propios más adquisición medible |
| Q-002 | Product, UX, Legal | ¿Se distingue evaluación comercial gratuita de consulta pagada? | Pending | Servicios con alcances distintos y evaluación opcional |
| Q-003 | Business, Product | ¿Se vende posicionamiento y cómo influye en los resultados? | Pending | Patrocinio identificado entre elegibles, separado del ranking orgánico |
| Q-004 | Business, Operations | ¿Qué evidencia, acceso a abogados y disposición a pagar existen? | Pending | Contrastar problemas y compra con usuarios reales |
| Q-005 | Business, Operations | ¿Qué presupuesto, equipo, dedicación y plazo existen para construcción, operación y adquisición? | Pending | Evaluar los tres presupuestos por separado |

## Decisiones posteriores por sesión

- Product y UX: profundidad de gestión de asuntos; contratación directa; entregable de consulta; persona física y empresa; cobertura geográfica y áreas; comportamiento sin oferta.
- Operations y Legal: responsable de verificación; capacidad de respuesta; urgencias; moderación; disputas; alcance de Abogalia y del profesional. **LEGAL REVIEW REQUIRED**.
- Product y Business: aceptación, pago, cancelación, no-show, devolución y liquidación; atribución y tratamiento de clientes propios; precios y límites de planes.
- Architecture, Data y Security: contextos independiente/despacho; accesos; cambio y salida de organización; agenda compartida sin exposición; revisión de conflictos; retención; IA y consentimiento.
- Architecture: aplicaciones, stack, identidad, almacenamiento, pagos, búsqueda, eventos y despliegue, mediante comparación y checkpoints aprobados.

## Respuestas registradas

| Pregunta anterior | Respuesta de Arturo | Alcance |
|---|---|---|
| Primera versión utilizable | Pide crítica desde el inicio | La primera entrega sigue pendiente; no aprueba una combinación específica |
| Cobertura de piloto | Pide mentalidad de proyecto completo | No ratifica Morelia ni decide cobertura de lanzamiento |
| Momento del cobro | Solicita investigación de la mejor opción | Recomendación discutida; no aprobada |
| Afiliación profesional | Independiente más un despacho | Aprobado; no decide permisos ni intercambio de datos |
| Monetización | Solicita análisis financiero de Doctoralia | Investigación realizada; modelo de Abogalia pendiente |
| Capacidad operativa | Autoservicio con soporte limitado | Aprobado; personas, horarios y escalamiento pendientes |

El análisis y las consecuencias están en [definición de solución](../19_solution_definition.md). Las decisiones aprobadas y propuestas se registran en [decision log](../decisions/decision-log.md).

## Preguntas derivadas de la crítica y del mapa de fricción

Estas preguntas están registradas para conversación; no se consideran respondidas por una recomendación.

| ID | Categoría | Pregunta | Estado |
|---|---|---|---|
| Q-006 | Product, UX | ¿Qué promesa debe liderar el producto? | Answered: atención clara y continua |
| Q-007 | Product, Business | ¿Quién es el comprador prioritario? | Answered: independientes y despachos pequeños |
| Q-008 | Product, Operations | ¿Qué profundidad tendrá la gestión posterior? | Answered: relación de servicio como centro |
| Q-009 | Product, Legal, Operations | ¿Qué atención y plazo promete Abogalia y qué responsabilidades corresponden al profesional? | Discussing: Arturo pide recomendación; compromisos supervisados propuestos |
| Q-010 | Product, Business, Operations | ¿Qué evidencia verificable confirmará o cambiará el propósito y qué recursos sostendrán esa promesa? | Pending |
| Q-011 | Product, Business, Legal | ¿Cómo tratar alternativas gratuitas y servicios privados? | Answered: búsqueda gratuita, condiciones de servicios y referencias institucionales pertinentes |
| Q-012 | Business, Legal | ¿El nombre Abogalia es adecuado y jurídicamente disponible para el proyecto en México? | Discussing: Arturo pregunta por cambiarlo; se recomienda explorar alternativas, sin aprobar cambio ni verificar registros |
| Q-013 | Product, UX, Legal | ¿Cómo se combinan solicitud directa y guiada, quién recibe la información y con qué autorización? | Pending: ideas derivadas de investigación competitiva |
| Q-014 | Product, Business, Legal | ¿Qué condiciones y alcance debe contener un acuerdo de servicio comparable? | Pending: formato propuesto, sin aprobar tarifas o contratación |
| Q-015 | Product, UX, Security | ¿Qué siguiente acción, documentos y actualizaciones ve el cliente, y qué permanece interno? | Pending: relación de servicio aprobada; permisos y recorrido pendientes |
| Q-016 | Product, UX, Security | ¿Se aprueban los flujos de resumen revisable y borrador editable, usando solo texto seleccionado y sin envío automático? | Answered: flujos aprobados en D-020; tratamiento por proveedor y permisos detallados pendientes |
| Q-017 | Architecture, Data, Legal | ¿Qué base de aplicación, proveedor y tratamiento de datos se utilizarán para estas dos funciones? | Partially answered: React + FastAPI aprobado; proveedor de IA y retención requieren decisión y revisión |
| Q-018 | Business, Operations | ¿Qué presupuesto y límites de consumo por cuenta y plataforma tendrá la asistencia de IA? | Pending: política de límites propuesta, importes sin aprobar |
| Q-019 | Architecture | ¿Qué stack de aplicación se utilizará? | Answered: React + FastAPI, D-025 y ADR-001; no aprueba hosting ni renderizado |
| Q-020 | Architecture, Security | ¿Identidad administrada con Supabase Auth, autenticación propia adaptada de Kova o Clerk separado? | Answered: Supabase Auth Approved, D-028; métodos, sesiones y permisos requieren diseño propio |
| Q-021 | Business, Operations | ¿Cuál es el tope mensual de servicios, separado de desarrollo y costos compartidos con Kova? | Pending: pregunta presentada; sin aprobación de gasto |
| Q-022 | Architecture, Operations | ¿Se ratifica Cloudflare para React y Fly para FastAPI con tiers Free, o una alternativa; cómo serán renderizado, releases y entornos? | Discussing: propuesta vigente Cloudflare/Fly y Supabase/Resend Free, con recursos propios; sin hosting ni gasto aprobados |
| Q-023 | Operations, Security | ¿Cómo separar Kova y Abogalia conservando conexiones de plugins/MCPs reutilizables? | Answered, D-027 Approved: posprojectsupport con espacios propios y cuenta personal existente de GitHub; configuración, alcance de conexiones y diagnóstico pendientes |
| Q-024 | Architecture | ¿Monorepo con React Router y prerenderizado, monorepo SPA con Vite, o repositorios separados? | Answered: confirmó monorepo Abogalia + React Router, D-030 Implemented en su base local; hosting y catálogo futuros pendientes |
| Q-025 | Architecture, Operations, Data | ¿Proyecto vacío abogalia en organización propia Free y us-east-1, o ubicación distinta? | Answered: D-029 Implemented; Arturo creó el proyecto y se verificaron organización, Free, us-east-1 y ACTIVE_HEALTHY; integración pendiente |

Contexto: [crítica estratégica](../20_critical_review.md) y [fricciones del proceso](../21_process_friction.md). Las decisiones aprobadas sobre afiliación y autoservicio se conservan; sus reglas operativas requieren diseño.

La refinación con cuatro respuestas explícitas está en [producto refinado](../23_refined_product.md); la evidencia pública en [hallazgos de investigación](../22_research_findings.md). Q-001 y Q-002 siguen abiertas: audiencia y búsqueda gratuita no aprueban monetización ni evaluación comercial gratuita obligatoria. Presupuesto, equipo, plazos y revisión jurídica siguen pendientes.

La [investigación de competidores e ideas](../24_competitive_research.md) incorpora las preguntas Q-013 a Q-015 para próximos checkpoints. La investigación no autoriza implementar funciones ni cambia estados aprobados.

Arturo aprobó el alcance de dos funciones de IA en D-019. Las preguntas Q-016 a Q-018 y el [checkpoint de asistencia](../checkpoints/ai-assistance.md) distinguen esa selección de las decisiones necesarias para programarlas. No se vuelve a pedir aprobación de qué funciones incluir.

Arturo aprobó los flujos en D-020 y pidió incorporar lecciones de Kova en D-021. Se preparó la [comparación basada en Kova](../25_kova_lessons_and_setup_order.md) y se presentaron Q-019 a Q-021. Q-021 determina el techo global de planificación; Q-018 deberá asignar cuotas y reserva para IA dentro de ese techo. No se consideran decididas por una recomendación.

Arturo aplazó procesamiento documental con IA en D-022 y confirmó suite propia en D-023. La [comparación de servicios y tiers](../26_services_and_tiers.md) incorpora tarifas oficiales actuales, escenarios de entornos separados y condiciones para cambiar de plan. Q-019 a Q-021 continúan pendientes: investigación y suite independiente no equivalen a elección de stack o presupuesto.

La solicitud de una suite escalable produjo el [checkpoint de base técnica](../checkpoints/platform-foundation.md), D-024. Se propone React Router en Workers con Supabase Auth y PostgreSQL, estructura por módulos y crecimiento según mediciones. Correo de producción y presupuesto se distinguen de una opción beta por validar. Q-020 y Q-021 siguen pendientes; no se interpreta la solicitud de recomendación como aprobación de proveedores o gasto.

Actualización: Arturo aprobó React + FastAPI en D-025. Q-019 queda respondida; la propuesta anterior se conserva como contexto. El checkpoint se actualiza para backend Python separado y presupuesto de cómputo, D-026. Q-020, Q-021 y Q-022 distinguen decisiones pendientes de servicios, identidad y gasto.

Primer bloque de preparación: organización Supabase Abogalia Free creada y acceso directo comprobado; Q-024, Q-020 y Q-025 presentadas juntas para estructura/renderizado, proveedor Auth y región de proyecto. [Checkpoint concreto](../checkpoints/repository-and-empty-database.md). Las preguntas no aprueban roles, esquema ni hosting pagado.
