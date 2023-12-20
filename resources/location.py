import uuid
from flask.views import MethodView
from flask_smorest import Blueprint
from db import location
from schemas import LocationSchema, LocationUpdateSchema
import datetime
from flask import abort, jsonify, request
import random
from auth import token_required

loc = Blueprint("Locations", __name__, description="Operations on locations")


def json_abort(status_code, message):
    data = {
        'code': status_code,
        'status': "fail",
        'message': message
    }

    response = jsonify(data)
    response.status_code = status_code
    abort(response)


@loc.route("/location/<string:id>")
class Location(MethodView):
    @loc.response(200, LocationSchema)
    @token_required
    def get(self, id):
        """Get a single location by ID"""
        try:
            predict_number = location[id]["predict_number"]
            list_rand = list(range(1, 6 + 1))
            random.shuffle(list_rand)
            return jsonify({
                "status": "success",
                "message": "success get destination",
                "destionation": location[id],
                # https://storage.googleapis.com/vloc-project/dataset/0/0.001.jpg
                "more_img_url1": f"https://storage.googleapis.com/vloc-project/dataset/{predict_number}/{predict_number}.00{list_rand[0]}.jpg",
                "more_img_url2": f"https://storage.googleapis.com/vloc-project/dataset/{predict_number}/{predict_number}.00{list_rand[1]}.jpg",
                "more_img_url3": f"https://storage.googleapis.com/vloc-project/dataset/{predict_number}/{predict_number}.00{list_rand[2]}.jpg"
            })
            # return location[id]
        except KeyError:
            json_abort(404, "location not found.")

    @token_required
    def delete(self, id):
        try:
            del location[id]
            return jsonify({
                "status": "success",
                "message": f"Successfully deleted the destination with id={id}"
            })
        except KeyError:
            json_abort(404, "location not found.")

    @loc.arguments(LocationUpdateSchema)
    @loc.response(201, LocationSchema)
    @token_required
    def put(self, location_data, id):
        try:
            locations = location[id]
            locations["updateAt"] = datetime.datetime.now()
            locations |= location_data
            return jsonify({
                "status": "success",
                "message": "Successfully updated.",
                "destination_name": locations['destination_name']

            })
        except KeyError:
            json_abort(404, "location not found.")


@loc.route("/location")
class LocationList(MethodView):
    @loc.response(200, LocationSchema(many=True))
    @token_required
    def get(self):
        try:
            category = request.args["category"]
            location_category = [
                x for x in location.values() if x["category"] == category]
            return jsonify(
                location_category
            )
        except KeyError:
            return location.values()

    @loc.arguments(LocationSchema)
    @loc.response(201, LocationSchema)
    @token_required
    def post(self, location_data):
        for loc in location.values():
            if loc['destination_name'] == location_data['destination_name']:
                json_abort(409, "Destinantion is already exist")
        try:
            id = uuid.uuid4().hex
            createdAt = datetime.datetime.now()
            updateAt = datetime.datetime.now()
            locations = {**location_data, "id": id,
                         "createdAt": createdAt, "updateAt": updateAt}
            location[id] = locations

            return jsonify({
                'status': 'success',
                'code': 201,
                'message': f'add new destination success',
                'data': {
                    'destination_name': location[id]["destination_name"],
                    "id": location[id]["id"]
                }
            })
        except KeyError:
            return json_abort(500, "Server error")
