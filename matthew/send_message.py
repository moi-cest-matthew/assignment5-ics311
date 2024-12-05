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

def generate_rsa_keys(key_size=2048):
     """Generates a new RSA key pair."""   
     private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
     public_key = private_key.public_key()
     return private_key, public_key

"""Using English Wikipedia's description of how RSA encryption works,
   simulate the encryption, sending, recieving, and decrypting of
   RSA-encrypted messages."""
class EncryptedMessenger:
    def __init__(self, network: CommunicationNetwork):
        self.network = network
        
    def encrypt_message(self, sender: Person, receiver: Person, metadata: MessageMetadata, message: str) -> Message:
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

        ciphertext = public_key.encrypt(
            message.encode(), padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

        metadata = MessageMetadata(
            message_type=MessageType.ENCRYPTED,
            original_length=len(message), 
        )
        return Message(sender, receiver, metadata, ciphertext)   

    def decrypt_message(self, sender: Person, message: Message) -> str:  
        """Decrypts an encrypted message using the recipient's private key."""
        if message.metadata.message_type != MessageType.ENCRYPTED:
            raise ValueError("Message is not encrypted!") 

        private_key = sender.private_key  
        if not private_key:
            raise ValueError("Sender's private key is missing!")

        plaintext = private_key.decrypt(
            message, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        ).decode() 
        return plaintext
        
if __name__ == "__main__":

    network = CommunicationNetwork()
    messenger = EncryptedMessenger(network)
    
    alice = Person("Alice")
    bob = Person("Bob")
    
    alice_private, alice_public = generate_rsa_keys()
    bob_private, bob_public = generate_rsa_keys()
    
    alice.private_key = alice_private
    alice.public_key = alice_public
    bob.private_key = bob_private
    bob.public_key = bob_public
    
    # Add people to network
    network.add_person(alice)
    network.add_person(bob)


    metadata = MessageMetadata(MessageType.PLAIN)
    encrypted_message = messenger.encrypt_message(alice, bob, metadata, "This is a secret message!") 
    print("Encrypted Message:", encrypted_message)  

    decrypted_message = messenger.decrypt_message(bob, encrypted_message)
    print("Decrypted Message:", decrypted_message)
    
   
