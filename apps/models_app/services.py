import cv2
import numpy as np
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings

class FaceBlurrer:
    def blur(self, image_field, mode='blur'):
        """
        Abstract/Base logic for protection. 
        Expects a Django ImageField.
        Modes: 'blur', 'emoji'
        """
        raise NotImplementedError

class OpenCVFaceBlurrer(FaceBlurrer):
    def __init__(self):
        # Using the default frontal face haar cascade
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Path for the emoji overlay
        self.emoji_path = os.path.join(settings.BASE_DIR, 'static/img/privacy_emoji.png')

    def blur(self, image_field, mode='blur'):
        # Read image
        image_field.seek(0)
        file_content = image_field.read()
        if not file_content:
            return image_field
            
        nparr = np.frombuffer(file_content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return image_field

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in faces:
            if mode == 'emoji' and os.path.exists(self.emoji_path):
                # Load emoji with alpha channel
                emoji = cv2.imread(self.emoji_path, cv2.IMREAD_UNCHANGED)
                if emoji is not None:
                    # Resize emoji to fit the face ROI
                    emoji_resized = cv2.resize(emoji, (w, h))
                    
                    # Extract channels
                    emoji_img = emoji_resized[:, :, 0:3]
                    mask = emoji_resized[:, :, 3] / 255.0
                    
                    # Composite
                    for c in range(0, 3):
                        img[y:y+h, x:x+w, c] = (mask * emoji_img[:, :, c] + (1 - mask) * img[y:y+h, x:x+w, c])
                else:
                    self._apply_black_smudge(img, x, y, w, h)
            else:
                self._apply_black_smudge(img, x, y, w, h)

        # Convert back to Django-friendly format
        _, buffer = cv2.imencode('.jpg', img)
        content = ContentFile(buffer.tobytes())
        
        return content

    def _apply_black_smudge(self, img, x, y, w, h):
        # Calculate center and radius for the circular smudge
        center = (x + w // 2, y + h // 2)
        # Radius set to 40% of max dimension (Diameter = 80%)
        radius = int(max(w, h) * 0.40) 
        
        # Create an overlay for the alpha-blended smudge
        overlay = img.copy()
        cv2.circle(overlay, center, radius, (0, 0, 0), -1)
        
        # Blend the solid black circle with 98% opacity
        alpha = 0.98
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

class BlurService:
    def __init__(self, provider: FaceBlurrer = None):
        self.provider = provider or OpenCVFaceBlurrer()

    def process_image(self, image_field, mode='blur'):
        return self.provider.blur(image_field, mode=mode)
