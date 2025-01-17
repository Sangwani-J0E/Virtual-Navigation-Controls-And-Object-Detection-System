### README for Virtual Navigation Controls and Object Detection Using Computer Vision

---

# Virtual Navigation Controls and Object Detection Using Computer Vision

Welcome to the **Virtual Navigation Controls and Object Detection Using Computer Vision** project! This is a **final year project** that leverages cutting-edge technologies in computer vision, hand gesture recognition, augmented reality, and object detection to provide a seamless, interactive experience. It allows users to control navigation actions (mouse and keyboard) through hand gestures, detect objects and measure their distance, and scan books with augmented reality features, all through the camera feed of a device.

This project was developed as part of my final year in **Computer Science**, showcasing advanced skills in machine learning, computer vision, and user interface development.

---

## Key Features

### 1. **Virtual Navigation Controls**

- The system uses the camera feed to track hand movements and gestures, allowing the user to control mouse and keyboard actions in real-time.
- Hand gestures are mapped to different navigation commands, such as moving the cursor, clicking, and scrolling.

### 2. **Object Detection with Distance Measurement**

- The system detects objects in the camera feed and provides real-time distance measurements, using computer vision techniques such as contour detection and depth sensing.
- Distance information is displayed to the user, providing a better understanding of their surroundings or specific objects.

### 3. **Augmented Reality (AR) with Book Scanning**

- Using augmented reality, the system can scan a physical book placed in front of the camera and overlay a video or interactive content directly on top of the book in the camera feed.
- This feature provides an immersive experience by integrating digital content with the physical world in real time.

### 4. **Data Viewing**

- The system collects data related to hand gestures, object detection, and AR interactions.
- A dedicated interface allows users to view the collected data, offering insights into their interactions with the system.

---

## Tech Stack

- **Programming Language**: Python
- **Libraries and Frameworks**:
  - **OpenCV**: For computer vision tasks such as object detection, hand gesture recognition, and augmented reality.
  - **MediaPipe**: For hand tracking and gesture recognition.
  - **NumPy**: For numerical computations and data handling.
  - **AR.js** or **Vuforia** (optional, depending on AR implementation).
- **Machine Learning**: Custom models or pre-trained models for object detection (e.g., YOLO, TensorFlow).
- **Frontend**: HTML, CSS (if applicable for data viewing interface).

---

## Installation

Follow these steps to set up and run the project locally:

1. **Clone the Repository**:  
   ```bash
   git clone https://github.com/yourusername/Virtual-Navigation-Controls-And-Object-Detection.git
   ```

2. **Install Required Dependencies**:
   Make sure you have Python installed (preferably version 3.x). Then, install the necessary packages via pip:
   ```bash
   pip install opencv-python mediapipe numpy
   ```

3. **Set Up the Environment**:
   If you're using augmented reality (AR), you may need additional libraries such as **AR.js** or **Vuforia** for AR features. Follow their documentation to install and set them up properly.

4. **Run the Project**:
   Navigate to the project directory and run the Python script:
   ```bash
   python main.py
   ```

5. **Access the Data Viewing Interface** (if applicable):
   Open the data viewing interface in your browser or desktop application to review the collected data from the system.

---

## How to Use

1. **Virtual Navigation**:
   - Position your hand in front of the camera.
   - The system will detect your hand movements and map gestures to mouse and keyboard controls (e.g., swipe for movement, open palm for clicks).
   
2. **Object Detection and Distance**:
   - Point the camera at any object.
   - The system will display the distance from the object in the feed, with the option to trigger an alert if the object is too close or too far.

3. **Augmented Reality (AR)**:
   - Place a book (or any predefined target object) in front of the camera.
   - The system will detect the book and play an interactive video overlay on top of it in the camera feed.

4. **Data Viewing**:
   - After using the system, open the data viewing interface to review the collected interaction data (e.g., hand gestures, object detection data, and AR scanning logs).

---

## Acknowledgements

This project would not have been possible without the following contributions and resources:

- **OpenCV** and **MediaPipe**: For providing the essential libraries for computer vision and hand gesture recognition.
- **TensorFlow** or other object detection models for enabling the real-time detection and distance calculation of objects.
  
---

## Future Enhancements

While the system is functional, there are areas that could be improved or expanded:

1. **Enhanced Gesture Recognition**:
   - Incorporate more complex gestures for advanced controls (e.g., zooming, rotating, etc.).
   
2. **Optimized Object Detection**:
   - Integrate more sophisticated object detection models to improve accuracy and speed.

3. **Augmented Reality Enhancements**:
   - Add more interactive AR features, such as text annotations, 3D objects, or games.

4. **Cross-Platform Support**:
   - Make the system cross-platform, allowing it to work on mobile devices or multiple operating systems.


Thank you for exploring the **Virtual Navigation Controls and Object Detection Using Computer Vision** project!
