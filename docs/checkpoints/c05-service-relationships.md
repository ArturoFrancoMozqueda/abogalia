# Checkpoint C05 — Acuerdos, relación de servicio y seguimiento

Fecha: 2026-10-16. Estado: **Proposed / Requires Arturo**. Orden A1, baseline
`4eb597c`, rama `codex/identity-design`. Revisión independiente A0/A2.
No aprobación de contrato, poderes, firma, datos jurídicos, precios ni esquema.

## Lo que entiendo

D-015 aprueba centrar la operación en la relación de servicio. El primer resultado
útil es que cliente y responsable sepan alcance, pendiente y siguiente acción sin
reconstruir comunicaciones. Esto no necesita inventar una consulta o pago para
clientes propios, pero esa entrada directa aún requiere aprobar AT-01/03.
Fuente: [plan](../27_development_plan_agents.md), [decisiones](../decisions/decision-log.md),
[producto](../23_refined_product.md), [C03](professional-contexts.md),
[C04](c04-requests-conflicts.md). No se entrega expediente judicial completo.

## Decisiones tomadas

D-011/014/015 fijan propósito, segmento y centro de gestión. D-003/031 separan
práctica propia y despacho, contexto propietario y profesional responsable, y
prohíben acceso jurídico universal por pertenencia o administración. D-040/041
resuelven C03 sin aprobar acuerdos, clientes de contexto, delegación jurídica o
retención C05. Los plazos de cuenta/membresía no se aplican por analogía.
La procedencia marketplace/directa no autoriza comisión ni transferencia de datos.

## Decisiones pendientes

AT-01 propone primer corte de atención directa; AT-03 propone acuerdo versionado,
asignación explícita y portal mínimo; AT-04 mantiene política jurídica por resolver.
**LEGAL REVIEW REQUIRED**: alcance del acuerdo, aceptación electrónica, capacidad de
representación, aviso de privacidad, cierre/disputa, evidencia y conservación.

Recomendado para primer corte: personas físicas actuando por sí mismas, sin
representación de empresas/terceros, servicios sin cobro gestionado por Legalia y
sin automatizar plazos procesales. No supone que todos los servicios sean gratuitos:
los importes/condiciones profesionales deben estar claros cuando procedan; su
formalización y cobro fuera de plataforma no se diseñan como atajo contractual.
Si no puede definirse un acuerdo suficiente sin C08, no activar esa modalidad.
Alternativa: diseñar y lanzar conjuntamente contrato de consulta/reserva/pago C07/08;
incrementa dependencias y requiere reglas económicas antes de liberar atención.

## Diseño propuesto

| Entidad | Propiedad y relaciones propuestas | Estados/historia propuestos |
|---|---|---|
| Lead | Prospecto de un contexto, ligado opcionalmente a LegalRequest; no crea identidad de cliente universal | abierto → en conversación → convertido / cerrado; conversión no prueba contratación |
| ClientInContext | Ficha mínima de una persona en un contexto, 0..N relaciones; vínculo a User solo comprobado por esa persona | activo / restringido / retirado; sin fusión por email/nombre y sin crear acceso por referencia |
| ServiceRelationship | Un contexto propietario, un cliente de ese contexto y un responsable habilitado; fuente directa o solicitud aprobada | propuesta → pendiente de aceptación → activa → cierre solicitado → cerrada; desacuerdo/suspensión como estados explícitos que no simulan fin de obligaciones |
| ServiceAgreementVersion | Una relación, N versiones; alcance, exclusiones, entregable, condiciones y responsabilidades explícitas | borrador → ofrecida → aceptada / rechazada / sustituida. Cambio material exige nueva aceptación, no sobreescritura |
| RelationshipParticipation | Relación/persona/capacidad/visibilidad/vigencia | propuesta → vigente → retirada; nueva membresía no restaura participación |
| Task | Una relación, responsable y audiencia compartida o interna explícita | pendiente → en curso → completada / cancelada; fecha de coordinación no es plazo procesal |
| RelationshipUpdate | Una relación, autor y audiencia explícita | borrador → publicada → corregida con referencia; no editar historia en silencio |
| InternalNote | Solo profesional autorizado de la relación | privada; nunca convertida automáticamente en actualización del cliente |
| LegalMatter | Asunto jurídico opcional, 0..N por relación, mismo contexto por defecto | diseño reservado para C18; no abrirlo ni guardar actuaciones en el primer corte |

No entidad genérica `case`: LegalRequest origina evaluación, IntakeSubmission
conserva entregas, ServiceRelationship vincula atención, Booking coordina tiempo,
Consultation registra una prestación y LegalMatter modelará la gestión jurídica.

Propuesta de recorrido:

1. Profesional con MFA/contexto activo propone relación y responsable explícito.
   Cliente autenticado acepta vinculación propia; nunca invitar por búsqueda global
   de email, importar libreta ni asumir que un contacto externo es un User.
   Mecanismo de conexión cliente-profesional y su vigencia requieren contrato antes
   de implementar; invitación de membresía C03 no se reutiliza como permiso cliente.
2. Preparar condiciones legibles por versión; aceptación registra quién aceptó qué
   versión y cuándo. No llamar a ese registro firma electrónica avanzada ni poder.
   Si ambas partes no aceptan el mismo texto vigente, relación no queda activa.
3. Solo responsable y colaboradores explícitos autorizados pueden operar contenido;
   el primer corte puede restringirse al responsable único para evitar delegación
   incompleta. Administrador no ve cartera jurídica por controlar el contexto.
4. Cliente ve acuerdo vigente, responsable, estado, próxima acción y actualizaciones
   compartidas. No ve notas internas ni las tareas marcadas internas. Audiencia
   por objeto, no un filtro de frontend ni ACL implícita para todo el despacho.
5. Reasignación dentro del contexto verifica elegibilidad del entrante y conserva
   evidencia mínima; comunicación/aceptación del cliente requiere política AT-03.
   Recomendación: aprobación explícita de cliente y nuevo responsable antes del
   relevo normal; ante retirada urgente, negar acceso antiguo inmediatamente y
   dejar atención suspendida hasta resolver, sin retrasar revocación.
6. Cierre registra motivo compartible, pendientes y acceso posterior permitido por
   política; no borra historia ni fija retención. Una disputa conserva estado visible
   y ruta operativa C17, sin prometer arbitraje o resolución profesional de Legalia.

API propuesta: comandos sobre relación/acuerdo/participación/tarea/actualización,
con autorización por acción/objeto, versión esperada y deduplicación de creación y
aceptación. Actualización interna y compartida con contratos separados para evitar
filtrado accidental. Rutas y campos finales serán un contrato A4/A5 después de
aprobar modelo; una lista de relaciones devuelve solo aquellas autorizadas.

## Datos afectados

| Familia | Clasificación/acceso propuestos | Historia/retención |
|---|---|---|
| Ficha y fuente | PII privada del contexto; solo relaciones habilitadas, no lista universal de clientes | Corregir contacto sin fusionar personas; conservación C05 pendiente |
| Acuerdo y aceptación | Jurídico confidencial compartido con participantes concretos | Versión exacta aceptada; plazo y eventuales bloqueos jurídicos pendientes |
| Tareas/actualizaciones | Jurídico confidencial con audiencia por objeto | Historial mínimo de cambio y autor, sin duplicar todo en auditoría |
| Notas internas | Confidencial restringido profesional | Finalidad/plazo diferentes de lo compartido; no acceso por ser titular de cuenta sin revisión de derechos aplicable |
| Participación/eventos | Autorización e historia restringidas | Retirada inmediata del acceso; retención de evidencia por definir, sin inferir C02 |

AT-04 debe decidir por familia inicio del plazo, contenido vs recibo, eliminación/
anonimización, solicitudes de derechos, restricciones justificadas, backups y
restauración. No elegir conservación indefinida ni borrar al cerrar cuenta del
profesional como solución. No almacenar datos hasta que la familia tenga contrato
aprobado. No se incluyen documentos C09 ni datos fiscales/pagos en el primer corte.

## Seguridad

Sesión vigente, MFA profesional, CSRF, no-store, autorización en transacción y
RLS/grants mínimos. Las referencias entre cliente, solicitud, relación, acuerdo y
contexto deben coincidir: impedir insertar un ID válido de otro ámbito. Acceso del
cliente propio separado de su membresía profesional; salir de despacho no lo amplía
ni lo elimina indiscriminadamente. Ningún administrador/soporte obtiene contenido
por resolver cierre excepcional D-041. Cierre o suspensión no habilita exportación
masiva; exportación y transferencia requieren contrato y derechos propios.

Comprobar audiencia en serialización servidor, búsquedas, contadores y errores.
No notas internas en correo, analytics, observabilidad, respuestas del cliente ni
borradores IA automáticos. No acceso directo desde navegador a tablas privadas.

## Impacto futuro

C09 adjuntará documentos a una relación y audiencia autorizadas, nunca a un
cliente global. C07 puede adjuntar consultas, C08/11 cobros/entitlements separados,
C13 selecciona texto con autorización vigente sin enviar automáticamente.
C18 debe aprobar profundidad del asunto, plazos y responsabilidades antes de ampliar
LegalMatter. No crear campos libres como sustituto de un expediente sin diseño.
Métricas propuestas: relaciones con responsable/próxima acción y seguimientos
cumplidos; no instrumentar texto, identidades ni medir resultado jurídico como KPI.

## Implementación propuesta

1. Arturo aprueba checkpoint AT-01/03/04, modelo conceptual, procedimiento de enlace,
   matriz y retención por familia antes de tablas. A2 revisa roles por acción y A3
   concreta invariantes. Esa aprobación permite trabajo local sintético asignado;
   no acredita validez jurídica del acuerdo ni habilita tratamiento real. Revisión
   de condiciones, representación y derechos sigue como gate de uso real:
   **LEGAL REVIEW REQUIRED**, sin exigir certificación jurídica para todo trabajo
   local aprobado ni declarar que ya existe dictamen.
2. Vertical inicial con responsable único: conexión consentida → propuesta versionada
   → aceptación coincidente → actualización compartida/próxima acción → cierre.
   Lead avanzado, múltiples profesionales, notas internas y LegalMatter se habilitan
   solo si el contrato de cada uno está resuelto; no son condición para ese corte.
3. A4/A5 desarrollan contrato y estados sin cobro/agenda/documentos/IA implícitos;
   A7 prueba integración con base aislada y participantes sintéticos.
4. Negativos obligatorios: admin sin participación; cliente ajeno; cruce de contexto;
   aceptación de versión sustituida; doble aceptación/conversión concurrente;
   nota interna en respuesta compartida; salida entre validación y escritura;
   reingreso sin acceso restaurado; responsable retirado y cierre pendiente;
   cuenta cliente/profesional con capacidades distintas; borrado/restore coherente.
5. Done: aislamiento SQL/API, flujo integrado, acuerdo y derechos revisados,
   operación de desacuerdo/cierre asignada y evidencia independiente A2/A7.

Entrega documental únicamente; no tablas, aplicación, datos reales ni aceptación
jurídica o funcional probada por este checkpoint.
