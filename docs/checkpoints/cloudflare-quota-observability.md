# Checkpoint — Cuota Cloudflare Free y preparación de observabilidad

2026-10-16. Arturo pidió expresamente optimizar cuota conservando Free y preparar
observabilidad sin secretos ni datos de usuarios. Approved para ese alcance;
la captura/persistencia nueva de logs, trazas o datos sigue sin activarse.

## Lo que entiendo

Reducir invocaciones innecesarias del Worker sin cambiar autenticación, respuestas
privadas, fallback, proveedor o presupuesto. Preparar diagnóstico mínimo útil.

## Decisiones tomadas

Conservar Worker-first excepto `/assets/*`, namespace de archivos públicos del
build. Mantener cabeceras de seguridad mediante `_headers` en esa ruta. API y
shells privados siguen por el Worker, sin caché y sin cambios en cookies/CSRF.
No costo extra, recurso nuevo, monitor programado o permisos adicionales.
Preparar una proyección estricta de eventos y una comprobación explícita de salud.
La preparación no recoge ni envía eventos, ni incluye logging por petición.

## Decisiones pendientes

Activación de observabilidad persistida, metadatos automáticos del proveedor,
retención/alertas y responsables de esos avisos. No se elige un plazo por inferencia.
Cloudflare documenta actualmente3d en Free; eso es referencia del proveedor y no
una aprobación para captar datos. No añadir una integración con terceros.

## Diseño propuesto

run_worker_first=["/*", "!/assets/*"]. Archivos existentes de assets se sirven
sin ejecutar el Worker; un archivo ausente puede volver al Worker y consumir cuota.
No se cambia html_handling/not_found_handling y no se permite fallback SPA en API.
Proyección futura: schema_version=1, component=web_gateway y outcome tomado solo de
backend_unavailable/upstream_redirect_blocked/origin_configuration_invalid.
No URLs, query, request ID, UID, tenant, email, IP, UA, cuerpos, headers, errores,
tiempos precisos, tokens ni cookies. Desconocidos se rechazan sin serializarlos.
La proyección no se conecta a console, logger, servicio o almacenamiento.

## Datos afectados

Solo configuración y archivos públicos del build. Salud usa tres GET fijos de web,
registro y API; salida de disponibilidad por componente y cumplimiento de headers.
No se crean cuentas, emiten correos, consultan usuarios o modifican datos privados.
Sin nuevos datos persistidos ni retención o tabla.

## Seguridad

Logs/traces/persistencia/invocation_logs explícitamente false, query redactada como
defensa futura. Captura automática puede adjuntar contexto aun con mensaje mínimo;
no afirmar anonimización del proveedor. La API conserva allowlist/CSRF/cookies/
TLS/no-store. Reglas negativas no incluyen rutas de API o páginas privadas.
Pruebas locales demuestran bypass de JS/CSS y precedencia del Worker ante archivos
que intenten sombrear API/registro. Fixture tiene marcador exclusivo de pruebas.

## Impacto futuro

La cuota se ahorra por cada JS/CSS servido directamente, no se promete una cantidad
de visitantes ni un porcentaje de tráfico no medido. Archivos de usuario/documentos
privados nunca se pondrán bajo el namespace público `/assets/`.
Antes de activar captura: verificar esquema final del evento del proveedor,
minimización real, retención y acceso; después decidir persistencia/alertas.

## Implementación propuesta

Actualizar ambos Wrangler configs, añadir `_headers`, conservar tipos generados,
ampliar pruebas workerd al router real de assets. Crear constructor puro de eventos
con pruebas de rechazo y checker de salud a demanda sin cookies ni redirects.
Validar build, dry-run y escaneo redactado antes de desplegar solo el Worker propio.
Registrar evidencia de ejecución real por separado; este checkpoint no la presume.
