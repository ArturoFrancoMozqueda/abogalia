# Registro de servicios de Abogalia

Actualizado: 2026-10-12, America/Mexico_City. Contiene destinos y estados comprobados, sin secretos. Identidad administrativa aprobada: posprojectsupport; en GitHub se conserva la cuenta personal existente.

| Servicio | Destino | Identificador comprobado | Estado |
|---|---|---|---|
| GitHub | ArturoFrancoMozqueda/abogalia | Repositorio público existente | Monorepo implementado localmente; CI preparado, sin commit ni push |
| Desarrollo local | React/FastAPI de Abogalia | Web 127.0.0.1:5190, API 127.0.0.1:8090 | Base técnica verificada; sin integración de Auth/base |
| Supabase | Organización Abogalia | `jdmkzzkgnzwldthjqtgx` | Creada; Free, `tier_free`, comprobado por conector |
| Supabase | Proyecto abogalia, Free, us-east-1 | `xggefantvuwpilksfdoy` | Creado por Arturo; organización, región y estado ACTIVE_HEALTHY verificados por conector |
| Cloudflare | Cuenta y frontend propios | Pendiente | Sin configurar |
| Fly | Organización y API propias | Pendiente | Sin configurar ni máquinas contratadas |
| Resend | Equipo y dominio propios | Pendiente | Sin configurar |
| Vercel | Sin selección para Abogalia | No aplica | Panel disponible; no se interpreta como cambio de hosting |

## Acceso comprobado

La organización Supabase se creó en el panel con la sesión administrativa de posprojectsupport y plan Free, US$0/mes. El conector `get_organization` devolvió su nombre y plan usando el identificador de esta tabla sin pedir reautenticación. `list_organizations` aún devolvió solo Kova; esa lista incompleta no es prueba de falta de acceso. Confirmar cada destino mediante su identificador y respuesta directa.

El método `get_cost` no estuvo disponible en el servidor del conector. No se confirma ni crea un proyecto por ese método, ni se inventa un ID de confirmación. La creación puede continuar por el panel con costo y región revisados; el usuario deberá completar una nueva contraseña de base si el formulario lo exige.

Formulario preparado tras aprobar D-029: organización Abogalia FREE, proyecto abogalia, East US (North Virginia) us-east-1; Data API habilitada, exposición automática de tablas desactivada y RLS automático activado. Integración opcional de GitHub sin seleccionar. El agente no generó ni introdujo contraseña ni envió el formulario. Arturo completó la creación y avisó «Listo, ya creé el proyecto».

Verificación posterior: `get_project` devolvió `xggefantvuwpilksfdoy`, nombre abogalia, organización `jdmkzzkgnzwldthjqtgx`, región `us-east-1` y `ACTIVE_HEALTHY`. `get_organization` confirmó Free. El panel muestra Healthy, North Virginia, cómputo Nano, sin repositorio GitHub conectado ni migraciones. URL pública del proyecto: https://xggefantvuwpilksfdoy.supabase.co; [panel](https://supabase.com/dashboard/project/xggefantvuwpilksfdoy). Las consultas directas funcionaron con la conexión existente, sin reautenticación; la lista general de proyectos todavía omitía el nuevo destino. No se promete ausencia permanente de login.

`list_tables` para public devolvió cero tablas. Una consulta de catálogo confirmó el event trigger `ensure_rls` habilitado. La revisión de privilegios predeterminados encontró que postgres no concede SELECT/INSERT/UPDATE/DELETE a anon/authenticated para nuevas tablas public, pero conserva otros privilegios, incluidos TRUNCATE; supabase_admin conserva también permisos CRUD predeterminados. No interpretar el checkbox de exposición como eliminación de todos los permisos ni RLS como protección de todas las operaciones. Antes de crear tablas, el diseño de Identity y sus migraciones deben definir explícitamente propietario, grants/revokes y políticas, con pruebas de aislamiento. No se modificaron esos permisos en esta verificación.

Supabase Auth aprobado como proveedor, D-028, todavía sin integración de aplicación. Proyecto vacío creado no equivale a conexión de la aplicación ni a autorización de usuarios.

## Límites de operación

La pestaña Supabase original apuntaba al SQL Editor de Kova Production y la de Fly a secretos de `pos-project-backend`. No se ejecutaron consultas, cambios de secretos ni configuración en esos recursos. La sesión existente de Vercel no selecciona ese hosting para Abogalia. Arturo creó la contraseña y el proyecto vacío de Abogalia; el agente no leyó ni guardó esa contraseña. No se han creado invitaciones, integraciones de GitHub, máquinas ni despliegues.

La aplicación local y su workflow de CI se prepararon tras aprobar D-030. [Verificación](local-foundation-verification.md). No se han publicado cambios ni ejecutado CI remoto; los costos de GitHub Actions se revisarán al operar, sin presumir que el cupo se multiplica por repositorio.

Guardar secretos únicamente en archivos locales excluidos o gestores del proveedor y CI. Este repositorio es público: nunca incorporar contraseñas, tokens, claves privadas ni información de clientes. No usar destinos de Kova como valor por defecto o sustitución cuando falte un recurso de Abogalia.
