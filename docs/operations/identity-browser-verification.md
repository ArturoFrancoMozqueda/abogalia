# Verificación de Identity en navegador real local

Fecha: 2026-10-12. Ejecutada por A4 con código integrado de la raíz del repositorio.
Resultado final: **13 comprobaciones pasan**, cleanup de recursos propios confirmado.
No equivale a operación de Supabase real ni a C02 Done.

## Recorrido y evidencia

Chromium headless real mediante Playwright bundled → React Router/Vite → FastAPI
por HTTP local → PostgreSQL real con PostgresSessionStore y PostgresSessionProbe.
El proveedor Auth usa HTTPX MockTransport explícito: login/JWT/logout sintéticos;
`auth.sessions` sintética vive en PostgreSQL, con rol probe de lectura limitado.
Claves de firma/cifrado/CSRF y tokens se generan en memoria para este recorrido,
no se guardan en Git ni se muestran.

| Comprobación | Resultado |
|---|---|
| Login inválido | 401 y mensaje español visible |
| Contraseña tras error | Campo queda vacío |
| Login válido | 200 por el gateway sintético |
| Cuenta | Navegación a `/cuenta`, sesión activa visible |
| Almacenamiento/ubicación | localStorage/sessionStorage vacíos; sin query ni fragmento |
| Cookie | Solo metadatos: HttpOnly, SameSite Strict, Path raíz; Secure falso en excepción HTTP local |
| Acceso JavaScript | Cookie de sesión no accesible desde JavaScript |
| Logout local | 204 desde el botón real |
| Consulta tras logout | Sesión anónima 200 |
| URLs Auth | Sin parámetros, fragmentos o marcador de contraseña |
| Consola | Sin marcador de contraseña ni nombres de tokens de proveedor |
| Persistencia SQL | Cero filas de custodia y sesiones Auth sintéticas; evento de borrado existente |
| Proveedor declarado | Un login correcto y un logout por el transporte HTTP sintético |

Las comprobaciones de cookie proyectan exclusivamente metadatos; ningún campo de
valor se accede, serializa o imprime. No se ejecutó enrolamiento/desafío MFA en
navegador, ni se capturaron pantallas, cookies, headers o cuerpos sensibles.
La excepción local no acredita flags Secure bajo HTTPS de producción.

## Harness y reproducción en este host

Archivo: [verify_identity_browser.py](../../scripts/verify_identity_browser.py).
Requiere dependencias API fijadas ya instaladas, módulos web existentes, runtime
Node/Playwright bundled de Codex para macOS arm64 y Chromium headless instalado
en la caché del host. No instala paquetes o navegadores y no pretende portabilidad.

Requiere cluster PostgreSQL local aislado previamente preparado por A0, puerto
54982, socket en la ruta temporal indicada por `/tmp/abogalia-pg-path`, owner de
pruebas y roles dedicados owner/runtime/probe existentes. El script crea únicamente
`abogalia_browser_test`; si existe previamente, falla sin sobrescribirla. Elimina
esa base al terminar; no detiene el cluster de A0. La suite general usa otro
cluster/puerto 54983 y no comparte esa base.

```sh
env -i PATH=/usr/bin:/bin LANG=C LC_ALL=C PYTHONPATH=apps/api/src \
  /Users/arturo/Documents/repos/abogalia/apps/api/.venv/bin/python \
  scripts/verify_identity_browser.py
```

El harness usa exclusivamente puertos libres 5191/8091; no toca procesos existentes
en 5190/8090. A0 autorizó cambiar origen solo en el objeto fixture sintético de
Settings: validación y defaults de producción no se modifican. Vite usa una
configuración temporal con `envDir:false`, sin `loadEnv`; entorno de subprocess
acotado. Guard de presencia de nombres `ABOGALIA_*` se evalúa antes de importar
`main` y falla cerrado; no lee sus valores ni archivos `.env`.

Uvicorn sin access logs; stdout/stderr de Vite y diagnósticos de navegador/SQL se
suprimen. Reporte acepta exactamente once claves fijas de navegador con valores
booleanos, enum de estado y exit code cero; agrega solo dos claves SQL fijas.
Nunca copia nombres de campos o diagnósticos arbitrarios a la salida pública.

Limpieza captura fallos sin traceback; detiene únicamente API/Vite propios, cierra
cliente HTTP del proveedor, elimina configuración/passfile vacío temporales y
base propia. El resultado final confirmó `owned_resources_cleaned=true` y puertos
alternos libres. No se intervino en sesiones de navegador o servicios ajenos.

## Revisión de secretos y límites

Durante revisión de este archivo fuente, Gitleaks detectó `generic-api-key` en
una expresión JavaScript del harness. Captura privada local y comparación por
booleanos confirmaron coincidencia exacta con una sentencia de código público
conocida, sin publicar Secret/Match ni fragmentos. Se reestructuró la expresión;
**nuevo scan local del script: cero hallazgos**. Sin ignore, allowlist nueva,
excepción al scanner o incorporación de la alerta como baseline. A0 ejecutará
el scan general antes de commit/publicación.

Ruff check/formato del harness pasan. No se verificó login con usuarios reales,
SMTP/OTP de proveedor, MFA real, HTTPS, hosting, CI remoto, despliegue o restore.
La tabla reporta únicamente el recorrido ejecutado; las suites unitarias y SQL
tienen evidencia separada. Tratamiento de datos reales sigue sujeto a los
checkpoints y LEGAL REVIEW REQUIRED.
