# Recorridos de profesionales y contextos — C03

Fecha: 2026-10-14; base `338617`, autor A1/A5. PC-01..PC-05 A Approved por Arturo;
implementación UI aún no autorizada en esta entrega. Contrato de referencia:
[API C03](../contracts/professional-contexts-api.md) y
[checkpoint](../checkpoints/professional-contexts.md). No nuevas decisiones de
precio, proveedor, envío o datos jurídicos. Revisión A0/A2 antes de pantallas.

## Primer recorrido implementable

Rutas propuestas privadas: `/profesional` y `/profesional/contextos`. No nuevas
rutas Auth, callback, OTP o campos en SessionView. `/cuenta` conserva MFA C02.

1. La persona entra a `/profesional`; sesión ausente/revocada confirmada → `/acceso`
   con navegación interna sin credenciales en URL. Fallo de red/503 conserva mensaje
   de indisponibilidad, sin fingir logout. Con aal1: «Verifica tu acceso para preparar
   tu perfil profesional» y enlace `/cuenta`; no leer/mostrar borrador privado aún.
2. Con aal2, GET profile propio. Si no existe: título «Prepara tu perfil profesional»;
   texto «Puedes guardar un borrador privado. Todavía no habilita actividad profesional
   ni aparece públicamente». Campos iniciales: nombre de presentación requerido,
   área declarada opcional. No nombre legal, cédula, identificación, dirección o
   dato de cliente en esta primera persistencia.
3. «Guardar borrador» envía POST profile. Éxito: «Borrador privado guardado» y
   «Tu práctica está en preparación». La API crea ambos objetos atómicamente;
   no mostrar profesional verificado, publicado, activo o administrador.
4. Si ya existe: cargar campos propios y editar con PATCH/expected_version.
   «Guardar cambios» no reinicia revisión porque el estado inicial siempre es draft.
   `declared_area` sigue siendo declaración, no especialidad certificada.
5. `/profesional/contextos` muestra solo «Práctica propia · En preparación».
   Contexto inactivo no ofrece clientes, asuntos, agenda, expedientes o botón de
   «empezar a atender». No selector de un despacho inexistente ni miembros simulados.
6. «Retirar borrador» presenta consecuencia concreta antes de confirmar: «Tu perfil
   y práctica dejarán de estar disponibles. Los datos se eliminarán o anonimizarán
   a los 30 días según su política. Esto no cierra tu cuenta». Confirmar envía versiones
   de perfil y práctica. Éxito: «Borrador retirado; práctica cerrada»; sin borrado
   físico inmediato ni botón de restaurar/recrear que evada retiro/retención.

Los borradores abandonados tienen corte a 30 días de última edición, según PC-05
aprobado. Mostrarlo junto al formulario: «Un borrador sin editar se elimina o
anonimiza después de 30 días». Ver el formulario/polling no cuenta como edición.
Cuenta cerrada no conserva acceso profesional por tener borrador previo; retención
y retiro real se integrarán con operación aprobada, no con un temporizador cliente.

## Funciones diseñadas con gates visibles

Las siguientes familias están en contrato completo, no en el primer incremento.
La interfaz informa disponibilidad real sin simular un botón que apruebe o publique.
No prometer revisión en una fecha, respuesta humana inmediata o entrega de invitación.

| Familia | Recorrido futuro | Mensaje mientras falta gate |
|---|---|---|
| Revisión | Titular completa declaración mínima nombre legal/cédula; envía snapshot; revisor autorizado ajeno claim/decide | «La revisión profesional aún no está habilitada. Tu borrador sigue privado» |
| Habilitación | Resultado manual con alcance específico; corrección/rechazo visibles solo al titular autorizado | «Guardar datos no habilita actividad profesional» |
| Publicación | Profesional enabled decide voluntariamente hacer pública la proyección permitida | «La publicación aún no está habilitada» |
| Activación de práctica | Perfil enabled + gate; confirmación explícita de práctica active | «Tu práctica sigue en preparación» |
| Despacho | Profesional enabled sin otro vínculo crea contexto con capacidades iniciales explícitas | «La gestión de despachos aún no está habilitada» |
| Invitación | Administrador propone capacidades a UUID confirmado que destinatario compartió; destinatario autenticado acepta | «Las invitaciones aún no están habilitadas» |
| Relevo/cierre | Nominación y aceptación auténtica; finalización con responsable definido | «El cierre requiere resolver la responsabilidad pendiente» |

No captura de CURP/RFC, documentos/ID/selfie, lectura de credenciales de fuentes
externas o consulta automática. Un profesional no se verifica a sí mismo. La
capacidad de revisor la habilita un mecanismo del producto aprobado; ser administrador
del despacho o de Supabase no la concede. Una cédula que coincide en un registro
no demuestra titularidad del solicitante: no mostrar «Identidad verificada».
Texto acotado futuro: «Datos de cédula cotejados», con fecha/alcance reales.
**LEGAL REVIEW REQUIRED** para procedimiento y personas reales.

## Estados y decisiones de revisión

Todos los estados provienen de API; no inferirlos de email confirmado, aal2,
botón pulsado o respuesta HTTP genérica. Perfil y publicación son independientes.

| Estado de perfil | Texto principal | Acción futura permitida por servidor |
|---|---|---|
| draft | Borrador privado | Editar/retirar propio; submit solo cuando review gate disponible |
| submitted | Solicitud recibida; pendiente de revisión | Ver/retirar; no editar snapshot enviado ni afirmar cotejo |
| under_review | En revisión | Ver/retirar; sin plazo inventado ni acceso a cola ajena |
| changes_requested | Necesitamos corregir tu declaración | Ver razón fija, editar nuevo borrador y volver a enviar según versión |
| rejected | No se habilitó tu perfil | Ver motivo mínimo; sin publicar, activar contexto o evadir con perfil nuevo |
| enabled | Perfil habilitado para el alcance indicado | Publicación/activación solo por decisiones separadas/gates |
| suspended | Actividad profesional suspendida | Sin trabajo/administración ordinaria; retirada y participación cliente independientes |
| withdrawn | Perfil retirado | Sin actividad/publicación; no restauración automática |

La pantalla de revisor propuesta muestra únicamente cola asignable/dato privado
necesario y resultado versionado. Claim tiene resultado real; si otro revisor gana,
mostrar conflicto y recargar. No autoaprobación, decisión sobre snapshot obsoleto
o razón libre que replique datos personales. No clientes/asuntos, acceso jurídico,
providers/admin keys o bypass MFA desde la revisión. Esta UI no se implementa aún.

Publicar necesita elección explícita y vista previa de campos efectivamente
públicos: nombre de presentación, área declarada, alcance/fecha de cotejo. La cédula
completa, email, reviewer, historial, User ID y membresías no se publican. Retirar
publicación la quita sin esperar a borrar datos privados; no usar build/prerender
para una proyección que no pueda retirarse en siguiente lectura.

## Despacho, capacidades y cambio de contexto

Contextos futuros: práctica propia y un despacho; active/suspended de membresía
ocupan el mismo slot hasta finalizarlo. No dos despachos por carreras concurrentes.
Presentar título y estado de cada contexto; al elegir, volver a consultar permisos.
No mover ficha/relación, unir información ni otorgar facultades por seleccionar.
La práctica propia conserva aislamiento cuando cambia la membresía del despacho.

Dos conjuntos con explicaciones concretas: «Administrar contexto y miembros» y
«Actividad profesional». Pueden coincidir; ninguno incluye lectura jurídica
general del despacho. En creación, administrar es transición inicial explícita;
actividad profesional solo si se pide y la API la concede. Invitación enumera
qué se propone y no aplica facultades hasta aceptación propia. Asistentes y sedes
aplazados; no expandir roles con un formulario libre.

Invitación interna propuesta: administrador introduce UUID que el destinatario
compartió personalmente; ningún buscador por email, roster Auth o correo saliente.
No mostrar dirección, nombre legal o cédula del destinatario. Rechazo genérico no
revela identidad ajena. Sin TTL/retención Q-C03-01, las acciones permanecen cerradas;
no usar ID de invitación como secreto de enlace. Aceptación fallida por slot ocupado
explica solo el vínculo propio, sin exponer otro contexto al administrador.

## Salida y cierre sin acceso residual

La salida retira facultades derivadas y conserva práctica propia; no copia relaciones
al exmiembro. Si participa como cliente, la API evalúa esa participación aparte.
Una cuenta cerrada no requiere acceso profesional o MFA para que el servidor retire
sus facultades por la operación C02 autorizada. No añadir cierre Auth nuevo aquí.

Relevo se propone y acepta; ofrecer «administración» o «responsabilidad de cierre»
con alcance explícito. No asumir que el destinatario aceptó por estar activo ni
que reviewer/soporte se convirtió en custodio. No acceso jurídico por ese relevo.

Si se revoca al último admin sin responsabilidad aceptada, mostrar resultado real
202: «Tu vínculo terminó. El despacho quedó sin actividad y su cierre necesita
resolver la responsabilidad». No indicar que la salida falló, pedir reintento para
revocar de nuevo ni conservar privilegios. El contexto closure_requested queda
cerrado a operación normal; cierre final no se afirma hasta Q-C03-03/responsable
resuelto. Sin mecanismo de resolución aprobado, despacho activo sigue gated.

Una operación que pierda permiso durante suspensión/salida informa rechazo y
limpia datos privados del ámbito revocado. Pestaña anterior, claims y asignación
histórica no continúan autorización. Ningún flujo garantiza retirar copias ya
descargadas o elimina datos de terceros por cerrar cuenta.

## Errores, accesibilidad y contenido

Formulario con labels visibles, ayuda ligada a campos, errores sin eco de valores,
orden de tabulación natural y teclado completo. Mensaje de éxito `role=status`;
error `role=alert`, foco al resumen de error y enlace al campo relevante. Botones
deshabilitados durante una solicitud, sin submit repetido ni retry automático.
`name` y autocomplete adecuados a campos de perfil; no reutilizar nombres de
password/OTP ni completar cédula con autocompletado Auth. Texto plano escapado.

| Respuesta | Tratamiento |
|---|---|
| 401 AUTHENTICATION_REQUIRED | Vaciar profile/context/roster/review y borradores en memoria; llevar a acceso cuando pérdida está confirmada |
| 403 MFA_REQUIRED | Vaciar vista profesional privada, conducir al paso C02 de MFA; no mostrar campos detrás del modal |
| 403 FEATURE_UNAVAILABLE | Mostrar mensaje de familia gated, no avanzar estado ni simular envío/revisión |
| 404 RESOURCE_UNAVAILABLE | Mensaje igual para ID ajeno/inexistente; no recuperar por otro endpoint |
| 409 VERSION_CONFLICT | «La información cambió. Actualiza antes de continuar»; recargar GET propio, no sobrescribir/reintentar automáticamente |
| 409 STATE_CONFLICT | Mostrar acción no permitida en estado actual; no ofrecer crear otro perfil para evadir |
| 409 FIRM_SLOT_OCCUPIED | «Ya tienes un vínculo de despacho vigente»; solo información propia |
| 422 INVALID_REQUEST | «Revisa los datos de la solicitud»; validación local guía sin imprimir cuerpo/provider |
| 429 RATE_LIMITED | «Inténtalo de nuevo más tarde»; respetar Retry-After sin reenvío automático |
| 503 PROFESSIONAL_UNAVAILABLE | «La operación no está disponible temporalmente»; no redirigir como si fuera logout, no nuevas mutaciones hasta recuperación |

Información declarada permanece solo en memoria/formulario autorizado hasta guardar;
no localStorage, analytics, log/captura o query. Al navegar, cerrar sesión o confirmar
revocación se elimina estado privado. Tras timeout incierto, informar «No pudimos
confirmar el resultado; actualiza antes de continuar» y reconciliar GET propio.
No declarar pérdida de cambios ni éxito hasta conocer estado real.

## Pendientes y aceptación

Q-C03-01 TTL/retención/canal interno de invitación; Q-C03-02 bootstrap del revisor
y procedimiento de cotejo/vínculo al titular; Q-C03-03 relevo/responsable de cierre
sin administrador. Están detalladas con alternativas en API; A0 ya las presenta a
Arturo. No volver a preguntar por los cinco paquetes aprobados.

A5 implementará pantallas solo después de consistencia API/modelo; A7/A2 verificarán
teclado/lector, estados C02/C03 reales, perfil/práctica atómicos, CAS/401/503,
negativos de ámbito/rol/snapshot/invitación/slot y salida transaccional. Pruebas
de diseño no sustituyen proveedor, persistencia y runtime. Sin interfaz, datos
reales, captura, envío, instalación, .env, consulta de proyecto o commit ejecutados
en esta entrega documental.
