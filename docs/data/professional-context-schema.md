# C03 — Contrato lógico de datos profesionales

Fecha: 2026-10-14. Base 338617. PC-01–PC-05 A aprobados por Arturo según orden
A0/D-040; el checkpoint conserva texto histórico pendiente de reconciliación por
A0. Este contrato concreta el modelo para revisión A1; **no SQL autorizado por este
documento ni campos pendientes elegidos silenciosamente**. LEGAL REVIEW REQUIRED.

## Alcance, propiedad y cardinalidad

### Persistencia incremental coordinada (D-041, 2026-10-14)

Arturo aprobó Q-C03-01..03 A: invitaciones24h, recibos terminales30d e historia90d;
revisor manual Arturo con correo confirmado/MFA y capacidad limitada, sin self-review;
cierre excepcional con capacidad distinta y sin acceso jurídico. Esta tanda sigue
limitada al agregado privado draft/preparing: esas aprobaciones no incorporan aquí
tablas de invitación, roles de revisor o transiciones de despacho.

Propuesta física antes de SQL: `identity.professional_drafts` representa el agregado
en una fila, con profile_id PK, owner_user_id UNIQUE, context_id UNIQUE, display_name,
declared_area nullable, profile_state/context_state, profile_version/context_version,
created_at, profile_updated_at/context_updated_at y withdrawn_at/closed_at nullable.
kind=practice es constante comprobada. CHECK liga draft/preparing o withdrawn/closed
y fecha de retiro igual: un UPDATE no puede dejar retiro parcial. Owner referencia
identity.users con RESTRICT, nunca cascada de datos o historia.

`identity.professional_events` contiene solo actor, profile_id/context_id lógicos,
transición, fecha y ambas versiones. Su identificador interno no contiene PII; sin
FK a cuenta/agregado, no pierde historia90d por borrado30d. No texto del formulario,
tokens, email, IP ni copias históricas de nombre/área. El runtime no lee ni modifica
historia; su inserción se liga al sujeto verificado y objeto propio.

Mismos roles existentes owner/runtime; ningún rol nuevo, grant público ni Data API.
FORCE RLS por subject GUC transaccional local. SELECT/INSERT propios y UPDATE solo
campos mutables; IDs, owner, kind y created_at sin UPDATE. Runtime sin DELETE/TRUNCATE,
sin capacidad DDL o lectura global. Política owner separada para mantenimiento, no
para tráfico API. Cuenta no puede borrarse antes de eliminar su agregado elegible;
los eventos lógicos90d sobreviven sin presentar UUID como anonimización.

Interfaz acordada con A4: `PostgresProfessionalContextStore(conn, *, subject, clock=None)` no acepta DSN ni abre
conexión; usa la misma conexión de SessionTransaction validada C02. Operaciones
create/read/edit/withdraw toman sujeto de ese principal, reloj inyectado y CAS;
lectura/edición bloquean la fila del agregado y creación se serializa con usuario
Identity. Métodos read()->agregado|None, create(fields), edit(fields, expected_version),
withdraw(expected_version, expected_context_version) devuelven agregado; create
genera IDs servidor y repetición informa STATE_CONFLICT sin restituir withdrawn.
Errores SQL se convierten a mensaje fijo sin query/params/diagnósticos.

La unidad de negocio usa savepoint separado después de guardar refresh consumido;
se mantiene hasta revalidación Auth de frontera. Error de dominio o frontera negativa/
indeterminada revierte agregado/eventos, conserva custodia renovada y no extiende
actividad. Contrato A4: tx.business()->CM(conn); authenticated(business=True) entrega
(record, conn), conserva savepoint durante yield y frontera, libera o rollback antes
touch/delete de Identity. Defaults de Auth existentes mantienen (record, tx).
No acceder a `_conn` desde rutas ni usar otra conexión/commit independiente.

Purga futura owner: agregado draft actualizado<=now-30d o withdrawn<=now-30d,
eventos occurred_at<=now-90d. Lectura/no-op/reintento retiro no reinician plazo.
Worker Identity vigente debe permanecer gated para borrar cuenta cuando exista
este agregado: antes comprobar/purgar C03 elegible a30d; si no elegible, reportar
cuenta bloqueada, nunca afirmar purge completo ni usar cascade. Su extensión no
forma parte de este store. Prueba negativa exige FK RESTRICT y eventos intactos.
Responsable operativo inicial: Arturo (D-036/D-041). No existe job C03 ejecutado
ni cumplimiento periódico comprobado; alertar bloqueo/omisión de30/90d a Arturo.
Una cuenta closed pierde Auth inmediatamente; no se reabre el agregado profesional
ni se mantiene acceso para superar FK. La operación debe retirar y purgar C03
cuando sea elegible antes de borrar cuenta, sin borrar historia90d ni terceros.
Scheduler/credencial de mantenimiento/retirada Auth siguen pendientes: almacenar
campos no demuestra cumplimiento operacional. LEGAL REVIEW REQUIRED.

Fuentes oficiales consultadas: [RLS PostgreSQL17](https://www.postgresql.org/docs/17/ddl-rowsecurity.html),
[transacciones/savepoints psycopg3](https://www.psycopg.org/psycopg3/docs/basic/transactions.html),
[CLI migration new](https://supabase.com/docs/reference/cli/supabase-migration-new).
Changelog Supabase leído2026-10-14; aviso TLS futuro HTTP no cambia estas reglasSQL.

Evidencia local actual: migración creada mediante CLI2.121.0 por A0 en
`supabase/migrations/20261014210931_professional_private_drafts.sql`; no nombre manual.
Store y19 pruebas SQLruntime reales pasan; suite fresh467 ejecutada por A4 tras
integrar sus32 pruebas API. Primer snapshot propio fresh432 pasó con16 de storage;
se añadieron3 negativos rol/unidad terminada, cuenta closed y edición concurrente.
A4 revisó store/migración independiente sin bloqueantes. A2 revisó rutas/service
incluida frontera business; fixtures Auth simulados no son aceptación
desplegada. Migración no aplicada remota, no grants/provisioning de proveedor.
DDL falla si faltan roles/esquema esperado o ya existen tablas; sin IF NOT EXISTS
que oculte deriva. Roles existentes no se modifican por resolver un error.

### Primer incremento coordinado: agregado privado inactivo

A0/A1 concretaron primero un subconjunto implementado como **dominio puro**;
la persistencia/API posterior se delimita en la actualización D-041 arriba. Crear atómicamente Profile draft
y práctica preparing para un User; GET/PATCH/withdraw propios, con Auth/MFA y CSRF
cuando exista API. No constituye habilitación profesional o declaración verificada.
Endpoints de submit/review/publication/activate/firm/membership/invitation permanecen
gated; no existe bootstrap de revisor ni envío de invitaciones por este incremento.

Campos de perfil: profile_id, owner_user_id, display_name y declared_area privados,
state draft/withdrawn, profile_version, created_at/updated_at/withdrawn_at nullable.
No declared_name legal ni número de cédula en este incremento: pertenecen a la fase
review pendiente de contrato completo. Campos de contexto: context_id,
owner_user_id, profile_id, kind=practice inmutable, state preparing/closed,
context_version, created_at/updated_at/closed_at nullable. Título visible de práctica
se deriva de display_name; no una columna con copia adicional.

Profile y context tienen versiones CAS independientes. PATCH cambia solo
display_name/declared_area y versión del perfil; withdraw exige las dos versiones
actuales y retira ambos en una sola transición, sin efecto parcial. Acciones
editoras disponibles no conceden professional_work/manage_context. No reapertura
automática de withdrawn/closed ni cambio de dueño/kind/capacidades por formulario.
Retirada deniega operación activa inmediatamente aunque purga ocurra a30d.

Eventos mínimos del dominio: actor/objetos lógicos, tipo de transición, fecha UTC
y versiones, sin contenido editado, nombre/área ni otras PII. Vigencia de draft es
última edición real +30d; withdrawn/closed desde retirada/cierre +30d; historia
mínima90d. GET no toca updated_at. No se implementa job/purga/proofAuth en dominio.
La práctica preparing acompaña el corte de su borrador, no queda huérfana ni
retenida indefinidamente; closed acompaña el corte withdrawn del mismo agregado.
PATCH real de perfil mueve el corte del agregado aunque context.updated_at no
cambie por esa edición. No iniciar otro plazo adicional para contexto inactivo.
Los cortes/permisos deben probarse con reloj sintético antes de futuro store.

La lista completa siguiente orienta bloques futuros; **no autoriza sus campos o
transiciones en el primer incremento**. A1 revisa agregado/retención/capacidades
antes de código de almacenamiento y A0 conserva invitación/revisor/relevo pendientes.

Una identidad User tiene 0..1 LawyerProfile y 0..1 práctica propia. Un despacho
LawFirm tiene exactamente un ProfessionalContext. El perfil pertenece a su titular;
la práctica propia a ese profesional; el despacho controla su contexto mediante
capacidades vigentes, sin apropiarse de prácticas de miembros. Autor de creación
y controlador actual no son equivalentes. Una persona puede ser cliente, pero no
hay Client/relación/asunto en este bloque. Office/sedes/direcciones fuera de alcance.

Se conservan los nombres conceptuales; nombres físicos/esquema/roles SQL se fijan
después de revisión. Propuesta: almacenamiento privado en la misma base, separación
lógica por context_id y autorización API/objeto/acción, sin DB por despacho ni vía
privada browser/Data API. No implica elección de facturación/tenant comercial.

| Entidad | Cardinalidad e identidad | Dueño/función |
|---|---|---|
| LawyerProfile | UNIQUE user_id; PK UUID | Titular edita declaración; revisión y publicación separadas |
| CredentialDeclaration | N por perfil, PK UUID; versión explícita | Declaración privada, no copia de documentos |
| ProfessionalReview | N decisiones por perfil/declaración y versión | Revisor autorizado; decisión no editable por solicitante |
| ProfessionalContext | PK UUID; tipo practice/firm inmutable | Práctica con titular único; firm con LawFirm único |
| LawFirm | PK UUID, context_id UNIQUE | Organización operativa, sin acreditar personalidad/representación legal |
| Membership | N históricas por User/contexto, PK UUID | Solo vínculos aceptados; capacidades por vínculo |
| Invitation | Concepto separado, no membresía vigente | Destinatario y mecanismo/vigencia requieren contrato antes de persistir |
| ContextChangeEvent | Eventos mínimos, PK UUID | Historia restringida 90d, sin contenido profesional completo |

Membresía active **o suspended** ocupa el único despacho de la persona; ended no
ocupa. La práctica propia no cuenta como otro despacho. Concurrencia requiere
constraint de unicidad parcial por User y bloqueo transaccional común al aceptar/
finalizar; no basta una consulta previa desde API. pending vive en Invitation, no
en Membership. Reingreso crea una nueva vigencia aceptada; no reanima un registro
ended ni restaura capacidades/asignaciones antiguas.

## Campos mínimos propuestos y clasificación

Los UUID, versiones y tiempos UTC son referencias técnicas para integridad y
concurrencia, no datos públicos ni prueba de identidad jurídica. Todas las familias
son privadas salvo proyección pública expresamente autorizada. Esta lista sirve
para revisión: aprobar PC-05 no convierte nuevos campos opcionales en aprobación.

| Familia | Campos mínimos revisables | Clasificación/finalidad |
|---|---|---|
| Profile | id, user_id, display_name, declared_name, declared_area, state, publication_state, version, created_at, updated_at, submitted_at?, withdrawn_at?, rejected_at? | Nombre declarado privado para contraste; display_name/ámbito declarado solo en proyección voluntaria válida. Sin teléfono, domicilio, experiencia detallada o especialidad verificada |
| Credential | id, profile_id, declared_registration_number, state, version, created_at, updated_at, retired_at?, rejected_at? | Cédula declarada privada, titular/revisor. No CURP/RFC, escaneo, identificación, biometría, imagen, scraping, proveedor o token |
| Review | id, profile_id, declaration_id?, reviewed_profile_version, reviewed_declaration_version?, reviewer_user_id, decision, checked_scope, source_reference, decided_at | Resultado/alcance/fecha/fuente de contraste privados; registro histórico mínimo. source_reference a fuente oficial, sin URL personalizada con PII ni copia de respuesta. No texto libre de investigación |
| Context | id, kind, practice_owner_user_id? o firm_id?, state, version, created_at, updated_at, closure_requested_at?, closed_at? | Ámbito privado; exactamente una rama según tipo. Owner/kind no editables mediante CRUD personal |
| Firm | id, context_id, declared_name, created_by_user_id, created_at | Metadatos privados. Nombre comercial declarado no es registro legal. Sin dirección, RFC, teléfono, sede o presentación pública del despacho |
| Membership | id, context_id, user_id, state, manage_context, professional_work, version, accepted_at, suspended_at?, ended_at? | Dos capacidades aprobadas distintas; privadas. Actor de cambio en evento, no historial completo de valores personales |
| Event | id, actor_user_id?, object_type, object_id lógico, context_id lógico?, transition, occurred_at, object_version | Historia privada mínima; no nombre/cédula/email/token/IP/relato. UUID aún puede ser dato personal; no se presenta como anonimización |
| Invitation/relevo/cierre | Contrato por completar abajo | No persistir contacto, credential/TTL o nueva facultad por inferencia |

No imponer unicidad global de número de cédula sin decisión: repetir declaración
puede ser disputa/suplantación o error y no se resuelve automáticamente con matching.
La etiqueta de alcance propuesta es `registry_record_checked`: acredita contraste
de un registro, **no identidad del titular verificada**, habilitación jurídica o
especialidad. Identidad y publicación no se aprueban por un booleano del formulario.

Review debe referenciar las versiones contrastadas. Cambiar declared_name/cédula
invalida vigencia de la revisión afectada y reabre el proceso; publicación no puede
apuntar a una versión sin revisión vigente. No conservar el perfil completo viejo
como audit. El detalle de fuente/decision/corrección se concreta con A1, sin generar
una taxonomía jurídica ni una columna de notas libre por conveniencia.

## Estados y transiciones

| Familia | Estados de contrato | Regla crítica |
|---|---|---|
| Profile | draft/submitted/under_review/changes_requested/rejected/enabled/suspended/withdrawn | Titular declara/solicita/retira; revisor decide. Sin autoaprobación |
| Publication | private/public | Separada y voluntaria; public requiere versión habilitada/revisión vigente. Retiro/suspensión/cambio relevante quita publicación |
| Credential | declared/review_pending/reviewed/rejected/retired | Revisión por versión/alcance; no expiración de cédula inventada |
| Context | preparing/active/suspended/closure_requested/closed | Práctica activada/despacho creado solo con habilitación revisada; retiro de acceso no espera purga |
| Membership | active/suspended/ended | Solo aceptación explícita activa; suspended mantiene slot pero no facultades profesionales |
| Invitation | pending/accepted/rejected/revoked/expired | No acceso por pendiente; esquema bloqueado sin vigencia/retención/mecanismo |

Crear despacho y administrador inicial deben ser una sola transición explícita:
perfil habilitado + Auth/MFA + cardinalidad libre → firm/contexto + membresía
aceptada de creador con capacidad de administración. La creación es la aceptación
de su propio control inicial, no una invitación que permita autoescalar otro vínculo.
La autoridad sobre la práctica propia no deriva de una membresía de despacho.

Invitar/proponer capacidades, aceptar, suspender, finalizar, modificar capacidades
y relevar administración son acciones separadas. Ningún cambio de capacidades
de sí mismo concede privilegios nuevos. Negación incluye retirar facultad a quien
entró con una sesión/pestaña anterior. Selección de contexto es preferencia; no
permiso ni claim de Auth que sustituya el estado de base.

Último administrador: relevo requiere nombramiento y aceptación; alternativa cierre
controlado con responsable explícito. Nunca se conserva acceso por pendientes ni
se bloquea cierre de cuenta por falta de relevo. Una responsabilidad no genera por
sí sola membresía/capacidad. Propiedad del contexto permanece; no copiar/transmitir
contenido a práctica propia al salir. No hay datos de C04/C05 que trasladar aquí.

## Historial, corte y eliminación aprobados

| Datos | Evento/corte | Tratamiento |
|---|---|---|
| Perfil/credencial/contexto retirados | withdrawn/retired/closed +30d | Borrar/anonimizar; quitar proyección/caché desde retirada, no al día30 |
| Alta rechazada | rejected_at +30d | Borrar datos de alta; mínimo histórico90d separado sin duplicar PII |
| Borrador abandonado | última edición +30d | Borrar borrador; avisar consecuencia. Una edición real actualiza fecha; lectura no reinicia plazo |
| Membership ended | ended_at +30d | Eliminar evidencia mínima, sin cascada a historia90d |
| ContextChangeEvent/review histórico mínimo | decided_at/occurred_at +90d | Eliminar historia mínima; no conservar perfil completo por90d |

Igualdad con umbral significa elegible; timestamps con zona UTC. No crear plazo
extra por frecuencia del job ni retención indefinida para evitar un FK. Suspensión
no es fin/retirada: mantiene slot y estado vigente; no inicia ended_at ni timer30d.
Un estado de revisión pendiente no se llama borrador abandonado por falta de edición
del solicitante; distinguir solicitud en cola de draft. Plazo de revisión sin decisión
no tiene nueva duración aprobada ni SLA numérico.

Review histórico90d conserva únicamente resultado/alcance/fecha/actor/versiones,
sin declared_name/número. Una referencia lógica a objeto borrado no concede acceso
ni mantiene ficha; no FK que bloquee eliminación30d de perfil/cuenta/contexto o
cascada que elimine historia90d. C03 no fija retención de datos jurídicos futuros.
Futuros vínculos negocio necesitarán integridad/retención propias antes de crear FK.

El cierre de cuenta debe retirar facultades dependientes y ordenar retirada de
perfil/práctica/membresías; no borrar automáticamente despacho o datos de otros.
`PostgresIdentityMaintenance` actual no conoce C03: no habilitar su purga de cuenta
con nuevos FK sin secuencia aprobada de retiro/purga y prueba Auth. GetUser negativo
no acredita identidad eliminada. Operación30/90 responsable Arturo y scheduler/
evidencia fiables siguen pendientes; no implementarlos por analogía.

## Ambigüedades concretas remitidas antes de SQL

1. **Invitation:** duración y corte de pending/revoked/rejected/expired, eliminación
   de aceptación/credential y entrega sin secretos en URL. recipient_user_id de
   cuenta confirmada es propuesta mínima A1, no autorización de buscar usuarios
   por email/cedula o enviar correo. No inventar TTL ni guardar contactos privados.
2. **Revisor inicial:** capacidad del producto explícita a Arturo, vinculada a
   User/Auth/MFA sin inferir identidad del login del proveedor. Registro/estado de
   capacidad y quién la concede/revoca; propio perfil necesita otro revisor o queda
   pendiente. No role SQL admin o claims editables como sustituto.
3. **Relevo/cierre:** aceptación, responsable, alcance de administración y evento
   de cierre; no elegir un custodio de soporte ni mantener privilegios del saliente.
4. **Capacidad administrativa con perfil no habilitado/suspendido:** separar
   professional_work de acciones de seguridad/salida. Precisar si manage_context
   queda disponible y a qué personas (asistentes aplazados), sin volver a decidir
   que revocación/cierre de cuenta nunca esperan el relevo.
5. **Campos fuente/revisión y proyección:** A1 valida lista mínima, formatos y
   versión publicada; no añadir libretextos/PII/catálogos legales. Oficina excluida.

Estas preguntas bloquean las tablas/transiciones correspondientes, no reabren
PC-01–PC-05 A. Un subconjunto de preparación puede avanzar solo tras revisión A1
y orden coordinada, con sus propios campos/estados/retención completos.

## Controles verificables previos a implementación

Ver [matriz C03](../security/professional-context-access.md). Contratos backend
deben concretar lectura/escritura/transiciones/grants por campo y rol; RLS FORCE
y transacciones con principal verificado y contexto local. Lock por User al aceptar
slot, y por contexto/vínculo al cambiar vigencia/capacidades; orden común evita
deadlocks y doble administrador/aceptación. Revalidar autorización al commit.
No TRUNCATE, grants, cambios de owner o funciones SECURITY DEFINER en runtime.

Entrega documental: revisión cardinalidades/estados/minimización/30–90 y límites,
sin migración, SQL remoto, tabla, dato real o proveedor nuevo. A1 revisa antesSQL;
A0 integra decisiones y gate C02 HTTP real. Auth sintético no es aceptación de C03.
