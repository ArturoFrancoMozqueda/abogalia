import { index, type RouteConfig, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  ...(import.meta.env.DEV
    ? [route("dev/conexion", "routes/connection.tsx")]
    : []),
] satisfies RouteConfig;
