# Revisión de Cloudflare y skills oficiales — 2026-10-16

Actualización posterior: [optimización de cuota y observabilidad preparada](legalia-cloudflare-quota-observability.md)
publicada2026-10-16; el resto de esta revisión conserva la evidencia anterior.


## Resultado y alcance

Se instalaron las 19 skills oficiales de `cloudflare/skills` en el directorio local
`~/.codex/skills`, mediante el instalador de Codex y con el commit upstream fijado
`86505e44f87d801aa1864a3c4109e9a8ae5c409f`. No se instaló un MCP ni se concedieron
permisos nuevos de cuenta. Las skills se descubren automáticamente en el próximo
turno; `workers-best-practices` y `wrangler` ya se leyeron para esta revisión.
Las fuentes de las skills permanecen fuera del repositorio de Legalia.

[Fuente oficial y método de copia para Codex](https://github.com/cloudflare/skills/tree/86505e44f87d801aa1864a3c4109e9a8ae5c409f).

Inventario: agents-sdk, basin, cf-cli, cloudflare-email-service,
cloudflare-one-migrations, cloudflare-one, cloudflare, durable-objects,
gateway-workers, k2, nextjs-on-cloudflare, sandbox-migrate-to-next, sandbox-next,
sandbox-stable, turnstile-spin, web-perf, workers-best-practices,
workers-profiling y wrangler. Instalación no implica habilitar esos servicios.

Se revisó el Worker y su configuración de producción, el aislamiento de su
herramienta local, las pruebas existentes y las rutas públicas desplegadas.
No es una auditoría completa de Supabase, Fly o negocio ni acredita C02 Done.
No se cambiaron recursos remotos, plan, scopes, datos, flags Auth ni `.env`.

## Hallazgos y acciones

| Área | Evidencia y resultado |
|---|---|
| Tipos de bindings | Corregido: `Env` se genera con Wrangler4.151.0 desde `wrangler.production.jsonc`, con tipos runtime para la fecha configurada. El export satisface `ExportedHandler<Env>`. `check:worker` verifica que el archivo generado siga vigente y compila con tsconfig exclusivo sin DOM del navegador. |
| Pruebas en runtime | Corregido: además de30 pruebas Node, nueve pruebas en workerd cubren fetch nativo/cache, streaming/header allowlist, Set-Cookie separados/Expires, redirects cerrados, Authorization presente, privacidad de ASSETS,404/405, origen denegado y cancelación. Estas pruebas detectan el contrato de fetch que la suite Node sola no podía validar. |
| Aislamiento de pruebas | Backend sintético y workerd en127.0.0.1 con puertos efímeros; HOME/config temporal, env mínimo, dotenv desactivado y env-file/devnull. Solo usa fecha/flags públicos del destino real; no copia bindings de producción. Sin acceso a proveedor, cuentas, correo o secretos. Limpieza al terminar. |
| Streaming/vida de promesas | Pasa: cuerpo request/response transmitido como stream; no buffer del contenido de usuarios ni estado mutable por petición en el módulo; operaciones esperadas mediante await. |
| Destinos y redirects | Pasa: allowlist exacta de Fly propio; no redirecciones upstream ni passThroughOnException; errores fijos y cierre ante fallo. No se amplía acceso para resolver errores. |
| Sesión y caché | Pasa en revisión y comprobación pública: no-store en API/shells privados, Authorization rechazado, headers mínimos, cookies host-only seguras y sin CORS adicional. No Cache API, KV ni caché de identidad. |
| Secretos | Pasa el escaneo redactado de fuentes/historia y artefactos. Worker solo contiene un origen público; credenciales runtime permanecen en Fly. La exclusión de formato del archivo generado no lo excluye del escáner. |
| Observabilidad | Excepción operativa: Logs/Traces desactivados por el contrato aprobado de privacidad. La skill recomienda habilitarlos; no se aplica automáticamente porque cambia captura/retención y necesita diseño de minimización. Errores saneados y verificaciones de salud existen, pero no equivalen a alertas/trazas. |
| Compatibilidad | Conservada2026-10-15, vigente al despliegue de ayer; no avance de fecha sin revisar cambios. El Worker usa APIs web, por lo que nodejs_compat no es necesario. No añadirlo solo para satisfacer una recomendación genérica. |
| Servicios/bindings | ASSETS usa binding. API externa Fly por HTTPS conforme al stack aprobado; no es Worker-to-Worker ni conexión SQL desde el Worker, por lo que service bindings/Hyperdrive no aplican. |
| Cuota Free | run_worker_first=true consume solicitudes Worker también en assets. Es válido pero no óptimo para cuota. Afinar rutas exige conservar headers, selección de HTML, fallos y privacidad antes de desplegar; se mantiene la configuración aprobada. No activación de Paid. |

## Comprobación

`pnpm check` pasa: formato/lint, tipos web, tipos generados del Worker y compilación
con runtime Cloudflare,30 pruebas Node,9 pruebas workerd y build prerenderizado.
Wrangler deploy --dry-run con destino de producción y sin credenciales pasa.
Escáner: fuentes/historia y client17archivos/bundleWorker2archivos, cero hallazgos.
La ejecución de estos checks es local; no se atribuye a CI remoto.

Lectura HTTPS del despliegue existente: `/`, `/registro`, `/api/health` y
`/api/auth/session` responden200. Registro/API conservan no-store y todos nosniff.
Sin registro, login, correo, lectura de usuarios o purga en esta revisión.
Los cambios de código de producción son exclusivamente de tipos, sin cambio del
JavaScript que ejecuta el gateway; no fue necesario otro despliegue.

Regeneración segura: `pnpm types:worker`; validación ordinaria `pnpm check:worker`.
Ambas usan el entorno limpio del runner. No se editan las declaraciones generadas
a mano y no se añade una dependencia ni cambia lockfile para estas comprobaciones.

Pendientes: diseño de observabilidad mínima/alertas, optimización medida de rutas
si la cuota lo requiere y aceptación real de correo/MFA/revocación/retención/restore.
No se afirma cumplimiento universal de buenas prácticas ni preparación jurídica.

## Fuentes consultadas

- [Workers best practices](https://developers.cloudflare.com/workers/best-practices/workers-best-practices/).
- [Tipos generados](https://developers.cloudflare.com/workers/languages/typescript/).
- [Enrutamiento Static Assets](https://developers.cloudflare.com/workers/static-assets/routing/worker-script/).
- [Facturación y límites](https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/).
- [Skills oficiales y revisión fijada](https://github.com/cloudflare/skills/tree/86505e44f87d801aa1864a3c4109e9a8ae5c409f).

Se contrastaron las recomendaciones con el schema/help instalado de Wrangler4.151.0.
El stack y las restricciones expresas de Arturo prevalecen sobre recomendaciones
que agreguen servicios, Node compatibility innecesaria o captura de información.
