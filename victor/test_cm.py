import unittest
from structures import MessageType, Person, MessageMetadata, Message, CommunicationNetwork
from compressed_messages import ExtendedCommunicationNetwork

class TestRLECompression(unittest.TestCase):
    def setUp(self):
        # Initialize network and test users
        self.network = ExtendedCommunicationNetwork()
        self.alice = Person(id="alice")
        self.bob = Person(id="bob")
        
        # Add persons to network
        self.network.add_person(self.alice)
        self.network.add_person(self.bob)
        self.network.add_connection("alice", "bob")

    def test_rle_encode_decode_basic(self):
        test_cases = [
            "",  # Empty string
            "A",  # Single character
            "AABBB",  # Simple repeating pattern
            "Hello",  # Regular word
            "WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWB"  # Long repeating sequence
        ]
        
        for test_str in test_cases:
            with self.subTest(test_str=test_str):
                # Send message
                message = self.network.send_rle_compressed_message(
                    sender_id="alice",
                    receiver_id="bob",
                    message_body=test_str
                )
                
                # Print actual results for verification
                print(f"\nTest string: {test_str}")
                print(f"Encoded message: {message.body}")
                decoded = self.network.receive_rle_compressed_message(message)
                print(f"Decoded message: {decoded}")

                # Verify message properties
                self.assertEqual(message.sender, self.alice)
                self.assertEqual(message.receiver, self.bob)
                self.assertEqual(message.metadata.message_type, MessageType.RLE_COMPRESSED)
                self.assertEqual(message.metadata.original_length, len(test_str))
                self.assertEqual(decoded, test_str)

    def test_invalid_message_type(self):
        # Create message with wrong type
        message = Message(
            sender=self.alice,
            receiver=self.bob,
            metadata=MessageMetadata(message_type=MessageType.PLAIN),
            body="test"
        )
        
        # Should raise error when trying to decode non-RLE message
        with self.assertRaises(ValueError):
            self.network.receive_rle_compressed_message(message)

    def test_invalid_persons(self):
        # Test sending to non-existent person
        with self.assertRaises(ValueError):
            self.network.send_rle_compressed_message(
                sender_id="alice",
                receiver_id="charlie",  # Non-existent person
                message_body="test"
            )
    
    def test_edge_cases(self):
        test_cases = [
            "A" * 100,
            "ABCDEFG", 
            "AAA BBB CCC", 
        ]
        
        for test_str in test_cases:
            with self.subTest(test_str=test_str):
                message = self.network.send_rle_compressed_message(
                    sender_id="alice",
                    receiver_id="bob",
                    message_body=test_str
                )
                decoded = self.network.receive_rle_compressed_message(message)
                self.assertEqual(decoded, test_str)

if __name__ == '__main__':
    unittest.main(verbosity=2)