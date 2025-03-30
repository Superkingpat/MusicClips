import cv2
import time
import numpy as np

def getActiveArea(clip_path):
    clip = cv2.VideoCapture(clip_path)
    bgSubtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
    boxes = []
    last_img = None

    while True:
        img = clip.read()[1]
        
        if img is None:
            break
        last_img = img

        mask = bgSubtractor.apply(img)

        _,thresh = cv2.threshold(mask, 150, 255, cv2.THRESH_BINARY)
        thresh = cv2.erode(thresh, None)
        thresh = cv2.dilate(thresh, None)
        contur,hirarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contur:
            area = cv2.contourArea(cnt)
            if area > 1000:
                x,y,w,h = cv2.boundingRect(cnt)
                boxes.append(np.array([x,y,x+w,y+h]))
                box = np.array(boxes)
                cv2.rectangle(img, (x,y), (x+w,y+h),(255,255,255),2)
                cv2.rectangle(last_img, (np.min(box[:, 0]),np.min(box[:, 1])), (np.max(box[:, 2]),np.max(box[:, 3])),(0,0,0),2)

        cv2.imshow("vid",img)
        cv2.imshow("thresh",thresh)
        cv2.waitKey(30)

    
    
    for box in boxes:
        cv2.rectangle(last_img, (box[0],box[1]), (box[2],box[3]),(255,255,255),2)
    cv2.imshow("vid",last_img)
    boxes = np.array(boxes)

    cv2.rectangle(last_img, (np.min(boxes[:, 0]),np.min(boxes[:, 1])), (np.max(boxes[:, 2]),np.max(boxes[:, 3])),(0,0,0),4)
    cv2.imshow("X",last_img)
    cv2.waitKey()


getActiveArea(r"C:\Users\patri\Documents\GitHub\MusicClips\data\packs\PianoTestPack\A4.mp4")