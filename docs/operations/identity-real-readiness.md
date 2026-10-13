# C02: preflight de Identity y condiciones para verificación real

Estado: implementación local de preflight, **sin activación real**. Base común
720c1cf. Alcance de esta tanda: tres archivos propios; sin modificaciones a runtime,
proveedor, storage, migraciones, grants ni recursos externos. Aprobaciones D-031,
D-032 y D-033 cubren el contrato local; esta herramienta no amplía autorización.

## Ejecución segura por defecto

`apps/api/.venv/bin/python scripts/check_identity_readiness.py` devuelve JSON con
`status=disabled`, `real_readiness=pending` y `jwks=not_executed`. Código 0 significa
que se generó el reporte, no que Identity esté habilitado. Solo itera los nombres de
variables del proceso: no lee valores, importa runtime, carga dotenv, conecta ni
consulta al proveedor. Presencia no comprueba contenido, formato o habilitación.
La salida usa nombres fijos y booleanos; no reproduce argumentos ni excepciones.

Variables que deben inyectarse por el mecanismo autorizado, sin enviarlas por chat
ni colocarlas como argumentos, URLs o VITE_*:

| Nombre | Condición de operación real |
|---|---|
| ABOGALIA_IDENTITY_ENABLED | Habilitación explícita del runtime aprobado |
| ABOGALIA_ENVIRONMENT | Entorno declarado; excepción HTTP solo desarrollo local |
| ABOGALIA_WEB_ORIGIN | Origin exacto aprobado para cookies/CSRF |
| ABOGALIA_SUPABASE_URL | Destino Abogalia del registro de servicios |
| ABOGALIA_SUPABASE_PUBLISHABLE_KEY | Clave pública publishable del mismo proyecto; jamás service_role |
| ABOGALIA_CSRF_KEY | Material de firma inyectado en backend |
| ABOGALIA_DATABASE_DSN | PostgreSQL privado con rol abogalia_identity_runtime |
| ABOGALIA_SESSION_CIPHER_KEY | Material de cifrado de custodia inyectado en backend |
| ABOGALIA_AUTH_SESSION_CHECK_DSN | Conexión independiente con rol abogalia_identity_probe |
| ABOGALIA_AUTH_EMAIL_READY | Declaración posterior a verificar correo y plantillas reales |

El preflight no solicita credenciales ni valida sus valores. La validación de
configuración sigue siendo responsabilidad del runtime existente y su operador.

## Opt-in local de catálogos

`--inspect-local --socket /ruta/absoluta/al/socket --port 54983` inspecciona únicamente
una fixture existente `abogalia_storage_test`, mediante socket Unix, roles fijos y
conexiones sin contraseña ni passfile. No crea la fixture ni aplica migraciones.
Rechaza nombres ambientales PG* salvo PGPASSFILE, que reemplaza por /dev/null,
para evitar selección implícita de servicios, credenciales u opciones libpq; no lee
sus valores. Exige directorio socket y padre de fixture abogalia-identity-tests-*
propiedad del proceso, sin permisos de grupo/otros ni symlinks; comprueba
listen_addresses vacío antes de consultar metadatos. Dependencias: Python y psycopg
fijados del repositorio, fixture preparada por el runner existente. El script no es
un provisionador ni un ejecutor remoto. No conectarlo a bases con clientes reales.

Cada conexión inicia su propia transacción READ ONLY con statement_timeout 3s y
lock_timeout 1s. Rechaza una conexión que ya tenga transacción abierta. Consulta
solo pg_roles, pg_namespace, pg_class, pg_attribute, pg_policy, pg_proc y funciones
de privilegios; antes verifica SHOW listen_addresses (configuración no secreta). No consulta filas, conteos o valores de identity.users,
identity.app_sessions, identity.audit ni auth.sessions. No ejecuta GRANT, REVOKE,
DDL o mantenimiento. Reporta solo comprobaciones booleanas y estados fijos.

Comprueba usuario efectivo exacto, ausencia de superuser/BYPASSRLS/CREATEDB/
CREATEROLE/REPLICATION y membresía en roles elevados o propietario; USAGE en esquema esperado y ausencia de CREATE en esquemas de aplicación; columnas/tipos/propietario de las tres tablas Identity;
RLS ENABLE y FORCE; grants efectivos por tabla y columna; secuencia de audit solo
USAGE; ausencia de acceso efectivo a otras relaciones y funciones Identity.
Runtime puede actualizar únicamente sessions_revoked_at de users; probe solo lee
columnas id/user_id de auth.sessions, sin SELECT de tabla ni escritura. Soporta que
Identity y Auth estén en bases distintas: runtime exige Identity, probe exige Auth.

Las políticas se comprueban **estructuralmente**: nombres, roles, comando,
permisividad y presencia de USING/WITH CHECK. No se certifica su expresión,
constraints, índices, triggers, privilegios MAINTAIN de versiones posteriores a
PostgreSQL 16, funciones de otros esquemas ni toda la superficie administrativa.
`local_catalog_passed` no sustituye revisar migración/políticas ni las pruebas de
comportamiento, aislamiento, renovación, revocación y retención ya existentes.

## JWKS público y puerta remota cerrada

`jwks_checks` valida un documento público inyectado y requiere `enabled=True` y el
destino exacto `https://xggefantvuwpilksfdoy.supabase.co/auth/v1/.well-known/jwks.json`.
No descarga documentos, lee archivos de claves ni imprime material de claves.
Rechaza secretos/atributos privados, HS256, coordenadas inválidas, kid duplicados,
conjunto vacío o demasiado grande y algoritmo distinto de ES256. Usa PyJWT para
comprobar estructura criptográfica; RSA queda fuera del default aprobado.

Supabase documenta que las claves asimétricas públicas se publican en este endpoint;
esto no comprueba cuenta, sesión activa ni correo. [Signing Keys](https://supabase.com/docs/guides/auth/signing-keys).
PostgreSQL distingue privilegios efectivos de tabla/columna y las restricciones de
RLS; propietario y BYPASSRLS requieren atención específica. [Funciones de privilegios](https://www.postgresql.org/docs/current/functions-info.html),
[Row Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html).
Se consultó también el [changelog oficial](https://supabase.com/changelog) de fecha
2026-10-12; la eliminación anunciada de cifrados TLS antiguos no justifica desactivar
validación TLS. No se realizó ninguna petición al proyecto Abogalia en esta tanda.

## Manual de preparación por operador — propuesta, sin ejecución

D-035 aprueba piloto frontend/API locales con Supabase real y D-034 selecciona
Resend SMTP Free, sin overages automáticos. No existe dominio propio. Esta elección
no prueba remitente/buzón de ensayo, credenciales SMTP o entrega; el contrato de
correo y el responsable deben concretarlos sin pantallas de claves ni valores visibles.

La propuesta mínima para revisión de Arturo es usar PostgreSQL del proyecto
Abogalia existente para el esquema privado Identity y la comprobación independiente
Auth; no provisionar otro destino por inferencia. Antes de cualquier DDL el operador
confirma mediante catálogos propiedad y privilegios efectivos y el coordinador
revisa exactamente el alcance de cambio. Ningún error autoriza elevar roles.

- Propietario abogalia_identity_owner, sin login de aplicación; runtime separado
  abogalia_identity_runtime, sin superuser/BYPASSRLS/CREATEDB/CREATEROLE/REPLICATION
  ni membresía del propietario. La identidad operativa para migrar necesita sus
  permisos existentes comprobados; no otorgárselos como parte del diagnóstico.
- Artefacto único de esquema:
  [001_identity.sql](/Users/arturo/Documents/repos/abogalia/apps/api/migrations/001_identity.sql).
  Revisar completo con su BEGIN/COMMIT y SET LOCAL ROLE propietario. No ejecutarlo
  si existen objetos incompatibles ni convertirlo en un script que borra/recrea datos.
  El operador autorizado aplica solamente este artefacto tras aprobación operativa.
- Runtime: USAGE de identity; SELECT/INSERT users y UPDATE(sessions_revoked_at);
  CRUD app_sessions; INSERT audit y USAGE de su secuencia. RLS ENABLE/FORCE y
  políticas aprobadas, sin acceso Data API/browser ni privilegios genéricos public.
  Conservar los revokes del artefacto para Identity, sin extrapolarlos a Auth gestionado.
- Probe: rol abogalia_identity_probe independiente con USAGE auth y SELECT solo
  id/user_id de auth.sessions. Sin SELECT de tabla, escrituras, rol propietario,
  service_role ni permisos runtime. Revisar grants efectivos/heredados/PUBLIC;
  si la plataforma impide el mínimo, detener y plantear alternativa de diseño, sin
  revocar permisos de roles Supabase gestionados ni ampliar privilegios por inferencia.
- Inyectar dos conexiones desde mecanismo privado del operador, sin copiar DSN al
  chat, documentación, comandos, archivos publicados o bundles. El módulo vigente
  [runtime.py](/Users/arturo/Documents/repos/abogalia/apps/api/src/abogalia_api/identity/runtime.py)
  verifica roles/destino declarados; no se modifica en esta tanda. Su custodia y probe
  están en [storage.py](/Users/arturo/Documents/repos/abogalia/apps/api/src/abogalia_api/identity/storage.py).
- Registrar únicamente estados, conteos y checks redactados. No marcar grants ni
  migración remota confirmados con una respuesta de conector no interpretable.
  El rollback operativo debe acordarse antes de aplicar; no destruir objetos/datos
  ni revocar otros roles por iniciativa del agente.

Este manual no concede autorización para crear roles, configurar contraseñas,
aplicar la migración o cambiar grants remotos. La aprobación operativa concreta
sigue en el [checkpoint de activación](/Users/arturo/Documents/repos/abogalia/docs/checkpoints/identity-real-activation.md).

## Plan de aceptación real pendiente de autorización

1. Arturo designa cuenta y buzón exclusivamente sintéticos de Abogalia, entorno,
   Origin, alcance de operaciones y responsable de cleanup; sin publicar identificadores
   ni credenciales. Definir si registro/recuperación/correo y MFA forman parte del lote.
2. Operador confirma inyección segura, DB privada destino aprobado y conexión probe
   restringida al proyecto Abogalia. Cualquier provisión de roles/grants o migración
   remota requiere orden separada; este preflight no la autoriza.
3. Tras autorización de lectura externa, ejecutar un futuro adaptador revisado que
   compruebe JWKS público por HTTPS y catálogos con conexiones inyectadas. Esta tanda
   deja esa puerta cerrada; no hay CLI de conexión remota o lectura de DSNs secretos.
4. Tras autorización de operaciones Auth, verificar navegador→FastAPI→PostgreSQL→
   Supabase con la cuenta designada: rechazo de login inválido, login válido,
   session mínimo, flags de cookie, CSRF/Origin, renovación, logout local/global y
   rechazo tras revocación. Usar únicamente el flujo aprobado; evitar capturas,
   logs/cabeceras, URL con credenciales y almacenamiento público de sesión.
5. Si correo está dentro del alcance, verificar recepción/OTP pegado en formulario,
   confirmación y recuperación sin enumeración ni tokens en URL. La recuperación
   de factor MFA permanece cerrada. Registrar solo resultados y conteos.
6. Limpieza acordada y evidencia redactada: sesiones sintéticas revocadas, procesos
   propios detenidos, cuenta/buzón tratados por responsable según alcance aprobado.
   C02 real no se declara Done hasta estas verificaciones y revisión independiente.

## Evidencia y límites

Pruebas propias sobre fixture PostgreSQL real aislada: **44 passed**, sin fallos.
Incluye CLI local real, verificación efectiva de READ ONLY y guardas de entorno,
socket privado, TCP desactivado y argumentos malformados sin eco. Negativos de catálogos alteran copias
sintéticas de metadatos; **no** alteran grants/políticas de bases reales. La prueba
baseline y READ ONLY usan conexiones reales con ambos roles. JWKS usa claves
públicas efímeras sintéticas en memoria; ningún JWT, cuenta, correo o proveedor real.
Lint/formato se ejecutan con configuración de apps/api/pyproject.toml. No se ejecutó
CI remoto, despliegue, SMTP ni autenticación real. Scanner y revisión de integración
son responsabilidad del coordinador antes de publicar.
