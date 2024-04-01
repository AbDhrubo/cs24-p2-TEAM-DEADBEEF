let map,directionsService, directionsRenderer
let sourceAutocomplete,desAutocomplete

function initMap()
{

    map = new google.maps.Map(document.getElementById('map'),
    {
        center: {lat:23.8041,lng:90.4152},
        zoom: 13
        //mapTypeId:google.maps.MyTypeId.ROADMAP
    })

    const trafficLayer = new google.maps.TrafficLayer();
    trafficLayer.setMap(map);


      google.maps.event.addListener(map,"click",function(event)
      {
          this.setOptions({scrollwheel:true})
      })

      directionsService = new google.maps.DirectionsService()
      directionsRenderer = new google.maps.DirectionsRenderer()
      directionsRenderer.setMap(map)

      sourceAutocomplete = new google.maps.places.Autocomplete(document.getElementById('source') )
      desAutocomplete = new google.maps.places.Autocomplete(document.getElementById('dest') )
}

function calcRoute()
{
  var source = document.getElementById('source').value
  var dest = document.getElementById('dest').value

  let request = {
        //origin:source,
        origin:{ lat: 23.8103, lng: 90.4125 },
//        destination:dest,
        destination:{ lat: 22.3569, lng: 91.7832 },
        travelMode:'DRIVING',
        drivingOptions: {
          departureTime: new Date(),  // request current traffic conditions
          trafficModel: 'pessimistic' // or 'best_guess' for average traffic
        }
  }

  directionsService.route(request,function(result,status)
  {   if(status == "OK")
      {

        const output = document.querySelector("#output");
        output.innerHTML =
        "<div class= 'alert-info' >From: "+
        document.getElementById("source").value +".</br>To: "+
        document.getElementById("dest").value + ".</br> Driving distance: "+
        result.routes[0].legs[0].distance.text +
        ".</br>Duration: " + result.routes[0].legs[0].duration.text + ".</div>"

          directionsRenderer.setDirections(result)
      }
  })

}