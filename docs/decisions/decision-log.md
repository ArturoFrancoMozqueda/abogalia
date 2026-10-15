# Registro de decisiones de Abogalia

Este registro distingue instrucciones y decisiones de Arturo de propuestas en discusión. Approved no significa Implemented. Fecha de la sesión: 2026-10-12.

| ID | Decisión | Estado | Fecha | ADR |
|---|---|---|---|---|
| D-001 | Diseñar el proyecto completo con entregas progresivas y capacidades permanentes | Approved | 2026-10-12 | No aplica a instrucción de producto |
| D-002 | Ejercer crítica desde el inicio y contrastar supuestos antes de consolidarlos | Approved | 2026-10-12 | No aplica a método de trabajo |
| D-003 | Permitir práctica independiente y pertenencia a un despacho por abogado | Approved | 2026-10-12 | Pendiente del diseño de organizaciones |
| D-004 | Modelo operativo de autoservicio con soporte limitado; procesos y responsables aún pendientes | Approved | 2026-10-12 | Pendiente del diseño operativo |
| D-005 | Mantener aprobación de checkpoint antes de implementar capacidades importantes | Approved | 2026-10-12 | No aplica a método de trabajo |
| D-006 | Plataforma para encontrar, contratar y seguir servicios conectada a operación profesional | Proposed | 2026-10-12 | Pendiente de definición de producto |
| D-007 | Revisar compatibilidad y conflicto antes de cobrar y confirmar la primera consulta | Discussing | 2026-10-12 | Pendiente de reservas y pagos |
| D-008 | Suscripción por operación como hipótesis económica principal; comisiones aún sin aprobar | Proposed | 2026-10-12 | Pendiente de monetización |
| D-009 | Separar evaluación comercial breve, consulta profesional y servicio posterior | Proposed | 2026-10-12 | Pendiente de servicios |
| D-010 | Patrocinio identificado sin alterar compatibilidad orgánica | Proposed | 2026-10-12 | Pendiente de ranking |
| D-011 | Atención clara y continua como promesa principal: encontrar quién puede atender, entender condiciones y saber qué sigue | Approved | 2026-10-12 | No aplica a posicionamiento de producto |
| D-012 | Contrastar respuesta útil, claridad de condiciones, repetición y seguimiento como oportunidades prioritarias | Proposed | 2026-10-12 | Pendiente de evidencia de fricción |
| D-013 | Diseñar atención útil con clientes propios antes de activar una promesa amplia de captación | Proposed | 2026-10-12 | Pendiente de secuencia de entrega |
| D-014 | Priorizar independientes y despachos pequeños como compradores, conservando visión de expansión | Approved | 2026-10-12 | No aplica a segmento comercial |
| D-015 | Relación de servicio como centro: contratación, tareas, documentos, cobros y seguimiento; ampliación jurídica con diseño específico | Approved | 2026-10-12 | Pendiente de diseños de capacidades |
| D-016 | Búsqueda gratuita, servicios profesionales con precio o cotización y referencias institucionales pertinentes | Approved | 2026-10-12 | Pendiente de catálogo y rutas |
| D-017 | Compromiso profesional supervisado por Abogalia como modelo de respuesta recomendado | Discussing | 2026-10-12 | Pendiente de modelo operativo |
| D-018 | Evaluar un nombre distinto antes de consolidar marca, por coincidencia con un producto jurídico argentino | Discussing | 2026-10-12 | No aplica a arquitectura; cambio y nombre nuevo sin aprobar |
| D-019 | Limitar la IA actual a resumen de solicitud a petición del usuario y borrador de mensaje con información seleccionada por el abogado | Approved | 2026-10-12 | Pendiente de diseño y proveedor de IA |
| D-020 | Aprobar los flujos de resumen revisable con relato original conservado y borrador editable con información seleccionada por el abogado y copia manual | Approved | 2026-10-12 | Pendiente de arquitectura base y proveedor de IA |
| D-021 | Incorporar lecciones verificadas de Kova en selección de servicios, costos y orden de preparación | Approved | 2026-10-12 | No aprueba stack ni copia de recursos de Kova |
| D-022 | Aplazar procesamiento documental con IA y continuar con las dos funciones de texto y el resto del proyecto | Approved | 2026-10-12 | No elimina almacenamiento básico de documentos de la visión |
| D-023 | Preparar una suite propia de servicios para Abogalia, con recursos, credenciales y costos separados de Kova | Approved | 2026-10-12 | No aprueba proveedores, tiers ni contratación |
| D-024 | Propuesta anterior de backend TypeScript integrado en Workers; conservada como alternativa tras elegir React + FastAPI | Proposed | 2026-10-12 | No fue aprobada; selección posterior en D-025 |
| D-025 | React para frontend y FastAPI sobre Python como backend central | Approved | 2026-10-12 | [ADR-001](ADR-001-react-fastapi.md) |
| D-026 | Suite en comparación para React + FastAPI: propuesta vigente Cloudflare frontend Free, API pequeña Fly y Supabase/Resend Free con recursos propios | Discussing | 2026-10-12 | Hosting, identidad, tiers, presupuesto y contratación pendientes |
| D-027 | Usar posprojectsupport para administrar servicios con espacios propios por producto y conexiones reutilizables en Codex; conservar identidad personal de GitHub | Approved | 2026-10-12 | [ADR-002](ADR-002-administration-and-product-isolation.md); configuración y alcance de conexiones pendientes |
| D-028 | Supabase Auth como proveedor de identidad de usuarios de Abogalia | Approved | 2026-10-12 | [ADR-003](ADR-003-supabase-auth.md); flujos, permisos y sesiones por diseñar |
| D-029 | Proyecto vacío abogalia en organización Abogalia Free y región us-east-1 | Implemented | 2026-10-12 | [ADR-004](ADR-004-empty-supabase-project.md); creado por Arturo y verificado; sin conexión de aplicación |
| D-030 | Monorepo Abogalia con apps/web React Router sobre Vite, prerenderizado público y apps/api FastAPI | Implemented | 2026-10-12 | [ADR-005](ADR-005-monorepo-and-rendering.md); base local verificada, sin despliegue ni flujos de negocio |
| D-031 | Aprobar recomendaciones A IC-01–IC-06 y diseño/matriz de Identity; continuar proactivamente con implementación local coordinada | Approved | 2026-10-12 | [ADR-006](ADR-006-identity-api-and-sessions.md); no equivale a capacidad terminada |
| D-032 | Retener cuenta cerrada/evidencia mínima de membresía terminada 30 días y auditoría 90 días, con eliminación o anonimización posterior | Approved | 2026-10-12 | Datos jurídicos y revisión legal pendientes |
| D-033 | Continuar controles locales C01 y baseline seguro conforme a T04 entregado, preservando cambios locales | Approved | 2026-10-12 | No autoriza publicación, acceso remoto o gasto |
| D-034 | Resend por SMTP en plan Free, sin sobrecostos automáticos, para confirmación/recuperación del piloto | Approved | 2026-10-12 | Dominio/remitente, cuenta por producto y tratamiento de correo pendientes; no implementado |
| D-035 | Primera validación desde frontend local con Supabase real de Abogalia | Approved | 2026-10-12 | Sin hosting publicado; configuración/grants y pruebas reales pendientes |
| D-036 | Activar plan C02 remoto en proyecto existente; OTP600s, pausa60s, máximo6 mensajes de ensayo; tratamiento SMTP aceptado; Arturo responsable cierre/retiro Auth y fallosretención | Approved | 2026-10-12 | Sin hosting nuevo; mínimos de roles y retirada verificada; operación pendiente |
| D-037 | Crear .env local privado y hacer commits/push periódicos de cambios revisados en rama de trabajo | Approved | 2026-10-12 | .env excluido; nunca publicar valores secretos ni desplegar por inferencia |

Morelia, especialidades, precios, primera entrega utilizable y reglas de cobro no han sido ratificados en esta conversación. React + FastAPI fue aprobado en D-025; servicios y detalles de arquitectura siguen pendientes. La investigación solicitada sobre Doctoralia no equivale a aprobar su modelo para Abogalia.

Fuente de las decisiones aprobadas: prompt maestro y respuestas de Arturo en la conversación. Propuestas y contexto: [definición de solución](../19_solution_definition.md). Cuando se apruebe una arquitectura se añadirá el ADR correspondiente; no se crean ADRs ficticios para cerrar decisiones pendientes.

Las decisiones D-011, D-014, D-015 y D-016 corresponden a cuatro respuestas explícitas de Arturo en esta sesión. Para D-017 expresó que no sabía cuál era el mejor approach; se registra una recomendación discutida, no una aprobación. Contexto y responsabilidades propuestas: [producto refinado](../23_refined_product.md).

Para D-018 Arturo preguntó si sería bueno cambiar el nombre. Se recomienda explorar una identidad propia por el solapamiento de producto y posible confusión comercial, sin concluir indisponibilidad jurídica en México. La pregunta no autoriza renombrar el proyecto. Antes de seleccionar una alternativa deben revisarse nombres iguales y similares, clases pertinentes, dominios y presencia comercial. [Orientación del IMPI sobre MARCia](https://www.gob.mx/impi/acciones-y-programas/marcia-265449). La búsqueda registral y la revisión jurídica siguen pendientes.

Para D-019 Arturo indicó: «Solo quiero implementar las primeras dos cosas ahortia», referido a las dos primeras filas de la comparación de complejidad. El alcance queda aprobado; las demás funciones de IA se aplazan. No se infiere aprobación de stack, diseño detallado, transmisión de datos a un proveedor o gasto. [Checkpoint preparado](../checkpoints/ai-assistance.md).

Para D-020 Arturo respondió «Sip» a la aprobación de los dos flujos descritos: generación a petición, revisión, edición, aceptación o descarte del resumen; selección de información, revisión, edición y copia del borrador, sin envío automático. La respuesta aprueba esos flujos funcionales. Arquitectura, proveedor, presupuesto, límites, política de retención y tratamiento de datos siguen pendientes, como se indicó al presentar el checkpoint.

Para D-021 Arturo pidió tener en cuenta las lecciones de Kova, desde servicios utilizados hasta el orden de configuración. Se revisó evidencia y se preparó la [comparación y secuencia](../25_kova_lessons_and_setup_order.md). La instrucción no autoriza cambiar Kova, reutilizar sus datos o secretos, seleccionar automáticamente un stack ni provisionar servicios de Abogalia.

Para D-022 Arturo indicó que por ahora se dejara de lado lo que generaría mucho gasto, referido al procesamiento documental explicado. Se aplazan OCR, extracción e indexación; continúan resumen y borrador de texto aprobados. No se interpreta como eliminación de carga y almacenamiento básicos del proyecto completo.

Para D-023 Arturo confirmó: «Obviamente crearía todo un suite nuevo para abogalia». Se presupuestan recursos propios sin descontar servicios o créditos de Kova. Solicitó discutir servicios, razones y tiers con información actual verificada. La [comparación de tarifas](../26_services_and_tiers.md) distingue fuentes oficiales, recomendaciones y cálculos; no autoriza contratación ni convierte propuestas en decisiones aprobadas.

Para D-024 Arturo solicitó una recomendación experta de suite escalable. Se preparó un [checkpoint de base técnica](../checkpoints/platform-foundation.md) con un camino concreto, organización por módulos, crecimiento medido, tiers y límites verificados. La solicitud autoriza el análisis y la propuesta, no la elección automática ni contratación. La recomendación de correo distingue desarrollo, producción y validación de Cloudflare Email Sending en beta.

Para D-025 Arturo confirmó expresamente React y FastAPI. Se registra la selección y su [ADR](ADR-001-react-fastapi.md), sin volver a pedir aprobación de esos frameworks. La propuesta D-024 de backend integrado deja de ser el camino principal. La actualización D-026 compara servicios propios y calcula costos; no aprueba por inferencia Fly.io, Cloudflare, Supabase Auth, réplicas, regiones, proveedores de IA ni contratación.

En la discusión de D-026 Arturo preguntó por Vercel y Resend y pidió algo semejante a Kova con mejoras. Se verificó FastAPI en Vercel, opción omitida en la primera comparación. La recomendación actual evalúa React y API en dos proyectos Vercel del mismo equipo Pro, conservando pipeline coordinado, identidad por decidir y datos externos. Services permite un despliegue conjunto pero sigue en beta; no se asume necesario. [Comparación revisada](../26_services_and_tiers.md). Es preferencia y propuesta de servicios, no aprobación de gasto ni prueba de funcionamiento.

Arturo cuestionó el costo inicial y pidió escalado vertical. D-026 sigue Discussing. Se ajusta la recomendación a capacidad pequeña: Vercel Pro, una Micro Supabase Pro y Resend Free dentro de cuota, US$45 de base; pruebas locales aisladas al inicio. Segunda base alojada y correo pagado se añaden por necesidad demostrada. Escalar cómputo no elimina cuotas de plataforma y no requiere subir a Supabase Team. No se aprueban gasto ni proveedores por esta revisión.

Tras verificar las cuentas de Kova y pedir Arturo una suite propia económica, D-026 mantiene Discussing con propuesta Cloudflare React Free + Fly FastAPI 1 GB + Supabase/Resend Free. [Checkpoint vigente](../checkpoints/platform-foundation-low-cost.md). Se calcula US$6.70 de cómputo por 30 días en iad/ewr, sin garantizar factura ni capacidad. Organizaciones/equipos y recursos propios pueden administrarse con el mismo acceso personal; cuotas no se multiplican automáticamente. No se crea infraestructura ni se interpreta la pregunta como aprobación.

Arturo pidió reorganizar las sesiones por producto y después señaló la fricción de autenticar plugins/MCPs repetidamente. Se incorpora Q-023 y se ajusta el checkpoint: conservar recursos propios, evaluar conexiones reutilizables a varias cuentas y distinguirlas de sesiones de navegador. La identidad administrativa por proveedor sigue Discussing; no se crean cuentas, perfiles ni conexiones y no se cambian permisos por esta propuesta.

Al pedir cómo organizar la suite sin logins repetidos, se concreta D-027: un usuario habitual por proveedor administra espacios de Kova y Abogalia separados. Conservar conexiones existentes, comprobar alcance al espacio correcto y añadir una conexión adicional solo cuando lo requiera la autorización. Las credenciales de runtime y despliegue, datos y facturación del producto son propios; la identidad humana administrativa se comparte. [Diseño vigente](../checkpoints/platform-foundation-low-cost.md). La propuesta no constituye aprobación de contratación ni garantiza soporte de varios espacios en cada plugin.

Arturo confirmó: «Va, entonces usemos posprojectsupport para administrar todo y los espacios separados para Abogalia». D-027 pasa a Approved y se registra ADR-002. Queda aprobada la organización administrativa; no se infiere aprobación de hosting, Auth, gasto, transferencia del repositorio o cambios a Kova. El orden de preparación se concreta en el checkpoint vigente. No se crean recursos externos en esta actualización.

Inicio de ejecución posterior: «Ya te deje abierto github, supabase, vercel y fly. Empecemos». Se ejecuta la preparación administrativa: organización Supabase Abogalia creada en Free y leída directamente por el conector; .gitignore y registro de destinos preparados. D-027 sigue Approved con implementación parcial; los demás espacios no se han configurado. Se presenta [checkpoint de repositorio y base vacía](../checkpoints/repository-and-empty-database.md) antes de elegir estructura, renderizado, Auth y región. No se contrata hosting ni se modifica Kova.

Arturo eligió Supabase Auth y Abogalia Free en us-east-1 en las preguntas del primer bloque. Se registran D-028 y D-029 Approved. Su respuesta «osea el monorepo seria abogalia» pide aclarar la estructura y no confirma todavía React Router ni prerenderizado; Q-024 permanece pendiente con una pregunta concreta de confirmación. Se preparó el formulario del proyecto en la organización correcta, nombre abogalia, Virginia, exposición automática de tablas desactivada y RLS automático activado. La contraseña y el envío del formulario corresponden al usuario; aún no hay proyecto ni código de aplicación.

Después Arturo respondió «Confirmo el monorepo Abogalia + React Router (recomendado)». Se aprueba D-030 y se inicia la base local, sin modificar Kova. Q-024 queda respondida. La entrega inicial comprueba prerenderizado y conexión navegador/API; no implementa flujos de Identity ni negocio por inferencia. El proyecto Supabase sigue pendiente del envío del formulario por el usuario.

D-030 Implemented: React Router en apps/web y FastAPI en apps/api ejecutables localmente, dependencias fijadas y lockfiles, checks locales y workflow de CI preparado. Verificados HTML prerenderizado, exclusión del diagnóstico del build, llamada real navegador → proxy Vite → FastAPI, fallo con API apagada y recuperación. [Evidencia y límites](../operations/local-foundation-verification.md). Sin commit, push, CI remoto, hosting contratado ni conexión a base; D-028 sigue Approved sin integración y D-029 Approved sin proyecto creado.

Actualización posterior: Arturo confirmó «Listo, ya creé el proyecto». D-029 pasa a Implemented tras consultar directamente el ref xggefantvuwpilksfdoy: organización jdmkzzkgnzwldthjqtgx, Free, us-east-1, ACTIVE_HEALTHY y cero tablas public. La conexión existente permitió estas lecturas sin reconectar. Trigger ensure_rls habilitado; los privilegios residuales de nuevas tablas quedan documentados para su diseño explícito en Identity. No se crearon tablas ni se modificaron grants durante esta comprobación. [Primer bloque completado](../checkpoints/repository-and-empty-database.md). D-028 continúa Approved sin flujos implementados; hosting y gasto siguen pendientes.


D-031/D-033: tras entregar tres diseños y T04, Arturo indicó «aprobado, tu continua
proactivamente». Se aprueban las recomendaciones presentadas y el avance local;
no las alternativas descartadas ni proveedores/contratación pendientes. Se preparan
contratos, custodia de sesión, datos locales, API/web y pruebas, con revisión
independiente. D-032 procede de su respuesta explícita a la pregunta de retención:
«30 días para cuenta/membresía; 90 días para auditoría». El contenido jurídico no
se incorpora a esta política ni se accede a clientes reales.


Tanda 03 C02: Arturo ordenó continuar proactivamente con Supabase real, correo y
retención y presentar decisiones. Eligió expresamente «Resend por SMTP, plan Free»
y «Frontend local con Supabase real». Se registran D-034/D-035 Approved; informó
«no tenemos dominio todavía». No se inventan dominio, remitente o buzón de prueba,
ni se interpreta esa respuesta como compra o permiso de envío a terceros. Se
preparan checkpoints operativos y herramientas locales sin modificar recursos
remotos. La política propia 30/90 permanece; tratamiento/retención del proveedor
SMTP es un contrato separado pendiente de revisión.


Arturo aprobó expresamente los tres paquetes operativos recomendados y asumió
cierre/retiro Auth y fallos de retención. D-036 autoriza configuración y schema/grants
mínimos revisados del proyecto Abogalia existente, piloto SMTP/OTP de máximo seis
mensajes al buzón controlado indicado y tratamiento del proveedor documentado.
No autoriza ampliación de privilegios para sortear un error ni elimina la necesidad
de prueba confiable antes de borrar cuentas. D-037 solicita `.env` con variables y
commit/push periódicos: archivo local privado excluido, plantilla pública vacía y
publicación solo de fuentes revisadas sin credenciales. No compra dominio/hosting.

D-038 — Arturo corrigió el nombre a Legalia, creó cuentas propias Google/Resend y
un proyecto Supabase nuevo, y pidió revisar best practices e implementar lo ya
aprobado. Destino vigente spohytnxscljtitvmdab / organización tagovxtvdicxjweeerwi,
Free/us-east-1, verificado en panel. Su «HAZLO TODO» respondió a confirmación de
roles/grants mínimos en el SQL Editor. Se conserva arquitectura y nombres técnicos;
no transferencia/borrado del proyecto anterior ni reutilización de Kova. Dominio
aplazado; no autoriza contratación, envío público sin dominio, eliminación de gates
o ampliación de permisos por un error. Ya no denominar el producto piloto; el
ejecutor histórico conserva límites de ensayo hasta contrato operativo distinto.
[Evidencia](../operations/legalia-supabase-setup.md).

D-039 — Approved (2026-10-14): Arturo aprobó validación activa por API Auth
GET /auth/v1/user con token custodiado, conforme al checkpoint revisado. Preservar
JWT/sub/session_id y fronteras, fail-closed sin caché ni fallback. La aprobación
habilita implementación local; demostrar revocación en la versión real de Legalia
sigue siendo requisito previo a activación. No nuevos permisos SQL Auth.

D-040 — Approved (2026-10-14): Arturo aprobó las opciones A de PC-01..PC-05 en
C03: contexto propio/despacho, revisión manual/publicación, capacidades/membresía,
salida/relevo y minimización/plazos nuevos 30/90 de datos e historia C03. Concretar
contratos/modelo/matriz y revisar antes de tablas; sedes, suplantación, revisión
jurídica y decisiones ajenas a esos paquetes no se resuelven por inferencia.
No autoaprobación del revisor ni acceso jurídico universal. Asked no equivale a Done.

D-041 — Approved (2026-10-14): Arturo respondió Q-C03-01..03 A: invitaciones
internas a cuenta confirmada, sin correo/búsqueda por email, vigencia24h y recibo
terminal30d/audit mínimo90d; capacidad review_professionals asignada manualmente a
su cuenta confirmada con MFA, sin self-review ni administración proveedor,
condicionada al procedimiento de revisión; resolución excepcional de cierre de
despacho a Arturo mediante capacidad separada y explícita sin contenido jurídico.
Relevo ordinario requiere nominación/aceptación; retiro no espera cierre. No concede
privilegios reales por sí sola ni resuelve el procedimiento jurídico pendiente.
