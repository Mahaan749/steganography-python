import unittest
import os
from PIL import Image
from stenography import SteganographyApp
import tkinter as tk


class TestSteganography(unittest.TestCase):

    def setUp(self):
        """Prepare test environment"""
        self.cover_image = "test_cover.png"
        self.stego_image = "test_stego.png"

        # create test image
        img = Image.new("RGB", (200, 200), color=(255, 255, 255))
        img.save(self.cover_image)

        root = tk.Tk()
        root.withdraw()
        self.app = SteganographyApp(root)

    def tearDown(self):
        """Clean test files"""
        if os.path.exists(self.cover_image):
            os.remove(self.cover_image)

        if os.path.exists(self.stego_image):
            os.remove(self.stego_image)

    def test_hide_message(self):
        """Verify message hiding works correctly"""
        message = "Hello World"

        self.app._hide_text(self.cover_image, message, self.stego_image)
        extracted = self.app._extract_text(self.stego_image)

        self.assertEqual(message, extracted)

    def test_extract_without_message(self):
        """Check extraction from non-stego image"""
        with self.assertRaises(ValueError):
            self.app._extract_text(self.cover_image)

    def test_message_too_large(self):
        """Ensure large messages are rejected"""
        message = "A" * 100000

        with self.assertRaises(ValueError):
            self.app._hide_text(self.cover_image, message, self.stego_image)

    def test_medium_message(self):
        """Test encoding and decoding of medium message"""
        message = "This is a test message for steganography."

        self.app._hide_text(self.cover_image, message, self.stego_image)
        extracted = self.app._extract_text(self.stego_image)

        self.assertEqual(message, extracted)


if __name__ == "__main__":
    unittest.main()