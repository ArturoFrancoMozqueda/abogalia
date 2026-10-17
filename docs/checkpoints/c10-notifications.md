# C10 — Notificaciones y entrega por finalidad

Fecha: 2026-10-16. Estado: **Proposed; no aprobado para implementar**.
Separado del correo C02 existente y de las invitaciones internas C03 aprobadas.

## Lo que entiendo

La aplicación avisa de acciones pendientes sin filtrar datos jurídicos ni convertir un
acuse en atención realizada. La fuente del estado sigue siendo la capacidad de negocio.
Aviso interno, intento de correo, aceptación SMTP y lectura por el destinatario no son
equivalentes. La entrega debe soportar duplicados, pérdida de permiso y fallos de envío.

## Decisiones tomadas

- C02 utiliza Supabase Auth → Resend SMTP Free, con alcance y tratamiento delimitados.
  Esa selección no aprueba reusar credenciales ni envío de mensajes del producto.
- D-041 aprueba invitaciones C03 internas a cuenta confirmada, sin búsqueda por email
  ni correo de invitación; vigencia 24h, recibo 30d y auditoría mínima 90d específicos.
- No se aprueba WhatsApp, SMS, marketing, tracking de apertura, ni dominio por este plan.
- Observabilidad actual no captura contenido ni eventos de usuarios automáticamente.

## Decisiones pendientes

| ID | Opciones y recomendación propuesta | Bloquea |
|---|---|---|
| NOT-01 | Internas solamente o internas + correo transaccional. Recomendar primeras internas por acción del usuario/consulta de bandeja, sin prometer envío externo | Canales y exposición |
| NOT-02 | Aprobar finalidades, quién recibe qué, preferencias, eventos obligatorios y frecuencia; recomendar matriz por evento/actor/contexto | Destinatarios/UX |
| NOT-03 | Si correo: dominio/remitente, responsable de respuestas, proveedor/credencial propios, tratamiento, cuota y reserva para Auth | Envío externo |
| NOT-04 | Fijar caducidad y conservación separadas de bandeja, intentos, deduplicación y auditoría; responsables de errores/colas | Datos/retención/operación |

Finalidad, comunicaciones y datos personales: **LEGAL REVIEW REQUIRED**. Las cuotas del
proveedor se revisarán con su documentación oficial antes de aprobar NOT-03; no se
atribuye una cuota actual ni se habilita otro plan aquí.

## Diseño propuesto

Cada módulo produce una intención estructurada junto a su transición de negocio.
Recomendar outbox transaccional en PostgreSQL; polling/ejecutor y frecuencia requieren
checkpoint operativo antes de instalar scheduler. El receptor no es un email arbitrario
aportado por el emisor: se deriva de la relación/acción aprobada y se reautoriza al
materializar, inmediatamente antes de cada envío externo y al abrir el aviso. Como
invariante propuesto, retirada de participación, pérdida de permiso o relevo exige
reevaluar destinatario y finalidad de toda intención pendiente; una autorización al
encolar no dura para siempre. Si ya no cumple, suprimir el envío, sin remitir al nuevo
responsable contenido que no tenga autorizado. Cambio de responsable invalida
destinatarios obsoletos.

| Entidad | Propiedad y relación | Estados propuestos |
|---|---|---|
| NotificationIntent | Evento de módulo + contexto y propósito versionados | pending, materialized, suppressed, expired |
| InboxNotification | Un destinatario y referencia opaca autorizada; nunca contenido jurídico | unread, read, dismissed, withdrawn, expired |
| DeliveryAttempt | N por intención/canal; referencia técnica del proveedor si existe | pending, sending, accepted, failed, suppressed, unknown |
| NotificationPreference | Cuenta/contexto/finalidad/canal según matriz aprobada | enabled, disabled |
| DeliverySuppression | Canal/destinatario verificado, razón estructurada | active, reviewed, cleared |

Unicidad por evento + destinatario + finalidad + canal; reintento conserva intención y
no duplica aviso. Webhook de rebote, si se aprueba, es idempotente y autenticado; un
rebote suprime posteriores envíos según política y ofrece alternativa interna. No
reintentar sin límite ni consumir reserva Auth. Estado ambiguo de envío se concilia;
no afirmar exactamente-once ante proveedor externo sin soporte contractual.

Contrato candidato `GET /api/notifications` paginado y autorizado,
`POST /api/notifications/{id}/read`, actualización limitada de preferencias. Abrir una
referencia requiere permiso actual del objeto; el aviso no es autorización. Email futuro
solo texto genérico, enlace fijo a la aplicación y autenticación normal; sin relato,
nombre de contraparte, adjuntos, OTP, credenciales ni URLs portadoras de acceso al asunto.
La bandeja distingue cambio real de estado frente a mensaje genérico de actividad.

## Datos afectados

Cuenta destinataria y referencia relacional son datos personales/restringidos incluso
sin texto jurídico. Guardar solo tipo/finalidad/versión/estado/fecha/contexto necesarios;
no copiar payload de solicitud, documento o mensaje a una outbox. Correo se obtiene
por vía autorizada al enviar, con presupuesto de tratamiento aprobado, no en logs.
Historial mínimo de supresión/fallo/lectura separado de métricas públicas.

Retención C10 **pendiente NOT-04**. No aplicar 30/90 por analogía ni conservar todos los
reintentos indefinidamente. C03 mantiene sus plazos aprobados sin replicar contenido
en una bandeja de mayor duración. Borrado de negocio debe retirar referencias/avisos
conforme a retención y excepciones aprobadas; eliminación no dispara otro correo.

## Seguridad

Acceso por destinatario y sesión vigente, nunca por membresía genérica. Emisor no
elige correo ajeno, plantilla HTML arbitraria ni campos libres que se vuelquen a correo.
Rate limits y presupuestos en servidor; autorización de plantilla y campos permitidos.
Logs/trazas no incluyen destinatarios, headers, eventos crudos ni cuerpo de proveedor.
Credenciales SMTP/Auth no se comparten con un worker de notificaciones por conveniencia.
Outbox sin secretos y acceso limitado no equivale a habilitar captura analítica.

## Impacto futuro

C04/C05/C07/C08 publican eventos solo tras aprobar contratos; cada uno sigue siendo
autoridad sobre estado/plazos. Nuevos canales C19 requieren consentimiento, costo,
tratamiento y prueba separados. El aviso de recordatorio no calcula plazos jurídicos.

## Implementación propuesta

1. Aprobar NOT-01/02/04, inventario cerrado de eventos y matriz; A3 datos/outbox solo
   tras revisión. Diseñar inicialmente transporte sintético y consumo manual controlado.
2. API/bandeja con retirada de acceso y pruebas. Evaluar correo solo al aprobar NOT-03.
3. Operación C14/C17 fija límites/reintentos/responsable; aceptación externa con buzón
   controlado, autorización y presupuesto propios, sin reutilizar envíos C02 por inferencia.

Negativos: duplicar evento no duplica aviso; miembro retirado no recibe/abre objeto;
preferencia no permitida no se cambia; datos jurídicos no salen en correo/logs; rebote
y caída prolongada no causan tormenta; fallo de outbox no pierde transición; email
aceptado no se presenta como leído; C03 no genera correo accidental. Sin envíos en esta entrega.
