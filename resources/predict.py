import tensorflow as tf
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.models import load_model
from keras.preprocessing import image
# from PIL import Image
import numpy as np
import os

from flask import jsonify, abort, request
from flask_smorest import Blueprint
from flask.views import MethodView
from werkzeug.utils import secure_filename

pre = Blueprint("Prediction", __name__)


def model_predict(img_path, model):
    img = image.load_img(img_path, target_size=(32, 32))

    img1 = image.img_to_array(img)
    img2 = np.expand_dims(img1, 0)

    pred = model.predict_classes(img2)
    return pred


@pre.route('/predict')
class Prediction(MethodView):
    @pre.doc(body=dict(image={"type": "string", "description": "A base64 encoded string of an image"}))
    def post(self):
        """Make a prediction on the uploaded image"""
        # Load the model
        model = load_model("model.h5")

        # Get the image from the request body and pre-process it
        img_str = request.files['file']
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'resources', secure_filename(img_str.filename))

        preds = model_predict(file_path, model)

        return jsonify(preds), 201
