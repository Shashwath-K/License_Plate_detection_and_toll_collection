from flask import Flask, render_template, request, jsonify, Response
from PIL import Image
import cv2
import pytesseract
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
import easyocr
import datetime
import os
import numpy as np
app = Flask(__name__)

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize vehicle type classifier with sample data
vehicle_data = {
    'license_plate': ['ABC123', 'XYZ789', 'LMN456'],
    'vehicle_type': ['Car', 'Truck', 'Motorcycle']
}
df_vehicle = pd.DataFrame(vehicle_data)
label_encoder = LabelEncoder()
df_vehicle['vehicle_type_encoded'] = label_encoder.fit_transform(df_vehicle['vehicle_type'])
knn = KNeighborsClassifier(n_neighbors=1)
knn.fit(df_vehicle[['vehicle_type_encoded']], df_vehicle['vehicle_type'])

# Define fixed toll fees for different vehicle types
toll_fees = {
    'Car': 50,
    'Truck': 70,
    'Bus': 60,
    'Motorcycle': 30,
}

entries = []

def recognize_number_plate(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    plates = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml').detectMultiScale(gray, 1.1, 10)
    for (x, y, w, h) in plates:
        roi = gray[y:y + h, x:x + w]
        number_plate_text = pytesseract.image_to_string(roi, config='--psm 8')
        number_plate_text = ''.join(e for e in number_plate_text if e.isalnum())  # Clean the text
        return number_plate_text, (x, y, w, h)
    return None, None

def predict_vehicle_type(license_plate):
    if license_plate in df_vehicle['license_plate'].values:
        vehicle_type_encoded = df_vehicle.loc[df_vehicle['license_plate'] == license_plate, 'vehicle_type_encoded'].values[0]
        return label_encoder.inverse_transform([vehicle_type_encoded])[0]
    return "Unknown"

def process_image(image_path):
    img = cv2.imread(image_path)
    reader = easyocr.Reader(['en'], gpu=False)
    text_ = reader.readtext(img)
    result_texts = []
    threshold = 0.25
    for bbox, text, score in text_:
        if score > threshold:
            result_texts.append(text)
    return ' '.join(result_texts)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file:
        file_path = os.path.join('uploads', file.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
        license_plate, _ = recognize_number_plate(cv2.imread(file_path))
        if not license_plate:
            license_plate = process_image(file_path)  # Use EasyOCR if Tesseract fails
        vehicle_type = predict_vehicle_type(license_plate)
        return jsonify({'license_plate': license_plate, 'vehicle_type': vehicle_type})
    return jsonify({'error': 'File upload failed'})

@app.route('/submit', methods=['POST'])
def submit_form():
    data = request.json
    license_plate = data['license_plate']
    vehicle_type = data['vehicle_type']
    additional_toll_fee = int(data['additional_toll_fee']) if data['additional_toll_fee'].isdigit() else 0
    toll_fee = toll_fees.get(vehicle_type, 0) + additional_toll_fee
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = {'License Plate': license_plate, 'Vehicle Type': vehicle_type, 'Toll Fee': toll_fee, 'Date/Time': current_time}
    entries.append(entry)
    df = pd.DataFrame(entries)
    df.to_csv('toll_data.csv', index=False)
    return jsonify({'success': True, 'entries': entries})

@app.route('/load', methods=['GET'])
def load_entries():
    if os.path.exists('toll_data.csv'):
        df = pd.read_csv('toll_data.csv')
        entries.clear()
        for _, row in df.iterrows():
            entries.append(row.to_dict())
    return jsonify(entries)

captured_frame = None

def gen_frames():
    global captured_frame
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            license_plate, bbox = recognize_number_plate(frame)
            if bbox:
                x, y, w, h = bbox
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            captured_frame = frame
    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture', methods=['POST'])
def capture():
    global captured_frame
    if captured_frame is not None:
        np_frame = cv2.imdecode(np.frombuffer(captured_frame, np.uint8), cv2.IMREAD_COLOR)
        license_plate, _ = recognize_number_plate(np_frame)
        if not license_plate:
            license_plate = process_image(np_frame)
        vehicle_type = predict_vehicle_type(license_plate)
        return jsonify({'license_plate': license_plate, 'vehicle_type': vehicle_type})
    return jsonify({'error': 'No frame captured'})

if __name__ == '__main__':
    app.run(debug=True)
