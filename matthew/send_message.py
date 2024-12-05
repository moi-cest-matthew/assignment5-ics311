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

"""Using English Wikipedia's description of how RSA encryption works,
   simulate the encryption, sending, recieving, and decrypting of
   RSA-encrypted messages."""
class EncryptedMessenger:
    def __init__(self, network: CommunicationNetwork):
        self.network = network
        
    def generate_rsa_keys(key_size=2048): 
    """Generates a new RSA key pair."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,  # Common public exponent value
        key_size=key_size, 
        backend=backends.default_backend()
    )

    public_key = private_key.public_key()

    return private_key, public_key
        
    def encrypt_message(self, sender: Person, receiver: Person, message: str) -> Message:
        """Encrypts a message using RSA and returns an encrypted Message object."""
        public_key = receiver.public_key  # Use the receiver's public key for encryption
        if not public_key:
            raise ValueError("Receiver's public key is missing!")

        private_key = sender.private_key 
        if not private_key:
            raise ValueError("Sender's private key is missing!")

        # Generate an RSA key pair if none exist
        if not sender.public_key:
            sender.generate_rsa_keys()  
        if not receiver.public_key:
            receiver.generate_rsa_keys() 

        ciphertext = rsa.encrypt(
            message.encode(), public_key, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

        metadata = MessageMetadata(
            message_type=MessageType.ENCRYPTED,
            original_length=len(message), 
        )
        return Message(sender, receiver, metadata, ciphertext.decode())   

    def decrypt_message(self, sender: Person, message: Message) -> str:  
        """Decrypts an encrypted message using the recipient's private key."""
        if message.metadata.message_type != MessageType.ENCRYPTED:
            raise ValueError("Message is not encrypted!") 

        private_key = sender.private_key  
        if not private_key:
            raise ValueError("Sender's private key is missing!")

        plaintext = rsa.decrypt(
            message.body.encode(), private_key, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        ).decode() 
        return plaintext
        
if __name__ == "__main__":
    network = CommunicationNetwork()
    network.add_person(Person(id="Alice", public_key=b"alice_public_key"))  # Replace with actual keys
    network.add_person(Person(id="Bob", public_key=b"bob_public_key"))   

    messenger = EncryptedMessenger(network)

    message = "This is a secret message!"
    encrypted_message = messenger.encrypt_message(Person(id="Alice"), Person(id="Bob"), message) 
    print("Encrypted Message:", encrypted_message)  

    decrypted_message = messenger.decrypt_message(Person(id="Bob"), encrypted_message)
    print("Decrypted Message:", decrypted_message)
    
   
