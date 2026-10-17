# Legalia — borrador profesional privado

2026-10-15. Incremento de C03 autorizado por D-040/D-041, integrado en la rama
codex/identity-design y revisado por los agentes A2/A3, A4 y A1/A5.

La web permite preparar, editar y retirar un perfil privado con su práctica
inactiva. FastAPI exige sesión vigente y MFA, autoriza el propietario y aplica
CSRF, versiones concurrentes y validación de campos. Perfil, contexto y eventos
se guardan en una transacción; una revocación en su frontera revierte el negocio.
La renovación de credenciales ya consumida conserva su custodia ante fallos.

El esquema incorpora FORCE RLS y permisos limitados al runtime existente. Los
eventos mínimos no copian el formulario y sobreviven al borrado de su agregado.
La migración Supabase fue creada con CLI y probada contra PostgreSQL aislado;
no se ha aplicado en el proyecto remoto. Revisión, publicación, invitaciones,
despachos y membresías permanecen pendientes; no hay concesiones reales a revisores.

Validación de integración: 484 pruebas API/SQL/herramientas pasan con PostgreSQL
temporal y transporte Auth simulado. Lint, formato, dependencias e importación API
pasan; lint, tipos y build web pasan. Scanner8.30.1 de fuentes/historial y artefacto
web sin hallazgos. Esto no acredita CI remoto, despliegue, recorrido autenticado
real, correo entregado o revocación remota.

C02 tiene conexión runtime real con TLS verify-full y configuración privada
validada; sus flags de activación y correo siguen desactivados. Retención30/90
está aprobada, pero falta coordinar la purga del agregado C03 con la cuenta y
comprobar la retirada Auth. La FK impide borrar prematuramente una cuenta con
perfil; el ejecutor de retención vigente sigue limitado al entorno sintético.
No se afirma eliminación periódica ni restauración verificada. Arturo conserva
la responsabilidad operativa aprobada. LEGAL REVIEW REQUIRED.
