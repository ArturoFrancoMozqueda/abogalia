# Handoff A3 — Planeación de operación y cierre

Fecha: 2026-10-16. Orden del coordinador A0; base común `4eb597c`, rama
`codex/identity-design`. Alcance: documentación C14–C19 y auditoría documental C00–C03.
**Planning preparado, no implementación ni aceptación de producto completadas.**

## Entregables

- [C14 Plataforma](../checkpoints/c14-platform-operations.md): cierre operativo,
  recuperación, versiones, mantenimiento y observabilidad pendiente.
- [C15 Entrega](../checkpoints/c15-complete-delivery.md): alcance de lanzamiento,
  dependencias y aceptación extremo a extremo.
- [C16 Auditoría/analítica](../checkpoints/c16-audit-analytics.md): separar finalidades,
  campos permitidos, métricas y retención nueva no aprobada.
- [C17 Operación limitada](../checkpoints/c17-limited-operations.md): revisión,
  excepciones y recursos sin lectura jurídica universal.
- [C18 Ampliación jurídica](../checkpoints/c18-legal-expansion.md) y
  [C19 Integraciones](../checkpoints/c19-advanced-integrations.md): diferidas;
  puertas de reentrada, no implementación o ampliación de release.

Cada checkpoint tiene las ocho secciones obligatorias, modelo conceptual, estados,
clasificación, propiedad, historia/retención, dependencias, aceptación y negativos.
Son Proposed; D-025..D-041 y autorizaciones posteriores citadas mantienen su alcance.
No se aprobaron por elaborar este planning tablas, UX, permisos, plazos o gastos nuevos.

## Matriz de evidencia y pendientes C00–C03

La evidencia es la documentada por entregas previas, no una nueva ejecución en
esta revisión. Un conteo de pruebas no sustituye el recorrido real correspondiente.

| Capacidad/control | Evidencia existente | Falta para cierre | Tipo / siguiente trabajo |
|---|---|---|---|
| C00 fundación | README, base web/API, lockfiles, build y HTTP; hosting ahora publicado | Conservar reproducibilidad por release; no declarar negocio terminado | Código/revisión continua dentro del baseline |
| C01 colaboración/secretos | Scans redactados antes de publicación; pruebas sintéticas y workflow de imagen Linux con bloqueo HIGH/CRITICAL | No confundir CI de imagen ejecutado con CI global; verificar checks remotos requeridos de cada release | Operación/QA: matriz de qué corrió local/CI/producción |
| C02 DB/runtime | Esquema Identity remoto, rol mínimo/TLS verify-full/RLS FORCE; API/health y cookies/CSRF HTTPS documentados | DB/Auth no se prueban por liveness; mantener prueba de conexión y controles por versión | Técnico sin pedir otra publishable ni privilegios Auth SQL |
| C02 registro/correo | SMTP/plantillas guardados, acceso público autorizado; Resend sin dominio con destinatario restringido | Crear cuenta APP controlada, confirmar OTP y verificar entrega/recuperación dentro del cupo aprobado | Humano introduce contraseña/OTP en UI privada; agente no los recibe |
| C02 MFA | Implementación y tests sintéticos | Enrolamiento/challenge real, fallos/expiración y sesión resultante; no registrar semilla/QR/código | Humano/QA; no conceder facultades por solo activar TOTP |
| C02 revocación proveedor | Herramienta aislada con19 tests sintéticos | Ejecutar con cuenta confirmada exclusiva; tokens originales aún vigentes deben ser rechazados tras logout local/global | Humano/QA mediante flujo privado documentado; no password por chat |
| C02 revocación integrada | Contrato D-039 y pruebas locales de frontera transaccional | Navegador/API/SQL conservando cookie local después de revocación externa; demostrar denegación y rollback de negocio | Técnico/QA después de prueba proveedor, sin fallback JWT |
| C02 retiro/retención |30/90 aprobados; runner de fixture y fases coordinadas C02/C03 probados | Adaptador de evidencia Auth auténtica, rol/ejecutor real mínimo, periodicidad, fallos y evidencia de apply | Diseño/operación pendiente; Arturo ya responsable, no volver a preguntar30/90 |
| C02 restauración | Diseño exige reconciliar retiros tras restore | Respaldo/custodia/RPO/RTO y ensayo aislado; impedir resucitar sesiones/perfiles/cuentas retirados | Decisión operativa + ejecución posterior; no atribuir recuperación a tests de purga |
| C03 borrador privado | API/SQL/web locales; MFA/propietario/CSRF/versión y FORCE RLS probados con fixtures | Aplicación remota revisada y aceptación real por cuenta confirmada/MFA | Técnico condicionado a integración y evidencia C02; no instalación por este handoff |
| C03 revisión/publicación | PC-01..PC-05 A y D-041 aprobados, modelo/matriz/API/UX preparados | Procedimiento de cotejo/suplantación/recurso, revisor alterno, implementación y pruebas | Jurídico/producto + técnico; no autoaprobación ni título de verificación excesivo |
| C03 despacho/membresía | Cardinalidad/contextos, invitación24h/recibo30d/audit90d, revisor/cierre excepcional aprobados | Implementar invitación interna/aceptación/concurrencia/salida/relevo y operación de datos | Técnico sobre contratos aprobados; no reabrir parámetros D-041 |

Fuentes: [sesiones reales preparadas](legalia-real-session-acceptance.md),
[retención coordinada](legalia-coordinated-retention.md),
[borrador C03](legalia-professional-draft-increment.md),
[Cloudflare real](legalia-cloudflare-deployment.md),
[Fly real](legalia-fly-deployment.md), [README](../../README.md).

## Cola segura y criterios verificables

1. A0 concilia estado vigente con evidencia ya documentada, registra por capacidad
   lo implementado local, remoto, simulado y pendiente. No reconectar proveedores
   o volver a pedir credenciales por descripciones históricas.
2. A7 prepara matriz de aceptación controlada sin envío adicional implícito. Arturo
   crea la cuenta APP en la UI; verifica correo/OTP y MFA sin compartir contraseña,
   códigos, semillas ni capturas con credenciales. El presupuesto SMTP original
   máximo6 solicitudes no se renueva por este planning; no afirmar cuánto queda
   sin evidencia segura del ejecutor.
3. A4/A7 usan el harness privado de revocación aprobado después de disponer de
   cuenta confirmada exclusiva; si resultado ambiguo, mantener pendiente y revisar
   contrato, no ampliar permisos ni dar por vencido el requisito.
4. A4/A2 preparan aceptación integrada de cookie/revocación y efectos transaccionales,
   sin clientes reales ni datos del proveedor en outputs.
5. A3 prepara compatibilidad de migración C03 y maintenance con revisión independiente.
   El runner coordinado falla cerrado si C03 no existe o está parcial; producción
   todavía no tiene C03. Resolver dependencia explícitamente, sin crear tablas
   como atajo ni introducir modo identity_only silencioso.
6. A0 prepara paquete operativo de retiro Auth/rol mínimo/evidencia/periodicidad y
   recuperación para decisión. Su implementación exige modelo/retención aprobados
   de cualquier evidencia nueva. Runtime no recibe owner/DELETE por conveniencia.
7. C03 restante puede avanzar localmente en contratos ya aprobados; la publicación
   profesional y asignación real del revisor esperan procedimiento de confianza,
   MFA y negativos. C04+ siguen sus checkpoints; C18/C19 no entran al release.

## Riesgos de apertura a resolver

- Registro público ya autorizado no equivale a entrega general de correo: sin
  dominio propio, el remitente de pruebas de Resend conserva restricción. No
  promocionar onboarding general o envíos a terceros sin resolver esta condición.
- Una VM/un worker conserva estado transitorio de preautenticación; no ofrece HA.
  No añadir réplicas para cubrirlo sin nuevo diseño/costo.
- La retirada Auth no se acredita por ausencia de sesión, GET/user negativo,
  UUID manual o logout; faltan autenticidad y vínculo operación/sujeto/proyecto.
- Retención implementada solo en fixture no demuestra30/90 reales; no perpetuar
  tombstones o cuentas vencidas por no contar con evidencia de retiro.
- Logs/traces siguen OFF; checker público es a demanda y no alerta ni historial.
  Nueva captura puede añadir metadatos invisibles a nuestra proyección cerrada.
- Falta revisión jurídica de confianza, derechos, conservación y condiciones de
  servicio. **LEGAL REVIEW REQUIRED**; no promesas de acreditación o cumplimiento.

## Próximas decisiones propuestas — máximo seis, sin respuestas asumidas

No requieren responderse todas hoy; A0 debe combinar con otros agentes y evitar
repetir aprobaciones. Este listado prepara decisiones, no es autorización.

1. **Primera entrega útil:** recomendar clientes propios con solicitud/acuerdo/
   seguimiento mínimo, frente a catálogo/derivación; precisar incluidos/excluidos,
   mercado y criterio de éxito. No implica aprobar C04/C05 de forma automática.
2. **Confianza profesional:** aprobar procedimiento de cotejo, identidad/suplantación,
   corrección/recurso y revisor alterno para el perfil de Arturo, con revisión jurídica.
   No preguntar de nuevo quién recibe la capacidad limitada D-041.
3. **Recuperación:** fijar RPO/RTO, custodia/retención de respaldos y ensayo; cualquier
   costo adicional se presenta concretamente y conserva configuración actual.
4. **Retiro y mantenimiento:** aprobar mecanismo verificable Auth, rol/ejecutor
   mínimo, horario/tolerancia y canal privado de fallos. Arturo y30/90 ya aprobados.
5. **Observabilidad:** mantener OFF como baseline; elegir finalidad/campos completos,
   acceso/retención/alertas si se desea captura. Analítica de producto se decide
   aparte y no se activa para compensar falta de logs técnicos.
6. **Correo para usuarios generales:** decidir cuándo adquirir dominio y qué
   remitente/buzón/control DNS usar; dominio sigue aplazado. No volver a elegir
   ResendFree ni confundir compra de dominio con buzón o correo entregado.

## Reconciliación transversal coordinada

A0 comunicó durante esta tanda que ya actualizó README (proxy/hosting publicado),
identity-real-activation (estado público vigente frente a flags0 históricos) y
plan27 (inventario único con histórico íntegro separado). Esas contradicciones
identificadas en la revisión inicial no se reportan como bloqueos aún abiertos.
No volver a pedir publishable, recrear hosting o apagar acceso por una foto vieja.

AGENTS.md conserva una foto inicial de base vacía/hosting pendiente; sus reglas de
seguridad siguen vigentes, pero la evidencia posterior D-026/D-038/D-040 y los
reportes fechados determinan estado real. Los docs locales C03/retención mantienen
flags apagados como estado de su entrega histórica; no equivalen al estado actual
de producción. Las notas de D-026 que dicen «despliegue pendiente» necesitan leerse
con su actualización posterior: aprobación de una decisión no implementa todas
las capacidades que dependan de ella.

Dependencia aún vigente: mantenimiento coordinado exige esquema C03 completo y
actualmente remoto carece de él. Resolver con paquete revisado/operación explícita,
sin omitir controles, ampliar rol ni instalar dependencias por conveniencia.

## Verificación y límites de esta entrega

Leídos AGENTS/README/plan27/decision-log y checkpoints/operaciones Identity/C03,
hosting y observabilidad. Consultadas skills instaladas workers-best-practices y
Supabase para conservar límites del proveedor; no se invocó ninguna API/CLI del
proveedor ni se hizo un diseño de API o SQL nuevo. La recomendación genérica de
habilitar logs/traces no sustituye la instrucción vigente de preparar sin captura.

Comprobación documental: ocho encabezados por checkpoint, rutas locales y diff
propio revisados. Sin código, dependencias, migraciones, datos reales, secretos,
consultas externas, commits, agentes hijos, CI, despliegues o pruebas funcionales
nuevas. A0 integra, escanea fuentes y decide publicación de esta documentación.
