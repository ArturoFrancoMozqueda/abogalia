# Checkpoint C04 — Solicitudes e incompatibilidad profesional

Fecha: 2026-10-16. Estado: **Proposed / Requires Arturo**. Trabajo A1 de
planificación; no autoriza tablas, endpoints, pantallas de negocio o datos reales.
Referencia común: `4eb597c`, rama `codex/identity-design`. Revisión: A0/A2.

## Lo que entiendo

Una persona necesita compartir lo mínimo con un profesional elegido y recibir una
respuesta útil antes de revelar información adicional o contratar. Solicitud,
intake, revisión de conflicto, relación de servicio, reserva, consulta y asunto
son objetos distintos. Una respuesta favorable a evaluar no equivale a contratación,
resultado jurídico, ausencia definitiva de conflicto ni reserva confirmada.

Fuentes: [plan](../27_development_plan_agents.md), [decisiones](../decisions/decision-log.md),
[contextos C03](professional-contexts.md), [recorridos](../06_user_journeys.md),
[producto refinado](../23_refined_product.md), [definición](../19_solution_definition.md).
Las propuestas históricas de pagar antes de revisar no son políticas aprobadas.

## Decisiones tomadas

- D-011/D-014: atención clara y continua, independientes y despachos pequeños.
- D-015: la relación de servicio articula la gestión posterior; no convierte toda
  solicitud en cliente, reserva o asunto.
- D-031: propiedad operativa del contexto, responsable separado y acceso por objeto;
  sin cliente universal, traslado automático ni lectura jurídica por administrar.
- D-040/D-041: reglas C03 aprobadas; revisión profesional y operación real no están
  terminadas por ello. No reabrir esos paquetes.
- D-032 no fija retención de relato, partes ni decisiones de conflicto. D-019/020
  permiten dos flujos de IA, pero no autorizan proveedor ni transmisión en C04.

## Decisiones pendientes

Paquetes propuestos del [handoff A1](../operations/planning-attention-handoff.md):
AT-01 (primer recorrido), AT-02 (datos/destinatario/respuesta), AT-04 (retención).
La revisión jurídica y el responsable operativo deben validar partes, consentimiento,
rechazo y urgencias: **LEGAL REVIEW REQUIRED**. D-007/D-009/D-017 siguen discutidos.

Recomendación AT-02: una solicitud dirigida a un profesional habilitado de un
contexto activo; no bandeja universal del despacho, reenvío a varios ni búsqueda
global de partes. Alternativa: bandeja de intake con destinatarios explícitos y
una nueva capacidad limitada; requiere diseñar asignación antes de habilitarla.
Para la primera entrega, no prometer SLA numérico ni renovación automática de espera;
mostrar fecha de envío/última respuesta y permitir retirada. Un plazo de respuesta,
vencimiento automático, recordatorios o consecuencias exige política posterior.

## Diseño propuesto

Modelo conceptual, no esquema aprobado:

| Entidad | Propiedad y relaciones propuestas | Estados/historia propuestos |
|---|---|---|
| LegalRequest | Solicitante User; un contexto destinatario y un profesional elegido. Custodia de borrador del solicitante; tras enviar, alcance compartido explícito entre solicitante y destinatario, sin transferencia de propiedad jurídica | borrador → enviada → en evaluación / aclaración solicitada → disponible para acuerdo / no atendible; retirada desde estados no terminales. No reapertura silenciosa |
| IntakeSubmission | Una solicitud, 0..N entregas versionadas e inmutables; autor y destinatario explícitos | borrador privado antes de envío; versión enviada sustituida solo por nueva versión visible, conservando original según política aprobada |
| ConflictReview | Una solicitud, 0..N decisiones del profesional autorizado; referencia a versión de intake examinada | pendiente → requiere aclaración / no puede continuar / puede continuar. Nueva información invalida suficiencia anterior; nunca dictamen automático |
| RequestDisclosureReceipt | Solicitud/versión/actor/destinatario/finalidad/texto informativo versionado | registra presentación y acción explícita; no presume consentimiento universal ni autorización sobre terceros |
| RequestTransition | Una solicitud, evento mínimo, autor y versión esperada | fecha, transición y resultado sin relato/nombres de partes; historia privada diferente de métricas |

Formulario mínimo recomendado: situación/área declarada si la conoce, jurisdicción
indicada como conocida o por aclarar, modalidad deseada, descripción breve limitada
y destinatario visible. Límites de caracteres y campos exigidos deben concretarse
con A2/UX antes de contrato; no exigir archivos, identificaciones, número de expediente,
CURP, RFC o información de salud en la primera entrega. Las partes necesarias se
piden en fase separada por el profesional, con finalidad y destinatario visibles;
la revisión legal debe decidir qué datos de terceros son proporcionados y lícitos.
No declarar que el intake prueba representación o titularidad de una empresa.

Transiciones y efectos:

1. Solicitante confirma versión/destinatario antes de enviar. API revalida contexto,
   perfil habilitado, membresía vigente y aceptación de solicitudes; fallo no entrega
   contenido ni crea cliente. Reintento idempotente no duplica envío.
2. Profesional destinatario con MFA abre solo su solicitud asignada y puede pedir
   aclaración pertinente, rechazar o habilitar el paso a acuerdo. El estado del
   catálogo no sustituye revisión individual; retirar acceso impide siguiente lectura.
3. Cliente envía aclaración creando versión nueva; una revisión basada en contenido
   anterior no puede usarse para contratar sin nueva evaluación pertinente.
4. Profesional registra motivo interno mínimo; solicitante recibe resultado y
   siguiente acción, sin identidad de otro cliente ni evidencia de otro conflicto.
5. Solicitante retira; la retirada impide nuevas acciones de evaluación. Contenido
   ya conocido no puede revocarse de la memoria del destinatario; no prometerlo.
6. Profesional suspendido o que sale deja la solicitud sin destinatario habilitado;
   cliente puede retirarla. Reasignación exige decisión explícita y nueva autorización
   de destinatario; administración del despacho no recibe el relato por defecto.

Propuesta API/UX posterior a aprobación: comandos privados de crear/enviar/leer,
aclarar, revisar y retirar, sobre identificadores opacos; versión esperada y clave
idempotente en comandos. Rutas finales pendientes de contrato A4. Error de objeto
ajeno uniforme; versión obsoleta/conflicto concurrente explícitos sin filtrar datos.
La interfaz muestra destinatario, qué se comparte, estado, pendiente y acción real;
no vende aceptación comercial como opinión jurídica o urgencia atendida.

## Datos afectados

| Familia | Clasificación y acceso propuestos | Retención pendiente |
|---|---|---|
| Relato y versiones | Jurídico confidencial; autor y destinatario autorizado | AT-04: plazo de borrador/terminal no contratado; sin heredar 30 días de cuenta |
| Partes y relaciones declaradas | Datos personales potencialmente sensibles por contexto, incluidos terceros; acceso mínimo de revisión | Separar datos de revisión y recibo; definir plazo y supresión antes de persistir |
| Decisión de revisión | Resultado compartible acotado; fundamento restringido profesional | Política de evidencia y controversia distinta de auditoría de acceso |
| Recibo/historia | Evidencia restringida, sin repetir relato ni nombres | Plazo por finalidad pendiente; 90 días de C02 no aprueban historia C04 |

Cerrar cuenta no borra en cascada contenido compartido ni lo vuelve público.
El modelo debe resolver derechos contrapuestos, bloqueo legal revisado, cachés,
respaldos y reaparición tras restauración antes de aceptar contenido real. La
entrega actual solo contiene diseño público y ejemplos sintéticos abstractos.

## Seguridad

FastAPI media acceso; autorizar contexto, asignación, estado y acción al leer y en
la frontera transaccional de escritura. Mantener MFA profesional, sesión activa,
CSRF, no-store, RLS/grants mínimos aprobados y salidas uniformes. Administración,
soporte y revisor de profesionales no leen contenido por sus capacidades C03.
No listar clientes de otros ámbitos para comprobar conflicto ni revelar una
coincidencia a quien no tiene acceso al dato de origen. Buscar por nombre global
no es parte de esta propuesta. No adjuntos, IA ni mensajes externos automáticos.

No enviar relato, nombres, IDs de solicitud, errores crudos ni decisiones a logs,
URLs públicas, métricas o eventos de observabilidad Cloudflare. Contadores agregados
requieren C16; no instrumentarlos por presentar una métrica en este documento.
Urgencia declarada no dispara diagnóstico ni aviso a terceros; mensajes y rutas
institucionales deben ser revisados antes de mostrar recursos concretos.

## Impacto futuro

C04 ofrece referencia estable a C05, sin crear relación automáticamente; C07 puede
exigir revisión vigente de esta solicitud. C06 puede orientar por categorías públicas,
pero no publicar intake. C13 solo consume texto seleccionado tras tratamiento aprobado.
C17 necesita procedimiento de no respuesta y conflicto, sin adjudicarse criterio
profesional o acceso universal. Cambiar destinatario nunca implica transferir asunto.
Métricas propuestas: enviadas que obtienen respuesta útil, tiempo a primera respuesta
y retiradas; definir denominador/evento y minimización antes de instrumentar.

## Implementación propuesta

1. A0 registra aprobación de Arturo del checkpoint, modelo conceptual, matriz de
   acceso/divulgación y política de retención por familia AT-01/02/04 antes de tablas.
   A2 revisa controles; sin esas aprobaciones, seguir solo diseño. Con ellas puede
   implementarse localmente con datos sintéticos bajo orden explícita. La revisión
   jurídica sigue pendiente como puerta para activar tratamiento real de partes,
   consentimiento y contenido; no se afirma dictamen ni certificación previa a
   todo trabajo local ya aprobado. **LEGAL REVIEW REQUIRED**.
2. A3 diseña invariantes: contexto consistente, destinatario elegible, revisión ligada
   a versión, historia mínima y comando idempotente; pruebas SQL locales aisladas.
3. A4/A5 entregan vertical: borrador → envío explícito → lectura destinatario →
   respuesta/retirada, con contrato revisado y datos sintéticos; sin IA/cobro/adjuntos.
4. A7/A2 prueban: objeto/tenant ajeno; administrador sin lectura; revisión obsoleta;
   retirada vs aceptación concurrentes; doble envío; salida/suspensión entre lectura
   y commit; aclaración que no reinicia promesa inexistente; cambio de destinatario
   sin consentimiento; errores que no revelan existencia; eliminación/restauración.
5. Done exige recorrido integrado y revisión independiente, no mock o pantalla.
   Uso real depende de C02/C03 aceptados y política jurídica/operativa aprobada.

Verificación documental: ocho secciones, referencias locales y separación de entidades.
No código, consultas remotas, migraciones, pruebas funcionales o despliegues ejecutados.
