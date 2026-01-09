#imports all the tkinter symbols
import threading
import tkinter as tk
from tkinter import *
#PIL bridges opencv
from PIL import Image, ImageTk

import cv2


#making a seprate class so it makes my code more clean
class shotGUI:

    #constructor, setting up the window and widgets
    def __init__(self):

        #creating the window
        self.root = tk.Tk()

        #setting the dimensions of the window
        self.root.geometry("1200x720")

        #creating frame in the window,setting the background and width
        self.statsFrame = Frame(self.root, width = 300, bg ="lightgray")
        
        #pack places the frame to the left, fill makes it stretch vertically to fill the window
        self.statsFrame.pack(side=LEFT, fill = Y)

        #text labels in the stat frame showing the statistics, font+size as well
        self.shotCountLabel = Label(self.statsFrame, text="Shots: 0", font=("Arial", 16), bg="lightgray")
        self.makesLabel = Label(self.statsFrame, text="Makes: 0", font=("Arial", 16), bg="lightgray")
        self.missesLabel = Label(self.statsFrame, text="Misses: 0", font=("Arial", 16), bg="lightgray")
        self.percentageLabel = Label(self.statsFrame, text="Percentage: 0.0%", font=("Arial", 16), bg="lightgray")

        #packs labels in stats frame, pady adds vertical padding
        self.shotCountLabel.pack(pady=10)
        self.makesLabel.pack(pady=10)
        self.missesLabel.pack(pady=10)
        self.percentageLabel.pack(pady=10)

        #right panel for video
        self.videoFrame = Frame(self.root)

        # places the video frame on the right side of the window,
        # fill=both stretches the camera both ways
        self.videoFrame.pack(side=RIGHT, fill=BOTH, expand=True)

        #label that displays the video frames as images
        self.videoLabel = Label(self.videoFrame)

        self.videoLabel.pack(fill=BOTH, expand=True)


    #method to refresh the stats text when the main updates the statistics
    #config changes the widget after the creation
    def updateStats(self, stats):
        if isinstance(stats, dict):
            # Update all statistics if stats is a dictionary
            self.shotCountLabel.config(text=f"Shots: {stats.get('count', 0)}")
            self.makesLabel.config(text=f"Makes: {stats.get('makes', 0)}")
            self.missesLabel.config(text=f"Misses: {stats.get('misses', 0)}")
            self.percentageLabel.config(text=f"Percentage: {stats.get('percentage', 0.0)}%")
        else:
            # Backward compatibility - if just a number is passed, treat as shot count
            self.shotCountLabel.config(text=f"Shots: {stats}")
            self.makesLabel.config(text="Makes: 0")
            self.missesLabel.config(text="Misses: 0")
            self.percentageLabel.config(text="Percentage: 0.0%")
    

    #converts array frame from opencv to Tk, i
    # ImageTk.PhotoImage = converts PIL to tk image object
    # Image.fromarray(frame) = turns array into PIL image
    def updateVideo(self, frame):
        img = ImageTk.PhotoImage(image=Image.fromarray(frame))

        #keeping reference to photoImage
        self.videoLabel.imgtk = img

        #updates the label to display the new frame 
        self.videoLabel.config(image=img)

    def startVideo(self, aiTrainerObj):
        def videoLoop():
            while True:
                frame, stats = aiTrainerObj.processFrame()
                if frame is not None:
                    frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.updateVideo(frameRGB)
                    if stats:
                        self.updateStats(stats['count'])
        thread = threading.Thread(target=videoLoop, daemon= True)
        thread.start()    

    def run(self):
        # if you previously created a different mainloop call, replace with:
        self.root.mainloop()

