import pytest
from structures import Person, CommunicationNetwork, MessageType, MessageMetadata, Message

@pytest.fixture
def network():
    return CommunicationNetwork()

def test_add_person(network):
    alice = Person("alice")
    network.add_person(alice)
    assert network.get_person("alice") == alice

def test_add_connection(network):
    alice = Person("alice")
    bob = Person("bob")
    network.add_person(alice)
    network.add_person(bob)
    network.add_connection("alice", "bob")
    assert network.are_connected("alice", "bob")

def test_path_finding(network):
    alice = Person("alice")
    bob = Person("bob")
    charlie = Person("charlie")
    
    network.add_person(alice)
    network.add_person(bob)
    network.add_person(charlie)
    
    network.add_connection("alice", "bob")
    network.add_connection("bob", "charlie")
    
    path = network.get_path("alice", "charlie")
    assert path == ["alice", "bob", "charlie"]

def test_message_creation():
    alice = Person("alice")
    bob = Person("bob")
    metadata = MessageMetadata(message_type=MessageType.SIGNED)
    message = Message(sender=alice, receiver=bob, metadata=metadata, body="Hello")
    
    assert message.sender == alice
    assert message.receiver == bob
    assert message.metadata.message_type == MessageType.SIGNED
    assert message.body == "Hello"