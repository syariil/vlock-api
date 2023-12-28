from flask.views import MethodView
from flask_smorest import Blueprint
from flask import abort, request, jsonify

from db import location
from auth import token_required
from settings import mydb
fav = Blueprint("Favorites", __name__)

mysql = mydb


@fav.route("/favorite/<int:user_id>/<string:location_id>")
class FavoriteDetail(MethodView):
    @token_required
    @fav.response(200)
    def get(self, user_id, location_id):
        try:
            mysql.ping()
            cursor = mysql.cursor()
            cursor.execute(
                f"""SELECT * from favorite where user_id={user_id} AND location_id='{location_id}'""")
            data = cursor.fetchone()
            if data is None:
                cursor.close()
                mysql.close()
                return jsonify({
                    "status": "fail",
                    "error": "favorite no found"
                }), 404

            # json_data = jsonify(data)
            cursor.close()
            
            location_result = location[data['location_id']]
            mysql.close()
            return jsonify({
                "status": "success",
                "message": "succes get favorite",
                "favorite": location_result
            }), 200
        except KeyError:
            abort(404)

    @fav.response(200)
    @token_required
    def delete(self, user_id, location_id):
        try:
            mysql.ping()
            cursor = mysql.cursor()
            cursor.execute(
                f"""SELECT * from favorite where user_id={user_id} AND location_id='{location_id}'""")
            data = cursor.fetchone()
            if data is None:
                cursor.close()
                mysql.close()
                return jsonify({
                    "status": "fail",
                    "error": "favorite no found"
                }), 404
            cursor.close()
            mysql.close()
            # cursor.execute("select * from ")
            mysql.ping()
            db = mysql.cursor()
            query = f"""DELETE FROM favorite WHERE location_id='{location_id}'"""
            db.execute(query)
            mysql.commit()
            db.close()
            mysql.close()
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
            mysql.ping()
            favorite = mysql.cursor()
            favorite.execute(
                f"""SELECT * FROM favorite where user_id={user_id}""")
            data = favorite.fetchall()
            if not data:
                favorite.close()
                mysql.close()
                return jsonify({
                    "status": "fail",
                    "message": "No favorites found"
                }), 404
            # json_data.append
            favorite.close()
            mysql.close()
            return jsonify({
                "status": "success",
                "message": "get favorite from users",
                "favorite": data
            }), 201
        except Exception as e:
            return jsonify({
                "status" : "fail",
                "message" : str(e)
            })

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

            # check if location

            query = f"""INSERT INTO favorite(user_id, location_id, destination_img_url) VALUES({user_id}, '{location_id}', '{location_exist[0]["destination_img_url"]}')"""
            mysql.ping()
            post = mysql.cursor()
            post.execute(query)
            mysql.commit()
            post.close()
            mysql.close()
            return jsonify({
                "status": "success",
                "Message": "new favorite added",
            }), 200

        except Exception as e:
            return jsonify({
                "status": "fail",
                "message": str(e)
            }), 400
