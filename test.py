from keras.models import load_model  # TensorFlow is required for Keras to work
from PIL import Image, ImageOps  # Install pillow instead of PIL
import numpy as np
from keras.preprocessing import image

# Disable scientific notation for clarity
# np.set_printoptions(suppress=True)

# Load the model
# model = load_model("model.h5", compile=False)

# # Load the labels
# class_names = open("labels.txt", "r").readlines()

# # Create the array of the right shape to feed into the keras model
# # The 'length' or number of images you can put into the array is
# # determined by the first position in the shape tuple, in this case 1
# data = np.ndarray(shape=(1, 150, 150, 3), dtype=np.float32)

# # Replace this with the path to your image
# image = Image.open("uploads/tumpeng_menoreh.002.jpg").convert("RGB")

# # resizing the image to be at least 224x224 and then cropping from the center
# size = (150, 150)
# image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

# # turn the image into a numpy array
# image_array = np.asarray(image)

# # Normalize the image
# normalized_image_array = (image_array.astype(np.float32) / 255)

# # Load the image into the array
# data[0] = normalized_image_array

# # Predicts the model
# prediction = model.predict(data)
# index = np.argmax(prediction)
# class_name = class_names[index]
# confidence_score = prediction[0][index]

# # Print prediction and confidence score
# # print("Class:", class_name[2:], end="")
# # print("Confidence Score:", confidence_score)

# print(prediction[0])


# Membaca file labels.txt
with open("labels.txt", "r") as file:
    labels = file.read().splitlines()

# Load model
loaded_model = load_model("model.h5")

# Load image for prediction
img_path = "uploads/parangteritis.103.png"
img = image.load_img(img_path, target_size=(150, 150))
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0)
# img_array /= 100.0

# Make prediction
predictions = loaded_model.predict(img_array)

# Decode predictions
predicted_class = np.argmax(predictions)
predicted_label = labels[predicted_class]

print("Predicted label:", predicted_label)
print(img_path)
