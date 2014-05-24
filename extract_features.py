#!/usr/bin/python
import sys,os
import cv2
import cv2.cv as cv
from PIL import Image, ImageOps

FACE_CLASSIFIER = '/usr/local/Cellar/opencv/2.3.1a/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml'
EYE_CLASSIFIER = '/Users/tim/mycode/findeyes/classifier/haarcascade_eye.xml'
CROP_DIR = '../data/crops2'

def detect_objects(fn, image):
        """Detects faces and then crops the image."""
        #image = cv2.cvtColor(image, cv.CV_RGB2GRAY)
        #clahe = cv2.createCLAHE(clipLimit=0.01)
        #image = clahe.apply(image)
        crop_file = '{}/{}-{}-{}.jpg'
        face_cl = cv2.CascadeClassifier(FACE_CLASSIFIER)
        eye_cl = cv2.CascadeClassifier(EYE_CLASSIFIER)   
        faces = face_cl.detectMultiScale(image, scaleFactor=1.1, minNeighbors=2, minSize=(100, 100), flags=cv.CV_HAAR_SCALE_IMAGE)
        print faces
        f = 1
        for (x,y,w,h) in faces:
            e = 1
            file, ext = os.path.splitext(fn)
            face_im = image[y:y+(h*.6), x:x+w]
            eyes = eye_cl.detectMultiScale(face_im, scaleFactor=1.1, minNeighbors=2, minSize=(40, 40), flags=cv.CV_HAAR_SCALE_IMAGE)
            if len(eyes) > 0:
                # If we can find an eye, then save the face.
                face = cv2.resize(image[y:y+h, x:x+w], (100, 100))
                cv2.imwrite(crop_file.format(CROP_DIR, os.path.basename(file), f, 0), face)
                # Save all the eyes.
                for (x,y,w,h) in eyes:
                # Minor contrast adjustment
                #im = cv2.equalizeHist(im)
                    eye = cv2.resize(face_im[y:y+h, x:x+w], (40, 40))
                    cv2.imwrite(crop_file.format(CROP_DIR, os.path.basename(file), f, e), eye)
                    e += 1
            f += 1

def process_image(fn):
    print fn
    image = cv2.imread(fn, 0);
    detect_objects(fn, image)

def main():
	image = cv2.imread(sys.argv[1], 0);
	detect_objects(sys.argv[1], image)

if __name__ == "__main__":
	main()
