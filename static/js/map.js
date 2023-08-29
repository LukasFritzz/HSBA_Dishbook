function initMap() {
    const map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: DEINE_START_LATITUDE, lng: DEINE_START_LONGITUDE },
        zoom: 15,
    });

    const service = new google.maps.places.PlacesService(map);

    service.nearbySearch(
        {
            location: new google.maps.LatLng(DEINE_START_LATITUDE, DEINE_START_LONGITUDE),
            radius: 1000,
            type: ["restaurant"],
        },
        (results, status) => {
            if (status === google.maps.places.PlacesServiceStatus.OK && results.length > 0) {
                const restaurant = results[0];
                const marker = new google.maps.Marker({
                    position: restaurant.geometry.location,
                    map: map,
                    title: restaurant.name,
                });

                const directionsService = new google.maps.DirectionsService();
                const directionsRenderer = new google.maps.DirectionsRenderer({
                    map: map,
                });

                directionsService.route(
                    {
                        origin: new google.maps.LatLng(DEINE_START_LATITUDE, DEINE_START_LONGITUDE),
                        destination: restaurant.geometry.location,
                        travelMode: google.maps.TravelMode.DRIVING,
                    },
                    (response, status) => {
                        if (status === google.maps.DirectionsStatus.OK) {
                            directionsRenderer.setDirections(response);
                        } else {
                            console.error("Fehler beim Abrufen der Wegbeschreibung:", status);
                        }
                    }
                );
            }
        }
    );

    document.getElementById("loader").style.display = "none";
    document.getElementById("map").style.display    = "block";
}

function loadGoogleMapsScript() {
    const script = document.createElement("script");
    script.src = "https://maps.googleapis.com/maps/api/js?key=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX&libraries=places&callback=initMap";
    script.defer = true;
    document.head.appendChild(script);
}

function getCurrentLocationAndInitMap() {

    document.getElementById("main-img").style.display   = "none";
    document.getElementById("map").style.display        = "none";
    document.getElementById("loader").style.display     = "flex";

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const latitude = position.coords.latitude;
                const longitude = position.coords.longitude;

                window.DEINE_START_LATITUDE = latitude;
                window.DEINE_START_LONGITUDE = longitude;

                loadGoogleMapsScript();
            },
            function(error) {
                console.error("Fehler bei der Geolocation:", error);
            }
        );
    } else {
        console.error("Geolocation wird vom Browser nicht unterstützt.");
    }
}

document.getElementById("showMapButton").addEventListener("click", getCurrentLocationAndInitMap);