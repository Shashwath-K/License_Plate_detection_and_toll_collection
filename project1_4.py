import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import pytesseract
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
import os

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize vehicle type classifier
vehicle_data = {
    'license_plate': ['ABC123', 'XYZ789', 'LMN456'],
    'vehicle_type': ['Car', 'Truck', 'Motorcycle']
}
df_vehicle = pd.DataFrame(vehicle_data)
label_encoder = LabelEncoder()
df_vehicle['vehicle_type_encoded'] = label_encoder.fit_transform(df_vehicle['vehicle_type'])
knn = KNeighborsClassifier(n_neighbors=1)
knn.fit(df_vehicle[['vehicle_type_encoded']], df_vehicle['vehicle_type'])

def recognize_number_plate(img_path):
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    plates = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml').detectMultiScale(gray, 1.1, 10)
    if len(plates) == 0:
        return None, None

    for (x, y, w, h) in plates:
        roi = gray[y:y + h, x:x + w]
        number_plate_text = pytesseract.image_to_string(roi, config='--psm 8')
        number_plate_text = ''.join(e for e in number_plate_text if e.isalnum())  # Clean the text
        return number_plate_text, roi

    return None, None

def predict_vehicle_type(license_plate):
    if license_plate in df_vehicle['license_plate'].values:
        vehicle_type_encoded = df_vehicle.loc[df_vehicle['license_plate'] == license_plate, 'vehicle_type_encoded'].values[0]
        return label_encoder.inverse_transform([vehicle_type_encoded])[0]
    return "Unknown"

def handle_form_submit():
    license_plate = license_plate_entry.get()
    vehicle_type = vehicle_type_entry.get()
    entry = {'License Plate': license_plate, 'Vehicle Type': vehicle_type}
    entries.append(entry)
    update_table()

def handle_image_upload():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return
    license_plate, roi = recognize_number_plate(file_path)
    if license_plate:
        license_plate_entry.delete(0, tk.END)
        license_plate_entry.insert(0, license_plate)
        vehicle_type = predict_vehicle_type(license_plate)
        vehicle_type_entry.delete(0, tk.END)
        vehicle_type_entry.insert(0, vehicle_type)
        img = Image.open(file_path)
        img.thumbnail((150, 150))
        img = ImageTk.PhotoImage(img)
        image_labels.append(tk.Label(image_frame, image=img))
        image_labels[-1].image = img
        image_labels[-1].pack()
        entries.append({'License Plate': license_plate, 'Vehicle Type': vehicle_type, 'Image': file_path})
        update_table()

def update_table():
    for row in table.get_children():
        table.delete(row)
    for entry in entries:
        table.insert('', 'end', values=(entry['License Plate'], entry['Vehicle Type'], entry['Image']))

def filter_table():
    vehicle_type = filter_var.get()
    for row in table.get_children():
        table.delete(row)
    filtered_entries = [entry for entry in entries if entry['Vehicle Type'] == vehicle_type]
    for entry in filtered_entries:
        table.insert('', 'end', values=(entry['License Plate'], entry['Vehicle Type'], entry['Image']))

root = tk.Tk()
root.title("Toll Collection and License Plate Recognition System")

# Form
form_frame = tk.Frame(root)
form_frame.pack(pady=10)

license_plate_label = tk.Label(form_frame, text="License Plate:")
license_plate_label.grid(row=0, column=0, padx=5, pady=5)
license_plate_entry = tk.Entry(form_frame)
license_plate_entry.grid(row=0, column=1, padx=5, pady=5)

vehicle_type_label = tk.Label(form_frame, text="Vehicle Type:")
vehicle_type_label.grid(row=1, column=0, padx=5, pady=5)
vehicle_type_entry = tk.Entry(form_frame)
vehicle_type_entry.grid(row=1, column=1, padx=5, pady=5)

submit_button = tk.Button(form_frame, text="Submit", command=handle_form_submit)
submit_button.grid(row=2, columnspan=2, pady=10)

# Image Upload
upload_button = tk.Button(root, text="Upload Image", command=handle_image_upload)
upload_button.pack(pady=10)

# Image Display
image_frame = tk.Frame(root)
image_frame.pack(pady=10)
image_labels = []

# Table
columns = ('License Plate', 'Vehicle Type', 'Image')
table = ttk.Treeview(root, columns=columns, show='headings')
for col in columns:
    table.heading(col, text=col)
table.pack(pady=10)

# Filter
filter_frame = tk.Frame(root)
filter_frame.pack(pady=10)
filter_var = tk.StringVar()
filter_label = tk.Label(filter_frame, text="Filter by Vehicle Type:")
filter_label.pack(side=tk.LEFT, padx=5)
filter_entry = tk.Entry(filter_frame, textvariable=filter_var)
filter_entry.pack(side=tk.LEFT, padx=5)
filter_button = tk.Button(filter_frame, text="Filter", command=filter_table)
filter_button.pack(side=tk.LEFT, padx=5)

entries = []
root.mainloop()
