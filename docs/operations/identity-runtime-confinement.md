# C02 — Confinamiento de DSN del runtime Legalia

Base común: eba6cbedb631, rama codex/identity-design. Orden A4 y separación técnica
validadas por A0; revisión independiente asignada a A2. Implementación local,
sin lectura de `.env`, conexiones remotas ni modificación de recursos/proveedores.

## Cambio y propósito

`validate_dsn` ahora confina la configuración del runtime directamente, incluso
cuando no se usa el launcher privado. Antes validaba campos básicos y usuario,
pero un host arbitrario con rol técnico podía pasar. El default acepta únicamente
PostgreSQL del proyecto Legalia `spohytnxscljtitvmdab`, con los roles técnicos
`abogalia_identity_runtime` o `abogalia_identity_probe`; rechaza roles administrativos.
No cambia los nombres ABOGALIA_*, Settings, gates de correo/Auth, permisos o retención.

| Condición remota | Resultado requerido |
|---|---|
| Host directo | db.spohytnxscljtitvmdab.supabase.co con usuario de rol base |
| Session pooler | Allowlist existente aws-0/1-us-east-1.pooler.supabase.com; usuario rol.spohytnxscljtitvmdab |
| Base/puerto | postgres y 5432; rechaza listas de hosts/puertos y 6543 |
| TLS | sslmode=verify-full explícito; no require/prefer/disable ni ausencia |
| Campos | Solo host, port, dbname, user, password, sslmode, sslrootcert, connect_timeout |
| Ambiente libpq | Rechaza presencia de cualquier PG* salvo PGPASSFILE, que storage sustituye por /dev/null |

Los hostnames de pooler conservan la allowlist del launcher; no se deriva otro
hostname desde región ni se asegura que alguno sea el endpoint efectivo. El operador
verifica el host no secreto del proveedor antes de usarlo. Si no coincide, falla y
requiere revisión del destino, no una ampliación automática. Certificado/CA y
privilegios reales se verifican en operación posterior: validar la forma del DSN
no certifica conexión, identidad de la base, grants, probe o SMTP.

Rechaza hostaddr, service, options, passfile, certificados/claves de cliente
explícitos y todo parámetro fuera del contrato. Los errores del parser se convierten
en ValueError fijo, sin contenido ni causa expuesta. `load_runtime` conserva el
error fijo existente y la construcción sin consultas; no registra valores.
Las comprobaciones ambientales iteran únicamente nombres, sin leer sus valores.

## Separación explícita de fixtures locales

Se aprobó el argumento Python-only
`validate_dsn(value, role, allow_local_fixture=True)`. No existe variable de entorno,
argumento del launcher ni llamada de main/load_runtime que active este modo.
`development` permite el Origin local aprobado, pero no elude el confinamiento de DB.

Opt-in local acepta exclusivamente cuatro campos: host, port, dbname, user. Exige
socket Unix absoluto llamado socket, padre con prefijo abogalia-identity-tests-,
ambos directorios reales sin symlink directo, propiedad del usuario actual y modo
0700; DB abogalia_storage_test, puerto no privilegiado y rol técnico base. Rechaza
password/passfile/opciones, rol owner, sufijo pooler, host remoto, otro nombre de DB,
permisos amplios y flags truthy diferentes de True. No conecta ni consulta el socket.
La fixture/runner existente prepara su cluster privado sin TCP; este validador no
provisiona ni acredita esa configuración del servidor por inspección de rutas.

Storage y pruebas Auth locales siguen usando dependencias inyectadas. La prueba
contra la fixture SQL existente reconstruye exclusivamente los cuatro campos de
configuración sintética y demuestra rechazo por default y aceptación opt-in.
No se comparte esta vía con la operación remota de la aplicación.

## Archivos y verificación

- [runtime.py](/Users/arturo/Documents/repos/abogalia/apps/api/src/abogalia_api/identity/runtime.py)
- [test_runtime.py](/Users/arturo/Documents/repos/abogalia/apps/api/tests/test_runtime.py)
- Este documento de evidencia.

Pruebas pertinentes de runtime + launcher antes de añadir la comprobación SQL:
154 passed. Ejecución posterior del runner completo contra PostgreSQL temporal
privado: **358 passed**, con transporte Auth sintético y salida redactada. Incluye
Auth/storage/retención existentes y la comprobación de ambos roles en la fixture.
Ruff lint y formato pasan en los dos archivos Python propios.

Negativos verifican proyecto retirado/ajeno, IP/loopback/host arbitrario/listas,
puerto transaction/listas, base ajena, falta/degradación TLS, hostaddr/options/service/
passfile, roles elevados/cruzados, claves/certificados explícitos y configuración
libpq heredada. La construcción positiva usa destinos públicos sintéticos sin
conectar; casos locales cubren propiedad/permisos/symlink y ausencia de activación
por environment o development. No se ha afirmado aceptación con Supabase real.

A2 confirmó revisión independiente sin bloqueantes del confinamiento. Identificó
un endurecimiento conexo: libpq puede buscar certificados/claves cliente por
defecto; el coordinador lo asignó por separado a storage (sslcertmode=disable
interno, libpq compatible). Esta entrega no lee esos archivos ni acredita una
exposición; prohibir parámetros DSN de cliente no elimina por sí solo esos defaults.
Scanner, integración,
configuración global, commits/push corresponden a A0. No se cambió `.env`, Settings,
launcher, lockfiles, migraciones, proveedor, grants o recursos remotos. C02 sigue
pendiente de sus verificaciones y condiciones operativas de SMTP/probe/retención.

Fuentes oficiales actuales consultadas:
[Supabase: conexiones PostgreSQL](https://supabase.com/docs/guides/database/connecting-to-postgres),
[libpq: parámetros y destinos](https://www.postgresql.org/docs/current/libpq-connect.html),
[libpq: TLS](https://www.postgresql.org/docs/current/libpq-ssl.html).
Supabase distingue conexión directa, session y transaction pooler; verify-full
comprueba confianza y hostname según libpq. No desactivar TLS por un fallo.
