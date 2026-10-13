# Verificación web — Identity C02

Fecha: 2026-10-12. Autor A5; revisores A0/A2. Worktree asignado
`/Users/arturo/.codex/worktrees/abogalia-identity-web/abogalia`, referencia base
`1eaf758d776a77e0507629c9e33c6c1d969bee79`. Cambios locales sin commit.
Contrato: [HTTP Identity](../contracts/identity-api.md) y
[recorridos UX](../ux/identity-flows.md).

## Resultado local

Implementadas `/acceso`, `/registro`, `/recuperar` y `/cuenta`. Registro y
recuperación aceptan únicamente la respuesta no enumerativa del contrato, sin
simular entrega de correo. Confirmación y cambio de contraseña usan códigos
en formulario/cuerpo JSON; no callbacks con credenciales en URL. Cuenta consulta
sesión y factores, configura TOTP manualmente y verifica challenge/código con API.
No renderiza el QR/SVG del proveedor: descarta ese campo y usa texto de clave/URI
solo dentro del flujo Auth privado autorizado. No capturas de ese estado.

MFA no otorga rol ni habilitación profesional. La cuenta no presenta contextos
o permisos ausentes del contrato. Recuperación y desinscripción de factores quedan
cerradas; no hay bypass. Práctica propia, despacho y relaciones de negocio no están
implementados en la web de esta entrega.

Cliente mismo origen, cookies gestionadas por navegador y CSRF solo en memoria:
GET bootstrap y `X-CSRF-Token`; no lectura de cookie Auth por JavaScript ni tokens
Supabase. Login/MFA/logout/recuperación reinician CSRF y hacen bootstrap nuevo, sin
repetir la mutación. Cuerpos sensibles nunca van a parámetros de navegación,
almacenamiento web o logs. Peticiones tienen timeout; formularios cancelan el
trabajo pendiente y limpian entradas/referencias al abandonar la ruta o pagehide.
La cancelación no promete revertir efectos ya aceptados por servidor.

Cuenta navega a acceso solo si `/session` devuelve `authenticated:false`; fallo
de red/503 muestra error y reintento consciente. Logout fallido oculta datos
privados locales y no afirma cierre global; informa posibilidad de fallo parcial.
Recuperación interrumpida advierte que la contraseña puede haberse actualizado.
Restauración desde caché de navegación vuelve a consultar la sesión.
Un 401 AUTHENTICATION_REQUIRED al consultar factores o completar MFA también
limpia correo, factores y configuración local; no conserva datos privados por
haber recibido antes una sesión válida. Red/503 no se confunde con sesión ausente.

Accesibilidad: etiquetas persistentes, tipos/autocomplete, soporte a pegado y
gestores, códigos como texto de seis dígitos con ceros, mensajes anunciados,
foco en error/resultado, contraseña repetida asociada a error, confirmación de
cierre global con foco y cancelación, estilos responsivos y contraste de mensajes.
La validación básica usa restricciones HTML nativas; errores del servidor son
generales para no revelar identidad o datos del proveedor.

## Archivos modificados

- `apps/web/app/lib/auth.ts`: tipos, validación de respuestas, fetch y CSRF.
- `apps/web/app/components/auth-form.tsx`: formularios y estructura accesibles.
- `apps/web/app/routes/login.tsx`, `register.tsx`, `recover.tsx`, `account.tsx`.
- `apps/web/app/routes.ts`: cuatro rutas de identidad.
- `apps/web/app/styles.css`: estilos Auth conservando diseño inicial.
- `apps/web/app/routes/home.tsx`: enlaces a entrar/crear cuenta.
- `docs/operations/identity-web-verification.md`: esta evidencia.

Sin cambios a backend, configuración global, package manifests, lockfiles o CI.
Dependencias existentes reproducidas con `pnpm install --frozen-lockfile
--ignore-scripts`; no dependencia nueva ni cambio de versión. Runtime Node
proporcionado por el entorno, Node 24.19.0 / pnpm 11.25.0.

## Comprobaciones ejecutadas

| Comprobación | Resultado | Límite |
|---|---|---|
| `pnpm check` | Pasa: lint Biome, typegen/TypeScript y build | No prueba proveedor ni autorización del backend |
| Build público | Portada `/` prerenderizada y fallback SPA; Auth en chunks | Hosting/fallback y caché privada aún requieren operación aprobada |
| Cliente Auth en Node con fetch sintético | Seis comprobaciones pasan | Prueba aislada temporal, sin fixture persistido; no cuenta como E2E |
| Revisión de fuentes Auth | Sin localStorage, sessionStorage, document.cookie, console o dangerouslySetInnerHTML | Revisión acotada; no scanner exhaustivo de historial/artefactos |
| Revisión de portada HTML | Conserva texto público; no contiene cuenta ni configuración MFA | No se usó identidad real ni render privado |

Las seis comprobaciones sintéticas cubren sesión ausente, error proveedor
redactado, POST rechazado sin retry y con credenciales/CSRF acordados, bootstrap
tras rotación login, rechazo de SessionView inválida y descarte de QR/SVG.
Se ejecutaron en memoria con Node `--experimental-transform-types`, solo reporte
de éxito, sin imprimir cuerpos ni credenciales. Primer intento de harness basado
en módulo JS de TypeScript no estuvo disponible; se corrigió usando transformación
de tipos de Node. No se instaló herramienta por esa limitación.

Skill React best practices aplicada: componentes fuera de render, hooks con
dependencias, limpieza de efectos/peticiones, estados tipados, accesibilidad y
sin librerías extra. Referencia de navegación verificada:
[React Router useNavigate](https://reactrouter.com/api/hooks/useNavigate).
Timeout/cancelación usan APIs del navegador verificadas en
[AbortSignal.any](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/any_static)
y [AbortSignal.timeout](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/timeout_static);
requieren navegador moderno. No polyfill/dependencia añadida.

## Pendientes y riesgos

A0 realiza prueba integrada en navegador con API local real; teclado/lector de
pantalla y revisión visual también pendientes. Flujos Supabase, correo/plantillas,
OTP/TOTP, revocación proveedor/global y persistencia/custodia de backend no fueron
ejecutados por A5. Backend ausente o proveedor sin configurar debe responder con
fallo visible y honesto, no demo ni éxito artificial. Antes de publicar se requiere
revisión independiente, scanner redactado y controles de secretos de A0/A2.
Retención aprobada D-032: 30 días tras cierre de cuenta y 30 días para evidencia
mínima tras fin de membresía; 90 días para auditoría de acceso, seguidos de
borrado/anonimización. No significa guardar tokens o historia de sesión 90 días:
sesiones mantienen 12 horas absolutas y 30 minutos de inactividad, con eliminación
de tokens al revocar/expirar. Su aplicación corresponde al contrato de datos/API;
esta UI no crea persistencia. Contenido jurídico/expedientes y evidencia
profesional conservan retención pendiente. Términos/aviso y confianza C03 siguen
sus decisiones propias;
LEGAL REVIEW REQUIRED antes de datos reales. Sin CI remoto, despliegue,
provisionamiento, acceso externo a proyectos, lectura de `.env`, secretos o Kova.
