# Verificación de la base local

Fecha: 2026-10-12. Alcance: monorepo y comunicación HTTP local, D-030. Esta entrega
no comprueba conexión a Supabase, identidad ni capacidades de negocio.

## Recorrido comprobado

Navegador en /dev/conexion → petición GET /api/health → proxy de Vite → FastAPI
local → respuesta validada por React → estado de conexión visible.

| Frontera | Resultado y evidencia |
|---|---|
| Portada React | Navegador abrió http://127.0.0.1:5190 con título y contenido de Abogalia |
| Prerender | Build generó apps/web/build/client/index.html con contenido, description e idioma es-MX |
| Diagnóstico local | Ruta /dev/conexion presente en desarrollo; enlace y módulo ausentes del build de producción |
| React → API | Botón de comprobación mostró «Conexión con FastAPI comprobada» |
| Backend | Log de Uvicorn registró GET /api/health 200 OK |
| Fallo | Al detener únicamente la API creada para esta prueba, React mostró error de conexión y permitió reintento |
| Recuperación | Tras reiniciar la API, el mismo botón recuperó la conexión |
| Base e identidad | Pendientes: no hay credenciales cargadas ni integración implementada |

Capturas locales en output/setup, excluidas de Git: supabase-project-prepared.jpg
y local-api-connected.jpg. No contienen credenciales ni datos de clientes.

Verificación administrativa posterior: proyecto Supabase propio creado y comprobado,
D-029 Implemented. Evidencia visual en output/setup/supabase-project-created.jpg y
consultas detalladas en [registro de servicios](service-registry.md). Esto no cambia
el alcance del recorrido HTTP: la aplicación sigue sin conexión a Supabase ni Auth.

## Checks ejecutados

- pnpm check: Biome, generación de tipos, TypeScript y build React Router pasaron.
- make check-api: Ruff, formato, pip check e importación real de FastAPI pasaron.
- Dependencias Python instaladas desde requirements-dev.txt con verificación de hashes.
- Comprobación del HTML generado: contenido público prerenderizado, metadata e idioma presentes; diagnóstico excluido.
- git diff --check y exclusiones de .env, claves y artefactos comprobados.

CI contiene jobs separados de web/API con acciones fijadas por SHA y permisos
contents: read. Workflow preparado, sin commit/push ni ejecución en GitHub.
Las verificaciones locales no se presentan como CI remoto ni pruebas de carga.

## Revisión React

Componentes separados, TypeScript estricto, respuesta de API tratada inicialmente
como unknown y validada, timeout de petición, botón bloqueado durante solicitud y
errores recuperables. Sin llamadas remotas durante el prerenderizado. Idioma,
enlace para saltar al contenido, encabezados, foco visible y anuncio del estado
presentes. No hay secretos ni datos personales en componentes o respuestas.

## Operación local y límites

Frontend en 127.0.0.1:5190; API en 127.0.0.1:8090. Escuchan solo en loopback. La
recarga Python observa apps/api/src, sin recorrer dependencias ni el repo Kova.
GET /api/health informa liveness únicamente y usa Cache-Control: no-store.

Auth, modelo de permisos y negocio requieren sus checkpoints y pruebas
automatizadas de flujos críticos. No se configuraron hosting remoto, proxy de
producción, integración de GitHub en Supabase, políticas de negocio, pagos ni IA.
