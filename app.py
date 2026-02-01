import os
from flask import Flask, request, render_template, send_file, jsonify
from flask_cors import CORS
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"

# Ensure uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
elif not os.path.isdir(UPLOAD_FOLDER):
    os.remove(UPLOAD_FOLDER)
    os.makedirs(UPLOAD_FOLDER)

# Face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['image']
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        return jsonify({"filename": file.filename})
    return jsonify({"error": "No file uploaded"}), 400

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    filename = data['filename']
    operation = data['operation']

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    img = cv2.imread(filepath)

    if img is None:
        return jsonify({"error": "Image not found"}), 404

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ----------- OPERATIONS -----------
    if operation == "grayscale":
        result = gray

    elif operation == "threshold":
        _, result = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    elif operation == "adaptive":
        result = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                       cv2.THRESH_BINARY, 11, 2)

    elif operation == "canny":
        result = cv2.Canny(gray, 100, 200)

    elif operation == "contours":
        edges = cv2.Canny(gray, 100, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        result = img.copy()
        cv2.drawContours(result, contours, -1, (0, 255, 0), 2)

    elif operation == "blur":
        result = cv2.GaussianBlur(img, (7, 7), 0)

    elif operation == "resize_up":
        result = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

    elif operation == "resize_down":
        result = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)

    elif operation == "invert":
        result = cv2.bitwise_not(img)

    elif operation == "sepia":
        kernel = np.array([[0.272, 0.534, 0.131],
                           [0.349, 0.686, 0.168],
                           [0.393, 0.769, 0.189]])
        result = cv2.transform(img, kernel)
        result = np.clip(result, 0, 255).astype(np.uint8)

    elif operation == "sketch":
        gray_blur = cv2.GaussianBlur(gray, (21, 21), 0)
        result = cv2.divide(gray, gray_blur, scale=256)

    elif operation == "cartoon":
        gray_blur = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray_blur, 255,
                                      cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY, 9, 9)
        color = cv2.bilateralFilter(img, 9, 250, 250)
        result = cv2.bitwise_and(color, color, mask=edges)

    elif operation == "rotate_90":
        result = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

    elif operation == "flip_horizontal":
        result = cv2.flip(img, 1)

    elif operation == "flip_vertical":
        result = cv2.flip(img, 0)

    elif operation == "masking":
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower = np.array([0, 120, 70])
        upper = np.array([10, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(img, img, mask=mask)

    else:
        result = img.copy()

    # Save file
    output_path = os.path.join(UPLOAD_FOLDER, "processed_" + filename)
    cv2.imwrite(output_path, result)

    return send_file(output_path, mimetype='image/jpeg')


if __name__ == "__main__":
    app.run(debug=True)
