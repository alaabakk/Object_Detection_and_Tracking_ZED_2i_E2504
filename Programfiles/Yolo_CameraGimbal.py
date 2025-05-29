from ultralytics import YOLO
import pyzed.sl as sl
import numpy as np
import cv2
import os
import threading
import time
import serial

## Global variables
selected_object = 'q'


## Serial configuration
PORT = '/dev/ttyUSB0'#'COM4  # <-- Use known USB port
BAUDRATE = 115200
TIMEOUT = 1


def init_zed():
    # Create a Camera object
    zed = sl.Camera()

    # Create a InitParameters object and set configuration parameters
    init_params = sl.InitParameters()
    init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE
    init_params.coordinate_units = sl.UNIT.METER
    init_params.sdk_verbose = 1
    init_params.camera_resolution = sl.RESOLUTION.HD720
    init_params.camera_fps = 30

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Camera Open : " + repr(err) + ". Exit program.")
        exit()

    return zed

def init_yolo():
    # Initialize the YOLO model
    print("Initializing YOLO model...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to the model file
    model_path = os.path.join(script_dir, "../Models/customYolov8n.engine")
    model = YOLO(model_path, task="detect")
    print("YOLO model initialized")
    return model

def init_serial():
    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT)
        time.sleep(2)
        print(f"Serial port {PORT} opened successfully.")
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port {PORT}: {e}")
        return None

def serial_print(ser, x1, y1, x2, y2):
    if not ser:
        return
    message1 = int(x1 + (x2 - x1) / 2) 
    message2 = int(y1 + (y2 - y1) / 2) - ((y2 - y1)/4)
    message = f"{message1} , {message2}\n"
    ser.write(message.encode())

def startup_message():
    print("\nYOLO Object Detection with ZED on Jetson")
    print("Program started. Press 'q' in the window to stop.")
    print("Enter the ID of the object you want to track. Enter 'q' to stop tracking.")


class FPSCounter:
    def __init__(self):
        self.start_time = time.perf_counter()
        self.frame_count = 0

    def calculateFPS(self):
        current_time = time.perf_counter()
        elapsed_time = current_time - self.start_time

        self.frame_count += 1

        if elapsed_time > 1.0:
            fps = int(self.frame_count / elapsed_time)
            self.start_time = current_time
            self.frame_count = 0
            return fps, True
        
        return 0, False
    
    def draw_fps(self, img, fps):
        # Set styles
        text = f"FPS: {fps}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.6
        thickness = 2
        text_color = (255, 255, 255)
        bg_color = (30, 30, 30)  # Dark grey
        padding = 10

        # Get text size
        (w, h), _ = cv2.getTextSize(text, font, scale, thickness)
        x, y = 10, 30  # Top-left corner

        # Draw rounded rectangle (you can swap to plain if preferred)
        cv2.rectangle(img, (x - padding, y - h - padding), (x + w + padding, y + padding), bg_color, -1)
        cv2.putText(img, text, (x, y), font, scale, text_color, thickness)

class KeyboardThread(threading.Thread):
    def __init__(self, input_cbk=None, ser=None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        self.ser = ser  # Pass the serial object
        super(KeyboardThread, self).__init__(name=name, daemon=True)
        self.start()

    def run(self):
        while True:
            user_input = input()  # Waits to get input + Return
            if self.input_cbk:
                self.input_cbk(user_input, self.ser)  # Pass user input and serial object to the callback

def my_callback(inp, ser):
    #evaluate the keyboard input
    print('You selected object:', inp)
    global selected_object
    selected_object = inp
    if inp == 'q':
        ser.write(inp.encode())

    

def calculateDistance(middle, depth_map):
    # Get the depth value at the center of the object
    if middle[0] >= 0 and middle[0] <= 1280 and middle[1] >= 0 and middle[1] <= 720:
        depth_value = depth_map.get_value(middle[0], middle[1])
        distance = depth_value[1]
    else:
        distance = 0.0

    return distance


def process_yolo_results(results, img_cv, ser, depth_map):
    global selected_object

    # Define the classes to keep
    names = {
        0: 'person'
    }

    # Process YOLO results and draw bounding boxes on the image
    for r in results:
        for box in r.boxes:
            label_id = int(box.cls[0])  # Class ID
            if label_id in names:  # Filter by desired classes
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box coordinates
                confidence = box.conf[0]  # Confidence score
                type = names[label_id]  # Get class label from the dictionary
                #ID = int(box.id[0])  # Get the unique ID of the object
                ID = int(box.id[0]) if box.id is not None else -1  # Use -1 as a fallback ID

                # Avstand til midten av objektet
                middle = (int(x1 + (x2 - x1) / 2), int(y1 + (y2 - y1) / 2))
                distance = calculateDistance(middle, depth_map)

                if selected_object == str(ID):
                    # Draw bounding box with red color for selected object
                    draw_bounding_box(img_cv, x1, y1, x2, y2, (0, 0, 255), ID, type, confidence, distance)

                    serial_print(ser, x1, y1, x2, y2)

                else:
                    # Draw bounding box with green color for other objects
                    draw_bounding_box(img_cv, x1, y1, x2, y2, (0, 255, 0), ID, type, confidence, distance)

def draw_bounding_box(img_cv, x1, y1, x2, y2, color, tracking_id, type, confidence, distance):
    cv2.rectangle(img_cv, (x1, y1), (x2, y2), color, 2)
    label_text = f"{tracking_id} {type} ({confidence:.2f}), distance: {distance:.2f} m"
    cv2.putText(img_cv, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


def main_loop(zed, model, fps_counter, fps, ser):
    # Create a ZED Mat object to store images
    zed_image = sl.Mat()

    # Define fixed width and height
    fixed_width = 1280
    fixed_height = 720

    while True:
        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            # Retrieve the left image from the ZED camera
            zed.retrieve_image(zed_image, sl.VIEW.LEFT)
            img_cv = np.array(zed_image.get_data(), dtype=np.uint8)

            # Convert RGBA to RGB
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGBA2RGB)

            #distanse
            depth_map = sl.Mat()
            zed.retrieve_measure(depth_map, sl.MEASURE.DEPTH)

            # Predict using YOLO
            results = model.track(img_cv, stream=True, augment=True, verbose=False, device=0, conf=0.7, tracker="custom_botsort.yaml", persist=True)

            # Process results and draw on the frame
            process_yolo_results(results, img_cv, ser, depth_map)

            # Calculate and draw FPS
            fps_new, updated = fps_counter.calculateFPS()
            if updated:
                fps = fps_new
            fps_counter.draw_fps(img_cv, fps)

            # Resize the frame to fixed dimensions
            resized_frame = cv2.resize(img_cv, (fixed_width, fixed_height))
            cv2.imshow("YOLO Object Detection with ZED", resized_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    zed.close()
    cv2.destroyAllWindows()


def main():
    # Initialize ZED camera
    zed = init_zed()

    # Initialize YOLO model
    model = init_yolo()

    # Initialize serial communication
    ser = init_serial()
    if ser is None:
        print("Failed to initialize serial communication. Exiting.")
        return

    # Start the keyboard input thread
    kthread = KeyboardThread(my_callback, ser)

    # Initialize FPS counter
    fps_counter = FPSCounter()
    fps = 0

    startup_message()

    # Start the main loop
    main_loop(zed, model, fps_counter, fps, ser)


if __name__ == "__main__":
    main()
