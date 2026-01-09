import cv2
import numpy as np
import time
import poseModule as pm
import csv
import datetime


class aiTrainer:
    #constructor
    def __init__(self, cam_index=0):
        self.cap = cv2.VideoCapture(cam_index)
        self.detector = pm.poseDectector()

        #count(shot count) and dir(state variable) variables used for shot detection
        self.count = 0
        self.dir = 0

        self.shot_released = False     # true when the arm fully extends
        self.shot_made = False     # true if the ball enters the hoop after release
        self.makes = 0    # total makes
        self.misses = 0      # total misses



        self.cap.set(3, 1280)  
        self.cap.set(4, 720)

        # Initialize ROI coordinates - you can set these manually or call setupROI() method
        self.x, self.y, self.w, self.h = 640, 50, 200, 150  # Default ROI coordinates
        
    def setupROI(self):
        """Call this method separately to set up ROI selection"""
        #reads a single frame from the camera to use for the ROI selection
        ret, frame = self.cap.read()
        if ret:
            #lets the user draw a square around the ROI(hoop)
            print("Please select the hoop area in the window that opens...")
            r = cv2.selectROI("Select ROI - Press SPACE or ENTER to confirm, ESC to use default", frame, False)
            
            # coordinate of the rectangle(ROI)
            if r[2] > 0 and r[3] > 0:  # Check if valid selection was made
                self.x, self.y, self.w, self.h = r
                print(f"ROI set to: x={self.x}, y={self.y}, w={self.w}, h={self.h}")
            else:
                print("No ROI selected, using default coordinates")
            
            #closes the roi section so it doesnt block live feed
            cv2.destroyWindow("Select ROI - Press SPACE or ENTER to confirm, ESC to use default")
        else:
            print("Could not read frame from camera for ROI selection")



    #------------main loop-------------------
    def processFrame(self):

        success, img = self.cap.read()
        
        #checks wether the frame failed, if it does it returns a placeholder so it doesnt crash
        if not success:
            return None, {}

        img = cv2.resize(img, (1280, 720))

        text_x = img.shape[1] - 250 #250 pixels from the top right edge


        ball_detected = False



        img = self.detector.findPose(img, False)

        lmList = self.detector.findPosition(img, False)


        if len(lmList) != 0 :
            
            
            
            # Shooting arm elbow angle
            elbow_angle = self.detector.findAngle(img, 12, 14, 16)  # Shoulder, Elbow, Wrist
            

            #linear interpolation function, first parameter is the degree of the elbow angle
            #second [60,175] is the range of elbow angles that i care about 60 is about the start of the shot 175 is the end(fully extended arm)
            #0-100 is the percentage range i want to map the angles to
            # example is elbow angle were to be 60, it would display 0%
            # the function would look like ((60 - 60)) / ((175 - 60)) * (100-0) + 0
            per = np.interp(elbow_angle, [60,175], [0,100])

           

            # ball detection logic---------------------------------

            #this is a 3d numpy array y:y + h slicing the rows, and x:x+w slicing the columns
            #y = starting row, y + h = ending row
            # x = starting column, x+w = ending column
            # basically saying from starting colum/row to end of column/row
            roi_img = img[self.y:self.y+self.h, self.x:self.x+self.w]

            #converting roi_img iinto HSV so itll detect the ball only in the hoop
            hsv = cv2.cvtColor(roi_img, cv2.COLOR_BGR2HSV)


            #lower and upper bounds for the orange we are detecting
            #range of HSV values that represent the color orange in our image
            lower_orange = np.array([5, 150, 150]) # (Hue(from 0-179, 5-25 is orange), Saturation(color intensity 0-255), Value(Brightness, 0-255))
            upper_orange = np.array([25, 255, 255])

            #create a mask for the ball
            #basically makes everything inside the color range white and everything else black
            #isolates the ball
            mask = cv2.inRange(hsv, lower_orange, upper_orange)


            #detecting the outlines of white regions in mask
            #parameters
            # mask = the inputed binary image
            # cv2.RETR_EXTERNAL = only retrieves the outermost contours
            # cv2.CHAIN_APPROX_SIMPLE = storing endpoints
            # returns a list of contour points for each detected object
            contours, _ = cv2.findContours(mask,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )


            # cnt a single contour (list of points that outline the white region)
            # area = calculates the area(number of pixels in the contour)
            for cnt in contours:
                area = cv2.contourArea(cnt)


                #x_ball, y_ball = top left corner of rectangle
                #w_ball, h_ball = width and height of the rectangle
                # this gives a box around the ball which is easier to work with than the fuull contour points
                if area > 100:
                    x_ball, y_ball, w_ball, h_ball = cv2.boundingRect(cnt)
                    
                    #drawing the red rectangle visualization around each detected ball in the hoop
                    #roi_img = image drawing the box
                    #(x_ball, y_ball) = top left corner
                    #(x_ball + w_ball, y_ball + h_ball) bottom right corner
                    #(0,0,255)= color of the rectangle
                    #2 = thickness of rectangle
                    cv2.rectangle(roi_img, (x_ball, y_ball),
                                (x_ball + w_ball, y_ball + h_ball), (0,0,255), 2)
                    
                    #if any ball-like contour is in the hoop ROI
                    ball_detected = True







            #shot counting logic------------------------------
            #dir = 0 means the arm is coming up, dir 1 = the arm is fully extended
            if per > 90: #elbow almost fully extended
                if self.dir == 0:
                    self.count += 0.5
                    self.dir = 1
                    self.shot_released = True


            if per < 10: # elbow is down
                if self.dir == 1:
                    self.count+=0.5
                    self.dir = 0

                    #if the shot was released and never detected it counts as a miss
                    if self.shot_released and not ball_detected:
                        self.misses += 1
                        self.shot_released = False
            
            # making the detection
            if self.shot_released and ball_detected:
                self.makes += 1
                self.shot_released = False # resting for the next shot


            stats = {
                "count": int(self.count),
                "makes": int(self.makes),
                "misses": int(self.misses),
                "percentage": round((self.makes / max(1, (self.makes + self.misses))) * 100, 1)
            }

            return img, stats
        
        # Return the frame even if no pose is detected
        return img, {}

    
        
    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()


           