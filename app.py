# import io
# import tensorflow as tf
# from tensorflow import keras
# import numpy as np
# from PIL.Image import Image

from flask import Flask, request, jsonify, abort, render_template
# from flask_smorest import Api
from resources.location import loc
from resources.users import us
from resources.predict import pre
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt


db = MySQL()
bcript = Bcrypt()


def create_app():
    app = Flask(__name__)
    app.config["API_TITLE"] = "VLOC REST API"
    app.config["API_VERSION"] = "v1.0.0"
    app.config.from_pyfile('settings.py')

    db.init_app(app)
    bcript.init_app(app)
    return app


app = create_app()

app.register_blueprint(loc)
app.register_blueprint(us)
app.register_blueprint(pre)


# model = keras.models.load_model("nn.h5")


# def transform_image(pillow_image):
#     data = np.asarray(pillow_image)
#     data = data / 255.0
#     data = data[np.newaxis, ..., np.newaxis]
#     # --> [1, x, y, 1]
#     data = tf.image.resize(data, [28, 28])
#     return data


# def predict(x):
#     predictions = model(x)
#     predictions = tf.nn.softmax(predictions)
#     pred0 = predictions[0]
#     label0 = np.argmax(pred0)
#     return label0


# @app.route("/prediction", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         file = request.files.get('file')
#         if file is None or file.filename == "":
#             return jsonify({"error": "no file"})

#         try:
#             image_bytes = file.read()
#             pillow_img = Image.open(io.BytesIO(image_bytes)).convert('L')
#             tensor = transform_image(pillow_img)
#             prediction = predict(tensor)
#             data = {"prediction": int(prediction)}
#             return jsonify(data)
#         except Exception as e:
#             return jsonify({"error": str(e)})

#     return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
    # app.run(host="0.0.0.0", port=3000, debug=True)


# api = Api(app)
