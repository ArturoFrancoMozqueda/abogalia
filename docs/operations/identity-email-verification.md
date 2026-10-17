# Verificación — Correo de Identity, tanda 03

Fecha: 2026-10-12. Base asignada `720c1cf`. Autor A5; revisión A0/A2 pendiente.
Estado: **diseño y fuentes HTML locales preparados; correo real no configurado**.

## Entrega

- [Checkpoint de operación](../checkpoints/identity-email-operations.md), con ocho
  secciones y cuatro paquetes IE-01..IE-04: proveedor/tratamiento; dominio/remitente;
  vigencia/cuotas/abuso; destinatarios/activación.
- [Confirmación HTML](../email/identity-confirmation.html), asunto propuesto
  «Confirma tu correo en Abogalia»; destino GoTrue Confirm sign up.
- [Recuperación HTML](../email/identity-recovery.html), asunto propuesto
  «Recupera tu acceso a Abogalia»; destino GoTrue Reset password.
- Este informe. Son los únicos cuatro archivos propios de esta orden.

El nombre Abogalia es un placeholder de marca de trabajo. No se inventaron dominio,
remitente, Reply-To o contacto. Las plantillas no generan From/To/Subject SMTP;
esos campos se configuran aparte tras aprobación. No contienen emails reales,
códigos de sesión, metadata de clientes, enlaces, imágenes, JS o recursos remotos.
La única variable GoTrue en cada HTML es `{{ .Token }}`; no es un secreto real.

## Verificación local ejecutada

Parser HTML estándar de Python y cálculo local de contraste, sin instalar paquetes,
renderizar datos reales o contactar validadores externos. Resultado: **11/11
comprobaciones pasan en cada plantilla**:

1. Elementos locales/inertes, atributos sin handlers y tablas presentacionales.
2. Etiquetas balanceadas.
3. Lengua `es-MX` en HTML.
4. Dirección `ltr` en HTML; lengua/dirección repetidas en contenedor directo.
5. Un encabezado h1.
6. Título específico.
7. Solo variable `.Token`.
8. Una inserción de código por mensaje.
9. Sin URL, fuente externa, enlace ni dirección inventada.
10. Contraste del texto `#18312c` sobre blanco **13.87:1**, supera 4.5:1.
11. Sustitución sintética en memoria conserva seis dígitos y cero inicial.

La sustitución usó el marcador público `012345`, sin OTP emitido por un proveedor;
no se guardó HTML con código renderizado. El primer harness marcó incorrectamente
el cierre de elementos vacíos `meta`; se corrigió el parser y se repitieron las
comprobaciones. No fue un defecto de las fuentes HTML ni se ocultó un fallo real.

Texto de cuerpo a 16 px, código seleccionable de 32 px, sin imagen de texto, CSS
en línea y contenedor fluido con máximo 560 px. La pérdida de estilos deja título,
propósito, código y acción como texto normal. Lectura manual de instrucciones
contrasta con los formularios existentes y no promete confirmación profesional,
plazo numérico de OTP o cierre exitoso por recibir un correo.

No se ejecutó render en navegador ni en clientes de correo, VoiceOver, modo oscuro,
validación MIME o captura de pantalla. No afirmar compatibilidad Outlook/Gmail/Apple
Mail por pasar el parser. Esas verificaciones, incluida alternativa MIME text/plain,
forman parte del piloto autorizado posterior.

## Contrato y fuentes oficiales consultadas

Consultadas el 2026-10-12; no se revisó configuración efectiva de ningún proyecto.

| Fuente | Hallazgo utilizado |
|---|---|
| [Supabase templates](https://supabase.com/docs/guides/auth/auth-email-templates) | Go Templates; `.Token` OTP de seis dígitos en cuerpo. No se usa ConfirmationURL/TokenHash ni metadata editable |
| [verify_otp Python](https://supabase.com/docs/reference/python/auth-verifyotp) | Verificación por email/token con tipo según flujo; contrato de Abogalia usa `email` para confirmación y `recovery` para recuperación |
| [signup](https://supabase.com/docs/reference/python/auth-signup), [reset password](https://supabase.com/docs/reference/python/auth-resetpasswordforemail) | La solicitud de correo no equivale a completar confirmación/cambiar contraseña; mantener confirmación requerida y OTP posterior según contrato |
| [SMTP Supabase](https://supabase.com/docs/guides/auth/auth-smtp) | Mailer default limitado a equipo, 2/hora y sin SLA; SMTP propio habilita destinatarios, con límite inicial bajo |
| [Cambio Free 2026-06-03](https://supabase.com/changelog/46599-changes-to-email-template-customisation-on-free-tier) | Free nuevo con default no puede personalizar; SMTP propio permite personalización sin obligar Pro |
| [Límites Auth](https://supabase.com/docs/guides/auth/rate-limits) | Signup/recovery usan espera predeterminada de 60 segundos; parámetros reales por confirmar, sin asumir forwarding de IP con publishable |
| [Resend cuotas/retención](https://resend.com/docs/knowledge-base/account-quotas-and-limits), [plan Free](https://resend.com/pricing) | Resend SMTP Free fue elegido por Arturo sin overages: 100/día UTC, 3,000/mes y 3 dominios. Contenido/metadatos conservados 30 días requieren decisión de tratamiento |
| [Resend SMTP con Supabase](https://resend.com/docs/send-with-supabase-smtp) | Guía de uso general requiere dominio verificado; el piloto al buzón propio tiene la excepción documental indicada abajo. Nada configurado por esta entrega |

La [página oficial SMTP](https://resend.com/features/smtp-service) incluye
`onboarding@resend.dev`; la [restricción de pruebas](https://resend.com/docs/knowledge-base/403-error-resend-dev-domain)
limita el destinatario a la dirección asociada a la cuenta Resend. De ambas se
infiere que el piloto SMTP sin dominio es documentalmente viable en ese único
buzón. Falta validarlo en la cuenta/proyecto reales. Los sinks de ejemplos no
reciben OTP utilizables; no acreditan recuperación real. El remitente de pruebas
no se agrega a HTML ni se presenta como dominio propio de Abogalia.

Skills email-best-practices (transaccional, accesibilidad y entregabilidad) y
Supabase aplicadas. La primera propone texto alternativo; no se supone que GoTrue
lo genere automáticamente por recibir estos HTML. No se instaló React Email ni
se llamó Resend CLI, API, MCP, SMTP o servidor DNS.

## Evidencia pendiente antes de activar

Revisión A0/A2 y parámetros pendientes IE-02..IE-04; IE-01 proveedor Free sin
overages y alcance piloto frontend local con Supabase real están Approved por
Arturo. Falta destinatario privado asociado a la cuenta Resend, límites de prueba
y orden/configuración concreta; dominio propio sigue Pending y no existe. Nunca enviar marcadores
`.invalid` de tests a SMTP real. La inspección de OTP real pertenece al usuario
autorizado en su flujo de Auth; no copiar el código o cuerpo al repo, logs, chat,
tools, capturas o reportes.

Antes de `ABOGALIA_AUTH_EMAIL_READY=1`: plantilla realmente instalada, correo
sin enlaces de credenciales, seis dígitos/TTL verificados, remitente/DNS/TLS,
tracking desactivado, entrega y fallos/cuotas, códigos usados/vencidos/ajenos,
confirmación seguida de login y recuperación con revocación/fallo parcial.
Registrar solo resultados mínimos; SMTP accepted no acredita delivered ni cuenta
verified. Reenvío de confirmación no se añade sin contrato.

Resend SMTP Free sin overages y el alcance del piloto quedaron Approved por
Arturo. SMTP/DNS/envíos no están Implemented. Dominio propio, plazo OTP propuesto
de 10 minutos y controles de cuota siguen pendientes. D-032 sobre 30/90 días no autoriza guardar
contenido OTP en auditoría propia ni decide copia/retención del tercero. Privacidad,
transferencias y términos: LEGAL REVIEW REQUIRED antes de datos reales.
Sin `.env`, secretos, clientes, Kova, recursos nuevos, envíos, DNS, CI remoto,
despliegue, commits o cambio de configuración runtime.
