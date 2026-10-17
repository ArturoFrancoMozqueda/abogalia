# Desarrollo seguro y baseline — T04

Fecha: 2026-10-12. Estado: Proposed. Capacidad C01. Preparado por coordinación;
revisión independiente A2 pendiente. No se modificó el workflow ni se instaló scanner.

Actualización de ejecución D-033: controles C01 implementados en scripts/check_secrets.py,
scripts/install_gitleaks.py y checks.yml; revisión independiente A2 sin bloqueantes
tras corregir confinamiento, rutas sensibles versionadas y ejemplo público exacto.
Diez pruebas de wrapper y self-test real positivo/negativo pasaron. Scan redactado
de inventario permitido, historial y artefacto inicial web sin hallazgos. El binario
8.30.1 se comprobó contra checksum oficial. CI remoto aún no ejecutado. Las secciones
siguientes conservan la propuesta original; la evidencia actual está en la tanda 02.

## Estado comprobado

`.github/workflows/checks.yml` limita permisos a `contents: read`, fija acciones
por SHA y separa web/API. No contiene un job de scanner. `gitleaks` no está
disponible en PATH. Los cambios locales de fundación todavía no tienen commit;
la rama de diseño no equivale a un baseline publicable.

## Propuesta de controles

Antes de commit, seleccionar archivos explícitos, excluir archivos sensibles y
revisar cambios con un proceso que entregue solo ruta, línea y regla. El reporte
público nunca incluye Match, Secret, fragmentos de línea ni valores. Escanear
también historial y artefactos antes de publicar; conservar fuera de Git cualquier
evidencia privada. No aceptar un baseline de hallazgos como forma de ignorarlos.

Gitleaks v8.30.1 es candidato fijado; el release y su documentación permiten
comprobar `git`, `dir` y `--redact=100`. Antes de instalar, verificar asset para
plataforma y checksum desde fuente oficial, revisar `--help` y validar la salida
con marcadores sintéticos. Versión candidata verificada; binario y checksum aún
no verificados. Nunca usar verbose, trace ni diagnósticos en un scan real.
[Release](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1),
[referencia de esa versión](https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md).

El wrapper deberá capturar stdout/stderr sin volcarlos ante errores y mostrar solo
estado y hallazgos sanitizados. Una falla del scanner falla el check. Validar que
ningún marcador aparezca en consola, reportes o archivos publicados, incluidos
los errores de ejecución. Escanear exclusivamente un inventario permitido y los
artefactos relevantes; no recorrer `.env`, almacenes de credenciales o datos privados.

## Diff propuesto de CI

El siguiente esquema es una especificación para implementación posterior, no YAML
listo para ejecutar. Se mantienen los jobs actuales y sus SHAs.

```diff
 jobs:
+  secret-scan:
+    permissions: contents: read
+    checkout: SHA revisado existente; historial completo
+    install: Gitleaks 8.30.1; asset y SHA256 revisados
+    self-test: marcadores sintéticos y fallos del wrapper
+    scan: historial y archivos permitidos; redacción completa
+    output: solo estado, ruta, línea y regla; sin reporte crudo
```

No pasar secretos de despliegue a estos jobs ni usar `pull_request_target` para
ejecutar código de una PR. Revisar acciones y permisos también en cambios futuros;
el masking del runner no asegura redacción de todos los formatos. Comprobar logs
usando únicamente marcadores sintéticos.
[GitHub: secure use](https://docs.github.com/en/actions/reference/security/secure-use).

## Verificación requerida y límites

Aceptación C01: scan redactado de archivos, historial y artefactos; prueba positiva
con marcador detectable, negativa sin marcador y error de herramienta que falle
cerrado; revisión independiente; referencia Git común con archivos explícitos.
No certificar ausencia absoluta de secretos. Ante hallazgo, detener publicación
y reportar solo ubicación/nombre lógico; coordinar respuesta con el responsable.

En esta tanda solo se revisaron configuración y documentación. Scan, self-test,
checks de aplicación, CI remoto y revisión de artefactos no se ejecutaron como
parte de T04. La evidencia previa de fundación sigue en su informe correspondiente.
No se comprobaron funciones de protección habilitadas en GitHub.
