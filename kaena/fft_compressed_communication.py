import numpy as np
from structures import CommunicationNetwork, Person, Message, MessageMetadata, MessageType

# Fast Fourier Transform-based lossy compression
def fft_compress_message(message_body: str, compression_ratio: float) -> str:
    """
    Compress a message using FFT by removing high-frequency components.
    Args:
        message_body (str): The original message body.
        compression_ratio (float): The ratio of frequencies to retain (0 < ratio <= 1).
    Returns:
        str: The lossy compressed message as a string.
    """
    if not (0 < compression_ratio <= 1):
        raise ValueError("Compression ratio must be between 0 and 1.")

    # Convert the message to a numerical representation
    message_array = np.array([ord(char) for char in message_body])

    # Perform FFT
    fft_result = np.fft.fft(message_array)

    # Zero out high-frequency components
    cutoff = int(len(fft_result) * compression_ratio)
    fft_result[cutoff:] = 0

    # Perform inverse FFT
    compressed_array = np.fft.ifft(fft_result).real.round().astype(int)

    # Convert back to string
    compressed_message = ''.join(chr(max(0, min(255, char))) for char in compressed_array)

    return compressed_message

# Send a lossy compressed message
def send_compressed_message(network: CommunicationNetwork, sender_id: str, receiver_id: str, 
                            message_body: str, compression_ratio: float):
    """
    Send a lossy compressed message from sender to receiver using FFT compression.

    Args:
        network (CommunicationNetwork): The communication network.
        sender_id (str): The ID of the sender.
        receiver_id (str): The ID of the receiver.
        message_body (str): The original message body.
        compression_ratio (float): The compression ratio for FFT compression.

    Returns:
        Message: The message object representing the sent message.
    """
    sender = network.get_person(sender_id)
    receiver = network.get_person(receiver_id)

    if not sender or not receiver:
        raise ValueError("Sender or receiver not found in the network.")

    compressed_body = fft_compress_message(message_body, compression_ratio)

    metadata = MessageMetadata(
        message_type=MessageType.FFT_COMPRESSED,
        original_length=len(message_body),
        compression_ratio=compression_ratio
    )

    message = Message(
        sender=sender,
        receiver=receiver,
        metadata=metadata,
        body=compressed_body
    )

    return message