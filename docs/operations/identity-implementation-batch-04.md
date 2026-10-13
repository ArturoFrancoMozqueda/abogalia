# Tanda 04 — Activación parcial y publicación C02

Base común 98dd4fa. Arturo aprobó tres paquetes recomendados y es responsable de
cierre/retiro Auth y fallos de retención (D-036); pidió env privado y commit/push
periódicos revisados (D-037). Sin compra de dominio, hosting o upgrade de proveedor.

## Entrega integrada

- Launcher local privado: 55 pruebas. Consume .env solo en runtime aprobado,
  whitelist, owner/0600/sin links, gramática restringida, DSN/origen/destino/TLS
  explícitos y herencia PG filtrada; vacío/ausente deshabilita Auth. Redacta también
  FD nativos, no solo Python/logging. make dev-api usa este launcher sin autoreload.
- Bootstrap SQL: 15 pruebas PostgreSQL reales aisladas. Owner/runtime independiente
  y probe separado. Negativos LOGIN reales, rollback de toda instalación, permisos
  temporales retirados; ADMIN automático de creador documentado, sin SET/herencia.
- Piloto OTP: 19 pruebas con HTTP simulado. TTY y prompts privados, buzón único
  hasheado, marcador local24h sin overwrite, lock, máximo6, pausa60 y fsync de archivo,
  directorio y padre; reserva previa durable incluso timeout, cero retries. Solo
  signup/recover HTTPS fijo; publishable exclusiva, respuestas sin tokens. Requiere
  verificación privada del operador de customSMTP/plantillas antes de permitir envío;
  global EMAIL_READY sigue separado. Ningún ensayo o marcador real ejecutado.
- Validador de dos HTML OTP: 7 nuevos tests stdlib, sin render/envíos reales. Guía de
  operador y ejemplo de scheduler SOURCE sin instalación o credenciales de producción.

Revisiones independientes: A5 launcher/SQL y A4 piloto. Se corrigieron diagnóstico
nativo por FD y durabilidad del directorio padre. No ampliar permisos por errores.
El coordinador ejecutó suite fresca final: **280 passed**; clusters principal y de
roles temporales detenidos/eliminados. **31 tests stdlib passed**, check-api y lint
nuevo pasan; sin dependencia nueva o lockfile modificado. Web no cambió.

## Operación real y pendientes

[Esquema Supabase](identity-supabase-verification.md): 002+001 aplicado y metadatos
remotos verificadas. Tres tablas privadas con RLS FORCE, owner/runtime mínimos,
sin USAGE anon/authenticated y permisos temporales revocados. Probe003 sigue cerrado
por falta de grantor USAGE Auth. Advisors conserva dos WARN de función previa del
trigger RLS público, registrados sin cambios fuera del bloque aplicado.

.env creado con nombres vacíos/0600/excluido, no leído por agentes; .env.example
vacío sí se revisa y escanea. Marcador privado /.identity-pilot/ excluido de Git.
Arturo configura las conexiones y SMTP mediante mecanismos privados, no chat.
El proyecto de Resend y su SMTP requieren confirmación del espacio por producto y
clave sending_access inyectada por el operador: herramienta create_api_key expondría
la clave y no se llamó. Supabase no ofrece aquí herramienta de configuración Auth
que permita hacerlo sin esa preparación privada; no se fingió integración.

Primer milestone b30bf7b publicado y verificado en codex/identity-design. La entrega
SQL/piloto/evidencia se publicará como segundo milestone después del scanner.
No merge/main, despliegue, CI remoto, mensajes, usuarios, job productivo o retirada
Auth afirmados. C02 sigue pendiente de configuración/prueba real y operación segura.

Escáner final Gitleaks8.30.1 con wrapper redactado: 141 fuentes permitidas e historial,
cero hallazgos; self-test positivo/negativo pasó. Ejemplo .env raíz permitido por
ruta exacta y escaneado, con negativos para otros env; .env privado no se versiona.
Se hará push del segundo milestone después de commit y verificación de remoto.
No se necesita otra aprobación de D-036; los pasos pendientes son de capacidad de
plataforma y configuración privada del operador, detallados en la guía.
