import cv2
import numpy as np
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class FaceBlurrer:
    def blur(self, image_field):
        """
        Abstract/Base logic for blurring. 
        Expects a Django ImageField.
        """
        raise NotImplementedError

class OpenCVFaceBlurrer(FaceBlurrer):
    def __init__(self):
        # Using the default frontal face haar cascade
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def blur(self, image_field):
        # Read image
        nparr = np.frombuffer(image_field.read(), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return image_field

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in faces:
            # Extract the ROI (Region of Interest)
            roi = img[y:y+h, x:x+w]
            # Apply Gaussian Blur
            roi = cv2.GaussianBlur(roi, (99, 99), 30)
            # Put back in original image
            img[y:y+h, x:x+w] = roi

        # Convert back to Django-friendly format
        _, buffer = cv2.imencode('.jpg', img)
        content = ContentFile(buffer.tobytes())
        
        # Return new content with original name
        return content

class BlurService:
    def __init__(self, provider: FaceBlurrer = None):
        self.provider = provider or OpenCVFaceBlurrer()

    def process_image(self, image_field):
        return self.provider.blur(image_field)
