# Contrato API — Profesionales y contextos (C03)

Actualización 2026-10-14 — D-041: Arturo aprobó Q-C03-01..03 A. Las tablas
históricas de alternativas se conservan como antecedente; no requieren nueva
aprobación. TTL interno 24h, recibo terminal 30d y eventos 90d; bootstrap manual
review_professionals y resolución excepcional de cierre con capacidad separada.
No se han concedido capacidades reales ni definido el procedimiento jurídico de
revisión. Este incremento frontend solo prepara perfil privado y práctica inactiva;
no implementa invitaciones, review, publicación, despachos o clientes.

Fecha: 2026-10-14. Base asignada `338617`. Autor A1/A5; revisión A0/A2 pendiente.
**PC-01..PC-05 A aprobadas por Arturo el 2026-10-14** según orden de A0. Este
contrato concreta esas decisiones; no instala endpoints, tablas, permisos o UI.
El encabezado Proposed del [checkpoint](../checkpoints/professional-contexts.md)
es anterior a esa aprobación; A0 conserva el registro de decisiones vigente.

Dependencias: [Identity HTTP](identity-api.md),
[flujos C03](../ux/professional-contexts-flows.md) y modelo/matriz C03 de A2 en
preparación. Este contrato debe reconciliarse con esos documentos antes de SQL.
No elegir otro proveedor, sede, precio, envío o transporte de autenticación.

## Incremento autorizado y gates

Primero: **perfil privado en borrador y práctica en preparación/inactiva**,
persistidos para el propio actor. No habilitación profesional, proyección pública,
despacho activo, membresía, invitación, revisor real ni evidencia jurídica.
Crear el perfil crea su práctica en la misma transacción; guardar un borrador no
concede `professional_work` ni `manage_context`.

El contrato completo de transiciones está diseñado abajo, pero las familias
review, publication, activation, firm, membership, invitation y handoff conservan
gates explícitos. Submit no convierte un borrador en una solicitud que nadie pueda
revisar: hasta bootstrap/procedimiento de revisión disponibles, devuelve
`FEATURE_UNAVAILABLE` y preserva borrador/fecha de edición. No respuestas simuladas.
API no implementada aún no se describe como disponible por aparecer aquí.

Tres detalles pendientes se concentran en Q-C03-01..03 al final; ninguno reabre
los cinco paquetes aprobados. Invitaciones no se crean ni aceptan sin TTL y
retención acordados. No tabla de invitaciones, tokens/invite claims, SMTP nuevo
o grants de actor real en el primer incremento. Offices/sedes aplazadas.

## Transporte, actor y concurrencia

Todas las rutas privadas usan cookie opaca, sesión válida y **aal2**, incluso
alta/edición del propio borrador. Si falta MFA, acceder al flujo C02; no exigir
perfil profesional para enrolar/verificar MFA. Cookies, Origin, CSRF y rechazos
de bearer conservan exactamente Identity. Ningún endpoint acepta actor, user_id
propietario, rol global, assurance, JWT o estado de verificación del navegador.
`recipient_user_id` es destinatario de una operación limitada, jamás identidad
del actor. Todos los POST/PATCH requieren JSON, CSRF y Origin antes de efectos.

Sin query strings en rutas de entidad. Los listados privados usan solo
`cursor` opaco de paginación y `limit` entero 1..100, default 20; no búsqueda por
correo/nombre/cédula, filtro arbitrario o listado de usuarios Auth. Cursor no es
credencial ni autorización; cada página vuelve a filtrar el ámbito vigente.
JSON UTF-8 hasta 8 KiB, propiedades extra rechazadas y errores sin `input`/echo.
UUID válidas para objetos; estado/cardinalidad/permisos se comprueban en servidor.

Respuestas privadas: `Cache-Control: no-store`, `Referrer-Policy: no-referrer`,
sin prerender/cache compartida/localStorage/analytics. No datos de cédula en URL,
logs, nombre de archivo o encabezados. Cédula es dato profesional personal, no un
token de acceso; se minimiza igualmente. No documentos/ID/biometría en cuerpos.

Entidades llevan `version` entero positivo asignado por servidor. Cambios exigen
`expected_version` del objeto; versión obsoleta produce 409 sin efectos. Cambiar
estado o dato revisado invalida versiones dependientes; el cliente no sobrescribe
tras 409. Autorización precede el chequeo de versión para no revelar objetos ajenos.
Nunca reintentar automáticamente mutación, incluso con timeout; reconciliar por
GET autorizado antes de otra acción. Creación única se resuelve con cardinalidad
transaccional y GET propio, sin duplicar perfil/práctica después de respuesta incierta.

En una transacción: sesión/actor vigentes, propietario, contexto y capacidades,
versiones, estado final y referencias del mismo ámbito. Salida/suspensión concurrente
gana frente a una acción que no haya confirmado su frontera de autorización.
Bloquear slot de despacho del destinatario antes de activar membresía; active y
suspended cuentan. No dependencia de claims antiguos o contexto aportado como permiso.

## Datos exactos y vistas

`DraftFields` del primer incremento: `display_name` string 1..120 y
`declared_area` string/null hasta 240. No legal_name/cédula en persistencia
inicial. En fase review gated, `DeclarationFields`: legal_name string 1..200 y
registration_number string de 1..32 dígitos ASCII, conserva cero inicial. Un borrador puede estar incompleto. Validar
solo forma/tamaño, no validez jurídica por longitud. Texto plano, nunca HTML;
recorte exterior de texto declarado no se aplica a credenciales Auth. No campo
email, CURP, RFC, domicilio, foto, especialidad verificada o experiencia certificada.

Vistas privadas mínimas:

```typescript
type DraftFields = { display_name: string; declared_area: string | null };
type ProfileState = "draft" | "submitted" | "under_review" | "changes_requested"
  | "rejected" | "enabled" | "suspended" | "withdrawn";
type ContextState = "preparing" | "active" | "suspended" | "closure_requested" | "closed";
type Capability = "manage_context" | "professional_work";
type MembershipState = "active" | "suspended" | "ended";
type ProfileView = {
  id: string; version: number; state: ProfileState;
  fields: DraftFields; publication: "private" | "public";
  review: null | { outcome: "changes_requested" | "rejected" | "enabled" | "suspended";
    scope: "registry_record_checked" | "none"; decided_at: string };
  allowed_actions: string[];
};
type ContextView = {
  id: string; version: number; kind: "practice" | "firm";
  title: string; state: ContextState;
  capabilities: Capability[]; allowed_actions: string[];
};
type MembershipView = {
  id: string; version: number; context_id: string; state: MembershipState;
  capabilities: Capability[];
};
```

`allowed_actions` es una ayuda de presentación derivada del actor y gates, no
una autorización reutilizable ni rol global. En incremento inicial: profile draft,
publication private, review null; práctica preparing, capabilities vacías. Title de practice se deriva del display_name propio; no es otro campo persistido.
No campos inventados en SessionView C02. Timestamps ISO8601 UTC; nunca tokens/claims
del proveedor o emails de terceros. GET de contexto no devuelve clientes/asuntos.

ReviewerView de fase gated extiende perfil con DeclarationFields privada vigente y versión enviada;
solo revisor asignado autorizado recibe lo mínimo para cotejo. No archivo de
identidad, cuerpo descargado de fuentes externas, password o notas jurídicas.
`source` es identificador de fuente oficial revisada, no URL libre que el servidor
visite; `scope` solo `registry_record_checked`. Resultado no certifica vínculo
al titular ni habilitación jurídica. Procedimiento antisuplantación pendiente.

## Matriz de acciones

Todos los actores privados necesitan sesión/aal2; filas no concedidas se deniegan.

| Actor vigente | Acciones | Límites |
|---|---|---|
| Titular del borrador | Crear/leer/editar/retirar propio perfil y preparar práctica | Primer incremento; no enabled/publication/firm/roles por edición |
| Profesional enabled | Activar propia práctica, pedir publicación y crear despacho bajo gates | Revisión habilita operación de plataforma con alcance limitado; no identidad/titularidad garantizadas |
| Miembro active con professional_work | Ver su contexto operativo y actuar profesionalmente según futuras asignaciones | C03 no contiene recursos jurídicos; pertenencia no abre relaciones |
| Miembro active con manage_context | Administrar metadatos/membresías, proponer capacidades/relevo, suspender/finalizar otros | No evidencia profesional privada ajena ni contenido jurídico por ser administrador |
| Miembro suspended/ended | Ver resultado mínimo de su vínculo y finalizar vínculo propio suspended | Sin nuevas operaciones del despacho, aun con capacidades históricas |
| Destinatario de invitación | Ver/aceptar/rechazar únicamente invitación propia vigente | Familia bloqueada Q-C03-01; no permiso durante pending |
| Revisor de producto explícitamente habilitado | Cola mínima, claim y decisión de perfil ajeno según asignación | Familia bloqueada Q-C03-02; no autoaprobación ni administración de despacho por ese permiso |
| Responsable de cierre aceptado | Acciones de gobierno delimitadas del cierre | Familia bloqueada Q-C03-03; no permiso jurídico implícito ni soporte omnipotente |

La práctica propia permanece independiente de la membresía de despacho. Suspensión
profesional bloquea trabajo profesional, sin quitar por inferencia una participación
legítima como cliente. Cuenta inactiva/closed bloquea todas las sesiones según C02;
MFA o login posterior no reactiva perfil, contexto o membresía.

## Rutas del primer incremento

| Método/ruta | Cuerpo exacto | Éxito y efecto |
|---|---|---|
| GET `/api/professional/profile` | Sin cuerpo/query | 200 `{profile:ProfileView|null,practice_context:ContextView|null}`; solo actor propio |
| POST `/api/professional/profile` | `DraftFields` | 201 misma vista; crea profile draft y práctica preparing una sola vez en transacción; existente → 409 STATE_CONFLICT |
| PATCH `/api/professional/profile` | `{expected_version:number,fields:Partial<DraftFields>}` | 200 misma vista; al menos un campo conocido; solo draft/changes_requested cuando esa etapa se habilite |
| POST `/api/professional/profile/withdraw` | `{expected_version:number,expected_context_version:number}` | 200 misma vista retirada; retira trabajo/publicación si alguna existiera, prepara cierre de práctica sin borrar referencias de terceros |
| GET `/api/professional/contexts` | Paginación definida | 200 `{contexts:ContextView[],next_cursor:string|null}`; inicial solo práctica propia preparing, sin contexto de terceros |

Withdraw inicial: profile withdrawn/publication private; práctica closed porque no
existen dependencias de negocio/membresía en este incremento. Ambas versiones
cambian y comienza retención PC-05. Una petición repetida con versiones actuales devuelve mismo resultado sin nuevos
eventos/fechas; versiones antiguas siguen 409. No borrado físico inmediato ni recreación por
POST mientras exista registro retirado. Una futura reapertura/restauración requiere
contrato explícito, sin evadir rechazo, revisión o retención.

GET iniciados por usuario siguen actividad C02; polling incidental no prolonga
sesión. Interfaz no sondea automáticamente estas rutas como mecanismo de vida.

## Rutas completas preparadas, todavía gated

Cada ruta devuelve 403 FEATURE_UNAVAILABLE antes de efectos si su familia no está
habilitada. Estado, capacidades y pertenencia se verifican además del gate.

| Método/ruta | Cuerpo exacto | Precondición y éxito esperado tras habilitar |
|---|---|---|
| POST `/api/professional/profile/submit` | `{expected_version:number,declaration:DeclarationFields}` | Titular; draft/changes_requested con declaración privada mínima completa → 200 profile submitted con snapshot inmutable de declaración; Q-C03-02 |
| GET `/api/professional/reviews` | Paginación | Revisor vigente, solo cola mínima asignable; 200 `{reviews:[{id,profile_id,version,state}],next_cursor}`; sin perfiles arbitrarios |
| POST `/api/professional/reviews/{review_id}/claim` | `{expected_version:number}` | Revisor ajeno al titular, pendiente/asignable → 200 ReviewerView under_review, claim exclusivo; Q-C03-02 |
| POST `/api/professional/reviews/{review_id}/decision` | `{expected_version:number,outcome:"changes_requested"|"rejected"|"enabled",reason_code:string,source:"official_registry"|null,scope:"registry_record_checked"|"none"}` | Revisor asignado no titular, snapshot vigente; 200 profile final; enabled exige fuente/cotejo procedimental aprobado; nunca publicación automática |
| POST `/api/professional/profile/publication` | `{expected_version:number,visibility:"private"|"public"}` | Titular; public solo enabled y revisión vigente; 200 profile; private retira proyección inmediatamente |
| POST `/api/professional/contexts/{context_id}/activate` | `{expected_version:number}` | Solo práctica propia preparing + profile enabled; 200 ContextView active; no activa despacho arbitrario |
| POST `/api/professional/firms` | `{title:string,initial_capabilities:Capability[]}` | Profesional enabled sin slot de despacho; lista única incluye manage_context, professional_work solo si lo pide explícitamente; 201 `{context:ContextView,membership:MembershipView}` atómicos; Q-C03-03 |
| GET `/api/professional/contexts/{context_id}` | Sin cuerpo/query | Miembro vigente autorizado/propietario práctica; 200 ContextView mínimo; no expedientes |
| GET `/api/professional/contexts/{context_id}/memberships` | Paginación | manage_context; 200 roster `{memberships:[{id,user_id,version,state,capabilities}],next_cursor}`; sin email/cédula/perfil privado |
| POST `/api/professional/contexts/{context_id}/invitations` | `{expected_version:number,recipient_user_id:string,capabilities:Capability[]}` | manage_context, UUID existente confirmado y destino permitido; 201 invitación mínima pending; Q-C03-01 |
| GET `/api/professional/invitations` | Paginación | Solo invitaciones dirigidas al actor; 200 `{invitations:[{id,version,context_id,context_title,state,capabilities}],next_cursor}`; Q-C03-01 |
| POST `/api/professional/invitations/{invitation_id}/accept` | `{expected_version:number}` | Destinatario propio, vigente, profile enabled, sin slot ocupado; 200 MembershipView active; consume invitación una sola vez; Q-C03-01 |
| POST `/api/professional/invitations/{invitation_id}/decline` | `{expected_version:number}` | Destinatario propio pending → 200 `{id,version,state:"rejected"}`; Q-C03-01 |
| POST `/api/professional/invitations/{invitation_id}/revoke` | `{expected_version:number}` | Administrador del contexto pending → 200 `{id,version,state:"revoked"}`; Q-C03-01 |
| POST `/api/professional/memberships/{membership_id}/suspend` | `{expected_version:number}` | Administrador del contexto sobre otro miembro; 200 MembershipView suspended, retira capacidades efectivas; último admin según cierre abajo |
| POST `/api/professional/memberships/{membership_id}/end` | `{expected_version:number}` | Administrador sobre otro; 200 MembershipView ended con continuidad de gobierno evaluada |
| POST `/api/professional/memberships/{membership_id}/leave` | `{expected_version:number}` | Solo titular, active/suspended, aun si perfil/contexto suspendidos; 200 MembershipView ended o 202 resultado parcial de cierre abajo |
| POST `/api/professional/contexts/{context_id}/handoffs` | `{expected_version:number,recipient_membership_id:string,purpose:"administration"|"closure"}` | Administrador propone a miembro active del mismo ámbito; 201 `{id,version,state:"pending",purpose}`; sin facultad hasta aceptación; Q-C03-03 |
| POST `/api/professional/handoffs/{handoff_id}/accept` | `{expected_version:number}` | Destinatario propio active, estado/versión vigentes → 200 `{id,version,state:"accepted",purpose}`; grant específico de gobierno solo por transición aprobada; Q-C03-03 |
| POST `/api/professional/contexts/{context_id}/close` | `{expected_version:number}` | Responsable de cierre aceptado, dependencias comprobadas → 200 ContextView closed; Q-C03-03 |

`title` 1..120 de texto plano; no certifica personalidad jurídica. Capability[]
de una o dos entradas únicas del enum; nunca custom roles o comandos SQL.
`reason_code` solo `incomplete_declaration`, `registry_mismatch`,
`identity_binding_unresolved`, `out_of_scope`, `registry_record_checked`.
No razón libre con cédulas/relatos. Review enabled no se emite con scope none.
Suspend/withdraw/edición de identidad invalidan publicación/revisión vigente;
la edición relevante de perfil enabled se hace mediante nuevo borrador/revisión,
no PATCH directo: esa ruta de reapertura queda cerrada hasta contrato específico.

No endpoint genérico PATCH de capacidades. Reducción de facultades se aplica por
suspensión/finalización autorizada; administración adicional por handoff aceptado.
Cambios arbitrarios/reativación suspended o concesiones de trabajo a un miembro
existente requieren completar transición/matriz, sin usar edición de perfil.
No DELETE físico, export, transferencia de relación, asistente o Office en C03.

## Invitaciones, relevo y cierre sin permisos residuales

Identificador de invitación no es bearer: aceptar exige identidad verificada del
destinatario y aal2. UUID compartido por su titular identifica destinatario; no
buscador global ni lookup de email. Invitación pending no crea Membership ni ocupa
slot por sí sola. El admin no puede aceptar por otra persona o sustituir destinatario.
Cambios de capacidades antes de aceptación invalidan la versión previa.
No entrega externa, SMTP, enlace/token/código de invitación, TTL inventado o renovación.
Cuando se acuerde TTL, creación devuelve expires_at y aceptación comprueba reloj
servidor dentro de la transacción; hasta entonces ambas operaciones permanecen gated.

Handoff registra nominador, destinatario de mismo contexto, propósito, versiones y
aceptación auténtica. El destinatario no hereda acceso jurídico. Cambio de estado
del destinatario, nominador o contexto obliga a reevaluar antes de aceptar; no
promesas de rol perpetuas. Historial/retención del acuerdo se reconciliarán con
modelo y Q-C03-03; no se persiste ni conceden facultades reales en primera etapa.

Si sale/suspenden al último admin sin relevo/responsable aceptado, **la revocación
sí ocurre** y el contexto pasa a closure_requested, sin trabajo/administración
normal. Resultado de leave/end: 202
`{membership:MembershipView,context:ContextView,resolution:"responsibility_required"}`.
No afirmar contexto closed o responsable asignado; la finalización del cierre
queda bloqueada hasta el mecanismo Q-C03-03. Nadie conserva admin por ser antiguo
creador; no asignar soporte/revisor como custodio de datos. La misma regla aplica
al cierre de cuenta por el flujo C02 autorizado: no puede depender de obtener
aal2/perfil enabled del usuario que se revoca ni bloquear el cierre de cuenta.
No se crea un endpoint Auth de cierre nuevo en este contrato.

Profesional_work activo/suspendido y assignments residuales se retiran en la
frontera; práctica propia y participación cliente se evalúan aparte. Relevo no
mueve relaciones al sucesor/práctica. Contextos con dependencias futuras no se
borran en cascada a 30 días; se reporta bloqueo de eliminación con responsable,
sin retención indefinida silenciosa ni restauración de permisos.

## Proyección pública futura

GET `/api/public/professionals/{public_id}` solo tras gate publication y profile
enabled/public/revisión vigente. 200 exacto:
`{public_id,display_name,declared_area,review:{scope:"registry_record_checked",checked_at}}`.
No Auth User ID, cédula, email, historial, reviewer, lista de clientes, membresía,
dirección o permisos. Public_id propio de la proyección, nunca subject Auth.
Retiro/suspensión invalida proyección en siguiente lectura; 404 igual a inexistente.
Inicialmente no-store, sin build/prerender con datos profesionales. No directorio,
búsqueda, ranking, SEO de profesionales o cachés fuera de contrato C06.
Etiqueta visible «Datos de cédula cotejados», no «Identidad verificada» ni promesa
de calidad/resultados/habilitación jurídica. Alcance y texto requieren LEGAL REVIEW
REQUIRED; matching público no implementado por esta ruta futura.

## Errores y aceptación

Envelope exacto Identity `{error:{code,message}}`, mensajes fijos sin datos.

| HTTP | code | message |
|---|---|---|
| 401 | AUTHENTICATION_REQUIRED | Se requiere iniciar sesión. |
| 403 | REQUEST_FORBIDDEN | La solicitud no está permitida. |
| 403 | MFA_REQUIRED | Completa la verificación adicional. |
| 403 | FEATURE_UNAVAILABLE | Esta función aún no está disponible. |
| 404 | RESOURCE_UNAVAILABLE | No se encontró un recurso disponible. |
| 409 | VERSION_CONFLICT | La información cambió. Actualiza antes de continuar. |
| 409 | STATE_CONFLICT | No es posible realizar esta acción en el estado actual. |
| 409 | FIRM_SLOT_OCCUPIED | Ya tienes un vínculo de despacho vigente. |
| 422 | INVALID_REQUEST | Revisa los datos de la solicitud. |
| 429 | RATE_LIMITED | Inténtalo de nuevo más tarde. |
| 503 | PROFESSIONAL_UNAVAILABLE | La operación no está disponible temporalmente. |

Identificador ajeno/inexistente mismo 404. FIRM_SLOT_OCCUPIED solo para slot del
propio actor tras autorización; no revela otro despacho. Estado/version no se
revelan para objetos ajenos. 401 elimina vistas privadas; 503 no redirige como si
fuera logout, no afirma vigencia nueva y no permite nueva mutación. 202 parcial
se reserva a revocación ya efectiva con cierre pendiente; no fake-success.

A7/A2 deben verificar OpenAPI/cuerpos/errors, own draft y práctica atómica,
ausencia de permisos iniciales, CAS/duplicados, contexto/ID ajenos, aislamiento
de conexión, revisión ajena/sin self-review/snapshot cambiado, publicación sin
datos privados y retirada, invitación pendiente/ajena/reusada/vencida, slot único
con aceptación concurrente, admin sin lectura jurídica, salida simultánea a
operación, último admin/account-close sin residuales y cleanup de 30/90 aprobado.
Pruebas sintéticas SQL real requeridas; mocks no acreditan proveedor/operación real.

## Tres detalles para decidir, no una nueva aprobación de PC-01..05

Estas **tres preguntas** preparan una decisión revisable; no están aplicadas.

| ID | Pregunta | A propuesta para revisar | B alternativa |
|---|---|---|---|
| Q-C03-01 | ¿Qué vigencia y retención tendrán las invitaciones internas por UUID confirmado? | TTL 24 horas; terminal accepted/rejected/revoked/expired conserva recibo mínimo 30 días y audit sin contenido 90 días; sin SMTP/búsqueda/email, destinatario comparte su UUID propio y servidor comprueba User activo/correo confirmado | TTL 7 días, mismo recibo mínimo/retención y canal interno. Si se aplaza la elección, creación/aceptación siguen cerradas |
| Q-C03-02 | ¿Cómo se identifica y habilita al revisor de producto de Arturo? | Grant manual específico `review_professionals` a una identidad de aplicación confirmada/aal2 nominada por Arturo, con auditoría/retirada, sin autoalta, self-review o permisos de proveedor; procedimiento de correspondencia titular y fuente oficial revisado antes de decisiones enabled | Mantener revisión/submit/habilitación/publicación cerradas; continuar guardando borradores privados sin revisor real |
| Q-C03-03 | ¿Quién resuelve el cierre si no existe relevo aceptado y cómo se registra su responsabilidad? | Nominación y aceptación in-app de miembro para administración/cierre; excepcionalmente Arturo puede resolver gobierno con capacidad separada `resolve_context_closure` concedida expresamente, sin leer contenido jurídico ni facultad automática de reviewer; registro mínimo/versionado, retención del acuerdo según fin de vínculo 30 días y eventos 90 | No habilitar despacho activo hasta tener responsable de cierre aceptado y mecanismo para pérdida simultánea de administradores. Account-close/retirada siguen efectivos; cierre final queda pendiente, sin custodio implícito |

Q-C03-01 propone números nuevos explícitamente; no deducirlos de D-032. Q-C03-02/03
no conceden roles por escribirlos aquí. Fuente/criterio profesional, disputas y
datos reales requieren **LEGAL REVIEW REQUIRED**. Resolver parámetros y modelo
por entidad antes de SQL; el primer incremento no depende de estos grants/invites.

Verificación de esta tanda: contratos C02/PC-01..05 reconciliados sin ampliar
SessionView. El dominio puro `apps/api/src/abogalia_api/professional_contexts/domain.py`
y sus 20 pruebas sintéticas están preparados y revisados independientemente por A2,
sin bloqueantes. Validan propiedad, UUID no nulo, CAS de ambas versiones, retiro
atómico, inmutabilidad, minimización y fronteras de 30/90 días. El texto privado se
normaliza a NFC y se recorta; una edición sin cambio efectivo no produce evento ni
extiende retención. La práctica preparing acompaña el vencimiento del borrador
(última edición real + 30 días); closed acompaña withdrawn_at + 30 días.

Esto no implementa HTTP, Auth, persistencia, unicidad global por User ni borrado:
el adaptador futuro debe autenticar el actor, aplicar MFA/CSRF y garantizar esas
restricciones transaccionales. El cálculo de vencimiento no ejecuta una purga.
No secretos/PII reales, migración, envío o commit en esta entrega. Las rutas y las
pantallas descritas siguen sin implementar.

## Evidencia frontend del primer incremento

Preparadas `/profesional` y `/profesional/contextos` con cliente mismo origen,
sesión C02 y gate aal2. Guardado privado y retiro con ambas versiones; 409 bloquea
escrituras hasta actualizar, 401/MFA limpia contenido y muestra acceso/MFA. No se
reintentan mutaciones; CSRF se obtiene antes de cada escritura y permanece en
memoria. Las vistas rechazan permisos profesionales y estados fuera del subset.
Consulta propia sin efectos de edición; retiro informa 30d de datos/90d de historia,
sin prometer borrado inmediato.

Once comprobaciones sintéticas del cliente pasan con fetch simulado: respuestas
privadas, rechazo de estados/capacidades incompatibles, mismo origen, CSRF,
CAS de retiro, 401/403/409/503 y redacción/red sin retry. No constituyen navegador
ni integración de Auth/DB reales. La integración de rutas global y verificación
navegador quedan a cargo de A0; lint/tipos/build locales pasan con ambas rutas registradas por A0.
