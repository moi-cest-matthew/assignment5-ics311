from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum
import networkx as nx
import re
from structures import MessageType, Person, MessageMetadata, Message, CommunicationNetwork

class ExtendedCommunicationNetwork(CommunicationNetwork):
    def send_rle_compressed_message(self, sender_id: str, receiver_id: str, message_body: str) -> Message:
        sender = self.get_person(sender_id)
        receiver = self.get_person(receiver_id)
        if not sender or not receiver:
            raise ValueError("Sender or receiver not found in the network.")
        # Compress the message using RLE
        compressed_body = rle_encode(message_body)
        # Create metadata indicating RLE compression
        metadata = MessageMetadata(
            message_type=MessageType.RLE_COMPRESSED,
            original_length=len(message_body)
        )
        # Create the message
        message = Message(
            sender=sender,
            receiver=receiver,
            metadata=metadata,
            body=compressed_body
        )
        return message
    
    def receive_rle_compressed_message(self, message: Message) -> str:
        if message.metadata.message_type != MessageType.RLE_COMPRESSED:
            raise ValueError("Message is not RLE compressed.")
        # Decode the message body
        decoded_body = rle_decode(message.body)
        return decoded_body

def rle_encode(input_string: str) -> str:
    if not input_string:
        return ""
    
    encoded = []
    count = 1
    prev_char = input_string[0]
    
    for char in input_string[1:]:
        if char == prev_char: 
            count += 1
        else:
            encoded.append(f"{count}{prev_char}")
            prev_char = char
            count = 1
            
    # Append the last group
    encoded.append(f"{count}{prev_char}")
    return ''.join(encoded)

def rle_decode(encoded_string: str) -> str:
    if not encoded_string:
        return ""
        
    decoded = []
    count = ""
    
    # Process each character
    for char in encoded_string:
        if char.isdigit():
            count += char  # Accumulate digits for count
        else:
            # When we hit a non-digit, multiply the character by count
            decoded.append(char * int(count))
            count = ""  # Reset count for next group
            
    return ''.join(decoded)
