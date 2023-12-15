# import tensorflow as tf
from keras.models import load_model
from keras.preprocessing import image
from PIL import Image, ImageOps
from keras.utils import img_to_array
import io
import os
from keras.applications.vgg16 import decode_predictions
import numpy as np
import tensorflow as tf

from flask import jsonify, abort, request
from flask_smorest import Blueprint
from flask.views import MethodView
from werkzeug.utils import secure_filename
import base64
from PIL import Image

pre = Blueprint("Prediction", __name__)


model = load_model("model.h5")
model.make_predict_function()


def predict_label(img_path):
    i = image.load_img(img_path, target_size=(150, 150))
    i = image.img_to_array(i)/255.0
    i = i.reshape(1, 150, 150, 3)
    p = model.predict(i)
    p = np.argmax(p, axis=-1)
    return p

# def preprocess_img(img_path):
#     op_img = Image.open(io.BytesIO(img_path.read()))
#     # # img_resize = op_img.resize((224, 224))
#     # img2arr = img_to_array(op_img) / 255.0
#     # # img_reshape = img2arr.reshape(1, 224, 224, 3)
#     # return img2arr
#     img = image.load_img(op_img, target_size=(125, 110))
#     img_array = image.img_to_array(img)
#     img_array = np.expand_dims(img_array, axis=0)
#     img_array /= 255.0  # Normalize the image
#     return img_array


# def predict_result(predict):
#     pred = model.predict(predict)
#     return np.argmax(pred[0])


# def model_predict(img_path, model):
#     img = image.load_img(img_path, target_size=(150, 150))

#     # Preprocessing the image
#     x = image.img_to_array(img)
#     # x = np.true_divide(x, 255)
#     x = np.expand_dims(x, axis=0)

#     # Be careful how your trained model deals with the input
#     # otherwise, it won't make correct prediction!
#     x = preprocess_input(x, mode='caffe')

#     preds = model.predict(x)
#     return preds


def transform_image(pillow_image):
    img = pillow_image.resize((150, 150))
    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    return tf.convert_to_tensor(img_array)


def predict(x):
    predictions = model.predict(x)
    predictions = tf.nn.softmax(predictions)
    # pred0 = predictions[0]
    # label0 = np.argmax(predictions)
    # return label0
    prod0 = predictions
    label0 = np.argmax(prod0)

    top5_predicted_classes = np.argsort(prod0)
    # top5_predicted_probabilities = prod0[top5_predicted_classes]
    return label0, top5_predicted_classes
    # , top5_predicted_probabilities

    # class_names = open("labels.txt", "r").readlines()
    # prediction = model.predict(x)
    # index = np.argmax(prediction)
    # class_name = class_names[index]
    # confidence_score = prediction[0][index]

    # return class_name, confidence_score


def preprocess_image(image, target_size):
    if image.mode != "RGB":
        image = image.convert("RGB")
    image = image.resize(target_size)
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = image / 255.0
    return image


# @app.route("/prediction", methods=["GET", "POST"])
# def prediction():
#     if request.method == "POST":
#         file = request.files['file']
#         if file is None or file.filename == "":
#             return jsonify({"error": "no file"})

#         try:
#             image_bytes = file.read()
#             pillow_img = Image.open(io.BytesIO(image_bytes)).convert('L')
#             tensor = transform_image(pillow_img)
#             prediction = predict(tensor)
#             data = {"prediction": int(prediction)}
#             return jsonify(file.filename)
#         except KeyError as e:
#             return jsonify({"error": str(e)})

#     return "OK"


@pre.route('/predict')
class Prediction(MethodView):
    @pre.response(201)
    def post(self):
        """Make a prediction on the uploaded image"""
        file = request.files['file']
        if file is None or file.filename == "":
            return jsonify({"error": "no file"})
        file_path = 'uploads/' + file.filename
        file.save(file_path)
        try:
            # img = image.load_img(io.BytesIO(file.read()),
            #                      target_size=(224, 224))
            # img_array = image.img_to_array(img)
            # img_array = np.expand_dims(img_array, axis=0)
            # img_array /= 255
            # prediction = model.predict(img_array)
            prediction = predict_label(file_path)
            return jsonify(str(prediction))
            # image_bytes = file.read()
            # pillow_img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            # tensor = transform_image(pillow_img)
            # label = decode_predictions(prediction)
            # label = label[0][0]
            # assuming prediction is a tuple containing an int, array and array
            # class_index = prediction[0]
            # classes = prediction[1].tolist()
            # probabilities = prediction[2].tolist()

            # creating a dictionary to store the readable data
            # readable_data = {
            #     "class_index": class_index,
            #     "classes": classes
            #     # "probabilities": probabilities
            # }
            # pred = model.predict(tensor)
            # y_classes = pred.argmax(-1)
            # pred = predict_img(file)
            # return jsonify(str(pred))
            # return jsonify({
            #     "class_index": class_index,
            #     "classes" : "predi"
            # })

            # image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            # processed_image = preprocess_image(image, target_size=(150, 150))

            # prediction = model.predict(processed_image)
            # classess_x = np.argmax(prediction, axis=1)

            # # response = {
            # #     'prediction': {
            # #         'dog': prediction[0][0],
            # #         'cat': prediction[0][1]
            # #     }
            # # }
            # return jsonify(str(classess_x))

            #  f = request.files['file']

            # Save the file to ./uploads
            # basepath = os.path.dirname()
            # file_path = os.path.join(
            #     basepath, 'uploads', secure_filename(file.filename))
            # file.save(file_path)

            # Make prediction
            # preds = model_predict(tensor, model)

            # # Process your result for human
            # # pred_class = preds.argmax(axis=-1)            # Simple argmax
            # pred_class = decode_predictions(preds, top=1)   # ImageNet Decode
            # result = str(pred_class[0][0][1])               # Convert to string
            # return result

        except KeyError as e:
            return jsonify({"error": str(e)})
