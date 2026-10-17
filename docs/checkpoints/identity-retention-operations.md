# Checkpoint — Operación de retención Identity

## Actualización C02/C03 — 2026-10-15

La implementación local coordina sesiones/auditoría, agregados profesionales30d
e historia mínima90d. La falta total o parcial del esquema C03 bloquea el ejecutor
antes de escrituras y se informa mediante un estado fijo. Limpieza de sesiones
e historia se confirma separadamente de la purga de cuentas: una dependencia de
una cuenta no conserva por rollback los tokens vencidos de otras.
Ver [diseño y evidencia actuales](../operations/legalia-coordinated-retention.md).

Esta extensión conserva el alcance sintético local. El runner no acepta evidencia
Auth ni borra cuentas vencidas: informa bloqueo y requiere al responsable. No se
ejecutó contra Supabase, no hay scheduler operativo y no se ha verificado retiro
Auth o restauración. Los apartados siguientes conservan el contrato histórico;
los conteos/estados nuevos se documentan en la evidencia enlazada. No se reabren
los plazos aprobados30/90 ni las responsabilidades asumidas por Arturo.

Fecha: 2026-10-12. Tanda 03, C02, A2/A3. Estado: implementación local sintética
autorizada por A0; operación real, eliminación de cuentas y scheduler pendientes.
Base común `720c1cf`. Revisor independiente: A0. No cambios remotos.

## Aprobación operativa vigente

Arturo aprobó los tres paquetes y parámetros recomendados (D-036). Activación en
proyecto existente, Resend SMTP Free, OTP600s/pausa60s/máximo6 mensajes de ensayo
y tratamiento documentado quedan Approved; falta ejecución/verificación. Arturo
es responsable de cierre/retiro Auth y fallos de retención. Se conservan los límites
de permisos mínimos, sin hosting nuevo ni borrado sin evidencia. Los apartados
Proposed siguientes describen preparación anterior; no reabren estas aprobaciones.
La elección del mecanismo técnico de retirada/mantenimiento no admite credenciales
amplias en runtime ni una lista de UUIDs como prueba. D-037 pide env privado y push
revisado de fuentes; nunca valores privados en Git.

## Lo que entiendo

D-032 aprueba cuenta cerrada/evidencia de membresía terminada a 30 días y auditoría
a 90 días. La sesión termina a 12 horas absolutas o 30 minutos inactiva; se eliminan
los tokens custodiados. C02 contiene users, app_sessions y audit. Membership todavía
no existe y este runner no la crea ni declara su retención implementada.

El cierre local bloquea nuevos logins. Borrar ese bloqueo antes de retirar la
identidad Auth permitiría reactivación; por ello una cuenta vencida sin confirmación
no puede borrarse. La falta de evidencia es incumplimiento pendiente, nunca permiso
para ampliar retención o conservar un tombstone perpetuo.

## Decisiones tomadas

- Preview por defecto: transacción PostgreSQL REPEATABLE READ READ ONLY, solo COUNT
  agregados, sin filas de usuario ni eventos.
- `--apply --isolated-local` explícitos: únicamente DB sintética
  `abogalia_storage_test` del cluster privado de `scripts/run_identity_tests.py`.
  No provisiona cluster, tablas ni roles. No aplica a operación real.
- Entrada inyectada `ABOGALIA_TEST_POSTGRES_DSN`: exactamente host/port/dbname/user;
  socket Unix absoluto privado 0700 del usuario local, padre privado con prefijo
  `abogalia-identity-tests-`, puerto no privilegiado, postgres/abogalia_test_owner.
  No argumento DSN, dotenv, service, password u options de entrada.
- Owner de fixture NOLOGIN preservado. Preview fija SQL `SET LOCAL ROLE` constante;
  apply deriva internamente options constante de rol owner y reutiliza
  `PostgresIdentityMaintenance.purge(retired_subjects=set())`. Nunca acepta sujetos,
  archivos, UUIDs o afirmaciones del operador como evidencia Auth.
- Verifica rol efectivo sin superuser/BYPASSRLS, owner de DB exacto y TCP desactivado.
  Passfile devnull/password vacío explícitos; rechaza presencia de otras variables
  PG sin leer sus valores para evitar configuración implícita de libpq.

## Decisiones pendientes

1. Contrato verificable de cierre/retiro Auth: actor autorizado, revocación y
   eliminación efectiva, vínculo sujeto/operación/fecha, origen y autenticidad de
   evidencia, reintentos y concurrencia. Ausencia de `auth.sessions` sola no acredita
   eliminación del usuario ni imposibilidad de nuevo login. No implementado aquí.
2. Rol de mantenimiento de operación real mínimo y LOGIN/ejecutor separado. El
   bootstrap privilegiado de fixture no es un contrato de privilegios de producción.
   Requiere aprobación y pruebas de grants/RLS, sin habilitar runtime propietario.
3. Scheduler/hosting, responsables de alertas y destino privado de evidencia.
4. Ventana de ejecución y tolerancia de demora: una ejecución diaria no garantiza
   borrado exactamente al umbral; no se aprueba un plazo adicional tácito.
5. Backups, restauraciones y derechos de datos/proveedor. LEGAL REVIEW REQUIRED.

## Diseño propuesto

Operación diaria propuesta para cuentas/audit a las 03:00 America/Mexico_City,
guardando tiempos de corte UTC; horario y scheduler pendientes. Sesiones necesitan
limpieza más frecuente propuesta cada 5 minutos, además de expiración al acceso;
no afirmar eliminación física instantánea de sesiones abandonadas ni elegir hosting.
Reintentos propuestos máximo tres, a 1/5/15 minutos para fallo transitorio; ninguna
repetición transforma ausencia de retiro Auth en prueba. Operador revisa fallo de
configuración o backlog de cuentas; no se automatiza una ampliación de permisos.
Un ejecutor a la vez; la purga es transaccional e idempotente, no hay lock distribuido
nuevo. Si una ejecución expira o falla no asumir commit; volver a preview y repetir
la operación idempotente. Toggle de aplicación por invocación explícita, no activación
persistente. No scheduler o alertas externas implementados.

Salida JSON fija: status/scope, conteos sessions/accounts/audit_events/blocked_accounts,
retention_compliant y diagnostics suppressed. Código 0 preview o apply sin cuentas
pendientes; 3 apply con cuentas bloqueadas (limpieza parcial ya confirmada); 2 fallo
sin diagnóstico crudo. Preview puede devolver 0 con incumplimiento visible: es una
lectura terminada, no éxito de borrado. Counts en preview son estimación de snapshot;
en apply son resultado real de la transacción posterior. retention_compliant proviene
del contrato de maintenance y expresa únicamente ausencia de cuentas vencidas
pendientes de retiro; no certifica cumplimiento legal/global ni backlog de membresías.

La primera operación es preview. Para aplicar se invoca con Python del entorno API
y las dos banderas; DSN solo se inyecta al proceso desde el runner local, nunca se
pega en terminal/chat. No se usa contra base de clientes. No se publica lista de
retired_subjects ni se llama Auth desde este comando.

## Datos afectados

Preview no modifica datos. Apply borra sesiones caducadas/inactivas o de cuenta no
activa y auditoría con occurred_at <= ahora-90d. Accounts permanece cero; cuentas
cerradas <= ahora-30d permanecen bloqueadas y se reportan por conteo. No cascadas
de terceros, historial jurídico, membresías o contenido legal. Política de respaldo
y retención del proveedor separadas; no se afirma destrucción en backups.

## Seguridad

SQL real/RLS real de fixture. Ningún service_role, bypass, endpoint de cierre, datos
reales, escaneo del esquema Auth real o borrado automático del proveedor. No tokens,
emails, sujetos, DSN, logs de eventos o excepciones en reportes. stderr del entrypoint
se suprime antes de conectar. Los controles de nombre/socket delimitan un sandbox
autorizado; un proceso local comprometido con bootstrap sigue siendo privilegiado.
No trasladar este mecanismo a producción. Una cuenta pendiente no detiene limpieza
de tokens de terceros ni auditoría vencida.

Supabase advierte que eliminar usuario no invalida JWT emitidos, y retirar solo el
registro de aplicación no impide Auth; requiere cierre de ventana por comprobación
de sesión para operaciones sensibles. [User management](https://supabase.com/docs/guides/auth/managing-user-data).
Preview usa modo READ ONLY real [PostgreSQL16 SET TRANSACTION](https://www.postgresql.org/docs/16/sql-set-transaction.html);
los defaults libpq incluyen variables de conexión [PostgreSQL16 environment](https://www.postgresql.org/docs/16/libpq-envars.html).
Fuentes y changelog oficial consultados el 2026-10-12. Índice Markdown no accesible
por herramienta; se consultó [changelog HTML](https://supabase.com/changelog).

## Impacto futuro

El cierre completo necesita retiro Auth autenticado y verificación operativa antes
de autorizar borrar la cuenta. Un bool del cliente, un archivo público de UUIDs o un
correo no sustituye prueba. Runtime/grants existentes no se amplían; futuro rol
dedicado y scheduler requieren coordinación. Membership C03 y retención jurídica
necesitan modelos y operación propios. C02 no se marca Done con este runner.

## Implementación propuesta

Archivos: scripts/run_identity_retention.py y
apps/api/tests/test_identity_retention_runner.py. Sin cambios a storage, migraciones,
UI, dependencias o configuración global. Pruebas de argumentos/destinos/env rechazados,
salida redactada, COUNT bajo READ ONLY y rol owner efectivo, bordes 30/90d/30min,
preview sin escrituras, apply parcial conservando cuentas e idempotencia. PostgreSQL
local real con datos sintéticos; Auth no se invoca ni simula como prueba de retiro.
Resultado ejecutado: **177 pruebas pasan** en suite fresh de PostgreSQL aislado,
incluidas **21 pruebas nuevas de retención**. Lint y formato pasan en los dos archivos
Python. El test observador de READ ONLY se retira antes de verificar totales con
admin; no altera el criterio de preview. Scanner y revisión independiente quedan
a cargo de A0 antes de integrar. CI remoto y operación real pendientes.
