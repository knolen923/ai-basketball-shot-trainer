import cv2
import mediapipe as mp
import time
import math

class poseDectector():

    def __init__(self, mode=False, upBody=False, smooth=True, 
             detectionCon=0.5, trackCon=0.5):

            self.mode = mode
            self.upBody = upBody
            self.smooth = smooth
            self.detectionCon = detectionCon
            self.trackCon = trackCon

            self.mpDraw = mp.solutions.drawing_utils
            self.mpPose = mp.solutions.pose

            self.pose = self.mpPose.Pose(
                static_image_mode=self.mode,
                model_complexity=1,
                smooth_landmarks=self.smooth,
                enable_segmentation=False,
                smooth_segmentation=True,
                min_detection_confidence=self.detectionCon,
                min_tracking_confidence=self.trackCon
            )

                

    def findPose(self, img, draw = True):
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.results = self.pose.process(imgRGB)
             
            if self.results.pose_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, self.results.pose_landmarks,
                                                self.mpPose.POSE_CONNECTIONS)
            return img
                


    def findPosition(self, img, draw = True):
        self.lmList = []
        
        if self.results.pose_landmarks:

            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                #height, width
                h, w, c = img.shape

                #print(id, lm)

                #finding the exact pixel
                cx, cy = int(lm.x * w), int(lm.y * h)

                self.lmList.append([id, cx,cy])

                if draw:

                    #changes what the circles look like
                    cv2.circle(img, (cx, cy), 5, (255,0,255), cv2.FILLED)
        return self.lmList
    

    def findAngle(self, img, p1, p2, p3, draw = True):
         
         #get the landmarks
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        x3, y3 = self.lmList[p3][1:]



        #calculate the angle
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1-y2, x1-x2))
        if angle < 0:
             angle += 360
        
        
        # print (angle)






        #draw
        if draw:
              cv2.line(img, (x1, y1),(x2, y2),(255,255,255),3 )
              cv2.line(img, (x3, y3),(x2, y2),(255,255,255), 3)




              cv2.circle(img, (x1, y1), 10, (255,0,255), cv2.FILLED) 
              cv2.circle(img, (x1, y1), 15, (255,0,255), 2) 
                            
              cv2.circle(img, (x2, y2), 10, (255,0,255), cv2.FILLED)
              cv2.circle(img, (x2, y2), 15, (255,0,255), 2) 

              cv2.circle(img, (x3, y3), 10, (255,0,255), cv2.FILLED)
              cv2.circle(img, (x3, y3), 15, (255,0,255), 2) 
               
              cv2.putText(img, str(int(angle)), (x2 - 10, y2 + 50),
                          cv2.FONT_HERSHEY_COMPLEX, 2 , (0, 255, 0), 2)
              return angle 


              



#if we run by itself it runs the main function, but if we call another function it ignores it
def main():
    #reads the video
    cap = cv2.VideoCapture('Video/shooting_form.mp4')
    pTime = 0

    detector = poseDectector()


    while True:
    #gives the image
        success, img = cap.read()
        img = detector.findPose(img)

        lmList = detector.findPosition(img)
        print(lmList[14])
    

        cTime = time.time()
        fps= 1 / (cTime-pTime)
        pTime = cTime

        cv2.putText(img,str(int(fps)), (70,50), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 0, 0), 3)


        cv2.imshow("Image", img)

        #  second delay, slows down fps
        cv2.waitKey(100)




if __name__ == "__main__":
    main()