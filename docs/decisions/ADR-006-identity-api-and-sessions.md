# ADR-006 — Identidad mediada por API y sesión de aplicación

Status: Approved, 2026-10-12. Implementación pendiente.

## Context

Arturo aprobó el checkpoint Identity y el modelo/matriz entregados, y autorizó
continuar proactivamente. La aprobación selecciona recomendaciones A IC-01–IC-06.

## Decision

Correo/contraseña, confirmación y recuperación no enumerativa. Una identidad
multifunción, práctica propia y un despacho activo por abogado. Relación de
servicio contextual con participantes/asignaciones explícitas. Administración de
miembros separada de contenido jurídico. Salida retira facultades profesionales
derivadas sin eliminar por inferencia participación independiente como cliente.

Supabase Auth conserva autenticación. FastAPI custodia tokens de proveedor; cookie
opaca HttpOnly/Secure y protección CSRF. MFA TOTP requerido en acciones profesionales
privadas y administrativas. Aplicación: 12 horas absolutas y 30 minutos de
inactividad; revocación impide siguiente petición privada. JWT objetivo 15 minutos,
sin modificar configuración remota por inferencia.

Datos privados por FastAPI hacia PostgreSQL, con identidad transaccional, permisos
por objeto/acción y rol runtime mínimo sujeto a RLS. Sin acceso privado directo
desde navegador. C01 y contratos preceden distribución de código.

## Consequences

Custodia cifrada y renovación serializada requieren almacenamiento de servidor;
los tokens no entran en respuestas, URLs, logs o artefactos. Las funciones nativas
Pro no se presumen en Free. Correo público y recuperación de MFA necesitan su
configuración/contrato independiente; no se abren rutas de bypass.

Retención D-032: cuenta cerrada y evidencia mínima de membresía terminada 30 días,
auditoría 90 días. Borrado o anonimización posterior. Datos jurídicos, verificación
profesional, hosting, presupuesto y revisión legal siguen en sus checkpoints.

## Verification

Diseño revisado documentalmente; implementación, pruebas reales, proveedor, CI
remoto y despliegue aún no verificados. C02 no se considera terminada por aprobar
este ADR. Fuente de autorización: respuesta de Arturo en esta conversación.
