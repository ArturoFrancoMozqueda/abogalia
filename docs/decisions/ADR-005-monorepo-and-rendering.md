# ADR-005: Monorepo Abogalia y renderizado público estático

Status: Implemented, 2026-10-12. Base local verificada; hosting y capacidades de negocio pendientes.

## Context

React y FastAPI están aprobados. El producto requiere catálogo público indexable y áreas privadas, con infraestructura inicial pequeña. Arturo aclaró que el monorepo sería Abogalia y después confirmó expresamente la opción recomendada con React Router. Kova conserva su repositorio independiente.

## Decision

Usar el repositorio abogalia como monorepo, con apps/web para React Router en modo framework sobre Vite y TypeScript, apps/api para FastAPI y docs para decisiones y producto. Prerenderizar páginas públicas seleccionadas, sin un servidor Node de producción en este bloque. Las áreas privadas futuras podrán usar carga cliente hacia FastAPI. Solo la portada se prerenderiza inicialmente; no se implementan todavía áreas privadas.

## Alternatives

- Monorepo con Vite SPA y renderizado público diseñado después.
- Repositorios separados de frontend y API.
- SSR en cada petición, con ejecución y costo de runtime pendientes.

## Why

Un repositorio permite coordinar contratos y versiones de frontend/API. El prerenderizado genera HTML indexable y permite servir archivos estáticos en el hosting propuesto. Conserva FastAPI como backend de negocio y evita añadir un servidor frontend permanente antes de necesitarlo.

## Consequences

Dependencias JS mediante pnpm con lockfile y Python en entorno propio con dependencias fijadas y hashes. CI distingue checks de web y API, sin despliegue automático. La configuración de ejemplo no necesita credenciales reales para iniciar la base técnica.

El contenido prerenderizado se actualiza al reconstruir. El catálogo dinámico deberá definir regeneración, rutas conocidas y metadatos cuando se diseñe; la elección no garantiza por sí sola actualización inmediata ni SEO completo. Rutas no prerenderizadas necesitarán fallback SPA en el hosting elegido. El proxy local Vite sirve para verificar llamadas a FastAPI y no configura producción.

## Risks

Despliegues descoordinados, contenido público obsoleto y publicación accidental de herramientas de desarrollo. La primera entrega excluye la ruta de comprobación local del build de producción y mantiene dominios sensibles sin implementar. No incorporar secretos a variables VITE_* o al HTML generado.

## Revisit when

El catálogo, la frecuencia de actualización, indexación o requisitos de contenido justifiquen SSR o regeneración distinta; o la coordinación de equipos exija separar repositorios. No cambiar stack ni hosting silenciosamente.

Fuentes: [React Router: prerenderizado](https://reactrouter.com/how-to/pre-rendering), [checkpoint del bloque](../checkpoints/repository-and-empty-database.md).

Verificación: [informe de base local](../operations/local-foundation-verification.md). Prerenderizado de portada y comunicación HTTP con FastAPI comprobados. CI preparado y checks ejecutados localmente; no se ha ejecutado CI remoto ni desplegado el producto.
