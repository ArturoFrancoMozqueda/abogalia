# Abogalia

Atención legal clara y continua. Producto en construcción para clientes, abogados
independientes y despachos pequeños en México.

Monorepo propio de Abogalia. Kova permanece en otro repositorio y no aporta datos,
claves ni infraestructura de ejecución.

| Ruta | Responsabilidad |
|---|---|
| `apps/web` | React Router sobre Vite, TypeScript y páginas públicas prerenderizadas |
| `apps/api` | FastAPI y módulos de negocio futuros |
| `docs` | Producto, checkpoints, decisiones y registro de servicios |

## Desarrollo local

Requisitos: Node 24, pnpm 11.25.0 y Python 3.12. Dependencias aisladas en cada
entorno; no se necesitan credenciales de Kova ni una base remota para arrancar.

```sh
pnpm install --frozen-lockfile --ignore-scripts
make api-install PYTHON=python3.12
```

En dos terminales, desde la raíz:

```sh
make dev-api
```

```sh
make dev-web
```

Abrir http://127.0.0.1:5190. La API escucha en http://127.0.0.1:8090.
`/dev/conexion` comprueba navegador → proxy Vite → FastAPI; esa ruta y su enlace
no se incluyen en el build de producción. El endpoint `/api/health` confirma
liveness, no conexión a base ni autenticación.

El destino del proxy se puede cambiar en `apps/web/.env.local`, usando
`apps/web/.env.example` como referencia. Variables sin prefijo `VITE_` se mantienen
en el proceso de desarrollo; nunca poner claves privadas en `VITE_*`.

## Verificación

```sh
make check
```

Incluye lint, formato, integridad de dependencias Python, importación de la API,
tipos TypeScript y build con prerenderizado. CI ejecuta esos checks al recibir
pushes o pull requests; todavía no se ha publicado este cambio ni ejecutado CI
en GitHub. La prueba navegador/API se hace con servicios locales reales.

Los flujos críticos de Identity y de negocio requieren sus contratos, pruebas y
checkpoint antes de implementarse. Esta base no implementa login, roles, asuntos,
reservas, pagos ni IA.

## Artefacto web

`pnpm build` genera archivos en `apps/web/build/client`, incluida la portada HTML
prerenderizada. No se requiere un servidor Node de producción. Rutas futuras que
no se prerendericen necesitan fallback SPA y rutas `/api/*` hacia FastAPI en el
hosting elegido; esa configuración aún está pendiente.

## Servicios y decisiones

- [Documentación de producto](docs/00_README.md).
- [Primer bloque técnico](docs/checkpoints/repository-and-empty-database.md).
- [Registro de servicios](docs/operations/service-registry.md).
- [Decisiones](docs/decisions/decision-log.md).
- [Plan de desarrollo por agentes](docs/27_development_plan_agents.md).
- [Reglas obligatorias para agentes](AGENTS.md).

No guardar secretos ni información de clientes en este repositorio público.
La identidad pública Abogalia sigue sujeta a la decisión de marca documentada.
