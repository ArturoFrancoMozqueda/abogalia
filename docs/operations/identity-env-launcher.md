# Launcher privado de Identity — piloto local C02

Base común: 98dd4fa. Alcance aprobado: piloto local con Supabase Abogalia real,
operación por Arturo y carga privada de configuración únicamente en runtime.
Este artefacto no provisiona roles, aplica migraciones, modifica Auth/SMTP ni opera
cuentas. Implementación: [dev_identity_api.py](/Users/arturo/Documents/repos/abogalia/scripts/dev_identity_api.py).

## Uso por el operador

Desde la raíz, ejecutar `apps/api/.venv/bin/python scripts/dev_identity_api.py`.
El launcher toma únicamente `.env` de la raíz conocida; no acepta argumentos ni
rutas alternativas por CLI. No se coloca ningún valor privado en el comando.
El archivo lo crea/edita el responsable autorizado fuera del chat; el agente no
lo lee ni verifica contenido real. Debe quedar excluido de Git, regular, propietario
del usuario actual, permiso exactamente 0600 y un solo enlace. Se rechazan symlinks,
directorios, FIFO, permisos distintos y archivos mayores de 32 KiB.

Archivo ausente, vacío o campos vacíos mantiene Identity deshabilitado; health y
estado de sesión siguen disponibles. Variables ABOGALIA_* heredadas no pueden
habilitarlo por accidente. Configuración explícitamente habilitada pero incompleta
o inválida detiene el arranque con estado fijo `launcher_unavailable` y código 2.
No confundir API local ejecutándose con C02 real verificado.

Servidor fijo `127.0.0.1:8090`; web/Origin fijo `http://127.0.0.1:5190`. Sin reload,
subprocesos de shell o múltiples workers; no toma otros puertos ni detiene procesos
existentes. Si el puerto está ocupado, falla con error redactado. Durante ejecución
no imprime logs; al cerrar informa `stopped`. Ese estado no acredita readiness,
correo, conexión DB ni éxito de Auth. Ctrl+C termina el proceso propio.

## Gramática y variables

Sin dependencia nueva: python-dotenv no estaba instalado, comprobado únicamente
mediante metadata. Parser stdlib restringido, **no compatible con todo dotenv**:
una asignación `NAME=value` por línea; líneas vacías y comentarios completos
permitidos. Divide en el primer `=`, conserva espacios internos (incluidos los DSN),
recorta espacios exteriores y omite valores vacíos. No admite quotes exteriores,
multilínea, export, duplicados, CRLF, controles/NUL ni expansión. Comentarios inline
no se interpretan: formarían parte literal del valor. No ejecutar `source .env`.
Rechaza metacaracteres de shell `$`, backtick, `;`, `|`, `&`, `<` y `>`; nunca ejecuta
su contenido aunque una cadena pase validación. Para valores que requieren sintaxis
no admitida, detener y acordar extensión del contrato; no cambiar el parser por
shell, eval o interpolación. En URI PostgreSQL se pueden percent-encode caracteres
reservados según documentación del proveedor, sin mostrar su valor.

Allowlist exacta; cualquier otro nombre falla, incluso vacío:

- ABOGALIA_IDENTITY_ENABLED
- ABOGALIA_ENVIRONMENT
- ABOGALIA_WEB_ORIGIN
- ABOGALIA_SUPABASE_URL
- ABOGALIA_SUPABASE_PUBLISHABLE_KEY
- ABOGALIA_CSRF_KEY
- ABOGALIA_DATABASE_DSN
- ABOGALIA_SESSION_CIPHER_KEY
- ABOGALIA_AUTH_SESSION_CHECK_DSN
- ABOGALIA_AUTH_EMAIL_READY

IDENTITY_ENABLED y AUTH_EMAIL_READY aceptan 0/1 o ausencia. Habilitación exige todos
los restantes nombres con valor y ENVIRONMENT=development; EMAIL_READY no se exige
para importar el runtime, pero debe seguir 0 hasta verificar entrega OTP real.
No incluir SMTP, admin/migración, tokens de sesiones o datos de cuentas en este
archivo de runtime API. Esos mecanismos conservan sus responsables y contratos.

## Validación y confinamiento

URL Auth exacta `https://xggefantvuwpilksfdoy.supabase.co`; ningún otro proyecto,
localhost alternativo o fallback a Kova. Usa los validadores existentes Settings,
validate_dsn y Fernet; exige publishable, firma CSRF y clave de cifrado de formato
aprobado, sin imprimirlos. No agrega ni modifica dependencias, runtime/main o locks.

DSNs de runtime/probe separados con sus roles mínimos: base postgres, port 5432,
sslmode=verify-full. Directo exige `db.xggefantvuwpilksfdoy.supabase.co` y usuario de
rol sin sufijo. Session pooler requiere usuario `rol.xggefantvuwpilksfdoy`; allowlist
preparada únicamente para `aws-0-us-east-1.pooler.supabase.com` y
`aws-1-us-east-1.pooler.supabase.com`. **No se verificó cuál corresponde al proyecto**:
el operador debe confirmar el hostname no secreto proporcionado por Supabase,
sin componerlo por región. Si es distinto, detener y revisar allowlist. No se acepta
puerto 6543/transaction pooling hasta verificación específica de storage.

DSN permite solo host/port/dbname/user/password/sslmode/sslrootcert/connect_timeout;
rechaza hostaddr, service, options, passfile y parámetros no revisados. Retira todos
los nombres PG* heredados y fija PGPASSFILE=/dev/null antes de importar backend;
las credenciales solo proceden del archivo privado validado. No usa roles admin,
service_role ni bypass RLS para evitar un error.

verify-full comprueba cadena y hostname; el operador debe preparar la confianza CA
adecuada. `sslrootcert=system` depende del libpq efectivo y confianza disponible;
no se ha probado contra el proyecto. Si no es compatible, proporcionar raíz pública
validada por mecanismo local del operador, sin que el agente lea archivos de claves.
No degradar TLS a require/prefer ni desactivar validación por un fallo.
[SSL de PostgreSQL](https://www.postgresql.org/docs/current/libpq-ssl.html).

## Salidas y fronteras

No imprime archivo, variables/valores, rutas de error, excepciones, cabeceras o
cuerpos. Desactiva logging y Uvicorn access logs; redirige stdout/stderr Python y
los descriptores nativos 1/2 a /dev/null durante parse/import/serve, restaurándolos
al terminar. Solo tres estados JSON: stopped, launcher_unavailable,
invalid_arguments. Los argumentos desconocidos no se reproducen. Un app global
previamente importado se rechaza para no reutilizar configuración anterior.

Esta protección cubre el proceso del launcher. No controla paneles, diagnósticos
externos, gestores, volcados de memoria, herramientas del operador o un servidor
arrancado por otro comando. Revisión de secretos e integración siguen a cargo del
coordinador. No arrancar servicios reales para probar este archivo sin la orden
operativa vigente y las demás condiciones de aceptación.

## Evidencia y operación pendiente

**55 pruebas pasan**, con archivos temporales sintéticos solamente. Cubren parser,
permisos/propiedad, symlink/hardlink/FIFO/tamaño/encoding, shell literal, nombres,
configuración/destinos/roles/TLS, aislamiento de entorno heredado, logs y escrituras
FD nativas, app global cacheado y parámetros Uvicorn. Una prueba importa la API real
con archivo temporal vacío y verifica health y sesión anónima usando transporte
ASGI en proceso; no abre puertos ni conecta al proveedor. Arranque del servidor se
simula en las demás pruebas. Ruff lint/formato pasan. Una ejecución global local
de esta tanda registró 251 passed y 6 failed, todos los fallos en el módulo nuevo
test_identity_role_bootstrap.py de otro responsable; no se modifica en esta entrega
ni se afirma que la suite integrada esté aprobada. Los 55 del launcher también
pasaron dentro de esa ejecución; coordinación recibió los nombres de los fallos.

No se leyó, creó o ejecutó contra `.env` real; no se ejecutó SMTP/Auth/DB remoto,
CI, commit, push o despliegue en esta entrega. El límite de probe/grants Auth informado
por coordinación queda pendiente de resolver por el operador con sus permisos
existentes; no se agregan memberships de roles gestionados ni se amplían privilegios.
Launcher listo no equivale a runtime real listo.

Fuentes públicas consultadas: [os.open de Python 3.12](https://docs.python.org/3.12/library/os.html#os.open),
[Uvicorn settings oficial](https://github.com/Kludex/uvicorn/blob/main/docs/settings.md),
[conexiones PostgreSQL Supabase](https://supabase.com/docs/guides/database/connecting-to-postgres),
[changelog Supabase](https://supabase.com/changelog). Supabase diferencia directo,
session y transaction pooler; esta implementación usa únicamente el primero o
session, con host confirmado por operador. La carga privada es una implementación
local, no una nueva API o garantía del proveedor.
