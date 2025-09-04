import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import pytesseract

# Vehicle toll amounts
toll_amounts = {
    "Bicycle": 10,
    "Motorcycle": 25,
    "Car": 50,
    "Van": 70,
    "Bus": 80,
    "Truck": 110,
    "SUV": 75,
    "Taxi": 50,
    "Ambulance": 0
}

collected_tolls = 0.0
toll_count = 0

# Function to process image for OCR
def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 200, 3)
    return edged

# Function to detect number plates
def detect_number_plates(edged):
    contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    plates = []

    for contour in contours:
        rect = cv2.boundingRect(contour)
        if rect[2] > rect[3] and rect[2] * rect[3] > 1000:
            plates.append(rect)

    return plates

# Function to recognize number plate text
def recognize_number_plate(img, plate_rect):
    x, y, w, h = plate_rect
    roi = img[y:y+h, x:x+w]
    number_plate_text = pytesseract.image_to_string(roi, config='--psm 8')
    return number_plate_text.strip()

# Function to handle manual entry
def handle_manual_entry():
    global collected_tolls, toll_count

    vehicle_type = vehicle_type_var.get()
    number_plate = number_plate_entry.get()
    
    if vehicle_type and number_plate:
        toll_amount = toll_amounts[vehicle_type]
        collected_tolls += toll_amount
        toll_count += 1
        update_collected_tolls()
        update_toll_count()
        messagebox.showinfo("Success", f"Vehicle {number_plate} ({vehicle_type}) added with toll amount ?{toll_amount}")
    else:
        messagebox.showerror("Error", "Please fill in all fields")

# Function to handle image upload
def handle_image_upload():
    global collected_tolls, toll_count

    file_path = filedialog.askopenfilename()
    if file_path:
        img = cv2.imread(file_path)
        if img is None:
            messagebox.showerror("Error", "Could not read the image.")
            return

        processed_image = preprocess_image(img)
        plates = detect_number_plates(processed_image)
        
        if plates:
            number_plate_text = recognize_number_plate(img, plates[0])
            if number_plate_text:
                number_plate_entry.delete(0, tk.END)
                number_plate_entry.insert(0, number_plate_text)
                display_uploaded_image(file_path)
            else:
                messagebox.showerror("Error", "License plate recognition failed")
        else:
            messagebox.showerror("Error", "No number plates detected")

# Function to update collected tolls display
def update_collected_tolls():
    collected_tolls_label.config(text=f"Collected Tolls: ?{collected_tolls:.2f}")

# Function to update toll count display
def update_toll_count():
    toll_count_label.config(text=f"Number of Tolls Collected: {toll_count}")

# Function to display uploaded image
def display_uploaded_image(file_path):
    img = Image.open(file_path)
    img.thumbnail((300, 300))
    img = ImageTk.PhotoImage(img)
    uploaded_image_label.config(image=img)
    uploaded_image_label.image = img

# Main application window
root = tk.Tk()
root.title("Toll Collection & License Plate Recognition System")

# Manual entry frame
manual_frame = ttk.LabelFrame(root, text="Manual Entry")
manual_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

vehicle_type_label = ttk.Label(manual_frame, text="Vehicle Type:")
vehicle_type_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

vehicle_type_var = tk.StringVar()
vehicle_type_combo = ttk.Combobox(manual_frame, textvariable=vehicle_type_var)
vehicle_type_combo['values'] = list(toll_amounts.keys())
vehicle_type_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

number_plate_label = ttk.Label(manual_frame, text="Number Plate:")
number_plate_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

number_plate_entry = ttk.Entry(manual_frame)
number_plate_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

manual_entry_button = ttk.Button(manual_frame, text="Submit", command=handle_manual_entry)
manual_entry_button.grid(row=2, columnspan=2, padx=5, pady=5)

# Image upload frame
image_frame = ttk.LabelFrame(root, text="Image Upload")
image_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

upload_button = ttk.Button(image_frame, text="Upload Image", command=handle_image_upload)
upload_button.grid(row=0, columnspan=2, padx=5, pady=5)

uploaded_image_label = ttk.Label(image_frame)
uploaded_image_label.grid(row=1, columnspan=2, padx=5, pady=5)

# Collected tolls display
collected_tolls_label = ttk.Label(root, text=f"Collected Tolls: ?{collected_tolls:.2f}")
collected_tolls_label.grid(row=2, column=0, padx=10, pady=5)

# Toll count display
toll_count_label = ttk.Label(root, text=f"Number of Tolls Collected: {toll_count}")
toll_count_label.grid(row=3, column=0, padx=10, pady=5)

root.mainloop()
