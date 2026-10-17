# C03 — Verificación del frontend privado

Fecha: 2026-10-15. Base de revisión `fe75a8b1f17b`. Alcance: las rutas
`/profesional` y `/profesional/contextos`, formulario privado y cliente HTTP C03.
PC-01..05 A y Q-C03-01..03 A aprobadas, D-040/D-041. No se habilitan revisión,
publicación, despacho, invitaciones, clientes ni actores reales.

## Hallazgo y corrección

Se reprodujo que `professionalMessage(new AuthError("constructor", 503))`
devolvía una función heredada del objeto de mensajes, en vez de texto. Un código
inesperado podía romper el renderizado de la alerta. El cliente ahora consulta
únicamente propiedades propias con `Object.hasOwn`; códigos desconocidos producen
el mensaje genérico fijo, sin repetir el mensaje del proveedor. No cambia contrato,
permisos o UX sustantiva. A0 aplicó el mismo control al constructor AuthError;
el harness verifica ambos mensajes fijos sin editar aquí el transporte Auth. No se modificaron componentes/rutas para
generar trabajo adicional.

## Revisión de flujos y accesibilidad

| Recorrido/control | Evidencia de fuente y alcance |
|---|---|
| Entrada | SessionView C02 false dirige a acceso; aal1 ofrece MFA en cuenta antes del GET profesional. Un error de red no se interpreta como logout |
| Privacidad | 401/MFA_REQUIRED elimina agregado y campos visibles; desmontaje/pagehide cancela solicitudes y limpia vista. Generación de solicitud ignora respuestas obsoletas; no hay localStorage ni logging de campos |
| Guardado | POST solo nombre/área privados; PATCH añade versión del perfil. Campos etiquetados, área opcional, límites 120/240 y ayuda asociada; valores se muestran como texto React |
| Concurrencia | Ref de exclusión y controles disabled impiden envío simultáneo. Error 409 bloquea escrituras hasta actualización explícita; no reintenta ni sobrescribe automáticamente |
| Retiro | Confirmación separada con foco al botón; solicitud contiene ambas versiones. Tras éxito, perfil withdrawn y práctica closed sin restauración/actividad. Mensajes distinguen plazos 30/90 y borrado físico no confirmado |
| Lectura | Actualizar solo obtiene sesión/agregado; no guarda ni toca timestamps desde cliente. Ambas pantallas leen agregado propio, sin selector que conceda autoridad |
| Errores | Alertas con role=alert, tabIndex=-1 y foco; éxito/carga role=status. 503 informa indisponibilidad, no éxito; timeout pide actualizar sin afirmar que la escritura no ocurrió |
| Navegación | Enlaces reales a perfil/contextos/cuenta/acceso, orden nativo de teclado; estilos de foco existentes reutilizados. No se cambió configuración global |

Se aplicó la skill React Best Practices: reglas de hooks, dependencias/cleanup,
respuestas obsoletas, ausencia de estado compartido con PII, TypeScript y controles
HTML accesibles. La inspección de fuente no acredita por sí sola lector de pantalla,
foco real, layout, teclado completo, BFCache ni carreras en navegador.

## Harness reproducible del cliente

Ejecutar desde la raíz con Node 24 y pnpm fijados ya disponibles. No instala
paquetes ni carga dotenv. Compila únicamente los módulos del cliente en un directorio
temporal y sustituye fetch en el proceso por respuestas públicas sintéticas. No
conecta a web/API/proveedor, no lee cookies ni introduce credenciales reales.
Salida: conteo de casos, sin cuerpos ni valores de cabeceras.

```sh
task_c03_qa_dir=$(mktemp -d /tmp/legalia-professional-web-qa.XXXXXX)
pnpm --filter @abogalia/web exec tsc --ignoreConfig app/lib/professional-contexts.ts app/lib/auth.ts --target ES2022 --module commonjs --lib ES2022,DOM --skipLibCheck --outDir "$task_c03_qa_dir/compiled"
cat > "$task_c03_qa_dir/check.cjs" <<'JS'
const assert = require('node:assert/strict');
const { AuthError, authMessage } = require(process.argv[2] + '/auth.js');
const api = require(process.argv[2] + '/professional-contexts.js');
let passed = 0;
const check = async (test) => { await test(); passed++; };
const signal = new AbortController().signal;
const empty = { profile: null, practice_context: null };
const draft = {
  profile: { id: 'public-synthetic-profile', version: 2, state: 'draft',
    fields: { display_name: 'PUBLIC SYNTHETIC', declared_area: null },
    publication: 'private', review: null, allowed_actions: ['edit', 'withdraw'] },
  practice_context: { id: 'public-synthetic-practice', version: 1,
    kind: 'practice', title: 'PUBLIC SYNTHETIC', state: 'preparing',
    capabilities: [], allowed_actions: [] },
};
const reply = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { 'Content-Type': 'application/json' },
});
let calls = [];
const successful = () => {
  calls = [];
  global.fetch = async (path, options) => {
    calls.push({ path, options });
    return reply(path === '/api/auth/csrf'
      ? { csrf_token: 'PUBLIC_SYNTHETIC_NOT_A_CREDENTIAL' } : draft);
  };
};
(async () => {
  await check(() => assert.deepEqual(api.readPrivateDraft(empty), empty));
  await check(() => assert.equal(api.readPrivateDraft(draft).profile.state, 'draft'));
  await check(() => assert.equal('unexpected' in api.readPrivateDraft({ ...draft, unexpected: 'public' }), false));
  await check(() => assert.throws(() => api.readPrivateDraft({ ...draft,
    practice_context: { ...draft.practice_context, capabilities: ['professional_work'] } })));
  await check(() => assert.throws(() => api.readPrivateDraft({ ...draft,
    practice_context: { ...draft.practice_context, state: 'closed' } })));
  await check(() => assert.throws(() => api.readPrivateDraft({ ...draft,
    profile: { ...draft.profile, version: 0 } })));
  await check(() => assert.throws(() => api.readPrivateDraft({ ...draft,
    profile: { ...draft.profile, version: true } })));
  await check(() => {
    for (const code of ['constructor', '__proto__', 'toString', 'UNLISTED_CODE']) {
      const message = api.professionalMessage(new AuthError(code, 503));
      assert.equal(typeof message, 'string');
      assert.equal(message, 'No pudimos completar la solicitud. Actualiza antes de continuar.');
      assert.equal(authMessage(new AuthError(code, 503)), 'No pudimos completar la solicitud. Inténtalo de nuevo.');
    }
  });
  await check(async () => {
    successful(); await api.requestPrivateDraft(signal);
    assert.equal(calls.length, 1);
    assert.equal(calls[0].path, '/api/professional/profile');
    for (const [key, value] of Object.entries({ credentials: 'same-origin',
      cache: 'no-store', redirect: 'error', referrerPolicy: 'no-referrer' }))
      assert.equal(calls[0].options[key], value);
  });
  await check(async () => {
    successful(); await api.requestPrivateDraft(signal, 'POST', draft.profile.fields);
    assert.equal(calls.length, 2);
    assert.equal(calls[0].path, '/api/auth/csrf');
    assert.equal(calls[1].options.headers['X-CSRF-Token'], 'PUBLIC_SYNTHETIC_NOT_A_CREDENTIAL');
    assert.deepEqual(JSON.parse(calls[1].options.body), draft.profile.fields);
  });
  await check(async () => {
    successful(); const body = { expected_version: 2, fields: { declared_area: 'PUBLIC SYNTHETIC' } };
    await api.requestPrivateDraft(signal, 'PATCH', body);
    assert.equal(calls[1].options.method, 'PATCH');
    assert.deepEqual(JSON.parse(calls[1].options.body), body);
  });
  await check(async () => {
    successful(); const body = { expected_version: 2, expected_context_version: 1 };
    await api.requestPrivateDraft(signal, 'POST', body, true);
    assert.equal(calls[1].path, '/api/professional/profile/withdraw');
    assert.deepEqual(JSON.parse(calls[1].options.body), body);
  });
  for (const [code, status] of [['VERSION_CONFLICT', 409], ['AUTHENTICATION_REQUIRED', 401],
    ['MFA_REQUIRED', 403], ['PROFESSIONAL_UNAVAILABLE', 503], ['INVALID_REQUEST', 422]]) {
    await check(async () => {
      let count = 0;
      global.fetch = async () => { count++; return reply({ error: { code,
        message: 'PUBLIC_SYNTHETIC_UPSTREAM_DETAIL' } }, status); };
      await assert.rejects(api.requestPrivateDraft(signal), (error) =>
        error.code === code && !api.professionalMessage(error).includes('UPSTREAM_DETAIL'));
      assert.equal(count, 1);
    });
  }
  await check(async () => {
    let writes = 0;
    global.fetch = async (path) => path === '/api/auth/csrf'
      ? reply({ csrf_token: 'PUBLIC_SYNTHETIC_NOT_A_CREDENTIAL' })
      : (writes++, reply({ error: { code: 'VERSION_CONFLICT' } }, 409));
    await assert.rejects(api.requestPrivateDraft(signal, 'PATCH', { expected_version: 2, fields: { display_name: 'PUBLIC SYNTHETIC' } }));
    assert.equal(writes, 1);
  });
  await check(async () => {
    let calls = 0;
    global.fetch = async () => { calls++; return reply({ error: { code: 'AUTH_UNAVAILABLE' } }, 503); };
    await assert.rejects(api.requestPrivateDraft(signal, 'POST', draft.profile.fields));
    assert.equal(calls, 1);
  });
  await check(async () => {
    const cancelled = new AbortController(); cancelled.abort(); let writes = 0;
    global.fetch = async (path) => {
      if (path !== '/api/auth/csrf') writes++;
      return reply({ csrf_token: 'PUBLIC_SYNTHETIC_NOT_A_CREDENTIAL' });
    };
    await assert.rejects(api.requestPrivateDraft(cancelled.signal, 'POST', draft.profile.fields));
    assert.equal(writes, 0);
  });
  await check(async () => {
    let count = 0; global.fetch = async () => { count++; throw new TypeError('PUBLIC_SYNTHETIC_RAW_NETWORK'); };
    await assert.rejects(api.requestPrivateDraft(signal)); assert.equal(count, 1);
    assert.equal(api.professionalMessage(new TypeError('PUBLIC_SYNTHETIC_RAW_NETWORK')).includes('RAW_NETWORK'), false);
  });
  await check(async () => {
    global.fetch = async () => reply({ profile: draft.profile, practice_context: null });
    await assert.rejects(api.requestPrivateDraft(signal));
  });
  console.log('Synthetic client checks passed:', passed, '; mocked fetch only');
})().catch(() => { console.log('Synthetic client check failed at case:', passed + 1); process.exitCode = 1; });
JS
node "$task_c03_qa_dir/check.cjs" "$task_c03_qa_dir/compiled"
```

Resultado de esta tanda: **22 comprobaciones pasan**. Cubren respuesta vacía y
privada, proyección de campos, rechazo de capacidades/estados/versiones inválidos,
códigos heredados/desconocidos, opciones same-origin/no-store/no-referrer/redirect,
CSRF, POST/PATCH, CAS de retiro, 409/401/MFA403/503/422, no retry, fallo CSRF sin
mutación, cancelación sin escritura, redacción de error de red y agregado incompleto.
La marca sintética en la cabecera no es una credencial y no se imprime.

## Navegador y límites

A0 verificó en la tanda anterior el recorrido anónimo real local
`/profesional` → `/acceso`, con Identity explícitamente apagada y sin archivo
privado cargado. Ese resultado conserva su alcance y no se vuelve a atribuir a
este harness. En esta revisión no se ejecutó un recorrido positivo de formulario,
MFA o retirada en navegador ni Auth real, envío, DB remota o migración.

Las comprobaciones de cliente no prueban transacciones, RLS, propiedad de filas,
revocación del proveedor o ejecución de retención. API/SQL disponen de evidencia
separada. La migración C03 remota y ejecución periódica siguen pendientes según el
estado coordinado; el frontend no las presenta como ejecutadas. No se modificaron
dependencias, lockfiles, configuración global, cuenta o transporte Auth.

Comprobación de calidad de esta tanda: `pnpm check` pasa (lint, tipos y build con
las dos rutas). El harness documental incluye la regresión de AuthError/authMessage
incorporada por A0, además de professionalMessage.
