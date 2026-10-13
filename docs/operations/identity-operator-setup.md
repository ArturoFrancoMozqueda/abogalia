# Operación privada del piloto Identity — tanda 04

Fecha: 2026-10-13. Base asignada `98dd4fa`. Autor A5; revisión A0 pendiente.
Arturo aprobó la configuración SMTP del piloto, cierre/retiro y operación de
retención/fallos en tres paquetes. Esta guía prepara esos pasos aprobados;
no configura proveedores, aplica SQL, envía correo ni instala un scheduler.
Hosting sigue sin selección. Approved no equivale a Implemented.

Referencias: [activación](../checkpoints/identity-real-activation.md),
[correo](../checkpoints/identity-email-operations.md),
[retención](../checkpoints/identity-retention-operations.md),
[contrato](../contracts/identity-api.md) y
[destinos públicos](service-registry.md). Los documentos de tanda 03 conservan
pendientes históricos; A0 registra la aprobación posterior sin ampliar alcance.

## Configurar Auth y correo en el proyecto correcto

El operador confirma **Abogalia**, organización `jdmkzzkgnzwldthjqtgx`, proyecto
`xggefantvuwpilksfdoy`, Free/us-east-1. El
[panel del proyecto](https://supabase.com/dashboard/project/xggefantvuwpilksfdoy)
es un destino público; nunca usar la pestaña de otro producto. Web local:
`http://127.0.0.1:5190`, API `http://127.0.0.1:8090` y proxy del mismo origen.
No seleccionar hosting ni añadir redirecciones con credenciales.

El operador aplica y registra **solo estado/valor no secreto** de estos ajustes:

| Ajuste | Valor aprobado para el piloto | Comprobación |
|---|---|---|
| Proveedor de acceso | Email/password, confirmación requerida | No autoconfirmar ni habilitar OAuth/SMS/magic-link como nuevo recorrido |
| JWT expiry | **900 segundos** | La API rechaza vigencia superior al contrato; no aumentar por fallos |
| Email OTP expiry | **600 segundos** | Probar vencimiento en el flujo sin copiar OTP a evidencia |
| Email OTP length | **6 dígitos** | Preservar cero inicial; GoTrue genera/verifica |
| Frecuencia mínima Email OTP | **60 segundos** por destinatario | No repetir solicitud en esa ventana; no añadir endpoint resend sin contrato |
| MFA | TOTP según contrato existente | No habilitar recuperación/unenroll ni atribuir permisos profesionales |
| Site URL de ensayo | `http://127.0.0.1:5190` | Fuente/plantillas no usan enlaces; no configurar callback que lleve tokens a URL |

Los nombres exactos/secciones del panel pueden variar. JWT se configura en Auth;
OTP, confirmación y frecuencia en Email/Auth; cuotas en Rate Limits. Revisar el
ajuste guardado, sin visitar pantallas de claves ni registrar capturas. Estos
valores propios no son los defaults documentados del proveedor. Supabase exige
confirmación en hosted por defecto, pero eso no prueba el estado de este proyecto.
[Password Auth](https://supabase.com/docs/guides/auth/passwords),
[sesiones/JWT](https://supabase.com/docs/guides/auth/sessions),
[límites](https://supabase.com/docs/guides/auth/rate-limits).

### SMTP Free y remitente de pruebas

El operador confirma equipo/cuenta **propios de Abogalia** en Resend Free, sin
overages, upgrade ni compra de dominio. El destinatario es exclusivamente el buzón
privado ya indicado por Arturo y asociado a esa cuenta Resend; no escribirlo en
repo/chat/log/captura. No CC/BCC, contactos o clientes. Máximo **6 envíos en todo
el piloto**, contabilizando cada solicitud que pueda emitir mensaje, incluso si
su entrega es incierta; al llegar al tope se detiene. No reintentar una mutación
automáticamente tras timeout. La cuota general Free es 100/día UTC y 3,000/mes;
ese límite no amplía el cupo aprobado de seis. [Cuotas oficiales](https://resend.com/docs/knowledge-base/account-quotas-and-limits).

La [documentación SMTP](https://resend.com/features/smtp-service) muestra el
remitente público de pruebas; [la restricción oficial](https://resend.com/docs/knowledge-base/403-error-resend-dev-domain)
permite solo el buzón asociado a la cuenta. De ambas se infiere viabilidad SMTP
sin dominio propio para ese destinatario. Aún debe comprobarse en el proyecto
real; la [guía general Supabase/Resend](https://resend.com/docs/send-with-supabase-smtp)
requiere dominio verificado para uso general. Un sink de pruebas no acredita
recepción de OTP utilizable. No abrir registro público con este remitente.

En Supabase: Authentication → Email bajo Notifications → SMTP Settings,
conforme a la guía oficial. Habilitar custom SMTP y completar privadamente:

| Campo | Valor/acción |
|---|---|
| Sender email | `onboarding@resend.dev`, remitente público de pruebas de Resend |
| Sender name | `Abogalia` como nombre de trabajo del piloto, sin fingir dominio propio |
| Host | `smtp.resend.com` |
| Port/TLS | `465`, TLS validado; no desactivar verificación |
| Username | `resend` |
| Password | Clave propia con **sending_access**, creada e introducida por operador mediante mecanismo privado; ningún valor en esta guía |
| Reply-To | No inventar dirección; no ampliar a buzón de soporte no aprobado |

No usar clave full_access como sustituto. En ausencia de dominio propio no se
promete restricción por domainId; mantener recurso/equipo propios y cupo cerrado.
Si la cuenta SMTP rechaza el remitente, guardar código fijo/error saneado y
mantener gate desactivado; no elegir otro proveedor/dominio silenciosamente.

El paso de creación/inyección privada corresponde al operador. La inspección
de metadatos del conector Resend encontró `create_api_key` con sending_access,
pero su contrato exige mostrar el token devuelto. No se usa porque contradice
la regla expresa de no exponer secretos. `get_usage` y `list_domains` tienen
alcance de cuenta y no filtro por Abogalia; no se llaman si la conexión puede
abarcar Kova. No hay herramienta identificada que configure SMTP o las plantillas
GoTrue: crear templates en Resend sería otro motor y no resuelve esta integración.
No se realizó ninguna llamada al conector ni se inspeccionaron recursos reales.

### Instalar fuentes GoTrue y verificar el recorrido

1. Ejecutar `python3 scripts/check_identity_mail_templates.py` desde el repo.
   Solo lee los dos HTML fijos, sin argumentos, entorno, red o OTP real. Salida
   JSON de estados/códigos fijos; exit 0 pasan, exit 1 falla.
2. En Email Templates del proyecto, **Confirm sign up**: copiar fuente
   [identity-confirmation.html](../email/identity-confirmation.html), asunto
   `Confirma tu correo en Abogalia`. **Reset password**: copiar fuente
   [identity-recovery.html](../email/identity-recovery.html), asunto
   `Recupera tu acceso a Abogalia`. No copiar el ejemplo default con enlaces.
3. La única variable es `{{ .Token }}`. Conservar seis dígitos en cuerpo visible;
   ningún código en asunto/URL, `.ConfirmationURL`, `.TokenHash` o `.Data`.
   Estas fuentes no generan From/To ni prueban MIME text/plain. SMTP propio
   permite personalización Free; [plantillas oficiales](https://supabase.com/docs/guides/auth/auth-email-templates).
4. Mantener tracking open/click desactivado. La plantilla no lleva pixels/links,
   pero el proveedor podría inyectarlos: el operador verifica el correo en su
   buzón, sin pasar cuerpo/cabeceras/código a herramientas visibles. Si no puede
   comprobar la configuración de tracking del remitente de pruebas, reportarlo.
5. El primer envío es un ensayo de instalación coordinado por A0, dentro del cupo
   de seis. El gate de la API sigue desactivado hasta revisar plantilla instalada,
   seis dígitos/TTL, destino propio, entrega y TLS. Ese ensayo privado no se
   sustituye por marcar el gate listo para probar un correo desconocido.
6. A0 habilita `ABOGALIA_AUTH_EMAIL_READY` mediante inyección privada después de
   esa evidencia. Arturo recorre registro → confirmar → acceso y recuperar →
   nueva contraseña, sin comunicar códigos. Registrar booleanos/códigos saneados,
   número acumulado de solicitudes y tiempos mínimos. 202 no acredita entrega;
   SMTP accepted no acredita delivered ni verified. Confirmación exige login.
7. Los negativos de reutilización/vencimiento y revocación no requieren reenviar
   por cada intento. Planearlos dentro del mismo cupo; no completar a costa de
   excederlo. Si se agota, conservar evidencia pendiente explícita.

Fallo/configuración ausente: 503; cuota 429 según contrato. Mailer fallido no
autoriza autoconfirmar, bajar MFA o imprimir errores del proveedor. Recuperación
puede cambiar contraseña antes de una revocación parcial: no afirmar rollback ni
reutilizar código consumido. Volver a estado seguro y diagnóstico mínimo.

### Ensayo inicial con gate global desactivado: diseño del ejecutor

Estado: diseño solicitado por A0; **sin implementación ni ejecución**. La API
actual bloquea registro/recuperación cuando `ABOGALIA_AUTH_EMAIL_READY=0`; un test
SMTP genérico no demuestra la plantilla Confirm sign up ni OTP de seis dígitos.
El conector Supabase disponible no expone signup: SQL, invitación administrativa,
crear usuario confirmado o desplegar una Edge Function no sustituyen este flujo.
No activar globalmente READY para salvar esa dependencia.

Propuesta acotada: ejecutor local de **una operación** que use el adaptador GoTrue
ya existente para signup inicial, sin modificar runtime, rutas web o flags del
servidor. Después del ensayo/entrega revisada, el recorrido API/web procede según
su contrato. Recuperación se habilita como acción de ensayo únicamente si A0 la
necesita dentro del mismo cupo. El ejecutor requiere revisión de estos controles
antes de operar; no se añade código en esta orden:

- Proyecto/origen y acción fijos; solo el buzón propio Resend ya autorizado.
  Marcador privado `identity-pilot` fuera de Git, propiedad/permisos del operador,
  con huella del destinatario autorizado, vencimiento y contador persistente del
  cupo global de **seis**. No admitir destinatario arbitrario, reset automático
  de cupo, argumento con OTP o archivo público de autorización. La huella también
  es dato privado y no se publica.
- Clave publishable y configuración mediante mecanismo privado aprobado del
  operador. Email/contraseña se introducen con entrada oculta en su terminal
  privada; no `write_stdin`, argumentos, comandos inline, URL, captura o chat.
  El agente no observa los valores. No abrir ni imprimir el archivo real.
- Reservar contador **antes** de HTTP, bajo exclusión mutua; rechazo/timeout
  consume reserva y no dispara retry. Al vencer marcador/agotarse cupo/fallar
  persistencia, no enviar. Ventana de 60 segundos aplicada además del cupo.
- Petición signup sin redirect y con confirmación requerida. Descartar cuerpo
  completo del proveedor y cualquier user/session/token; sesión inesperada
  representa fallo de configuración y no se entrega al navegador. Sin login,
  MFA, retiro Auth o lecturas de usuarios/sesiones desde este ejecutor.
- Resultado fijo `accepted` o error saneado, contador y estado del ensayo; ningún
  correo, subject, código, contraseña, clave, cuerpo o excepción cruda. El
  operador comprueba entrega/OTP en su buzón y solo comunica resultados mínimos.
- Pruebas sintéticas deben cubrir destino/buzón ajeno, marcador ausente/vencido,
  reserva concurrente, timeout sin retry ni recuperar cupo y respuesta con sesión
  inesperada; no confundir tests con prueba de entrega real.

Las herramientas existentes pueden ejecutar código local revisado con salida
saneada, pero hoy no hay ejecutor con estos controles. La intervención privada
del operador es inevitable; no pegar un signup HTTP con contraseña en un tool.
Este diseño mantiene `ABOGALIA_AUTH_EMAIL_READY=0` y no crea un bypass general.

## Retención en el host local, sin elegir hosting

La funcionalidad periódica está aprobada: sesiones cada **5 minutos**; auditoría
diaria a **03:00 America/Mexico_City**, cortes UTC. Un ejecutor; reintentos
transitorios máximos tres a 1/5/15 minutos y alerta al responsable Arturo/A0 con
estado/conteos, sin dirección/IDs/DSN. Configuración rota o cuentas bloqueadas
requieren intervención; un retry no acredita retirada Auth.

La sesión se rechaza al alcanzar 12 h absolutas o 30 min inactiva aunque el host
duerma; su eliminación física por job tiene demora operativa hasta que vuelva a
ejecutar. Las cuentas cerradas vencen a 30 días y audit a 90 días. Un job perdido
no amplía esos plazos ni acredita cumplimiento. Revisar ejecuciones perdidas al
despertar/reiniciar y alertar backlog. Mac local debe tener runtime/configuración
privada disponibles y política de reanudación comprobada antes de instalar job.

**Bloqueante mecánico actual:** `scripts/run_identity_retention.py` solo acepta
la base temporal **sintética** y `--apply --isolated-local`. No apuntarlo a Supabase,
quitar sus guards ni convertir su owner de fixture en usuario operativo. Se
necesita un adaptador operativo separado revisado, con destino exacto de Abogalia,
capacidad mínima de mantenimiento, exclusión mutua y corte/errores verificados.
El cron de abajo es **SOURCE público de referencia, no instalado ni ejecutable
como está**; `identity-retention-job` representa ese adaptador pendiente y no un
archivo existente. A0 coordina el nombre/CLI y elige launchd u orquestador según
el host; aprobar la periodicidad no selecciona ni instala un scheduler.

```cron
# SOURCE, SIN INSTALAR. Adaptador/rutas pendientes de integración.
# Requiere scheduler que interprete esta zona; no asumir CRON_TZ en macOS cron.
CRON_TZ=America/Mexico_City
*/5 * * * * /RUTA_PUBLICA/abogalia/identity-retention-job --sessions
0 3 * * * /RUTA_PUBLICA/abogalia/identity-retention-job --audit-accounts
```

Sin contraseña, DSN, dotenv, mailto, redirecciones a logs crudos o shell tracing.
El adaptador recibe configuración desde el mecanismo privado del host; cron no
la incorpora en command/env source. No ejecutar estos ejemplos ni instalar job
antes de pruebas de destino/permisos/lock/fallos y revisión independiente.

### Cierre, retiro y fallos

El cierre aprobado primero bloquea el sujeto local y revoca sesiones custodiadas;
la retirada Auth corresponde al operador autorizado, con evidencia auténtica
ligada al sujeto/operación/tiempo, custodiada privadamente. Nunca aceptar UUID,
bool/archivo del cliente o ausencia de auth.sessions como prueba de eliminación.
La eliminación local a 30 días exige comprobar ese retiro; de otro modo conserva
bloqueo y reporta incumplimiento, sin inventar retención perpetua. Los permisos
para retirada Auth son una capacidad separada; el job rutinario no obtiene
service_role ni privilegios administrativos. Membership no existe aún.

El runner sintético mantiene `accounts=0` y `blocked_accounts` explícito:
exit 0 preview completado o apply sin bloqueo; exit 3 apply parcial con cuentas
pendientes; exit 2 fallo fijo. Preview 0 no acredita borrado/cumplimiento.
Conserva expiración/rechazo al acceso; un bloqueo de cuentas no detiene limpieza
de sesiones y audit vencidos. La adaptación real debe preservar esos resultados
y probar aislamiento con SQL real; no reutilizar mocks como aceptación.

## Evidencia para A0 y pasos privados inevitables

Archivos entregados: esta guía, [validador](../../scripts/check_identity_mail_templates.py)
y [tests](../../scripts/tests/test_identity_mail_templates.py). El validador protege
fuente estática contra enlaces/recursos/variables extra/código renderizado,
ubicación del Token, estructura, lengua y tablas accesibles. No verifica entrega,
TTL efectivo, configuración del proveedor, render de cliente, MIME, contraste de
ediciones arbitrarias ni cumplimiento legal. No recibe contenido de buzones.

El operador debe confirmar equipo/buzón asociado, crear/injectar clave privada,
guardar SMTP/ajustes/plantillas y completar OTP en su propio flujo. A0 coordina
grants/SQL y launcher; el operador provee configuración desde su gestor privado,
sin enviarla al agente. Falta implementar/revisar adaptador de mantenimiento y
comprobar scheduler del host antes de instalar. No se solicita nuevamente la
aprobación del diseño ya recibido; estos son requisitos mecánicos pendientes.

Resend conserva sus políticas propias de tratamiento/retención; D-032 no modifica
copias en proveedor/buzón/backups. **LEGAL REVIEW REQUIRED** antes de ampliar a
clientes/datos jurídicos. Sin envío, API/MCP real, DNS, instalación, claves,
capturas, cambios de env, hosting o publicación en esta entrega.

Verificación local de esta entrega: las dos fuentes pasan el validador; **7 tests
stdlib negativos pasan** y Ruff check/format pasan en los dos Python. Sin
verificación de proveedor, instalación de job ni recorrido OTP real ejecutados.
