#!/usr/bin/python3
"""
Place view object that handles all default RESTFul API actions
"""
from api.v1.views import app_views
from flask import abort, jsonify, make_response, request
from models import storage
from models.city import City
from models.place import Place
import os
import requests
import json


@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
def all_places(city_id):
    """Retireve the list of places objects of a specified city"""
    city = storage.get("City", city_id)
    if city is None:
        abort(404)
    return jsonify([place.to_dict() for place in city.places])


@app_views.route('/places/<place_id>', methods=['GET'],
                 strict_slashes=False)
def get_place(place_id):
    """get place information if place id is given"""
    place = storage.get("Place", place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_place(place_id):
    """deletes a place based on it's place_id"""
    place = storage.get("Place", place_id)
    if place is None:
        abort(404)
    place.delete()
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
def create_place(city_id):
    """create a new place"""
    city = storage.get("City", city_id)
    if city is None:
        abort(404)
    data = request.get_json()
    if not data:
        abort(400, "Not a JSON")
    if 'user_id' not in data:
        abort(400, "Missing user_id")
    user_id = data['user_id']
    if not storage.get("User", user_id):
        abort(404)
    if 'name' not in data:
        abort(400, "Missing name")
    place = Place(**data)
    setattr(place, 'city_id', city_id)
    storage.new(place)
    storage.save()
    return make_response(jsonify(place.to_dict()), 201)


@app_views.route('/places/<place_id>', methods=['PUT'],
                 strict_slashes=False)
def update_place(place_id):
    """update the place object"""
    place = storage.get("Place", place_id)
    if place is None:
        abort(404)
    if not request.get_json():
        abort(400, "Not a JSON")
    for key, value in request.get_json().items():
        if key not in ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
            setattr(place, key, value)
    place.save()
    return make_response(jsonify(place.to_dict()), 200)


@app_views.route('/places_search', methods=['POST'],
                 strict_slashes=False)
def places_search():
    """Retrieves all Place objects having all listed amenities"""
    req = request.get_json()
    if req is None:
        abort(400, "Not a JSON")
    if not req or (
            not req.get('states') and
            not req.get('cities') and
            not req.get('amenities')
    ):
        places = storage.all(Place).values()
        return jsonify([place.to_dict() for place in places])
    places = []
    if req.get('states'):
        states = [storage.get("State", id) for id in req.get('states')]
        for state in states:
            for city in state.cities:
                for place in city.places:
                    places.append(place)
    if req.get('cities'):
        cities = [storage.get("City", id) for id in req.get('cities')]
        for city in cities:
            for place in city.places:
                if place not in places:
                    places.append(place)
    if not places:
        places = storage.all(Place).values()
        places = [place for place in places]
    if req.get('amenities'):
        ams = [storage.get("Amenity", id) for id in req.get('amenities')]
        i = 0
        limit = len(places)
        HBNB_API_HOST = os.getenv('HBNB_API_HOST')
        HBNB_API_PORT = os.getenv('HBNB_API_PORT')
        port = 5000 if not HBNB_API_PORT else HBNB_API_PORT
        first_url = "http://0.0.0.0:{}/api/v1/places/".format(port)
        while i < limit:
            place = places[i]
            url = first_url + '{}/amenities'
            reqst = url.format(place.id)
            response = requests.get(reqst)
            am_d = json.loads(response.text)
            amenities = [storage.get("Amenity", o['id']) for o in am_d]
            for amenity in ams:
                if amenity not in amenities:
                    places.pop(i)
                    i -= 1
                    limit -= 1
                    break
            i += 1
    return jsonify([place.to_dict() for place in places])
