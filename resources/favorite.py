from flask.views import MethodView
from flask_smorest import Blueprint
from flask import abort, request, jsonify

from db import location
from auth import token_required
from settings import mydb
fav = Blueprint("Favorites", __name__)

mysql = mydb


@fav.route("/favorite/<int:user_id>/<int:id>")
class FavoriteDetail(MethodView):
    @token_required
    @fav.response(200)
    def get(self, user_id, id):
        try:
            cursor = mysql.cursor()
            cursor.execute(
                f"""SELECT * from favorite where user_id={user_id} AND id={id}""")
            data = cursor.fetchone()
            if data is None:
                return jsonify({
                    "status": "fail",
                    "error": "favorite no found"
                }), 404

            row_headers = [x[0] for x in cursor.description]
            json_data = []
            json_data.append(dict(zip(row_headers, data)))
            cursor.close()

            location_result = location[json_data[0]['location_id']]
            return jsonify({
                "status": "success",
                "message": "succes get favorite",
                "favorite": location_result
            }), 200
        except KeyError:
            abort(404)

    @fav.response(200)
    @token_required
    def delete(self, user_id, id):
        try:
            cursor = mysql.cursor()
            cursor.execute(
                f"""SELECT * from favorite where user_id={user_id} AND id={id}""")
            data = cursor.fetchone()
            if data is None:
                return jsonify({
                    "status": "fail",
                    "error": "favorite no found"
                }), 404
            # cursor.execute("select * from ")
            db = mysql.cursor()
            query = f"""DELETE FROM favorite WHERE id={id}"""
            db.execute(query)
            mysql.commit()
            db.close()
            return jsonify({
                'status': 'success',
                'message': 'delete favorite successfully'
            }), 200

        except KeyError:
            abort(404)


@fav.route("/favorite/<int:user_id>")
class Favorite(MethodView):
    @fav.response(201, "Favorite")
    @token_required
    def get(self, user_id):
        try:
            favorite = mysql.cursor()
            favorite.execute(
                f"""SELECT * FROM favorite where user_id={user_id}""")
            data = favorite.fetchall()
            if not data:
                return jsonify({
                    "status": "fail",
                    "message": "No favorites found"
                }), 404
            row_headeres = [x[0] for x in favorite.description]
            json_data = []
            for result in data:
                json_data.append(dict(zip(row_headeres, result)))
            # json_data.append
            favorite.close()
            return jsonify({
                "status": "success",
                "message": "get favorite from users",
                "favorite": json_data
            }), 201
        except TabError:
            abort(404)

    @fav.response(200)
    @token_required
    def post(self, user_id):
        try:
            location_id = request.form['location_id']
            # location_exist = location[location_id]
            location_exist = [
                x for x in location.values() if x["id"] == location_id
            ]
            if not location_exist:
                return jsonify({
                    "status": "fail",
                    "error": "Location does not exist."
                }), 404

            query = f"""INSERT INTO favorite(user_id, location_id, destination_img_url) VALUES({user_id}, '{location_id}', '{location_exist[0]["destination_img_url"]}')"""
            post = mysql.cursor()
            post.execute(query)
            mysql.commit()
            post.close()
            return jsonify({
                "status": "success",
                "Message": "new favorite added",
            }), 200

        except Exception as e:
            return jsonify({
                "status": "fail",
                "message": str(e)
            }), 400
