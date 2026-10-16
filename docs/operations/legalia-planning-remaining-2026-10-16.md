# Legalia — integración del planning restante por Agent Teams

Fecha2026-10-16. Solicitud de Arturo: reactivar equipos y terminar la planificación
restante. Base común publicada `4eb597c`, rama `codex/identity-design`, sin cambios
locales antes de asignar. A0 integrador; tres agentes con archivos exclusivos.

## Resultado

El [plan vigente](../27_development_plan_agents.md) cubre C00–C19. Se prepararon
16 checkpoints C04–C19; C00–C03 conservan sus contratos y una matriz de cierre real.
Cada checkpoint nuevo tiene las ocho secciones requeridas, modelos/relaciones,
propiedad, estados, clasificación, historia/retención, seguridad, dependencias,
trabajo posterior y aceptación negativa. C18/C19 permanecen aplazadas.

Estado de la entrega: **planning integrado y revisado**; diseños nuevos Proposed.
No se afirma que toda la aplicación esté implementada ni que se hayan aprobado
proveedores, políticas comerciales, plazos, permisos o esquemas pendientes.
La cobertura del planning no elimina decisiones de Arturo ni la revisión jurídica.

## Equipo y entregas

| Agente | Archivos propios | Resultado |
|---|---|---|
| A1 planning_attention | c04-requests-conflicts, c05-service-relationships, c06-discovery-catalog, c07-bookings-consultations y handoff | Solicitud/intake, acuerdo/seguimiento, oferta y agenda separados; versiones, audiencias y concurrencia; seis paquetes de decisión propuestos |
| A2 planning_services | c08-payments-refunds, c09-private-documents, c10-notifications, c11-subscriptions-billing, c12-reviews-reputation, c13-ai-assistance-delivery y handoff | Dinero/entitlements/documentos/avisos/reseñas/IA con fronteras propias; nada de proveedores o retención inferidos |
| A3 planning_operations | c14-platform-operations, c15-complete-delivery, c16-audit-analytics, c17-limited-operations, c18-legal-expansion, c19-advanced-integrations y handoff | Gates de operación, cierre C00–C03, aceptación, datos y futuro aplazado |
| A0 | Plan actual, archivo histórico, índice, este informe y reconciliación documental | Cobertura completa, revisión transversal, referencias/estructura/secretos y publicación |

Handoffs: [atención](planning-attention-handoff.md),
[servicios](planning-services-handoff.md), [operación](planning-operations-handoff.md).
No se iniciaron agentes adicionales ni se concedió acceso remoto a estos agentes.

## Revisión independiente e integración

- A3 revisó C04–C07: sin bloqueantes de planning; no admin jurídico universal,
  mutaciones sujetas a versión/revocación, gates C02/C03 y política pendiente clara.
- A1 revisó C08/C09/C10: señaló tres ajustes de contrato; A2 los integró: reautorizar
  inmediatamente antes de envío externo, revalidar versión/contexto/participantes
  de un cobro y limitar documentos a participación C05, incluido cierre de relación.
- A2 revisó C14–C17: sin retención/precio/permiso nuevo inferido; C15 exige contratos
  propios si incluye dinero/IA, y C16/observabilidad no capturan datos por este plan.
- A0 revisó estados/fuentes, separación de entidades, puertas de implementación,
  preguntas agrupadas y coherencia con D-031/032/039/040/041. Conserva búsqueda
  gratuita y flujos IA aprobados, sin reabrir hosting/costo ni destinatarios anteriores.

Se archivó íntegro el plan acumulativo anterior en
[histórico](../27_development_plan_agents_history_2026-10-16.md), misma ubicación
relativa para conservar referencias. El nuevo plan separa hechos de propuestas.
Se reconciliaron README/índice y checkpoint de activación: hosting público y
configuración ya resueltos; sus flags0 anteriores quedan identificados como historia.
No se editaron secretos ni se cambiaron flags de ejecución por reconciliar texto.

## Cola inmediata de trabajo

Las tareas siguientes están listas para asignar en tandas pequeñas, con rutas
exactas y revisión independiente al emitir cada orden. No son ejecuciones iniciadas.

| Orden | Dueño propuesto | Dependencia/gate | Entrega verificable |
|---|---|---|---|
| N01 Evidencia C02 | A7/A0 + paso humano de Arturo | Cuenta APP controlada confirmada/MFA; mantener presupuesto original de correo y no solicitar secretos por chat | Entrega/OTP/recuperación/MFA y revocación local/global probados; sin tokens o códigos en reportes |
| N02 Retirada integrada | A4 + revisión A2/A7 | Resultado fiable de revocación y contrato D-039 | Cookie local anterior negada tras retirada externa; rollback y aislamiento demostrados, no solo token vencido |
| N03 Mantenimiento/restore | A0/A3/A2 | Mecanismo fiable Auth, rol/ejecutor mínimo y esquema C03 compatible; resolver objetivos/custodia/retención de copias | Paquete operativo concreto para decisión, sin purga ni grants nuevos por inferencia; prueba aislada tras aprobación |
| N04 C03 restante | A3 único escritor SQL → A4/A5; revisión A2 | PC-01..05/D-041 ya aprobados; concretar contratos/revisión y no confundir con producción instalada | Incrementos locales de invitación/membresía/salida/relevo con negativos y retención30/90; activación/publicación real espera gates aplicables |
| N05 Confianza | A1/A2/C17 | Procedimiento de cotejo/suplantación/recurso y revisor alterno pendientes; facultades D-041 no se vuelven a votar | Proceso y matriz revisables; sin afirmar identidad profesional verificada por simple coincidencia de cédula |
| N06 Atención directa | A1/A2 → A3 → A4/A5/A7 | Prioridad y checkpoints C04/C05 aprobados, modelo/matriz/retención concretos | Solicitud dirigida, respuesta, acuerdo versionado y siguiente acción; sin pago/IA/agenda/adjuntos implícitos |
| N07 Descubrimiento/agenda | A1/A2 → A3/A4/A5/A7 | C06/C07, oferta y reglas/zonas/cambios aprobados | Corte público y reserva consistente; disponibilidad no revela otro asunto/contexto |
| N08 Servicios/expansión | Equipos por capacidad | Checkpoints C08–C13 y sus proveedores/políticas; C18/C19 solo reapertura específica | Trabajo asignado con contratos propios; no habilitar un paquete por aprobación de otro |

C02/C03 pueden seguir en trabajos locales ya aprobados y sin datos reales. Un
pendiente jurídico no constituye una nueva obligación genérica de certificar todo
código sintético: debe identificarse qué tratamiento/promesa bloquea. Antes de tablas
sí se exige modelo/propiedad/estados/historia/retención aprobados. Uso jurídico real
mantiene su revisión y condiciones correspondientes: **LEGAL REVIEW REQUIRED**.

La migración C03 no se aplica en remoto por este planning. El mantenimiento coordinado
falla cerrado con C03 ausente/parcial: esa dependencia debe resolverse en un paquete
revisado, sin owner runtime, bypassRLS o modo identity_only silencioso.

## Primera sesión de decisión preparada

Se recomienda C04/C05 de atención directa con profesional elegido como primer corte;
la prioridad sigue pendiente de Arturo. Se presentó una pregunta opcional para elegir
entre esa secuencia y marketplace primero; una selección no aprueba todos sus contratos.
No es un producto desechable: es un incremento permanente del producto completo.

La primera sesión se limita a estas seis decisiones, con opciones desarrolladas en
los handoffs/checkpoints. No se pide aprobar todos los plazos/proveedores de golpe:

1. Prioridad de la primera entrega (atención directa o descubrimiento/consulta/pago).
2. Solicitud a un destinatario profesional o bandeja con delegación explícita.
3. Responsable único y acuerdo versionado/portal mínimo, o colaboración multiactor.
4. Matriz concreta por familia jurídica y proceso de aprobación de conservación/
   divulgación; los números aún pendientes no se eligen al aprobar la dirección.
5. Procedimiento de confianza y recurso/revisor alterno, sin repetir capacidad D-041.
6. Paquete operativo mínimo de mantenimiento/retirada/restore, con campos y
   parámetros concretos antes de ejecutar; Arturo/30/90 ya aprobados.

AT-05/06 y decisiones de dinero/documentos/canales/IA van a sesiones posteriores,
según dependencias y máximo5–8 decisiones por sesión. No son preguntas pendientes
que obliguen a parar todo trabajo: se continúa diseño o implementación ya autorizada
que no dependa de ellas. Ninguna respuesta por silencio o tiempo transcurrido.

## Validación de esta entrega

A0 comprueba cobertura C00–C19,16 checkpoints con ocho secciones y todos los enlaces
locales del paquete, conservación íntegra del histórico y diff sin errores.
Scanner redactado de fuentes/historia antes de commit/push, sin valores sensibles.
No pruebas de software nuevas: esta tanda solo modifica Markdown. Los resultados
previos587 API/SQL y57 controles web/operación se citan como evidencia anterior,
no como nuevas ejecuciones ni como aceptación de negocio.

Sin cuentas creadas, correos, usuarios consultados, SQL, proveedores, gasto, nuevas
concesiones, retención real, despliegue o CI remoto ejecutados en esta tanda.

Validación ejecutada por A0:20capacidades,16checkpoints con8secciones cada uno,
enlaces locales correctos y archivo histórico íntegro respecto a4eb597c.
Escáner8.30.1:238archivos de fuentes e historial, cero hallazgos. Git diff --check
sin errores. Todos los agentes entregaron y congelaron sus archivos antes de integrar.
