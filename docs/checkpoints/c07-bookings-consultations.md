# Checkpoint C07 — Disponibilidad, reservas y consultas

Fecha: 2026-10-16. Estado: **Proposed / Requires Arturo**. Orden A1, baseline
`4eb597c`, rama `codex/identity-design`; revisión A0/A2/A7. Solo planificación.

## Lo que entiendo

Coordinar un intervalo y prestar una consulta son hechos distintos. Una solicitud,
evaluación comercial, reserva, pago, consulta y asunto no deben confundirse.
El mismo profesional opera en práctica propia y despacho; evitar doble reserva no
autoriza revelar participantes, relatos, títulos o detalles del otro contexto.
Fuentes: [plan](../27_development_plan_agents.md), [decisiones](../decisions/decision-log.md),
[C03](professional-contexts.md), [C04](c04-requests-conflicts.md),
[C05](c05-service-relationships.md), [recorridos](../06_user_journeys.md).

## Decisiones tomadas

D-003/D-031: práctica propia más un despacho, sin mezcla de contenidos; revocación
profesional en siguiente petición y autorización vigente por objeto. D-011/D-015
priorizan claridad y seguimiento; no aprueban duración de consulta, buffers,
prepago, cancelaciones, no-show ni sanciones. D-007 sobre revisión antes de cobro
y D-009 sobre clases de servicio siguen discutidos. C02/C03 no están terminados
por existir sesiones o un borrador profesional. Hosting no añade calendarios externos.

## Decisiones pendientes

AT-06 del [handoff](../operations/planning-attention-handoff.md) propone empezar
coordinación manual interna, después de evaluación C04 vigente, sin cobro gestionado
por Legalia, sin bloqueo temporal vendido como confirmación ni calendario externo.
Alternativa: autoservicio transaccional junto con C08; requiere política de pagos,
holds/vencimientos/reembolso y excepciones completa antes de liberar reservas.

Faltan servicio/entregable/modalidad, duración, buffers, antelación mínima, horizonte,
franjas de atención, zona horaria elegida, cambios/cancelación/no-show, responsables
y canal de recordatorio. No elegir números por una convención técnica. Calendario
con disponibilidad recurrente solo después de aprobar esos campos. AT-04 decide
retención por familia. Condiciones jurídicas/profesionales: **LEGAL REVIEW REQUIRED**.
Aprobar diseño manual no decide automáticamente políticas comerciales de autoservicio.

## Diseño propuesto

| Entidad | Propiedad/relación propuesta | Estados/historia propuesta |
|---|---|---|
| AvailabilityRule | Profesional + contexto + modalidad/servicio; regla local versionada | borrador → vigente → retirada; cambio afecta futuras propuestas, no reescribe reservas |
| AvailabilityException | Profesional/contexto y rango; causa privada | vigente/cancelada; ocupación de otro contexto solo proyecta no disponible |
| CalendarOccupancy | Un profesional/recurso y intervalo ocupado; coordinación transversal mínima | ocupado/liberado; receptor de proyección solo sabe si intervalo está libre, sin IDs de contraparte |
| BookingProposal | Solicitante, profesional/contexto, servicio/versión y rango propuesto | propuesta → aceptada por ambas partes / rechazada / retirada. No ocupa ni promete intervalo por sí sola en corte manual |
| Booking | Un contexto propietario y profesional/recurso, participantes y relación/solicitud autorizada | confirmada → realizada / cancelada / ausencia reportada. Reagendar crea nueva versión confirmada y libera anterior atómicamente; no duplicar reserva |
| Consultation | Prestación profesional vinculada a una reserva o relación autorizada, nunca un alias del horario | pendiente → realizada / no realizada; resultado y siguiente paso compartibles separados de nota interna |
| SchedulingEvent | Reserva/propuesta/versión/actor/transición mínimos | historia sin motivo jurídico, invitados ajenos o texto privado en auditoría |

Modelo temporal propuesto: conservar instantes UTC y zona IANA que informó la
selección; UI muestra fecha/hora/zona y duración a ambos. Una hora local inexistente
o ambigua por cambio horario exige corrección/desambiguación explícita. Rango
semiabierto [inicio, fin); fin posterior a inicio; límites/buffers aprobados se
incluyen en la comprobación. No inferir zona por IP ni convertir fecha sin mostrarla.

Flujo manual inicial recomendado:

1. C04 registra revisión profesional vigente y C05 ofrece condiciones suficientes.
   Profesional propone intervalo/servicio/condiciones; cliente ve qué acepta. La
   propuesta no garantiza horario ni crea cargo. No se inventa periodo de hold.
2. Confirmación requiere aceptación coincidente del cliente y profesional y
   validación actual de elegibilidad/ocupación, en transacción. Solo una reserva
   puede ganar un intervalo incompatible; la perdedora recibe conflicto para elegir
   otra opción. Reintento idempotente no duplica reserva ni ocupa dos intervalos.
3. Reagendar verifica primero nuevo intervalo con versión esperada. Recomendación:
   conservar el horario anterior hasta aceptación coincidente y confirmación atómica
   del nuevo; propuesta alternativa no debe dejar dos reservas ni liberar a destiempo.
4. Cancelar retira ocupación atómicamente conforme a política aprobada; pagos C08
   tienen estado aparte y una cancelación nunca finge reembolso. No-show es reporte,
   no prueba automática de culpa ni cargo; desacuerdo sigue procedimiento C17.
5. Prestación registrada por profesional y resultado/siguiente paso visibles según
   acuerdo. Cliente puede reportar discrepancia; no registrar consulta realizada
   por transcurrir el reloj o por cobrarse. Notas internas no van al cliente.
6. Suspensión/salida profesional deniega acceso de inmediato; reserva queda marcada
   para resolución/cancelación por procedimiento sin exponer datos a administrador.
   No asignación automática a otro abogado ni retención de acceso por tener agenda.

API/UX futura: consulta acotada de intervalos posibles, propuesta/aceptación,
confirmación, cambio/cancelación y resultado, con versiones y claves idempotentes.
IDs opacos; proyección busy/free transversal mínima solo dentro de un algoritmo
servidor, no endpoint para enumerar todo el horario personal. No enlaces de
videollamada con credenciales en URLs públicas; videoproveedor fuera de alcance.

## Datos afectados

| Familia | Clasificación y visibilidad propuesta | Retención pendiente |
|---|---|---|
| Reglas/ocupación | Metadatos privados; pueden revelar hábitos y actividad aun sin relato | Vigencia y plazo de historia propio AT-04, no conservar indefinidamente |
| Reserva/participantes | Información privada de atención; cliente propio y profesional autorizado | Confirmada/cancelada/ausencia por finalidad y evento terminal; no aplicar cuenta30d |
| Consulta/resultado | Jurídico confidencial; compartido y privado separados | Política C05/jurídica propia antes de persistir contenido |
| Eventos/motivos | Historia restringida; motivo libre puede ser jurídico | Eventos mínimos sin texto; plazo distinto de auditoría C02 por aprobar |

No sincronizar calendarios personales/Google ni enviar invitaciones a terceros en
este corte. No incluir área legal, contraparte, relato o documentos en títulos de
recordatorio. C10 define contenido/destinatarios/canal antes de correo/WhatsApp/SMS.
Backups, eliminación, restauración y evidencia de disputa siguen AT-04; ocupación
liberada no elimina la reserva ni autoriza conservar su contenido sin plazo.

## Seguridad

Validación por objeto/contexto/acción y MFA profesional, CSRF/no-store y RLS/grants
mínimos. Autorizar de nuevo al confirmar; solicitud/revisión/acuerdo deben corresponder
al mismo contexto/participantes. Aislamiento de datos y serialización mínima.

Evitar doble reserva con exclusión/serialización transaccional efectiva sobre el
profesional/recurso y rango ocupado incluidos buffers; mecanismo SQL se elegirá
tras modelo aprobado por A3. Prueba con dos conexiones reales en base sintética,
no solo mock de disponibilidad. No confiar en calendario del navegador ni mutex
por proceso. El bloqueo transversal de tiempo no da lectura transversal del negocio.
Bloqueo de recursos compartidos del despacho (sala/equipo) requiere modelo propio;
no asumirlo por tener Office. Sincronización externa futura requiere permisos y
resolución de datos ajenos, no acceso total a agendas como solución universal.

## Impacto futuro

C08 añade pagos, vencimientos y reconciliación como contratos separados; no inferir
que reserva confirmada significa pagada o que pago significa consulta prestada.
C12 define elegibilidad para reseña; reserva/consulta son evidencia, no permiso
para publicar datos jurídicos. C05 recibe seguimiento, C10 recordatorios y C17
discrepancias. Medir dobles reservas efectivas y cambios fallidos de forma agregada,
sin participantes o contenido en logs/Cloudflare. Autoservicio no se habilita por
aprobar inicialmente coordinación manual.

## Implementación propuesta

1. Cerrar AT-06/04 y política de modalidad/duración/cambios; verificar C02/C03 y
   evaluación C04. A1/A2/A3 acuerdan ocupación mínima, estados y derechos.
2. Vertical manual: propuesta → aceptación coincidente → confirmación concurrente
   segura → cancelación/reagendado → resultado/seguimiento. No pagos, recordatorios,
   recurrencia compleja o integración externa sin sus checkpoints aprobados.
3. A4/A5 definen contrato de instantes/zona/versiones y UI que distingue propuesta,
   confirmación y prestación. A3 prueba exclusión con práctica propia y despacho.
4. Negativos A7/A2: dos confirmaciones simultáneas; intervalo/buffer solapado; cambio
   horario; zona equivocada; doble click/reintento tras timeout; cambio concurrente
   vs cancelación; nuevo horario ocupado conserva anterior; suspensión en commit;
   detalle de cita ajena en busy/error; pago fallido no muta prestación; no-show
   discutido no cobra/sanciona; restore no resucita ocupación cancelada.
5. Done exige estados e integridad probados desde UI/API/SQL, operación de fallos y
   políticas aprobadas. Solo dibujar slots no completa agenda ni una consulta real.

Verificación de esta entrega: documentación y referencias locales, sin código,
pruebas funcionales, tablas, cambios de agenda, emails ni operaciones remotas.
