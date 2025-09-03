# License_Plate_detection_and_toll_collection
License_Plate_detection_and_toll_collection is a Python-based computer vision project that automatically detects vehicle license plates from real-time images or video streams and extracts the plate number using Optical Character Recognition (OCR). It simulates an automated toll collection system by identifying registered vehicles.

## Version 1: License Plate Text Extraction with GUI
Version 1 introduces a simple **Python-based GUI application** for extracting text from license plates using `EasyOCR` and `OpenCV`. It processes images offline and displays the results in a Tkinter interface.

### Added: extract_img.py
- A utility script that extracts text from a given license plate image.  
- Uses EasyOCR to detect text and visualize results with OpenCV and Matplotlib.  
- Part of the core functionality for testing OCR separately from the GUI.
#### Requirements 
``` bash
 pip install opencv-python pytesseract pygame numpy easyocr matplotlib numpy pillow
```
### 📷 Snapshots

**Model Download Initialization**  
Image showing the downloading of the text detection model required by EasyOCR.  
![Model Downloading](assets/Downloading_Detection_model.png)

**Version 0.1 - Early Output Example**  
Initial version showing detection errors and limited accuracy (~72%).  
![Version 0.1 Output](./assets/ver0_1.png)


## Version 1.1: License Plate Text Extraction with GUI
This version is made with the intention of gamifying the experience. This is just a random alpha phase for the project where we test out all the grounds on making the user experience better in the view of user requirements.