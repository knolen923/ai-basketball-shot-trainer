# AI Basketball Shot Trainer

A real-time basketball shot tracking system built in **Python** using **MediaPipe Pose**, **OpenCV**, and a **Tkinter GUI**.  
The system detects shooting motion using joint-angle analysis and estimates makes/misses by detecting the basketball within a hoop region-of-interest (ROI).

##  Features
- Real-time webcam feed with live shot statistics
- Pose-based shot detection using elbow joint angles
- Interactive hoop region-of-interest (ROI) selection
- Color-based basketball detection using HSV masking
- GUI dashboard displaying shots, makes, misses, and shooting percentage


## How It Works

### 1. Pose Estimation
MediaPipe Pose is used to detect upper-body landmarks in each video frame.  
Key joints (shoulder, elbow, wrist) are tracked to compute arm angles in real time.

### 2. Shot Detection
A basketball shot is detected by monitoring the elbow angle:
- A shot begins when the elbow angle exceeds a predefined extension threshold
- The shot is confirmed once the arm returns downward
This approach models the biomechanical motion of a shooting action rather than relying on ball tracking alone.

### 3. Hoop ROI Selection
The user selects a rectangular region corresponding to the hoop at startup.  
This region-of-interest (ROI) limits ball detection to the relevant area of the frame, reducing false positives and improving performance.

### 4. Make / Miss Classification
After a shot release:
- The system detects the basketball using HSV color masking
- Contours are analyzed to identify circular ball-like objects
- If the ball is detected inside the hoop ROI shortly after release, the shot is counted as a make

### 5. GUI and Statistics
A Tkinter-based GUI displays:
- Live video feed
- Total shots, makes, misses
- Shooting percentage
Statistics update in real time as shots are detected.

## Tech Stack
- Python
- OpenCV
- MediaPipe
- NumPy
- Tkinter

##  Notes and Limitations
- Lighting conditions affect color-based ball detection
- HSV thresholds may require tuning for different environments
- Best results with a clear view of the shooter and the hoop


##  Installation
```bash
pip install -r requirements.txt




