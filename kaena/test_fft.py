import unittest
from structures import CommunicationNetwork, Person, MessageType
from fft_compressed_communication import fft_compress_message, send_compressed_message

class TestFFTCompression(unittest.TestCase):

    def setUp(self):
        """Set up a sample communication network for testing."""
        self.network = CommunicationNetwork()
        self.kaena = Person(id="Kaena")
        self.sylva = Person(id="Sylva")
        self.network.add_person(self.kaena)
        self.network.add_person(self.sylva)
        self.network.add_connection("Kaena", "Sylva")

    def test_compression_validity(self):
        """Test that a compressed message is generated and metadata is correct."""
        original_message = "FFT compression test."
        compression_ratio = 0.5

        message = send_compressed_message(
            self.network, "Kaena", "Sylva", original_message, compression_ratio
        )

        self.assertEqual(message.sender, self.kaena)
        self.assertEqual(message.receiver, self.sylva)
        self.assertEqual(message.metadata.message_type, MessageType.FFT_COMPRESSED)
        self.assertEqual(message.metadata.original_length, len(original_message))
        self.assertAlmostEqual(message.metadata.compression_ratio, compression_ratio)
        self.assertNotEqual(original_message, message.body)

    def test_invalid_compression_ratio(self):
        """Test that an invalid compression ratio raises an error."""
        original_message = "Invalid compression test"
        with self.assertRaises(ValueError):
            send_compressed_message(
                self.network, "Kaena", "Sylva", original_message, 1.5
            )

        with self.assertRaises(ValueError):
            send_compressed_message(
                self.network, "Kaena", "Sylva", original_message, 0
            )

    def test_no_sender_or_receiver(self):
        """Test that sending a message without a valid sender or receiver raises an error."""
        original_message = "Missing participant test"

        with self.assertRaises(ValueError):
            send_compressed_message(
                self.network, "Unknown", "Sylva", original_message, 0.5
            )

        with self.assertRaises(ValueError):
            send_compressed_message(
                self.network, "Kaena", "Unknown", original_message, 0.5
            )

    def test_message_compression_ratio_effect(self):
        """Test the effect of different compression ratios on message compression."""
        original_message = "This is a test message for compression ratios."

        # High compression ratio (retain most frequencies)
        high_compression_message = send_compressed_message(
            self.network, "Kaena", "Sylva", original_message, 0.9
        )

        # Low compression ratio (retain fewer frequencies)
        low_compression_message = send_compressed_message(
            self.network, "Kaena", "Sylva", original_message, 0.1
        )

        self.assertNotEqual(original_message, high_compression_message.body)
        self.assertNotEqual(original_message, low_compression_message.body)
        self.assertNotEqual(high_compression_message.body, low_compression_message.body)

if __name__ == "__main__":
    unittest.main()
