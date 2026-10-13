# Instrucciones para agentes de Abogalia

Estas reglas aplican a todo el repositorio. La instrucción expresa del usuario es:
**jamás filtrar secretos, comprometer credenciales ni exponer sus valores**.

## Contexto obligatorio

Antes de trabajar, leer README.md, docs/27_development_plan_agents.md,
docs/decisions/decision-log.md y el checkpoint de la capacidad asignada.
Consultar docs/operations/service-registry.md solo para destinos no secretos.
Approved no equivale a Implemented. Las propuestas históricas no autorizan cambios.

Stack aprobado: monorepo Abogalia, apps/web con React Router sobre Vite y
TypeScript, apps/api con FastAPI, Supabase Auth y PostgreSQL propio. La base local
y el proyecto vacío existen; login, permisos y negocio todavía no están implementados.
Hosting, presupuesto, pagos, modelo de tenants y proveedor de IA siguen pendientes.

## Secretos y datos

- No leer ni mostrar valores de .env, credenciales, tokens, contraseñas, cookies,
  claves privadas, cabeceras Authorization o cadenas de conexión con contraseña.
  Usar solo nombres de variables, ejemplos vacíos y estado presente/ausente.
- No solicitar secretos por chat ni incluirlos en prompts, mensajes entre agentes,
  herramientas con salida visible, capturas, logs, fixtures, documentación, issues,
  PRs, commits, artefactos, bundles del navegador o reportes de pruebas.
- No ejecutar volcados de entorno, shell tracing, diagnósticos HTTP que impriman
  cabeceras/cookies o búsquedas recursivas indiscriminadas en archivos sensibles.
  Excluir .env, gestores de credenciales y datos privados de las lecturas habituales.
- Los secretos de runtime se inyectan desde gestores del proveedor o mecanismos
  locales excluidos de Git. Nunca convertirlos en argumentos visibles de comandos,
  URLs, variables públicas VITE_* o respuestas API. No abrir pantallas de claves.
- Una clave publishable identificada por el proveedor como pública no es un secreto;
  su uso necesita el contrato aprobado. Nunca confundirla con service_role/secret.
  Las credenciales de sesión se usan solo en el flujo de autenticación aprobado,
  sin volcarlas en salidas, logs, URLs o lugares ajenos a ese flujo.
- No acceder a datos reales de clientes para desarrollar. Usar datos sintéticos
  aislados. No enviar información jurídica a IA ni a telemetría sin diseño aprobado.
- Kova queda fuera del alcance: no leer sus secretos o datos, modificar sus recursos
  ni reutilizar sus credenciales. Confirmar producto, entorno y destino antes de
  cualquier operación externa; un conector autenticado no autoriza una mutación.
- Ante posible exposición: detener publicación y la operación afectada, informar
  solo proveedor/variable/ubicación y coordinar revocación o rotación mediante el
  responsable autorizado. Nunca repetir el valor, ni siquiera parcialmente.
  Borrar una línea de Git no revoca una credencial. No reescribir historia ni borrar
  evidencia por cuenta propia.

## Autorización y diseño

Implementar una capacidad importante solo cuando su checkpoint esté aprobado por
Arturo. Debe contener: Lo que entiendo, Decisiones tomadas, Decisiones pendientes,
Diseño propuesto, Datos afectados, Seguridad, Impacto futuro e Implementación
propuesta. Una aprobación previa suficiente no se vuelve a solicitar.

No elegir silenciosamente permisos, roles, tenencia, datos, UX sustantiva, precios,
pagos, retención, proveedores, gasto o tratamiento de IA. Preparar alternativas y
preguntas para el coordinador; agrupar como máximo 5–8 decisiones por sesión.
Si la decisión pendiente bloquea código, avanzar solo con diseño o investigación
que no dependa de ella. Validación jurídica mexicana: LEGAL REVIEW REQUIRED.

Antes de tablas: modelo conceptual, propiedad, relaciones, estados, clasificación,
historial y retención aprobados. No usar una entidad genérica case para solicitud,
consulta, reserva y asunto. No otorgar permisos amplios para resolver un error.
No desactivar RLS ni usar service_role como solución universal a autorización.

IA actual: solo resumen revisable a petición y borrador editable con copia manual;
original conservado, sin envío automático. Proveedor, límites y tratamiento aún
pendientes. OCR, embeddings e indexación documental con IA están aplazados.

## Colaboración y entrega

- Recibir una orden de trabajo con capacidad, archivos propios, dependencias,
  checkpoint y criterios verificables. No iniciar otros agentes sin autorización
  explícita para esa tarea. No contactar terceros ni otras tareas por inferencia.
- Trabajar en la rama/worktree asignados. Un worktree separa archivos, no permisos
  ni secretos. No resetear, limpiar, sobreescribir o descartar cambios ajenos.
- No editar fuera del alcance sin coordinación. Un único responsable controla
  migraciones; el coordinador controla integración, lockfiles y configuración global.
- Consultar las skills aplicables y documentación oficial actual antes de usar un
  proveedor o instalar una dependencia. Mantener versiones fijadas y lockfiles.
- Pruebas de autorización, aislamiento y estados críticos deben fallar si se rompe
  el control. No declarar terminada una capacidad por una pantalla o un mock.
- Revisar secretos con salida redactada antes de commit/push y publicación de
  artefactos. Los escáneres no sustituyen revisión; no ignorar alertas para publicar.
- Entregar archivos cambiados, decisiones aplicadas, pruebas ejecutadas y resultados,
  límites y riesgos, sin datos sensibles. Declarar mocks y verificaciones pendientes.
  No afirmar CI remoto, despliegue o restauración si no se ejecutaron.
- No provisionar recursos, aplicar migraciones remotas, desplegar, elevar privilegios,
  transferir repositorios ni contratar servicios fuera del alcance aprobado.

## Estado del repositorio al comenzar

La fundación y documentos tienen cambios locales sin publicar. Antes de distribuir
implementaciones, el coordinador debe revisar el estado y preparar una referencia
común segura. No crear worktrees desde una rama remota que omita la base local ni
usar git add . sin revisar qué se incorpora.

