import cv2
import easyocr
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

# Function to process image and extract text
def process_image(image_path):
    # Read image
    img = cv2.imread(image_path)

    # Instance text detector
    reader = easyocr.Reader(['en'], gpu=False)

    # Detect text on image
    text_ = reader.readtext(img)

    # Process each detected text
    result_texts = []
    threshold = 0.25
    for bbox, text, score in text_:
        if score > threshold:
            result_texts.append(text)

    # Return combined result
    return ' '.join(result_texts)

# Function to update GUI with processed image and text
def update_gui(image_path):
    # Process image and extract text
    extracted_text = process_image(image_path)

    # Update GUI elements
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img.thumbnail((400, 400))  # Resize image for display

    imgtk = ImageTk.PhotoImage(image=img)
    image_label.config(image=imgtk)
    image_label.image = imgtk  # Keep reference to avoid garbage collection

    text_output.delete('1.0', tk.END)  # Clear previous text
    text_output.insert(tk.END, extracted_text)

# Create Tkinter GUI window
window = tk.Tk()
window.title("License Plate Text Extraction")

# Create image label
image_label = tk.Label(window)
image_label.pack(padx=10, pady=10)

# Create text output field
text_output = tk.Text(window, height=10, width=60)
text_output.pack(padx=10, pady=(0, 10))

# Initial image path
image_path = 'License plates/images.jpeg'

# Button to process image and update GUI
process_button = tk.Button(window, text="Process Image", command=lambda: update_gui(image_path))
process_button.pack(pady=10)

# Call update_gui initially
update_gui(image_path)

# Run the Tkinter event loop
window.mainloop()