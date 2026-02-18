import cv2
import numpy as np
import tempfile
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from .services import BlurService

class FaceBlurringTest(TestCase):
    def setUp(self):
        self.blur_service = BlurService()
        
        # Create a synthetic image with a "face" (a white rectangle)
        # Haar cascades might not detect this, so for a real behavioral test 
        # we'd ideally use a small real face sample, but let's start with structural delta.
        self.img_size = (200, 200, 3)
        self.face_img = np.zeros(self.img_size, dtype=np.uint8)
        # Draw a white rectangle to simulate a face-like object
        cv2.rectangle(self.face_img, (50, 50), (150, 150), (255, 255, 255), -1)
        
        _, buffer = cv2.imencode('.jpg', self.face_img)
        self.face_file = SimpleUploadedFile('face.jpg', buffer.tobytes(), content_type='image/jpeg')

    def test_blur_service_produces_output(self):
        """
        Behavior: The service must return a ContentFile regardless of detection.
        """
        output = self.blur_service.process_image(self.face_file)
        self.assertIsNotNone(output)
        self.assertTrue(output.size > 0)

    def test_processing_integration(self):
        """
        Behavior: Ensure the service integrates with the OpenCV backend without crashing.
        """
        try:
            output = self.blur_service.process_image(self.face_file)
            processed_content = output.read()
            self.assertNotEqual(len(processed_content), 0)
        except Exception as e:
            self.fail(f"BlurService raised {type(e).__name__} unexpectedly!")

    def test_double_read_behavior(self):
        """
        Behavior: Ensure the service can handle an image file that has already been read/polled.
        """
        self.face_file.read() # Move pointer to end
        output = self.blur_service.process_image(self.face_file)
        self.assertIsNotNone(output)
        output.seek(0)
        self.assertNotEqual(len(output.read()), 0)
