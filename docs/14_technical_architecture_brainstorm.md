# Brainstorming de Arquitectura Técnica

## Propósito

React para frontend y FastAPI como backend están aprobados en D-025 y [ADR-001](decisions/ADR-001-react-fastapi.md). Este documento conserva preguntas de la arquitectura completa; no constituye aprobación de proveedores, identidad o datos.

La arquitectura técnica se decidirá mediante sesiones de diseño, pruebas de concepto y Architecture Decision Records.

La recomendación concreta actual está en [checkpoint de suite inicial pequeña](checkpoints/platform-foundation-low-cost.md): React en Cloudflare Free, una API FastAPI pequeña en Fly y Supabase/Resend Free en recursos propios; Vercel y Render se conservan como alternativas. Estado de servicios Discussing, D-026; la selección de React + FastAPI está Approved. La [comparación actualizada](26_services_and_tiers.md) distingue cuotas de hosting y consumo. No hay implementación. La propuesta previa de backend TypeScript integrado en Workers queda como alternativa.

La comparación debe incorporar las lecciones verificadas de Kova solicitadas por Arturo: [evidencia, opciones y orden de preparación](25_kova_lessons_and_setup_order.md). Su arquitectura es React/Vite + FastAPI + Supabase PostgreSQL, con autenticación propia; no se asume Supabase Auth. La experiencia de Kova informa la decisión, pero no aprueba copiar sus proveedores o contratar recursos. Los dos flujos de IA y React + FastAPI están aprobados; identidad, datos y servicios siguen pendientes.

## Principios

- Evitar decisiones irreversibles.
- Diseñar por dominios.
- Preferir simplicidad operativa.
- Escalar cuando exista evidencia.
- Separar operación transaccional y analítica.
- Instrumentar desde el inicio.
- Priorizar seguridad.
- Controlar costos.
- Automatizar despliegue y pruebas.

## Preguntas de arquitectura

### Aplicaciones

- ¿Una aplicación o varias?
- ¿Web responsive?
- ¿Aplicaciones móviles?
- ¿Portal cliente?
- ¿Portal abogado?
- ¿Portal despacho?
- ¿Admin independiente?

### Backend

- ¿Monolito modular?
- ¿Servicios?
- ¿Serverless?
- ¿Contenedores?
- ¿Arquitectura híbrida?
- ¿Qué dominios requieren aislamiento?
- ¿Qué capacidades requieren colas?

### Lenguajes

- ¿TypeScript?
- ¿Python?
- ¿Java?
- ¿Go?
- ¿Combinación?
- ¿Qué experiencia tiene el equipo?
- ¿Qué costo operativo implica?

### Datos

- ¿PostgreSQL?
- ¿Base documental?
- ¿Motor de búsqueda?
- ¿Warehouse?
- ¿Lakehouse?
- ¿Event store?
- ¿Vector database?
- ¿Cache?

### Integraciones

- Pagos.
- Calendario.
- Correo.
- WhatsApp.
- Videollamada.
- Firma.
- Facturación.
- Verificación.
- Identidad.
- Almacenamiento.

### Infraestructura

- AWS.
- Azure.
- Google Cloud.
- Vercel.
- Fly.io.
- Supabase.
- Kubernetes.
- Plataformas administradas.
- Multi-cloud.

### Seguridad

- IAM.
- MFA.
- SSO.
- Secrets.
- KMS.
- WAF.
- SIEM.
- DLP.
- Backups.
- DR.

### Observabilidad

- Logs.
- Métricas.
- Trazas.
- Auditoría.
- Alertas.
- SLO.
- Error tracking.
- Product analytics.

## Pruebas de concepto sugeridas

- Auth multi-tenant.
- Reserva concurrente.
- Pago y reembolso.
- Agenda e integración.
- Enrutamiento de notificaciones.
- Almacenamiento seguro.
- Auditoría.
- Event tracking.
- Search.
- Matching.
- IA con datos anonimizados.

## ADRs necesarios

- Arquitectura de aplicación.
- Estrategia multi-tenant.
- Lenguaje backend.
- Base de datos.
- Almacenamiento.
- Integración de pagos.
- Mensajería.
- Analítica.
- Identidad.
- Despliegue.
- Observabilidad.
- IA.
