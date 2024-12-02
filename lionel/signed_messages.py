import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature
from typing import Tuple, Optional

from structures import (
    Message,
    MessageType,
    Person,
    MessageMetadata,
    CommunicationNetwork
)

class SignedMessenger:
    def __init__(self, network: CommunicationNetwork):
        self.network = network

    def generate_key_pair(self) -> Tuple[bytes, bytes]:
        """Generate a new RSA key pair."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
    
        # Properly serialize the keys
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
        return private_bytes, public_bytes

    def calculate_message_hash(self, message_body: str) -> bytes:
        """Calculate the SHA-256 hash of a message."""
        digest = hashes.Hash(hashes.SHA256())
        digest.update(message_body.encode())
        return digest.finalize()

    def encrypt_hash(self, message_hash: bytes, private_key: bytes) -> bytes:
        """Encrypt (sign) the message hash using the sender's private key."""
        key = serialization.load_pem_private_key(private_key, password=None)
        signature = key.sign(
            message_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    def verify_signature(self, message_hash: bytes, signature: bytes, public_key: bytes) -> bool:
        """Verify the signature using the sender's public key."""
        try:
            key = serialization.load_pem_public_key(public_key)
            key.verify(
                signature,
                message_hash,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False

    def send_signed_message(self, sender_id: str, receiver_id: str, message_body: str) -> Optional[Message]:
        """Send a signed message from one person to another."""
        sender = self.network.get_person(sender_id)
        receiver = self.network.get_person(receiver_id)

        if not (sender and receiver and sender.private_key):
            return None

        # Calculate message hash and create signature
        message_hash = self.calculate_message_hash(message_body)
        signature = self.encrypt_hash(message_hash, sender.private_key)

        # Create metadata for signed message
        metadata = MessageMetadata(
            message_type=MessageType.SIGNED,
            signature=signature,
            original_hash=message_hash
        )

        # Create and return the signed message
        return Message(
            sender=sender,
            receiver=receiver,
            metadata=metadata,
            body=message_body
        )

    def verify_received_message(self, message: Message) -> bool:
        """Verify a received signed message."""
        if message.metadata.message_type != MessageType.SIGNED:
            return False

        # Calculate hash of received message
        calculated_hash = self.calculate_message_hash(message.body)

        # Verify that the calculated hash matches the original hash
        if calculated_hash != message.metadata.original_hash:
            return False

        # Verify the signature
        return self.verify_signature(
            message.metadata.original_hash,
            message.metadata.signature,
            message.sender.public_key
        )

if __name__ == "__main__":
    # Example usage
    network = CommunicationNetwork()
    
    # Create some people
    alice = Person("alice")
    bob = Person("bob")
    
    # Generate keys for both people
    messenger = SignedMessenger(network)
    alice_private, alice_public = messenger.generate_key_pair()
    bob_private, bob_public = messenger.generate_key_pair()
    
    alice.private_key = alice_private
    alice.public_key = alice_public
    bob.private_key = bob_private
    bob.public_key = bob_public
    
    # Add people to network
    network.add_person(alice)
    network.add_person(bob)
    network.add_connection("alice", "bob")
    
    # Send a signed message
    message = messenger.send_signed_message("alice", "bob", "Hello, Bob! This is a signed message.")
    
    # Verify the message
    if message:
        is_valid = messenger.verify_received_message(message)
        print(f"Message verification result: {is_valid}")