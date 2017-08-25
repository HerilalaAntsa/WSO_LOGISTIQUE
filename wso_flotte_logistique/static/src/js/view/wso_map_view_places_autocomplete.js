odoo.define('wso_flotte_logistique.WsoMapViewPlacesAutocomplete', function (require) {
    'use strict';

    var core = require('web.core');
    var Model = require('web.Model');
    var _t = core._t;
    var WsoMapViewPlacesAutocomplete = require('web.MapViewPlacesAutocomplete');
    var WsoMapView = require('web.MapView');
    var GOOGLE_PLACES_COMPONENT_FORM = WsoMapViewPlacesAutocomplete.GOOGLE_PLACES_COMPONENT_FORM;

    var WsoMapViewPlacesAutocomplete = WsoMapViewPlacesAutocomplete.MapPlacesAutocomplete.include({
        events: {
            'click .btn_places_control': 'on_control_places',
            'click button#pac-button-create': 'on_create_partner',
            'click input[id^="changetype"], input[id="use-strict-bounds"]': 'on_place_changetype',
        	'click .btn_create_partner': 'on_point_partner'
        },
//        En cliquant le boutant 'Ajouter partenaire'
        on_point_partner: function (ev) {
    		this.creatable = false;
    		this.map = this.parent.map;

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

        	$(ev.currentTarget).toggleClass('opened');
        	// Si le bouton ajouter est activé (cliqué)
            if($(ev.currentTarget).hasClass('opened')){
	        	this.parent.map.setOptions({ draggableCursor: 'crosshair' });
	        	this.creatable = true;
            }else{
            	this.creatable = false;
	        	this.parent.map.setOptions({ draggableCursor: '' });
            }
        	this.on_point_to_create_partner();
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
//                    console.log(values);
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
//    	@override
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
//    	@override
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
//    	@override
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
//    	fonctions afin de créer un res.partner a partir de la carte
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
    	},

//    	fonctions afin de modifier les coordonnees d'un res.partner
        _modify_address: function (place,modif_totale) {
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
	                var partner_name = self.parent.dataset.context.search_default_name;
	                var partner_id = self.parent.dataset.context.search_default_id;
	                new Model(self.options.model).call('modify_partner_from_map', [values, partner_id, modif_totale]).done(function (record) {
	                    if (record) {
	                        window.alert(_t('Successfully modified partner : '+partner_name));
	                        location.reload();
	                    } else {
	                        window.alert(_t('Fail to modify partner : '+partner_name));
	                        $('#btn_modify_totale_customer').disabled = false;
	                    }
	                }).fail(function (err, event) {
	                    window.alert(err);
	                });

	//                google.maps.event.trigger(this.map, 'resize');
	//                if (this.markers.length == 1) {
	//                    var self = this;
	//                    google.maps.event.addListenerOnce(this.map, 'idle', function () {
	//                        self.map.setCenter(self.markers[0].getPosition());
	//                        self.map.setZoom(17);
	//                    });
	//                } else {
	//                    var bounds = new google.maps.LatLngBounds();
	//                    _.each(this.markers, function (marker) {
	//                        bounds.extend(marker.getPosition());
	//                    });
	//                    this.map.fitBounds(bounds);
	//                }
	            });
            }
        },
        on_point_to_modify_partner: function () {
	        /*
	         *  Cliquer n'importe où dans la carte.
	         *  Une petite fenetre s'affichera avec les nouveaux coordonnées
	         *  pour modifier un partenaire
	        */
        	self = this;

	        var geocoder = new google.maps.Geocoder;
	    	var map = this.parent.map;
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
                            contents += '<hr><button class="btn btn-sm btn-success" id="btn_modify_totale_customer" title="Modifier l\'adresse & les coordonnées"> Modification totale</button>';
                            contents += '<button class="btn btn-sm btn-primary" id="btn_modify_customer" title="Modifier que les coordonnées (longitude & latitude)"> Modification coordonnées</button>';
                            infowindow.setContent(contents);
                            infowindow.open(map, marker);
                            $('#btn_modify_totale_customer').click(function(){
                            							$('#btn_modify_totale_customer').disabled = true;
                            							self._modify_address(results[1],true);
                            						});
                            $('#btn_modify_customer').click(function(){
						    							$('#btn_modify_customer').disabled = true;
						    							self._modify_address(results[1],false);
						    						});
                          } else {
                            window.alert('No results found');
                          }
                        } else {
                          window.alert('Geocoder failed due to: ' + status);
                        }
                    });
	    	}

        	// Si bouton "assigner adresse" cf. res_partner_view.xml
            var editable = self.parent.dataset.context.editable ? true : false;
        	if(editable){
		    	$(document).ready(function(){
		    		google.maps.event.addListener(map, 'click', do_click);
		    	});
        	}else{
        		google.maps.event.clearListeners(map, 'click');
        	}
    	},
        start: function () {
            this._super();
            var editable = this.parent.dataset.context.editable ? true : false;
        	if(editable){
        		this.on_point_to_modify_partner();
        	}
        }
    });

    var WsoMapControl = WsoMapView.MapControl.include({
        on_change_mode: function (ev) {
            ev.preventDefault();
            $(ev.currentTarget).siblings().removeClass('active');
            $(ev.currentTarget).toggleClass('active');
            var mode = $(ev.currentTarget).data('mode');
            if(this.route){
                this.parent.on_calculate_and_display_route(mode);
            }else{
                this.parent.on_calculate_and_display_many_routes(mode);
            }
        }
    });

    return WsoMapViewPlacesAutocomplete;

});