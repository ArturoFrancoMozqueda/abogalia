# Retención local coordinada C02/C03

Fecha2026-10-15. Basefe75a8b1f17b. AutorA2/A3; revisión independienteA4 sin bloqueantes
en esquema actual, con precisión sobre constraints futuros diferidos aplicada.
Alcance: PostgreSQL sintético aislado y runner local explícito. Sin operación
remota, retirada Auth, scheduler, rol nuevo, migración o dependencia.

## Lo que entiendo

D-032/D-036 y PC-05/D-040 conservan30d para cuentas cerradas/agregados retirados o
borradores abandonados y90d para historia mínima. Perfil/práctica son una fila
privada; su FK users RESTRICT no permite borrar cuenta antes del agregado. El
maintenance anterior podía abortar toda la limpieza por ese FK, conservando
sesiones o historia vencidas de otras personas. No se modifica el contrato Auth.

## Decisiones tomadas

Tres fases transaccionales independientes, en una conexión owner de mantenimiento:

1. Sesiones vencidas12h/30min o de usuarios no activos; auditoría Identity y eventos
   profesionales occurred_at<=ahora-90d. Se confirma antes de tocar cuentas.
2. Agregados cuyo COALESCE(withdrawn_at,profile_updated_at)<=ahora-30d. Se bloquean
   primero users en orden UUID y después se borra/recomprueba el agregado actual;
   el orden coincide con Identity. Una edición real concurrente puede mover el
   corte mientras se espera el lock: la consulta DELETE vuelve a comprobarlo.
3. Cuentas closed<=ahora-30d, bajo lockuser y savepoint por cuenta. Sin confirmación
   Auth o con agregado restante se bloquean. Un error FK inmediato dentro del
   savepoint revierte solo el DELETE de esa cuenta y se registra dependencia,
   sin CASCADE ni elevar permisos. RESTRICT actual no es diferible.

Si faltan tablas C03 o solo existe una, la verificación de catálogo anterior a
escrituras falla cerrado. No existe modo identity_only implícito ni creación de
esquema para resolverlo. Las fixtures C02 de retención aplican el esquema C03 solo
durante esas pruebas; las otras pruebas C02 conservan sus tablas originales.

## Decisiones pendientes

El runner siempre envía retired_subjects vacío: accounts=0 aunque haya cuentas
vencidas. El set legacy permite probar contratos de borrado en la fixture; no es
prueba de retirada Auth operativa. Falta adaptador aprobado que compruebe origen,
proyecto/sujeto, operación, cierre vigente y revocación/eliminación confirmadas.
GET/user negativo, sesión ausente, UUID manual o timeout no prueban retirada.

Arturo conserva responsabilidad de retiro Auth y fallos de30/90d. Ejecutar trabajo
periódico, rol/credencial operativos, alertas, backups y restauración siguen
pendientes. No se inventa tombstone perpetuo ni archivo público de sujetos.

## Diseño propuesto e interfaz implementada

PostgresIdentityMaintenance.purge(retired_subjects=...) conserva su firma y retorna
PurgeResult ampliado con professional_drafts/professional_events,
blocked_accounts_missing_proof/blocked_accounts_dependencies y professional_schema.
En resultado exitosamente calculado, professional_schema es ready. Los conteos de
motivos pueden solaparse; blocked_accounts cuenta cada cuenta una sola vez.
retention_compliant significa únicamente que esta pasada no dejó cuentas vencidas
bloqueadas; no acredita cumplimiento jurídico, periodicidad ni terceros futuros.

El runner preview usa REPEATABLE READ READ ONLY y solo conteos. Para dependencias
predice agregados que seguirían presentes después de purgar los elegibles; un FK
desconocido o una edición concurrente puede cambiar el resultado real de apply.
Preview con código0 confirma lectura, nunca eliminación. Apply con cuentas
bloqueadas devuelve3; error devuelve2 con salida fija. Schema ausente/parcial
devuelve professional_schema_unavailable y enum absent/partial, sin filas ni valores.

Error posterior a una fase confirmada NO significa rollback total: conservar
evidencia de fallo, repetir preview y reintentar conscientemente sobre la fixture.
Un fallo inesperado no se presenta como éxito; no imprime consultas o diagnósticos.

## Datos afectados

El agregado se elimina completo; ninguna columna de nombre/área se copia a audit.
Historial90d conserva referencias lógicas privadas sin FK que provoque cascada30d.
La retirada no se reconstruye retrospectivamente a partir de closed_at para vencer
plazos; un agregado reciente puede bloquear cuenta y necesita cierre coordinado.
Lectura, no-op o reintento de retirada no mueven su fecha. No se purgan membresías,
clientes, asuntos u otras entidades que no existen en este incremento.

## Seguridad

Runner conserva confinamiento al socket Unix privado0700 de la fixture, DB exacta,
bootstrap local exacto, no TCP, owner efectivo mínimo, rechazo PG* heredadas salvo
passfile sobrescrito, sin DSN en argumentos ni dotenv. El mantenimiento aplica
password explícito/passfiledevnull/sslcertmodedisable mediante custodia existente.
Runtime no recibe DELETE/owner por implementar mantenimiento. Ninguna conexión
remota ni credencial de proveedor se usa en pruebas.

Un DELETE local no evita recuperar un backup antiguo. La activación posterior a
restore debe permanecer cerrada hasta reconciliar retiros y purgas con Auth/evidencia
privada fiable, sin reinsertar perfiles o sesiones viejos. Esta entrega no implementa
ni verifica restauración o destrucción de backups. LEGAL REVIEW REQUIRED.

## Impacto futuro

Futuros FK requieren política propia y tratamiento explícito de dependencias;
RESTRICT se conserva como última defensa. Scheduler/producción no deben reutilizar
bootstrap de fixture o retired_subjects como autorización real. Agregar evidencia
operativa o nuevas tablas exige su contrato/modelo/retención antes de migrar.
Un futuro FK diferido hasta commit puede abortar la fase3 completa (borrados de
cuentas), aunque las fases1/2 confirmadas permanecen. Esta entrega no fuerza
constraints futuros a immediate ni promete aislamiento por cuenta para esos
modelos no aprobados; un error de commit no se presenta como éxito.

## Implementación y verificación

Modificados exclusivamente PurgeResult/PostgresIdentityMaintenance en storage,
runner y pruebas de retención. Las clases de sesión no cambian. Pruebas dedicadas
cubren esquema ausente/parcial antes de escrituras, preview real READ ONLY,
30/90d±1µs, retiro reciente con creación vieja, falta de prueba, FK reciente y FK
adicional con otra cuenta purgada, edición concurrente y reintento idempotente.
Resultado ejecutado: **512 pruebas pasan** en runner global fresh de PostgreSQL
aislado, incluidas **9 pruebas nuevas coordinadas**; exit0 y limpieza del cluster
confirmada por runner. Ruff check/format pasa en los5 archivos Python afectados.
Diff revisado: storage solo PurgeResult y PostgresIdentityMaintenance, sin clases
de sesión modificadas. A4 revisó sin ejecutar PostgreSQL ni encontrar bloqueantes
del esquema actual; A0 integra/escanea. No afirmar
CI remoto, scheduler operativo, restauración o aceptación Auth real.

Fuentes oficiales consultadas2026-10-15: [FK/RESTRICT PostgreSQL17](https://www.postgresql.org/docs/17/ddl-constraints.html),
[transacciones/savepoints](https://www.postgresql.org/docs/17/tutorial-transactions.html),
[Supabase gestión de usuarios](https://supabase.com/docs/guides/auth/managing-user-data).
