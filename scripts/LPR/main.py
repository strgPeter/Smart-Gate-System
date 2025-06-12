import cv2
import LPR as lpr
import subprocess
import os

filename = 'capture'
i=0

while True:

    i += 1
    
    with open(os.devnull, 'w') as FNULL:
      retcode = subprocess.call(
          ['fswebcam', '-r', '640x480', '--no-banner', filename + str(i) + ".jpg"],
          stdout=FNULL,
          stderr=FNULL
      )
    if retcode != 0:
        print("Fehler beim Aufnehmen mit fswebcam")
        break

    frame = cv2.imread(filename+str(i)+".jpg")

    if frame is None:
        print("Fehler beim Laden des Bildes:", filename+str(i)+".jpg")
    else:
        lpr.rec(frame)
        
    if os.path.exists(filename+str(i)+".jpg"):
      os.remove(filename+str(i)+".jpg")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
