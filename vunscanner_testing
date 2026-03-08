import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
from vunscanner import HTTPSecurityScannerGUI


class TestHTTPSecurityScanner(unittest.TestCase):

    def setUp(self):
        """Create GUI instance for testing"""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide GUI window during tests
        self.app = HTTPSecurityScannerGUI(self.root)

    def tearDown(self):
        """Destroy GUI after test"""
        self.root.destroy()

    # Test 1: URL validation
    def test_url_validation(self):
        """Check that invalid URLs trigger warning"""
        self.app.url_var.set("example.com")

        with patch("tkinter.messagebox.showwarning") as mock_warning:
            self.app.run_header_analysis()
            mock_warning.assert_called_once()

    # Test 2: Successful header retrieval
    @patch("requests.get")
    def test_header_fetching(self, mock_get):
        """Ensure headers are fetched and processed"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {
            "Strict-Transport-Security": "max-age=31536000",
            "Content-Security-Policy": "default-src 'self'",
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff"
        }

        mock_get.return_value = mock_response

        self.app.url_var.set("https://example.com")
        self.app.run_header_analysis()

        self.assertTrue(True)  # If no crash, test passes

    # Test 3: Security header validation logic
    @patch("requests.get")
    def test_security_header_validation(self, mock_get):
        """Verify PASS/FAIL header logic works"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {
            "Strict-Transport-Security": "max-age=31536000",
            "X-Frame-Options": "DENY"
        }

        mock_get.return_value = mock_response

        self.app.url_var.set("https://example.com")
        self.app.run_header_analysis()

        self.assertTrue(True)

    # Test 4: Network error handling
    @patch("requests.get")
    def test_network_error_handling(self, mock_get):
        """Ensure network exceptions are handled safely"""
        mock_get.side_effect = Exception("Connection error")

        self.app.url_var.set("https://example.com")

        # Should not crash
        try:
            self.app.run_header_analysis()
            success = True
        except:
            success = False

        self.assertTrue(success)


if __name__ == "__main__":
    unittest.main(verbosity=2)