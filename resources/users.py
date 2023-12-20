from flask.views import MethodView
from flask_smorest import Blueprint
from flask import abort, request, jsonify
from flask_mysqldb import MySQL
import datetime
import os
from google.cloud import storage
from auth import token_required
from flask_bcrypt import Bcrypt
import jwt
import settings

# load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"vloc-project.json"

storage_client = storage.Client()
storage_name = storage_client.bucket('vloc-project')

us = Blueprint('Users', __name__)

mysql = MySQL()
bcrypt = Bcrypt()


@us.route('/users/<int:id>')
class Users(MethodView):
    @us.response(200, 'User')
    @token_required
    def get(self, id):
        try:
            cursor = mysql.connection.cursor()
            cursor.execute(f"""SELECT * FROM user where id={id}""")
            data = cursor.fetchone()
            if data is None:
                return jsonify({
                    "status": "fail",
                    "message": "user not found"
                }), 404

            row_headers = [x[0] for x in cursor.description]
            json_data = []
            json_data.append(dict(zip(row_headers, data)))
            cursor.close()
            return jsonify(json_data), 200
        except KeyError:
            abort(404)

    @us.response(200)
    @token_required
    def delete(self, id):
        try:
            check = mysql.connection.cursor()
            query = f'''SELECT username FROM user WHERE id={id} '''
            check.execute(query)
            data = check.fetchone()
            if data is None:
                return jsonify({
                    "status": "fail",
                    "message": "User Not Found"
                }), 404

            check.execute(f'''select * from favorite where user_id={id}''')
            favorite = check.fetchone()
            if favorite:
                # remove the record of this user's favorite from favorite table
                sql_command = f'''DELETE FROM favorite WHERE user_id="{id}"'''
                check.execute(sql_command)
                mysql.connection.commit()

            check.close()
            db = mysql.connection.cursor()
            query = f"""DELETE FROM user WHERE id={id}"""
            db.execute(query)
            mysql.connection.commit()
            db.close()
            return jsonify({
                'status': 'success',
                'message': 'delete user successfully'
            }), 200
        except KeyError:
            return {'error': 'Not allowed to perform the DELETE operation here.'}, 405


@us.route('/users/profile/<int:id>')
class UserUpdateProfile(MethodView):
    @us.response(200)
    @token_required
    def put(self, id):
        """"update user from id"""
        try:
            image = request.files['image']
            # request file
            if image.filename == "":
                return jsonify({
                    "status": "fail",
                    "message": "profile not found"
                }), 409
            # files is images
            if "image" not in image.content_type:
                return jsonify({
                    "status": "fail",
                    "message": "profile image should be image"
                }), 409

            # get image extension
            image_ext = os.path.splitext(image.filename[::1])

            # get username
            cursor = mysql.connection.cursor()
            cursor.execute(f"""SELECT username FROM user where id={id}""")
            username = cursor.fetchone()
            if username is None:
                return jsonify({"message": "invalid ID"}), 403
            cursor.close()

            # set name file and save it
            time = datetime.datetime.now()
            filename1 = f"{time.strftime('%m%d%H%M%S')}_{username[0]}{image_ext[1]}"
            image.filename = filename1
            filename = image.filename
            file_path = os.path.join('static/images', filename)
            image.save(file_path)

            # upload image to bucket
            blob = storage_name.blob("profile/" + image.filename)
            blob.upload_from_filename("static/images/" + image.filename)
            # update data in database
            db = mysql.connection.cursor()
            image_url = f"https://storage.cloud.google.com/vloc-project/profile/{filename}"
            db.execute(
                f"""UPDATE user SET image="{image_url}" where id={id}""")
            mysql.connection.commit()
            db.close()
            # remove file from local directory
            os.remove("static/images/" + image.filename)

            return jsonify({
                "status": "success",
                "message": "update profile successfully",
            }), 200
        except KeyError:
            return jsonify({
                "status": "fail",
                "message": "just recive request file image"
            }), 404


@us.route('/users')
class UserList(MethodView):
    @us.response(200, 'Success')
    @token_required
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


@us.route("/register")
class Register(MethodView):
    @us.response(201, "User registered successfully.")
    @us.doc(description="Register an account.",
            responses={
                409: "Email address already in use."})
    def post(self):
        try:

            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            image = 'https://storage.cloud.google.com/vloc-project/profile/default-image.jpg'
            createdAt = datetime.datetime.now()
            updateAt = datetime.datetime.now()

            db = mysql.connection.cursor()
            db.execute(
                f"""SELECT username, email from `user` WHERE username='{username}' OR email='{email}'""")
            check = db.fetchall()
            if (len(check) == 0):
                db.close()

                hashPass = bcrypt.generate_password_hash(
                    password, 8).decode("utf-8")

                query = f"""INSERT INTO user(username, email, password, image, createdAt, updateAt) VALUES('{username}', '{email}', "{hashPass}",'{image}','{createdAt}','{updateAt}')"""
                update = mysql.connection.cursor()
                update.execute(query)
                mysql.connection.commit()
                update.close()
                return jsonify({
                    'status': 'success',
                    'message': 'New user created!'
                }), 201
            else:
                response = jsonify({
                    'status': 'fail',
                    'message': 'Username or Email already exists.'
                })
                response.status_code = 400
                return response

        except KeyError:
            abort(404)


@us.route("/login")
class Login(MethodView):
    @us.response(200, "Logged in successfully.")
    def post(self):
        email = request.form["email"]
        password_req = request.form["password"]

        try:

            db = mysql.connection.cursor()
            query = f"""SELECT * FROM `user` WHERE email="{email}" """
            db.execute(query)
            result = db.fetchone()
            if not result:
                return jsonify({
                    "status": "error",
                    "data": None,
                    "message": "User does not exist."
                }), 404

            # Checking if the password is correct using bcrypt compare method
            row_headers = [x[0] for x in db.description]
            json_data = []
            json_data.append(dict(zip(row_headers, result)))

            pass_user = json_data[0]['password']
            generatePass = bcrypt.check_password_hash(pass_user, password_req)

            if not generatePass:
                return jsonify({
                    "status": "fail",
                    "message": "wrong password"
                }), 403

            token = jwt.encode({
                'iat': datetime.datetime.utcnow(),                          # Current time
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=3),
                'id': json_data[0]["id"]
            },
                settings.SECRET_KEY, algorithm="HS256")
            db.close()

            return jsonify({
                "status": "success",
                "username": json_data[0]["username"],
                "token": token
            })

        except KeyError:
            return jsonify({
                "status": "fail",
                "message": "Key Error. Please check your data."
            })
