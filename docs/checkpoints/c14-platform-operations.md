# C14 — Plataforma y operación

Fecha: 2026-10-16. Estado: **Proposed** para el cierre operativo restante. Hosting,
costo y optimización ya aprobados conservan su estado; este checkpoint no los reabre.
Base documental: rama `codex/identity-design`, referencia común `4eb597c`.

## Lo que entiendo

La web y API de Legalia están publicadas, pero disponibilidad HTTP no demuestra
recuperación, aceptación Auth ni operación de datos. C14 debe sostener una entrega
con versiones identificables, costo controlado y recuperación probada. Este diseño
no provisiona recursos ni habilita captura de observabilidad.

## Decisiones tomadas

- D-025/D-026/D-030: React Router/Vite y FastAPI, Cloudflare Workers Static Assets
  Free y una sola Fly shared-cpu-1x/1 GB en iad; base autorizada US$6.70/30 días
  encendida más transferencia/impuestos. Sin réplicas o servicios pagados extra.
- Supabase/Resend propios y Kova fuera de alcance; secretos inyectados privadamente.
- Optimización del 2026-10-16: assets públicos existentes evitan Worker; API/HTML
  conservan gateway, headers y no-store. Logs, invocation logs y traces OFF.
- D-032/D-036: 30/90 días y Arturo responsable de retirada Auth/fallos de retención.
  Son obligaciones aprobadas, no evidencia de ejecución periódica.

## Decisiones pendientes

1. Objetivos RPO/RTO y tolerancia de indisponibilidad/pérdida, incluyendo una VM.
2. Procedimiento de respaldo y restauración: alcance, custodia privada, retención
   de copias, acceso y costo si excede recursos existentes; sin garantía inventada.
3. Ejecutor mínimo de mantenimiento real, calendario, tolerancia de demora,
   autenticidad de retiro Auth y canal privado de fallos. No nuevos plazos tácitos.
4. Observabilidad: fuente/campos completos, finalidad, acceso, retención y canal de
   alertas antes de activar cualquier captura; un evento mínimo no limpia el
   contexto añadido por el proveedor.

## Diseño propuesto

Modelo conceptual: ReleaseRecord identifica fuente, digest/versión y configuración
pública; VerificationResult pertenece a una release y contiene únicamente controles
fijos; RecoveryExercise refiere versiones fuente/destino y resultado saneado;
MaintenanceExecution registra fases, conteos y fallo fijo. Estos conceptos no crean
tablas ni autorizan persistencia nueva.

Ciclo de release: preparada → verificada → desplegada → comprobada; un fallo pasa
a detenida y exige evaluar rollback. Un rollback de código no revierte esquemas,
retiros Auth o datos. Restauración: planificada → aislada → reconciliada → probada
→ reactivada; no se vuelve a abrir acceso antes de reconciliar cierres, retiros,
sesiones y purgas posteriores a la copia.

Coordinador controla promoción/artefactos; Arturo es responsable operativo ya
aprobado para retiro Auth/fallos30/90. Las capacidades de despliegue, runtime y
mantenimiento son distintas. No usar el runtime como owner, ni fixture owner como
rol de producción. La preautenticación actual exige una VM/un proceso: escalar
necesita otro diseño y presupuesto, no cambiar una bandera.

## Datos afectados

Solo documentación pública en esta entrega. Futuras evidencias operativas son
restringidas: referencias de versiones, tiempos, checks y conteos mínimos, sin
identidades de usuario o cuerpos. Retención de estos registros y respaldos pendiente;
no aplicar automáticamente90 días de auditoría a cualquier registro nuevo. C02/C03
conservan sus políticas aprobadas. Backups y proveedor tienen contratos separados.

## Seguridad

No dotenv/modelo de secretos, DSN, cabeceras, cookies o diagnósticos crudos en
reportes. Preservar TLS verify-full, RLS/FORCE, runtime mínimo, CSRF y revocación.
Restauración aislada sin correos o jobs salientes; no volver a publicar datos
retirados. Fallar ante destino ajeno, esquema parcial, prueba Auth ambigua, exceso de
cuota o fallo de scan. No elevar privilegios ni activar Paid por esos fallos.
**LEGAL REVIEW REQUIRED** para retención, derechos y tratamiento de respaldos.

## Impacto futuro

C14 acompaña cada incremento C02–C17. Un checker público sano solo acredita
web/acceso/health y no DB, correo o autorización. Observabilidad y analítica de
producto son contratos separados (C16). Publicar un incremento no cierra C15.

## Implementación propuesta

1. A0 mantiene inventario no secreto de versión/destino y concilia documentación
   actual; A2 revisa privacidad y A7 reproduce negativos con fixtures sintéticos.
2. Preparar runbook de incidente/rollback sin efectos remotos y simulación de
   pérdida de proceso, caché privado, downgrade TLS y config parcial. Debe rechazar
   destino no aprobado y conservar versiones anteriores identificables.
3. Tras aprobar pendientes, diseñar rol/adaptador Auth de mantenimiento y prueba
   restauración aislada; migraciones únicas a cargo del responsable de datos.
4. Aceptación: release real identificada, smoke HTTPS y negativos pasan, recuperación
   ensayada con RPO/RTO medidos frente a objetivos aprobados, mantenimiento real y
   alertas verificadas si se aprueban. No declarar estos controles ejecutados aquí.

Evidencia existente: [Fly](../operations/legalia-fly-deployment.md),
[Cloudflare](../operations/legalia-cloudflare-deployment.md),
[cuota/observabilidad](../operations/legalia-cloudflare-quota-observability.md),
[retención coordinada](../operations/legalia-coordinated-retention.md).
