import { state } from "@/socket";

export function register_plugin_routes(router) {
  state.vendors.forEach((item) => {
    if (!router.hasRoute('/'+item.name)) {
      item.configuration.frontend_routes.forEach((route) => {
        router.addRoute({
          name: route.name,
          path: route.path,
          component: () => import(`@/../../plugins/${item.name}/frontend${route.component_file}`),
          props: {
            vendorId: item.id
          }
        });
      });
    }
  });
  const currentRoute = router.resolve(router.currentRoute.value.path);
  router.replace(currentRoute);
}
