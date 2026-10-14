# Configuración privada de la publishable — Legalia

Destino vigente: proyecto `spohytnxscljtitvmdab`. D-039/D-040 aprobados.
Este procedimiento no habilita Identity ni acredita correo/revocación reales.

1. En el panel del proyecto correcto, el operador abre Settings → API Keys y
   copia únicamente la clave identificada como **Publishable**, con prefijo
   `sb_publishable_`. El agente no abre esta pantalla ni inspecciona su contenido.
2. En su editor privado, abre `/Users/arturo/Documents/repos/abogalia/.env`.
   Localiza `ABOGALIA_SUPABASE_PUBLISHABLE_KEY=` y pega el valor después del `=`.
   Una línea, sin comillas, comentarios inline o expansión de shell. No sustituir
   el archivo completo ni duplicar la variable. Nunca editar `.env.example` con valores.
3. Conserva `ABOGALIA_IDENTITY_ENABLED=0` y `ABOGALIA_AUTH_EMAIL_READY=0`.
   El destino público es `ABOGALIA_SUPABASE_URL=https://spohytnxscljtitvmdab.supabase.co`.
   Los demás campos privados requieren su preparación separada; no copiar credenciales
   administrativas o la clave Resend a este archivo.
4. Guarda el archivo y ejecuta únicamente:

   ```sh
   chmod 600 /Users/arturo/Documents/repos/abogalia/.env
   ```

5. Comunica solo «publishable guardada». No compartir capturas, valores, contraseñas,
   tokens o códigos. El coordinador comprueba permisos/exclusión de Git por metadata;
   no lee el contenido del archivo real.

La publishable es pública según el proveedor, pero su configuración permanece
local. No se requiere `service_role`, clave secret ni DSN SQL de Auth para el modo
HTTP explícito. `ABOGALIA_AUTH_SESSION_CHECK_DSN` es legado opcional no inyectado.
La API aún necesita su DSN de rol runtime mínimo/TLS, firma CSRF y cifrado Fernet.
Esos valores se preparan privadamente y no se pasan como argumentos visibles.

Antes de activar Identity faltan pruebas reales de sesión/revocación y preparación
privada de runtime. EMAIL_READY solo pasa a 1 después de comprobar entrega OTP.
No ejecutar `source .env`, publicar el archivo o reiniciar servicios existentes
por inferencia. No cargar claves privadas en variables `VITE_*`.
