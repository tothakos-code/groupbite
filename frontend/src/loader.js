
export function register_plugin_routes(router) {
  fetch(`http://${window.location.host}/get_vendors`,{
    method: "GET",
  })
    .then(response => response.json())
      .then(data => {
        data.forEach((item) => {
          router.addRoute({
            name: item.name,
            path: '/'+item.name,
            component: () => import(`@/../../plugins/${item.name}/frontend/App.vue`),
          })
          console.log('registering:');
          console.log(item);
        });
        router.replace();
        // router.replace(router.currentRoute.value.fullPath)
      })
    .catch(error => console.error('Error fecthing vendors:',error));
}
