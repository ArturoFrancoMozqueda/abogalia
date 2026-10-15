# Registro privado de cuenta APP de ensayo

2026-10-15. C02, D-036/D-039. Herramienta preparada y probada solo con transporte
sintético; no ejecutada contra Legalia por esta entrega. Arturo autorizó el buzón
controlado para crear una cuenta APP; el código no incorpora ese destinatario.

## Operación humana privada

Desde terminal interactiva real, con el Python del entorno fijado del repositorio:

```sh
apps/api/.venv/bin/python scripts/register_identity_test_account.py --run
```

No argumentos con valores, pipes, terminal grabada o entrada mediante herramientas
de agentes. Se pide atestación de cuenta APP sintética exclusiva y buzón autorizado,
mailbox oculto, contraseña nueva dos veces y OTP oculto. La contraseña debe quedar
bajo custodia privada de Arturo para el ensayo posterior; este script no la guarda.
Nunca enviar contraseña, OTP, capturas de correo o valores `.env` al chat.

Si el directorio `.identity-pilot` está completamente ausente, la herramienta pide
la atestación SMTP/plantillas/OTP600s/6d/pausa60s/JWT900 vigente del helper auditado
antes de crear el marcador privado0700/0600. Si el directorio ya existe, utiliza
estrictamente su marcador original: no lo inicializa, renueva, repara ni reinicia,
aunque falte el archivo, esté corrupto o haya vencido. Mantiene hash del único
buzón, TTL24h, pausa60s y cupo máximo histórico seis. Ante bloqueo, detenerse y
coordinar con el responsable; no borrar marcador para obtener otros seis envíos.

Un único signup por invocación, con reserva durable/fsync anterior a HTTP; un fallo
consume su reserva. No reenvío, retry, recover o login alternativo. Invocar otra
vez es otra solicitud consciente del mismo cupo, no continuación automática.
La aceptación de signup no acredita entrega, cuenta nueva ni confirmación: el
proveedor puede evitar enumeración para cuentas existentes. El prompt OTP explica
esa diferencia. El código solo viaja en cuerpo POST /verify, `type=email`, nunca
URL. Un código rechazado/vencido/ya usado o timeout no se reintenta. Si no llega
correo, interrumpir privadamente; no introducir valores ficticios ni pedir reenvío
para forzar una prueba positiva.

## Fuente y confinamiento

Se reutilizan sin cambios `run_identity_email_pilot.py` y sus controles de marcador,
reserva, parser de publishable y getpass sin fallback. El parser abre `.env` raíz
solo dentro del proceso runtime y selecciona exclusivamente publishable; ningún
agente lee sus valores. No instalar variables en entorno ni importar main/runtime.
No se cambian Identity/email flags, DB, SQL, grants, presupuesto, dependencias,
configuración SMTP ni cuentas de proveedor. Sin service_role ni rutas admin.

HTTPS fijo a Legalia `spohytnxscljtitvmdab`; clientes sin proxy de entorno ni
redirect y timeout10s. Signup queda restringido al helper existente; gateway de
confirmación solo permite verify email, JWKS y logout local. GET/user utiliza el
adaptador activo aislado aprobado. No operaciones globales, registro público,
clientes reales, roles profesionales, invitaciones o tratamiento jurídico.

## Confirmación y limpieza

Después de signup aceptado, Arturo revisa el buzón privado e introduce seis dígitos.
Se comprueba otra vez vigencia del marcador antes de verificar. La respuesta debe
producir identidad confirmada, JWT firmado con issuer/audience/TTL900/sub/SID/aal
válidos y sujeto/email ligados al buzón introducido; GET/user debe confirmar sesión
activa con ese mismo token. Metadata editable no concede permisos.

Finalmente se intenta exactamente un logout local para cualquier par devuelto,
incluso si falla la validación anterior. Solo ausencia definitiva HTTP con token
original aún criptográficamente válido permite afirmar cleanup=true. ACK de logout
solo, JWT vencido, 403 genérico o indisponibilidad dejan cleanup_failed. Timeout de
verify o respuesta inválida puede haber creado sesión sin devolver referencia:
cleanup_failed exige comprobación/retiro privado por Arturo, sin retry OTP ni
logout ambiguo. Una interrupción abrupta puede impedir finally. Strings existen
en memoria temporal y Python no promete borrado seguro; no persistirlos en archivo,
logs, salida, marcador o informe. Cierra cliente y elimina referencias al finalizar.

Salida JSON fija: status `verified`, `registration_pending`, `cleanup_failed` o
`registration_unavailable`; seis checks booleanos y cleanup booleano. Exit0 solo
verified. La salida omite email, OTP, contraseña, sujeto/SID/JWT, cabeceras y errores
crudos. Durante operación se suprimen logging, streams Python y FD1/2; prompts
privados usan TTY. Un error de signup indeterminado también queda cleanup_failed;
no acredita sesión presente, pero evita prometer limpieza sin evidencia.

## Evidencia y límites

Pruebas con archivos privados sintéticos en tmp, MockTransport y claves efímeras
en memoria: reserva previa a red, máximo un signup/verify/logout, tipo email,
contraseña doble, marcador preservado, cupo/TTL, duplicado, OTP/error/timeout,
logout ignorado/ambiguo, JWT vencido, CLI sin TTY/argumentos y supresión nativa.
Resultado: 20 pruebas sintéticas pasan; Ruff check y formato pasan. A2 ejecutó
las mismas 20 pruebas y revisó fuente/documento de forma independiente, sin
bloqueantes de fuente. Escaneo e integración quedan a cargo de A0.

No ejecución real, correo enviado ni cuenta confirmada acreditados aquí. Un verified
real cubriría posesión/confirmación y revocación local de esa sesión; no prueba
recuperación, MFA, cierre global/aislamiento, navegador/API/custodia SQL, retiro
Auth definitivo, retención o activación de producto. El siguiente paso independiente
es `verify_identity_auth_sessions.py` con la misma cuenta ya confirmada y contraseña
privada; tampoco habilita flags automáticamente.

Fuentes oficiales consultadas2026-10-15:
[plantillas/Token seis dígitos](https://supabase.com/docs/guides/auth/auth-email-templates),
[verifyOTP](https://supabase.com/docs/reference/python/auth-verifyotp) y
[sesiones](https://supabase.com/docs/guides/auth/sessions).
Se conserva `email` del contrato existente para confirmación. Changelog Markdown
no admitido por herramienta; HTML oficial revisado en esta tanda, sin dependencia
nueva ni downgrade TLS. Las fuentes no sustituyen aceptación de la versión real.
