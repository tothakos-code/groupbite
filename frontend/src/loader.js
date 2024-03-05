import { state } from "@/socket";

export function register_plugin_routes(router) {
  fetch(`http://${window.location.host}/api/vendor/find-all-active`,{
    method: "GET",
  })
    .then(response => response.json())
      .then(data => {
        data.forEach((item) => {
          router.addRoute({
            name: item.name,
            path: '/'+item.name,
            redirect: () => {
              let day = state.selectedDate
              if (day.getHours() >= 13) {
                day.setDate(day.getDate() +1)
              }
              return {"path":`/${item.name}/`+day.toISODate()};
            }
          });
          // router.replace();
          router.addRoute({
            name: item.name+'-dated',
            path: '/'+item.name+'/:selected_date',
            component: () => import(`@/../../plugins/${item.name}/frontend/App.vue`),
          });
          console.log('registering:');
          console.log(item);
        });
        const currentRoute = router.resolve(router.currentRoute.value.path);
        router.replace(currentRoute);
      })
    .catch(error => console.error('Error fecthing vendors:',error));
}
