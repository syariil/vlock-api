from keras.models import load_model
from keras.utils import img_to_array, load_img
import os
import numpy as np
from flask import jsonify, request
from flask_smorest import Blueprint
from flask.views import MethodView
from db import location
from auth import token_required


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow logging
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

pre = Blueprint("Prediction", __name__)

model = load_model("model.h5")


def read_image(filename):
    # Adjust target size as needed
    img = load_img(filename, target_size=(150, 150))
    x = img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = x / 255.0  # Normalize pixel values
    return x


ALLOWED_EXT = {'jpg', 'jpeg', 'png'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


@pre.route('/predict')
class Prediction(MethodView):
    @pre.response(201)
    @token_required
    def post(self):
        """Make a prediction on the uploaded image"""
        file = request.files['file']
        # file on request
        if file is None or file.filename == "":
            return jsonify({
                "status": "fail",
                "message": "no file found"
            }), 404
        # file is images
        if not allowed_file(file.filename):
            return jsonify({
                "status": "fail",
                "message": "file should be image."
            }), 409
        try:
            # save file in local diractory
            filename = file.filename
            file_path = os.path.join('static/images', filename)
            file.save(file_path)

            # Make prediction
            img_array = read_image(file_path)
            prediction = model.predict(img_array)
            classes_x = np.argmax(prediction, axis=1)
            prob = prediction[0][classes_x]
            prob = round(float(prob), 3) * 100
            place = [x for x in location.values() if x["predict_number"]
                     == classes_x[0]]

            # remove file request in directory
            os.remove(file_path)

            result_json = {
                "id": place[0]['id'],
                "destination_name" : place[0]['destination_name'],
                "address": place[0]['address'],
                "destination_img_url": place[0]['destination_img_url']
            }
#            return jsonify(str(classes_x)), 200

            return jsonify({
                'status': 'success',
                'result': result_json,
                "probabilitis": f"{float(prob)}%"
            }), 200

        except KeyError as e:
            return jsonify({"error": str(e)})
