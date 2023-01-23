#!/usr/bin/python3
"""View for the link between Place objects and Amenity objects
that handles all default RESTFul API actions
"""
from api.v1.views import app_views
from flask import jsonify, abort, make_response, request
from models import storage
from models.place import Place
from models.amenity import Amenity
import os


@app_views.route('/places/<place_id>/amenities', methods=['GET'],
                 strict_slashes=False)
def all_places_amenities(place_id):
    """ Retrieves the list of all Amenities objects in a Place"""
    place = storage.get("Place", place_id)
    if place is None:
        abort(404)
    amenities = []
    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        amenity_objects = place.amenities
    else:
        amenity_objects = place.amenity_ids
    for amenity in amenity_objects:
        amenities.append(amenity.to_dict())
    return jsonify(amenities)


@app_views.route('/places/<place_id>/amenities/<amenity_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_places_amenities(place_id, amenity_id):
    """ Deletes an Amenity object """
    place = storage.get("Place", place_id)
    amenity = storage.get("Amenity", amenity_id)
    if place is None or amenity is None:
        abort(404)
    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        place_amenities = place.amenities
    else:
        place_amenities = place.amenity_ids
    if amenity not in place_amenities:
        abort(404)
    place_amenities.remove(amenity)
    place.save()
    return make_response(jsonify({}), 200)


@app_views.route('/places/<place_id>/amenities/<amenity_id>',
                 methods=['POST'],
                 strict_slashes=False)
def link_amenity_place(place_id, amenity_id):
    """ Link a Amenity and a Place """
    place = storage.get("Place", place_id)
    amenity = storage.get("Amenity", amenity_id)
    if place is None or amenity is None:
        abort(404)
    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        place_amenities = place.amenities
    else:
        place_amenities = place.amenity_ids
    if amenity in place_amenities:
        return jsonify(amenity.to_dict())
    place_amenities.append(amenity)
    place.save()
    return make_response(jsonify(amenity.to_dict()), 201)
