odoo.define('wso_flotte_logistique.WsoMapView', function (require) {
    'use strict';


    var mapView = require('web.MapView');
    var MapViewPlacesAutocomplete = require('web.MapViewPlacesAutocomplete');
    var core = require('web.core');
    var Model = require('web.Model');
    var QWeb = core.qweb;
    var _lt = core._lt;
    var _t = core._t;

    var GOOGLE_PLACES_COMPONENT_FORM = MapViewPlacesAutocomplete.GOOGLE_PLACES_COMPONENT_FORM;
    var WsoMapView = core.view_registry.get('map');

    WsoMapView.include({
        on_init_routes: function () {
            this.geocoder = new google.maps.Geocoder;
            this.directionsDisplay = new google.maps.DirectionsRenderer;
            this.directionsService = new google.maps.DirectionsService;
            this.directionsDisplay.setMap(this.map);
            var context = this.dataset.context;
//          For many directions
            if(context.many_directions){
                this.on_calculate_and_display_many_routes();
            }else{
                this.on_calculate_and_display_route();
            }
        },
        on_calculate_and_display_many_routes: function (mode) {
            var self = this;
            var options = {
                    'model': 'wso.flotte.route',
                    'method': 'set_total_distance'
                };
            var context = this.dataset.context;
            var mode = mode || 'DRIVING';
            var routes = [];
            for(var i = 0; i <=context.total_count; i++){
            	routes.push({
	            				'origin': new google.maps.LatLng(context['origin_latitude'+i], context['origin_longitude'+i]),
	            				'destination': new google.maps.LatLng(context['destination_latitude'+i], context['destination_longitude'+i])
	            			});
            }
            var rendererOptions = {
            	    preserveViewport: true,
            	    routeIndex:i
            	};
            var total_dist = 0;
             var each = _.each(routes, function(value,index){
                var request = {
                    origin: value.origin,
                    destination: value.destination,
                    travelMode: google.maps.TravelMode[mode],
                    avoidHighways: false,
                    avoidTolls: false
                };
                var directions_display = new google.maps.DirectionsRenderer(rendererOptions);
                directions_display.setMap(self.map);
                self.directionsService.route(request, function (response, status) {
                    if (status === 'OK') {
                    	if(index % 2 == 0){
                        	directions_display.setOptions({
                      		  polylineOptions: {
                      		    strokeColor: '#35C4BB'
                      		  }
                      		});
                    	}
//                    	Parse string distance to float (ex: '5,4 km' -> 5.4)
                    	var str = response.routes[0].legs[0].distance.text;
                        str = str.split(" ");
                        str = str[0].split(",");
                        str = parseFloat(str.join("."));
                        total_dist += str;
                        self.get_routes_total_distance(total_dist);
//                        google.maps.event.trigger(self.map, 'resize');
                        directions_display.setDirections(response);
                    } else if (status === 'ZERO_RESULTS') {
                    		alert('ERROR when displaying routes: Some partners cannot be localized.');
//                        self.on_add_polyline(paths);
                    } else {
                        window.alert(_t('Directions request failed due to ' + status));
                    }
                    if(routes.length - 1 == index){
                        var feuille_id = context.default_partner_id;
                        new Model(options.model).call('set_total_distance', [total_dist, feuille_id]).done(function (record) {
                            if (record) {
                                console.log(total_dist);
                            } else {
                                console.log("Cannot find total distance");
                            }
                        }).fail(function (err, event) {
                            window.alert(err);
                        });
                    }
                });
            });
        },
//        on_calculate_distance: function () {
//            var options = {
//                    'model': 'wso.flotte.route',
//                    'method': 'set_total_distance'
//                };
//            var self = this;
//            var context = this.dataset.context;
//            var mode =  'DRIVING';
//            var routes = [];
//            for(var i = 0; i <=context.total_count; i++){
//            	routes.push({
//	            				'origin': new google.maps.LatLng(context['origin_latitude'+i], context['origin_longitude'+i]),
//	            				'destination': new google.maps.LatLng(context['destination_latitude'+i], context['destination_longitude'+i])
//	            			});
//            }
//            var rendererOptions = {
//            	    preserveViewport: true,
//            	    routeIndex:i
//            	};
//            var total_dist = 0;
//            $.each(routes, function(index, value){
//                var request = {
//                    origin: value.origin,
//                    destination: value.destination,
//                    travelMode: google.maps.TravelMode[mode],+
//                    avoidHighways: false,
//                    avoidTolls: false
//                };
//                var directions_display = new google.maps.DirectionsRenderer(rendererOptions);
//                directions_display.setMap(self.map);
//                self.directionsService.route(request, function (response, status) {
//                    if (status === 'OK') {
////                    	Parse string distance to float (ex: '5,4 km' -> 5.4)
//                    	var str = response.routes[0].legs[0].distance.text;
//                        str = str.split(" ");
//                        str = str[0].split(",");
//                        str = parseFloat(str.join("."));
//                        total_dist += str;
//                        self.get_routes_total_distance(total_dist);
//
//    	                var partner_id = this.dataset.context.default_partner_id;
//    	                new Model(self.options.model).call('set_total_distance', [total_dist, partner_id]).done(function (record) {
//    	                    if (record) {
//    	                        console.log(total_dist);
//    	                    } else {
//    	                        console.log("Cannot find total distance");
//    	                    }
//    	                }).fail(function (err, event) {
//    	                    window.alert("Total distance not found");
//    	                });
//                    } else if (status === 'ZERO_RESULTS') {
//                    		alert('ERROR when calculating distance: Some partners cannot be localized.')
//                    } else {
//                        window.alert(_t('Calculating distance failed due to ' + status));
//                    }
//                });
//            });
//        },
        get_routes_total_distance: function (total_dist) {
            var content = "";
                content += '<strong> Total distance : </strong>';
                content += '<p><span class="badge">'+total_dist+' km</span></p>';
            this.on_add_routes_window(content);
        }
    });
});