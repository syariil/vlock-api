import uuid
from flask.views import MethodView
from flask_smorest import Blueprint
from db import location
from schemas import LocationSchema, LocationUpdateSchema
import datetime
from flask import abort, jsonify


loc = Blueprint("Locations", __name__, description="Operations on locations")


def json_abort(status_code, message):
    data = {
        'code': status_code,
        'message': message
    }

    response = jsonify(data)
    response.status_code = status_code
    abort(response)


@loc.route("/location/<string:id>")
class Location(MethodView):
    @loc.response(200, LocationSchema)
    def get(self, id):
        """Get a single location by ID"""
        try:
            return location[id]
        except KeyError:
            json_abort(404, "location not found.")

    def delete(self, id):
        try:
            del location[id]
            return {"message": "Item deleted"}
        except KeyError:
            json_abort(404, "location not found.")

    @loc.arguments(LocationUpdateSchema)
    @loc.response(201, LocationSchema)
    def put(self, location_data, id):
        try:
            locations = location[id]
            locations["updateAt"] = datetime.datetime.now()
            locations |= location_data
            return locations
        except KeyError:
            json_abort(404, "location not found.")


@loc.route("/location")
class LocationList(MethodView):
    @loc.response(200, LocationSchema(many=True))
    def get(self):
        return location.values()

    @loc.arguments(LocationSchema)
    @loc.response(201, LocationSchema)
    def post(self, location_data):
        for loc in location.values():
            if loc['title'] == location_data['title']:
                json_abort(409, "data is already exist")

        id = uuid.uuid4().hex
        createdAt = datetime.datetime.now()
        updateAt = datetime.datetime.now()
        locations = {**location_data, "id": id,
                     "createdAt": createdAt, "updateAt": updateAt}
        location[id] = locations

        return locations
