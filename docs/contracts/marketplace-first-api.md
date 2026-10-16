# Contrato propuesto — Catálogo → búsqueda → solicitud a profesional

Fecha: 2026-10-16. Baseline de inspección: `7b88b4e`, rama `codex/identity-design`.
**Proposed; requiere checkpoint y parámetros aprobados antes de código/tablas.**
Arturo eligió este recorrido inicial. La elección no aprueba taxonomía, publicación,
permisos nuevos, retención jurídica o condiciones comerciales. Sin agenda, reserva,
pagos, suscripciones, documentos, IA ni envío de correo de producto en este corte.

Fuentes: [C03 API](professional-contexts-api.md),
[C03 modelo](../data/professional-context-schema.md),
[C04](../checkpoints/c04-requests-conflicts.md),
[C06](../checkpoints/c06-discovery-catalog.md),
[Identity API](identity-api.md), [decisiones](../decisions/decision-log.md).
Este contrato propone límites verificables, no describe endpoints ya disponibles.

## 1. Qué existe y qué falta

| Elemento inspeccionado | Implementado localmente | Pendiente para este recorrido |
|---|---|---|
| `professional_contexts/router.py` | GET/POST/PATCH perfil propio, withdraw y listado de contextos; validación estricta/extra forbid, JSON máximo8KiB, errores saneados y no-store | Router público, proyección, filtros, solicitudes; no reutilizar prefijo privado para búsquedas públicas |
| `professional_contexts/domain.py` | Profile draft/withdrawn; Practice preparing/closed, versiones CAS; edición/retirada propias | Profile enabled y publicación, revisión vigente, contexto active y destinatario habilitado |
| `professional_contexts/service.py` | `identity.authenticated(..., business=True)`; MFA aal2; sujeto servidor; vista publication private/review null/capabilities vacías | Servicio público de campos aprobados y elegibilidad de recibir solicitudes; no convertir private en public por serialización |
| `professional_contexts/storage.py` y modelo C03 | Agregado propio y eventos mínimos en unidad de conexión C02, según contrato de datos | Modelo C03 ampliado y retiro concurrente coherente con solicitudes; migración C03 remota no aplicada según README |
| Catch-all profesional | Familia no implementada →403 FEATURE_UNAVAILABLE, sin falso éxito | Review/publication/activation/membership según gates y procedimiento; permiso de revisor no implica concesión real |

Referencias de implementación:
[router](../../apps/api/src/abogalia_api/professional_contexts/router.py),
[domain](../../apps/api/src/abogalia_api/professional_contexts/domain.py),
[service](../../apps/api/src/abogalia_api/professional_contexts/service.py),
[storage](../../apps/api/src/abogalia_api/professional_contexts/storage.py).

No hay profesionales publicables por ese incremento privado. No completar la ausencia
con datos reales ni fixtures publicados. Antes de habilitar este contrato hacen falta
aceptación operativa C02, C03 de confianza/publicación/contexto activo y decisiones
C04/C06 específicas. La selección del recorrido no elimina estas dependencias.

## 2. Límites de publicación y descubrimiento

Directorio muestra profesionales publicados voluntariamente con revisión vigente;
no vende consultas ni publica ServiceOffering. No precio, compra, calendario,
"disponible ahora", ranking de calidad, reputación, patrocinio o garantía de admisión.
Solicitar atención abre una evaluación; no celebra acuerdo ni certifica ausencia de
conflicto. Ofertas transaccionables requieren C05/C07/C08 y condiciones propias.

Criterio propuesto de elegibilidad de una entrada: perfil enabled, publicación public
sobre versión revisada vigente, contexto destinatario activo y vínculo profesional
vigente. Requerir además aceptación expresa de recibir solicitudes, con semántica y
control pendientes de aprobar: no existe hoy ese campo. Este corte recomienda listar
solo entradas aptas para recibir solicitud; si se decide directorio informativo más
amplio, debe distinguirse explícitamente `requestable:false`, sin CTA que prometa envío.
No publicar un contexto de despacho completo porque un miembro publique su perfil.

Proyección pública de ficha propuesta, cerrada por esquema de respuesta:

```typescript
type PublicProfessional = {
  public_id: string;                  // UUID opaco exclusivo profesional+contexto
  display_name: string;               // 1..120, texto plano
  declared_area: string | null;       // máximo240; declaración, no credencial
  review: { scope: "registry_record_checked"; checked_at: string };
  listing_version: number;            // entero positivo; publicación/destinatario
  public_context_label: string;      // etiqueta pública aprobada, máximo120 propuesto
  requestable: boolean;               // hecho derivado actual, no autorización
};
```

`display_name/declared_area/review` conservan la proyección futura C03; la vinculación
inmutable de public_id a profesional+contexto y `listing_version/public_context_label/
requestable` son **extensiones propuestas**, no campos implementados/aprobados.
La etiqueta permite distinguir práctica/despacho al confirmar envío sin revelar el
context_id. Su fuente y publicación voluntaria deben aprobarse antes de implementarla;
no deducir nombre público de despacho de un metadato privado ni publicar roster.
Cambiar contexto requiere nueva entrada/public_id y elección expresa, nunca redirigir
el identificador antiguo a otro destinatario. Si no hay etiqueta aprobada que aclare
el ámbito, no habilitar envío ambiguo. No nuevas jurisdicciones/modalidades/taxonomías
en la variante mínima recomendada.

Prohibidos: Auth subject/user_id, context_id privado, cédula, legal_name, email, teléfono,
reviewer, membresías/capacidades, dirección privada, clientes, motivo de suspensión,
relato y fechas privadas. Serializer allowlist en servidor; no `.model_dump()` del
agregado privado ni SELECT amplio seguido de ocultamiento en React. La revisión indica
solo cotejo de registro, no identidad/habilitación jurídica/especialidad certificadas.

## 3. Rutas públicas y búsqueda acotada

| Ruta propuesta | Entrada | Respuesta |
|---|---|---|
| GET `/api/public/professionals` | Query cerrada descrita abajo, sin cuerpo |200 `{items:PublicProfessional[], next_cursor:string|null, order:"display_name"}` |
| GET `/api/public/professionals/{public_id}` | UUID válido, sin query/cuerpo |200 `{professional:PublicProfessional}` o404 uniforme |

Variante mínima recomendada, **pendiente aprobación**: filtrar solo nombre/ámbito
declarado ya publicables C03. `name` y `declared_area` son texto público acotado1..80
caracteres cada uno tras NFC/recorte, con máximo combinado80; omitir campo no usado,
no enviarlo vacío. Sin `q` libre que invite a narrar el problema. Rechazar caracteres
de control; comparación case-insensitive sobre texto público normalizado, literal,
no regex ni sintaxis de consulta. `%`/`_` se tratan literalmente, no comodines SQL.
Intersección si ambos filtros están presentes; sin filtro, listado orgánico general.
El campo de ámbito sigue siendo declaración profesional, no especialidad verificada.
UI pide solo nombre/ámbito, advierte no introducir relato ni datos de terceros.

Otros límites técnicos propuestos: `limit` decimal canónico entero1..50, default20;
`cursor` opaco máximo512 caracteres. Un solo valor por parámetro; desconocidos,
duplicados, vacío, exceso combinado, entero negativo o booleano como entero →422
INVALID_REQUEST. Query total máximo2048 bytes UTF-8 propuesto. La API no acepta email,
relato, ubicación precisa ni filtros por datos privados. No búsqueda fonética,
personalizada, matching por relato o ampliación silenciosa de criterio.

Sin resultados devuelve200 lista vacía. Orden recomendado: clave de nombre normalizado
más public_id como desempate estable; normalización/colación documentadas y fijadas.
No se presenta como mejor calidad ni permite ordenar por pago, aceptación o datos
privados. Jurisdicción/modalidad/códigos editoriales y `/directory-filters` son variante
futura C06, no requeridos ni recomendados para este corte; necesitan atributos/fuentes,
editor, permisos y datos aprobados antes de contrato e implementación propios.

Cursor versionado y validado por servidor, ligado a filtros/orden y limitado en tamaño,
sin texto de búsqueda/PII decodificable; no contiene secretos ni es autorización.
No aceptar SQL, offset arbitrario o identidad/contexto desde cursor. Desajuste/formato
inválido →422. Cada página reevalúa publicación; sin snapshot histórico que resucite
perfiles retirados. Cambios de nombre pueden exigir reiniciar lista; no prometer una
foto consistente de lista cambiante. No conceder lectura privada por adivinar cursor.

No persistir consultas/resultados por defecto es propuesta C06 pendiente de aprobación;
no implica que navegador/red/proveedor carezcan de rastros. Búsqueda texto pública sigue
pudiendo contener datos personales por error: sin analytics/autocaptura, sin eco de input
en errores y sin logs de query. API pública también no-store en este corte; no tocar
reglas actuales `/assets/*`. Rechazar Authorization presente conforme al transporte
vigente; no sesión como ranking personalizado ni Set-Cookie por listado anónimo.

## 4. Transporte privado de solicitud

Cookie opaca C02, comprobación activa y usuario confirmado/activo; no bearer ni Auth
subject enviado por navegador. CSRF y Origin exacto antes de efectos, JSON estricto,
propiedades desconocidas rechazadas, sin eco de input. No credenciales en URL ni
localStorage. Todas las respuestas no-store/no-referrer, errores incluidos.

Solicitante utiliza su identidad confirmada; no necesita crear un perfil profesional.
Exigir o no aal2 al solicitante es **decisión pendiente**: no copiar el requisito aal2
del router C03 a clientes automáticamente. El destinatario profesional conserva MFA y
capacidad/vínculo vigentes. Admin de despacho, revisor profesional y soporte no reciben
lectura de solicitudes por esos cargos. No crear rol/capacidad nueva en este contrato.

Propuesta primer envío: composición local efímera sin guardar borrador servidor; el
solicitante revisa destinatario y contenido y hace un POST que crea solicitud enviada.
Borrador persistente, editar relato enviado, intake ampliado/partes, reasignación y
comunicación libre quedan fuera hasta contratos separados C04 aprobados.

```typescript
type SendRequest = {
  public_id: string;
  expected_listing_version: number;
  description: string;
  disclosure_version: string;         // texto informativo revisado presentado
  disclosure_acknowledged: true;      // acción expresa, no consentimiento universal
  command_id: string;                 // UUID aleatorio por intención; no token
};
type RequestView = {
  id: string;
  version: number;
  state: "submitted" | "responded" | "withdrawn";
  recipient: { public_id: string; display_name: string; public_context_label: string };
  submitted_at: string;               // ISO8601 UTC
  description: string;               // solo actor participante autorizado
  response: null | { outcome: "can_continue_evaluation" | "cannot_assist"; responded_at: string };
  next_action: "await_professional_response" | "review_response" | "none";
};
```

Longitud description propuesta1..2000 caracteres tras NFC/recorte exterior, sin
controles salvo saltos de línea permitidos; body máximo8192 bytes, coherente con
C03. UUID no cero, versiones enteros1..2^31-1, disclosure_version
referencia de allowlist vigente. Cifras/campos y texto informativo requieren aprobación;
no son una política de admisión elegida silenciosamente. Rechazar adjuntos, números de
expediente, campos de partes estructurados o IA no significa garantizar que un relato
libre no contenga información sensible: aviso/minimización y retención siguen necesarios.

## 5. Comandos, lectura e idempotencia

| Ruta propuesta | Actor/precondición | Resultado |
|---|---|---|
| POST `/api/legal-requests` | Solicitante confirmado; SendRequest y destinatario vigente |201 `{request:RequestView}`; no cliente/reserva/acuerdo creados |
| GET `/api/legal-requests/{id}` | Solicitante o profesional destinatario vigente autorizado |200 vista privada mínima propia; sin fundamento de conflicto ajeno |
| GET `/api/legal-requests` | Actor confirmado; profesionales aal2 y vínculo vigente |200 `{items:[resumen privado mínimo],next_cursor}` ámbito filtrado en servidor |
| POST `/api/legal-requests/{id}/withdraw` | Solo solicitante; submitted/responded conforme a política propuesta |200 `{request:RequestView}` cuerpo `{expected_version,command_id}` |
| POST `/api/legal-requests/{id}/response` | Solo profesional destinatario vigente, aal2, submitted |200 `{request:RequestView}` cuerpo `{expected_version,command_id,outcome:"can_continue_evaluation"|"cannot_assist"}` |

Listado privado propone solo cursor opaco/limit1..50, sin filtro arbitrario por contexto,
email o destinatario. No heredar actualmente el límite100 de C03 como política aprobada.
La API deriva ámbitos de asignación, no de una selección de contexto que conceda permiso.
GET no cambia estado. Respuesta mínima estandarizada cambia submitted→responded,
incrementa versión y muestra texto fijo revisado: disposición a conversar o imposibilidad
de atender, sin fundamento de conflicto, narrativa profesional o identidad de terceros.
`can_continue_evaluation` no es ausencia definitiva de conflicto, contratación, consulta ni
apertura C05. No usar comando `accept` comercial. Responder dos veces con intenciones
nuevas falla STATE_CONFLICT; el replay del mismo comando sigue idempotencia. Aclaración,
corrección de respuesta, discusión libre y reasignación quedan fuera del primer corte.
Solicitante puede retirar después de respuesta conforme a la política propuesta; no
se borra el hecho mínimo de respuesta ni se interpreta retirada como aceptación.

Resumen de listado privado propuesto: `{id,version,state,recipient,submitted_at,response,
next_action}` sin description. Los textos fijos y estados finales deben ratificarse
con UX/Arturo. No correo/notificación externa por responder: cliente consulta su
bandeja de solicitudes autorizada, sin prometer avisos ni SLA numérico.

`command_id` en JSON evita añadir un header que el gateway no reenvía hoy; cualquier
cambio de proxy se revisa explícitamente. Unicidad por actor + operación + command_id,
con huella privada del cuerpo canónico, no contenido duplicado en logs. Repetición
idéntica, tras revalidar sesión/acceso, devuelve resultado original y mismo ID sin
segunda entrega; mismo command_id con contenido distinto →409 STATE_CONFLICT.
Reintento de creación devuelve201 idempotente de la creación original, documentado;
no crea versión/historia nueva. No prolonga retención ni reapertura tras retirada.
Reintento de withdraw ya aplicado devuelve estado vigente autorizado sin repetir evento.

Recibo mínimo de idempotencia y su plazo están **pendientes de política C04**. No crear
la tabla antes de fijarlos. Tras caducar recibo, no permitir un reintento antiguo como
nueva intención sin política explícita; definir antigüedad admitida o reconciliación por
lista/GET, sin prometer deduplicación infinita. No persistir relato otra vez como recibo.
Los cuerpos completos de errores/peticiones no se guardan para diagnosticar duplicados.

## 6. Frontera de autorización y concurrencia

Crear: autenticar → resolver public_id internamente a profesional/contexto → autorizar
versión de publicación/recepción/cuenta/contexto/vínculo → validar disclosure/retención
aprobada → reclamar command_id → crear solicitud y asignación exacta → revalidar frontera
C02/C03 → confirmar. Ninguna entrega/outbox previa al commit. La respuesta no expone
IDs internos del destinatario. Reutilizar patrón business de C02; no conexión/commit
independiente que evite revocación. Modelo A3 debe especificar bloqueo/serialización
compartido entre recepción de solicitud y retiro/suspensión; una consulta previa sola
no protege concurrencia. Sin ampliar grants/RLS ni owner para resolverlo.

Si salida/suspensión/retirada gana antes de confirmar, rollback completo y404
RESOURCE_UNAVAILABLE uniforme, sin solicitud medio enviada. Si envío confirmó antes,
retiro posterior impide nueva lectura/acción profesional; solicitud no se reasigna al
admin, a la práctica propia o a otro abogado. Solicitante recibe vista mínima de
indisponibilidad conforme a política C04, sin motivos privados, y puede retirar.
Versión cambió pero profesional sigue visible →409 VERSION_CONFLICT; actualizar ficha y
pedir confirmación nueva. Autorización precede chequeo de versión de objetos privados.

Respuesta profesional revalida asignación, cuenta, perfil/contexto/vínculo/capacidad,
MFA, versión y estado dentro de la misma frontera transaccional. Suspensión/salida o
retirada concurrente antes de commit impide respuesta y revierte su evento. Un borrador
local de respuesta no conserva autorización. Tras retirada, nueva respuesta falla
STATE_CONFLICT solo después de autorizar al actor; objeto ajeno sigue404.

Retirada de solicitud gana frente a evaluación/acciones futuras aún no confirmadas;
posteriores comandos no la reabren. Solicitud withdrawn conserva solo acceso/plazo
expresamente aprobados: política de lectura tras retirada/cierre pendiente antes de
implementar, no autorización perpetua implícita. Contenido ya conocido no se revoca
de la memoria del profesional; la UI no lo promete. Persistencia mínima del nombre del
destinatario tras retirada también requiere política, no copiar perfil completo.

## 7. Errores uniformes y límites

Cuerpo único: `{error:{code,message}}` con mensaje fijo localizado; sin input, stack,
SQL, excepción de proveedor, PII ni existencia de recursos ajenos. HTTP status y body
uniformes para inexistente/no autorizado/retirado en las rutas de objeto.

| HTTP/código | Uso |
|---|---|
|401 AUTHENTICATION_REQUIRED | Sesión ausente/inválida; código existente C02, sin alias nuevo |
|403 REQUEST_FORBIDDEN | Origin/CSRF/Authorization o acción no concedida sin revelar objeto |
|403 MFA_REQUIRED | Actor para cuya acción se requiere aal2 no lo tiene |
|403 FEATURE_UNAVAILABLE | Familia existente explícitamente gated; no éxito simulado |
|404 RESOURCE_UNAVAILABLE | Objeto privado ajeno/inexistente; ficha o destinatario retirado/invisible |
|409 VERSION_CONFLICT | Versión obsoleta tras autorizar; no se actualiza automáticamente |
|409 STATE_CONFLICT | Estado incompatible o command_id reutilizado con otro contenido |
|422 INVALID_REQUEST | Forma/tamaño/query/cursor/código no permitido; sin eco |
|429 RATE_LIMITED | Presupuesto de abuso agotado; cantidades/llaves/ventana por aprobar |
|503 OPERATION_UNAVAILABLE | Código de dominio propuesto para indisponibilidad; mensaje fijo y sin detalles |

Antes de implementar, reconciliar los códigos propuestos con AuthError/ProfessionalError
actuales; no cambiar todos los errores existentes como efecto lateral. Gate no habilitado
no revela existencia de registros. Listados públicos vacíos solo significan ausencia de
entradas elegibles cuando la capacidad esté operativa; fallo de configuración no se
oculta como200 vacío. Revisión de abuso/bot protection necesita política propia; no
instalar Turnstile, cuota pagada ni proveedor por este contrato.

## 8. Retención, pendientes y aceptación

Retención jurídica C04 aún **pendiente**, separada de cuenta30d/auditoría90d C02/C03.
Aprobar relato enviado, solicitudes retiradas/no atendidas, recibos de disclosure,
idempotencia, historia mínima, lectura tras retirada/cierre y eliminación/backups.
No cascade por cierre de cuenta ni conservación ilimitada para resolver dependencias.
Antes de aceptar datos reales: revisión de finalidad/destinatarios/terceros/avisos y
procedimiento profesional, **LEGAL REVIEW REQUIRED**. Política pública C06 y parámetros
numéricos de este contrato requieren decisión; no se selecciona ciudad/especialidad.

Pruebas de contrato propuestas, sin ejecutarlas en esta entrega:

- Proyección exacta: ninguna cédula/email/ID Auth/contexto privado en ficha/listado/error.
- Draft/preparing, revisión inválida y publicación retirada nunca aparecen; sin fixtures
  simulados en producción. Retiro entre páginas o ficha/envío no reutiliza autorización.
- Query duplicada/desconocida, tamaño excesivo, búsqueda sobrelímite y cursor manipulado fallan;
  ausencia de oferta no relaja filtros ni muestra oferta transaccionable.
- Solicitante no adopta actor/destinatario/contexto por campos extras; cliente sin perfil
  profesional puede utilizar el flujo cuando su requisito de assurance quede aprobado.
- Respuesta mínima exige destinatario vigente/aal2; no concede acuerdo ni da contexto
  privado. Retirada/suspensión concurrente impide respuesta y no filtra motivos.
- Admin/revisor sin asignación no lee solicitudes; destinatario suspendido no continúa.
- Doble clic/concurrencia con mismo command_id crea una solicitud; reutilizar con cuerpo
  distinto falla; timeout se reconcilia sin envío automático adicional.
- Revocación entre validación y commit revierte contenido/asignación/evento; retirada
  de solicitud concurrente no permite reapertura ni aceptación comercial accidental.
- CSRF/Origin inválidos y bearer presente no producen efectos; errores no reflejan relato.
- Migración/restauración no resucita ficha o asignación retirada; purga respeta política
  aprobada por categoría, sin reset de plazo por GET/reintento.

Done exige navegador→API→datos→respuesta y revisión independiente con negativos, no
solo mocks del directorio. La evidencia de diseño no afirma API instalada, migración
aplicada, catálogo real, solicitudes enviadas o pruebas funcionales ejecutadas.
