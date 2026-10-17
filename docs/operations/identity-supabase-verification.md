# C02 — Esquema privado Supabase aplicado

Operación autorizada D-036. Proyecto confirmado antes de aplicar:
`xggefantvuwpilksfdoy`, organización `jdmkzzkgnzwldthjqtgx`, abogalia,
ACTIVE_HEALTHY; PostgreSQL 17.11. Sin acceso a datos de clientes o secretos.

## Artefacto y atomicidad

El coordinador aplicó mediante el conector `apply_migration`, nombre
`identity_owner_runtime_private_schema`, una única transacción con los cuerpos
públicos de 002_identity_roles.sql y 001_identity.sql (sin BEGIN/COMMIT internos).
La receta, revisada independientemente y probada bajo operador NOSUPER/CREATEROLE,
concede SET al owner NUEVO y CREATE de base a ese owner solo durante instalación;
RESET ROLE y revoca ambos antes de COMMIT. No modifica roles administrados de Auth,
contraseñas, clientes, Data API o hosting. No es `supabase db push` ni despliegue.

PostgreSQL conserva ADMIN automático del creador sobre sus roles nuevos; no se
alteraron grantors administrados para eliminarlo. La comprobación efectiva confirma
SET=false, herencia=false y CREATE DB=false al terminar. Runtime no recibe DDL,
propiedad, superuser/BYPASSRLS o membresías elevadas. Propietario NOLOGIN.

## Verificación remota por catálogos

| Control | Resultado |
|---|---|
| Tablas users/app_sessions/audit privadas, owner correcto y RLS ENABLE/FORCE | 3 |
| Runtime LOGIN mínimo / owner NOLOGIN mínimo | Ambos true |
| Operador puede SET/heredar owner tras instalación | Ambos false |
| Owner conserva CREATE en base | false |
| Runtime actualiza state / cutoff de revocación | false / true |
| Runtime lee / inserta auditoría | false / true |
| anon/authenticated usan esquema identity | Ambos false |
| Probe existente | false |

No se leyeron filas, emails, sesiones o contenido de auditoría. No se configuraron
contraseñas de roles ni conexiones del frontend/API. Estas comprobaciones no prueban
login, aislamiento con usuarios reales, SMTP, restauración o ejecución de retención.

## Probe diferido por capacidad de plataforma

003_identity_probe.sql queda sin aplicar. Catálogo comprobó que postgres tiene
SELECT WITH GRANT OPTION solo sobre id/user_id de auth.sessions, pero no USAGE WITH
GRANT OPTION sobre auth; PUBLIC tampoco tiene USAGE. El owner del esquema es
supabase_admin y el operador no puede SET ese rol. La operación necesita un grantor
legítimo de USAGE, sin agregar membresía a roles administrados o usar service_role.
El script falla antes de crear el rol si esa capacidad no existe. No reducir la
comprobación de revocación para abrir acceso mientras falta esa conexión.

## Advisors y límites

Advisors de seguridad devolvió dos WARN de EXECUTE a anon/authenticated sobre una
función SECURITY DEFINER. Se consultaron exclusivamente metadatos: función previa
public.rls_auto_enable, owner postgres, retorno event_trigger. C02 no creó funciones
ni se modificó ese trigger o sus ACL por inferencia. Son avisos pendientes de revisión
del control previo de RLS; no afirmar proyecto libre de avisos.
[Anon](https://supabase.com/docs/guides/database/database-linter?lint=0028_anon_security_definer_function_executable),
[Authenticated](https://supabase.com/docs/guides/database/database-linter?lint=0029_authenticated_security_definer_function_executable).

No SMTP/Auth settings, usuarios, envíos, scheduler, claves privadas o recursos Kova
modificados. La credencial publishable pública se pudo obtener del método dedicado
que devuelve solo claves públicas; no se imprimió, publicó o confundió con secretos.
El .env local se creó con variables vacías y 0600; permanece excluido y no fue leído
por agentes. Configuración privada y ensayo real siguen en el mecanismo del operador.
