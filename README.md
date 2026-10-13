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

La API usa el launcher privado: lee `.env` únicamente dentro del proceso de runtime,
con permisos 0600 y sin logs de configuración. El coordinador creó ese archivo con
variables vacías y exclusión de Git. La plantilla pública [.env.example](.env.example)
contiene solo nombres; no copiar valores privados a ella. El archivo vacío conserva
Auth deshabilitado. No sobrescribir un `.env` existente. Formato restringido
`NAME=valor`, sin expansión de shell ni valores entre comillas/multilínea;
[contrato del launcher](docs/operations/identity-env-launcher.md).
El launcher ejecuta un único proceso y no usa autoreload; reiniciar conscientemente
tras editar código o configuración, respetando servicios existentes.

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

Identity cuenta con implementación local de acceso, recuperación, MFA TOTP y
sesiones custodiadas por API, conforme al checkpoint aprobado. La operación con
Supabase y correo reales sigue pendiente de configuración y verificación. Roles,
contextos profesionales, asuntos, reservas, pagos e IA no están implementados.

`make test-api` ejecuta pruebas contra un PostgreSQL temporal aislado (requiere
`initdb` y `pg_ctl`). Usa datos sintéticos y un transporte Auth simulado; nunca
conecta a una base remota. La salida omite diagnósticos crudos.
Consultar [evidencia de integración](docs/operations/identity-implementation-batch-02.md).

## Configuración de Identity

Por defecto Identity queda deshabilitada y los intentos de acceso reciben 503.
La configuración se inyecta mediante un gestor de secretos o un mecanismo local
excluido de Git; la API no carga archivos dotenv ni imprime sus valores.

| Variable | Uso |
|---|---|
| `ABOGALIA_IDENTITY_ENABLED` | Activación explícita con `1` |
| `ABOGALIA_ENVIRONMENT` | `development` permite únicamente origen local aprobado |
| `ABOGALIA_WEB_ORIGIN` | Origen exacto; HTTPS en producción |
| `ABOGALIA_SUPABASE_URL` | Destino Abogalia del registro de servicios |
| `ABOGALIA_SUPABASE_PUBLISHABLE_KEY` | Clave pública publishable |
| `ABOGALIA_CSRF_KEY` | Material privado de firma, al menos 32 bytes |
| `ABOGALIA_DATABASE_DSN` | PostgreSQL propio, rol Identity runtime mínimo |
| `ABOGALIA_SESSION_CIPHER_KEY` | Clave Fernet privada para credenciales almacenadas |
| `ABOGALIA_AUTH_SESSION_CHECK_DSN` | Consulta limitada de sesiones Auth, rol probe separado |
| `ABOGALIA_AUTH_EMAIL_READY` | `1` solo tras verificar entrega y plantillas OTP |

El cierre operativo de C02 se prepara en el
[checkpoint de activación real](docs/checkpoints/identity-real-activation.md).
Arturo eligió Resend SMTP Free y frontend local con Supabase real. Todavía no hay
dominio ni envío configurado; el ensayo sin dominio está limitado al buzón de la
cuenta Resend y requiere verificarlo. `scripts/check_identity_readiness.py` imprime
solo presencia de nombres por defecto; no acredita valores válidos ni conexiones.
`scripts/run_identity_retention.py` hace preview por defecto y solo permite apply
expreso dentro de la base sintética privada de pruebas; no opera cuentas reales.

No colocar valores privados en comandos, URLs, variables `VITE_*` o documentación.
La consulta de sesiones Auth requiere una conexión explícita con permisos mínimos;
no usar `service_role`. Antes de habilitar operación real faltan validar correo OTP,
JWT de 15 minutos, roles/grants y migración en los destinos aprobados. No se aplicó
ningún cambio remoto. Retención aprobada: 30 días para cuenta cerrada y evidencia
de membresía terminada, 90 días de auditoría; la ejecución periódica y la retirada
confirmada de la identidad del proveedor siguen pendientes. LEGAL REVIEW REQUIRED.

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
