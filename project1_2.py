import cv2
import pytesseract
import pygame
import sys
import numpy as np

# Initialize Pygame
pygame.init()

# Global variables for Pygame window
window_width = 600
window_height = 600
space_pressed = False  # Flag to track if space button is pressed
show_instructions = False
show_prices = False
countdown_started = False
countdown_time = 5  # Countdown time in seconds
frame_count = 0

# Vehicle parameters
vehicle_speed = 2.0

# Toll parameters
toll_booth_position = 400.0
motorcycle_toll_amount = 25.0
car_toll_amount = 50.0
bus_toll_amount = 80.0
truck_toll_amount = 110.0
van_toll_amount = 70.0
bicycle_toll_amount = 10.0

collected_tolls = 0.0

# Enum for vehicle types
class VehicleType:
    BICYCLE, MOTORCYCLE, CAR, VAN, BUS, TRUCK, SUV, TAXI, AMBULANCE = range(9)

# Structure for vehicles
class Vehicle:
    def __init__(self, position, vehicle_type, passed_toll):
        self.position = position
        self.vehicle_type = vehicle_type
        self.passed_toll = passed_toll

# Array of vehicles
vehicles = []
num_vehicles = 0

# Project details
project_name = "Toll Collection & License Plate Recognition System"
student_name = "Karthik G"
guide_name = "-------"

# Function to preprocess the image
def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 200, 3)
    return edged

# Function to detect potential number plates
def detect_number_plates(edged):
    contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    plates = []

    for contour in contours:
        rect = cv2.boundingRect(contour)
        if rect[2] > rect[3] and rect[2] * rect[3] > 1000:
            plates.append(rect)

    return plates

# Function to perform OCR on detected number plates
def recognize_number_plate(img, plate_rect):
    x, y, w, h = plate_rect
    roi = img[y:y+h, x:x+w]

    number_plate_text = pytesseract.image_to_string(roi, config='--psm 8')
    return number_plate_text.strip()

# Function to draw a vehicle
def draw_vehicle(screen, x_pos, y_pos, vehicle_type):
    if vehicle_type == VehicleType.BICYCLE:
        pygame.draw.line(screen, (25, 178, 76), (x_pos - 10, y_pos), (x_pos + 10, y_pos), 2)
    elif vehicle_type == VehicleType.MOTORCYCLE:
        pygame.draw.circle(screen, (229, 25, 25), (x_pos, y_pos), 10)
    elif vehicle_type == VehicleType.CAR:
        pygame.draw.rect(screen, (128, 128, 128), (x_pos - 10, y_pos - 10, 20, 20))
    elif vehicle_type == VehicleType.VAN:
        pygame.draw.polygon(screen, (178, 127, 76), [(x_pos - 10, y_pos - 5), (x_pos + 10, y_pos - 5), (x_pos + 15, y_pos), (x_pos + 10, y_pos + 5), (x_pos - 10, y_pos + 5), (x_pos - 15, y_pos)])
    elif vehicle_type == VehicleType.BUS:
        pygame.draw.polygon(screen, (204, 153, 51), [(x_pos, y_pos - 10), (x_pos + 20, y_pos + 10), (x_pos - 20, y_pos + 10)])
    elif vehicle_type == VehicleType.TRUCK:
        pygame.draw.polygon(screen, (76, 76, 178), [(x_pos - 10, y_pos - 5), (x_pos + 10, y_pos - 5), (x_pos + 15, y_pos), (x_pos, y_pos + 10), (x_pos - 15, y_pos)])
    elif vehicle_type == VehicleType.SUV:
        pygame.draw.polygon(screen, (102, 51, 25), [(x_pos - 15, y_pos - 5), (x_pos + 15, y_pos - 5), (x_pos + 20, y_pos + 5), (x_pos - 20, y_pos + 5)])
    elif vehicle_type == VehicleType.TAXI:
        pygame.draw.rect(screen, (255, 204, 0), (x_pos - 10, y_pos - 5, 20, 10))
    elif vehicle_type == VehicleType.AMBULANCE:
        pygame.draw.line(screen, (255, 0, 0), (x_pos - 10, y_pos - 5), (x_pos + 10, y_pos + 5), 2)
        pygame.draw.line(screen, (255, 0, 0), (x_pos - 10, y_pos + 5), (x_pos + 10, y_pos - 5), 2)

# Function to draw the toll booth
def draw_toll_booth(screen, x_pos):
    pygame.draw.rect(screen, (76, 178, 76), (x_pos, 0, 100, window_height))

# Function to display text
def draw_text(screen, x, y, text, color=(0, 0, 0)):
    font = pygame.font.SysFont(None, 24)
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

# Function to update vehicle positions
def update_vehicles():
    global collected_tolls, num_vehicles
    for vehicle in vehicles:
        if not vehicle.passed_toll:
            vehicle.position += vehicle_speed
            if vehicle.position >= toll_booth_position:
                if vehicle.vehicle_type == VehicleType.BICYCLE:
                    collected_tolls += bicycle_toll_amount
                elif vehicle.vehicle_type == VehicleType.MOTORCYCLE:
                    collected_tolls += motorcycle_toll_amount
                elif vehicle.vehicle_type == VehicleType.CAR:
                    collected_tolls += car_toll_amount
                elif vehicle.vehicle_type == VehicleType.VAN:
                    collected_tolls += van_toll_amount
                elif vehicle.vehicle_type == VehicleType.BUS:
                    collected_tolls += bus_toll_amount
                elif vehicle.vehicle_type == VehicleType.TRUCK:
                    collected_tolls += truck_toll_amount
                elif vehicle.vehicle_type == VehicleType.SUV:
                    collected_tolls += car_toll_amount * 1.5
                elif vehicle.vehicle_type == VehicleType.TAXI:
                    collected_tolls += car_toll_amount
                vehicle.passed_toll = True

    vehicles[:] = [vehicle for vehicle in vehicles if not vehicle.passed_toll]
    num_vehicles = len(vehicles)

# Function to draw instructions
def draw_instructions(screen):
    draw_text(screen, 10, window_height - 30, "Toll Collection and License Plate Recognition System Instructions")
    draw_text(screen, 10, window_height - 60, "Press 1-9 to add vehicles like bicycle, motorcycle, car, van, bus, truck, SUV, taxi, or ambulance.")
    draw_text(screen, 10, window_height - 90, "Press 'Space Bar': Start/Stop")
    draw_text(screen, 10, window_height - 110, "Hit 'Enter' to begin number plate detection.")
    draw_text(screen, 10, window_height - 140, "Press 'P' for price details")

# Function to draw vehicle toll prices
def draw_prices(screen):
    draw_text(screen, 10, window_height - 200, "Vehicle Toll Prices:")
    draw_text(screen, 10, window_height - 220, "Bicycle: ?10.00")
    draw_text(screen, 10, window_height - 240, "Motorcycle: ?25.00")
    draw_text(screen, 10, window_height - 260, "Car: ?50.00")
    draw_text(screen, 10, window_height - 280, "Van: ?70.00")
    draw_text(screen, 10, window_height - 300, "Bus: ?80.00")
    draw_text(screen, 10, window_height - 320, "Truck: ?110.00")
    draw_text(screen, 10, window_height - 340, "SUV: ?75.00")
    draw_text(screen, 10, window_height - 360, "Taxi: ?50.00")
    draw_text(screen, 10, window_height - 380, "Ambulance: Toll Exempted")

# Function to process image
def process_image():
    image = cv2.imread("/home/karthi/Documents/number_plate.jpeg")
    if image is None:
        print("Error: Could not read the image.")
        return

    processed_image = preprocess_image(image)
    plates = detect_number_plates(processed_image)

    print("Number Plates Detected:")
    for plate_rect in plates:
        number_plate_text = recognize_number_plate(image, plate_rect)
        print(number_plate_text)

# Main loop
def main():
    global num_vehicles, space_pressed, show_instructions, show_prices, countdown_started, frame_count

    # Create Pygame window
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Toll Collection & License Plate Recognition System")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    space_pressed = not space_pressed
                elif event.key == pygame.K_RETURN:
                    process_image()
                elif event.key == pygame.K_i:
                    show_instructions = not show_instructions
                elif event.key == pygame.K_p:
                    show_prices = not show_prices
                elif event.key == pygame.K_1:
                    vehicles.append(Vehicle(0, VehicleType.BICYCLE, False))
                elif event.key == pygame.K_2:
                    vehicles.append(Vehicle(0, VehicleType.MOTORCYCLE, False))
                elif event.key == pygame.K_3:
                    vehicles.append(Vehicle(0, VehicleType.CAR, False))
                elif event.key == pygame.K_4:
                    vehicles.append(Vehicle(0, VehicleType.VAN, False))
                elif event.key == pygame.K_5:
                    vehicles.append(Vehicle(0, VehicleType.BUS, False))
                elif event.key == pygame.K_6:
                    vehicles.append(Vehicle(0, VehicleType.TRUCK, False))
                elif event.key == pygame.K_7:
                    vehicles.append(Vehicle(0, VehicleType.SUV, False))
                elif event.key == pygame.K_8:
                    vehicles.append(Vehicle(0, VehicleType.TAXI, False))
                elif event.key == pygame.K_9:
                    vehicles.append(Vehicle(0, VehicleType.AMBULANCE, False))
                num_vehicles = len(vehicles)

        if space_pressed:
            update_vehicles()

        screen.fill((255, 255, 255))

        draw_toll_booth(screen, toll_booth_position)
        for vehicle in vehicles:
            draw_vehicle(screen, vehicle.position, window_height // 2, vehicle.vehicle_type)

        draw_text(screen, 10, 10, f"Collected Tolls: ?{collected_tolls:.2f}")
        draw_text(screen, 10, 40, f"Number of Vehicles: {num_vehicles}")

        if show_instructions:
            draw_instructions(screen)

        if show_prices:
            draw_prices(screen)

        if countdown_started:
            draw_text(screen, 10, 70, f"Countdown: {countdown_time - frame_count // 30}")

        pygame.display.update()

        if space_pressed:
            frame_count += 1
            if frame_count // 30 >= countdown_time:
                frame_count = 0
                space_pressed = False
                countdown_started = False

if __name__ == "__main__":
    main()
