# Checkpoint — Operación de correo de Identity

Fecha: 2026-10-12. Tanda 03 / C02. Estado: **Approved proveedor y alcance de piloto; Pending dominio y parámetros**.
Base asignada: `720c1cf`. Autor A5; revisión A0/A2 pendiente. Arturo eligió Resend SMTP Free sin overages y piloto frontend local con
Supabase real. Approved no equivale a Implemented. Esta entrega prepara diseño
y plantillas locales; no configura SMTP, DNS, destinatarios o recursos,
no envía mensajes y no habilita `ABOGALIA_AUTH_EMAIL_READY`.

## Lo que entiendo

Registro y recuperación de Abogalia necesitan correo real que entregue códigos
de seis dígitos, introducidos en la aplicación y enviados a la API solo en el
cuerpo de la petición. La implementación local ya tiene esos formularios y
contratos; su prueba con proveedor/entrega real sigue pendiente. No basta tener
una plantilla o respuesta 202 para demostrar entrega, confirmación o recuperación.

La cuenta confirmada no verifica al profesional ni concede membresía o permisos.
Esta entrega prepara solo confirmación de correo y recuperación de contraseña.
No activa marketing, invitaciones, cambio de correo, notificaciones jurídicas,
recuperación MFA o IA. Abogalia sigue como nombre de trabajo; no se elige marca
definitiva ni dominio por este documento.

## Decisiones tomadas

D-028 aprueba Supabase Auth. D-031 conserva correo/contraseña con confirmación,
API mediadora y códigos fuera de URL; D-032 fija retención de cuenta/membresía y
auditoría, sin decidir retención de correo en terceros. D-023/D-027 conservan
recursos propios y administración por producto; Kova queda excluido.
Fuente: [decisiones](../decisions/decision-log.md),
[checkpoint Identity](identity-and-contexts.md) y
[contrato HTTP](../contracts/identity-api.md).

IE-01: **Approved** por Arturo: Supabase Auth → Resend SMTP Free, sin overages,
upgrade automático ni compra de dominio. IE-04: **Approved alcance** de piloto
frontend local con Supabase real, limitado al buzón propio asociado a la cuenta
Resend, controlado por Arturo; destinatario concreto y configuración privada aún
pendientes. Dominio propio: **Pending**, actualmente no existe. No se aprueba
registro público ni envío a clientes por esa elección.

Los dos archivos HTML usan exclusivamente `{{ .Token }}` como variable GoTrue.
Es un placeholder público, sin OTP real. No se incluye código en asunto,
preheader, enlaces, metadatos de usuario o diagnósticos. Los asuntos propuestos
son «Confirma tu correo en Abogalia» y «Recupera tu acceso a Abogalia».

La documentación de Supabase describe `.Token` como OTP de seis dígitos. Sus
plantillas distinguen Confirm sign up y Reset password; usar código evita enlaces
de confirmación consumidos por prefetch. Fuente:
[plantillas Auth](https://supabase.com/docs/guides/auth/auth-email-templates).

## Decisiones pendientes

Estos son **cuatro paquetes de decisión** con aprobación parcial indicada; A0
registra respuestas de Arturo sin reabrir D-028/D-031 ni la elección Resend Free. Una aprobación parcial no
autoriza el resto del paquete ni gasto/DNS/envío implícitos.

| ID | Decisión necesaria | Estado y parámetros pendientes |
|---|---|---|
| IE-01 | Proveedor, mecanismo y tratamiento | **Approved** Supabase Auth → Resend SMTP Free sin overages. Validar accesos, retención y tratamiento antes de ampliar a datos reales del producto; Send Email hook o cambio de proveedor necesitan nueva decisión |
| IE-02 | Dominio y remitente verificables | **Pending** dominio propio: no existe. Piloto sin compra puede usar el remitente de pruebas publicado por Resend, solo hacia el buzón asociado a su cuenta; ver evidencia abajo. Para público, Arturo elige dominio/subdominio propio de Abogalia, nombre From y dirección real autorizada; designa quién atiende respuestas y si se usa Reply-To real. Recomendar separar reputación de Auth y marketing, SPF/DKIM y DMARC con política revisada por responsable. Sin contactos/dominio inventados, compra o modificación DNS por esta entrega |
| IE-03 | Vigencia, cuotas y abuso | Recomendar OTP de 10 minutos y conservar seis dígitos; pausa mínima de 60 segundos entre solicitudes del mismo destinatario, límite por proyecto compatible con el piloto y topes por IP/destinatario a concretar y probar. Fijar máximos diarios/mensuales, reserva para recuperación, alertas, responsable y conducta al agotarlos. No extender el código ni desactivar confirmación ante fallos; no reenvío automático |
| IE-04 | Destinatarios y activación operativa | **Approved alcance** piloto frontend local con Supabase real, sin clientes. Falta que Arturo indique el buzón controlado asociado a su cuenta Resend mediante canal privado, número máximo de pruebas/envíos y autorización operativa concreta. Registro público solo tras validar entrega, fallos, privacidad, términos y revisión independiente. Aprobar contenidos/asuntos, soporte limitado y quién puede activar/desactivar el gate tras la evidencia |

IE-03 contiene números propuestos; no se aplica configuración con ellos. La
pausa no crea un endpoint de reenvío de confirmación: ese contrato todavía debe
resolverse si el piloto lo necesita. La plantilla no promete un plazo hasta que
el TTL real se configure y verifique. No sumar cuotas por clave/dominio ni
atribuir a Abogalia cuota de Kova. Los destinatarios reales autorizados del piloto
se guardan fuera del repositorio público; no se solicita una lista de clientes.

### Parámetros concretos propuestos para el primer ensayo

El coordinador propone OTP de 10 minutos, intervalo mínimo de 60 segundos y máximo
seis mensajes de todo el ensayo, solo al buzón controlado indicado por Arturo en
la conversación. No registrar su dirección en el repositorio. Usar el remitente de
prueba de Resend únicamente si la cuenta y la restricción de destinatario quedan
verificadas; no abrir registro público o prometer remitente/dominio definitivo.
Estos parámetros y el tratamiento de email/cuerpo por Resend (retención propia
30 días, datos en Estados Unidos) siguen pendientes de aceptación consciente.
No se envió ningún mensaje ni se leyó ningún OTP.

## Diseño propuesto

Ruta elegida en IE-01, pendiente de configuración/verificación: usuario → formularios web → API → Supabase
Auth → SMTP elegido → buzón autorizado. GoTrue emite/verifica el código; la API
no inventa OTP, no duplica envío y no recibe contraseñas SMTP por navegador.
La credencial de correo se configura mediante el mecanismo privado del proveedor
por el responsable autorizado, sin valores en comandos, conversación o evidencias.
Solo documentar nombres lógicos y estado presente/ausente.

| Alternativa | Hecho oficial actual y limitación | Implicación para Abogalia |
|---|---|---|
| SMTP predeterminado Supabase | Solo direcciones del equipo del proyecto; actualmente 2 mensajes/hora, sin SLA de entrega | No habilitar registro público ni usarlo como sustituto de SMTP propio. [Fuente](https://supabase.com/docs/guides/auth/auth-smtp) |
| Personalización Free | Desde 2026-06-03, proyectos Free nuevos con mailer default no pueden modificar plantillas; Free con SMTP propio conserva personalización | El proyecto nuevo necesita SMTP propio aprobado para usar estas plantillas. No obliga a contratar Pro. [Cambio oficial](https://supabase.com/changelog/46599-changes-to-email-template-customisation-on-free-tier) |
| Resend Free, Approved | 100 correos/día y 3,000/mes, hasta 3 dominios; envío y recepción cuentan, y varios destinatarios consumen cuota adicional | El límite diario usa día UTC; no es ventana móvil. Mínimo una entrega por confirmación y otra por recuperación, más solicitudes posteriores; no convertirlo en número de usuarios soportados. [Cuotas](https://resend.com/docs/knowledge-base/account-quotas-and-limits), [plan](https://resend.com/pricing) |
| Resend SMTP | La guía de integración para destinatarios generales requiere dominio verificado y credencial propia; remitente de pruebas tiene excepción acotada abajo. Integración Supabase documentada en `smtp.resend.com`, SMTPS puerto 465 | Host/puerto son destinos públicos del mecanismo elegido; ninguna credencial se lee o genera aquí. [Guía oficial](https://resend.com/docs/send-with-supabase-smtp) |

### Piloto sin dominio: evidencia y límite

Resend publica un ejemplo **SMTP** con `onboarding@resend.dev` en su
[servicio SMTP](https://resend.com/features/smtp-service). Su
[restricción del dominio de pruebas](https://resend.com/docs/knowledge-base/403-error-resend-dev-domain)
permite destinatario únicamente en la dirección asociada a la cuenta Resend.
La combinación sustenta **viabilidad documental**, inferida de ambas fuentes,
de SMTP al buzón propio sin comprar dominio; no se limita a asumir ejemplos REST.
La guía de Supabase SMTP sigue pidiendo dominio verificado para el uso general.
No se ha comprobado aceptación SMTP ni entrega en la cuenta/proyecto reales.

`onboarding@resend.dev` es un remitente de pruebas público del proveedor, no una
dirección propia ni una identidad inventada de Abogalia. No se añade From a las
plantillas HTML. `delivered@resend.dev` en ejemplos es un sink sintético: no sirve
para recibir OTP y completar el flujo real. El piloto debe permanecer cerrado a
un único buzón autorizado asociado a la cuenta, sin CC/BCC ni registro público;
cualquier otro destinatario requiere dominio propio verificado y nueva autorización.
Cuotas Free siguen 100/día UTC y 3,000/mes; no se aprueban excedentes, upgrade ni
recarga al agotarlas. Parar solicitudes y mostrar indisponibilidad/cuota sin
prometer reenvío. Arturo aportará el destinatario privado antes de operar; no
registrarlo en este documento. No enviar correo en esta entrega.

Al habilitar SMTP propio, Supabase documenta límite inicial de 30 mensajes/hora;
registro y recuperación tienen ventana predeterminada de 60 segundos por usuario.
Estos defaults no son los límites reales comprobados del proyecto. La API con
publishable key no debe asumir que el rate limit IP del proveedor identifica a
cada usuario: las llamadas salen del servidor. Reenvío de IP requiere otro
contrato; no elevar privilegios o añadir secret key por comodidad. Fuente:
[SMTP](https://supabase.com/docs/guides/auth/auth-smtp),
[límites Auth](https://supabase.com/docs/guides/auth/rate-limits).

### Plantillas y estados verificables

- [Confirmación](../email/identity-confirmation.html): usar en Confirm sign up;
  indica volver a registro y escribir el código en «Confirmar correo».
- [Recuperación](../email/identity-recovery.html): usar en Reset password;
  indica volver a recuperación y escribir código/nueva contraseña.
- Ambos asuntos se configuran aparte del HTML. El código está solo en cuerpo
  visible, como texto seleccionable; no imágenes, botones con links, píxeles,
  scripts, fuentes remotas ni datos jurídicos. No usan `.Email` o `.Data`.
- Plantillas sin estilos permanecen legibles: encabezado, propósito, código,
  acción y advertencia. Lengua/dirección repetidas en HTML y contenedor directo,
  un h1, contraste y layout simple. Alternativa MIME de texto: verificar soporte
  efectivo GoTrue/SMTP; no declarar multipart generado por estos HTML.

Una respuesta API 202 usa mensajes genéricos existentes y no promete envío al
buzón. Mailer/configuración ausentes o fallos desconocidos son 503; cuota 429;
código inválido/usado/vencido 401 genérico. Confirmación requiere login posterior.
Recuperación cambia contraseña y revoca según contrato; fallo parcial no promete
reversión ni permite reutilizar OTP consumido. No repetir operación tras timeout
incierto. La aplicación no reenvía mensajes al pulsar GET/session/CSRF.

## Datos afectados

Actual: únicamente fuentes HTML y documentación pública; todos los placeholders
son públicos. En operación futura: dirección destinataria, nombre/dirección From,
OTP temporal, propósito de correo, tiempos y estados mínimos de entrega/fallo.
No relato jurídico, adjuntos, nombre de cliente, contraseña o datos profesionales.
Un correo es personal y un OTP es material de autenticación: el proveedor/mailbox
necesita recibirlo para esta finalidad, bajo IE-01/IE-04 y revisión de privacidad.

Resend documenta 30 días de retención de contenido/metadatos, eventos, logs y
métricas. D-032 no autoriza automáticamente esa copia del OTP, ni la convierte en
auditoría de Abogalia. Aprobar tratamiento y acceso, contrastar borrado/retención
del proveedor y destinatario antes de ampliar el piloto aprobado. Fuente:
[retención del proveedor](https://resend.com/docs/knowledge-base/account-quotas-and-limits).
**LEGAL REVIEW REQUIRED** para privacidad/transferencias, términos y tratamiento
antes de datos reales. No enviar PII a nuevos servicios para render/testear HTML.

## Seguridad

La configuración usa recursos propios, responsable y destino confirmados. Las
claves privadas SMTP no van a `.env` leído por agentes, prompts, repo o `VITE_*`.
Ningún conector/panel autenticado ni anterior aprobación local autoriza este cambio
remoto. No abrir pantallas de claves, correo real o datos de clientes para validar.

Desactivar open/click tracking en el proveedor elegido; no archivar contenido OTP
en analítica/auditoría ni reutilizarlo como clave de idempotencia. SMTP soportar
un header de idempotencia no implica que GoTrue lo configure: verificarlo antes
de prometer deduplicación. Mantener certificado/TLS validado y remitente verificado.
Verificar SPF/DKIM/DMARC con DNS real solo en una orden aprobada; no crear un
segundo SPF o endurecer DMARC sin analizar remitentes existentes.

La prueba real la realiza un actor autorizado en su propio buzón/flujo de Auth,
sin capturar ni volcar OTP, cabeceras, cookies o cuerpos sensibles. Evidencia:
resultado booleano, código fijo del error y tiempo/estado mínimo; no dirección,
ID del mensaje asociado a identidad o transcripción del correo. Ante exposición,
detener envío/publicación y coordinar revocación sin repetir el valor.

## Impacto futuro

Correo fallido bloquea altas y recuperación; el login de cuentas previamente
confirmadas sigue su contrato. Reservar presupuesto/cuota para recuperación y
documentar indisponibilidad evita sacrificar confirmación bajo presión. El gate
de configuración no sustituye límites de abuso. Cambiar a marketing, notificaciones
de seguridad adicionales, correo jurídico o Send Email hook requiere diseño propio.

Proveedor, dominio, retención y operación determinan reputación, acceso externo y
costo; Resend Free ya fue elegido; dominio y ampliación operativa siguen pendientes. No crear direcciones o DNS
ligados a una marca discutida sin IE-02 y la revisión de marca aplicable.

## Implementación propuesta

1. A0/A2 revisan este checkpoint y plantillas; A0 conserva IE-01 Approved y Arturo resuelve los parámetros pendientes IE-02..IE-04.
   Registrar parámetros/destino/autorización concreta; mantener pendientes parciales.
2. Orden posterior de operación: comprobar espacio Abogalia, remitente de pruebas/buzón propio para el piloto o dominio propio para público,
   mecanismo privado SMTP y DNS aprobados; configurar plantilla OTP/asunto sin
   tocar correo default de otros productos. Claves mediante responsable/gestor.
3. Mantener confirmación requerida; contrastar longitud/TTL/límites reales con el
   contrato. Verificar envío sólo a buzones controlados autorizados y cuotas del
   piloto. Revisión de términos/tratamiento antes de destinatarios reales del producto.
4. Probar confirmación/recuperación feliz y negativos: código vencido/usado/ajeno,
   cuota, bloqueo SMTP, duplicados, tiempo de entrega y fallo parcial. Comprobar
   cabeceras MIME/From, TLS, autenticación DNS y tracking desactivado sin imprimir
   material sensible. Declarar mail accepted distinto de delivered y de verified.
5. Responsable activa `ABOGALIA_AUTH_EMAIL_READY` sólo tras evidencia revisada;
   caída/desconfiguración conserva 503 honesto. Stop/rollback restaura gate
   desactivado, no un proveedor silencioso ni autoconfirmación. No marcar C02 Done
   únicamente por recibir un correo: proveedor, sesiones y operación mantienen
   sus pruebas y pendientes propios.

[Verificación de esta entrega](../operations/identity-email-verification.md).
Sin SMTP/DNS/envío/recursos nuevos, instalación, conexión a proyecto o datos reales.
