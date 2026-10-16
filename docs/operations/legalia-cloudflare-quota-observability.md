# Cloudflare Free — cuota y observabilidad preparada

2026-10-16. [Checkpoint y alcance aprobado](../checkpoints/cloudflare-quota-observability.md).

## Cambios

Los configs de producción y plantilla usan `run_worker_first: ["/*", "!/assets/*"]`.
Los archivos públicos existentes de `/assets/` se sirven directamente, evitando
una invocación Worker por petición; rutas HTML, desconocidas y `/api` mantienen el
Worker. Archivos inexistentes pueden volver al Worker; no se promete bypass para
cualquier URL bajo assets. No se altera caché de API/sesiones ni fallback.
`public/_headers` aporta nosniff y no-referrer a las respuestas estáticas directas.
No caché immutable nuevo, CORS adicional, cambio de fecha, servicio o plan.

La proyección `worker/observability.ts` solo acepta tres outcomes fijos y devuelve
un objeto congelado de tres campos. No inspecciona Request/Response/Error, no
serializa desconocidos y no está conectada a un logger. Observabilidad preparada,
no activada. Los configs apagan explícitamente logs, invocation_logs, traces y
persistencia y prevén redactar queries si se revisa una activación futura.

## Comprobación operativa a demanda

```sh
apps/api/.venv/bin/python scripts/check_legalia_public.py --run
```

Hace tres GET fijos públicos, sin cookies/Authorization/identificadores/query y sin
seguir redirects. Comprueba200, HTML/health esperado, no-store privado y nosniff.
La salida solo tiene estado passed/failed y booleanos web/access/api. No imprime
URLs, cuerpos, cabeceras, excepciones o diagnósticos. Sin --run solo muestra ayuda.
No scheduler, telemetría, histórico, destinatario de alertas ni coste adicional.
Es una comprobación de disponibilidad pública, no aceptación de Auth, DB o negocio.

## Verificación local

33 pruebas Node (incluida proyección y configuración sin captura),9 workerd y
11 de enrutamiento real Static Assets: JS/CSS no invocan el Worker conservando
headers; seis shells privados sí, incluso ante archivo registro de sombra; API
mantiene precedencia frente a archivo api/health aun con navegación HTML;404/405
conservados. Fixtures sintéticos solo127.0.0.1; sin datos, claves o proveedores.
Cuatro pruebas del checker verifican destino fijo/sin credenciales, salida
saneada, cuerpo acotado y rechazo de redirects. Tipos/build/dry-run y scanner
se registran después de ejecutarse. No atribuir estos resultados a CI remoto.

## Captura pendiente

Workers Logs añade metadatos del contexto y los invocation logs incluyen URL.
Desactivar invocation_logs no demuestra ausencia de todo metadato contextual.
No activar captura hasta verificar el formato completo y resolver minimización,
retención/acceso/alertas. Cloudflare publica actualmente200000eventos/día y3d de
retención Free, con cambio de pricing anunciado para2026-12-01; esta referencia
no selecciona retención para Legalia ni habilita Paid.

Fuentes oficiales: [routing/binding](https://developers.cloudflare.com/workers/static-assets/binding/),
[headers](https://developers.cloudflare.com/workers/static-assets/headers/),
[billing](https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/),
[Workers Logs y límites actuales](https://developers.cloudflare.com/workers/observability/logs/workers-logs/).
