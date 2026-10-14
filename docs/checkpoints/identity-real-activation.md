# Checkpoint — Activación real de Identity C02

## Actualización vigente D-038: Legalia

Arturo aprobó el nuevo destino `spohytnxscljtitvmdab`, organización
`tagovxtvdicxjweeerwi`, y pidió instalar lo ya aprobado. Owner/runtime y esquema
privado están implementados y verificados por once controles de catálogo. Auth
JWT900/OTP600/6d y origen local guardados. Probe y SMTP/credenciales aún bloquean
activación. [Evidencia vigente](../operations/legalia-supabase-setup.md).
Los destinos y términos piloto siguientes son históricos; no son configuración
vigente ni autorización para modificar el proyecto anterior. El producto se llama
Legalia; no se eliminaron controles de seguridad por el cambio de nombre.

Fecha: 2026-10-12. Estado: Proposed / Awaiting decision para la operación remota.
Base local revisada: `720c1cf`, rama `codex/identity-design`. La petición de Arturo
ordena avanzar con Supabase real, correo y retención y presentar decisiones;
no resuelve proveedores, remitente, gasto, permisos operativos nuevos ni hosting.

## Aprobación operativa vigente

Arturo aprobó los tres paquetes y parámetros recomendados (D-036). Activación en
proyecto existente, Resend SMTP Free, OTP600s/pausa60s/máximo6 mensajes de ensayo
y tratamiento documentado quedan Approved; falta ejecución/verificación. Arturo
es responsable de cierre/retiro Auth y fallos de retención. Se conservan los límites
de permisos mínimos, sin hosting nuevo ni borrado sin evidencia. Los apartados
Proposed siguientes describen preparación anterior; no reabren estas aprobaciones.
La elección del mecanismo técnico de retirada/mantenimiento no admite credenciales
amplias en runtime ni una lista de UUIDs como prueba. D-037 pide env privado y push
revisado de fuentes; nunca valores privados en Git.

## Lo que entiendo

C02 tiene UX/API y sesiones persistentes verificadas localmente. Falta recorrer
registro, confirmación, acceso, recuperación, MFA y revocación con el proveedor
real y un buzón controlado, sin clientes reales ni publicar credenciales.
El piloto recomendado mantiene web/API locales y usa el proyecto Supabase
existente de Abogalia. Supabase/correo real no equivale a publicar el producto.

## Decisiones tomadas

- D-028: Supabase Auth. Proyecto `xggefantvuwpilksfdoy`, organización
  `jdmkzzkgnzwldthjqtgx`, Free/us-east-1, propios de Abogalia.
- D-031: correo/contraseña confirmado, custodia API/cookie opaca, JWT de 15 minutos,
  MFA TOTP y límites propios de 12 h/30 min. Sin roles por metadata.
- D-032: cuenta/evidencia mínima de membresía 30 días; auditoría 90 días.
- D-027: administración posprojectsupport, recursos y credenciales por producto.
- El 2026-10-12 el conector confirmó proyecto/organización y ACTIVE_HEALTHY.
  JWKS público respondió con una clave ES256. No se probaron login o correo real.

## Decisiones pendientes

1. **Piloto y datos:** D-035 aprueba frontend/API locales con Supabase real; propongo
   PostgreSQL del proyecto existente para el esquema privado Identity; sin crear
   otra base alojada ni hosting. Solo identidad sintética de Arturo, sin clientes.
   La aprobación local no selecciona ni publica hosting.
2. **Correo:** D-034 aprueba Resend SMTP Free sin overages automáticos. Arturo
   informó que no existe dominio; evaluar remitente de ensayo de Resend limitado
   al buzón de la cuenta. Arturo indicó su buzón privadamente; falta verificar
   asociación/configuración. Dominio/subdominio y
   From definitivo, tratamiento SMTP y cuota/TTL OTP siguen pendientes.
3. **Operación remota concreta:** revisar y autorizar creación de roles mínimos,
   aplicación de `apps/api/migrations/001_identity.sql` y permisos probe limitados
   a `auth.sessions(id,user_id)`; sin acceso browser/Data API, BYPASSRLS o service_role.
   Antes de ejecutar hay que comprobar privilegios del operador y propiedad actual;
   no elevarlos por un error. La migración local probada no es prueba remota.
4. **Retirada y retención:** quién tramita cierre/retirada Auth, prueba confiable de
   retirada, responsable del job y alerta de fallos; consultar checkpoint de retención.
   No volver a decidir 30/90 ni añadir retención jurídica.

## Diseño propuesto

Secuencia: decisiones → revisión de catálogo sin filas de usuario → preparación de
roles/DSN desde mecanismo privado del operador → esquema privado probado → Auth
configurado → SMTP/DNS y plantillas OTP → preflight → recorrido real controlado.
Todo cambio remoto debe limitarse a los destinos y artefactos revisados.

Auth: confirmar correo; mantener desactivados métodos no aprobados; verificar JWT
900 s mediante configuración sin abrir pantallas de claves. Habilitar TOTP según
contrato; recuperación/unenroll MFA permanecen cerrados. Códigos de seis dígitos en
cuerpo de formulario; nada de enlaces con tokens o redirecciones con credenciales.
TTL de OTP, cuotas y password policy se revisan con el checkpoint de correo.

La API usa DSN runtime mínimo y otro DSN probe; las credenciales y claves de
cifrado/CSRF se inyectan fuera de Git. Un operador configura credenciales sin
pasarlas al chat, herramientas con salida visible o argumentos de comandos.
No se pide al agente leer archivos dotenv ni claves existentes.

## Datos afectados

Piloto: identificador Auth, email del buzón controlado, sesiones cifradas y eventos
mínimos de acceso. Supabase Auth y SMTP procesan datos de autenticación; no reciben
información jurídica. No existen membresías o perfiles profesionales en esta tanda.
Datos y correo del proveedor tienen sus propios contratos/retención; 30/90 de
Abogalia no afirma que se hayan cambiado políticas del proveedor o de backups.

## Seguridad

Bloquear acceso si configuración/grants/probe/JWT/correo no están verificados.
No registrar cuerpos, tokens, códigos, cookies ni cabeceras privadas. No abrir
pantallas de claves; no contar usuarios o leer sesiones reales para diagnosticar.
La revisión de catálogo solicitada mediante el conector no produjo una evidencia
interpretable; su resultado se deja no confirmado y no se infieren grants ausentes.
No continuar con privilegios amplios ni desactivar RLS por este límite.

Solo buzón controlado con autorización de envío explícita y cupo de prueba
acordado. No avisos a terceros o clientes. LEGAL REVIEW REQUIRED antes de piloto
con personas/datos reales; el ensayo sintético no acredita cumplimiento legal.

## Impacto futuro

El piloto valida C02 sin seleccionar hosting. Un despliegue HTTPS deberá verificar
Secure/__Host, mismo origen y protección de caché. Job remoto, cierre de cuentas,
verificación profesional y contenido jurídico conservan sus propios contratos.
No declarar C02 Done mientras falten operación/retención y negativos del proveedor.

## Implementación propuesta

A4 entrega preflight seguro y pruebas; A5 entrega plantillas y contrato de correo;
A2 entrega dry-run/purga local y contrato operativo; A0 integra, mantiene migración
única y registra decisiones. El trabajo parte del commit común local; archivos
exclusivos en el checkout coordinador, sin copiar secretos o alterar cambios ajenos.

Entrega revisable: [correo](identity-email-operations.md),
[retención](identity-retention-operations.md),
[preflight](../operations/identity-real-readiness.md).
No se ha contratado SMTP, cambiado DNS/Auth, aplicado grants/migración remota,
creado usuario real, enviado correo o programado tarea de producción.

Fuentes verificadas: [sesiones Supabase](https://supabase.com/docs/guides/auth/sessions),
[SMTP Supabase](https://supabase.com/docs/guides/auth/auth-smtp),
[plantillas](https://supabase.com/docs/guides/auth/auth-email-templates),
[SMTP Resend](https://resend.com/docs/send-with-smtp),
[planes](https://resend.com/pricing).
