import pytest
from structures import Person, CommunicationNetwork
from signed_messages import SignedMessenger

@pytest.fixture
def network():
    return CommunicationNetwork()

@pytest.fixture
def messenger(network):
    return SignedMessenger(network)

@pytest.fixture
def setup_network(network, messenger):
    # Create people
    alice = Person("alice")
    bob = Person("bob")
    
    # Generate and assign keys
    alice_private, alice_public = messenger.generate_key_pair()
    bob_private, bob_public = messenger.generate_key_pair()
    
    alice.private_key = alice_private
    alice.public_key = alice_public
    bob.private_key = bob_private
    bob.public_key = bob_public
    
    # Add to network
    network.add_person(alice)
    network.add_person(bob)
    network.add_connection("alice", "bob")
    
    return network, alice, bob

def test_key_generation(messenger):
    private_key, public_key = messenger.generate_key_pair()
    assert private_key is not None
    assert public_key is not None
    assert private_key != public_key

def test_message_signing(messenger, setup_network):
    network, alice, bob = setup_network
    message = "Hello, Bob! This is a signed message."
    
    signed_message = messenger.send_signed_message("alice", "bob", message)
    assert signed_message is not None
    assert messenger.verify_received_message(signed_message)

def test_tampered_message(messenger, setup_network):
    network, alice, bob = setup_network
    message = "Hello, Bob! This is a signed message."
    
    signed_message = messenger.send_signed_message("alice", "bob", message)
    signed_message.body = "Tampered message"
    assert not messenger.verify_received_message(signed_message)

def test_wrong_sender(messenger, setup_network):
    network, alice, bob = setup_network
    message = "Hello, Bob! This is a signed message."
    
    # Create Eve with different keys
    eve = Person("eve")
    eve_private, eve_public = messenger.generate_key_pair()
    eve.private_key = eve_private
    eve.public_key = eve_public
    network.add_person(eve)
    
    signed_message = messenger.send_signed_message("alice", "bob", message)
    signed_message.sender = eve
    assert not messenger.verify_received_message(signed_message)