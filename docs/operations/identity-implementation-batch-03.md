# Tanda 03 — Preparación operativa C02

Fecha 2026-10-12. Base común `720c1cf`; rama `codex/identity-design`.
Tres agentes con propiedad exclusiva de archivos y coordinación A0. No cambios
ajenos descartados, dependencias nuevas, recursos remotos creados o publicación.

## Cambios y revisiones

- A4: preflight por presencia de nombres y catálogo local read-only; 44 pruebas.
  A2 revisó y se corrigieron variables PG implícitas y eco de argumentos; además
  socket/padre privados del usuario, prefijo de fixture y servidor sin TCP.
- A2: preview/purga explícita local de sesiones/auditoría; 21 pruebas. A5 revisó
  sin bloqueantes; no acepta sujetos o pruebas de retirada Auth del operador.
  Cuenta vencida sin retirada verificada permanece bloqueada y se reporta.
- A5: dos plantillas OTP españolas GoTrue, sin enlaces/JS/píxeles; 11 comprobaciones
  de HTML por plantilla y contraste 13.87:1. Revisión A0 de propósito, placeholders
  y ausencia de contactos/dominios inventados. MIME, clientes reales y entrega
  siguen pendientes.
- A0: checkpoint de activación, decisiones D-034/D-035, registro y documentación.
  Se preserva D-032 30/90; no se infiere retención de otros datos o proveedores.

## Verificación final y alcance

La ejecución fresca `scripts/run_identity_tests.py` reportó **191 passed** sobre
PostgreSQL real aislado; terminó y eliminó su cluster. Incluye 126 pruebas de la
entrega anterior y las 65 nuevas. Ruff y formato de código nuevo pasan. Se conservan
las 22 pruebas stdlib previas; no se volvió a prometer o ejecutar CI remoto.

CLI de preflight real por defecto: ninguna variable requerida presente en ese
proceso, status disabled, real_readiness pending. Solo se leyeron nombres, no valores.
No conecta, no lee dotenv y no se puede deducir configuración de otros procesos.

Lectura externa limitada: get_project confirmó organización/ref/región/healthy
correctos; JWKS público una clave ES256. La consulta de catálogo por conector no
produjo evidencia interpretable: no afirmar presencia/ausencia de roles/schema.
Sin lectura de usuarios, sesiones, claves privadas o recursos de Kova.

Arturo eligió Resend SMTP Free sin sobrecostos automáticos y frontend local con
Supabase real; no existe dominio. Indicó buzón de prueba en conversación, omitido
en repo. Se comprobó viabilidad documental del remitente de ensayo de Resend por
SMTP para el correo asociado a la cuenta; no es prueba de envío o integración.

## Pendientes concretos

[Activación real](../checkpoints/identity-real-activation.md): revisar operación de
roles/schema privado/probe, configuración Auth y mecanismo privado del operador.
No usar service_role o grants amplios para habilitar un error.
[Correo](../checkpoints/identity-email-operations.md): aceptar TTL/cuotas y tratamiento
SMTP, verificar cuenta/buzón y configurar sin divulgar material privado; dominio
puede aplazarse solo para ensayo acotado.
[Retención](../checkpoints/identity-retention-operations.md): actor/proof de cierre y
retirada Auth, job/rol operativo y responsable/horario/alertas. No cuentas o job
remotos implementados. C02 sigue incompleta por estos pendientes.

Sin SMTP configurado, correos enviados, Auth real probado, DNS, migraciones/grants
remotos, scheduler instalado, compra de dominio, hosting o CI remoto.

Escaneo final Gitleaks 8.30.1 con wrapper redactado: 127 fuentes permitidas e
historial, cero hallazgos. `make check-api` pasó (lint/formato/import/dependencias).
Formato del código nuevo normalizado con configuración API. No cambios al frontend
ni lockfiles: el build anterior se conserva y no se atribuye una nueva ejecución.
El buzón solicitado a Arturo fue indicado; se registra solo su selección, no la
dirección personal. Procesamiento SMTP, parámetros del ensayo y operación remota
siguen en los checkpoints propuestos, sin reabrir proveedor/piloto ya elegidos.
