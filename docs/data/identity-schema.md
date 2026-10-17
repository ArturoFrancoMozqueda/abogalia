# C02 — Custodia PostgreSQL de sesiones

Fecha: 2026-10-12. Implementación local asignada A3; revisión A0/A4 pendiente.
Base de trabajo `1eaf758d776a77e0507629c9e33c6c1d969bee79`, worktree de datos
aislado. D-031/D-032/D-033 autorizan este alcance: cuentas mínimas, sesión y
auditoría C02. No se crean LawFirm, Membership, Client ni datos jurídicos C03+.
Referencia: [checkpoint](../checkpoints/identity-and-contexts.md),
[modelo](identity-model-proposed.md), [contrato HTTP](../contracts/identity-api.md).

## API entregada

`PostgresSessionStore(dsn: str, cipher_key: bytes, clock: Clock | None = None)`
usa Fernet y un rol runtime dedicado. DSN y clave se inyectan por el ejecutor desde
mecanismos excluidos de Git. No leer `.env`, imprimir configuración o copiar valores
en herramientas. `SessionRecord` compartido tiene repr desactivado.

| Operación | Garantía local |
|---|---|
| `create(record)` | Crea cuenta mínima si el sujeto Auth verificado no existe; nunca reactiva cuenta cerrada/restringida; rechazo de intento anterior a cierre global |
| `transaction(digest)` | Digest SHA256 de cookie opaca, nunca cookie cruda; contexto solo transaccional, bloqueo de usuario antes de sesión, commit/rollback automático |
| `tx.record` | Registro descifrado interno o None; falta de fila/caducidad no devuelve tokens; nunca serializarlo como JSON Auth |
| `tx.save(record)` | Actualiza dentro del bloqueo; permite rotación de digest y tokens; conserva sujeto, SID y hora inicial absoluta; actividad no retrocede |
| `tx.delete()` | Retira fila completa y material cifrado; no puede recrearse con save posterior |
| `tx.revoke_subject(subject)` | Solo sujeto de la sesión bloqueada; retira todas sus sesiones y marca cutoff; no permiso de administrador por body |
| `store.revoke_subject(subject)` | Recuperación con principal verificado por API, sin cookie; mismo bloqueo/cutoff, nunca sujeto tomado del payload sin validar |

El servicio debe fijar `created_at` **al comenzar el intento de login**, antes de
llamar Auth. `users.sessions_revoked_at` impide que un intento anterior al cierre
global inserte sesión cuando por fin obtiene el lock. Un login nuevo posterior al
cierre puede crear sesión si la cuenta permanece activa y Auth lo permite.

Las conexiones store/probe/mantenimiento fijan `passfile=os.devnull` y contraseña
tomada exclusivamente del DSN inyectado, o vacío explícito cuando está ausente:
no recurren a `.pgpass` o PGPASSWORD ajenos. El parser interno no emite esos valores.
Las fixtures también deshabilitan passfile/contraseña implícitos, incluidos sus
DSN derivados para lecturas de prueba. Validación de destino explícito/rol y
rechazo de service corresponde además al loader de runtime coordinado por A0.
La validación de firma/claims, duración JWT máxima 15 minutos, MFA y vigencia del
proveedor pertenecen al servicio/probe; cifrar un token no demuestra autenticación.

## Esquema y propiedad

`001_identity.sql` es instalación inicial transaccional, no script idempotente.
Reaplicarlo falla y no se presenta como upgrade. El operador autorizado prepara
roles separados; la migración no crea conexiones, contraseñas ni recursos remotos.

| Objeto | Datos | Propiedad y acceso |
|---|---|---|
| `identity.users` | UUID sujeto, estado active/restricted/closed, created_at/closed_at/cutoff | Owner dedicado; runtime inserta/lee su sujeto y solo actualiza cutoff; no modifica estado o fecha de cierre |
| `identity.app_sessions` | Digest, sujeto, SID, assurance, fechas y sobre cifrado | FK RESTRICT a users; runtime limitado por digest de sesión o sujeto validado; grants SELECT/INSERT/UPDATE/DELETE con RLS |
| `identity.audit` | ID, sujeto lógico, acción fija y fecha | Runtime INSERT sin lectura/edición/borrado; sin email, relato, tokens, digest o cargas variables; no FK que borre historia de terceros |

Esquema privado sin grants PUBLIC, sin vistas ni funciones SECURITY DEFINER.
RLS y FORCE RLS en las tres tablas. `abogalia_identity_owner` posee objetos y
política explícita de mantenimiento; `abogalia_identity_runtime` no es propietario,
superusuario ni BYPASSRLS, y no puede crear objetos, TRUNCATE, editar permisos o
leer auditoría. No se conceden REFERENCES ni facultades de administración al runtime.
Los índices cubren sujeto de sesión, vencimiento/actividad, cierre y fecha audit.

El sobre Fernet incluye email/access/refresh, ligado a digest/sujeto/SID para
detectar sustitución entre filas. La clave solo reside en el proceso que custodia
sesiones; backup de base sin ella no revela esos valores. Su aprovisionamiento,
rotación/recovery y backups de claves requieren operación aprobada; no hay una
clave real configurada por esta entrega. Fernet no oculta fecha de generación ni
tamaño del sobre y no protege un proceso comprometido con acceso a la clave.

RLS recibe `abogalia.digest` y `abogalia.subject` mediante `set_config(..., true)`.
Primero el digest habilita lookup; el sujeto se obtiene del registro, después se
bloquea users y se relee/lockea la sesión. No sale de una preferencia del navegador.
En create/recovery el llamador es exclusivamente API que verificó Auth. El runtime
de SQL es una frontera confiable: un poseedor de su DSN puede fijar contexto;
estas políticas no protegen contra compromiso total del proceso/API o sus claves.
No exponer ese DSN ni una ruta SQL al navegador; no se presume `auth.uid()` en SQL.

## Expiración, cierre y mantenimiento

12 horas absolutas y 30 minutos de inactividad, con igualdad del límite caducada.
JWT expirado puede requerir renovación dentro de una sesión de aplicación vigente;
no se borra toda sesión simplemente por `token_expires_at`. La lectura de una
sesión de aplicación caducada elimina fila/tokens; un job separado debe limpiar las
sesiones no visitadas. No se afirma borrado físico justo al segundo del límite sin
ese job. El almacenamiento no modifica actividad por una mera lectura.

`PostgresIdentityMaintenance(dsn_owner, clock).purge(retired_subjects=...)` ejecuta
en transacción: sesiones caducadas/inactivas/cuenta no activa; cuentas cerradas a
30d con retiro Auth confirmado; auditoría a 90d. A igualdad del umbral son elegibles.
Devuelve solo `sessions/accounts/audit_events/blocked_accounts` y
`retention_compliant`. Si faltan confirmaciones, limpia igualmente tokens caducados
y auditoría vencida, pero mantiene bloqueo de esas cuentas y devuelve
`retention_compliant=False`; nunca éxito total ni retención extendida aprobada.
Un fallo SQL revierte la transacción; runtime no tiene permisos de mantenimiento.

La lista `retired_subjects` es una afirmación verificada del ejecutor autorizado,
no decisión del cliente ni comprobación real de proveedor implementada aquí.
Cerrar una cuenta requiere revocar/retirar identidad Auth antes de purgar el bloqueo
local; de otro modo ese sujeto podría volver a autenticarse. Si falta confirmación
a 30d, reportar incumplimiento operacional pendiente y corregirlo, sin declarar
retención extendida aprobada ni crear tombstone perpetuo. No hay nuevo endpoint de
cierre en esta entrega: las pruebas usan transición SQL owner sobre datos sintéticos.
El borrado de cuenta no borra auditoría de 90d ni relaciones futuras por cascada.

Tratamiento en Auth, backups/restore, solicitudes de derechos y datos jurídicos
requieren operación/revisión propias. **LEGAL REVIEW REQUIRED** antes de datos reales.
La purga no es un scheduler ni evidencia de eliminación remota/restore ejecutados.

## Verificación local y límites

`ABOGALIA_TEST_POSTGRES_DSN` del runner identifica solo un cluster PostgreSQL local
aislado: socket Unix, puerto, postgres, abogalia_test_owner; nada de contraseña,
service o opciones externas. Fixtures rechazan destinos no conformes/missing y no
hacen skip silencioso. Crean exclusivamente DB abogalia_storage_test y los dos
roles de owner/runtime asignados, con preparación separada del ejercicio bajo runtime real.
No SQLite ni mocks de PostgreSQL/RLS. Clave efímera y tokens públicos sintéticos.

Casos: grants/owner/BYPASSRLS/FORCE; lookup ajeno y contexto ausente; mover sujeto;
ciphertext y binding; rollback/rotación/borrado; invariantes de save; bordes 12h/30min;
global y cutoff; refresh serializado; refresh frente a revoke; create frente a global;
cuenta cerrada, purga 30d/90d/idempotencia y falta de retiro Auth; instalación inicial
y reaplicación rechazada. Una cuenta pendiente no conserva tokens de terceros ni
auditoría vencida. Salidas de pruebas restringidas a estado/nombres/conteos.

`PostgresSessionProbe(dsn_readonly).active(provider_session_id, subject)` usa una
conexión separada con transacción READ ONLY y SELECT EXISTS de `auth.sessions`
por id/user_id. Devuelve booleano, no IDs o filas. Error/configuración inválida
produce StorageUnavailable sin diagnóstico; el servicio debe fallar cerrado.
La prueba local tiene `auth.sessions` sintética y tercer rol
`abogalia_identity_probe` autorizado expresamente por A0: LOGIN sin superuser,
createDB/createRole, herencia o BYPASSRLS; solo USAGE auth y SELECT(id,user_id),
sin lectura de columna privada adicional ni escritura/acceso al esquema identity.
Estos grants aparecen únicamente en fixture local; nunca en la migración.

Documentación oficial consultada el 2026-10-12:
[Psycopg transactions](https://www.psycopg.org/psycopg3/docs/basic/transactions.html),
[PostgreSQL 16 RLS](https://www.postgresql.org/docs/16/ddl-rowsecurity.html),
[locks](https://www.postgresql.org/docs/16/explicit-locking.html),
[Fernet](https://cryptography.io/en/latest/fernet/).
Sin migración remota, lectura del esquema Auth real o proveedor real. Probe remoto
necesita DSN separado y aprobación/verificación operativa con privilegios acotados;
la fixture no prueba ese permiso ni su viabilidad en el proyecto real. No se
conceden grants sobre Auth en esta migración. CI/release/restore pendientes.

Resultado ejecutado en cluster local aislado PostgreSQL 16: **16 pruebas pasaron**;
Ruff check y formato de los tres archivos Python pasan. No se simuló PostgreSQL,
roles, RLS o cifrado; Auth remoto sigue sin verificar. Incluye rechazo de store
configurado con owner/superuser y pruebas del probe con sujeto/SID incorrecto,
columna privada y escritura denegadas. Conexiones verifican rol efectivo dedicado,
sin superuser/BYPASSRLS ni membresía owner para runtime/probe. Mantenimiento exige
rol owner efectivo. A0 ejecutará scanner redactado, suite desde cluster fresh e
integración; aprobación independiente A0/A4 pendiente. No commit/push/deploy.
