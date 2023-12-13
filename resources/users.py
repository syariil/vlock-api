from flask.views import MethodView
from flask_smorest import Blueprint
from flask import abort, request, jsonify, render_template
# from json import dumps
from flask_mysqldb import MySQL
import datetime
from flask_bcrypt import Bcrypt
import os

us = Blueprint('Users', __name__)

mysql = MySQL()
bcrypt = Bcrypt()


@us.route('/users/<int:id>')
class Users(MethodView):
    @us.response(200, 'User')
    def get(self, id):
        try:
            cursor = mysql.connection.cursor()
            cursor.execute(f"""SELECT * FROM user where id={id}""")
            data = cursor.fetchone()
            if data is None:
                return jsonify({"message": "user not found"}), 404

            row_headers = [x[0] for x in cursor.description]
            json_data = []
            json_data.append(dict(zip(row_headers, data)))
            cursor.close()
            return jsonify(json_data), 200
        except KeyError:
            abort(404)

    @us.response(202)
    def put(self, id):
        """"update user from id"""
        try:
            image = request.files['image']
            if image.filename == "":
                return jsonify({"message": "profile not found"}), 409
            if "image" not in image.content_type:
                return jsonify({"message": "profile image should be image"}), 409
            image_ext = os.path.splitext(image.filename[::1])

            cursor = mysql.connection.cursor()
            cursor.execute(f"""SELECT username FROM user where id={id}""")
            username = cursor.fetchone()
            if username is None:
                return jsonify({"message": "invalid ID"}), 403
            cursor.close()
            filename = f'{datetime.datetime.now()}_{username[0]}{image_ext[1]}'
            db = mysql.connection.cursor()
            db.execute(f"""UPDATE user SET image="{filename}" where id={id}""")
            mysql.connection.commit()
            db.close()
            return jsonify({"message": "update profile successfully"}), 201
            # cursor.close()
            # filename = f''
        except KeyError:
            return jsonify({"message": "just recive request file image"}), 404

    @us.response(201)
    def delete(self, id):
        try:
            check = mysql.connection.cursor()
            query = f'''SELECT username FROM user WHERE id={id} '''
            check.execute(query)
            data = check.fetchone()
            if data is None:
                return {"message": "User Not Found"}, 404
            check.close()
            db = mysql.connection.cursor()
            query = f"""DELETE FROM user WHERE id={id}"""
            db.execute(query)
            mysql.connection.commit()
            db.close()
            return {'message': 'delete user successfully'}, 201
        except KeyError:
            abort(404)


@us.route('/users')
class UserList(MethodView):
    @us.response(200, 'Success')
    def get(self):
        """Get all users"""
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("SELECT * FROM User")
            # this will extract row headers
            row_headers = [x[0] for x in cursor.description]
            rv = cursor.fetchall()
            json_data = []
            for result in rv:
                json_data.append(dict(zip(row_headers, result)))
            cursor.close()
            return jsonify(json_data), 200
        except KeyError:
            abort(404)

    # @us.arguments()
    @us.response(201)
    def post(self):
        """Create a new user"""
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            image = 'default-image.jpg'
            createdAt = datetime.datetime.now()
            updateAt = datetime.datetime.now()

            db = mysql.connection.cursor()
            db.execute(
                f"""SELECT username, email from `user` WHERE username='{username}' OR email='{email}'""")
            check = db.fetchall()
            if (len(check) == 0):
                db.close()
                hashedPassword = bcrypt.generate_password_hash(
                    password, 4)
                query = f"""INSERT INTO user(username, email, password, image, createdAt, updateAt) VALUES('{username}', '{email}', "{hashedPassword}",'{image}','{createdAt}','{updateAt}')"""
                update = mysql.connection.cursor()
                update.execute(query)
                mysql.connection.commit()
                update.close()
                return jsonify({'message': 'New user created!'}), 201
            else:
                response = jsonify(
                    {'message': 'Username or Email already exists.'})
                response.status_code = 400
                return response

        except KeyError:
            abort(404)
