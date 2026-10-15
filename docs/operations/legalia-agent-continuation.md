# Legalia — órdenes de continuación por agentes

## Estado vigente — 2026-10-15

Esta actualización sustituye el estado operativo de los apartados históricos
siguientes, que se conservan como evidencia de cada tanda. Se basa en las
verificaciones privadas comunicadas por A0; esta actualización documental no
lee configuración privada ni repite conexiones o pruebas del proveedor.

| Área | Estado verificado y límite actual |
|---|---|
| Configuración privada C02 | Credencial/contraseña del rol runtime y conexión DB configuradas y verificadas; TLS `verify-full` verificado. Publishable y claves necesarias presentes y validadas privadamente. No publicar valores ni diagnósticos crudos |
| Gates de ejecución | `ABOGALIA_IDENTITY_ENABLED=0` y `ABOGALIA_AUTH_EMAIL_READY=0`; configuración lista no equivale a activación |
| Validación de sesión | Mecanismo HTTP D-039 implementado localmente, con fallo cerrado. Sigue pendiente demostrar revocación con el proveedor real; sin fallback JWT local ni permisos SQL Auth adicionales |
| Correo/Auth real | SMTP y plantillas guardados; entrega de correo, OTP, MFA y recorrido positivo real pendientes. No atribuir envío o acceso real a pruebas sintéticas |
| C03 privado | API, SQL y web implementados y verificados localmente para borrador privado y práctica inactiva. Migración C03 remota no aplicada; sin habilitación profesional, publicación, despacho, invitaciones o capacidades reales |
| Retención | Plazos aprobados conservados; ejecución periódica pendiente. Retiro lógico y cálculo de vencimiento no acreditan borrado físico ni retirada Auth del proveedor |

D-040 y D-041 mantienen aprobados PC-01..05 A y Q-C03-01..03 A; las
preguntas históricas no requieren volver a aprobarse. La identificación/concesión
real del revisor, el procedimiento de revisión profesional y su validación
jurídica no se resuelven por esa aprobación. **LEGAL REVIEW REQUIRED**.

Próximo trabajo coordinado: verificar revocación HTTP, entrega/OTP/MFA reales y
los demás gates antes de activar C02; revisar por separado la aplicación remota
de C03 y la operación periódica de retención. Cada operación mantiene su alcance
y evidencia propios. No ampliar privilegios ni activar flags para sortear un
fallo. Hosting, pagos, IA y datos jurídicos no se habilitan por este estado.

La verificación anónima local de `/profesional` → `/acceso` con Identity apagada
no acredita autenticación positiva o persistencia profesional real. Consultar el
[checkpoint vigente de activación](../checkpoints/identity-real-activation.md) y
el [informe integrado](legalia-approved-implementation-batch.md).

## Antecedentes de las órdenes y entregas

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

Checkpoint de validación activa de sesiones y C03 preparados/revisados en la tanda
anterior. Se presentaron dos decisiones a Arturo; entonces permanecían Proposed,
sin código GET/user ni tablas/permisos/contextos profesionales. Publishable privada
continúa pendiente del operador, según su respuesta de esta tanda. No pruebas de
correo/login real, operación de retención, CI remoto o despliegue atribuidos.

## Nueva orden aprobada — 2026-10-14

Arturo aprobó validación activa HTTP D-039 y PC-01..PC-05 A de C03 D-040.
Base publicada al iniciar: 338617a91589. La tabla anterior es histórica.

- A4: gateway/probe HTTP y fronteras Identity; pruebas firmadas sintéticas +
  PostgreSQL aislado. A2 revisa revocación/rotación/fallos antes de integrar.
- A2/A3: modelo de datos y matriz C03; único responsable de futuras migraciones.
  Shim SQL limitado a fixtures legados, sin usarlo como fallback runtime.
- A1/A5: contratos API/UX C03 y primer modelo de dominio privado, tras revisión
  de campos/propiedad/estados/retención. Invitaciones, concesión del revisor y
  relevo requieren sus precisiones; no inventar TTL, capacidades o responsables.
- A0: integración runtime/launcher explícitamente HTTP, documentación privada
  de publishable, verificación, escaneo redactado y publicación por archivos.

C03 no habilita datos reales por aprobar sus paquetes. C02 conserva la prueba real
obligatoria de revocación y entrega; no requerir permisos SQL Auth adicionales
para el mecanismo HTTP aprobado. No leer valores del .env o secretos de proveedor.

Revisión independiente A2 del mecanismo HTTP completada sin bloqueantes en el
ámbito Identity; 396 pruebas API/SQL pasaron en la integración de A0 antes del
dominio C03. El runtime no requiere SQL auth ni credenciales probe. El resultado
final de toda esta tanda se conserva en [informe integrado](legalia-approved-implementation-batch.md).
