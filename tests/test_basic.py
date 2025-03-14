import tempfile
import unittest
from pathlib import Path

from PIL import Image

from ic.coder.simple import SimpleCoder
from ic.decoder.simple import SimpleAutoCropper, SimpleDecoder


class TestBasicCodingDecoding(unittest.TestCase):
    """Basic test case for encoding and decoding functionality."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.test_data = "hallo!".encode("utf-8") * (1024 * 1024)
        self.test_filename = "test_file.txt"
        self.image_path = self.temp_path / "encoded.png"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_happy_path_encode_decode_file(self):

        coder = SimpleCoder(w=2048)
        image = coder.encode(self.test_data, self.test_filename)
        image.save(self.image_path, format="PNG")
        self.assertTrue(self.image_path.exists())

        decoder = SimpleDecoder(str(self.image_path))
        decoded_data, decoded_filename = decoder.decode()

        self.assertEqual(decoded_data, self.test_data)
        self.assertEqual(decoded_filename, self.test_filename)

    def test_happy_path_encode_decode_image(self, w=2048):

        coder = SimpleCoder(w=w)
        image = coder.encode(self.test_data, self.test_filename)
        self.assertIsInstance(image, Image.Image)
        self.assertEqual(image.size[0], w, f"image.w ≠ {w}")

        decoder = SimpleDecoder(image)
        decoded_data, decoded_filename = decoder.decode()

        self.assertEqual(decoded_data, self.test_data)
        self.assertEqual(decoded_filename, self.test_filename)

    def test_happy_path_encode_decode_image_padding(self, px=89, py=123):

        coder = SimpleCoder(w=2048)
        image = coder.encode(self.test_data, self.test_filename)
        w, h = image.size
        padded_image = Image.new("RGB", (w + px, h + py), (12, 34, 56))
        padded_image.paste(image, (px // 2, py // 2))

        failed = False
        try:
            decoder = SimpleDecoder(padded_image)
            decoded_data, decoded_filename = decoder.decode()
        except ValueError as e:
            failed = True
            print(f"failed as expected: {e}")
        self.assertTrue(failed, "expected to fail")

        failed = False
        try:
            cropped_image = SimpleAutoCropper(padded_image).autocrop()
            decoder = SimpleDecoder(cropped_image)
            decoded_data, decoded_filename = decoder.decode()
        except ValueError as e:
            failed = True
            print(f"unexpectedly failed: {e}")

        self.assertFalse(failed, "expected to succeed")
        self.assertEqual(decoded_data, self.test_data)
        self.assertEqual(decoded_filename, self.test_filename)


if __name__ == "__main__":
    unittest.main()
