import { index, type RouteConfig, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("acceso", "routes/login.tsx"),
  route("registro", "routes/register.tsx"),
  route("recuperar", "routes/recover.tsx"),
  route("cuenta", "routes/account.tsx"),
  ...(import.meta.env.DEV
    ? [route("dev/conexion", "routes/connection.tsx")]
    : []),
] satisfies RouteConfig;
