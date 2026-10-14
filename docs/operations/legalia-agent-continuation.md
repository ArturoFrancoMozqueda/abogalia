# Legalia — órdenes de continuación por agentes

2026-10-13, America/Mexico_City. Arturo pidió reactivar agentes y continuar el plan.
Base común `eba6cbedb631`, `codex/identity-design`, checkout compartido con propiedad
de archivos separada. Coordinador conserva integración/configuración global/locks
y commit/push revisados. No worktrees del baseline anterior ni `.env` compartidos.

| Agente | Capacidad y alcance | Archivos propios | Aceptación / dependencia |
|---|---|---|---|
| A4 identity_checkpoint | C02: confinar DSN en runtime fuera del launcher | identity/runtime.py, tests/test_runtime.py, operations/identity-runtime-confinement.md | Rechazar hosts/proyectos/roles/parámetros no aprobados; fixtures locales solo opt-in Python, sin modo activable por env/main; A2 revisa |
| A2/A3 identity_security | C02: revocación Auth y retención pendientes | operations/identity-c02-security-next.md, checkpoints/identity-session-validation.md | Fuentes oficiales, solución soportada o bloqueo; checkpoint antes de cambiar fuente de revocación; único escritor de migraciones si después se autorizan |
| A1 identity_data | C03: contextos y confianza profesional | checkpoints/professional-contexts.md | Ocho secciones, modelo conceptual y máximo cinco decisiones; no tablas/código/UX sustantiva sin aprobación |

Todos leen README, plan27, decisionlog y checkpoint asignado antes de trabajar.
No leer `.env`, copiar secretos, usar sesiones del proveedor fuera del flujo
autorizado, consultar datos reales o operar Kova. Sin mutaciones remotas por parte
de agentes; el coordinador conserva control del destino y autorización.

Los agentes de C03 avanzan diseño mientras C02 necesita pasos privados del
operador. No confundir trabajo concurrente con cumplimiento de dependencias: C03
no se habilita en runtime antes de permisos/modelo aprobados y cierre de sus gates.
El plan completo se entrega por capacidades verificables; hosting, pagos, IA y
tratamiento jurídico siguen requiriendo sus decisiones explícitas.

## Entrega comprobada de esta tanda

Confinamiento runtime implementado y revisado A2. Custodia de conexiones reforzada
con sslcertmode=disable, soporte libpq16+ y fallo previo a conectar cuando no es
compatible; revisión A4. Sin archivos de certificados/claves privados leídos.
380 pruebas API/SQL pasan en PostgreSQL temporal aislado; gateway Auth simulado.
make check-api pasa. Interfaz: doce sustituciones de nombre visible en ocho archivos,
sin modificar autenticación/rutas/contratos; A1 comparó contra HEAD y confirmó
alcance. pnpm check pasa (lint, tipos, build). No cambios de dependencias o lockfiles.

Checkpoint de validación activa de sesiones y C03 preparados/revisados. Se
presentaron dos decisiones a Arturo; mientras no responda, permanecen Proposed,
sin código GET/user ni tablas/permisos/contextos profesionales. Publishable privada
continúa pendiente del operador, según su respuesta de esta tanda. No pruebas de
correo/login real, operación de retención, CI remoto o despliegue atribuidos.
