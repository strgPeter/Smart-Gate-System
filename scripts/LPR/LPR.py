import cv2
import imutils
import numpy as np
import pytesseract
import paho.mqtt.client as mqtt
import json

client = mqtt.Client()


def rec(img):

    print("Starting detection...")


    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17) 
    edged = cv2.Canny(gray, 30, 200)

    try:
        
        cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]
        screenCnt = None

        
        for c in cnts:
            
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.018 * peri, True)

            
            if len(approx) == 4:
                screenCnt = approx
                break
              
        if screenCnt is None:
            print("NOT DETECTED")
            detected = 0
        else:
            print("DETECTED")
            detected = 1


        if detected == 1:
            cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)

            mask = np.zeros(gray.shape, np.uint8)
            new_image = cv2.drawContours(mask, [screenCnt], 0, 255, -1,)
            new_image = cv2.bitwise_and(img, img, mask=mask)
    
            
            (x, y) = np.where(mask == 255)
            (topx, topy) = (np.min(x), np.min(y))
            (bottomx, bottomy) = (np.max(x), np.max(y))
            Cropped = gray[topx:bottomx + 1, topy:bottomy + 1]
    
            
            text = pytesseract.image_to_string(
                Cropped, config="-c tessedit_char_whitelist='ABCDEFGHIJKLMNOPRSTUVYZ0123456789'")
            text = text.rstrip("\n")
            
            
            print("RAW TEXT: " + text)
            
            client.connect("10.0.0.1", 1883, 60)
            msg = {
                "plate-present":text
            }
              
            client.publish("plate", json.dumps(msg))
            
            if text == "TKBL08" :
            
              print("OPEN GATE")
              client.connect("10.0.0.1", 1883, 60)
              msg = {
                "action":"open"
              }
              
              client.publish("barrier", json.dumps(msg))
              
            client.disconnect()
              

    except Exception:
        pass
    return img
