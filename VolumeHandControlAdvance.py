import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

################################
wCam, hCam = 640, 480
################################

cap = cv2.VideoCapture(1)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7,maxHands=1)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
area = 0
colorVol = (255,0,0)
while True:
    success, img = cap.read()

    # Find Hand
    img = detector.findHands(img)
    lmList,bbox  = detector.findPosition(img, draw=True)
    if len(lmList) != 0:

        # Filter Based On Size
        area = (bbox[2]-bbox[0])*(bbox[3]-bbox[1])//100
        if 250<area<1000:
            # print("yes")
            # Find Distance Between index and thumb
            length,img,line_info = detector.findDistance(4,8,img)
            # print(length)


            # Convert Volume
            volBar = np.interp(length, [50, 200], [400, 150])
            volPer = np.interp(length, [50, 200], [0, 100])
            # print(int(length), vol)
            # volume.SetMasterVolumeLevel(vol, None)



            # Reduce Resulution to make it better
            # smoothness = 1
            # volPer = smoothness * round(volPer/100,None)


            # Check fingers up
            fingers = detector.fingersUp()
            print(fingers)
            # if pinky is down set Volume
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                cv2.circle(img, (line_info[4], line_info[5]), 15, (0, 255, 0), cv2.FILLED)
                colorVol = (0,255,0)
                time.sleep(0.25)
            else:
                colorVol = (0,255,0)

            # Drawings
            cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
            cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
            cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                        1, (255, 0, 0), 3)
            cVol = int(volume.GetMasterVolumeLevelScalar()*100)

            cv2.putText(img, f'Vol Set : {int(cVol)}', (400, 50), cv2.FONT_HERSHEY_COMPLEX,
                        1, colorVol, 3)


            # Frame Rate
            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                        1, (255, 0, 0), 3)

            # print(lmList[4], lmList[8])


            # print(length)

            # Hand range 50 - 300
            # Volume Range -65 - 0






    cv2.imshow("Img", img)
    cv2.waitKey(1)