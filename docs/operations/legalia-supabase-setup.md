# Legalia — instalación Supabase y revisión de seguridad

Fecha: 2026-10-13, America/Mexico_City. Proyecto `spohytnxscljtitvmdab`;
organización `tagovxtvdicxjweeerwi`, Free, us-east-1, PostgreSQL 17.11.
Arturo creó el proyecto y pidió instalar lo ya aprobado y revisar best practices.
La pregunta específica de creación de roles/grants recibió «HAZLO TODO».
El producto no se denomina piloto. Configuración local no implica servicio público listo.

## Instalación ejecutada

Se verificó proyecto y organización en el panel antes de cada operación. El conector
anterior no tiene acceso a esta nueva cuenta; se usó exclusivamente el SQL Editor
de Legalia, sin consultar filas de usuarios, sesiones o auditoría.
Se ejecutó una transacción equivalente a los cuerpos públicos revisados de
[install_identity_owner_runtime.sql](../../scripts/sql/install_identity_owner_runtime.sql)
con formato compacto y comentarios omitidos. No hubo contraseñas ni secretos.
Se crearon owner NOLOGIN y runtime LOGIN, ambos sin SUPER/CREATEROLE/CREATEDB,
herencia, replicación o BYPASSRLS. SET del instalador y CREATE del owner se
revocaron dentro de la misma transacción antes de COMMIT.

La verificación posterior [verify_identity_owner_runtime.sql](../../scripts/sql/verify_identity_owner_runtime.sql)
dio once booleanos true: roles mínimos, tres tablas privadas con ENABLE/FORCE RLS,
SET/herencia/CREATE temporales retirados, runtime sin owner/DDL, anon/authenticated
sin USAGE, actualización limitada al cutoff de revocación, auditoría solo INSERT
y probe diferido. Esto no acredita autenticación real ni predicados RLS con clientes.

## Advisor

Antes había dos advertencias de EXECUTE público sobre la función preexistente
`public.rls_auto_enable()`, owner postgres, retorno event_trigger, SECURITY DEFINER.
Se verificaron únicamente metadatos. Su trigger ensure_rls sigue habilitado para
CREATE TABLE, CREATE TABLE AS y SELECT INTO; REVOKE no dispara ese filtro.
[harden_default_rls_function.sql](../../scripts/sql/harden_default_rls_function.sql)
revocó solo EXECUTE de PUBLIC/anon/authenticated con RESTRICT, preservando firma,
propietario, modo y metadatos del trigger. Resultado browser_execute_denied=true.
Security Advisor fresco: cero errores, cero advertencias, cero sugerencias.
No afirmar auditoría del cuerpo interno de la función ni certificación global.

Performance Advisor detectó tres advertencias de current_setting evaluado por fila.
Tras revisión independiente y 299 pruebas integradas locales correctas, se aplicó
[optimize_identity_rls.sql](../../scripts/sql/optimize_identity_rls.sql), con el mismo
formato compacto sin comentarios. Conserva los predicados y usa subconsultas escalares
para evaluar contexto por sentencia. SET temporal del instalador se revoca antes
de COMMIT; no concede CREATE ni amplía autorización. La instalación inicial usó
predicados previos; 001 y la receta fresh ahora incluyen la forma optimizada.
Advisor fresco final: seguridad cero errores/advertencias; rendimiento cero
errores/advertencias y cinco avisos informativos de índices sin uso en la base nueva.
Índices necesarios conservados; no se midió rendimiento bajo carga real.

## Auth y correo

Confirmación requerida verificada. Anonymous y manual linking desactivados.
Email activo; proveedores OAuth/Phone no habilitados. OTP guardado: 600 segundos,
seis dígitos. JWT guardado: 900 segundos; refresh replay protection habilitada,
reuse interval 10 s. Site URL guardado: http://127.0.0.1:5190; sin redirect URLs.
TOTP Enabled verificado; SMS MFA Disabled. Limit duration of AAL1 sessions activo
con ventana de quince minutos; no se alteraron estos valores. JWKS público del
proyecto devolvió una clave ES256; se registró únicamente cantidad y algoritmo.

Arturo confirmó que introdujo y guardó la clave SMTP privadamente. El panel
desbloqueó la edición de plantillas, corroborando Custom SMTP configurado, sin
abrir su campo Password. Formulario preparado anteriormente: remitente de prueba
público onboarding@resend.dev, nombre Legalia, smtp.resend.com, puerto 465, usuario
resend e intervalo 60 s. No se leyó clave, contraseña, `.env` real ni correo.

Se instalaron y guardaron Confirm sign up y Reset password con las fuentes del
repositorio y asuntos «Confirma tu correo en Legalia» / «Recupera tu acceso a Legalia».
El panel confirmó guardado; la vista previa de recuperación muestra Legalia,
código {{ .Token }} en cuerpo y ningún enlace. Sin envíos ni OTP reales. Guardar
SMTP no acredita que la clave sea válida, TLS efectivo o entrega; faltan ensayos
controlados. Dominio verificado pendiente para enviar a usuarios. Arturo confirmó
el destinatario propio asociado a la nueva cuenta Resend; su dirección se conserva
solo en el contexto privado de operación, sin publicarla en el repositorio.

## Bloqueos reales y operación

Auth USAGE WITH GRANT OPTION=false; SELECT grantable de id/user_id=true. La receta
003 permanece sin aplicar; no se otorgó service_role ni membresías administradas,
no se desactivó RLS ni se creó una función para sortear el permiso. Runtime cerrado
hasta resolver probe, credenciales separadas, TLS y entrega OTP verificadas.

Retención 30/90 y responsable Arturo siguen aprobados; scheduler real y evidencia
confiable de retiro Auth siguen pendientes. No se instalaron cron ni jobs reales.
El ejecutor histórico run_identity_email_pilot.py conserva sus límites y queda como
herramienta de ensayo, no como operación del producto; no se inicializó ni ejecutó.
No se accedió o modificó Kova ni el Supabase anterior. No hosting, compra o upgrade.

Los nombres técnicos de variables, cookies, roles y paquetes se conservan para
evitar renombrado general. Launcher/Auth URL y pruebas ahora fijan Legalia y rechazan
el proyecto anterior; `.env` queda para actualización privada del operador.
El launcher es la entrada local aprobada y comprueba host/rol/puerto/TLS. El
validador genérico de DSN, fuera del launcher, conserva soporte de fixtures y no
garantiza el mismo confinamiento de hosts/TLS: endurecer la futura entrada de
producción antes de desplegar; no arrancar por otra ruta para salvar sus gates.
LEGAL REVIEW REQUIRED para el tratamiento jurídico y puesta en operación pública.

## Validación local y publicación

Tres agentes revisaron SQL, destino/Auth y plantillas. 299 pruebas API/SQL pasan
en PostgreSQL temporal aislado; Auth por transporte sintético. 31 pruebas de
herramientas stdlib y los dos validadores de plantillas pasan. make check-api
incluye lint, formato, integridad de dependencias y creación de la aplicación.
Una primera prueba de upgrade detectó colisión de variable RECORD con alias SQL;
se corrigió antes de ejecutar remotamente y la suite completa pasó después.
No login/MFA/correo reales, scheduler, despliegue, backup/restauración o CI remoto.
