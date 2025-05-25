# Object Detection and Tracking Utilizing a ZED 2i Stereo Camera and a Two-Axis Gimbal

## Overview

This repository contains the code, models, and resources for the E2504 Bachelor project "Lone Wolf - Object Detection and Tracking Utilizing a ZED 2i Stereo Camera and a Two-Axis Gimbal" at NTNU. The project involves 3D printing, object detection using YOLOv8, and tracking with DeepSort, with integration for camera gimbal control.

## Repository Structure

- **3D-Printing/**  
  Contains 3MF and SolidWorks (SLD) files for 3D-printed components.

- **Docker/**  
  Docker resources for building and running the project environment.

- **Models/**  
  Pre-trained YOLOv8 models (`.pt` and `.engine` files) and scripts for model conversion.
  - `ConvertToTensorRT.py`: Script to convert PyTorch models to TensorRT.
  - `Training/`: Training scripts and resources.

- **Programfiles/**  
  Main Python scripts for detection, tracking, and camera/gimbal integration.
  - `Yolo.py`: Basic YOLOv8 inference.
  - `Yolo_DeepSort.py`: YOLOv8 with DeepSort tracking.
  - `Yolo_CameraGimbal.py`: Full pipeline with camera and gimbal control.
  - `DetectorDeepSort.py`, `TrackerDeepSort.py`: Detection and tracking modules.
  - `custom_botsort.yaml`: Custom configuration for tracking.

## Getting Started

### Prerequisites

- NVIDIA Jetson device (e.g., Orin Nano, Xavier, TX2, etc.) with JetPack 6.2 (L4T 36.4.3) or compatible
- ZED 2i Stereo Camera + USB 3.0 (or higher) cable for camera connection
- Docker installed on Jetson device for containerized setup
- 3D printer for two-axis components (optional, for hardware assembly)

### Installation

1. *(Optional but recommended)* Set up your NVIDIA Jetson device with an SSD for Docker with GPU acceleration. This improves performance and storage capacity.

2. Clone the repository:
    ```sh
    git clone https://github.com/alaabakk/Object_Detection_and_Tracking_ZED_2i_E2504.git
    cd Object_Detection_and_Tracking_ZED_2i_E2504
    ```

3. Build and run with Docker for NVIDIA Jetson platforms:
    ```sh
    chmod +x RunContainer.sh # Make script executable
    ./RunContainer.sh # This will pull and create a Docker environment
    ```

### Usage

- To run YOLOv8 detection:
    ```sh
    python Programfiles/Yolo.py
    ```
- To run detection and tracking:
    ```sh
    python Programfiles/Yolo_DeepSort.py
    ```
- For full camera and gimbal integration:
    ```sh
    python Programfiles/Yolo_CameraGimbal.py
    ```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Authors

- Kjetil Homelien
- Petter Hauge Dignes
- Arthur Leiv Claude Prevault Aabakken
- Ole Fjeld Haugstvedt

## Acknowledgements

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [DeepSort](https://github.com/nwojke/deep_sort)
