import cv2
import time
import dlib
import csv
import os
import PIL
import datetime
import argparse
import imutils
import pandas
import random
import smtplib
import numpy as np
import seaborn as sn
from PIL import Image
from random import randint
from threading import Thread
from imutils import face_utils
import matplotlib.pyplot as plt
from imutils.video import VideoStream
from gaze_tracking import GazeTracking



def Average(lst):
    return sum(lst) / len(lst)

 
# creating a object
im = Image.open(r"Basic_Needs1.png")
#im = im.rotate(90, PIL.Image.NEAREST, expand = 1)

im.show()

ap = argparse.ArgumentParser()
ap.add_argument("-w", "--webcam", type=int, default=0,help="index of webcam on system")
args = vars(ap.parse_args())

EYE_AR_THRESH = 0.26

COUNTER = 0

print("-> Loading the predictor and detector...")
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")   
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

print("-> Starting Video Stream")
vs = VideoStream(src=args["webcam"]).start()
time.sleep(1.0)
ffc=0

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
counter=0
prevtext=""
row=[]
framescounter=0

for i in range(0,50):
    _, frame = webcam.read()
    cv2.putText(frame, "Please look at the center of the Image", (90, 60), cv2.FONT_HERSHEY_DUPLEX, 0.5, (147, 58, 31), 2)
    
    cv2.imshow("Eye Gaze", frame)
    cv2.moveWindow("Eye Gaze",200,200)
    cv2.waitKey(1) 
    if cv2.waitKey(1) == 27:
        break
   

ListcenterLeftx=[]
ListcenterLefty=[]
ListcenterRightx=[]
ListcenterRighty=[]

for i in range(0,20):
    # We send this frame to GazeTracking to analyze it
    try:
        gaze.refresh(frame)
        frame = gaze.annotated_frame()
        left_pupil = gaze.pupil_left_coords()
        right_pupil = gaze.pupil_right_coords()
        listleftpupil = list(left_pupil)
        ListcenterLeftx.append(listleftpupil[0])
        ListcenterLefty.append(listleftpupil[1])
        listrightpupil = list(right_pupil)
        ListcenterRightx.append(listrightpupil[0])
        ListcenterRighty.append(listrightpupil[1])
        #print(str(leftx),str(lefty),str(rightx),str(righty))
        #time.sleep(0.5)
        cv2.imshow("Eye Gaze", frame)
        cv2.waitKey(1) 
        if cv2.waitKey(1) == 27:
            break
    except:
        pass
CenterLeftXValue = Average(ListcenterLeftx)
CenterLeftYValue = Average(ListcenterLefty)
CenterRightXValue = Average(ListcenterRightx)
CenterRightYValue = Average(ListcenterRighty)

print(CenterLeftXValue,CenterLeftYValue,CenterRightXValue,CenterRightYValue)
water,restroom,food,emergency,blinking=0,0,0,0,0
Listleftx,Listlefty,Listrightx,Listrighty = [],[],[],[]

while True and framescounter<=3500:
    # We get a new frame from the webcam
    _, frame = webcam.read()

    # We send this frame to GazeTracking to analyze it
    gaze.refresh(frame)

    frame = gaze.annotated_frame()
    text = ""

    
    left_pupil = gaze.pupil_left_coords()
    right_pupil = gaze.pupil_right_coords()
    #print(type(left_pupil))
    try:
        listleftpupil=list(left_pupil)
        leftx=listleftpupil[0]
        Listleftx.append(leftx)
        lefty=listleftpupil[1]
        Listlefty.append(lefty)
        listrightpupil=list(right_pupil)
        rightx=listrightpupil[0]
        Listrightx.append(rightx)
        righty=listrightpupil[1]    
        Listrighty.append(righty)
    except:
        print(' ')

    #print('Left:'+str(left_pupil)+'Right:'+str(right_pupil))

    if gaze.is_blinking():
        prevtext=text
        text = "Blinking"
        blinking=blinking+1
        if prevtext=="Blinking":
            counter=counter+1
    elif leftx<=CenterLeftXValue and lefty>=CenterLeftYValue:
        text = "Medical Emergency"
        #print(text)
        emergency=emergency+1
        #if emergency > 150 :
        #   print("Patient is requesting Medical Emergency!")
        #    break
    elif leftx<=CenterLeftXValue and lefty<=CenterLeftYValue:
        text = "Food"
        #print(text)
        food = food+1
        #if food > 150 :
        #    print("Patient is requesting food!")
        #    break
    elif leftx>=CenterLeftXValue and lefty<=CenterLeftYValue:
        text = "Water"
        #print(text)
        water=water+1
        #if water > 150 :
        #    print("Patient is requesting water!")
        #    break
    elif leftx>=CenterLeftXValue and lefty>=CenterLeftYValue:
        text = "Restroom"
        #print(text)
        restroom=restroom+1
        #if restroom > 150 :
        #    print("Patient is requesting restroom!")
        #    break


    cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

    #center_pupil = (int(left_pupil)+int(right_pupil))/2
    cv2.putText(frame, "Left pupil:  " + str(left_pupil), (250, 360), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 0, 0), 1)
    cv2.putText(frame, "Right pupil: " + str(right_pupil), (250, 430), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 0, 0), 1)
    
    framescounter=framescounter+1
    
    cv2.imshow("Eye Co-ordinates", frame)
    
    if cv2.waitKey(1) == 27:
        break
   
webcam.release()
cv2.destroyAllWindows()
vs.stop()

if water>150 and water>food and water>restroom and water>emergency:
    message="Patient is requesting water!"
    print(message)
elif food>150 and food>water and food>restroom and food>emergency:
    message="Patient is requesting food!"
    print(message)
elif restroom>150 and restroom>water and restroom>food and restroom>emergency:
    message="Patient wants to go to restroom!"
    print(message)
elif emergency>150 and emergency>water and emergency>restroom and emergency>food:
    message="Patient is requesting emergency!"
    print(message)
elif blinking >150 and blinking>water and blinking>food and blinking>emergency and blinking>restroom:
        print("Patient is not looking the screen")

    
subject = "Alert!" 

# Construct the message
formatted_message = 'Subject: {}\n\n{}'.format(subject, message)

# Connect to the SMTP server
conn = smtplib.SMTP('smtp.gmail.com', 587)
conn.ehlo()
conn.starttls()

# Login to the sender's email account
conn.login('patient1.2403@gmail.com', 'julezvfqsryfrkrg')

# Send the email
conn.sendmail('patient1.2403@gmail.com','caretaker2403@gmail.com', formatted_message)
print("Mail sent successfully!")

# Disconnect from the server
conn.quit()


fields = ['Left_pupil','Right_pupil','Center_value']

rows=row
filename = "pupil.csv"
with open(filename, 'w') as csvfile:
	# creating a csv writer object
	csvwriter = csv.writer(csvfile)
		
	# writing the fields
	csvwriter.writerow(fields)
		
	# writing the data rows
	csvwriter.writerows(rows)



# creating the dataset
data = {'Water':water,"Food":food,"Restroom":restroom,"Medical Emergency":emergency}
needs = list(data.keys())
values = list(data.values())

fig = plt.figure(figsize = (10, 5))

# creating the bar plot
plt.bar(needs, values, color ='maroon',width = 0.4)

plt.xlabel("View Locations")
plt.ylabel("Total Amount of Time")
plt.title("view based on Gaze")
plt.show()

plt.hist2d(Listleftx,Listlefty,bins=[np.arange(0,400,1),np.arange(0,300,1)])

