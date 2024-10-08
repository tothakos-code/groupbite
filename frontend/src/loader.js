import { useVendorStore } from "@/stores/vendor";


export function register_plugin_routes(router) {
  useVendorStore().vendors.forEach((item) => {
    if (!router.hasRoute("/"+item.name)) {
      let component = () => import("@/views/MenuRender.vue")
      router.addRoute("menu", {
        name: `${item.name}`,
        path: `${item.name}`,
        component: component,
        props: {
          vendorId: item.id
        }
      });
      router.addRoute("menu", {
        name: `${item.name}-dated`,
        path: `${item.name}/:selected_date`,
        component: component,
        props: {
          vendorId: item.id
        }
      });
    }
  });
  const currentRoute = router.resolve(router.currentRoute.value.path);
  router.replace(currentRoute);
}
