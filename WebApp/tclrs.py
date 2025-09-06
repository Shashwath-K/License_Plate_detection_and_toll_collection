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

# ==== [SETTINGS] ====
UPLOAD_DIR = 'uploads'
CSV_FILE = 'toll_data.csv'
CAMERA_INDEX = 0  # Default camera

# Ensure required directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Set Tesseract path (adjust only if needed)
if os.name == 'nt':  # Windows
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ==== [MODEL INIT] ====
vehicle_data = {
    'license_plate': ['ABC123', 'XYZ789', 'LMN456'],
    'vehicle_type': ['Car', 'Truck', 'Motorcycle']
}
df_vehicle = pd.DataFrame(vehicle_data)
label_encoder = LabelEncoder()
df_vehicle['vehicle_type_encoded'] = label_encoder.fit_transform(df_vehicle['vehicle_type'])

knn = KNeighborsClassifier(n_neighbors=1)
knn.fit(df_vehicle[['vehicle_type_encoded']], df_vehicle['vehicle_type'])

# ==== [STATIC TOLL FEES] ====
toll_fees = {
    'Car': 50,
    'Truck': 70,
    'Bus': 60,
    'Motorcycle': 30,
}

# ==== [APP STATE] ====
entries = []
captured_frame = None
reader = easyocr.Reader(['en'], gpu=False)

# ==== [HELPERS] ====
def recognize_number_plate(img):
    """Detect and OCR a license plate using OpenCV + Tesseract."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml')
    plates = plate_cascade.detectMultiScale(gray, 1.1, 10)

    for (x, y, w, h) in plates:
        roi = gray[y:y + h, x:x + w]
        number_plate_text = pytesseract.image_to_string(roi, config='--psm 8')
        clean_text = ''.join(filter(str.isalnum, number_plate_text))
        return clean_text, (x, y, w, h)

    return None, None

def process_image(image_input):
    """Fallback OCR using EasyOCR. Supports file path or np.array."""
    try:
        if isinstance(image_input, str):
            img = cv2.imread(image_input)
        else:
            img = image_input

        text_blocks = reader.readtext(img)
        results = [text for _, text, conf in text_blocks if conf > 0.25]
        return ' '.join(results).strip()
    except Exception as e:
        print(f"[EasyOCR Error]: {e}")
        return "Unknown"

def predict_vehicle_type(license_plate):
    if license_plate in df_vehicle['license_plate'].values:
        encoded = df_vehicle.loc[df_vehicle['license_plate'] == license_plate, 'vehicle_type_encoded'].values[0]
        return label_encoder.inverse_transform([encoded])[0]
    return "Unknown"

def get_toll_fee(vehicle_type, extra_fee=0):
    return toll_fees.get(vehicle_type, 0) + extra_fee

# ==== [ROUTES] ====

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

    try:
        save_path = os.path.join(UPLOAD_DIR, file.filename)
        file.save(save_path)

        img = cv2.imread(save_path)
        license_plate, _ = recognize_number_plate(img)

        if not license_plate:
            license_plate = process_image(save_path)

        vehicle_type = predict_vehicle_type(license_plate)
        return jsonify({'license_plate': license_plate, 'vehicle_type': vehicle_type})

    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'})

@app.route('/submit', methods=['POST'])
def submit_form():
    data = request.json
    license_plate = data.get('license_plate', 'Unknown')
    vehicle_type = data.get('vehicle_type', 'Unknown')
    additional_fee = int(data.get('additional_toll_fee', 0)) if str(data.get('additional_toll_fee')).isdigit() else 0

    toll_fee = get_toll_fee(vehicle_type, additional_fee)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    entry = {
        'License Plate': license_plate,
        'Vehicle Type': vehicle_type,
        'Toll Fee': toll_fee,
        'Date/Time': timestamp
    }

    entries.append(entry)
    pd.DataFrame(entries).to_csv(CSV_FILE, index=False)

    return jsonify({'success': True, 'entries': entries})

@app.route('/load', methods=['GET'])
def load_entries():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        entries.clear()
        entries.extend(df.to_dict(orient='records'))
    return jsonify(entries)

# ==== [VIDEO FEED] ====

def gen_frames():
    global captured_frame
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        raise RuntimeError("Cannot open camera")

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break

            license_plate, bbox = recognize_number_plate(frame)
            if bbox:
                x, y, w, h = bbox
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            captured_frame = frame_bytes

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture', methods=['POST'])
def capture():
    global captured_frame
    if captured_frame:
        try:
            np_frame = cv2.imdecode(np.frombuffer(captured_frame, np.uint8), cv2.IMREAD_COLOR)
            license_plate, _ = recognize_number_plate(np_frame)

            if not license_plate:
                license_plate = process_image(np_frame)

            vehicle_type = predict_vehicle_type(license_plate)
            return jsonify({'license_plate': license_plate, 'vehicle_type': vehicle_type})

        except Exception as e:
            return jsonify({'error': f'Capture failed: {str(e)}'})
    return jsonify({'error': 'No frame captured'})

# ==== [APP ENTRYPOINT] ====

if __name__ == '__main__':
    app.run(debug=True)
