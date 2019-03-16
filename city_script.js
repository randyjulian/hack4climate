var app = new Vue({
    el: '#app',
    data: {
      cities_list: [], 
      info: {}, 
      actions: [],
      city_name: 'Singapore'
    }, 
    created: function() {
      fetch("https://ync.yenter.io/get_info/" + this.city_name).then((resp) => {
        return resp.json()
      }).then((resp) => {
        console.log(resp)
        this.info = resp;
        console.log(resp['actions'])
      })
    }
  })
  