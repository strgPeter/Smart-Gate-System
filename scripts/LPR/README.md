## License Plate Recognition 
LPR is a technology that uses optical character recognition on images to read vehicle registration plates to create vehicle location data.

## Prerequisites

1. Connect USB Camera and LCD Display to your RPi.
2. Install [Python](https://www.python.org/).
3. Install 

   ```
   sudo apt install \
     python3-numpy
	 libcamera-apps \
     python3-pip \
     python3-venv \
     python3-opencv \
     python3-rpi.gpio \
     tesseract-ocr \
     libtesseract-dev \
	 fswebcam
   ```
   
   ```
   sudo pip3 install imutils
   ```
   ```
   sudo pip3 install pytesseract
   ```

## How to run

After the prerequisites, download or clone repository, locate folder in terminal and run following command

```
python3 main.py
```