# Tanda 02 — Implementación local de Identity

Fecha: 2026-10-12. Coordinador A0. D-031/D-032/D-033 Approved.
T05–T07 entregados como contratos técnicos; revisados por A0 para implementación.
Retención: 30 días de cuenta cerrada/evidencia de membresía terminada y 90 días de
auditoría. No retención jurídica ni verificación profesional por inferencia.

## Orden y responsabilidades

Antes de repartir código: C01 con Gitleaks 8.30.1 comprobado contra checksum oficial,
wrapper sin salida cruda y revisión independiente A2. Diez pruebas de wrapper,
self-test real positivo/negativo y scan de archivos permitidos/historial pasaron;
artefacto inicial web revisado. Se corrigieron symlinks antecesores, archivos
sensibles versionados y excepción exacta del ejemplo público web.

Baseline incluye fundación y diseños locales mediante inventario explícito;
sin `git add .`, sin archivos de runtime, sin push. Cada implementación se asignará
a un worktree desde ese commit y con archivos exclusivos. A0 conserva dependencias,
lockfiles, workflow y referencias comunes. Ningún agente elige proveedores/gasto.

| Autor | Trabajo | Archivos exclusivos | Revisor |
|---|---|---|---|
| A4 | Gateway Supabase, JWT, CSRF, sesión y HTTP | Módulo identity excepto storage, ruta Auth, main y tests Auth | A0/A2 |
| A3 | Almacén PostgreSQL y migración local mínima | storage, migración Identity, pruebas de datos y diccionario físico | A0/A4 |
| A5 | Rutas españolas y cliente API | Nuevas rutas/componentes Auth, cliente TS, rutas y estilos Auth | A0/A2 |
| A0 | Integración, runtime sintético, dependencias, C01 y checks | Configuración global y evidencia | A2 |

Alcance actual C02: acceso/sesión y controles técnicos; futuras entidades C03–C19
siguen separadas. No crear cliente global o tablas de servicio. Profesional sin
habilitación aprobada no recibe permisos por metadata ni nivel MFA.

## Entorno y límites

PostgreSQL local en cluster temporal aislado y socket privado; datos sintéticos,
roles owner/runtime separados. No leer claves existentes ni usar base de clientes.
SDK/HTTP Auth real implementado, pruebas de proveedor usan transporte simulado
declarado; jamás equivalen a prueba del proyecto Supabase o de MFA real.

La configuración se inyecta en runtime y no se imprime. Sin credenciales/plantillas
de correo aprobadas, dependencias incompletas devuelven 503; no anunciar envío o
revocación del proveedor exitosa por simulación. Restricción de consulta de sesiones
Auth necesita contrato mínimo y verificación antes de operación remota. No aplicar
migraciones/grants remotos. Recuperación/desinscripción MFA permanece cerrada.

Los endpoints siguen [T05](../contracts/identity-api.md); frontend sigue
[T06](../ux/identity-flows.md); aceptación sigue [T07](../testing/identity-acceptance.md).
No se declara C02 Done hasta recorrer integración, negativos y proveedor configurado
y documentar claramente los límites. Hosting, SMTP, legal y release siguen pendientes.
