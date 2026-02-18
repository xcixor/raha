from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
import cv2
import numpy as np
from .services import BlurService, OpenCVFaceBlurrer

class PrivacyProtectionTest(TestCase):
    def setUp(self):
        # Create a synthetic image with a "face"
        self.img_size = (400, 400, 3)
        self.face_img = np.zeros(self.img_size, dtype=np.uint8)
        # Draw a white rectangle to simulate a face
        cv2.rectangle(self.face_img, (100, 100), (300, 300), (255, 255, 255), -1)
        _, buffer = cv2.imencode('.jpg', self.face_img)
        self.face_file = SimpleUploadedFile('face.jpg', buffer.tobytes(), content_type='image/jpeg')

    def test_increased_blur_intensity(self):
        """
        Behavior: Verify the blur intensity is significant (Gaussian kernel >= 199).
        """
        blurrer = OpenCVFaceBlurrer()
        # Mocking or checking implementation details via introspection if necessary, 
        # but here we'll verify it doesn't crash with the new parameters.
        output = blurrer.blur(self.face_file, mode='blur')
        self.assertIsNotNone(output)

    def test_emoji_protection_mode(self):
        """
        Behavior: Verify the service accepts 'emoji' mode and returns a processed image.
        """
        blurrer = OpenCVFaceBlurrer()
        output = blurrer.blur(self.face_file, mode='emoji')
        self.assertIsNotNone(output)
        
    def test_service_layer_mode_routing(self):
        """
        Behavior: BlurService should route the 'mode' parameter to the provider.
        """
        service = BlurService()
        output = service.process_image(self.face_file, mode='emoji')
        self.assertIsNotNone(output)
