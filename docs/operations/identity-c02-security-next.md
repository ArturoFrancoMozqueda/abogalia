# C02 — Seguridad y operación siguiente

Fecha: 2026-10-13. A2/A3; base eba6cbedb631. Investigación pública y revisión
documental; sin SQL remoto, secretos, .env, contactos externos o commits.
Destino vigente Legalia spohytnxscljtitvmdab/tagovxtvdicxjweeerwi.

## Estado verificable y bloqueo SQL

La evidencia integrada [instalación Legalia](legalia-supabase-setup.md) registra
owner/runtime mínimos, tres tablas FORCE RLS, retirada de privilegios temporales,
ACL de la función por defecto y optimización de políticas. Advisor sin errores o
advertencias no prueba login, revocación real, correo, retención o restauración.

La misma evidencia registra USAGE auth grantable=false, columnas id/user_id
grantable=true y PUBLIC sin USAGE. PostgreSQL distingue uso de un privilegio de
la capacidad de concederlo: CREATEROLE o SELECT de columnas no habilita conceder
USAGE del esquema. [PG17 GRANT](https://www.postgresql.org/docs/17/sql-grant.html).
Cambiar SQL Editor por CLI/Management API no demuestra otro grantor; Supabase
documenta que [consultas del Dashboard usan postgres](https://supabase.com/docs/guides/database/postgres/roles).

No encontré un mecanismo documentado de autoservicio hosted para dar este USAGE
al rol personalizado bajo las restricciones actuales. **Bloqueo honesto**, no
afirmación de imposibilidad absoluta ni permiso de cambiar ownership/memberships.
Las [permisiones de plataforma](https://supabase.com/docs/guides/platform/permissions)
advierten que el servicio necesita conservar sus entidades administradas; la guía
de [PUBLIC y roles personalizados](https://supabase.com/docs/guides/troubleshooting/custom-role-inherits-privileges-that-were-not-explicitly-granted-ddaa1c)
confirma que NOINHERIT no elimina derechos PUBLIC y que auth no otorga USAGE aPUBLIC.
Una explicación histórica que atribuye permisos amplios a postgres no demuestra
WITH GRANT OPTION vigente en este proyecto.

Si se mantiene SQL, Arturo/A0 pueden solicitar al proveedor un mecanismo soportado
para USAGE a un rol dedicado, sin compartir credenciales o datos de usuarios.
No se ha enviado solicitud ni se promete que soporte concederá ese permiso.
Antes de usar003 hace falta capacidad legítima, prueba efectiva con rol real,
solo SELECT(id,user_id), columnas privadas/escritura negadas y continuidad de Auth.
No conceder USAGE aPUBLIC/anon/authenticated, managed membership, SECURITY DEFINER,
propiedad de Auth, service_role o BYPASSRLS para desbloquear la aplicación.

## Alternativa soportada propuesta

La documentación actual de [Auth avanzado](https://supabase.com/docs/guides/auth/server-side/advanced-guide)
explica validación activa mediante getUser. Puede cambiarse el probe a GET/user
con bearer custodiado y publishable pública, sin permiso SQL administrado. Es una
alternativa técnica condicionada, no evidencia de revocación desplegada ni código
autorizado por esta investigación. [Checkpoint con una decisión](../checkpoints/identity-session-validation.md)
define contrato mínimo, enlace JWT/sub/SID, controles por frontera, errores y
prueba real de cierre con JWT aún vigente. Mantener fail-closed mientras falta
aprobación/verificación. No usar falta de DSN como selección automática de HTTP.

## Retención y mantenimiento

D-032/D-036 mantienen **30 días** cuenta/evidencia mínima de membresía terminada y
**90 días** auditoría; Arturo es responsable de cierre/retiro Auth y fallos.
No se reabren parámetros aprobados. Membership aún no existe: no declarar su
retención implementada. Datos jurídicos/proveedor/backups se tratan aparte.

PostgresIdentityMaintenance ya prueba purga transaccional e idempotente local:
sesiones vencidas/inactivas/cuenta no activa, auditoría90d y cuentas30d únicamente
con retiro Auth confirmado. Una cuenta pendiente no mantiene tokens de terceros
ni auditoría vencida. blocked_accounts/retention_compliant=False informa
incumplimiento; conservar bloqueo pendiente no es retención extendida aprobada.
El runner actual está confinado a fixture sintética, no sirve para operación remota.

Pendientes operativos concretos:

- **Ejecutor:** owner es NOLOGIN. Un scheduler que usa DSN postgres/SETowner sería
  una nueva credencial administrativa y no queda autorizado por pruebas fixture.
  Diseñar rol de mantenimiento separado, grants/RLS y alcance temporal; no adaptar
  runtime para custodiar owner ni ampliar conexión del proveedor por inferencia.
- **Retiro verificable:** logout/revocación de sesión, GET/user negativo o una lista
  de UUIDs no demuestran eliminación permanente de identidad. Definir comprobación
  confiable del ejecutor, sujeto/operación/fecha, tratamiento privado de evidencia,
  autorización y concurrencia antes de borrar bloqueo. No fabricar confirmaciones
  ni tombstones indefinidos. [Gestión Auth](https://supabase.com/docs/guides/auth/managing-user-data).
- **Ejecución:** parametrizar periodos/cortes UTC ya aprobados; elegir scheduler,
  responsable de ejecución y recepción privada de fallos. Un ciclo diario puede
  eliminar después del umbral: concretar SLA operacional sin agregar retención.
  Limpieza de sesiones requiere cadencia propia además de borrado al acceso.
- **Fallo/restore:** reintentos acotados no cambian evidencia faltante. Verificar
  cleanup e idempotencia en datos sintéticos y restauración sin reintroducir
  identidades retiradas; no declarar éxito si parte del mantenimiento quedó pendiente.

No propongo aún código remoto de mantenimiento compatible con el contrato actual:
faltan ejecutor mínimo y prueba de retiro. Puede continuar prueba/documentación
local, manteniendo retired_subjects vacío hasta recibir orden específica. El
[checkpoint de retención](../checkpoints/identity-retention-operations.md) conserva
lo autorizado y los límites; LEGAL REVIEW REQUIRED antes de datos reales.

## Revisión runtime y próximos gates

Revisión independiente por lectura del endurecimiento runtime A4: default remoto
fija destino directo Legalia o dos session poolers publicados, role o role.ref
exactos, postgres/5432/verify-full y campos permitidos; bloquea PG* por presencia
sin leer valores, salvo passfile que las conexiones sobreescriben. Fixture Python
opt-in no se activa por env/development/main; exige socket y padre privados/propios
y DB sintética. No bloqueantes detectados en ese confinamiento.

Endurecimiento de custodia conexa autorizado por A0 antes de activación: libpq puede
seleccionar cert/key cliente de sus rutas predeterminadas con sslcertmode=allow;
rechazar PG* y passfile no cubre ese default. `_credentials` ahora fija
`sslcertmode=disable` internamente en store/probe/maintenance, sin ampliar campos de
entrada DSN. Cliente libpq<16, versión no entera o error de parser fallan antes de
connect; no fallback. [Control TLS libpq16](https://www.postgresql.org/docs/16/libpq-connect.html#LIBPQ-CONNECT-SSLCERTMODE)
documenta la opción (PG15 no la contiene). Se leyó solo metadata de versión cliente:
180006. 22 pruebas de kwargs/caminos/versiones/rechazo/redacción pasan; Ruff y formato
pasan. A4 completó revisión independiente sin bloqueantes y repitió las 22 pruebas.
El coordinador ejecutó la suite integrada con PostgreSQL temporal aislado: 380 pasan.
No se afirma lectura/exposición de un archivo real ni se consultó su presencia.
La fuente pública [libpq16 OpenSSL](https://github.com/postgres/postgres/blob/REL_16_STABLE/src/interfaces/libpq/fe-secure-openssl.c)
omite carga del certificado cliente en disable, con have_cert=false que evita carga
de su clave. No se cambiaron CA/verificación de servidor, credenciales, dependencia
o configuración del operador.

Faltan gates separados: mecanismo de validación activa aprobado, runtime privado
configurado por operador, comprobación del rol/TLS real, entrega OTP controlada,
registro/recuperación/MFA/cierre real y operación de retención. No todos se resuelven
con getUser. Ninguna prueba local/MockTransport sustituye prueba del proveedor.

Fuentes oficiales consultadas el 2026-10-13; índice changelog Markdown no accesible
por herramienta, alternativa [changelog oficial HTML](https://supabase.com/changelog?tags=security).
Sin cambio de fuente de validación de sesiones, aplicación remota, servicio de
soporte, jobs, nuevas tablas o secretos en esta entrega. Solo endurecimiento local
aprobado, investigación y propuesta de contrato.
