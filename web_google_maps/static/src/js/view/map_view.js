odoo.define('web.MapView', function (require) {
    'use strict';

    var core = require('web.core');
    var View = require('web.View');
    var Widget = require('web.Widget');
    var Model = require('web.Model');
    var MapViewPlacesAutocomplete = require('web.MapViewPlacesAutocomplete');
    var QWeb = core.qweb;
    var _lt = core._lt;
    var _t = core._t;

    var GOOGLE_PLACES_COMPONENT_FORM = {
            'street_number': 'long_name',
            'route': 'long_name',
            'intersection': 'short_name',
            'political': 'short_name',
            'country': 'short_name',
            'administrative_area_level_1': 'long_name',
            'administrative_area_level_2': 'short_name',
            'administrative_area_level_3': 'short_name',
            'administrative_area_level_4': 'short_name',
            'administrative_area_level_5': 'short_name',
            'colloquial_area': 'short_name',
            'locality': 'short_name',
            'ward': 'short_name',
            'sublocality_level_1': 'short_name',
            'sublocality_level_2': 'short_name',
            'sublocality_level_3': 'short_name',
            'sublocality_level_5': 'short_name',
            'neighborhood': 'short_name',
            'premise': 'short_name',
            'postal_code': 'short_name',
            'natural_feature': 'short_name',
            'airport': 'short_name',
            'park': 'short_name',
            'point_of_interest': 'long_name'
        };

    var MapView = View.extend({
        template: 'MapView',
        className: 'o_map_view',
        display_name: _lt('Map'),
        icon: 'fa-map-o',
        searchable: true,
        init: function () {
            this._super.apply(this, arguments);
            this.markers = [];
            this.map = false;
            this.shown = $.Deferred();
            this.fields = this.fields_view.fields;
            this.children_field = this.fields_view.field_parent;
            this.creatable = false;

            /* The three keys('model', 'method', 'fields') in the object assigned to variable 'options' is a mandatory keys.
             * The idea is to be able to pass any 'object' that can be created within the map
             *
             * The fields options is divided into three parts:
             * 1) 'general'
             *     This configuration is for 'general' fields of the object, fields like name, phone, etc..
             *     On the right side of each field is an attribute(s) from 'Places autocomplete'
             * 2) 'geolocation'
             *     This configuration is for geolocation fields (only 'latitude' and 'longitude')
             * 3) 'address'
             *     This configuration is similar to configuration used by 'google_places' widget
             *
             */
            var options = {
                'model': 'res.partner',
                'method': 'create_partner_from_map',
                'fields': {
                    'general': {
                        'name': 'name',
                        'website': 'website',
                        'phone': ['international_phone_number', 'formatted_phone_number'],
                        'is_company': '',
                    },
                    'geolocation': {
                        'latitude': 'partner_latitude',
                        'longitude': 'partner_longitude'
                    },
                    'address': {
                        'street': ['street_number', 'route', 'vicinity'],
                        'street2': ['administrative_area_level_3', 'administrative_area_level_4', 'administrative_area_level_5'],
                        'city': ['locality', 'administrative_area_level_2'],
                        'zip': 'postal_code',
                        'state_id': 'administrative_area_level_1',
                        'country_id': 'country',
                    }
                }
            };
            this.options = options;
        },
        start: function () {
            var self = this;
            this.shown.done(this.proxy('_init_start'));
            return this._super.apply(this, arguments);
        },
        _init_start: function () {
    	    try {
    	    	this.init_map();
                this.on_load_markers();
                this.on_point_to_create_partner();
                return $.when();
    	    } catch (e) {
	    	    if (e instanceof ReferenceError) {
	    	      // When google map cannot be loaded due to internet connection failure
	    			window.alert(_t('The map could not be load. Please check your internet connection.'));
    			}
    	    }
        },
        willStart: function () {
            this.set_geolocation_fields();
            return this._super.apply(this, arguments);
        },
        set_geolocation_fields: function () {
            if (this.fields_view.arch.attrs.lat && this.fields_view.arch.attrs.lng) {
                this.latitude = this.fields_view.arch.attrs.lat;
                this.longitude = this.fields_view.arch.attrs.lng;
                return true;
            } else {
                this.do_warn(_t('Error: cannot display locations'), _t('Please define alias name for geolocations fields for map view!'));
                return false;
            }
        },
        on_load_markers: function () {
            var self = this;
            this.load_markers().done(function () {
                self.map_centered();
            });
        },
        load_markers: function () {
            var self = this;
            this.infowindow = new google.maps.InfoWindow();
            return $.when(this.dataset.read_slice(this.fields_list()).done(function (records) {
                self.clear_marker_clusterer();
                if (!records.length) {
                    self.do_notify(_t('No geolocation is found!'));
                    return false;
                }
                _.each(records, function (record) {
                    if (record[self.latitude] && record[self.longitude]) {
                        var latLng = new google.maps.LatLng(record[self.latitude], record[self.longitude]);
                        self._create_marker(latLng, record);
                    };
                });
            }));
        },
        _create_marker: function (lat_lng, record) {
            var record = record || {
                'name': 'XY'
            };
            var marker = new google.maps.Marker({
                position: lat_lng,
                map: this.map,
                animation: google.maps.Animation.DROP,
                label: record.name.slice(0, 2)
            });
            this.markers.push(marker);
            this.set_marker(marker, record);
        },
        clear_marker_clusterer: function () {
            this.marker_cluster.clearMarkers();
            this.markers.length = 0;
        },
        set_marker: function (marker, record) {
            var record = record || false;
            this.marker_cluster.addMarker(marker);
            google.maps.event.addListener(marker, 'click', this.marker_infowindow(marker, record));
        },
        marker_infowindow: function (marker, record) {
            if (!Object.keys(record).length) {
                return;
            }
            var self = this;
            var content = this.marker_infowindow_content(record);
            return function () {
                self.infowindow.setContent(content);
                self.infowindow.open(self.map, marker);
            }
        },
        marker_infowindow_content: function (record) {
            var self = this;
            var ignored_fields = ['id', this.latitude, this.longitude];
            var contents = [];
            var title = "";
            _.each(record, function (val, key) {
                if (val && ignored_fields.indexOf(key) === -1) {
                    if (key == 'name') {
                        title += '<h3>' + val + '</h3>';
                    } else {
                        if (val instanceof Array && val.length > 0) {
                            contents.push('<p><strong>' + self.fields[key].string + '</strong> : <span>' + val[1] + '</span></p>');
                        } else {
                            contents.push('<p><strong>' + self.fields[key].string + '</strong> : <span>' + val + '</span></p>');
                        }
                    }
                }
            });
            var res = '<div>' + title + '<dl>' + contents.join('') + '</dl></div>';
            return res;
        },
        init_map: function () {
            this.map = new google.maps.Map(this.$el[0], {
                mapTypeId: google.maps.MapTypeId.ROADMAP,
                center:new google.maps.LatLng(-18.9033,47.5211),
                zoom: 13,
                minZoom: 3,
                maxZoom: 20,
                fullscreenControl: true,
                mapTypeControl: true,
                mapTypeControlOptions: {
                    style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
                    position: google.maps.ControlPosition.TOP_CENTER
                }
            });
            this.marker_cluster = new MarkerClusterer(this.map, null, {
                imagePath: '/web_google_maps/static/src/img/m'
            });
            this.on_maps_add_controls();
        },
        fields_list: function () {
            var fields = _.keys(this.fields);
            if (!_(fields).contains(this.children_field)) {
                fields.push(this.children_field);
            }
            return _.filter(fields);
        },
        map_centered: function () {
            var self = this;
            var context = this.dataset.context;
            if (context.route_direction) {
                this.on_init_routes();
            } else {
                this._map_centered();
            }
        },
        _map_centered: function () {
            google.maps.event.trigger(this.map, 'resize');
            if (this.markers.length == 1) {
                var self = this;
                google.maps.event.addListenerOnce(this.map, 'idle', function () {
                    self.map.setCenter(self.markers[0].getPosition());
                    self.map.setZoom(17);
                });
            } else {
                var bounds = new google.maps.LatLngBounds();
                _.each(this.markers, function (marker) {
                    bounds.extend(marker.getPosition());
                });
                this.map.fitBounds(bounds);
            }
        },
        do_show: function () {
            this.do_push_state({});
            this.shown.resolve();
            return this._super.apply(this, arguments);
        },
        do_search: function (domain, context, group_by) {
            var self = this;
            var _super = this._super;
            var _args = arguments;
            this.shown.done(function () {
                _super.apply(self, _args);
                self.on_load_markers();
            });
        },
        on_maps_add_controls: function () {
            var route_mode = this.dataset.context.route_direction ? true : false;
            new MapControl(this).open(route_mode);

            var opt = this.options
            new MapViewPlacesAutocomplete.MapPlacesAutocomplete(this, opt).open();
        },
        on_init_routes: function () {
            this.geocoder = new google.maps.Geocoder;
            this.directionsDisplay = new google.maps.DirectionsRenderer;
            this.directionsService = new google.maps.DirectionsService;
            this.directionsDisplay.setMap(this.map);
            this.on_calculate_and_display_route();
        },
        on_calculate_and_display_route: function (mode) {
            var self = this;
            var context = this.dataset.context;
            var mode = mode || 'DRIVING';
            var origin = new google.maps.LatLng(context.origin_latitude, context.origin_longitude);
            var destination = new google.maps.LatLng(context.destination_latitude, context.destination_longitude);
            var paths = [{
                'path': 'origin',
                'lat_lng': origin
            }, {
                'path': 'destination',
                'lat_lng': destination
            }];
            // Append new control button to the map, a control to open the route in a new tab
            this.add_btn_redirection(paths);

            this.directionsService.route({
                'origin': origin,
                'destination': destination,
                travelMode: google.maps.TravelMode[mode],
                avoidHighways: false,
                avoidTolls: false
            }, function (response, status) {
                if (status === 'OK') {
                    google.maps.event.trigger(self.map, 'resize');
                    self.directionsDisplay.setDirections(response);
                    self.get_routes_distance(response.routes[0]);
                } else if (status === 'ZERO_RESULTS') {
                    self.on_add_polyline(paths);
                } else {
                    window.alert(_t('Directions request failed due to ' + status));
                }
            });
        },
        get_routes_distance: function (route) {
            var content = "";
            for (var i = 0; i < route.legs.length; i++) {
                content += '<strong>' + route.legs[i].start_address + '</strong> &#8594;';
                content += ' <strong>' + route.legs[i].end_address + '</strong>';
                content += '<p>' + route.legs[i].distance.text + '</p>';
            }
            this.on_add_routes_window(content);
        },
        on_add_routes_window: function (content) {
            if (this.$route_window == undefined) {
                this.$route_window = $(QWeb.render('MapViewRoutes', {}));
                this.map.controls[google.maps.ControlPosition.LEFT_BOTTOM].push(this.$route_window[0]);
            }
            this.$route_window.find('span').html(content);
        },
        on_add_polyline: function (paths) {
            var self = this;
            var context = this.dataset.context;
            var route_path = _.pluck(paths, 'lat_lng');
            var polyline = new google.maps.Polyline({
                path: route_path,
                geodesic: true,
                strokeColor: '#3281ff',
                strokeOpacity: 0.8,
                strokeWeight: 5,
                fillColor: '#FF0000',
                fillOpacity: 0.35,
                map: this.map
            });
            var distance = this.on_compute_distance(route_path[0], route_path[1]);
            // display routes information
            var request_reverse = [];
            _.each(paths, function (path) {
                request_reverse.push(self._on_reverse_geocoding(path));
            });
            $.when.apply($, request_reverse).done(function () {
                var route = "";
                _.each(arguments, function (val) {
                    if (val.hasOwnProperty('origin') || val.hasOwnProperty('destination')) {
                        if (val.origin != false || val.destination != false) {
                            route += val.hasOwnProperty('origin') ? "<strong>" + val.origin + "</strong> &#8594; " : "<strong>" + val.destination + "</strong>";
                        }
                    }
                });
                route += "<p>" + distance + "</p>";
                self.on_add_routes_window(route);
            });
            // resize the map
            google.maps.event.trigger(this.map, 'resize');
            var bounds = new google.maps.LatLngBounds();
            _.each(route_path, function (route) {
                bounds.extend(route);
            });
            this.map.fitBounds(bounds);
        },
        on_compute_distance: function (origin, destination) {
            var distance = google.maps.geometry.spherical.computeDistanceBetween(origin, destination);
            var to_km = (distance / 1000).toFixed(2) + " km";
            return to_km;
        },
        redirect_to_gmaps_website: function (locations) {
            var self = this;
            var url = "https://www.google.com/maps/dir/?api=1";
            var window_reference = window.open();
            var requests = [];
            _.each(locations, function (path) {
                requests.push(self._on_reverse_geocoding(path));
            });
            $.when.apply($, requests).done(function () {
                var is_success = true;
                _.each(arguments, function (val) {
                    if (val.hasOwnProperty('origin') || val.hasOwnProperty('destination')) {
                        if (val.origin == false || val.destination == false) {
                            is_success = false;
                            window.alert(_t('Reverse geocoding is failed!'));
                            return false;
                        } else {
                            url += val.hasOwnProperty('origin') ? "&origin=" + val.origin : "&destination=" + val.destination;
                        }
                    }
                });
                if (is_success) {
                    window_reference.location = url;
                }
            });
        },
        _on_reverse_geocoding: function (location) {
            var def = $.Deferred();
            var lat_lng = location['lat_lng'];
            var path = location['path'];
            var res = {};
            this.geocoder.geocode({
                'location': lat_lng
            }, function (results, status) {
                if (status === 'OK') {
                    res[path] = results[0].formatted_address;
                } else {
                    res[path] = false;
                }
                def.resolve(res);
            });
            return def;
        },
        add_btn_redirection: function (locations) {
            var self = this;
            if (this.$btn_google_redirection === undefined) {
                this.$btn_google_redirection = $(QWeb.render('MapRedirectToGoogle', {}));
                this.map.controls[google.maps.ControlPosition.RIGHT_TOP].push(this.$btn_google_redirection[0]);
                this.$btn_google_redirection.on('click', function (ev) {
                    ev.preventDefault();
                    self.redirect_to_gmaps_website(locations);
                });
            }
        },
        reload: function () {
            var self = this;
            setTimeout(function () {
                self.on_load_markers();
            }, 1000);
            return $.when();
        },
        on_create_partner_new: function (place) {
            var self = this;
            if (place && place.hasOwnProperty('address_components')) {
                var values = self.set_default_values_new();
                var google_address = this.populate_address(place);
                var requests = [];
                _.each(this.options.fields.address, function (items, field) {
                    requests.push(self.prepare_value(field, google_address[field]));
                });
                $.when.apply($, requests).done(function () {
                    _.each(arguments, function (data, idx) {
                        _.each(data, function (val, key) {
                            if (val) {
                                values[key] = val;
                            }
                        });
                    });
                    console.log(values);
                    new Model(self.options.model).call(self.options.method, [values]).done(function (record) {
                        if (record) {
                            window.alert(_t('Successfully created new partner'));
                            // empty search results
//                            self.action_pac_form_visibility('hide');
                            // reload map
                            location.reload();
                        } else {
                            window.alert(_t('Fail to create new partner!'));
                            $('#btn_create_customer').disabled = false;
                        }
                    }).fail(function (err, event) {
                        window.alert(err);
                        $('#btn_create_customer').disabled = false;
                    });
                });
            }
        },
        populate_address: function (place) {
            var self = this;
            var fields_to_fill = {}
            var result = {};
            // initialize object key and value
            _.each(this.options.fields.address, function (value, key) {
                fields_to_fill[key] = [];
            });
            _.each(this.options.fields.address, function (options, field) {
                var vals = _.map(place.address_components, function (components) {
                    if (options instanceof Array) {
                        var val = _.map(options, function (item) {
                            if (_.contains(components.types, item)) {
                                return components[GOOGLE_PLACES_COMPONENT_FORM[item]];
                            } else {
                                return false;
                            }
                        });
                        return _.filter(val); // eliminate false
                    } else {
                        if (_.contains(components.types, options)) {
                            return components[GOOGLE_PLACES_COMPONENT_FORM[options]];
                        } else {
                            return false;
                        }
                    }
                });
                fields_to_fill[field] = _.flatten(_.filter(vals, function (val) {
                    return val.length;
                }));
            });
            console.log(fields_to_fill);
            _.each(fields_to_fill, function (value, key) {
                if (key == 'street' && !value.length) {
                    var addrs = self.options.fields.address.street;
                    if (addrs instanceof Array) {
                        var addr = _.map(addrs, function (item) {
                            return place[item];
                        });
                        result[key] = _.filter(addr).join(', ');
                    } else {
                        result[key] = place[addrs] || '';
                    }
                } else if (key == 'city') {
                    result[key] = value.length ? value[0] : '';
                } else {
                    result[key] = value.join(', ');
                }
            });

            return result;
        },
        set_default_values_new: function () {
            var self = this;
            var values = {};
            _.each(this.options.fields, function (attrs, type) {
                if (type === 'general') {
                    _.each(attrs, function (option, field) {
                        if (field == 'name') {
                            var $name = $('#name_new').val();
                            if ($name) {
                                values[field] = $name;
                            }
                        } else if (field == 'website'){
                            var $website = $('#website_new').val();
                            if ($website) {
                                values[field] = $website;
                            }
                        } else if (field == 'phone'){
                            var $phone = $('#phone_new').val();
                            if ($phone) {
                                values[field] = $phone;
                            }
                        } else if (field == 'is_company') {
                            var $partner_type = self.$el.find('input[name="company_type"]:checked');
                            if ($partner_type.length && $partner_type.val() == 'company') {
                                values[field] = true;
                            }
                        } else {
                            values[field] = place[option];
                        }
                    });
                } else if (type === 'geolocation') {
                	values['partner_latitude'] = $('#span_lat').text();
                	values['partner_longitude'] = $('#span_lng').text();
                }
            });
            return values;
        },
        prepare_value: function (field_name, value) {
            var def = $.Deferred();
            var res = {};
            if (field_name == 'state_id') {
                new Model('res.country.state').call('search', [
                    ['|', ['name', '=', value], ['code', '=', value]]
                ]).done(function (record) {
                    res[field_name] = record.length > 0 ? record[0] : false;
                    def.resolve(res);
                });
            } else if (field_name == 'country_id') {
                new Model('res.country').call('search', [
                    ['|', ['name', '=', value], ['code', '=', value]]
                ]).done(function (record) {
                    res[field_name] = record.length > 0 ? record[0] : false;
                    def.resolve(res);
                });
            } else {
                res[field_name] = value;
                def.resolve(res);
            }
            return def;
        },
        on_point_to_create_partner: function () {
	        /*
	         *  Cliquer n'importe où dans la carte.
	         *  Une petite fenetre s'affichera avec un formalaire basique
	         *  pour créer un partenaire
	        */
        	self = this;

	        var geocoder = new google.maps.Geocoder;
	    	var map = this.map;
	    	var infowindow = new google.maps.InfoWindow();

	    	function do_click(event) {

	    		var pnt = event.latLng;
            	  var lat = pnt.lat();
                  lat = lat.toFixed(4);
                  var lng = pnt.lng();
                  lng = lng.toFixed(4);
                  var latlng = {lat: parseFloat(lat), lng: parseFloat(lng)};


                    geocoder.geocode({'location': latlng}, function(results, status) {
                        if (status === 'OK') {
                          if (results[1]) {
                            map.setZoom(16);
                            var marker = new google.maps.Marker({
                              position: latlng,
                              map: map
                            });
                            var contents = '<p><strong>' + results[1].formatted_address + '</strong></p>';
                            contents += '<p>Latitude : <span class="badge" id="span_lat" >'+lat+'</span></p>';
                            contents += '<p>Longitude : <span class="badge" id="span_lng" >'+lng+'</span></p><br>';
                            contents += '<input type="text" id="name_new" placeholder="Nom" class="form-control" />';
                            contents += '<input type="text" id="website_new" placeholder="Site web" class="form-control" />';
                            contents += '<input type="text" id="phone_new" placeholder="Telephone" class="form-control" /><br>';
                            contents += '<input type="radio" name="company_type_new" checked="checked" value="person" class="radio-inline"/>';
                            contents += '<label for="radio_company_person_new">Individual  </label>';
        					contents += '<input type="radio" name="company_type_new" value="company" class="radio-inline"/>';
        					contents += '<label for="radio_company_company_new">Company</label>';
                            contents += '<hr><button class="btn btn-sm btn-primary" id="btn_create_customer"> Créer un partenaire ici!</button>';
                            infowindow.setContent(contents);
                            infowindow.open(map, marker);
//                            document.getElementById('btn_create_customer').addEventListener("click", this.on_create_partner_new(results[1]));
                            $('#btn_create_customer').click(function(){
                            							console.log('latitude = '+lat+'&longitude = '+lng);
                            							$('#btn_create_customer').disabled = true;
                            							self.on_create_partner_new(results[1]);
                            						});
                          } else {
                            window.alert('No results found');
                          }
                        } else {
                          window.alert('Geocoder failed due to: ' + status);
                        }
                    });
	    	}

        	// Si le bouton "Ajouter un nouveau partenaire" a été cliqué, creatable = true (default false)
        	if(self.creatable){
		    	$(document).ready(function(){
		    		google.maps.event.addListener(map, 'click', do_click);
		    	});
        	}else{
        		google.maps.event.clearListeners(map, 'click');
        	}
    	}
    });

    var MapControl = Widget.extend({
        init: function (parent) {
            this._super.apply(parent, {});
            this.parent = parent;
            this.$controls = $(QWeb.render('MapViewControl', {}));
        },
        bind_events: function () {
            this.$controls.on('click', '.btn_map_control', this.on_control_maps.bind(this));
            this.$controls.on('click', 'p#map_layer', this.on_change_layer.bind(this));
            this.$controls.on('click', 'p#travel_mode', this.on_change_mode.bind(this));
            this.$controls.on('mouseleave', '#o_map_sidenav', this.on_map_sidenav_mouseleave.bind(this));
        },
        _init_controls: function () {
            this.bind_events();
            this.parent.map.controls[google.maps.ControlPosition.LEFT_TOP].push(this.$controls[0]);
        },
        open: function (route_mode) {
            if (route_mode) {
                this.$controls.find('#o_map_travel_mode').show();
            }
            this.parent.shown.done(this.proxy('_init_controls'));
        },
        on_control_maps: function (ev) {
            $(ev.currentTarget).toggleClass('opened');
            this.$controls.find('#o_map_sidenav').toggleClass('opened');
            if (this.$controls.find('#o_map_sidenav').hasClass('opened')) {
                this.action_sidenav_visibility('show');
            } else {
                this.action_sidenav_visibility('hide');
            }
        },
        on_map_sidenav_mouseleave: function () {
            var self = this;
            setTimeout(function () {
                self.action_sidenav_visibility('hide');
            }, 3000);
        },
        action_sidenav_visibility: function (action) {
            if (action == 'show') {
                this.$controls.find('#o_map_sidenav').css({
                    'width': '150px'
                }).show();
                this.$controls.find('.fa').removeClass('fa-bars').addClass('fa-angle-double-left');
            } else {
                this.$controls.find('.btn_map_control').removeClass('opened');
                this.$controls.find('#o_map_sidenav').removeClass('opened').hide();
                this.$controls.find('.fa').removeClass('fa-angle-double-left').addClass('fa-bars');
            }
        },
        on_change_layer: function (ev) {
            ev.preventDefault();
            var layer = $(ev.currentTarget).data('layer');
            if (layer == 'traffic') {
                this._on_traffic_layer(ev);
            } else if (layer == 'transit') {
                this._on_transit_layer(ev);
            } else if (layer == 'bicycle') {
                this._on_bicycle_layer(ev);
            }
        },
        on_change_mode: function (ev) {
            ev.preventDefault();
            $(ev.currentTarget).siblings().removeClass('active');
            $(ev.currentTarget).toggleClass('active')
            var mode = $(ev.currentTarget).data('mode');
            this.parent.on_calculate_and_display_route(mode);
        },
        _on_traffic_layer: function (ev) {
            $(ev.currentTarget).toggleClass('active');
            if ($(ev.currentTarget).hasClass('active')) {
                this.trafficLayer = new google.maps.TrafficLayer();
                this.trafficLayer.setMap(this.parent.map);
            } else {
                this.trafficLayer.setMap(null);
                this.trafficLayer = undefined;
            }
        },
        _on_transit_layer: function (ev) {
            $(ev.currentTarget).toggleClass('active');
            if ($(ev.currentTarget).hasClass('active')) {
                this.transitLayer = new google.maps.TransitLayer();
                this.transitLayer.setMap(this.parent.map);
            } else {
                this.transitLayer.setMap(null);
                this.transitLayer = undefined;
            }
        },
        _on_bicycle_layer: function (ev) {
            $(ev.currentTarget).toggleClass('active');
            if ($(ev.currentTarget).hasClass('active')) {
                this.bikeLayer = new google.maps.BicyclingLayer();
                this.bikeLayer.setMap(this.parent.map);
            } else {
                this.bikeLayer.setMap(null);
                this.bikeLayer = undefined;
            }
        },
        display_location: function () {
        	var geocoder = new google.maps.Geocoder;
        	var map = this.map;
        	var infowindow = new google.maps.InfoWindow();
            google.maps.event.addListener(map, 'click', function (event) {
	              var pnt = event.latLng;
            	  var lat = pnt.lat();
		          lat = lat.toFixed(4);
		          var lng = pnt.lng();
		          lng = lng.toFixed(4);
		          var latlng = {lat: parseFloat(lat), lng: parseFloat(lng)};


		            geocoder.geocode({'location': latlng}, function(results, status) {
		                if (status === 'OK') {
		                  if (results[1]) {
		                    map.setZoom(11);
		                    var marker = new google.maps.Marker({
		                      position: latlng,
		                      map: map
		                    });
		                    infowindow.setContent(results[1].formatted_address);
		                    infowindow.open(map, marker);
		                  } else {
		                    window.alert('No results found');
		                  }
		                } else {
		                  window.alert('Geocoder failed due to: ' + status);
		                }
		              });
	          });
        }
    });

    core.view_registry.add('map', MapView);

    return MapView;
});