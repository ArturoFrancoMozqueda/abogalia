# Legalia — tanda aprobada D-039 / D-040

2026-10-14. Base 338617a91589, rama codex/identity-design. Arturo aprobó
validación activa por API y cinco paquetes de C03. El coordinador reutilizó tres
agentes con archivos exclusivos y revisión independiente.

## Cambios y garantías

C02 selecciona explícitamente HTTP Auth para validar la sesión custodiada. No
requiere grant SQL auth o DSN probe, ni usa ausencia de configuración como fallback.
Runtime conserva rol PostgreSQL mínimo/TLS y launcher privado; el nombre legado
AUTH_SESSION_CHECK_DSN se acepta pero no se inyecta o usa. GET/user está ligado al
JWT/sub/SID verificados; errores indeterminados deniegan acceso sin purgar custodia.
Las renovaciones consumidas se conservan aun cuando falle la comprobación activa,
sin prolongar actividad ni entregar cookie/datos privados. Ver informe detallado
[HTTP Identity](identity-api-session-verification.md).

C03 concreta modelo, matriz de acceso, contratos API y UX del checkpoint aprobado.
Primer incremento: dominio privado de borrador y práctica inactiva, separado de
habilitación, cédula, revisión, publicación, despacho y membresía. No SQL remoto,
endpoints o interfaz profesionales habilitados por esos documentos. Invitación,
concesión del revisor y responsabilidad excepcional de cierre requieren sus
respuestas concretas Q-C03-01..03; no se reabren PC-01..PC-05.

La [guía privada de publishable](legalia-private-publishable-setup.md) permite al
operador pegarla localmente sin compartir valores. El .env real se comprobó solo
por metadata: archivo regular, propietario actual, enlace único, permiso0600 y
exclusión Git. No se leyó su contenido ni se afirmó que estuviera configurado.

## Validación y límites

Integración A0: **416 pruebas pasan**, incluidas 20 del dominio puro C03 y
396 de Identity/herramientas API/SQL. make check-api pasa: lint, formato,
dependencias e importación; 31 pruebas de herramientas pasan. Scanner fijo8.30.1:
164 fuentes/historial, cero hallazgos, canarios positivo/negativo correctos.
No se modificó el frontend ni se atribuye un build nuevo a esta tanda.
Las pruebas usan PostgreSQL real aislado y transporte Auth simulado declarado.
No equivalen a Supabase remoto, correo entregado, revocación real, retención
programada, restauración, CI remoto o despliegue. Sin datos de clientes ni recursos
Kova. No cambios de dependencias/lockfiles ni acceso directo del navegador a tokens.

C02 mantiene aceptación real, configuración privada y operación30/90 pendientes.
C03 necesita persistencia/aislamiento/RLS/HTTP/UX y revisión jurídica antes de
usuarios/datos profesionales reales. LEGAL REVIEW REQUIRED.
