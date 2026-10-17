# Tanda 02 — Implementación local de Identity

Fecha: 2026-10-12. Coordinador A0. D-031/D-032/D-033 Approved.
T05–T07 entregados como contratos técnicos; revisados por A0 para implementación.
Retención: 30 días de cuenta cerrada/evidencia de membresía terminada y 90 días de
auditoría. No retención jurídica ni verificación profesional por inferencia.

## Orden y responsabilidades

Antes de repartir código: C01 con Gitleaks 8.30.1 comprobado contra checksum oficial,
wrapper sin salida cruda y revisión independiente A2. Diez pruebas de wrapper,
self-test real positivo/negativo y scan de archivos permitidos/historial pasaron;
artefacto inicial web revisado. Se corrigieron symlinks antecesores, archivos
sensibles versionados y excepción exacta del ejemplo público web.

Baseline incluye fundación y diseños locales mediante inventario explícito;
sin `git add .`, sin archivos de runtime, sin push. Cada implementación se asignará
a un worktree desde ese commit y con archivos exclusivos. A0 conserva dependencias,
lockfiles, workflow y referencias comunes. Ningún agente elige proveedores/gasto.

| Autor | Trabajo | Archivos exclusivos | Revisor |
|---|---|---|---|
| A4 | Gateway Supabase, JWT, CSRF, sesión y HTTP | Módulo identity excepto storage, ruta Auth, main y tests Auth | A0/A2 |
| A3 | Almacén PostgreSQL y migración local mínima | storage, migración Identity, pruebas de datos y diccionario físico | A0/A4 |
| A5 | Rutas españolas y cliente API | Nuevas rutas/componentes Auth, cliente TS, rutas y estilos Auth | A0/A2 |
| A0 | Integración, runtime sintético, dependencias, C01 y checks | Configuración global y evidencia | A2 |

Alcance actual C02: acceso/sesión y controles técnicos; futuras entidades C03–C19
siguen separadas. No crear cliente global o tablas de servicio. Profesional sin
habilitación aprobada no recibe permisos por metadata ni nivel MFA.

## Entorno y límites

PostgreSQL local en cluster temporal aislado y socket privado; datos sintéticos,
roles owner/runtime separados. No leer claves existentes ni usar base de clientes.
SDK/HTTP Auth real implementado, pruebas de proveedor usan transporte simulado
declarado; jamás equivalen a prueba del proyecto Supabase o de MFA real.

La configuración se inyecta en runtime y no se imprime. Sin credenciales/plantillas
de correo aprobadas, dependencias incompletas devuelven 503; no anunciar envío o
revocación del proveedor exitosa por simulación. Restricción de consulta de sesiones
Auth necesita contrato mínimo y verificación antes de operación remota. No aplicar
migraciones/grants remotos. Recuperación/desinscripción MFA permanece cerrada.

Los endpoints siguen [T05](../contracts/identity-api.md); frontend sigue
[T06](../ux/identity-flows.md); aceptación sigue [T07](../testing/identity-acceptance.md).
No se declara C02 Done hasta recorrer integración, negativos y proveedor configurado
y documentar claramente los límites. Hosting, SMTP, legal y release siguen pendientes.

## Integración y revisión ejecutadas

A0 integró archivos exclusivos de los tres worktrees; conservó configuración,
contratos compartidos, dependencias y locks. A3 revisó seguridad del gateway; A5
revisó escenarios negativos del backend; A4 revisó almacenamiento y migración.
Las revisiones corrigieron normalización excesiva de errores de registro, purga
tras rechazo de renovación, comprobación de revocación al devolver MFA, contrato
OpenAPI, eliminación del digest rotado, cierre global desde cookie revocada y
rollback de renovación al fallar una acción. Ninguna corrección amplió permisos.

| Comprobación | Resultado | Alcance |
|---|---|---|
| API Auth/JWT/CSRF | 73 pruebas pasan | Transporte Supabase sintético; firma JWT real con claves efímeras |
| Almacén, roles/RLS y retención | 16 pruebas pasan | PostgreSQL local real aislado |
| HTTP con custodia y probe SQL | 8 pruebas pasan | PostgreSQL real; proveedor Auth simulado |
| Runtime y aislamiento de configuración | 29 pruebas pasan | Sin conexión remota; errores y valores redactados |
| Runner de PostgreSQL | 12 negativos pasan | Cleanup, timeouts, errores y entorno cerrado |
| Scanner redactado | 10 pruebas pasan y self-test positivo/negativo real | Gitleaks 8.30.1; no salida cruda |
| Navegador real local | 13 comprobaciones pasan | Chromium → Vite → API → PostgreSQL; Auth sintético |
| `make check` | Pasa | Ruff/formato, dependencias, importación, Biome, tipos y build |
| Scanner código/historial/build | Sin hallazgos | Inventario permitido; no certificación absoluta |

Los ocho recorridos SQL prueban cifrado y eliminación en logout normal/fallo
parcial, cookie revocada que no cierra otra sesión válida, rechazo de renovación
que confirma borrado, renovación seguida de 403/401 que conserva el nuevo par
sin extender actividad, rotación MFA y revocación después de rotar que elimina
la fila actual. Nunca aceptan un almacén en memoria como evidencia de persistencia.
La ejecución fresca final de API reportó 126 aprobadas, incluyendo 29 de runtime,
y eliminó su cluster al terminar. Los 22 tests stdlib del scanner/runner también
pasan. Revisión independiente A2 aprobó entrega local tras comprobar las
correcciones; no constituye aval de proveedor, CI remoto o despliegue.

El runtime exige activación explícita y nombres de configuración documentados en
README. Sin configuración permanece cerrado. No carga dotenv; impide roles de
conexión arbitrarios o archivos de contraseña implícitos. La clave de cifrado,
CSRF y DSN privados se inyectan y no se imprimen. Probe usa otro rol y consulta
únicamente existencia de sesión/usuario Auth. Los grants remotos y su verificación
están pendientes y no se ejecutan desde esta migración.

Cuentas cerradas solo se eliminan al vencer 30 días y existir confirmación de
retirada de Auth; una retirada pendiente produce un resultado explícito de
retención incumplida, sin frenar purga de sesiones caducadas o auditoría de 90 días.
Faltan programar el job y el flujo de cierre/retirada; no hay tablas de membresía
ni contenido jurídico en esta tanda. C02 permanece en integración local.

Los worktrees de backend, datos y web se archivaron mediante el mecanismo de la
app después de integrar y escanear sus cambios. Sus snapshots son recuperables;
no se descartó trabajo ajeno ni se publicaron cambios. Las verificaciones finales
se ejecutaron en el checkout coordinador de `codex/identity-design`.

[Recorrido de navegador y limpieza](identity-browser-verification.md): login
inválido/válido, campo privado vaciado, navegación y sesión, cookie HttpOnly,
URLs/almacenamiento/consola limpios y logout con eliminación persistida. Trece
comprobaciones pasan. Se usaron puertos alternos y no se tocaron servicios ya
abiertos. El hallazgo de scanner en el harness se clasificó como sentencia de
código pública mediante comparación privada; se reestructuró sin ignores y el
escaneo general posterior volvió a cero hallazgos.

Al cerrar la tanda se detuvo el cluster PostgreSQL temporal de A0 y se eliminaron
sus datos sintéticos. API/Vite de verificación también terminaron; los servicios
preexistentes quedaron intactos. El escaneo final cubrió 115 fuentes permitidas,
historial y 14 archivos del artefacto web, sin hallazgos. Sin push, despliegue,
migración/grants remotos, acceso a clientes reales o lectura de secretos.
